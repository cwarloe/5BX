"""Synthetic-only V13 native-video source and live-Flow-edit reservation gates."""

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
from photo_motion import preflight_v13_v2v as v13
from photo_motion.preflight_v12_apex_frames import FLOW_SETTINGS as V12_SETTINGS


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class V13VideoEditPaidGateTests(unittest.TestCase):
    def setUp(self):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            self.skipTest("ffmpeg and ffprobe required for real synthetic MP4 format test")
        temp = tempfile.TemporaryDirectory(prefix="synthetic-v13-v2v-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.raw = self.root / "synthetic-previous-v12-raw.mp4"
        subprocess.run([
            "ffmpeg", "-v", "error", "-f", "lavfi", "-i",
            "color=c=red:s=640x360:r=24:d=3", "-f", "lavfi", "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100", "-t", "3",
            "-c:v", "libx264", "-crf", "38", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", str(self.raw)], check=True, timeout=30,
            capture_output=True)
        self.scene = "11111111-2222-4333-8444-555555555555"
        self.qa = self.root / "synthetic-private-independent-v12-qa.md"
        self.qa.write_text(f"**Verdict: QA HOLD**\nProvider Flow scene ID `{self.scene}` supplied by agent; original source rehashed.\n")
        self.prompt = self.root / "private-synthetic-arm-edit-prompt.txt"
        self.prompt.write_bytes(b"SYNTHETIC TEST: correct arm trajectory only; never submitted to a provider.\n")
        self.evidence = self.root / "synthetic-edit-screen.txt"
        self.evidence.write_bytes(b"SYNTHETIC: this is NOT an actual Flow screenshot")
        self.observation = self.root / "private-v13-ui.json"
        self.ledger = self.root / "reconciled-private-ledger"
        self.patches = [
            patch.object(v13, "RAW_V12_SHA256", digest(self.raw)),
            patch.object(v13, "V12_QA_SHA256", digest(self.qa)),
            patch.object(v13, "PROMPT_SHA256", digest(self.prompt)),
        ]
        for context in self.patches:
            context.start()
            self.addCleanup(context.stop)
        self._build_native_v12_ledger()
        self.spec = self.root / "v13-spec.json"
        self.spec.write_text(json.dumps(v13.expected_spec()))
        self.ui = {
            "schema_version": 1, "authority": v13.UI_AUTHORITY,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "operator": "synthetic test operator", "provider": "Google Flow",
            "model": v13.FLOW_MODEL, "settings": deepcopy(v13.FLOW_SETTINGS),
            "quoted_credits": "3", "source_scene_id": self.scene,
            "source_video_visible": True, "edit_prompt_interface_visible": True,
            "source_qa_hold_acknowledged": True, "project_silent_setting_on": True,
            "ledger_reconciled": True, "ledger_actual_credits": "3",
            "ledger_pending_reserved_credits": "0", "ledger_available_credits": "3",
            "ui_evidence_path": str(self.evidence),
            "ui_evidence_sha256": digest(self.evidence),
        }
        self.write_ui()
        self.request = {
            "schema_version": 1, "attempt_key": "synthetic-v13-arm-only-001",
            "exercise_id": "chart1-scissor-jump", "spec_path": str(self.spec),
            "submitted_prompt_file": str(self.prompt),
            "input_assets": [{"role": "source-video", "locator": "synthetic V12 MP4",
                              "local_path": str(self.raw), "sha256": digest(self.raw)}],
            "provider": "Google Flow", "model": v13.FLOW_MODEL,
            "settings": deepcopy(v13.FLOW_SETTINGS), "estimated_credits": "3",
            "source_preflight": {
                "authority": v13.AUTHORITY, "raw_v12_video": str(self.raw),
                "independent_v12_qa": str(self.qa),
                "existing_ledger_store": str(self.ledger),
                "flow_ui_observation": str(self.observation),
            },
        }

    def _build_native_v12_ledger(self):
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="6",
                               opening_spent_credits="0")
        original = {
            "schema_version": 1, "attempt_key": "synthetic-previous-v12",
            "exercise_id": "chart1-scissor-jump", "spec_sha256": "a" * 64,
            "spec_reference": "synthetic-v12-spec.json", "submitted_prompt": "synthetic V12 prompt",
            "submitted_prompt_sha256": "b" * 64,
            "input_assets": [
                {"role": "start-frame",
                 "sha256": "777abf5ca478cf03688824f49380cc1a77bb06987bb13a983d1890993fd17a38",
                 "locator": "synthetic-A", "verification": "rehashed_from_local_bytes"},
                {"role": "end-frame",
                 "sha256": "c834cd10a7347d710087666324a785d09b76dbc106edbd1e9b3a713805771886",
                 "locator": "synthetic-B", "verification": "rehashed_from_local_bytes"},
            ],
            "provider": "Google Flow", "model": v13.FLOW_MODEL,
            "settings": deepcopy(V12_SETTINGS), "estimated_credits": "3",
            "source_preflight": {"authority": "V12_REVIEWED_APEX_B002_FRAMES_360P"},
        }
        run_id = hashlib.sha256(experiments._canonical(original)).hexdigest()
        self.run_id = run_id
        context = patch.object(v13, "V12_RUN_ID", run_id)
        context.start()
        self.addCleanup(context.stop)
        intent = {"schema_version": 1, "run_id": run_id,
                  "request_fingerprint": run_id, "created_at_utc": datetime.now(timezone.utc).isoformat(),
                  "release_status": experiments.HOLD, "request": original,
                  "estimated_credits": "3"}
        experiments._create_only(self.ledger / "intents" / f"{run_id}.json", intent)
        charge = {"schema_version": 1, "run_id": run_id, "actual_credits": "3",
                  "provider_generation_id": self.scene, "outcome": "COMPLETED",
                  "release_status": experiments.HOLD, "recorded_at_utc": datetime.now(timezone.utc).isoformat()}
        self.charge = self.ledger / "charges" / f"{run_id}.json"
        experiments._create_only(self.charge, charge)
        proof = {"schema_version": 1, "run_id": run_id, "role": "raw-generated-video",
                 "locator": "synthetic-private-source", "sha256": digest(self.raw),
                 "size_bytes": self.raw.stat().st_size,
                 "verification": "rehashed_from_local_bytes", "release_status": experiments.HOLD}
        artifact_id = hashlib.sha256(experiments._canonical(proof)).hexdigest()
        self.artifact = self.ledger / "artifacts" / run_id / f"{artifact_id}.json"
        experiments._create_only(self.artifact, {"artifact_id": artifact_id,
                                 "created_at_utc": datetime.now(timezone.utc).isoformat(),
                                 "proof": proof})

    def write_ui(self):
        self.observation.write_text(json.dumps(self.ui))

    def reject(self, pattern):
        with self.assertRaisesRegex((experiments.ExperimentError, v13.V13PreflightError), pattern):
            experiments._validate_request(self.request)

    def test_proven_arm_only_v2v_trial_reserves_only_one_three_credit_diagnostic(self):
        preflight = experiments._validate_request(self.request)["source_preflight"]
        self.assertEqual(preflight["source_video_sha256"], digest(self.raw))
        self.assertEqual(preflight["source_qa_verdict"], "HOLD")
        self.assertEqual(preflight["source_native_actual_credits"], "3")
        self.assertEqual(preflight["precredit_result"],
                         "V12_NATIVE_VIDEO_AND_LIVE_V2V_EDIT_CONFIRMED_DIAGNOSTIC_ONLY")
        self.assertEqual(preflight["video_motion_form_and_release_approval"], "NOT_GRANTED")
        run = experiments.reserve(self.ledger, self.request)
        self.assertEqual(run["release_status"], experiments.HOLD)
        self.assertEqual(experiments.snapshot(self.ledger)["available_credits"], "0")
        self.assertEqual(experiments.snapshot(self.ledger)["pending_reserved_credits"], "3")

    def test_missing_wrong_or_derivative_video_and_changed_qa_are_holds(self):
        raw = self.raw.read_bytes()
        self.raw.write_bytes(raw + b"not original")
        self.reject("source SHA mismatch")
        self.raw.write_bytes(raw)
        self.request["input_assets"][0]["local_path"] = str(self.root / "absent.mp4")
        self.reject("unavailable")
        self.request["input_assets"][0]["local_path"] = str(self.raw)
        self.qa.write_text(self.qa.read_text() + "tampered")
        self.reject("QA bytes differ")

    def test_wrong_native_charge_scene_and_artifact_receipt_are_holds(self):
        for attr, replacement, match in (
                ("actual_credits", "0", "three-credit charge"),
                ("provider_generation_id", "not-original-scene", "three-credit charge")):
            original = json.loads(self.charge.read_text())
            edited = {**original, attr: replacement}
            self.charge.unlink()
            experiments._create_only(self.charge, edited)
            self.reject(match)
            self.charge.unlink()
            experiments._create_only(self.charge, original)
        artifact = json.loads(self.artifact.read_text())
        self.artifact.unlink()
        artifact["proof"]["sha256"] = "0" * 64
        experiments._create_only(self.artifact, artifact)
        self.reject("inconsistent native receipts")

    def test_fresh_actual_edit_screen_and_exact_single_output_are_required(self):
        cases = [
            ("model", "Omni 1.1 Flash"), ("source_scene_id", "different-scene"),
            ("source_video_visible", False), ("edit_prompt_interface_visible", False),
            ("source_qa_hold_acknowledged", False), ("ledger_reconciled", False),
            ("project_silent_setting_on", False), ("quoted_credits", "4"),
            ("quoted_credits", "0"), ("ledger_actual_credits", "2"),
            ("ledger_available_credits", "6"),
        ]
        for field, wrong in cases:
            with self.subTest(field=field, wrong=wrong):
                current = self.ui[field]
                self.ui[field] = wrong
                self.write_ui()
                self.reject("(mode/model/source|quoted edit cost|ledger differs)")
                self.ui[field] = current
        for field, wrong in (("generation_mode", "Frames to Video"),
                             ("resolution", "720p"), ("variants", 2),
                             ("variants", True), ("duration_seconds", 8),
                             ("return_silent_videos", False)):
            with self.subTest(field=field):
                current = self.ui["settings"][field]
                self.ui["settings"][field] = wrong
                self.write_ui()
                self.reject("mode/model/source")
                self.ui["settings"][field] = current

    def test_stale_future_and_unverifiable_screenshot_are_holds(self):
        for observed in (datetime.now(timezone.utc) - timedelta(minutes=16),
                         datetime.now(timezone.utc) + timedelta(minutes=1),
                         datetime.now()):
            self.ui["observed_at_utc"] = observed.isoformat()
            self.write_ui()
            self.reject("(stale|UTC)")
        self.ui["observed_at_utc"] = datetime.now(timezone.utc).isoformat()
        self.write_ui()
        self.evidence.write_bytes(self.evidence.read_bytes() + b"changed")
        self.reject("screenshot bytes")

    def test_prompt_changed_legs_or_unquoted_settings_cannot_reserve(self):
        other = self.root / "altered-motion-prompt.txt"
        other.write_text(self.prompt.read_text() + " Also alter the leg stride.")
        self.request["submitted_prompt_file"] = str(other)
        self.reject("preregistered arm-only")
        self.request["submitted_prompt_file"] = str(self.prompt)
        self.request["settings"]["variants"] = 2
        self.reject("V13 differs")

    def test_different_credit_store_cannot_be_used_for_v13_reservation(self):
        alternate = self.root / "not-the-reconciled-project-ledger"
        experiments.initialize(alternate, provider="Google Flow", credit_limit="300",
                               opening_spent_credits="0")
        with self.assertRaisesRegex(experiments.ExperimentError, "SAME existing V12"):
            experiments.reserve(alternate, self.request)

    def test_concurrent_ledger_change_after_preflight_blocks_reservation(self):
        checked = experiments._validate_request(self.request)
        changed_balance = {"actual_credits": "3", "pending_reserved_credits": "1",
                           "available_credits": "2"}
        with patch.object(experiments, "_validate_request", return_value=checked):
            with patch.object(experiments, "_snapshot", return_value=changed_balance):
                with self.assertRaisesRegex(experiments.ExperimentError,
                                            "changed between UI attestation"):
                    experiments.reserve(self.ledger, self.request)

    def test_pinned_spec_historical_limits_and_source_roles_are_immutable(self):
        changed = json.loads(self.spec.read_text())
        changed["full_scissor_cycle_proven"] = True
        self.spec.write_text(json.dumps(changed))
        self.reject("V13 spec differs")
        self.spec.write_text(json.dumps(v13.expected_spec()))
        self.request["input_assets"][0]["role"] = "silent-derived-video"
        self.reject("original.*raw MP4")


if __name__ == "__main__":
    unittest.main()
