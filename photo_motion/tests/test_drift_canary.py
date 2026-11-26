"""Synthetic-only canary controls; no provider, videos, or owner approvals."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from photo_motion import drift_canary, experiments


def intent(*, attempt="run-a", model="model-1", provider="Google Flow",
           prompt="prompthash", spec="a", identity="b", verification="rehashed_from_local_bytes",
           settings=None, exercise="chart1-scissor-jump", preflight=None):
    request = {
        "schema_version": 1, "attempt_key": attempt,
        "exercise_id": exercise,
        "spec_sha256": spec * 64, "spec_reference": "chart1-scissor-jump.json",
        "submitted_prompt": prompt,
        "submitted_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "input_assets": [{"role": "start-frame", "locator": "private://image",
                          "sha256": identity * 64, "verification": verification}],
        "provider": provider, "model": model,
        "settings": settings if settings is not None else {"duration_seconds": 6, "seed": None},
        "estimated_credits": "8", "source_preflight": preflight,
    }
    digest = hashlib.sha256(experiments._canonical(request)).hexdigest()
    return {"schema_version": 1, "run_id": digest, "request_fingerprint": digest,
            "estimated_credits": "8", "release_status": experiments.HOLD,
            "request": request, "created_at_utc": "2026-11-26T01:00:00+00:00"}


def inspection(source, *, width=1280, warning=None):
    req = source["request"]
    return {
        "tool": "photo_motion.video_qa", "source_video_sha256": "c" * 64,
        "spec_sha256": req["spec_sha256"],
        "video": {"duration_seconds": 6, "fps": 24, "width": width,
                  "height": 720, "codec": "h264", "pixel_format": "yuv420p",
                  "audio_stream_count": 0},
        "technical_warnings": [warning] if warning else [],
        "generation_provenance": {
            "provider": req["provider"], "model": req["model"],
            "exact_submitted_prompt_sha256": req["submitted_prompt_sha256"],
            "input_images": [{"role": "start-frame", "sha256": req["input_assets"][0]["sha256"]}],
            "warnings": []},
        "form_and_release_approval": "NOT_EVALUATED",
    }


class DriftCanaryTests(unittest.TestCase):
    def test_equivalent_configuration_does_not_claim_media_or_form_pass(self):
        baseline = intent()
        candidate = intent(attempt="run-b")
        result = drift_canary.compare(baseline, candidate)
        self.assertEqual(result["configuration"], "UNCHANGED")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["form_verdict"], "NOT_ASSESSED")
        self.assertEqual(result["release_verdict"], "NO_AUTOMATIC_APPROVAL")
        self.assertEqual(result["video_validation"], "NOT_PROVIDED")

    def test_model_and_input_change_trigger_requalification(self):
        result = drift_canary.compare(intent(), intent(attempt="other", model="model-2", identity="d"))
        self.assertEqual(result["configuration"], "REQUALIFICATION_REQUIRED")
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual({i["field"] for i in result["changes"]}, {"model", "input_assets"})

    def test_all_operational_change_fields_are_tracked(self):
        changed = intent(attempt="new", provider="Grok Imagine", prompt="another prompt", spec="f",
                         settings={"duration_seconds": 10, "seed": None})
        fields = {item["field"] for item in drift_canary.compare(intent(), changed)["changes"]}
        self.assertEqual(fields, {"provider", "submitted_prompt_sha256", "spec_sha256", "settings"})

    def test_unverified_remote_asset_cannot_be_reported_as_stable(self):
        result = drift_canary.compare(intent(), intent(attempt="retry", verification="declared_unverified"))
        self.assertEqual(result["exit_code"], 1)
        self.assertTrue(result["source_warnings"])

    def test_changed_original_or_transform_manifest_requires_requalification(self):
        baseline = intent(preflight={"original_v6_card_sha256": "a" * 64,
                                     "preparation_manifest_sha256": "b" * 64})
        changed = intent(attempt="retry", preflight={"original_v6_card_sha256": "a" * 64,
                                                          "preparation_manifest_sha256": "c" * 64})
        result = drift_canary.compare(baseline, changed)
        self.assertIn("source_preflight", {row["field"] for row in result["changes"]})
        self.assertEqual(result["exit_code"], 1)

    def test_tampered_immutable_intent_fails_closed(self):
        broken = intent()
        broken["request"]["model"] = "tampered"
        with self.assertRaisesRegex(drift_canary.CanaryError, "fingerprint"):
            drift_canary.compare(broken, intent(attempt="other"))

    def test_mismatched_exercise_cannot_be_compared(self):
        with self.assertRaisesRegex(drift_canary.CanaryError, "different exercises"):
            drift_canary.compare(intent(), intent(attempt="other", exercise="chart1-kneeling-pushup"))

    def test_technical_changes_and_warnings_are_not_form_verdicts(self):
        baseline = intent()
        candidate = intent(attempt="other")
        result = drift_canary.compare(baseline, candidate,
                                      baseline_inspection=inspection(baseline),
                                      candidate_inspection=inspection(candidate, width=1920,
                                                                      warning="frame drop"))
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual(result["video_validation"], "TECHNICAL_REQUALIFICATION_REQUIRED")
        self.assertIn("video.width", {item["field"] for item in result["changes"]})
        self.assertEqual(result["form_verdict"], "NOT_ASSESSED")

    def test_inspection_must_bind_to_intent(self):
        baseline = intent()
        candidate = intent(attempt="other")
        bad = inspection(candidate)
        bad["spec_sha256"] = "d" * 64
        with self.assertRaisesRegex(drift_canary.CanaryError, "spec_sha256"):
            drift_canary.compare(baseline, candidate,
                                 baseline_inspection=inspection(baseline), candidate_inspection=bad)
        bad = inspection(candidate)
        bad["generation_provenance"]["input_images"].append("malformed dangling input")
        with self.assertRaisesRegex(drift_canary.CanaryError, "inspection inputs"):
            drift_canary.compare(baseline, candidate,
                                 baseline_inspection=inspection(baseline), candidate_inspection=bad)

    def test_no_single_inspection_or_forged_approval(self):
        baseline = intent()
        with self.assertRaisesRegex(drift_canary.CanaryError, "both inspections"):
            drift_canary.compare(baseline, intent(attempt="other"),
                                 baseline_inspection=inspection(baseline))
        fake = inspection(baseline)
        fake["form_and_release_approval"] = "APPROVED"
        with self.assertRaisesRegex(drift_canary.CanaryError, "NOT_EVALUATED"):
            drift_canary.compare(baseline, intent(attempt="other"),
                                 baseline_inspection=fake,
                                 candidate_inspection=inspection(intent(attempt="other")))

    def test_cli_json_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline = Path(tmp) / "baseline.json"
            candidate = Path(tmp) / "candidate.json"
            baseline.write_text(json.dumps(intent()), encoding="utf-8")
            candidate.write_text(json.dumps(intent(attempt="other", model="model-2")), encoding="utf-8")
            self.assertEqual(drift_canary.main(["compare", str(baseline), str(candidate), "--json"]), 1)
            candidate.write_text("{bad", encoding="utf-8")
            self.assertEqual(drift_canary.main(["compare", str(baseline), str(candidate), "--json"]), 2)


if __name__ == "__main__":
    unittest.main()
