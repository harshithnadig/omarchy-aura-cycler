import importlib.util
import json
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
