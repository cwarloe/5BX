"""Synthetic-only regression tests for paid-run accounting (never call models)."""

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from photo_motion import experiments


class ExperimentLedgerTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory(prefix="photo-experiment-tests-")
        self.addCleanup(self.sandbox.cleanup)
        self.root = Path(self.sandbox.name)
        self.private = self.root / "private-ledger"
        self.spec = self.root / "generic-photo-contract.json"
        self.prompt = self.root / "actual-submitted-prompt.txt"
        self.identity = self.root / "photographic-identity-reference.png"
        self.motion = self.root / "motion-reference.jpg"
        self.video = self.root / "generated-output.mp4"
        self.spec.write_text('{"exercise_id":"ledger-synthetic","schema_version":1}\n', encoding="utf-8")
        self.prompt.write_bytes(b"Verbatim photographic input\r\nTwo real flights.\r\n")
        self.identity.write_bytes(b"synthetic-identity-input-not-an-actual-image")
        self.motion.write_bytes(b"synthetic-motion-reference")
        self.video.write_bytes(b"synthetic-output-not-an-actual-video")

    def request(self, *, attempt="run-one", cost="8", provider="Google Flow"):
        return {
            "schema_version": 1,
            "attempt_key": attempt,
            "exercise_id": "ledger-synthetic",
            "spec_path": str(self.spec),
            "submitted_prompt_file": str(self.prompt),
            "input_assets": [
                {"role": "identity", "locator": "private://identity/source-v1", "local_path": str(self.identity)},
                {"role": "movement", "locator": "private://movement/source-v1", "local_path": str(self.motion)},
            ],
            "provider": provider,
            "model": "example-video-model-v1",
            "settings": {"duration_seconds": 6, "seed": None, "camera": "fixed 35 mm"},
            "estimated_credits": cost,
        }

    def initialize(self, cap="20"):
        return experiments.initialize(self.private, provider="Google Flow", credit_limit=cap)

    def test_full_immutable_run_lifecycle_and_exact_prompt_bytes(self):
        self.initialize()
        request = self.request()
        first = experiments.reserve(self.private, request)
        again = experiments.reserve(self.private, request)
        self.assertEqual(first, again)
        self.assertEqual(first["release_status"], experiments.HOLD)
        self.assertEqual(first["request"]["submitted_prompt_sha256"],
                         hashlib.sha256(self.prompt.read_bytes()).hexdigest())
        self.assertEqual(first["request"]["submitted_prompt"], self.prompt.read_bytes().decode("utf-8"))
        self.assertEqual(first["run_id"], first["request_fingerprint"])
        self.assertEqual(first["request"]["input_assets"][0]["verification"], "rehashed_from_local_bytes")
        self.assertEqual(experiments.snapshot(self.private)["pending_reserved_credits"], "8")

        charge = experiments.settle(self.private, first["run_id"], actual_credits="6.25",
                                    provider_generation_id="flow-private-test-001", outcome="COMPLETED")
        self.assertEqual(charge, experiments.settle(self.private, first["run_id"], actual_credits="6.25",
                                                    provider_generation_id="flow-private-test-001", outcome="COMPLETED"))
        self.assertEqual(charge["release_status"], experiments.HOLD)
        state = experiments.snapshot(self.private)
        self.assertEqual(state["actual_credits"], "6.25")
        self.assertEqual(state["pending_reserved_credits"], "0")
        self.assertEqual(state["available_credits"], "13.75")
        self.assertEqual(state["attempts"], 1)

        artifact = experiments.record_artifact(self.private, first["run_id"], artifact_path=self.video,
                                               role="raw-generated-video", locator="private://video/flow-001")
        self.assertEqual(artifact, experiments.record_artifact(self.private, first["run_id"], artifact_path=self.video,
                                                               role="raw-generated-video", locator="private://video/flow-001"))
        self.assertEqual(artifact["proof"]["release_status"], experiments.HOLD)
        self.assertEqual(artifact["proof"]["sha256"], hashlib.sha256(self.video.read_bytes()).hexdigest())
        self.assertFalse((self.private / self.video.name).exists(), "do not copy private media to the ledger")
        self.assertEqual(len(list((self.private / "artifacts" / first["run_id"]).glob("*.json"))), 1)
        self.assertEqual(len(list((self.private / "intents").glob("*.json"))), 1)

    def test_immutable_policy_and_provider_isolation(self):
        self.initialize("10")
        self.assertEqual(self.initialize("10")["credit_limit"], "10")
        with self.assertRaisesRegex(experiments.ExperimentError, "authorization"):
            self.initialize("100")
        with self.assertRaisesRegex(experiments.ExperimentError, "provider"):
            experiments.reserve(self.private, self.request(provider="Other Video Provider"))
        self.assertFalse((self.private / "intents").exists())

    def test_budget_overspend_blocks_new_runs_even_after_actual_charge(self):
        self.initialize("10")
        first = experiments.reserve(self.private, self.request(cost="8"))
        with self.assertRaisesRegex(experiments.ExperimentError, "insufficient"):
            experiments.reserve(self.private, self.request(attempt="second", cost="3"))
        # Provider's actual charge is a fact, even if it exceeded the estimate/cap.
        experiments.settle(self.private, first["run_id"], actual_credits="12.5",
                           provider_generation_id="overage-id", outcome="FAILED")
        self.assertEqual(experiments.snapshot(self.private)["available_credits"], "-2.5")
        with self.assertRaisesRegex(experiments.ExperimentError, "insufficient"):
            experiments.reserve(self.private, self.request(attempt="third", cost="0"))

    def test_same_attempt_conflict_and_real_retries_are_distinct(self):
        self.initialize()
        first = experiments.reserve(self.private, self.request())
        self.prompt.write_text("Changed prompt intentionally", encoding="utf-8")
        with self.assertRaisesRegex(experiments.ExperimentError, "attempt_key already"):
            experiments.reserve(self.private, self.request())
        second = experiments.reserve(self.private, self.request(attempt="run-two"))
        self.assertNotEqual(first["run_id"], second["run_id"])
        self.assertEqual(experiments.snapshot(self.private)["pending_reserved_credits"], "16")

    def test_charge_cannot_be_changed_or_assigned_to_unknown_run(self):
        self.initialize()
        run = experiments.reserve(self.private, self.request())
        experiments.settle(self.private, run["run_id"], actual_credits="3",
                           provider_generation_id="provider-123", outcome="FAILED")
        with self.assertRaisesRegex(experiments.ExperimentError, "different result"):
            experiments.settle(self.private, run["run_id"], actual_credits="0",
                               provider_generation_id="provider-123", outcome="FAILED")
        with self.assertRaisesRegex(experiments.ExperimentError, "different result"):
            experiments.settle(self.private, run["run_id"], actual_credits="3",
                               provider_generation_id="provider-456", outcome="FAILED")
        with self.assertRaisesRegex(experiments.ExperimentError, "missing or invalid"):
            experiments.settle(self.private, "f" * 64, actual_credits="1",
                               provider_generation_id="never-generated", outcome="COMPLETED")

    def test_artifact_change_cannot_rewrite_old_provenance(self):
        self.initialize()
        run = experiments.reserve(self.private, self.request())
        first = experiments.record_artifact(self.private, run["run_id"], artifact_path=self.video,
                                            role="video", locator="private://clip")
        self.video.write_bytes(b"different synthetic bytes")
        later = experiments.record_artifact(self.private, run["run_id"], artifact_path=self.video,
                                            role="video", locator="private://clip")
        self.assertNotEqual(first["artifact_id"], later["artifact_id"])
        preserved = json.loads((self.private / "artifacts" / run["run_id"] / f"{first['artifact_id']}.json").read_text())
        self.assertEqual(first, preserved)

    def test_declared_hash_is_unverified_and_bad_hash_rejected(self):
        self.initialize()
        req = self.request()
        req["input_assets"] = [{"role": "identity", "locator": "drive://unavailable-resource",
                                 "sha256": "a" * 64}]
        run = experiments.reserve(self.private, req)
        self.assertEqual(run["request"]["input_assets"][0]["verification"], "declared_unverified")
        req["attempt_key"] = "run-two"
        req["input_assets"][0].pop("sha256")
        with self.assertRaisesRegex(experiments.ExperimentError, "URL alone is insufficient"):
            experiments.reserve(self.private, req)
        req["input_assets"][0].update({"sha256": "b" * 64, "local_path": str(self.identity)})
        with self.assertRaisesRegex(experiments.ExperimentError, "SHA mismatch"):
            experiments.reserve(self.private, req)

    def test_strict_request_and_credit_validation(self):
        self.initialize()
        for bad in ("NaN", "Infinity", "-1", 1.25, None):
            with self.subTest(bad=bad), self.assertRaises(experiments.ExperimentError):
                experiments.reserve(self.private, self.request(cost=bad))
        malformed = self.request()
        malformed["undocumented"] = "surprise"
        with self.assertRaisesRegex(experiments.ExperimentError, "unknown request fields"):
            experiments.reserve(self.private, malformed)
        malformed.pop("undocumented")
        malformed["settings"] = {"seed": float("nan")}
        with self.assertRaisesRegex(experiments.ExperimentError, "not serializable JSON"):
            experiments.reserve(self.private, malformed)
        with self.assertRaisesRegex(experiments.ExperimentError, "nonnegative"):
            experiments.initialize(self.root / "other", provider="Google Flow", credit_limit="-10")

    def test_repository_local_private_store_is_rejected(self):
        with self.assertRaisesRegex(experiments.ExperimentError, "outside the Git repository"):
            experiments.initialize(experiments.REPO_ROOT / "photo_motion" / "internal", provider="Google Flow",
                                   credit_limit="5")

    def test_immutable_intent_detects_corrupted_fingerprint(self):
        self.initialize()
        run = experiments.reserve(self.private, self.request())
        path = self.private / "intents" / f"{run['run_id']}.json"
        # Simulate forensic discovery of a corrupt ledger, not an API write.
        path.chmod(0o600)
        record = json.loads(path.read_text())
        record["request"]["model"] = "tampered-model"
        path.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaisesRegex(experiments.ExperimentError, "fingerprint"):
            experiments.snapshot(self.private)

    def test_forged_release_status_is_never_accepted(self):
        self.initialize()
        run = experiments.reserve(self.private, self.request())
        path = self.private / "intents" / f"{run['run_id']}.json"
        path.chmod(0o600)
        record = json.loads(path.read_text())
        record["release_status"] = "APPROVED"
        path.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaisesRegex(experiments.ExperimentError, "forged release status"):
            experiments.snapshot(self.private)
        with self.assertRaisesRegex(experiments.ExperimentError, "forged release status"):
            experiments.settle(self.private, run["run_id"], actual_credits="3",
                               provider_generation_id="forge-test", outcome="COMPLETED")

    def test_concurrent_reservations_cannot_exceed_cap(self):
        self.initialize("3")

        def try_reserve(number):
            try:
                experiments.reserve(self.private, self.request(attempt=f"concurrent-{number}", cost="1"))
                return "reserved"
            except experiments.ExperimentError as exc:
                self.assertIn("insufficient", str(exc))
                return "blocked"

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(try_reserve, range(8)))
        self.assertEqual(results.count("reserved"), 3)
        self.assertEqual(results.count("blocked"), 5)
        self.assertEqual(experiments.snapshot(self.private)["available_credits"], "0")

    def test_standalone_cli_uses_no_paid_provider(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(experiments._main(["init", "--store", str(self.private), "--provider", "Google Flow",
                                                "--credit-limit", "4"]), 0)
        self.assertEqual(json.loads(output.getvalue())["credit_limit"], "4")
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(experiments._main(["status", "--store", str(self.private)]), 0)
        self.assertEqual(json.loads(output.getvalue())["attempts"], 0)


if __name__ == "__main__":
    unittest.main()
