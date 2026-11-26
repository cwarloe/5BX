"""Synthetic paid-reservation negatives: never contact Google Flow or spend credits."""

import hashlib
import json
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from photo_motion import experiments
from photo_motion import preflight_v12_apex_frames as v12


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class V12ApexPaidGateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="v12-synthetic-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.a = self.root / "synthetic-astar.png"
        self.b = self.root / "synthetic-bstar.jpg"
        self.qa = self.root / "synthetic-independent-qa.json"
        self.a.write_bytes(b"synthetic A candidate bytes not a real photograph")
        self.b.write_bytes(b"synthetic B candidate bytes not a real photograph")
        self.qa.write_bytes(b'{"synthetic":"independent reviewer evidence"}')
        self.a_hash, self.b_hash, self.qa_hash = sha(self.a), sha(self.b), sha(self.qa)
        self.spec = self.root / "spec.json"
        self.prompt = self.root / "verbatim-prompt.txt"
        self.prompt.write_bytes(b"One synthetic A-to-airborne-B diagnostic; silent.\n")
        self.evidence = self.root / "screen-capture-placeholder.txt"
        self.evidence.write_bytes(b"SYNTHETIC TEST EVIDENCE: not a Google Flow screenshot")
        self.observation = self.root / "private-ui-observation.json"
        self.ledger = self.root / "private-test-ledger"
        self.patches = [patch.object(v12, "SOURCE_A_SHA256", self.a_hash),
                        patch.object(v12, "SOURCE_B_SHA256", self.b_hash),
                        patch.object(v12, "SOURCE_QA_SHA256", self.qa_hash),
                        patch.object(v12, "check_candidate", return_value={
                            "b_sha256": self.b_hash,
                            "independent_b_qa_sha256": self.qa_hash,
                            "v10_manifest_sha256": v12.V10_MANIFEST_SHA256,
                            "paid_video_precredit_authority": "NOT_GRANTED",
                            "motion_video_release_approval": "NOT_EVALUATED",
                        })]
        for context in self.patches:
            context.start()
            self.addCleanup(context.stop)
        self.spec.write_text(json.dumps(v12.expected_spec()))
        self.v10 = {label: str(self.root / f"synthetic-{label}") for label in v12.V10_PATHS}
        self.ui_record = {
            "schema_version": 1,
            "authority": v12.FLOW_UI_AUTHORITY,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "operator": "synthetic reviewer",
            "provider": "Google Flow", "model": v12.FLOW_MODEL,
            "settings": deepcopy(v12.FLOW_SETTINGS),
            "quoted_credits": "3", "project_silent_setting_on": True,
            "start_tile": {"source_sha256": self.a_hash, "pose": "A*",
                           "flow_asset_id": "synthetic-start", "visually_confirmed": True},
            "end_tile": {"source_sha256": self.b_hash, "pose": "B*002",
                         "flow_asset_id": "synthetic-end", "visually_confirmed": True},
            "ui_evidence_path": str(self.evidence),
            "ui_evidence_sha256": sha(self.evidence),
            "ledger_reconciled": True,
        }
        self.write_observation()
        self.request = {
            "schema_version": 1,
            "attempt_key": "synthetic-v12-001",
            "exercise_id": "chart1-scissor-jump",
            "spec_path": str(self.spec),
            "submitted_prompt_file": str(self.prompt),
            "input_assets": [
                {"role": "start-frame", "locator": "synthetic-test-source-A",
                 "local_path": str(self.a), "sha256": self.a_hash},
                {"role": "end-frame", "locator": "synthetic-test-source-B",
                 "local_path": str(self.b), "sha256": self.b_hash},
            ],
            "provider": "Google Flow", "model": v12.FLOW_MODEL,
            "settings": deepcopy(v12.FLOW_SETTINGS),
            "estimated_credits": "3",
            "source_preflight": {"authority": v12.AUTHORITY,
                                 "v10_source_paths": self.v10,
                                 "b_apex_image": str(self.b),
                                 "independent_b_qa": str(self.qa),
                                 "flow_ui_observation": str(self.observation)},
        }

    def write_observation(self):
        self.observation.write_text(json.dumps(self.ui_record))

    def assert_rejected(self, pattern="V12"):
        with self.assertRaisesRegex((experiments.ExperimentError, v12.V12PreflightError), pattern):
            experiments._validate_request(self.request)

    def test_exact_synthetic_sources_and_ui_allow_only_diagnostic_reservation(self):
        inspected = experiments._validate_request(self.request)
        self.assertEqual(inspected["source_preflight"]["precredit_result"],
                         "EXACT_SOURCE_AND_FRESH_UI_ATTESTED_DIAGNOSTIC_ONLY")
        self.assertEqual(inspected["source_preflight"]["video_motion_form_and_release_approval"],
                         "NOT_EVALUATED")
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="3",
                               opening_spent_credits="0")
        run = experiments.reserve(self.ledger, self.request)
        self.assertEqual(run["release_status"], experiments.HOLD)
        self.assertEqual(experiments.snapshot(self.ledger)["pending_reserved_credits"], "3")
        self.assertEqual(experiments.snapshot(self.ledger)["available_credits"], "0")
        self.assertEqual(run["request"]["source_preflight"]["end_sha256"], self.b_hash)

    def test_no_ui_observation_is_not_paid_authority(self):
        self.request["source_preflight"]["flow_ui_observation"] = str(self.root / "missing.json")
        self.assert_rejected("fresh Flow")

    def test_stale_quote_future_quote_and_timestamp_without_utc_are_rejected(self):
        for timestamp in (datetime.now(timezone.utc) - timedelta(minutes=16),
                          datetime.now(timezone.utc) + timedelta(minutes=1),
                          datetime.now()):
            with self.subTest(timestamp=timestamp.isoformat()):
                self.ui_record["observed_at_utc"] = timestamp.isoformat()
                self.write_observation()
                self.assert_rejected("(stale|UTC)")

    def test_wrong_endpoints_or_false_visual_attestation_fail_closed(self):
        cases = [
            ("start_tile", "source_sha256", self.b_hash),
            ("end_tile", "source_sha256", self.a_hash),
            ("end_tile", "pose", "C*"),
            ("end_tile", "flow_asset_id", "synthetic-start"),
            ("end_tile", "visually_confirmed", False),
        ]
        for section, key, value in cases:
            with self.subTest(section=section, key=key):
                copy = deepcopy(self.ui_record)
                copy[section][key] = value
                self.ui_record = copy
                self.write_observation()
                self.assert_rejected("(endpoint|distinct)")
                self.ui_record[section][key] = (
                    self.b_hash if section == "end_tile" and key == "source_sha256" else
                    self.a_hash if section == "start_tile" and key == "source_sha256" else
                    "B*002" if key == "pose" else
                    "synthetic-end" if key == "flow_asset_id" else True)

    def test_quote_model_resolution_silence_and_ledger_attestation_cannot_change(self):
        cases = [
            ("model", "Omni 1.1 Flash"), ("quoted_credits", "0"),
            ("project_silent_setting_on", False), ("ledger_reconciled", False),
        ]
        for key, value in cases:
            with self.subTest(key=key):
                original = self.ui_record[key]
                self.ui_record[key] = value
                self.write_observation()
                self.assert_rejected("Flow model/price/settings")
                self.ui_record[key] = original
        for field, value in (("resolution", "720p"), ("variants", 2),
                             ("return_silent_videos", False), ("variants", True)):
            with self.subTest(field=field):
                self.ui_record["settings"][field] = value
                self.write_observation()
                self.assert_rejected("Flow model/price/settings")
                self.ui_record["settings"][field] = v12.FLOW_SETTINGS[field]

    def test_changed_bytes_report_or_screenshot_fail_closed(self):
        self.b.write_bytes(self.b.read_bytes() + b"changed")
        self.assert_rejected("source SHA mismatch")
        self.b.write_bytes(b"synthetic B candidate bytes not a real photograph")
        self.qa.write_bytes(self.qa.read_bytes() + b"changed")
        self.assert_rejected("B002")
        self.qa.write_bytes(b'{"synthetic":"independent reviewer evidence"}')
        self.evidence.write_bytes(self.evidence.read_bytes() + b"changed")
        self.assert_rejected("evidence bytes differ")

    def test_non_rehashed_or_reordered_assets_and_request_settings_fail_closed(self):
        self.request["input_assets"][1].pop("local_path")
        self.assert_rejected("locally rehashed")
        self.request["input_assets"][1]["local_path"] = str(self.b)
        self.request["input_assets"].reverse()
        self.assert_rejected("locally rehashed")
        self.request["input_assets"].reverse()
        self.request["settings"]["resolution"] = "720p"
        self.assert_rejected("V12 differs")

    def test_qa_holds_and_exact_spec_pins_must_be_preserved(self):
        with patch.object(v12, "check_candidate", return_value={
                "b_sha256": self.b_hash, "independent_b_qa_sha256": self.qa_hash,
                "v10_manifest_sha256": v12.V10_MANIFEST_SHA256,
                "paid_video_precredit_authority": "NOT_GRANTED",
                "motion_video_release_approval": "APPROVED"}):
            self.assert_rejected("source receipt")
        self.spec.write_text(self.spec.read_text().replace("360p", "720p"))
        self.assert_rejected("V12 Frames spec")


if __name__ == "__main__":
    unittest.main()
