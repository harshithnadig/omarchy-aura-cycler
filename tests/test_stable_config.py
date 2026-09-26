import importlib.util
import json
import os
import stat
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import SimpleNamespace

MODULE = Path(__file__).parents[1] / "bin" / "aura-config.py"


def load_layer(name="aura_config_test"):
    loader = SourceFileLoader(name, str(MODULE))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class FakeCore:
    GPU_GUARD_DEFAULTS = {"auto_protect": False, "aura_paused": False}
    DEFAULT_CONFIG = {
        "interval": 300,
        "blur": 12,
        "weather_sync": False,
        "stream_online": False,
        "screen_effects": False,
        "keyboard_sync": True,
        "location_mode": "off",
        "gpu_guard": GPU_GUARD_DEFAULTS.copy(),
    }

    def __init__(self, config_file, key_file):
        self.CONFIG_FILE = str(config_file)
        self.WALLHAVEN_KEY_FILE = str(key_file)
        self.logs = []

    def atomic_write_text(self, path, text, mode=0o600):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.chmod(tmp, mode)
        os.replace(tmp, path)

    def log(self, message):
        self.logs.append(str(message))


def make_control(tmp_path):
    state = tmp_path / "state"
    runtime_dir = tmp_path / "runtime"
    state.mkdir()
    runtime_dir.mkdir()
    core = FakeCore(state / "aura-cycler-config.json", tmp_path / "config" / "wallhaven.key")

    def original_load():
        try:
            saved = json.loads(Path(core.CONFIG_FILE).read_text())
        except (OSError, ValueError):
            saved = {}
        cfg = core.DEFAULT_CONFIG.copy()
        cfg["gpu_guard"] = core.DEFAULT_CONFIG["gpu_guard"].copy()
        cfg.update(saved if isinstance(saved, dict) else {})
        return cfg

    def original_save(cfg):
        core.atomic_write_text(core.CONFIG_FILE, json.dumps(cfg) + "\n", 0o600)

    runtime = SimpleNamespace(
        core=core,
        XDG_RUNTIME_DIR=runtime_dir,
        XDG_CONFIG_HOME=tmp_path / "xdg-config",
        AURA_STATE_DIR=state,
        load_config=original_load,
        save_config=original_save,
    )
    control = SimpleNamespace(
        runtime=runtime,
        core=core,
        VERSION="1.4.0",
        HISTORY_FILE=state / "aura-history.json",
        FAVORITES_FILE=state / "aura-favorites.json",
    )

    def read_json(path, fallback):
        try:
            return json.loads(Path(path).read_text())
        except (OSError, ValueError):
            return fallback

    def write_private(path, value):
        core.atomic_write_text(path, json.dumps(value) + "\n", 0o600)

    control._read_json = read_json
    control._write_private_json = write_private
    control._save_history = lambda items: write_private(control.HISTORY_FILE, {"version": 1, "items": items})
    control._save_favorites = lambda items: write_private(control.FAVORITES_FILE, {"version": 1, "items": items})
    return control


def test_migrates_and_owner_only(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    layer = load_layer("aura_config_migrate")
    control = make_control(tmp_path)
    Path(control.core.CONFIG_FILE).write_text('{"interval": 60}')
    layer.install(control)
    cfg = control.runtime.load_config()
    assert cfg["config_version"] == 2
    assert cfg["interval"] == 60
    assert stat.S_IMODE(Path(control.core.CONFIG_FILE).stat().st_mode) == 0o600


def test_existing_private_config_permissions_are_repaired_before_read(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    layer = load_layer("aura_config_permissions")
    control = make_control(tmp_path)
    config_path = Path(control.core.CONFIG_FILE)
    config_path.write_text(json.dumps({
        "config_version": 2,
        "interval": 75,
        "location_mode": "manual",
        "manual_location": {"lat": 12.97, "lon": 77.59, "city": "Bengaluru"},
    }))
    config_path.chmod(0o644)

    layer.install(control)
    cfg = control.runtime.load_config()

    assert cfg["interval"] == 75
    assert cfg["manual_location"]["lat"] == 12.97
    assert stat.S_IMODE(config_path.stat().st_mode) == 0o600


def test_symlink_config_is_quarantined_without_reading_target(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    layer = load_layer("aura_config_symlink")
    control = make_control(tmp_path)
    config_path = Path(control.core.CONFIG_FILE)
    target = tmp_path / "outside.json"
    target.write_text(json.dumps({"config_version": 2, "interval": 777}))
    config_path.symlink_to(target)

    layer.install(control)
    cfg = control.runtime.load_config()

    assert cfg["interval"] == 300
    assert not config_path.is_symlink()
    assert stat.S_IMODE(config_path.stat().st_mode) == 0o600
    quarantined = list(config_path.parent.glob("aura-cycler-config.unsafe-*.json"))
    assert len(quarantined) == 1
    assert quarantined[0].is_symlink()
    assert target.read_text() == json.dumps({"config_version": 2, "interval": 777})


def test_corrupt_config_is_preserved_and_recovered(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    layer = load_layer("aura_config_corrupt")
    control = make_control(tmp_path)
    Path(control.core.CONFIG_FILE).write_text('{broken json')
    layer.install(control)
    cfg = control.runtime.load_config()
    assert cfg["config_version"] == 2
    backups = list(Path(control.core.CONFIG_FILE).parent.glob("aura-cycler-config.corrupt-*.json"))
    assert len(backups) == 1
    assert backups[0].read_text() == '{broken json'


def test_stale_saves_merge_without_lost_updates(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    layer = load_layer("aura_config_merge")
    control = make_control(tmp_path)
    layer.install(control)

    first = control.runtime.load_config()
    second = control.runtime.load_config()
    first["interval"] = 900
    control.runtime.save_config(first)
    second["blur"] = 4
    control.runtime.save_config(second)

    final = control.runtime.load_config()
    assert final["interval"] == 900
    assert final["blur"] == 4


def test_settings_import_is_typed_and_bounded(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    layer = load_layer("aura_config_settings")
    control = make_control(tmp_path)
    layer.install(control)
    shell = Path(control.runtime.XDG_CONFIG_HOME) / "omarchy" / "shell.json"
    shell.parent.mkdir(parents=True)
    shell.write_text(json.dumps({
        "version": 1,
        "bar": {"layout": {"left": [], "center": [], "right": [{
            "id": "harshith.aura-cycler",
            "interval": 1,
            "blur": 999,
            "weatherSync": True,
            "themeScope": "editors",
        }]}}
    }))
    rc = layer.dispatch(control, ["settings-import", json.dumps({
        "interval": 1,
        "blur": 999,
        "weatherSync": True,
        "themeScope": "editors",
    })])
    assert rc == 0
    cfg = control.runtime.load_config()
    assert cfg["interval"] == 5
    assert cfg["blur"] == 24
    assert cfg["weather_sync"] is True
    assert cfg["theme_scope"] == "editors"


def test_backup_redacts_location_by_default(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    layer = load_layer("aura_config_backup")
    control = make_control(tmp_path)
    layer.install(control)
    cfg = control.runtime.load_config()
    cfg["manual_location"] = {"lat": 12.9, "lon": 77.5}
    cfg["location_mode"] = "manual"
    control.runtime.save_config(cfg)

    target = tmp_path / "backup.json"
    assert layer.dispatch(control, ["backup", str(target)]) == 0
    bundle = json.loads(target.read_text())
    assert bundle["config"]["manual_location"]["redacted"] is True
    assert stat.S_IMODE(target.stat().st_mode) == 0o600


def test_restore_creates_emergency_backup(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    layer = load_layer("aura_config_restore")
    control = make_control(tmp_path)
    layer.install(control)
    backup = tmp_path / "restore.json"
    backup.write_text(json.dumps({
        "format": "aura-backup",
        "backup_version": 1,
        "aura_version": "1.4.0",
        "private": True,
        "config": {"interval": 777, "blur": 8},
        "history": {"version": 1, "items": []},
        "favorites": {"version": 1, "items": []},
    }))
    assert layer.dispatch(control, ["restore", str(backup)]) == 0
    cfg = control.runtime.load_config()
    assert cfg["interval"] == 777
    assert cfg["blur"] == 8
    assert list(Path(control.runtime.AURA_STATE_DIR).glob("pre-restore-*.json"))


def test_first_manifest_defaults_do_not_overwrite_existing_config(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    layer = load_layer("aura_config_first_sync")
    control = make_control(tmp_path)
    Path(control.core.CONFIG_FILE).write_text(json.dumps({
        "interval": 1200, "blur": 7, "weather_sync": True
    }))
    layer.install(control)
    assert layer.dispatch(control, ["settings-import", json.dumps({
        "interval": 300, "blur": 12, "weatherSync": False
    })]) == 0
    cfg = control.runtime.load_config()
    assert cfg["interval"] == 1200
    assert cfg["blur"] == 7
    assert cfg["weather_sync"] is True
