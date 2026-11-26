"""Synthetic-only tests for photographic foreground compositing controls."""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from photo_motion.foreground_composite import CompositeError, composite, main


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ForegroundCompositeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plate = self.root / "plate.png"
        self.frame = self.root / "foreground.png"
        y, x = np.indices((24, 32))
        plate = np.stack(
            [x * 4 + 15, y * 5 + 10, np.full((24, 32), 160)],
            axis=-1,
        ).astype(np.uint8)
        Image.fromarray(plate, "RGB").save(self.plate)
        fg = np.zeros((24, 32, 4), dtype=np.uint8)
        # Invisible RGB junk must not contaminate the fixed plate.
        fg[:, :, :3] = [245, 0, 245]
        fg[6:18, 10:22, :3] = [210, 60, 40]
        fg[6:18, 10:22, 3] = 128
        fg[7:17, 11:21, 3] = 255
        Image.fromarray(fg, "RGBA").save(self.frame)
        self.recipe = {
            "schema_version": 1,
            "plate": {
                "asset": {"path": str(self.plate), "sha256": digest(self.plate)},
                "origin": "synthetic_fixture",
                "evidence": "generated rectangle/gradient unit-test fixture",
            },
            "frames": [{"path": str(self.frame), "sha256": digest(self.frame)}],
            "fps": 24,
            "margin_px": 2,
            "key_spill": {"rgb": [0, 255, 0], "max_distance": 20, "max_pixels": 0},
        }
        self.recipe_path = self.root / "recipe.json"
        self._write_recipe()

    def _write_recipe(self):
        self.recipe_path.write_text(json.dumps(self.recipe))

    def test_exact_background_and_integer_blend(self):
        result = composite(self.recipe_path, self.root / "out")
        self.assertEqual(result["status"], "PIXEL_QA_PASS_FORM_HOLD")
        self.assertEqual(result["production_release"], "HOLD")
        self.assertFalse(result["plate_origin_independently_verified"])
        output = np.asarray(Image.open(self.root / "out" / "frame_000000.png"))
        plate = np.asarray(Image.open(self.plate))
        self.assertTrue(np.array_equal(output[0, 0], plate[0, 0]))
        self.assertTrue(np.array_equal(output[15, 29], plate[15, 29]))
        self.assertTrue(np.array_equal(output[8, 12], [210, 60, 40]))
        expected = ((np.array([210, 60, 40]) * 128 +
                     plate[6, 10].astype(np.int32) * 127 + 127) // 255)
        self.assertTrue(np.array_equal(output[6, 10], expected))
        self.assertTrue(result["frames"][0]["background_outside_alpha_exact"])
        self.assertEqual(result["frames"][0]["hard_alpha_adjacencies"], 0)
        self.assertEqual(result["frames"][0]["key_color_visible_pixels"], 0)
        self.assertIsNone(result["video_preview"])
        self.assertEqual(digest(self.plate), self.recipe["plate"]["asset"]["sha256"])
        self.assertEqual(digest(self.frame), self.recipe["frames"][0]["sha256"])

    def test_replay_identical_bytes_independent_output_folder(self):
        first = composite(self.recipe_path, self.root / "first")
        second = composite(self.recipe_path, self.root / "second")
        self.assertEqual(first, second)
        self.assertEqual(
            digest(self.root / "first" / "frame_000000.png"),
            digest(self.root / "second" / "frame_000000.png"),
        )
        self.assertEqual(
            digest(self.root / "first" / "composite_report.json"),
            digest(self.root / "second" / "composite_report.json"),
        )

    def test_edge_and_key_spill_hold_without_form_approval(self):
        fg = np.asarray(Image.open(self.frame)).copy()
        fg[0, 0] = [0, 255, 0, 255]
        fg[11, 15] = [0, 255, 0, 255]
        Image.fromarray(fg, "RGBA").save(self.frame)
        self.recipe["frames"][0]["sha256"] = digest(self.frame)
        self._write_recipe()
        result = composite(self.recipe_path, self.root / "bad")
        self.assertEqual(result["status"], "QA_FLAGGED_EXPERIMENTAL_HOLD")
        self.assertIn("MASK_NEAR_IMAGE_EDGE", result["warning_codes"])
        self.assertIn("KEY_COLOR_IN_FOREGROUND", result["warning_codes"])
        self.assertEqual(result["frames"][0]["key_color_visible_pixels"], 2)
        self.assertEqual(result["exercise_form"], "NOT_EVALUATED")

    def test_independently_annotated_alpha_points_catch_missing_cutout(self):
        # Geometry/alpha presence only. This cannot diagnose an inverted or
        # duplicated photographic wrist or prove anatomical correctness.
        self.recipe["frames"][0]["required_alpha_points"] = [
            {"label": "synthetic_hand", "x": 12, "y": 9, "min_alpha": 200},
            {"label": "synthetic_foot", "x": 2, "y": 20, "min_alpha": 120},
        ]
        self._write_recipe()
        report = composite(self.recipe_path, self.root / "alpha_points")
        self.assertIn("REQUIRED_ALPHA_POINT_MISSING", report["warning_codes"])
        self.assertEqual(
            report["frames"][0]["missing_required_alpha_point_labels"],
            ["synthetic_foot"],
        )
        self.assertEqual(report["frames"][0]["required_alpha_points_checked"], 2)
        self.assertEqual(report["exercise_form"], "NOT_EVALUATED")

    def test_opaque_thigh_roi_catches_internal_alpha_hole(self):
        # A synthetic opaque body region with an interior matte dropout.
        # The ROI is independent annotation; no anatomy is inferred by code.
        fg = np.asarray(Image.open(self.frame)).copy()
        fg[10:12, 14:16, 3] = 0
        Image.fromarray(fg, "RGBA").save(self.frame)
        self.recipe["frames"][0]["sha256"] = digest(self.frame)
        self.recipe["frames"][0]["required_alpha_regions"] = [{
            "label": "synthetic_solid_thigh",
            "bbox_xyxy": [12, 8, 20, 16],
            "min_alpha": 220,
            "max_below_pixels": 0,
        }]
        self._write_recipe()
        report = composite(self.recipe_path, self.root / "hole")
        self.assertIn("REQUIRED_ALPHA_REGION_HOLE", report["warning_codes"])
        self.assertEqual(report["frames"][0]["required_alpha_regions_checked"], 1)
        self.assertEqual(
            report["frames"][0]["failed_required_alpha_regions"],
            [{"label": "synthetic_solid_thigh", "pixels_below_min_alpha": 4}],
        )
        self.assertEqual(report["production_release"], "HOLD")

    def test_bad_roi_coordinates_fail_closed_before_render(self):
        self.recipe["frames"][0]["required_alpha_regions"] = [{
            "label": "impossible",
            "bbox_xyxy": [30, 7, 34, 10],
            "min_alpha": 200,
            "max_below_pixels": 0,
        }]
        self._write_recipe()
        out = self.root / "should_not_be_created"
        with self.assertRaisesRegex(CompositeError, "alpha-region outside image"):
            composite(self.recipe_path, out)
        self.assertFalse(out.exists())

    def test_reject_mismatched_hash_before_output_creation(self):
        self.recipe["frames"][0]["sha256"] = "0" * 64
        self._write_recipe()
        out = self.root / "must_not_exist"
        with self.assertRaisesRegex(CompositeError, "SHA-256-mismatched"):
            composite(self.recipe_path, out)
        self.assertFalse(out.exists())

    def test_reject_unpinned_or_wrong_mode_assets(self):
        self.recipe["frames"][0].pop("sha256")
        self._write_recipe()
        with self.assertRaises(CompositeError):
            composite(self.recipe_path, self.root / "no_hash")
        rgb = np.zeros((24, 32, 3), dtype=np.uint8)
        Image.fromarray(rgb, "RGB").save(self.frame)
        self.recipe["frames"][0]["sha256"] = digest(self.frame)
        self._write_recipe()
        with self.assertRaisesRegex(CompositeError, "exact RGBA PNG"):
            composite(self.recipe_path, self.root / "no_alpha")

    def test_existing_output_directory_is_never_reused(self):
        out = self.root / "existing"
        out.mkdir()
        sentinel = out / "keep.txt"
        sentinel.write_text("unchanged")
        self.assertEqual(main([str(self.recipe_path), "--out", str(out)]), 2)
        self.assertEqual(sentinel.read_text(), "unchanged")

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires ffmpeg")
    def test_h264_preview_reencode_determinism_and_no_audio(self):
        # A second frame represents synthetic movement; no photographic data.
        second = self.root / "foreground2.png"
        fg = np.asarray(Image.open(self.frame)).copy()
        fg[:, :, 3] = np.roll(fg[:, :, 3], 2, axis=1)
        Image.fromarray(fg, "RGBA").save(second)
        self.recipe["frames"].append({"path": str(second), "sha256": digest(second)})
        self._write_recipe()
        first = composite(self.recipe_path, self.root / "encoded1", encode_mp4=True)
        second_run = composite(self.recipe_path, self.root / "encoded2", encode_mp4=True)
        video = first["video_preview"]
        self.assertEqual(video["frame_count_decoded"], 2)
        self.assertEqual(video["audio_streams"], 0)
        self.assertFalse(video["stream_copy"])
        self.assertFalse(video["bit_exact_across_toolchain_versions"])
        self.assertEqual(video, second_run["video_preview"])
        self.assertEqual(
            digest(self.root / "encoded1" / "composite_preview.mp4"),
            digest(self.root / "encoded2" / "composite_preview.mp4"),
        )


if __name__ == "__main__":
    unittest.main()
