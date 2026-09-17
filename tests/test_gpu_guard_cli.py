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


class AuraGpuGuardCliTests(unittest.TestCase):
    def load_module(self, state_home):
        runtime = state_home / "runtime"
        runtime.mkdir(exist_ok=True)
        home = state_home / "home"
        home.mkdir(exist_ok=True)
        environment = os.environ.copy()
        previous_sigterm = signal.getsignal(signal.SIGTERM)
        os.environ.update({
            "HOME": str(home),
            "XDG_RUNTIME_DIR": str(runtime),
        })
        try:
            loader = SourceFileLoader("aura_cycler_test_module", str(CLI))
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
        env = os.environ.copy()
        env.update({
            "HOME": str(state_home / "home"),
            "XDG_STATE_HOME": str(state_home / "state"),
            "XDG_RUNTIME_DIR": str(runtime),
        })
        result = subprocess.run(
            [str(CLI), *args],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_guard_reports_driver_failure_without_mutating_system(self):
        with tempfile.TemporaryDirectory() as directory:
            state_home = Path(directory)
            status = json.loads(self.run_cli(state_home, "gpu-guard", "status"))
            self.assertIn(status["level"], {"unavailable", "nominal", "warning", "critical"})
            self.assertIn("metrics", status)
            self.assertIn("processes", status)

    def test_protection_toggle_is_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            state_home = Path(directory)
            output = self.run_cli(state_home, "gpu-guard", "toggle-protect")
            self.assertIn("Enabled", output)
            status = json.loads(self.run_cli(state_home, "gpu-guard", "status"))
            self.assertTrue(status["auto_protect"])

    def test_offline_mode_skips_background_prefetch(self):
        with tempfile.TemporaryDirectory() as directory:
            state_home = Path(directory)
            module = self.load_module(state_home)
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
            module = self.load_module(state_home)
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
