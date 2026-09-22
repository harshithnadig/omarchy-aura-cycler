import importlib.util
import json
import stat
import tempfile
from pathlib import Path
from importlib.machinery import SourceFileLoader
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
GUARD = ROOT / "bin" / "aura-cycler-service-guard"


def load_guard():
    loader = SourceFileLoader("aura_service_guard", str(GUARD))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_systemd_unit_runs_public_entrypoint():
    unit = (ROOT / "systemd" / "material-cycler.service").read_text()
    assert "ExecStart=%h/.config/omarchy/plugins/harshith.aura-cycler/bin/aura-cycler run" in unit
    assert ".local/libexec/omarchy/harshith.aura-cycler-service-guard" not in unit


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


def test_invalid_checkout_disables_and_removes_only_owned_unit_links():
    guard = load_guard()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        unit_path = root / "systemd" / "user" / guard.SERVICE_NAME
        unit_path.parent.mkdir(parents=True)
        unit_path.write_text(
            "[Service]\n"
            f"ExecStart={guard.UNIT_EXEC_MARKER}\n"
        )
        for wants_directory in (
            "graphical-session.target.wants",
            "default.target.wants",
        ):
            wants = unit_path.parent / wants_directory
            wants.mkdir()
            (wants / guard.SERVICE_NAME).symlink_to(unit_path)

        calls = []

        def fake_run(command, **_kwargs):
            calls.append(command)
            raise OSError("systemd unavailable in test")

        guard.UNIT_PATH = unit_path
        with patch.object(guard.subprocess, "run", side_effect=fake_run):
            guard.remove_owned_unit()

        assert not unit_path.exists()
        assert not any(
            (unit_path.parent / wants_directory / guard.SERVICE_NAME).is_symlink()
            for wants_directory in (
                "graphical-session.target.wants",
                "default.target.wants",
            )
        )
        assert calls == [
            ["systemctl", "--user", "disable", guard.SERVICE_NAME],
            ["systemctl", "--user", "daemon-reload"],
        ]
