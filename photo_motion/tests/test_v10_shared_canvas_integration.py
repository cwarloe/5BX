"""Real, fully synthetic A/C/canvas composition -> V10 byte replay preflight."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photo_motion import preflight_v10_shared_canvas as v10
from photo_motion.shared_canvas import compose


class V10RealReplayTests(unittest.TestCase):
    def test_recomposition_and_qa_binding_with_synthetic_images(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            files = {}
            for name, format_name, size, color in (
                    ("A", "PNG", (1280, 720), "red"),
                    ("C", "PNG", (1280, 720), "blue"),
                    ("canvas", "JPEG", (1344, 756), "gray")):
                file = root / f"{name}.{format_name.lower()}"
                Image.new("RGB", size, color).save(file, format=format_name)
                files[name] = file
            source_hashes = {key: hashlib.sha256(path.read_bytes()).hexdigest()
                             for key, path in files.items()}
            annotations = {}
            for name in ("A", "C", "canvas"):
                annotation = root / f"{name}.annotation.json"
                annotation.write_text(json.dumps({
                    "schema_version": 1, "role": name,
                    "source_image_sha256": source_hashes[name],
                    "image_size": [1344, 756] if name == "canvas" else [1280, 720],
                    "reviewer": "synthetic-bounds-author", "coverage": "ALL_VISIBLE_PERSON_PIXELS",
                    "confidence": "OPERATOR_DECLARED",
                    "subject_bounds_half_open": [560, 300, 800, 650] if name == "canvas"
                        else [500, 200, 740, 600],
                }))
                annotations[name] = annotation
            manifest = compose(
                files["A"], files["C"], files["canvas"], root,
                a_sha=source_hashes["A"], c_sha=source_hashes["C"],
                canvas_sha=source_hashes["canvas"],
                a_annotation=annotations["A"], c_annotation=annotations["C"],
                canvas_annotation=annotations["canvas"],
                scale_num=37, scale_den=50, x=200, y=172,
                window=(355, 172, 1020, 705), feather=(55, 5, 18),
            )
            manifest_file = root / "shared_canvas.manifest.json"
            manifest_sha = hashlib.sha256(manifest_file.read_bytes()).hexdigest()
            output_hashes = {key: manifest["outputs"][key]["sha256"] for key in ("A", "C")}
            report = root / "independent-qa.json"
            report.write_text(json.dumps({
                "schema_version": 1,
                "authority": "V10_SHARED_CANVAS_INDEPENDENT_QA",
                "manifest_sha256": manifest_sha,
                "source_sha256": source_hashes,
                "output_sha256": output_hashes,
                "producer": "synthetic-producer", "reviewer": "synthetic-independent-reviewer",
                "decision": "CANDIDATE_FOR_DIAGNOSTIC_ONLY",
                "checks": {name: {"verdict": "PASS", "evidence": "Synthetic full deterministic replay, no real form claim"}
                           for name in v10.QA_CHECKS},
                "anatomical_left_right_proven": False,
                "exercise_form": "NOT_EVALUATED",
                "video_motion_and_release": "NOT_EVALUATED",
            }))
            spec = root / "v10.json"
            with patch.object(v10, "SOURCE_SHA256", source_hashes):
                spec.write_text(json.dumps(v10._expected_spec("A_TO_C")))
                result = v10.verify_segment(
                    spec, files["A"], files["C"], files["canvas"], manifest_file,
                    root / "A_shared_canvas.png", root / "C_shared_canvas.png",
                    a_annotation=annotations["A"], c_annotation=annotations["C"],
                    canvas_annotation=annotations["canvas"],
                    independent_qa_report=report, expected_role="A_TO_C",
                )
                self.assertEqual(result["deterministic_replay"], "EXACT_BYTE_REPLAY_PASS")
                self.assertEqual(result["shared_canvas_manifest_sha256"], manifest_sha)
                self.assertEqual(result["start_sha256"], output_hashes["A"])
                self.assertEqual(result["end_sha256"], output_hashes["C"])
                self.assertEqual(result["video_motion_form_and_release_approval"], "NOT_EVALUATED")


if __name__ == "__main__":
    unittest.main()
