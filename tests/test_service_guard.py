import importlib.util
import json
import stat
import tempfile
from pathlib import Path
from importlib.machinery import SourceFileLoader


ROOT = Path(__file__).parents[1]
GUARD = ROOT / "bin" / "aura-cycler-service-guard"


def load_guard():
    loader = SourceFileLoader("aura_service_guard", str(GUARD))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_systemd_unit_runs_external_guard():
    unit = (ROOT / "systemd" / "material-cycler.service").read_text()
    assert "ExecStart=%h/.local/libexec/omarchy/harshith.aura-cycler-service-guard" in unit
    assert ".config/omarchy/plugins/harshith.aura-cycler/bin/aura-cycler" not in unit


def test_guard_requires_owned_manifest_and_real_entrypoint():
    guard = load_guard()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "plugin"
        (root / "bin").mkdir(parents=True)
        (root / "manifest.json").write_text(json.dumps({"id": guard.PLUGIN_ID}))
        entrypoint = root / "bin" / "aura-cycler"
        entrypoint.write_text("#!/usr/bin/env python3\n")
        entrypoint.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        guard.PLUGIN_ROOT = root
        guard.ENTRYPOINT = entrypoint
        assert guard.plugin_checkout_is_valid()

        entrypoint.unlink()
        entrypoint.symlink_to("/bin/sh")
        assert not guard.plugin_checkout_is_valid()
