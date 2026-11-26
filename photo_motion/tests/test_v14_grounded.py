"""Synthetic-only V14 A* -> C* grounded Frames precredit negative controls."""

import hashlib
import json
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from photo_motion import experiments
from photo_motion import preflight_v14_grounded as v14


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class V14GroundedPrecreditTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="v14-synthetic-only-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.assets = {}
        for name in v14.V10_PATHS:
            file = self.root / f"synthetic-{name}.dat"
            file.write_bytes(f"SYNTHETIC FIXTURE {name}: not a photograph".encode())
            self.assets[name] = str(file)
        self.a = Path(self.assets["derived_a_png"])
        self.c = Path(self.assets["derived_c_png"])
        self.manifest = Path(self.assets["shared_manifest"])
        self.qa = Path(self.assets["independent_qa_report"])
        self.prompt = self.root / "synthetic-submitted.txt"
        self.prompt.write_bytes(b"Synthetic grounded A-to-C one-flight prompt no person data")
        self.spec = self.root / "synthetic-v14-spec.json"
        self.screenshot = self.root / "synthetic-flow-screenshot.txt"
        self.screenshot.write_bytes(b"SYNTHETIC TEST ONLY: never observed from Google Flow")
        self.ui_path = self.root / "synthetic-ui.json"
        self.ledger = self.root / "synthetic-existing-ledger"
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="20",
                               opening_spent_credits="0")
        fields = [
            ("A_SHA256", digest(self.a)), ("C_SHA256", digest(self.c)),
            ("V10_MANIFEST_SHA256", digest(self.manifest)),
            ("V10_QA_SHA256", digest(self.qa)),
            ("PROMPT_SHA256", digest(self.prompt)),
        ]
        for name, value in fields:
            context = patch.object(v14, name, value)
            context.start()
            self.addCleanup(context.stop)
        self.spec.write_text(json.dumps(v14.expected_spec()))
        self.good_source = {
            "authority": "V10_REPLAYED_SHARED_CANVAS_FRAMES",
            "start_sha256": digest(self.a), "end_sha256": digest(self.c),
            "shared_canvas_manifest_sha256": digest(self.manifest),
            "independent_source_qa_report_sha256": digest(self.qa),
            "deterministic_replay": "EXACT_BYTE_REPLAY_PASS",
            "independent_source_qa": "CANDIDATE_FOR_DIAGNOSTIC_ONLY",
            "parent_v6_card_status": "UNAVAILABLE_NOT_BYTE_REPLAY_VERIFIED",
            "anatomical_left_right_proven": False,
            "video_motion_form_and_release_approval": "NOT_EVALUATED",
        }
        source_patch = patch.object(v14, "verify_v10_segment", return_value=self.good_source)
        source_patch.start()
        self.addCleanup(source_patch.stop)
        ledger_patch = patch.object(v14, "verify_existing_ledger", side_effect=lambda path: {
            f"ledger_{key}": experiments.snapshot(path)[key] for key in
            ("actual_credits", "pending_reserved_credits", "available_credits")})
        ledger_patch.start()
        self.addCleanup(ledger_patch.stop)
        self.ui = {
            "schema_version": 1, "authority": v14.UI_AUTHORITY,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "operator": "synthetic tester", "provider": "Google Flow",
            "model": v14.FLOW_MODEL, "settings": deepcopy(v14.FLOW_SETTINGS),
            "quoted_credits": "2.5",  # A real quote is required, not assumed to be three.
            "start_tile": {"pose": "A*", "source_sha256": digest(self.a),
                           "flow_asset_id": "synthetic-A", "visually_confirmed": True},
            "end_tile": {"pose": "C*", "source_sha256": digest(self.c),
                         "flow_asset_id": "synthetic-C", "visually_confirmed": True},
            "only_two_endpoints_selected": True,
            "project_silent_setting_on": True, "ledger_reconciled": True,
            "ledger_actual_credits": "0", "ledger_pending_reserved_credits": "0",
            "ledger_available_credits": "20",
            "ui_evidence_path": str(self.screenshot),
            "ui_evidence_sha256": digest(self.screenshot),
        }
        self.write_ui()
        self.request = {
            "schema_version": 1, "attempt_key": "synthetic-v14-grounded-001",
            "exercise_id": "chart1-scissor-jump", "spec_path": str(self.spec),
            "submitted_prompt_file": str(self.prompt),
            "input_assets": [
                {"role": "start-frame", "locator": "synthetic-A", "local_path": str(self.a),
                 "sha256": digest(self.a)},
                {"role": "end-frame", "locator": "synthetic-C", "local_path": str(self.c),
                 "sha256": digest(self.c)},
            ],
            "provider": "Google Flow", "model": v14.FLOW_MODEL,
            "settings": deepcopy(v14.FLOW_SETTINGS), "estimated_credits": "2.5",
            "source_preflight": {
                "authority": v14.AUTHORITY, "v10_source_paths": self.assets.copy(),
                "existing_ledger_store": str(self.ledger),
                "flow_ui_observation": str(self.ui_path)},
        }

    def write_ui(self):
        self.ui_path.write_text(json.dumps(self.ui))

    def reject(self, message):
        with self.assertRaisesRegex((experiments.ExperimentError, v14.V14PreflightError), message):
            experiments._validate_request(self.request)

    def test_exact_mocked_sources_live_two_point_five_quote_reserve_diagnostic_only(self):
        result = experiments._validate_request(self.request)
        self.assertEqual(result["estimated_credits"], "2.5")
        self.assertEqual(result["source_preflight"]["deterministic_source_replay"],
                         "EXACT_BYTE_REPLAY_PASS")
        self.assertEqual(result["source_preflight"]["video_motion_form_and_release_approval"],
                         "NOT_GRANTED")
        run = experiments.reserve(self.ledger, self.request)
        self.assertEqual(run["release_status"], experiments.HOLD)
        self.assertEqual(experiments.snapshot(self.ledger)["pending_reserved_credits"], "2.5")

    def test_absent_or_substituted_source_chain_fails(self):
        self.request["source_preflight"]["v10_source_paths"].pop("c_annotation")
        self.reject("ten exact")
        self.request["source_preflight"]["v10_source_paths"] = self.assets.copy()
        self.qa.write_bytes(self.qa.read_bytes() + b"tampered")
        self.reject("manifest/output/independent QA")

    def test_source_replay_independent_hold_and_legacy_parent_fail(self):
        for key, value in (("deterministic_replay", "HASH_ONLY"),
                           ("independent_source_qa", "HOLD"),
                           ("parent_v6_card_status", "REPLAY_VERIFIED"),
                           ("anatomical_left_right_proven", True),
                           ("video_motion_form_and_release_approval", "APPROVED")):
            with self.subTest(key=key):
                old = self.good_source[key]
                self.good_source[key] = value
                self.reject("corrected manifest/output/independent QA")
                self.good_source[key] = old

    def test_only_ordered_rehashed_A_C_no_held_out_apex_as_input(self):
        self.request["input_assets"].reverse()
        self.reject("ordered locally rehashed")
        self.request["input_assets"].reverse()
        self.request["input_assets"].append({"role": "apex-reference",
                                              "locator": "synthetic-B-held-out",
                                              "sha256": v14.HELD_OUT_APEX_SHA256})
        self.reject("exactly two ordered")
        self.request["input_assets"].pop()
        self.request["input_assets"][1].pop("local_path")
        self.reject("locally rehashed")

    def test_flow_tiles_wrong_identity_duplicate_or_false_visibility_fail(self):
        cases = [
            ("start_tile", "pose", "C*"), ("end_tile", "pose", "B*002"),
            ("end_tile", "source_sha256", digest(self.a)),
            ("end_tile", "flow_asset_id", "synthetic-A"),
            ("end_tile", "visually_confirmed", False),
        ]
        for section, key, bad in cases:
            with self.subTest(section=section, key=key):
                old = self.ui[section][key]
                self.ui[section][key] = bad
                self.write_ui()
                self.reject("(correct exact selected photo|distinct asset)")
                self.ui[section][key] = old
        self.ui["only_two_endpoints_selected"] = False
        self.write_ui()
        self.reject("selected endpoints")

    def test_model_settings_count_silence_and_live_quote_fail(self):
        for key, bad in (("model", "Omni 1.1 Flash"),
                         ("project_silent_setting_on", False),
                         ("ledger_reconciled", False)):
            with self.subTest(key=key):
                old = self.ui[key]
                self.ui[key] = bad
                self.write_ui()
                self.reject("model/settings")
                self.ui[key] = old
        for field, bad in (("resolution", "720p"), ("variants", 2),
                           ("variants", True), ("return_silent_videos", False)):
            with self.subTest(field=field):
                old = self.ui["settings"][field]
                self.ui["settings"][field] = bad
                self.write_ui()
                self.reject("model/settings")
                self.ui["settings"][field] = old
        for quote in ("0", "4", "-1", "not quoted"):
            with self.subTest(quote=quote):
                self.ui["quoted_credits"] = quote
                self.write_ui()
                self.reject("positive quote")

    def test_request_must_match_actual_live_quote_and_settings(self):
        self.request["estimated_credits"] = "3"
        self.reject("actual fresh")
        self.request["estimated_credits"] = "2.5"
        self.request["settings"]["duration_seconds"] = 6
        self.reject("actual fresh")

    def test_stale_future_non_UTC_and_missing_observation_fail(self):
        for observed in (datetime.now(timezone.utc) - timedelta(minutes=16),
                         datetime.now(timezone.utc) + timedelta(minutes=2),
                         datetime.now()):
            with self.subTest(observed=observed.isoformat()):
                self.ui["observed_at_utc"] = observed.isoformat()
                self.write_ui()
                self.reject("(UTC|stale/future)")
        self.request["source_preflight"]["flow_ui_observation"] = str(self.root / "missing.json")
        self.reject("fresh Flow")

    def test_screenshot_and_duplicate_observation_key_tampering_fail(self):
        self.screenshot.write_bytes(self.screenshot.read_bytes() + b"tampered")
        self.reject("screenshot")
        self.screenshot.write_bytes(b"SYNTHETIC TEST ONLY: never observed from Google Flow")
        self.ui_path.write_text(self.ui_path.read_text()[:-1] + ',"quoted_credits":"2.5"}')
        self.reject("duplicate")

    def test_prompt_spec_and_ledger_observation_fail(self):
        self.prompt.write_bytes(self.prompt.read_bytes() + b" paraphrase")
        self.reject("preregistered")
        self.prompt.write_bytes(b"Synthetic grounded A-to-C one-flight prompt no person data")
        self.spec.write_text(self.spec.read_text().replace("360p", "720p"))
        self.reject("V14 specification")
        self.spec.write_text(json.dumps(v14.expected_spec()))
        self.ui["ledger_available_credits"] = "1000"
        self.write_ui()
        self.reject("ledger attestation")

    def test_same_store_and_concurrent_ledger_drift_rejected_at_reserve(self):
        alternate = self.root / "different-initialized-ledger"
        experiments.initialize(alternate, provider="Google Flow", credit_limit="20",
                               opening_spent_credits="0")
        with self.assertRaisesRegex(experiments.ExperimentError, "SAME existing"):
            experiments.reserve(alternate, self.request)
        # Change the existing balance after UI observation with a separate
        # synthetic reservation, while retaining the same experiment's sources.
        other_spec = self.root / "other-synthetic-non-scissor.json"
        other_spec.write_text('{"schema_version":1,"synthetic":true}')
        other_prompt = self.root / "other-prompt.txt"
        other_prompt.write_text("Unrelated synthetic reservation")
        other_asset = self.root / "other-input.jpg"
        other_asset.write_bytes(b"synthetic input")
        unrelated = {
            "schema_version": 1, "attempt_key": "synthetic-unrelated-reservation",
            "exercise_id": "synthetic-unrelated-exercise", "spec_path": str(other_spec),
            "submitted_prompt_file": str(other_prompt),
            "input_assets": [{"role": "source", "locator": "synthetic",
                              "local_path": str(other_asset)}],
            "provider": "Google Flow", "model": "synthetic model",
            "settings": {"duration_seconds": 1}, "estimated_credits": "1",
        }
        experiments.reserve(self.ledger, unrelated)
        with self.assertRaisesRegex(experiments.ExperimentError, "ledger attestation"):
            experiments.reserve(self.ledger, self.request)
        # Even a stale source gate that falsely reports the original snapshot
        # cannot win the atomic balance comparison under reserve's store lock.
        with patch.object(v14, "verify_existing_ledger", return_value={
                "ledger_actual_credits": "0", "ledger_pending_reserved_credits": "0",
                "ledger_available_credits": "20"}):
            with self.assertRaisesRegex(experiments.ExperimentError, "changed between UI attestation"):
                experiments.reserve(self.ledger, self.request)


if __name__ == "__main__":
    unittest.main()
