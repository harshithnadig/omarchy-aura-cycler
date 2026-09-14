import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
CLI = ROOT / "bin" / "aura-cycler"


class AuraGpuGuardCliTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
