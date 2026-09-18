import socketserver
import socket
import json
import threading
import time

import pytest

from damru.proxy_bridge import BridgeHandler, ThreadingTCPServer, TrafficPolicy, _parse_upstream


class _NoopHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        return None


def test_proxy_bridge_exits_after_idle_timeout():
    with ThreadingTCPServer(
        ("127.0.0.1", 0),
        _NoopHandler,
        idle_timeout_seconds=0.05,
    ) as server:
        thread = threading.Thread(target=server.serve_until_idle)
        thread.start()
        thread.join(timeout=1)

        assert not thread.is_alive()


def test_proxy_bridge_does_not_expire_while_connection_is_active():
    with ThreadingTCPServer(
        ("127.0.0.1", 0),
        _NoopHandler,
        idle_timeout_seconds=0.01,
    ) as server:
        server.connection_started()
        time.sleep(0.02)
        assert server.idle_expired() is False

        server.connection_finished()
        time.sleep(0.02)
        assert server.idle_expired() is True


@pytest.mark.parametrize('scheme', ['http', 'socks5'])
@pytest.mark.parametrize('host', ['browser-intake-datadoghq.com', 'rum.browser-intake-datadoghq.com', 'www.googletagmanager.com'])
def test_telemetry_is_rejected_before_upstream_connection(tmp_path, monkeypatch, scheme, host):
    from damru import proxy_bridge
    config = tmp_path / 'policy.json'
    config.write_text(json.dumps({'name': 'telemetry', 'blocked_domains': ['browser-intake-datadoghq.com', 'googletagmanager.com']}))
    def unexpected(*args, **kwargs):
        raise AssertionError('A blocked request must never contact the paid proxy')
    monkeypatch.setattr(proxy_bridge, '_connect_target_via_upstream', unexpected)
    # Create the client before patching the upstream connector.
    class Handler(BridgeHandler):
        upstream = _parse_upstream(f'{scheme}://user:secret@127.0.0.1:1')
    with ThreadingTCPServer(('127.0.0.1', 0), Handler) as server:
        server.traffic_policy = TrafficPolicy(config, tmp_path / 'metrics')
        client = socket.create_connection(server.server_address)
        monkeypatch.setattr(proxy_bridge.socket, 'create_connection', unexpected)
        thread = threading.Thread(target=server.handle_request)
        thread.start()
        with client:
            client.settimeout(2)
            client.sendall(f'CONNECT {host}:443 HTTP/1.1\r\nHost: {host}\r\n\r\n'.encode())
            assert client.recv(4096).startswith(b'HTTP/1.1 403')
        thread.join(2)
        for _ in range(50):
            files = list((tmp_path / 'metrics').glob('*.jsonl'))
            if files and files[0].stat().st_size:
                break
            time.sleep(0.01)
        text = files[0].read_text()
        record = json.loads(text)
        assert record['blocked'] is True
        assert record['upstream_bytes'] == record['downstream_bytes'] == 0
        assert 'secret' not in text and 'Proxy-Authorization' not in text


def test_policy_updates_match_domain_boundaries_and_allow_exceptions(tmp_path):
    config = tmp_path / 'policy.json'
    config.write_text(json.dumps({'blocked_domains': ['googletagmanager.com'], 'allowed_domains': ['preview.googletagmanager.com']}))
    policy = TrafficPolicy(config)
    assert policy.decision('www.googletagmanager.com')[0]
    assert not policy.decision('googletagmanager.com.evil.example')[0]
    assert not policy.decision('preview.googletagmanager.com')[0]
    config.write_text(json.dumps({'name': 'baseline', 'blocked_domains': []}))
    assert policy.decision('www.googletagmanager.com') == (False, 'baseline')


def test_allowed_connect_relays_data_and_counts_both_directions(tmp_path):
    class UpstreamHandler(socketserver.BaseRequestHandler):
        def handle(self):
            self.request.recv(4096)
            self.request.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
            data = self.request.recv(4096)
            self.request.sendall(data.upper())
    with ThreadingTCPServer(('127.0.0.1', 0), UpstreamHandler) as upstream:
        upstream_thread = threading.Thread(target=upstream.handle_request)
        upstream_thread.start()
        class Handler(BridgeHandler):
            pass
        Handler.upstream = _parse_upstream(f'http://user:secret@127.0.0.1:{upstream.server_address[1]}')
        with ThreadingTCPServer(('127.0.0.1', 0), Handler) as server:
            server.traffic_policy = TrafficPolicy(metrics_dir=tmp_path)
            thread = threading.Thread(target=server.handle_request)
            thread.start()
            with socket.create_connection(server.server_address) as client:
                client.settimeout(2)
                client.sendall(b'CONNECT shopee.com.br:443 HTTP/1.1\r\n\r\n')
                assert client.recv(4096).startswith(b'HTTP/1.1 200')
                client.sendall(b'payload')
                assert client.recv(4096) == b'PAYLOAD'
            thread.join(2)
        upstream_thread.join(2)
    for _ in range(50):
        files = list(tmp_path.glob('*.jsonl'))
        if files and files[0].stat().st_size:
            break
        time.sleep(0.01)
    record = json.loads(files[0].read_text())
    assert record['host'] == 'shopee.com.br' and not record['blocked']
    assert record['upstream_bytes'] > 7 and record['downstream_bytes'] > 7


def test_invalid_config_rejects_connection_policy_instead_of_silently_disabling(tmp_path):
    config = tmp_path / 'policy.json'
    config.write_text('{broken')
    with pytest.raises(ValueError):
        TrafficPolicy(config).decision('www.googletagmanager.com')
