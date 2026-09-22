import importlib.util
import json
import os
import signal
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
CLI = ROOT / "bin" / "aura-cycler"


def load_control(tmp_path):
    home = tmp_path / "home"
    runtime = tmp_path / "runtime"
    for path in (home, runtime):
        path.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
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
        loader = SourceFileLoader("aura_control_test", str(CLI))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)
        os.environ.clear()
        os.environ.update(env)


def test_history_is_bounded_and_deduplicates_consecutive_entries(tmp_path):
    module = load_control(tmp_path)
    for number in range(module.HISTORY_LIMIT + 5):
        module._record_history(str(tmp_path / f"wall-{number}.jpg"))
    items = module._load_history()
    assert len(items) == module.HISTORY_LIMIT
    assert items[-1]["name"] == f"wall-{module.HISTORY_LIMIT + 4}.jpg"
    before = len(items)
    assert module._record_history(items[-1]["path"]) is False
    assert len(module._load_history()) == before


def test_favorite_toggle_uses_current_wallpaper(tmp_path, capsys):
    module = load_control(tmp_path)
    wallpaper = tmp_path / "wallpaper.jpg"
    wallpaper.write_bytes(b"fixture")
    current = Path(module.runtime.AURA_STATE_DIR) / "current/background"
    current.parent.mkdir(parents=True, exist_ok=True)
    current.symlink_to(wallpaper)

    assert module.favorites_cmd(["toggle"]) == 0
    assert len(module._load_favorites()) == 1
    assert module._is_favorite(str(wallpaper))
    assert module.favorites_cmd(["toggle"]) == 0
    assert module._load_favorites() == []
    capsys.readouterr()


def test_theme_scope_filters_only_known_live_sync_commands(tmp_path):
    module = load_control(tmp_path)
    assert module._live_sync_allowed(["omarchy-theme-set-browser"], "shell") is False
    assert module._live_sync_allowed(["omarchy-restart-terminal"], "terminals") is True
    assert module._live_sync_allowed(["omarchy-theme-set-vscode"], "terminals") is False
    assert module._live_sync_allowed(["omarchy-theme-set-vscode"], "editors") is True
    assert module._live_sync_allowed(["omarchy-theme-set-browser"], "editors") is False
    assert module._live_sync_allowed(["omarchy-theme-set-browser"], "all") is True
    assert module._live_sync_allowed(["future-critical-helper"], "shell") is True


def test_scene_does_not_silently_enable_network(tmp_path):
    module = load_control(tmp_path)
    cfg = module.runtime.load_config()
    cfg["weather_sync"] = False
    cfg["stream_online"] = False
    module.runtime.save_config(cfg)

    assert module.scene_cmd(["apply", "ambient"]) == 0
    cfg = module.runtime.load_config()
    assert cfg["scene"] == "ambient"
    assert cfg["weather_sync"] is False
    assert cfg["stream_online"] is False

    assert module.scene_cmd(["apply", "gaming"]) == 0
    cfg = module.runtime.load_config()
    assert cfg["gpu_guard"]["auto_protect"] is True
    assert cfg["screen_effects"] is False


def test_privacy_status_redacts_manual_coordinates_by_default(tmp_path, capsys):
    module = load_control(tmp_path)
    cfg = module.runtime.load_config()
    cfg["location_mode"] = "manual"
    cfg["weather_sync"] = True
    cfg["manual_location"] = {"lat": 12.9, "lon": 77.5, "city": "Private"}
    module.runtime.save_config(cfg)

    assert module.privacy_cmd([]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["manual_location_configured"] is True
    assert "manual_location" not in data


def test_config_export_redacts_location_by_default(tmp_path, capsys):
    module = load_control(tmp_path)
    cfg = module.runtime.load_config()
    cfg["manual_location"] = {"lat": 1, "lon": 2, "city": "Secret"}
    cfg["location_cache"] = {"lat": 1, "lon": 2}
    module.runtime.save_config(cfg)

    assert module.config_cmd(["export"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert "location_cache" not in data
    assert data["manual_location"]["redacted"] is True


def test_cache_prune_only_touches_generated_palette_cache(tmp_path, capsys):
    module = load_control(tmp_path)
    palette_dir = Path(module.core.PALETTE_CACHE_DIR)
    palette_dir.mkdir(parents=True, exist_ok=True)
    old = palette_dir / "old.json"
    old.write_text("{}")
    os.utime(old, (1, 1))
    unrelated = tmp_path / "keep.jpg"
    unrelated.write_bytes(b"keep")

    assert module.cache_cmd(["prune-palettes", "1"]) == 0
    assert not old.exists()
    assert unrelated.exists()
    capsys.readouterr()


def test_doctor_never_performs_network_io(tmp_path):
    module = load_control(tmp_path)
    with patch("urllib.request.urlopen", side_effect=AssertionError("doctor used network")):
        checks = module._doctor_checks()
    assert checks


def test_runtime_daemon_identity_is_public_front_controller(tmp_path):
    module = load_control(tmp_path)
    assert module.runtime.WRAPPER_PATH == module.FRONT_PATH
