"""Synthetic-only V15 Video Ingredients method gate/ledger negative controls."""

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from photo_motion import experiments
from photo_motion import preflight_v15_synthetic as v15


def digest(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()


class V15SyntheticPrecreditTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="v15-test-fixtures-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.image = self.root / "synthetic-identity.png"
        self.image.write_bytes(b"SYNTHETIC PHOTO PLACEHOLDER, NOT REAL HUMAN")
        self.movie = self.root / "synthetic-guide.mp4"
        self.movie.write_bytes(b"SYNTHETIC VIDEO PLACEHOLDER, NOT REAL VIDEO")
        self.spec = self.root / "synthetic-spec.json"
        self.prompt = self.root / "synthetic-prompt.txt"
        self.prompt.write_bytes(b"SYNTHETIC EXPERIMENTAL TEST PROMPT")
        self.screenshot = self.root / "synthetic-screenshot.bin"
        self.screenshot.write_bytes(b"SYNTHETIC UI EVIDENCE NEVER FROM GOOGLE FLOW")
        self.ui_path = self.root / "synthetic-ui.json"
        self.store = self.root / "synthetic-ledger"
        experiments.initialize(self.store, provider="Google Flow", credit_limit="10",
                               opening_spent_credits="0")
        for key, value in (("IMAGE_SHA256", digest(self.image)),
                           ("GUIDE_SHA256", digest(self.movie)),
                           ("PROMPT_SHA256", digest(self.prompt))):
            ctx = patch.object(v15, key, value)
            ctx.start()
            self.addCleanup(ctx.stop)
        self.spec.write_text(json.dumps(v15.expected_spec()))
        self.sources = {"v10_source_paths": {k: str(self.image) for k in v15.v14.V10_PATHS},
                        "motion_guide_mp4": str(self.movie), "motion_guide_replay_mp4": str(self.movie),
                        "motion_sidecar": str(self.movie), "motion_replay_sidecar": str(self.movie),
                        "motion_qa_report": str(self.movie), "motion_generator_script": str(self.movie)}
        source_ctx = patch.object(v15, "verify_sources", side_effect=lambda s, p: {
            "authority": v15.AUTHORITY, "spec_sha256": digest(self.spec),
            "identity_image_sha256": digest(self.image),
            "motion_video_sha256": digest(self.movie),
            "photographic_identity_source_replay": "EXACT_BYTE_REPLAY_PASS",
            "motion_guide_replay": "TWO_INDEPENDENT_BYTE_IDENTICAL_RENDERS",
            "video_motion_form_and_release_approval": "NOT_GRANTED"})
        source_ctx.start()
        self.addCleanup(source_ctx.stop)
        ledger_ctx = patch.object(v15, "verify_existing_ledger", side_effect=lambda store: {
            f"ledger_{k}": experiments.snapshot(store)[k]
            for k in ("actual_credits", "pending_reserved_credits", "available_credits")})
        ledger_ctx.start()
        self.addCleanup(ledger_ctx.stop)
        self.ui = {
            "schema_version": 1, "authority": v15.UI_AUTHORITY,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "operator": "synthetic fixture operator", "provider": "Google Flow",
            "model": v15.MODEL, "settings": deepcopy(v15.SETTINGS),
            "quoted_credits": "2.5", "identity_tile": {
                "asset_kind": "image", "source_sha256": digest(self.image),
                "flow_asset_id": "synthetic-image", "visually_confirmed": True},
            "motion_video_tile": {
                "asset_kind": "video", "source_sha256": digest(self.movie),
                "flow_asset_id": "synthetic-video", "visually_confirmed": True},
            "only_two_ingredients_selected": True, "no_frames_endpoints": True,
            "post_asset_quote_confirmed": True, "project_silent_setting_on": True,
            "ledger_reconciled": True, "ledger_actual_credits": "0",
            "ledger_pending_reserved_credits": "0", "ledger_available_credits": "10",
            "ui_evidence_path": str(self.screenshot),
            "ui_evidence_sha256": digest(self.screenshot),
        }
        self.write_ui()
        self.request = {
            "schema_version": 1, "attempt_key": "synthetic-v15-001",
            "exercise_id": "chart1-scissor-jump", "spec_path": str(self.spec),
            "submitted_prompt_file": str(self.prompt), "input_assets": [
                {"role": "identity-image", "locator": "synthetic-image", "local_path": str(self.image),
                 "sha256": digest(self.image)},
                {"role": "motion-reference-video", "locator": "synthetic-video", "local_path": str(self.movie),
                 "sha256": digest(self.movie)},
            ], "provider": "Google Flow", "model": v15.MODEL,
            "settings": deepcopy(v15.SETTINGS), "estimated_credits": "2.5",
            "source_preflight": {"authority": v15.AUTHORITY, "source_paths": self.sources,
                                 "existing_ledger_store": str(self.store),
                                 "flow_ui_observation": str(self.ui_path)},
        }

    def write_ui(self):
        self.ui_path.write_text(json.dumps(self.ui))

    def reject(self, message):
        with self.assertRaisesRegex((experiments.ExperimentError, v15.V15PreflightError), message):
            experiments._validate_request(self.request)

    def test_mocked_sources_live_quote_and_reserve_still_hold_for_form(self):
        checked = experiments._validate_request(self.request)
        self.assertEqual(checked["estimated_credits"], "2.5")
        self.assertEqual(checked["source_preflight"]["video_motion_form_and_release_approval"], "NOT_GRANTED")
        intent = experiments.reserve(self.store, self.request)
        self.assertEqual(intent["release_status"], experiments.HOLD)
        self.assertEqual(experiments.snapshot(self.store)["pending_reserved_credits"], "2.5")

    def test_source_roles_rehash_required_and_no_extra_third_asset(self):
        self.request["input_assets"].reverse()
        self.reject("exactly two ordered")
        self.request["input_assets"].reverse()
        self.request["input_assets"].append(self.request["input_assets"][0])
        self.reject("exactly two ordered")
        self.request["input_assets"].pop()
        self.request["input_assets"][1].pop("local_path")
        self.reject("locally rehashed")

    def test_prompt_and_spec_exact_pins(self):
        self.prompt.write_bytes(self.prompt.read_bytes() + b" paraphrase")
        self.reject("preregistered")
        self.prompt.write_bytes(b"SYNTHETIC EXPERIMENTAL TEST PROMPT")
        self.spec.write_text(self.spec.read_text().replace("Ingredients", "Frames to Video"))
        with patch.object(v15, "verify_sources", side_effect=v15.V15PreflightError("V15 specification/prompt/source pins differ")):
            self.reject("specification/prompt/source pins differ")

    def test_wrong_model_mode_settings_or_output_count_holds(self):
        for key, bad in (("generation_mode", "Frames to Video"), ("resolution", "720p"),
                         ("variants", 2), ("variants", True), ("return_silent_videos", False)):
            with self.subTest(key=key, bad=bad):
                old = self.ui["settings"][key]
                self.ui["settings"][key] = bad
                self.write_ui()
                self.reject("model/mode/settings")
                self.ui["settings"][key] = old
        self.ui["model"] = "unverified model"
        self.write_ui()
        self.reject("model/mode/settings")

    def test_missing_post_asset_price_or_selection_is_not_authority(self):
        for key in ("post_asset_quote_confirmed", "only_two_ingredients_selected",
                    "no_frames_endpoints", "project_silent_setting_on", "ledger_reconciled"):
            with self.subTest(key=key):
                self.ui[key] = False
                self.write_ui()
                self.reject("model/mode/settings")
                self.ui[key] = True
        for bad in ("0", "4", "-1", "not observed"):
            with self.subTest(quote=bad):
                self.ui["quoted_credits"] = bad
                self.write_ui()
                self.reject("positive fresh")

    def test_selected_photo_video_identity_and_dupe_flow_assets(self):
        for tile, key, bad in (("identity_tile", "asset_kind", "video"),
                               ("motion_video_tile", "asset_kind", "image"),
                               ("motion_video_tile", "source_sha256", digest(self.image)),
                               ("motion_video_tile", "visually_confirmed", False)):
            with self.subTest(tile=tile, key=key):
                old = self.ui[tile][key]
                self.ui[tile][key] = bad
                self.write_ui()
                self.reject("selected exact visual source")
                self.ui[tile][key] = old
        self.ui["motion_video_tile"]["flow_asset_id"] = "synthetic-image"
        self.write_ui()
        self.reject("distinct")

    def test_live_quote_and_settings_cannot_be_inferred_from_request(self):
        self.request["estimated_credits"] = "3"
        self.reject("fresh single-output")
        self.request["estimated_credits"] = "2.5"
        self.request["settings"]["duration_seconds"] = 6
        self.reject("fresh single-output")

    def test_expired_future_non_utc_observation_fails(self):
        for when in (datetime.now(timezone.utc) - timedelta(minutes=16),
                     datetime.now(timezone.utc) + timedelta(minutes=2), datetime.now()):
            with self.subTest(time=when.isoformat()):
                self.ui["observed_at_utc"] = when.isoformat()
                self.write_ui()
                self.reject("stale/future/non-UTC")

    def test_screenshot_or_duplicate_json_field_tampering_holds(self):
        self.screenshot.write_bytes(self.screenshot.read_bytes() + b"bad")
        self.reject("screenshot")
        self.screenshot.write_bytes(b"SYNTHETIC UI EVIDENCE NEVER FROM GOOGLE FLOW")
        self.ui_path.write_text(self.ui_path.read_text()[:-1] + ',"quoted_credits":"2.5"}')
        self.reject("duplicate")

    def test_ledger_quote_balance_drift_and_wrong_ledger_holds(self):
        self.ui["ledger_available_credits"] = "999"
        self.write_ui()
        self.reject("ledger snapshot")
        self.ui["ledger_available_credits"] = "10"
        self.write_ui()
        new_ledger = self.root / "second-ledger"
        experiments.initialize(new_ledger, provider="Google Flow", credit_limit="10",
                               opening_spent_credits="0")
        with self.assertRaisesRegex(experiments.ExperimentError, "SAME existing"):
            experiments.reserve(new_ledger, self.request)
        other_spec = self.root / "other.json"
        other_spec.write_text('{"synthetic":true}')
        other_prompt = self.root / "other-prompt.txt"
        other_prompt.write_text("SYNTHETIC OTHER")
        other = {"schema_version": 1, "attempt_key": "synthetic-unrelated",
                 "exercise_id": "non-scissor", "spec_path": str(other_spec),
                 "submitted_prompt_file": str(other_prompt),
                 "input_assets": [{"role": "image", "locator": "synthetic",
                                   "local_path": str(self.image), "sha256": digest(self.image)}],
                 "provider": "Google Flow", "model": "synthetic",
                 "settings": {"variants": 1}, "estimated_credits": "1"}
        experiments.reserve(self.store, other)
        with self.assertRaisesRegex(experiments.ExperimentError, "ledger snapshot drifted|live quote/ledger changed"):
            experiments.reserve(self.store, self.request)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg tools unavailable")
class V15SyntheticVideoIntakeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="v15-synthetic-video-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def render(self, source):
        video = self.root / f"synthetic-{source}.mp4"
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                   "-f", "lavfi", "-i", f"{source}=size=640x360:rate=24:duration=3",
                   "-frames:v", "72", "-c:v", "libx264", "-threads", "1",
                   "-qp", "18", "-preset", "medium", "-profile:v", "high",
                   "-pix_fmt", "yuv420p", "-an", str(video)]
        subprocess.run(command, check=True, capture_output=True)
        return video

    def test_full_decode_no_audio_and_exact_static_rgb_loop(self):
        video = self.render("color")
        info = v15.verify_guide_video(video, expected_sha=digest(video))
        self.assertEqual(info["frame_count"], 72)
        self.assertEqual(info["decoded_rgb_loop_seam"], "EXACT")

    def test_animated_synthetic_rgb_loop_seam_is_rejected(self):
        video = self.render("testsrc2")
        with self.assertRaisesRegex(v15.V15PreflightError, "seam differs"):
            v15.verify_guide_video(video, expected_sha=digest(video))

    def test_truncated_mp4_is_rejected_even_with_matching_hash(self):
        video = self.render("color")
        video.write_bytes(video.read_bytes()[:128])
        with self.assertRaisesRegex(v15.V15PreflightError, "ffprobe failed"):
            v15.verify_guide_video(video, expected_sha=digest(video))

    def test_digest_mismatch_rejected_before_probe(self):
        video = self.render("color")
        with self.assertRaisesRegex(v15.V15PreflightError, "SHA mismatch"):
            v15.verify_guide_video(video)


if __name__ == "__main__":
    unittest.main()
