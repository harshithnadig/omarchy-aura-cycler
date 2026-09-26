import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

from PIL import Image


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
