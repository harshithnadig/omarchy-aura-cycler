import importlib.util
import io
import json
import os
import signal
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
CLI = ROOT / "bin" / "aura-cycler"


class MockHttpResponse:
    def __init__(self, data=b"", headers=None):
        self._bio = io.BytesIO(data)
        self.headers = headers or {}

    def read(self, amt=None):
        if amt is None:
            return self._bio.read()
        return self._bio.read(amt)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class SecurityAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_home = Path(self.tmpdir.name)
        self.runtime = self.state_home / "runtime"
        self.runtime.mkdir(exist_ok=True)
        self.home = self.state_home / "home"
        self.home.mkdir(exist_ok=True)
        self.cache_dir = self.home / "cache"
        self.cache_dir.mkdir(exist_ok=True)

        environment = os.environ.copy()
        previous_sigterm = signal.getsignal(signal.SIGTERM)
        os.environ.update({
            "HOME": str(self.home),
            "XDG_RUNTIME_DIR": str(self.runtime),
        })
        try:
            loader = SourceFileLoader("aura_cycler_sec_module", str(CLI))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            self.module = importlib.util.module_from_spec(spec)
            loader.exec_module(self.module)
            self.module.CACHE_DIR = str(self.cache_dir)
        finally:
            signal.signal(signal.SIGTERM, previous_sigterm)
            os.environ.clear()
            os.environ.update(environment)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_safe_cache_path_allows_valid_identifiers(self):
        path = self.module.safe_cache_path("wallhaven", "photo123_abc", ".png")
        self.assertTrue(path.startswith(str(self.cache_dir)))
        self.assertEqual(os.path.basename(path), "wallhaven_photo123_abc.png")

    def test_safe_cache_path_neutralizes_directory_traversal(self):
        traversal_attempts = [
            "../../../../etc/passwd",
            "../secret.txt",
            "/etc/shadow",
            "subdir/evil",
            "photo;rm -rf /",
            "photo space",
        ]
        for malicious_id in traversal_attempts:
            dest = self.module.safe_cache_path("wallhaven", malicious_id, ".jpg")
            # Verify containment under CACHE_DIR
            resolved_cache = os.path.realpath(str(self.cache_dir))
            resolved_dest = os.path.realpath(dest)
            self.assertEqual(
                os.path.commonpath([resolved_cache, resolved_dest]),
                resolved_cache,
                f"Malicious identifier '{malicious_id}' escaped CACHE_DIR: {dest}"
            )
            # Verify filename contains no slashes or directory traversal markers
            base = os.path.basename(dest)
            self.assertNotIn("/", base)
            self.assertNotIn("..", base)
            self.assertTrue(base.endswith(".jpg"))

    def test_safe_cache_path_restricts_extensions(self):
        for unsafe_ext in [".sh", ".exe", ".php", ".py", ".html", ""]:
            dest = self.module.safe_cache_path("bing", "test_hsh", unsafe_ext)
            self.assertTrue(dest.endswith(".jpg"))

        for valid_ext in [".jpg", ".jpeg", ".png", ".webp"]:
            dest = self.module.safe_cache_path("bing", "test_hsh", valid_ext)
            self.assertTrue(dest.endswith(valid_ext))

    def test_read_capped_json_success(self):
        data = json.dumps({"status": "success", "lat": 12.97, "lon": 77.59}).encode("utf-8")
        resp = MockHttpResponse(data, headers={"Content-Length": str(len(data))})
        parsed = self.module.read_capped_json(resp, max_bytes=1024)
        self.assertEqual(parsed["status"], "success")
        self.assertEqual(parsed["lat"], 12.97)

    def test_read_capped_json_rejects_oversized_content_length(self):
        resp = MockHttpResponse(b"{}", headers={"Content-Length": "2097152"})  # 2 MiB
        with self.assertRaises(ValueError) as ctx:
            self.module.read_capped_json(resp, max_bytes=1048576)
        self.assertIn("exceeds maximum allowed size", str(ctx.exception))

    def test_read_capped_json_aborts_on_oversized_payload_without_header(self):
        huge_payload = b"x" * (1024 * 1024 + 50)
        resp = MockHttpResponse(huge_payload)
        with self.assertRaises(ValueError) as ctx:
            self.module.read_capped_json(resp, max_bytes=1024 * 1024)
        self.assertIn("exceeds maximum allowed size", str(ctx.exception))

    def test_download_wallpaper_blocks_destination_outside_cache(self):
        outside_dest = str(self.state_home / "escape" / "outside.jpg")
        success = self.module.download_wallpaper("http://example.com/test.jpg", outside_dest)
        self.assertFalse(success)
        self.assertFalse(os.path.exists(outside_dest))

    def test_download_wallpaper_rejects_non_http_urls(self):
        destination = str(self.cache_dir / "local.jpg")
        success = self.module.download_wallpaper("file:///etc/passwd", destination)
        self.assertFalse(success)
        self.assertFalse(os.path.exists(destination))

    def test_download_wallpaper_rejects_oversized_content_length(self):
        dest = str(self.cache_dir / "oversized.jpg")
        mock_resp = MockHttpResponse(
            b"fake-image-bytes",
            headers={"Content-Length": str(self.module.MAX_WALLPAPER_BYTES + 1024)}
        )
        with patch("urllib.request.urlopen", return_value=mock_resp):
            success = self.module.download_wallpaper("http://example.com/huge.jpg", dest)
        self.assertFalse(success)
        self.assertFalse(os.path.exists(dest))

    def test_download_wallpaper_aborts_mid_stream_when_byte_limit_exceeded(self):
        dest = str(self.cache_dir / "stream_overflow.jpg")
        # Generate stream chunks exceeding limit without Content-Length
        chunk = b"A" * (64 * 1024)
        num_chunks = (self.module.MAX_WALLPAPER_BYTES // len(chunk)) + 2
        overflow_data = chunk * num_chunks
        mock_resp = MockHttpResponse(overflow_data, headers={})

        with patch("urllib.request.urlopen", return_value=mock_resp):
            success = self.module.download_wallpaper("http://example.com/unbounded.jpg", dest)

        self.assertFalse(success)
        self.assertFalse(os.path.exists(dest))
        # Ensure temporary files in cache_dir were cleaned up
        temp_files = [f for f in os.listdir(self.cache_dir) if f.startswith(".material-download-")]
        self.assertEqual(temp_files, [], "Temporary download file leaked on size abort")


if __name__ == "__main__":
    unittest.main()
