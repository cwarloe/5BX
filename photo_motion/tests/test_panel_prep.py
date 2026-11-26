import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from photo_motion.panel_prep import DEFAULT_V6_A_BOUNDS, VERIFIED_V6_SOURCE_SHA256, main, prepare


class PanelPreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.source = self.folder / "synthetic-full-card.png"
        src = Image.new("RGB", (1536, 1024), (21, 42, 63))
        dr = ImageDraw.Draw(src)
        # Distinct edge swatches prove that reflection is used, not a solid fill.
        for k in range(100):
            dr.line([(k + 4, 4), (k + 4, 507)], fill=(k, 80, 120))
            dr.line([(763 - k, 4), (763 - k, 507)], fill=(90, k, 180))
        # Synthetic "subject" occupies the inner panel; never needs cropping.
        dr.rectangle([155, 12, 600, 476], fill=(197, 66, 17))
        dr.ellipse([176, 405, 275, 480], fill=(25, 195, 220))
        dr.ellipse([457, 404, 546, 474], fill=(25, 195, 220))
        src.save(self.source)
        self.original = self.source.read_bytes()
        self.hash = hashlib.sha256(self.original).hexdigest()

    def test_native_canvas_preserves_central_crop_bit_for_bit(self):
        dest = self.folder / "prepared.png"
        result = prepare(self.source, dest, expected_source_sha256=self.hash,
                         expected_source_size=(1536, 1024))
        self.assertEqual(result["crop_bounds_half_open"], [4, 4, 764, 508])
        self.assertEqual(result["crop_size"], [760, 504])
        self.assertEqual(result["padding"]["left"], 68)
        self.assertEqual(result["padding"]["right"], 68)
        self.assertEqual(result["output_size"], [896, 504])
        self.assertEqual(result["resampling"]["used"], False)
        with Image.open(self.source) as source, Image.open(dest) as output:
            expected = source.crop(DEFAULT_V6_A_BOUNDS)
            actual = output.crop((68, 0, 828, 504))
            self.assertIsNone(ImageChops.difference(expected, actual).getbbox())
            # Left pad mirrors exact outer 68 columns, in reverse order.
            self.assertEqual(output.getpixel((0, 0)), expected.getpixel((67, 0)))
            self.assertEqual(output.getpixel((67, 0)), expected.getpixel((0, 0)))
            # Right pad mirrors exact outer 68 columns, in reverse order.
            self.assertEqual(output.getpixel((828, 0)), expected.getpixel((759, 0)))
            self.assertEqual(output.getpixel((895, 0)), expected.getpixel((692, 0)))
            # Mirrored join has no one-pixel color discontinuity (C0 seam).
            self.assertEqual(output.getpixel((67, 0)), output.getpixel((68, 0)))
            self.assertEqual(output.getpixel((827, 0)), output.getpixel((828, 0)))
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(result["source_image_sha256_before"], result["source_image_sha256_after"])
        self.assertEqual(hashlib.sha256(dest.read_bytes()).hexdigest(), result["output_sha256"])
        self.assertEqual(json.loads((self.folder / "prepared.manifest.json").read_text()), result)
        self.assertEqual(result["video_motion_and_form"], "NOT_EVALUATED")
        self.assertEqual(result["visual_subject_completeness"], "NOT_EVALUATED_FOR_THIS_SOURCE_AND_CROP")
        self.assertIn("can repeat visual features", result["mirrored_side_extension_risk"])
        self.assertEqual(result["expected_source_sha256"], self.hash)

    def test_cli_pins_verified_v6_sha_by_default(self):
        dest = self.folder / "wrong-source.png"
        with redirect_stderr(io.StringIO()) as stderr:
            status = main([str(self.source), str(dest)])
        self.assertEqual(status, 2)
        self.assertIn("source SHA-256 differs", stderr.getvalue())
        self.assertFalse(dest.exists())
        self.assertFalse(dest.with_suffix(".manifest.json").exists())
        self.assertNotEqual(self.hash, VERIFIED_V6_SOURCE_SHA256)

    def test_cli_allows_explicit_unverified_source_and_records_gate(self):
        dest = self.folder / "explicit-other-source.png"
        with redirect_stdout(io.StringIO()):
            status = main([str(self.source), str(dest), "--allow-unverified-source"])
        self.assertEqual(status, 0)
        manifest = json.loads(dest.with_suffix(".manifest.json").read_text())
        self.assertIsNone(manifest["expected_source_sha256"])
        self.assertFalse(manifest["source_hash_matches_expected"])
        self.assertEqual(manifest["visual_subject_completeness"], "NOT_EVALUATED_FOR_THIS_SOURCE_AND_CROP")

    def test_cli_accepts_explicit_alternate_exact_sha(self):
        dest = self.folder / "other-exact-sha.png"
        with redirect_stdout(io.StringIO()):
            status = main([str(self.source), str(dest), "--expected-sha256", self.hash])
        self.assertEqual(status, 0)
        manifest = json.loads(dest.with_suffix(".manifest.json").read_text())
        self.assertEqual(manifest["expected_source_sha256"], self.hash)
        self.assertTrue(manifest["source_hash_matches_expected"])

    def test_cli_rejects_conflicting_sha_options(self):
        dest = self.folder / "conflicting.png"
        with redirect_stderr(io.StringIO()) as stderr, self.assertRaises(SystemExit) as raised:
            main([str(self.source), str(dest), "--expected-sha256", self.hash, "--allow-unverified-source"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("mutually exclusive", stderr.getvalue())
        self.assertFalse(dest.exists())

    def test_optional_720p_export_is_16_by_9_and_manifest_discloses_resampling(self):
        dest = self.folder / "prepared720.png"
        result = prepare(self.source, dest, expected_source_sha256=self.hash,
                         export_size=(1280, 720))
        with Image.open(dest) as image:
            self.assertEqual(image.size, (1280, 720))
        self.assertEqual(result["resampling"]["method"], "LANCZOS")
        self.assertTrue(result["resampling"]["used"])
        self.assertEqual(result["canvas_size_before_resampling"], [896, 504])
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_bad_expected_sha_prevents_write(self):
        dest = self.folder / "badsha.png"
        with self.assertRaisesRegex(ValueError, "source SHA-256 differs"):
            prepare(self.source, dest, expected_source_sha256="0" * 64)
        self.assertFalse(dest.exists())
        self.assertFalse(dest.with_suffix(".manifest.json").exists())

    def test_bad_crop_rejected_without_write(self):
        for bounds in ((-1, 4, 764, 508), (4, 4, 1540, 508), (4, 4, 4, 508), (4, 508, 764, 508)):
            dest = self.folder / "badbounds.png"
            with self.assertRaisesRegex(ValueError, "outside source|zero area"):
                prepare(self.source, dest, crop=bounds)
            self.assertFalse(dest.exists())

    def test_wider_than_16by9_crop_requires_different_plan(self):
        with self.assertRaisesRegex(ValueError, "wider than 16:9"):
            prepare(self.source, self.folder / "wide.png", crop=(4, 4, 764, 103))

    def test_non_divisible_height_cannot_be_exact_16by9_by_side_padding(self):
        dest = self.folder / "non_exact.png"
        with self.assertRaisesRegex(ValueError, "divisible by 9"):
            prepare(self.source, dest, crop=(4, 4, 764, 509))
        self.assertFalse(dest.exists())
        self.assertFalse(dest.with_suffix(".manifest.json").exists())

    def test_existing_image_must_not_be_overwritten(self):
        dest = self.folder / "protected.png"
        dest.write_bytes(b"SENTINEL")
        with self.assertRaises(FileExistsError):
            prepare(self.source, dest)
        self.assertEqual(dest.read_bytes(), b"SENTINEL")

    def test_existing_manifest_prevents_image_create(self):
        dest = self.folder / "existing_manifest.png"
        manifest = dest.with_suffix(".manifest.json")
        manifest.write_text("SENTINEL", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            prepare(self.source, dest)
        self.assertFalse(dest.exists())
        self.assertEqual(manifest.read_text(), "SENTINEL")

    def test_output_symlink_rejected_without_modifying_target(self):
        dest = self.folder / "output-symlink.png"
        sentinel = self.folder / "sentinel.txt"
        sentinel.write_bytes(b"ORIGINAL")
        dest.symlink_to(sentinel)
        with self.assertRaises(FileExistsError):
            prepare(self.source, dest)
        self.assertEqual(sentinel.read_bytes(), b"ORIGINAL")
        self.assertTrue(dest.is_symlink())
        self.assertFalse(dest.with_suffix(".manifest.json").exists())

    def test_source_symlink_rejected(self):
        linked = self.folder / "source-link.png"
        linked.symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, "source must be an explicit non-symlink"):
            prepare(linked, self.folder / "out.png")

    def test_bad_export_ratio_rejected_without_write(self):
        dest = self.folder / "badexport.png"
        with self.assertRaisesRegex(ValueError, "exact 16:9"):
            prepare(self.source, dest, export_size=(1280, 800))
        self.assertFalse(dest.exists())

    def test_repeat_output_rejected_and_old_output_preserved(self):
        dest = self.folder / "repeat.png"
        prepare(self.source, dest)
        original_output = dest.read_bytes()
        with self.assertRaises(FileExistsError):
            prepare(self.source, dest)
        self.assertEqual(dest.read_bytes(), original_output)

    def test_deterministic_file_hash_with_same_name_other_folder(self):
        out1 = self.folder / "one"
        out2 = self.folder / "two"
        out1.mkdir()
        out2.mkdir()
        a = prepare(self.source, out1 / "same.png")
        b = prepare(self.source, out2 / "same.png")
        self.assertEqual(a, b)
        self.assertEqual((out1 / "same.png").read_bytes(), (out2 / "same.png").read_bytes())
        self.assertEqual((out1 / "same.manifest.json").read_bytes(), (out2 / "same.manifest.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
