"""Runtime proxy helpers shared by CLI, UI, and AsyncDamru."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path, PureWindowsPath
from urllib.parse import urlparse

from .proxy import resolve_system_proxy

DEFAULT_PROXY_BRIDGE_IDLE_TIMEOUT_SECONDS = 3600.0


def is_windows() -> bool:
    return sys.platform == "win32"


def is_wsl_linux() -> bool:
    if is_windows() or platform.system() != "Linux":
        return False
    try:
        release = platform.uname().release.lower()
        if "microsoft" in release or "wsl" in release:
            return True
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return False


def configured_wsl_distro() -> str:
    env_distro = os.environ.get("DAMRU_WSL_DISTRO")
    if env_distro:
        return env_distro
    try:
        from . import config

        return config.WSL_DISTRO
    except Exception:
        return "Ubuntu"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def to_wsl_path(value: str) -> str:
    if re.match(r"^[A-Za-z]:[\\/]", value):
        p = PureWindowsPath(value)
        drive = p.drive.rstrip(":").lower()
        rest = "/".join(p.parts[1:])
        return f"/mnt/{drive}/{rest}"
    return value


def linux_cmd(script: str, root_user: bool = False) -> list[str]:
    if is_windows():
        encoded = base64.b64encode(script.encode("utf-8")).decode("ascii")
        wrapped = f"printf %s {encoded} | base64 -d | bash"
        cmd = ["wsl", "-d", configured_wsl_distro()]
        if root_user:
            cmd.extend(["-u", "root"])
        cmd.extend(["--", "bash", "-lc", wrapped])
        return cmd
    return ["bash", "-lc", script]


def linux_run(script: str, timeout: int = 30, root_user: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        linux_cmd(script, root_user=root_user),
        capture_output=True,
        text=True,
        timeout=timeout,
        errors="replace",
    )


def proxy_bridge_upstream(proxy: str | None, http_proxy: str | None = None) -> str | None:
    value = (http_proxy or proxy or "").strip()
    if not value or "://" not in value:
        return None
    parsed = urlparse(value)
    scheme = (parsed.scheme or "").lower()
    if scheme in {"http", "https"}:
        return value if parsed.username is not None else None
    if scheme in {"socks5", "socks5h"}:
        return value
    return None


def _bridge_alive(port: int, *, root_user: bool, host: str = "127.0.0.1") -> bool:
    probe = linux_run(
        f"timeout 1 bash -c '</dev/tcp/{shlex.quote(host)}/{port}' >/dev/null 2>&1",
        timeout=5,
        root_user=root_user,
    )
    return probe.returncode == 0


def android_proxy_host_from_route(route_text: str, *, fallback: str = "172.17.0.1") -> str:
    match = re.search(r"\bvia\s+(\d+\.\d+\.\d+\.\d+)\b", route_text or "")
    if match:
        return match.group(1)
    src = re.search(r"\bsrc\s+(\d+)\.(\d+)\.(\d+)\.\d+\b", route_text or "")
    if src:
        return f"{src.group(1)}.{src.group(2)}.{src.group(3)}.1"
    return fallback


def _proxy_bridge_idle_timeout_seconds() -> float:
    raw_value = os.environ.get("DAMRU_PROXY_BRIDGE_IDLE_TIMEOUT_SECONDS")
    if raw_value is None:
        return DEFAULT_PROXY_BRIDGE_IDLE_TIMEOUT_SECONDS
    try:
        return max(0.0, float(raw_value))
    except ValueError:
        return DEFAULT_PROXY_BRIDGE_IDLE_TIMEOUT_SECONDS


def ensure_proxy_bridge(upstream: str, *, listen_host: str = "127.0.0.1") -> int:
    digest = hashlib.sha256(f"{listen_host}|{upstream}".encode("utf-8")).hexdigest()[:12]
    port = 18000 + (int(digest[:6], 16) % 3000)
    runtime_dir = "/home/damru/runtime/proxy-bridges" if is_windows() or is_wsl_linux() else str(Path.home() / ".cache" / "damru" / "proxy-bridges")
    config_path = f"{runtime_dir}/{digest}.json"
    log_path = f"{runtime_dir}/{digest}.log"
    script_path = repo_root() / "damru" / "proxy_bridge.py"
    linux_script = to_wsl_path(str(script_path)) if is_windows() else str(script_path)
    root_user = is_windows() or is_wsl_linux()
    config = json.dumps(
        {
            "upstream": upstream,
            "listen_host": listen_host,
            "listen_port": port,
            "idle_timeout_seconds": _proxy_bridge_idle_timeout_seconds(),
        }
    )
    config_b64 = base64.b64encode(config.encode("utf-8")).decode("ascii")

    if not _bridge_alive(port, root_user=root_user, host=listen_host):
        write_cmd = (
            f"umask 077; mkdir -p {shlex.quote(runtime_dir)}; "
            f"printf %s {shlex.quote(config_b64)} | base64 -d > {shlex.quote(config_path)}; "
            f"chmod 600 {shlex.quote(config_path)}"
        )
        write = linux_run(write_cmd, timeout=10, root_user=root_user)
        if write.returncode != 0:
            raise RuntimeError((write.stderr or write.stdout or "failed to write proxy bridge config").strip())
        start_cmd = (
            f"setsid -f python3 {shlex.quote(linux_script)} --config {shlex.quote(config_path)} "
            f"> {shlex.quote(log_path)} 2>&1 < /dev/null"
        )
        if is_windows():
            start = subprocess.run(
                ["wsl", "-d", configured_wsl_distro(), "-u", "root", "--", "bash", "-lc", start_cmd],
                capture_output=True,
                text=True,
                timeout=10,
                errors="replace",
            )
        else:
            start = linux_run(start_cmd, timeout=10, root_user=root_user)
        if start.returncode != 0:
            raise RuntimeError((start.stderr or start.stdout or "failed to start proxy bridge").strip())
        deadline = time.time() + 5
        while time.time() < deadline:
            if _bridge_alive(port, root_user=root_user, host=listen_host):
                break
            time.sleep(0.25)
        else:
            raise RuntimeError("proxy bridge did not become ready")
    return port


def resolve_android_proxy(proxy: str | None = None, http_proxy: str | None = None, route_text: str = "") -> str | None:
    upstream = proxy_bridge_upstream(proxy, http_proxy)
    if upstream:
        listen_host = android_proxy_host_from_route(route_text)
        port = ensure_proxy_bridge(upstream, listen_host=listen_host)
        return f"{listen_host}:{port}"
    return resolve_system_proxy(proxy=proxy, http_proxy=http_proxy)
