import importlib.util
import json
import os
import signal
import subprocess
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).parents[1]
CLI = ROOT / "bin" / "aura-cycler"
CORE = ROOT / "bin" / "aura-cycler-core"


class AuraGpuGuardCliTests(unittest.TestCase):
    def load_core(self, state_home):
        runtime = state_home / "runtime"
        runtime.mkdir(exist_ok=True)
        home = state_home / "home"
        home.mkdir(exist_ok=True)
        environment = os.environ.copy()
        previous_sigterm = signal.getsignal(signal.SIGTERM)
        os.environ.update({"HOME": str(home), "XDG_RUNTIME_DIR": str(runtime)})
        try:
            loader = SourceFileLoader("aura_cycler_test_core", str(CORE))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)
            return module
        finally:
            signal.signal(signal.SIGTERM, previous_sigterm)
            os.environ.clear()
            os.environ.update(environment)

    def run_cli(self, state_home, *args):
        runtime = state_home / "runtime"
        runtime.mkdir(exist_ok=True)
        home = state_home / "home"
        home.mkdir(exist_ok=True)
        env = os.environ.copy()
        env.update({
            "HOME": str(home),
            "XDG_STATE_HOME": str(state_home / "state"),
            "XDG_DATA_HOME": str(state_home / "data"),
            "XDG_CACHE_HOME": str(state_home / "cache"),
            "XDG_CONFIG_HOME": str(state_home / "config"),
            "XDG_RUNTIME_DIR": str(runtime),
        })
        result = subprocess.run(
            [str(CLI), *args],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip(), env

    def test_guard_reports_without_mutating_system(self):
        with tempfile.TemporaryDirectory() as directory:
            state_home = Path(directory)
            output, _ = self.run_cli(state_home, "gpu-guard", "status")
            status = json.loads(output)
            self.assertIn(status["level"], {"unavailable", "nominal", "warning", "critical"})
            self.assertIn("metrics", status)
            self.assertIn("processes", status)

    def test_protection_toggle_is_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            state_home = Path(directory)
            output, env = self.run_cli(state_home, "gpu-guard", "toggle-protect")
            self.assertIn("Enabled", output)
            status_raw, _ = self.run_cli(state_home, "gpu-guard", "status")
            self.assertTrue(json.loads(status_raw)["auto_protect"])
            config = Path(env["XDG_STATE_HOME"]) / "omarchy/aura-cycler-config.json"
            self.assertTrue(config.exists())
            self.assertEqual(config.stat().st_mode & 0o777, 0o600)

    def test_offline_mode_skips_background_prefetch_in_core(self):
        with tempfile.TemporaryDirectory() as directory:
            state_home = Path(directory)
            module = self.load_core(state_home)
            module.save_config({"stream_online": False, "interval": 300})
            prefetched = []
            module.apply_next_wallpaper = lambda: None
            module.fetch_4k_wallpapers = lambda count: prefetched.append(count)

            class StopAfterOneIteration(Exception):
                pass

            module.sleep_with_keyboard_sync = lambda _seconds: (_ for _ in ()).throw(
                StopAfterOneIteration()
            )
            with self.assertRaises(StopAfterOneIteration):
                module.run_loop()
            self.assertEqual(prefetched, [])

    def test_wallpaper_inventory_can_skip_expensive_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            state_home = Path(directory)
            module = self.load_core(state_home)
            folder = state_home / "wallpapers"
            folder.mkdir()
            module.CACHE_DIR = str(state_home / "cache")
            (folder / "one.jpg").write_bytes(b"not-an-image")
            module.load_config = lambda: {"custom_folders": [str(folder)]}
            validations = []
            module.valid_wallpaper = lambda path: validations.append(path) or path == str(folder / "one.jpg")

            self.assertEqual(module.collect_local_wallpapers(validate=False), [str(folder / "one.jpg")])
            self.assertEqual(validations, [])
            self.assertEqual(module.collect_local_wallpapers(validate=True), [str(folder / "one.jpg")])
            self.assertEqual(validations, [str(folder / "one.jpg")])


if __name__ == "__main__":
    unittest.main()
