import importlib.util
import json
import os
import signal
import stat
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
CLI = ROOT / "bin" / "aura-cycler"


class MockResponse:
    def __init__(self, payload):
        self.payload = payload
        self.headers = {"Content-Length": str(len(payload))}

    def read(self, amount=None):
        if amount is None:
            return self.payload
        return self.payload[:amount]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def load_runtime(tmp_path):
    home = tmp_path / "home"
    runtime = tmp_path / "runtime"
    for path in (home, runtime):
        path.mkdir(parents=True, exist_ok=True)

    environment = os.environ.copy()
    previous_sigterm = signal.getsignal(signal.SIGTERM)
    os.environ.update({
        "HOME": str(home),
        "XDG_STATE_HOME": str(tmp_path / "state"),
        "XDG_DATA_HOME": str(tmp_path / "data"),
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
        "XDG_CONFIG_HOME": str(tmp_path / "config"),
        "XDG_RUNTIME_DIR": str(runtime),
    })
    try:
        loader = SourceFileLoader("aura_runtime_test", str(CLI))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)
        os.environ.clear()
        os.environ.update(environment)


def test_fresh_install_weather_is_offline_by_default(tmp_path):
    module = load_runtime(tmp_path)
    cfg = module.load_config()
    assert cfg["weather_sync"] is False
    assert cfg["location_mode"] == "off"
    with patch.object(module.urllib.request, "urlopen", side_effect=AssertionError("network used")):
        weather = module.get_weather()
    assert weather["available"] is False
    assert weather["source"] == "unavailable"


def test_config_is_owner_only(tmp_path):
    module = load_runtime(tmp_path)
    cfg = module.load_config()
    cfg["location_mode"] = "manual"
    cfg["manual_location"] = {
        "lat": 12.9716,
        "lon": 77.5946,
        "city": "Bengaluru",
        "country": "India",
        "timestamp": 1,
    }
    module.save_config(cfg)
    path = Path(module.core.CONFIG_FILE)
    assert path.is_file()
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_auto_location_uses_https(tmp_path):
    module = load_runtime(tmp_path)
    cfg = module.load_config()
    cfg["location_mode"] = "auto"
    cfg["weather_sync"] = True
    module.save_config(cfg)

    payload = json.dumps({
        "latitude": 12.9716,
        "longitude": 77.5946,
        "city": "Bengaluru",
        "country_name": "India",
    }).encode()

    seen = []

    def fake_urlopen(request, timeout=0):
        seen.append((request.full_url, timeout))
        return MockResponse(payload)

    with patch.object(module.urllib.request, "urlopen", side_effect=fake_urlopen):
        location = module.get_location(force=True)

    assert location["city"] == "Bengaluru"
    assert seen
    assert seen[0][0].startswith("https://")


def test_manual_location_never_needs_ip_lookup(tmp_path):
    module = load_runtime(tmp_path)
    cfg = module.load_config()
    cfg["location_mode"] = "manual"
    cfg["weather_sync"] = True
    cfg["manual_location"] = {
        "lat": 12.9716,
        "lon": 77.5946,
        "city": "Bengaluru",
        "country": "India",
        "timestamp": 1,
    }
    module.save_config(cfg)

    with patch.object(module.urllib.request, "urlopen", side_effect=AssertionError("IP lookup used")):
        location = module.get_location(force=True)
    assert location["source"] == "manual"


def test_gpu_autoprotect_marks_pause_without_stopping_service(tmp_path):
    module = load_runtime(tmp_path)
    state = dict(module.core.GPU_GUARD_DEFAULTS)
    state["auto_protect"] = True
    metrics = {
        "available": True,
        "vram_percent": 95,
        "temperature_c": 70,
    }
    action = module.apply_gpu_guard_protection(metrics, state)
    assert state["aura_paused"] is True
    assert "Paused Aura cycling" in action

    metrics["vram_percent"] = 10
    action = module.apply_gpu_guard_protection(metrics, state)
    assert state["aura_paused"] is False
    assert "Resumed Aura cycling" in action


def test_theme_generation_failure_restores_previous_staging(tmp_path):
    module = load_runtime(tmp_path)
    current = tmp_path / "current-theme"
    next_theme = tmp_path / "next-theme"
    lock = tmp_path / "runtime" / "theme.lock"
    current.mkdir()
    next_theme.mkdir()
    (next_theme / "old-marker").write_text("old")

    module.core.CURRENT_THEME_DIR = str(current)
    module.core.NEXT_THEME_DIR = str(next_theme)
    module.core.THEME_LOCK_FILE = str(lock)

    with patch.object(
        module.subprocess,
        "run",
        return_value=SimpleNamespace(returncode=1, stdout="", stderr="failed"),
    ):
        assert module.regenerate_derived_theme_files('mode = "dark"\n') is False

    assert (next_theme / "old-marker").read_text() == "old"
