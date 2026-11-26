"""Synthetic-only first-party adult reference intake regression tests."""

import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from photo_motion import human_motion_reference_intake as gate
from photo_motion.video_qa import file_sha256


TIMES = [round(n / 60, 7) for n in range(660)]
PHASE_FRAMES = [30, 100, 170, 240, 310, 380, 450, 520, 590]
INTERVAL_FRAMES = [(99, 101), (239, 241), (379, 381), (519, 521)]


def synthetic_locator(component):
    # Never embed even example private archive URIs in public Git diffs.
    return "private" + "://" + "5bx/synthetic/" + component


def fixture(original, review, release, location):
    phases = []
    for phase, frame in zip(gate.PHASES, PHASE_FRAMES):
        airborne = phase[0] in "BD"
        is_a = phase[0] == "A"
        phases.append({"id": phase, "frame_number": frame, "timestamp_seconds": TIMES[frame],
                       "support": "BOTH_SHOES_ENTIRELY_AIRBORNE" if airborne else "BOTH_SHOES_GROUNDED",
                       "right_leg": "EXCHANGING" if airborne else ("FORWARD" if is_a else "BACK"),
                       "left_leg": "EXCHANGING" if airborne else ("BACK" if is_a else "FORWARD"),
                       "right_arm": "EXCHANGING" if airborne else ("BACK" if is_a else "FORWARD"),
                       "left_arm": "EXCHANGING" if airborne else ("FORWARD" if is_a else "BACK")})
    intervals = [{"id": phase, "first_frame": first, "last_frame": last,
                  "first_timestamp_seconds": TIMES[first], "last_timestamp_seconds": TIMES[last],
                  "both_entire_outsoles_clear_every_frame": True}
                 for phase, (first, last) in zip(gate.FLIGHTS, INTERVAL_FRAMES)]
    return {
        "schema_version": 1, "capture_id": "C1-EX5-HUMAN-MOTION-TEST-001",
        "status": "EXPERIMENTAL_NOT_FORM_APPROVED", "captured_at_utc": "2026-11-26T11:00:00Z",
        "recorded_local_timezone": "America/Toronto",
        "source": {"locator": synthetic_locator("camera-original"), "sha256": file_sha256(original),
                   "bytes": original.stat().st_size, "codec": "h264", "width": 1920, "height": 1080,
                   "fps_reported": "60/1", "fps_measured": "60/1", "decoded_frames": 660,
                   "duration_seconds": 11.0, "rotation_degrees": 0,
                   "camera_original_reviewed_by": "Jordan SyntheticReviewer", "camera_original_unmodified": True},
        "setup": {"camera_model": "Synthetic test camera", "camera_side_relative_to_performer": "PERFORMER_RIGHT",
                  "camera_locked": "MANUALLY_VERIFIED", "focus_exposure_white_balance_locked": "MANUALLY_VERIFIED",
                  "full_body_margin_review": "MANUALLY_VERIFIED", "side_on_view_review": "MANUALLY_VERIFIED",
                  "static_background_review": "MANUALLY_VERIFIED", "ground_contact_plane_review": "MANUALLY_VERIFIED",
                  "no_bystanders_or_minors_review": "MANUALLY_VERIFIED",
                  "no_private_conversations_review": "MANUALLY_VERIFIED"},
        "human_motion_evidence": {
            "reviewer_full_name": "Alex SyntheticReviewer", "reviewed_at_utc": "2026-11-26T12:00:00Z",
            "review_evidence_locator": synthetic_locator("review"), "review_evidence_sha256": file_sha256(review),
            "nine_checkpoints": phases, "four_distinct_both_shoes_airborne_frame_intervals": intervals,
            "all_frames_head_and_shoes_visible": "MANUALLY_VERIFIED",
            "anatomical_side_continuity": "MANUALLY_VERIFIED", "technical_motion_verdict": "PASS",
            "form_and_safety_verdict": "NOT_EVALUATED"},
        "rights": {
            "performer_is_adult_18_plus": True, "performer_release_locator": synthetic_locator("release"),
            "performer_release_sha256": file_sha256(release), "performer_release_signed_and_dated": True,
            "consent_reviewer_full_name": "Taylor SyntheticReviewer", "consent_reviewed_at_utc": "2026-11-26T12:01:00Z",
            "permitted_filming_and_private_storage": True, "permitted_editing_and_technical_analysis": True,
            "permitted_ai_provider_upload": ["Google Flow"], "permitted_derivatives": True,
            "permitted_public_educational_commercial_use": True,
            "permitted_likeness_transfer": False, "permitted_voice_or_biometric_transfer": False,
            "permitted_liveness_testing": False, "permitted_purpose": "MOTION_ONLY_NOT_IDENTITY",
            "withdrawal_terms_recorded": True, "location_permission_status": "NONE_REQUIRED_DOCUMENTED",
            "location_evidence_locator": synthetic_locator("location"),
            "location_evidence_sha256": file_sha256(location)},
        "release": "HOLD_FOR_CHARLES_EXACT_VIDEO_REVIEW"}


class FirstPartyHumanIntakeTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="5bx-synthetic-human-intake-")
        self.addCleanup(self.folder.cleanup)
        root = Path(self.folder.name)
        self.original = root / "camera_original.MOV"
        self.review = root / "synthetic-review-evidence.txt"
        self.release = root / "synthetic-release-evidence.txt"
        self.location = root / "synthetic-location-evidence.txt"
        for path, value in ((self.original, b"synthetic camera bytes: NOT HUMAN VIDEO"),
                            (self.review, b"synthetic TEST ONLY review"),
                            (self.release, b"synthetic TEST ONLY release"),
                            (self.location, b"synthetic TEST ONLY location determination")):
            path.write_bytes(value)
        self.receipt = fixture(self.original, self.review, self.release, self.location)

    def _inspector(self, path):
        return {"sha256": file_sha256(path), "bytes": path.stat().st_size,
                "codec": "h264", "width": 1920, "height": 1080,
                "fps_measured": "60/1", "decoded_frames": 660,
                "duration_seconds": 11.0, "rotation_degrees": 0, "times": TIMES}

    def verdict(self, receipt=None, inspector=None, **kwargs):
        options = {"source_path": self.original, "release_path": self.release,
                   "review_path": self.review, "location_path": self.location,
                   "inspector": inspector or self._inspector}
        options.update(kwargs)
        return gate.evaluate(receipt if receipt is not None else self.receipt, **options)

    def assertBlocked(self, receipt=None, phrase=None, **kwargs):
        result = self.verdict(receipt, **kwargs)
        self.assertEqual(result["decision"], "NOT_EVALUATED", result)
        self.assertFalse(result["provider_upload_authorized"])
        self.assertFalse(result["form_correctness_approved"])
        self.assertFalse(result["public_release_authorized"])
        if phrase:
            self.assertIn(phrase, " ".join(result["blockers"]))

    def test_complete_synthetic_fixture_reaches_only_reference_candidate(self):
        result = self.verdict()
        self.assertEqual(result["decision"], "CAPTURE_REFERENCE_CANDIDATE", result)
        self.assertTrue(result["source_bytes_verified"])
        self.assertTrue(result["full_decode_and_timing_verified"])
        self.assertTrue(result["human_review_evidence_bytes_verified"])
        self.assertTrue(result["signed_release_bytes_verified"])
        self.assertTrue(result["location_permission_evidence_bytes_verified"])
        self.assertFalse(result["provider_upload_authorized"])
        self.assertFalse(result["form_correctness_approved"])
        self.assertFalse(result["public_release_authorized"])
        self.assertNotIn(str(self.original), json.dumps(result))
        self.assertNotIn("SyntheticReviewer", json.dumps(result))

    def test_receipt_schema_fail_closed_and_untrusted_approval(self):
        for mutate in (lambda r: r.update({"owner_approved": True}),
                       lambda r: r.pop("rights"),
                       lambda r: r.update({"schema_version": True}),
                       lambda r: r.update({"release": "ACCEPT"}),
                       lambda r: r.update({"status": "FORM_APPROVED"}),
                       lambda r: r["rights"].update({"future_use": "anything"})):
            sample = copy.deepcopy(self.receipt)
            mutate(sample)
            with self.subTest(mutate=mutate):
                self.assertBlocked(sample)

    def test_anatomical_phases_and_timestamp_checked_from_decoded_pts(self):
        def edits(r):
            return r["human_motion_evidence"]["nine_checkpoints"]
        mutations = (
            lambda r: edits(r)[2].update({"id": "A1"}),
            lambda r: edits(r)[2].update({"right_leg": "FORWARD"}),
            lambda r: edits(r)[4].update({"left_arm": "BACK"}),
            lambda r: edits(r)[2].update({"frame_number": 29}),
            lambda r: edits(r)[4].update({"frame_number": 660}),
            lambda r: edits(r)[4].update({"timestamp_seconds": 10.2}),
            lambda r: edits(r)[3].update({"support": "BOTH_SHOES_GROUNDED"}),
            lambda r: edits(r).pop(),
        )
        for mutate in mutations:
            sample = copy.deepcopy(self.receipt)
            mutate(sample)
            with self.subTest(mutate=mutate):
                self.assertBlocked(sample)

    def test_flight_windows_distinct_two_frames_and_around_phase(self):
        def edits(r):
            return r["human_motion_evidence"]["four_distinct_both_shoes_airborne_frame_intervals"]
        mutations = (
            lambda r: edits(r)[1].update({"id": "B0"}),
            lambda r: edits(r)[1].update({"first_frame": 240, "last_frame": 240}),
            lambda r: edits(r)[1].update({"first_frame": 99, "last_frame": 241}),
            lambda r: edits(r)[1].update({"first_frame": 238, "last_frame": 239}),
            lambda r: edits(r)[1].update({"both_entire_outsoles_clear_every_frame": False}),
            lambda r: edits(r)[2].update({"last_timestamp_seconds": 8.5}),
            lambda r: edits(r).pop(),
        )
        for mutate in mutations:
            sample = copy.deepcopy(self.receipt)
            mutate(sample)
            with self.subTest(mutate=mutate):
                self.assertBlocked(sample)

    def test_unverified_motion_or_setup_never_candidate(self):
        for group, field, value in (
            ("setup", "camera_locked", "NOT_EVALUATED"),
            ("setup", "full_body_margin_review", "NOT_EVALUATED"),
            ("human_motion_evidence", "all_frames_head_and_shoes_visible", "NOT_EVALUATED"),
            ("human_motion_evidence", "anatomical_side_continuity", "NOT_EVALUATED"),
            ("human_motion_evidence", "technical_motion_verdict", "FAIL"),
            ("human_motion_evidence", "form_and_safety_verdict", "PASS"),
            ("human_motion_evidence", "reviewer_full_name", "UNKNOWN"),
            ("source", "camera_original_reviewed_by", "REPLACE")):
            sample = copy.deepcopy(self.receipt)
            sample[group][field] = value
            with self.subTest(field=field):
                self.assertBlocked(sample)

    def test_consent_named_provider_and_identity_transfer_never_assumed(self):
        for field, value in (
            ("performer_is_adult_18_plus", False),
            ("performer_release_signed_and_dated", "NOT_EVALUATED"),
            ("permitted_ai_provider_upload", "NOT_EVALUATED"),
            ("permitted_ai_provider_upload", ["Unknown Provider"]),
            ("permitted_ai_provider_upload", []),
            ("permitted_derivatives", False),
            ("permitted_public_educational_commercial_use", "NOT_EVALUATED"),
            ("permitted_likeness_transfer", True),
            ("permitted_voice_or_biometric_transfer", True),
            ("permitted_liveness_testing", True),
            ("permitted_purpose", "IDENTITY_TRANSFER"),
            ("withdrawal_terms_recorded", False),
            ("location_permission_status", "NOT_EVALUATED"),
            ("consent_reviewer_full_name", "Nobody")):
            sample = copy.deepcopy(self.receipt)
            sample["rights"][field] = value
            with self.subTest(field=field, value=value):
                self.assertBlocked(sample)

    def test_actual_hashes_required_not_only_receipt_assertions(self):
        for kw, field in (("source_path", "original"), ("review_path", "review"),
                          ("release_path", "release"), ("location_path", "location")):
            path = getattr(self, field)
            with self.subTest(field=field):
                self.assertBlocked(phrase="file not supplied", **{kw: None})
                link = path.parent / (field + ".linked")
                link.symlink_to(path)
                self.assertBlocked(phrase="bytes", **{kw: link})
        self.original.write_bytes(b"changed original after receipt signed")
        self.assertBlocked(phrase="SHA-256")

    def test_private_archive_and_no_identifying_result(self):
        sample = copy.deepcopy(self.receipt)
        sample["rights"]["performer_release_locator"] = "https://public.example/user"
        self.assertBlocked(sample)
        sample = copy.deepcopy(self.receipt)
        sample["human_motion_evidence"]["review_evidence_sha256"] = "not sha"
        self.assertBlocked(sample)
        # External utility messages containing a private path must not leak.
        def unsafe_inspector(path):
            raise RuntimeError(f"decode failed at private path: {path}")
        result = self.verdict(inspector=unsafe_inspector)
        self.assertEqual(result["decision"], "NOT_EVALUATED")
        self.assertNotIn(str(self.original), json.dumps(result))

    def test_inspected_stream_values_rechecked_not_trusting_receipt(self):
        for field, value in (("codec", "hevc"), ("bytes", 400), ("width", 1080),
                             ("fps_measured", "30/1"), ("decoded_frames", 300),
                             ("duration_seconds", 10.0), ("rotation_degrees", 90)):
            sample = copy.deepcopy(self.receipt)
            sample["source"][field] = value
            with self.subTest(field=field):
                self.assertBlocked(sample)

    def test_probe_detects_variable_pts_even_with_advertised_60fps(self):
        metadata = {"streams": [{"codec_type": "video", "codec_name": "h264",
                                 "avg_frame_rate": "60/1", "r_frame_rate": "60/1",
                                 "width": 1920, "height": 1080}],
                    "format": {"duration": "11.0"}}
        pts = [n / 60 for n in range(660)]
        pts[400] += .01  # Duplicate-like jump masked by nominal FPS metadata.
        frames = {"frames": [{"best_effort_timestamp_time": str(p)} for p in pts]}
        with patch.object(gate, "_run_json", side_effect=[metadata, frames]):
            with self.assertRaisesRegex(ValueError, "decoded PTS"):
                gate.inspect_original(self.original)

    def test_probe_rejects_nonzero_display_rotation(self):
        metadata = {"streams": [{"codec_type": "video", "codec_name": "h264",
                                 "avg_frame_rate": "60/1", "r_frame_rate": "60/1",
                                 "width": 1920, "height": 1080,
                                 "side_data_list": [{"side_data_type": "Display Matrix", "rotation": -90}]}],
                    "format": {"duration": "11.0"}}
        frames = {"frames": [{"best_effort_timestamp_time": str(p)} for p in TIMES]}
        with patch.object(gate, "_run_json", side_effect=[metadata, frames]):
            with self.assertRaisesRegex(ValueError, "rotation"):
                gate.inspect_original(self.original)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg/ffprobe unavailable")
    def test_real_decode_rejects_actual_small_synthetic_video(self):
        small = Path(self.folder.name) / "small-synthetic-not-human.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                        "color=c=blue:s=320x180:r=60:d=1", "-c:v", "libx264", "-threads", "1",
                        "-pix_fmt", "yuv420p", "-y", str(small)],
                       capture_output=True, check=True)
        with self.assertRaisesRegex(ValueError, "shorter than preferred 10s"):
            gate.inspect_original(small)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg/ffprobe unavailable")
    def test_real_ffprobe_full_decode_and_600_frame_pts_on_synthetic_color(self):
        """Exercise *real* subprocesses with no human/private content."""
        original = Path(self.folder.name) / "color-synthetic-not-human.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                        "color=c=blue:s=1920x1080:r=60:d=10", "-c:v", "libx264",
                        "-preset", "ultrafast", "-threads", "1", "-pix_fmt", "yuv420p",
                        "-y", str(original)], capture_output=True, check=True)
        result = gate.inspect_original(original)
        self.assertEqual(result["decoded_frames"], 600)
        self.assertEqual(result["fps_measured"], "60/1")
        self.assertEqual(result["width"], 1920)
        self.assertEqual(result["height"], 1080)
        self.assertEqual(result["sha256"], file_sha256(original))
        self.assertAlmostEqual(result["times"][599], 599 / 60, places=5)


if __name__ == "__main__":
    unittest.main()
