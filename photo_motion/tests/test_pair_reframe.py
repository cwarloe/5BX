"""Regression tests for the optional *photographic* A/C headroom transform."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from photo_motion.pair_reframe import CANVAS_SIZE, OUTPUT_NAMES, reframe_pair


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_image(path, *, accent):
    image = Image.new("RGB", CANVAS_SIZE, (84, 136, 98))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 545, 1279, 719), fill=(177, 70, 54))
    draw.rectangle((0, 550, 1279, 550), fill=(220, 215, 181))
    draw.ellipse((530 + accent, 100, 620 + accent, 200), fill=(226, 190, 152))
    draw.polygon([(530 + accent, 200), (650 + accent, 200), (640 + accent, 530), (540 + accent, 530)], fill=(64, 155, 201))
    image.save(path)


class PairReframeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.a, self.c = self.root / "a.png", self.root / "c.png"
        make_image(self.a, accent=-30)
        make_image(self.c, accent=30)
        self.sha_a, self.sha_c = sha(self.a), sha(self.c)
        self.out = self.root / "out"
        self.out.mkdir()

    def call(self, *, out=None, **kwargs):
        return reframe_pair(
            self.a, self.c, out or self.out,
            a_sha256=kwargs.pop("a_sha256", self.sha_a),
            c_sha256=kwargs.pop("c_sha256", self.sha_c),
            **kwargs,
        )

    def test_pair_is_uniformly_scaled_and_source_unmodified(self):
        m = self.call()
        self.assertEqual([128, 72, 1152, 648], m["transform"]["central_region_half_open"])
        self.assertEqual({"left": 128, "right": 128, "top": 72, "bottom": 72}, m["transform"]["padding_pixels"])
        self.assertEqual("NOT_EVALUATED", m["motion_form_identity_and_release"])
        self.assertEqual("NOT_VERIFIED_BY_THIS_TOOL", m["source_parent_card_provenance"])
        self.assertEqual(self.sha_a, sha(self.a))
        self.assertEqual(self.sha_c, sha(self.c))
        for role, original in (("A", self.a), ("C", self.c)):
            prepared = self.out / m["output_images"][role]["filename"]
            self.assertEqual(sha(prepared), m["output_images"][role]["sha256"])
            with Image.open(prepared) as actual, Image.open(original) as source:
                self.assertEqual(CANVAS_SIZE, actual.size)
                center = actual.crop((128, 72, 1152, 648))
                expected = source.resize((1024, 576), Image.Resampling.LANCZOS)
                self.assertEqual(expected.tobytes(), center.tobytes())
                # Top border mirrors the first 72 rows of resized photo,
                # not a newly invented sky, and covers all four corners.
                self.assertEqual(actual.getpixel((128, 0)), expected.getpixel((0, 71)))
                self.assertEqual(actual.getpixel((0, 72)), expected.getpixel((127, 0)))

    def test_replay_is_byte_exact_across_output_directories(self):
        first = self.call()
        other = self.root / "other"
        other.mkdir()
        second = self.call(out=other)
        self.assertEqual(first, second)
        for name in OUTPUT_NAMES:
            self.assertEqual((self.out / name).read_bytes(), (other / name).read_bytes())
        self.assertEqual(first, json.loads((other / OUTPUT_NAMES[2]).read_text()))

    def test_fails_closed_on_stale_source_hash(self):
        with self.assertRaisesRegex(ValueError, "A input SHA-256 mismatch"):
            self.call(a_sha256="0" * 64)
        self.assertFalse(any(self.out.iterdir()))

    def test_fails_closed_on_missing_or_bad_format(self):
        self.a.write_text("not a png")
        with self.assertRaisesRegex(ValueError, "A input SHA-256 mismatch"):
            self.call()
        self.assertFalse(any(self.out.iterdir()))
        self.sha_a = sha(self.a)
        with self.assertRaisesRegex(Exception, "cannot identify image"):
            self.call()

    def test_fails_closed_on_source_symlink(self):
        link = self.root / "link.png"
        link.symlink_to(self.a)
        with self.assertRaisesRegex(ValueError, "non-symlink"):
            reframe_pair(link, self.c, self.out, a_sha256=self.sha_a, c_sha256=self.sha_c)
        self.assertFalse(any(self.out.iterdir()))

    def test_fails_closed_on_same_images(self):
        with self.assertRaisesRegex(ValueError, "distinct"):
            reframe_pair(self.a, self.a, self.out, a_sha256=self.sha_a, c_sha256=self.sha_a)
        self.assertFalse(any(self.out.iterdir()))

    def test_fails_closed_on_existing_destination(self):
        marker = self.out / OUTPUT_NAMES[1]
        marker.write_text("keep-me")
        with self.assertRaises(FileExistsError):
            self.call()
        self.assertEqual("keep-me", marker.read_text())
        self.assertEqual([OUTPUT_NAMES[1]], [p.name for p in self.out.iterdir()])

    def test_fails_closed_on_bad_scale_and_preserves_inputs(self):
        with self.assertRaisesRegex(ValueError, "70 through 90"):
            self.call(scale_percent=95)
        with self.assertRaisesRegex(ValueError, "even"):
            self.call(scale_percent=81)
        self.assertEqual(self.sha_a, sha(self.a))
        self.assertEqual(self.sha_c, sha(self.c))
        self.assertFalse(any(self.out.iterdir()))

    def test_partial_output_reservations_are_removed(self):
        # A pre-existing C file detected after A reservation must remain
        # untouched. The first A output must not remain as a partial output.
        marker = self.out / OUTPUT_NAMES[2]
        marker.write_bytes(b"existing")
        with self.assertRaises(FileExistsError):
            self.call()
        self.assertEqual(b"existing", marker.read_bytes())
        self.assertFalse((self.out / OUTPUT_NAMES[0]).exists())


if __name__ == "__main__":
    unittest.main()
