import importlib.util
from importlib.machinery import SourceFileLoader
import base64
import subprocess
from pathlib import Path

from PIL import Image
import pytest


CORE = Path(__file__).parents[1] / "bin" / "aura-cycler-core"


def test_palette_extraction_handles_fewer_distinct_colors_than_clusters(tmp_path):
    loader = SourceFileLoader("aura_palette_regression", str(CORE))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    image_path = tmp_path / "three-colors.png"
    image = Image.new("RGB", (30, 30))
    pixels = image.load()
    colors = ((230, 20, 20), (20, 230, 20), (20, 20, 230))
    for y in range(30):
        for x in range(30):
            pixels[x, y] = colors[(x // 10) % len(colors)]
    image.save(image_path)
    module.PALETTE_CACHE_FILE = str(tmp_path / "palette-cache.json")

    accent, palette = module.extract_focal_colors_offline(str(image_path))

    assert accent
    assert palette


def test_wallpaper_rotation_does_not_reload_shell_plugins(tmp_path, monkeypatch):
    loader = SourceFileLoader("aura_wallpaper_lifecycle", str(CORE))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    chosen = tmp_path / "wallpaper.png"
    chosen.write_bytes(b"image")
    module.load_config = lambda: {"stream_online": False}
    module.collect_local_wallpapers = lambda validate=False: [str(chosen)]
    module.valid_wallpaper = lambda _path: True
    module.CURRENT_THEME_DIR = str(tmp_path / "theme")
    module.PALETTE_STATE_FILE = str(tmp_path / "palette.json")
    module.extract_focal_colors_offline = lambda _path: (
        "abcdef", {"primary": "#abcdef"}
    )
    module.write_colors_toml = lambda path, _palette: (
        Path(path).parent.mkdir(parents=True, exist_ok=True) or "colors = true\n"
    )
    module.regenerate_derived_theme_files = lambda _colors: True
    module.set_keyboard_color = lambda _color: None
    module.regenerate_derived_theme_files = lambda _colors: True

    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.subprocess, "Popen", lambda *a, **k: None)
    monkeypatch.setattr(module.subprocess, "DEVNULL", subprocess.DEVNULL)
    module.apply_next_wallpaper()

    assert not any(command[-2:-1] == ["applyTheme"] for command in calls)
    assert not any("shell" in command and "applyTheme" in command for command in calls)
    assert any("themeTransition" in command for command in calls)
