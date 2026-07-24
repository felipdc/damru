import sys
import os
import pytest
from pathlib import Path

# Add project root to python path to ensure imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import damru.ui.server as ui_server
from damru.ui.server import (
    redact,
    android_input_text,
    now_ms,
    static_dir,
    capture_dir,
    package_command,
    parse_adb_devices,
    next_action,
    config_snapshot,
    build_command,
    STATE
)

@pytest.mark.unit
def test_redact_secrets() -> None:
    # Test password pattern
    assert redact("password=mysecret") == "password=<redacted>"
    assert redact("passwd=123") == "passwd=<redacted>"
    assert redact("api-key=xyz") == "api-key=<redacted>"
    
    # Test proxy URL pattern
    assert redact("socks5://user:pass@proxy.com:1080") == "socks5://<redacted>:<redacted>@proxy.com:1080"
    assert redact("http://admin:secret123@127.0.0.1:8080") == "http://<redacted>:<redacted>@127.0.0.1:8080"
    
    # Test command proxy patterns
    assert redact("--proxy socks5://user:pass@proxy.com:1080") == "--proxy <redacted>"
    assert redact("proxy=127.0.0.1:8080") == "proxy=<redacted>"


@pytest.mark.unit
def test_android_input_text_escaping() -> None:
    # Test spaces
    assert android_input_text("hello world") == "hello%sworld"
    
    # Test percent
    assert android_input_text("100%") == "100%25"
    
    # Test special characters escaping
    assert android_input_text("hello$world") == "hello\\$world"
    assert android_input_text("foo&bar") == "foo\\&bar"
    
    # Test newlines mapping to spaces
    assert android_input_text("line1\nline2") == "line1%sline2"
    
    # Test character cap
    long_text = "a" * 600
    assert len(android_input_text(long_text)) <= 500


@pytest.mark.unit
def test_now_ms() -> None:
    t = now_ms()
    assert isinstance(t, int)
    assert t > 0


@pytest.mark.unit
def test_dirs() -> None:
    assert isinstance(static_dir(), Path)
    assert static_dir().name == "static"
    
    assert isinstance(capture_dir(), Path)
    assert capture_dir().exists()


@pytest.mark.unit
def test_package_command() -> None:
    cmd = package_command("check-env")
    assert cmd[0] == sys.executable
    assert cmd[1] == "-m"
    assert cmd[2] == "damru"
    assert cmd[3] == "check-env"


@pytest.mark.unit
def test_parse_adb_devices() -> None:
    text = (
        "List of devices attached\n"
        "127.0.0.1:5600\tdevice\n"
        "emulator-5554\toffline\n"
        "unauthorized_dev\tunauthorized\n"
    )
    devices = parse_adb_devices(text)
    assert len(devices) == 3
    assert devices[0] == {"serial": "127.0.0.1:5600", "state": "device"}
    assert devices[1] == {"serial": "emulator-5554", "state": "offline"}
    assert devices[2] == {"serial": "unauthorized_dev", "state": "unauthorized"}


@pytest.mark.unit
def test_next_action_recommendation() -> None:
    # Test unsupported state
    assert next_action([], "unsupported") == {"label": "Read requirements", "action": "none"}
    
    # Test missing dependencies
    checks = [{"key": "wsl", "ok": False}, {"key": "adb", "ok": True}]
    assert next_action(checks, "supported") == {"label": "Install dependencies", "action": "install-deps"}
    
    # Test missing binderfs/docker daemon
    checks = [{"key": "wsl", "ok": True}, {"key": "binderfs", "ok": False}]
    assert next_action(checks, "supported") == {"label": "Repair Docker / binderfs", "action": "fix-wsl"}
    
    # Test missing apks
    checks = [{"key": "binderfs", "ok": True}, {"key": "apks", "ok": False}]
    assert next_action(checks, "supported") == {"label": "Install APK bundle", "action": "install-apks"}
    
    # Test missing redroid image
    checks = [{"key": "apks", "ok": True}, {"key": "image", "ok": False}]
    assert next_action(checks, "supported") == {"label": "Install Redroid image", "action": "install-image"}
    
    # Test all ok
    checks = [{"key": "image", "ok": True}]
    assert next_action(checks, "supported") == {"label": "Start working", "action": "workers"}


@pytest.mark.unit
def test_state_job_manager() -> None:
    # Reset/clear active state
    STATE.clear_finished_jobs()
    
    # Add a job
    job = STATE.add_job(
        name="Test Job",
        command_key="check-env",
        command=["python", "--version"],
        timeout=10
    )
    
    assert job.name == "Test Job"
    assert job.command_key == "check-env"
    assert job.status in {"pending", "running", "finished", "failed"}
    
    # Get job
    retrieved = STATE.get_job(job.id)
    assert retrieved is not None
    assert retrieved["name"] == "Test Job"
    
    # Add a failed job directly
    failed_job = STATE.add_failed_job("Failed Job", "error-key", "An error occurred")
    assert failed_job.status == "failed"
    assert "An error occurred" in failed_job.stderr
    
    # Clear finished/failed jobs
    removed = STATE.clear_finished_jobs()
    assert removed >= 0


@pytest.mark.unit
def test_config_snapshot() -> None:
    snap = config_snapshot()
    assert isinstance(snap, dict)
    assert "MODE" in snap
    assert "NUM_DEVICES" in snap


@pytest.mark.unit
def test_build_command_surface() -> None:
    # Test standard actions
    label, cmd, timeout, art = build_command("check-env", {})
    assert label == "Check environment"
    assert "check-env" in cmd
    
    label, cmd, timeout, art = build_command("install-deps", {})
    assert "install-deps" in cmd
    
    label, cmd, timeout, art = build_command("fix-wsl", {})
    assert "fix-wsl" in cmd
    
    # Test actions requiring arguments
    label, cmd, timeout, art = build_command("fix-internet", {"serial": "127.0.0.1:5600"})
    assert "fix-internet" in cmd
    assert "--serial" in cmd
    assert "127.0.0.1:5600" in cmd
    
    # Test unsupported action exception
    with pytest.raises(KeyError):
        build_command("unsupported-action", {})
