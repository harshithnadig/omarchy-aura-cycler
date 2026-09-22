import fcntl
import importlib.util
import json

import pytest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import SimpleNamespace

PUBLIC = Path(__file__).parents[1] / "bin" / "aura-cycler"


def load_public(name="aura_public_compat_test"):
    loader = SourceFileLoader(name, str(PUBLIC))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_standard_omarchy_shell_config_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    public = load_public()

    home = tmp_path / "home"
    xdg = tmp_path / "xdg-config"
    shell = home / ".config" / "omarchy" / "shell.json"
    shell.parent.mkdir(parents=True)
    shell.write_text(json.dumps({
        "version": 1,
        "bar": {
            "layout": {
                "left": [],
                "center": [],
                "right": [{
                    "id": "harshith.aura-cycler",
                    "interval": 777,
                    "blur": 4,
                    "themeScope": "editors",
                }],
            }
        },
    }), encoding="utf-8")

    fake = SimpleNamespace(runtime=SimpleNamespace(HOME=home, XDG_CONFIG_HOME=xdg))
    explicit = public._standard_shell_fallback(fake)

    assert explicit == {
        "interval": 777,
        "blur": 4,
        "themeScope": "editors",
    }


def test_xdg_shell_config_remains_preferred(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    public = load_public("aura_public_xdg_preferred_test")

    home = tmp_path / "home"
    xdg = tmp_path / "xdg-config"
    standard = home / ".config" / "omarchy" / "shell.json"
    preferred = xdg / "omarchy" / "shell.json"
    standard.parent.mkdir(parents=True)
    preferred.parent.mkdir(parents=True)

    standard.write_text(json.dumps({
        "version": 1,
        "bar": {"layout": {"left": [], "center": [], "right": [{
            "id": "harshith.aura-cycler", "interval": 111
        }]}}
    }), encoding="utf-8")
    preferred.write_text(json.dumps({
        "version": 1,
        "bar": {"layout": {"left": [], "center": [], "right": [{
            "id": "harshith.aura-cycler", "interval": 222
        }]}}
    }), encoding="utf-8")

    fake = SimpleNamespace(runtime=SimpleNamespace(HOME=home, XDG_CONFIG_HOME=xdg))
    explicit = public._standard_shell_fallback(fake)
    assert explicit["interval"] == 222


def test_plugin_enabled_state_tracks_omarchy_shell_config(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    public = load_public("aura_public_plugin_lifecycle_state_test")

    home = tmp_path / "home"
    xdg = tmp_path / "xdg-config"
    shell = xdg / "omarchy" / "shell.json"
    shell.parent.mkdir(parents=True)
    fake = SimpleNamespace(runtime=SimpleNamespace(HOME=home, XDG_CONFIG_HOME=xdg))

    shell.write_text(json.dumps({
        "version": 1,
        "bar": {"layout": {"left": [], "center": [], "right": [
            {"id": "harshith.aura-cycler"}
        ]}},
        "plugins": [],
    }), encoding="utf-8")
    assert public._plugin_enabled_from_shell(fake) is True

    shell.write_text(json.dumps({
        "version": 1,
        "bar": {"layout": {"left": [], "center": [], "right": []}},
        "plugins": [],
    }), encoding="utf-8")
    assert public._plugin_enabled_from_shell(fake) is False

    shell.unlink()
    assert public._plugin_enabled_from_shell(fake) is None


def test_public_run_refuses_when_omarchy_plugin_is_disabled(monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    public = load_public("aura_public_disabled_run_test")
    dispatched = []

    monkeypatch.setattr(public, "_plugin_enabled_from_shell", lambda _control: False)
    monkeypatch.setattr(public.control, "_dispatch", lambda: dispatched.append(True) or 99)
    monkeypatch.setattr(public.sys, "argv", [str(PUBLIC), "run"])

    assert public.main() == 0
    assert dispatched == []


def test_running_daemon_sleep_exits_after_plugin_disable(monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    public = load_public("aura_public_disable_during_sleep_test")
    sleeps = []
    logs = []
    states = iter([True, False])

    fake_core = SimpleNamespace(
        sleep_with_keyboard_sync=lambda seconds: sleeps.append(seconds),
        log=lambda message: logs.append(str(message)),
    )
    fake_control = SimpleNamespace(core=fake_core)

    monkeypatch.setattr(public, "_plugin_enabled_from_shell", lambda _control: next(states))
    guard = public._install_omarchy_lifecycle_guard(fake_control)

    assert guard() is True
    with pytest.raises(SystemExit) as stopped:
        fake_core.sleep_with_keyboard_sync(30)
    assert stopped.value.code == 0
    assert any("disabled" in message.lower() for message in logs)


def test_public_reset_requires_explicit_yes(monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    public = load_public("aura_public_reset_guard_test")
    called = []

    def should_not_run(_control, _argv):
        called.append(True)
        return 0

    monkeypatch.setattr(public.config_layer, "dispatch", should_not_run)
    monkeypatch.setattr(public.sys, "argv", [str(PUBLIC), "reset"])

    assert public.main() == 2
    assert called == []


def test_public_reset_allows_explicit_yes(monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    public = load_public("aura_public_reset_yes_test")
    seen = []

    def fake_dispatch(_control, argv):
        seen.append(list(argv))
        return 0

    monkeypatch.setattr(public.config_layer, "dispatch", fake_dispatch)
    monkeypatch.setattr(public.sys, "argv", [str(PUBLIC), "reset", "--yes", "--keep-favorites"])

    assert public.main() == 0
    assert seen == [["reset", "--yes", "--keep-favorites"]]


def test_bounded_log_rotates_oversized_log(tmp_path, monkeypatch):
    monkeypatch.setenv("AURA_DISABLE_SHELL_SETTINGS_SYNC", "1")
    public = load_public("aura_public_log_rotation_test")
    log_path = tmp_path / "material-cycler.log"
    log_path.write_bytes(b"x" * (public.MAX_LOG_BYTES + 1))

    def append_log(message):
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(str(message) + "\n")

    fake_core = SimpleNamespace(LOG_FILE=str(log_path), log=append_log, fcntl=fcntl)
    public._install_bounded_logging(SimpleNamespace(core=fake_core))
    fake_core.log("after rotation")

    assert Path(str(log_path) + ".1").is_file()
    assert log_path.read_text(encoding="utf-8") == "after rotation\n"
    assert log_path.stat().st_mode & 0o777 == 0o600
    assert Path(str(log_path) + ".1").stat().st_mode & 0o777 == 0o600
    assert (tmp_path / "material-cycler.log.lock").stat().st_mode & 0o777 == 0o600
