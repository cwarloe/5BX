"""Synthetic, zero-credit regression for distinct 3-second Frames endpoints."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from photo_motion import experiments, preflight_v8_segments as v8


ROOT = Path(__file__).resolve().parents[1]


class V8SegmentTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.a, self.c = self.root / "a.png", self.root / "c.png"
        self.a.write_bytes(b"synthetic-A")
        self.c.write_bytes(b"synthetic-C")
        self.a_sha = hashlib.sha256(self.a.read_bytes()).hexdigest()
        self.c_sha = hashlib.sha256(self.c.read_bytes()).hexdigest()
        self.prompt = self.root / "submitted.txt"
        self.prompt.write_text("Exactly one physical airborne exchange, no fade or audio")
        for key, digest in (("V7_PREPARED_A_SHA256", self.a_sha),
                            ("V7_PREPARED_C_SHA256", self.c_sha)):
            p = patch.object(v8, key, digest)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(v8, "_SEGMENTS", {
            "A_TO_C": ("A", "C", self.a_sha, self.c_sha),
            "C_TO_A": ("C", "A", self.c_sha, self.a_sha),
        })
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(v8, "verify_pair", return_value={
            "prepared_png_sha256": self.a_sha,
            "opposite_pose_reference": {"prepared_png_sha256": self.c_sha},
            "parent_crop_replay_verified": False,
        })
        self.verify_source = p.start()
        self.addCleanup(p.stop)

    def request(self, role):
        filename = "chart1-scissor-v8-a-to-c.json" if role == "A_TO_C" else "chart1-scissor-v8-c-to-a.json"
        spec = json.loads((ROOT / "segment_specs" / filename).read_text())
        spec["start_sha256"] = self.a_sha if role == "A_TO_C" else self.c_sha
        spec["end_sha256"] = self.c_sha if role == "A_TO_C" else self.a_sha
        spec_path = self.root / filename
        spec_path.write_text(json.dumps(spec))
        first, last = (self.a, self.c) if role == "A_TO_C" else (self.c, self.a)
        return {
            "schema_version": 1, "attempt_key": f"synthetic-v8-{role}",
            "exercise_id": "chart1-scissor-jump", "spec_path": str(spec_path),
            "submitted_prompt_file": str(self.prompt),
            "input_assets": [
                {"role": "start-frame", "locator": "synthetic-start", "local_path": str(first)},
                {"role": "end-frame", "locator": "synthetic-end", "local_path": str(last)},
            ],
            "provider": "Google Flow", "model": "Omni 1.2 Flash",
            "settings": {"duration_seconds": 3, "aspect_ratio": "16:9", "variants": 1,
                         "seed": None, "generation_mode": "Frames to Video", "resolution": "720p"},
            "estimated_credits": "9",
            "source_preflight": {"authority": "V8_FRAMES_DIRECT_A_C_SEGMENTS",
                                 "a_png": str(self.a), "c_png": str(self.c), "segment_role": role},
        }

    def test_both_distinct_endpoint_directions_are_qualified(self):
        for role in ("A_TO_C", "C_TO_A"):
            with self.subTest(role=role):
                intent = experiments._validate_request(self.request(role))
                self.assertEqual(intent["source_preflight"]["segment_role"], role)
                self.assertEqual(intent["settings"]["duration_seconds"], 3)
                self.assertEqual([a["role"] for a in intent["input_assets"]], ["start-frame", "end-frame"])
                self.assertTrue(all(a["verification"] == "rehashed_from_local_bytes" for a in intent["input_assets"]))
        self.assertEqual(self.verify_source.call_count, 2)

    def test_swapped_images_and_endpoint_roles_are_rejected(self):
        for change in ("images", "role"):
            with self.subTest(change=change):
                request = self.request("A_TO_C")
                if change == "images":
                    request["input_assets"].reverse()
                else:
                    request["source_preflight"]["segment_role"] = "C_TO_A"
                with self.assertRaisesRegex(ValueError, "endpoint|role"):
                    experiments._validate_request(request)

    def test_mode_duration_and_output_count_cannot_drift(self):
        for key, bad in (("duration_seconds", 6), ("generation_mode", "Ingredients"),
                         ("variants", 2), ("resolution", "1080p")):
            with self.subTest(key=key):
                request = self.request("A_TO_C")
                request["settings"][key] = bad
                with self.assertRaisesRegex(ValueError, "settings|duration"):
                    experiments._validate_request(request)

    def test_unquoted_settings_and_unverified_remote_inputs_are_rejected(self):
        request = self.request("A_TO_C")
        request["settings"]["output_count"] = 10
        with self.assertRaisesRegex(ValueError, "six exact quoted settings"):
            experiments._validate_request(request)
        request = self.request("A_TO_C")
        del request["input_assets"][0]["local_path"]
        request["input_assets"][0]["sha256"] = self.a_sha
        with self.assertRaisesRegex(ValueError, "locally verified"):
            experiments._validate_request(request)


if __name__ == "__main__":
    unittest.main()
