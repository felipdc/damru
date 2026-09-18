import socketserver
import threading
import time

from damru.proxy_bridge import ThreadingTCPServer


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
