"""Optional render-cache integration tests (requires Pillow and NumPy).

Run: python3 -m unittest discover -s sprites/tests -p render_cache_integration.py -v
The dependency-free production preflight CI intentionally excludes this file.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import build


class TrialCacheTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "sprite-kit"
        self.source = self.root / "assets"
        self.trial = self.root / ".work" / "asset-cache"
        (self.root / "sheets").mkdir(parents=True)
        for name, path in (("ROOT", str(self.root)),
                           ("SOURCE_ASSETS", str(self.source)),
                           ("ASSETS", str(self.trial))):
            ctx = patch.object(build, name, path)
            ctx.start()
            self.addCleanup(ctx.stop)

    def test_trial_reuses_valid_approved_sprite_without_writing_to_source(self):
        sheet = self.root / "sheets" / "one.png"
        sheet.write_bytes(b"unchanged approved sheet")
        cache = self.source / "sprites" / "one"
        cache.mkdir(parents=True)
        Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(cache / "p1.png")
        meta = {"source_hash": build.filehash(str(sheet)), "key": {"lo": 28, "hi": 95},
                "n": 1, "version": build.BAKE_VERSION, "rows": None, "row": None,
                "poses": [{"file": "p1.png"}]}
        original = json.dumps(meta)
        (cache / "meta.json").write_text(original)

        result = build.bake("one", {"file": "one.png", "poses": 1}, {"key": meta["key"]})

        self.assertEqual(result["_cache_dir"], str(cache))
        self.assertEqual((cache / "meta.json").read_text(), original)
        self.assertFalse(self.trial.exists())

    def test_trial_uses_imported_backdrop_without_overwriting_it(self):
        cache = self.source / "backdrops" / "gym" / "landscape"
        cache.mkdir(parents=True)
        Image.new("RGBA", (8, 6), (12, 100, 200, 255)).save(cache / "00-picture.png")
        manifest = {"source": "images", "layers": [["picture", "00-picture.png"]]}
        original = json.dumps(manifest)
        (cache / "manifest.json").write_text(original)

        layers = build.backdrop_layers({"backdrop": {"id": "gym", "style": "image"}},
                                       {"W": 8, "H": 6, "ground": 0.8}, "landscape")

        self.assertEqual(layers[0][1].getpixel((0, 0)), (12, 100, 200, 255))
        self.assertEqual((cache / "manifest.json").read_text(), original)
        self.assertFalse(self.trial.exists())


if __name__ == "__main__":
    unittest.main()
