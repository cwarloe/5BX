"""Synthetic V7 direct A/C photographic-source authority regressions; no Flow."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from photo_motion import contract, experiments, generation_preflight, preflight_v7, source_authority


SPEC = Path(__file__).resolve().parents[1] / "specs" / "chart1-scissor-jump-v7-prepared-pair.json"


class V7PreparedPairTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="synthetic-v7-pair-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.a = self.root / "prepared-a.png"
        self.c = self.root / "prepared-c.png"
        self.a_manifest = self.root / "historical-a.json"
        self.c_manifest = self.root / "historical-c.json"
        self.spec = self.root / "spec-v7.json"
        self.prompt = self.root / "verbatim-prompt.txt"
        self.ledger = self.root / "private-ledger"
        Image.new("RGB", (1280, 720), (60, 110, 152)).save(self.a)
        Image.new("RGB", (1280, 720), (61, 112, 151)).save(self.c)
        self.a_sha = hashlib.sha256(self.a.read_bytes()).hexdigest()
        self.c_sha = hashlib.sha256(self.c.read_bytes()).hexdigest()
        for module in (contract, preflight_v7):
            for field, replacement in (("V7_PREPARED_A_SHA256", self.a_sha),
                                       ("V7_PREPARED_C_SHA256", self.c_sha)):
                p = patch.object(module, field, replacement)
                p.start()
                self.addCleanup(p.stop)
        spec = contract.load_spec(SPEC)
        spec["track_provenance"]["prepared_a_png_sha256"] = self.a_sha
        spec["track_provenance"]["prepared_c_png_sha256"] = self.c_sha
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        self.prompt.write_bytes(b"One real photographic A-C-A cycle. No audio.\r\n")
        self._make_manifest(self.a_manifest, "A", self.a_sha)
        self._make_manifest(self.c_manifest, "C", self.c_sha)

    def _make_manifest(self, path, panel, image_sha):
        entry = {
            "tool": "photo_motion.panel_prep", "version": "1",
            "output_sha256": image_sha, "output_size": [1280, 720],
            "source_image_sha256_before": source_authority.V6_TAGGED_CARD_SHA256,
            "source_image_sha256_after": source_authority.V6_TAGGED_CARD_SHA256,
            "source_size": [1536, 1024],
            "crop_bounds_half_open": list(source_authority.V6_PANEL_A_CROP if panel == "A" else source_authority.V6_PANEL_C_CROP),
        }
        if panel == "C":
            entry["source_panel"] = "C"
        path.write_text(json.dumps(entry), encoding="utf-8")

    def request(self):
        return {
            "schema_version": 1, "attempt_key": "c1-v7-two-image-provenance-test",
            "exercise_id": "chart1-scissor-jump", "spec_path": str(self.spec),
            "submitted_prompt_file": str(self.prompt),
            "input_assets": [
                {"role": "start-frame", "locator": "private://v7/A-start", "local_path": str(self.a), "sha256": self.a_sha},
                {"role": "opposite-pose-reference", "locator": "private://v7/C-opposite", "local_path": str(self.c), "sha256": self.c_sha},
            ],
            "provider": "Google Flow", "model": "synthetic-Omni-Flash",
            "settings": {"duration_seconds": 6, "aspect_ratio": "16:9", "variants": 1, "seed": None},
            "estimated_credits": "18",
            "source_preflight": {
                "authority": "V7_DIRECT_PREPARED_PAIR", "prepared_png": str(self.a),
                "opposite_pose_reference": {"prepared_png": str(self.c)},
                "historical_manifests": {"start": str(self.a_manifest), "opposite": str(self.c_manifest)},
            },
        }

    def test_versioned_spec_pins_real_archived_digests_without_unverified_claim(self):
        actual = contract.load_spec(SPEC)["track_provenance"]
        self.assertEqual(actual["source_authority_version"], source_authority.V7_PREPARED_PAIR_AUTHORITY)
        self.assertEqual(actual["prepared_a_png_sha256"], source_authority.V7_PREPARED_A_SHA256)
        self.assertEqual(actual["prepared_c_png_sha256"], source_authority.V7_PREPARED_C_SHA256)
        self.assertEqual(actual["parent_v6_card_status"], source_authority.V7_PARENT_V6_STATUS)
        self.assertNotIn("source_card_sha256", actual)
        self.assertFalse(actual["anatomical_left_right_proven"])

    def test_true_direct_png_bytes_and_historical_manifest_claims_only(self):
        result = preflight_v7.verify_pair(self.spec, self.a, self.c, self.a_manifest, self.c_manifest)
        self.assertEqual(result["preflight_result"], "VERIFIED_DIRECT_PREPARED_PAIR_BYTES_ONLY")
        self.assertEqual(result["prepared_png_sha256"], self.a_sha)
        self.assertEqual(result["opposite_pose_reference"]["prepared_png_sha256"], self.c_sha)
        self.assertEqual(result["parent_v6_card_status"], "UNAVAILABLE_NOT_BYTE_REPLAY_VERIFIED")
        self.assertFalse(result["parent_crop_replay_verified"])
        self.assertFalse(result["anatomical_left_right_proven"])
        self.assertEqual(result["exercise_motion_and_release_approval"], "NOT_EVALUATED")
        self.assertEqual(result["historical_manifests"]["status"],
                         "CONSISTENCY_CHECKED_ONLY_PARENT_V6_NOT_REPLAYED")

    def test_archive_manifests_are_optional_but_cannot_be_forged(self):
        self.assertIsNone(preflight_v7.verify_pair(self.spec, self.a, self.c)["historical_manifests"])
        with self.assertRaisesRegex(preflight_v7.PreflightError, "as a pair"):
            preflight_v7.verify_pair(self.spec, self.a, self.c, self.a_manifest)
        entry = json.loads(self.c_manifest.read_text())
        entry["crop_bounds_half_open"] = list(source_authority.V6_PANEL_A_CROP)
        self.c_manifest.write_text(json.dumps(entry))
        with self.assertRaisesRegex(preflight_v7.PreflightError, "historical C manifest crop_bounds"):
            preflight_v7.verify_pair(self.spec, self.a, self.c, self.a_manifest, self.c_manifest)

    def test_corrupted_or_swapped_or_malformed_images_are_rejected(self):
        with self.assertRaisesRegex(preflight_v7.PreflightError, "SHA-256"):
            preflight_v7.verify_pair(self.spec, self.c, self.a)
        self.c.write_bytes(self.c.read_bytes()[:-12])
        with self.assertRaisesRegex(preflight_v7.PreflightError, "SHA-256"):
            preflight_v7.verify_pair(self.spec, self.a, self.c)
        self.c.write_bytes(b"not-a-PNG")
        with self.assertRaisesRegex(preflight_v7.PreflightError, "SHA-256"):
            preflight_v7.verify_pair(self.spec, self.a, self.c)

    def test_wrong_dimensions_and_unreadable_png_fail_even_when_digest_mock_matches(self):
        Image.new("RGB", (640, 360), "white").save(self.c)
        with patch.object(preflight_v7, "V7_PREPARED_C_SHA256", hashlib.sha256(self.c.read_bytes()).hexdigest()):
            with self.assertRaisesRegex(preflight_v7.PreflightError, "RGB 1280x720 PNG"):
                preflight_v7.verify_pair(self.spec, self.a, self.c)
        self.c.write_bytes(b"not-a-PNG")
        with patch.object(preflight_v7, "V7_PREPARED_C_SHA256", hashlib.sha256(self.c.read_bytes()).hexdigest()):
            with self.assertRaisesRegex(preflight_v7.PreflightError, "decodable PNG"):
                preflight_v7.verify_pair(self.spec, self.a, self.c)

    def test_v7_spec_cannot_promote_missing_parent_to_verified(self):
        spec = contract.load_spec(self.spec)
        spec["track_provenance"]["parent_v6_card_status"] = "VERIFIED"
        self.spec.write_text(json.dumps(spec))
        with self.assertRaisesRegex(preflight_v7.PreflightError, "parent_v6_card_status"):
            preflight_v7.verify_pair(self.spec, self.a, self.c)

    def test_v7_rejects_legacy_v6_spec_or_unversioned_source_claim(self):
        legacy_spec = Path(__file__).resolve().parents[1] / "specs" / "chart1-scissor-jump.json"
        with self.assertRaisesRegex(preflight_v7.PreflightError, "separately versioned"):
            preflight_v7.verify_pair(legacy_spec, self.a, self.c)
        doc = contract.load_spec(self.spec)
        doc["track_provenance"]["source_card_sha256"] = source_authority.V6_TAGGED_CARD_SHA256
        self.spec.write_text(json.dumps(doc))
        with self.assertRaisesRegex(preflight_v7.PreflightError, "must not claim verified original"):
            preflight_v7.verify_pair(self.spec, self.a, self.c)

    def test_paid_reservation_requires_two_ordered_and_hashed_ingredients(self):
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="200", opening_spent_credits="0")
        req = self.request()
        invalid = copy.deepcopy(req)
        invalid["input_assets"].reverse()
        with self.assertRaisesRegex(experiments.ExperimentError, "ordered verified start-frame A"):
            experiments.reserve(self.ledger, invalid)
        invalid = copy.deepcopy(req)
        invalid["input_assets"] = invalid["input_assets"][:1]
        with self.assertRaisesRegex(experiments.ExperimentError, "exactly ordered"):
            experiments.reserve(self.ledger, invalid)
        invalid = copy.deepcopy(req)
        invalid["input_assets"].append(copy.deepcopy(invalid["input_assets"][0]))
        with self.assertRaisesRegex(experiments.ExperimentError, "exactly ordered"):
            experiments.reserve(self.ledger, invalid)
        invalid = copy.deepcopy(req)
        invalid["input_assets"][1].pop("local_path")
        with self.assertRaisesRegex(experiments.ExperimentError, "exactly ordered"):
            experiments.reserve(self.ledger, invalid)
        self.assertEqual(experiments.snapshot(self.ledger)["attempts"], 0)
        receipt = experiments.reserve(self.ledger, req)
        self.assertEqual(receipt["release_status"], experiments.HOLD)
        self.assertEqual(receipt["request"]["source_preflight"]["source_authority_version"],
                         "V7_DIRECT_PREPARED_PAIR")
        self.assertFalse(receipt["request"]["source_preflight"]["parent_crop_replay_verified"])
        self.assertEqual(experiments.snapshot(self.ledger)["pending_reserved_credits"], "18")

    def test_paid_reservation_rejects_wrong_preflight_and_nonphotographic_settings(self):
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="200", opening_spent_credits="0")
        req = self.request()
        for index, (mutate, expected) in enumerate((
            (lambda r: r["source_preflight"].pop("opposite_pose_reference"), "source_preflight requires"),
            (lambda r: r["source_preflight"]["opposite_pose_reference"].update({"manifest": "unverified"}), "requires exactly"),
            (lambda r: r["source_preflight"]["historical_manifests"].pop("opposite"), "historical_manifests"),
            (lambda r: r["settings"].update({"aspect_ratio": "9:16"}), "16:9"),
            (lambda r: r["settings"].update({"duration_seconds": 5}), "six-second"),
            (lambda r: r["settings"].update({"variants": 3}), "one.*output"),
            (lambda r: r["settings"].update({"variants": 1.0}), "one.*output"),
            (lambda r: r["settings"].update({"output_count": 3}), "unsupported V7 settings"),
            (lambda r: r["settings"].update({"batch_size": 9}), "unsupported V7 settings"),
            (lambda r: r["settings"].pop("variants"), "one.*output"),
            (lambda r: r.update({"estimated_credits": "0"}), "positive provider-quoted"),
        )):
            broken = copy.deepcopy(req)
            broken["attempt_key"] = f"invalid-v7-{index}"
            mutate(broken)
            with self.subTest(expected=expected), self.assertRaisesRegex(experiments.ExperimentError, expected):
                experiments.reserve(self.ledger, broken)
        self.assertEqual(experiments.snapshot(self.ledger)["attempts"], 0)

    def test_explicitly_held_v7_motion_contract_cannot_reserve_credits(self):
        experiments.initialize(self.ledger, provider="Google Flow", credit_limit="200", opening_spent_credits="0")
        spec = json.loads(self.spec.read_text())
        spec["status"] = "HOLD"
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        # Image-byte verification alone can still PASS while production use is held.
        self.assertEqual(preflight_v7.verify_pair(self.spec, self.a, self.c)["preflight_result"],
                         "VERIFIED_DIRECT_PREPARED_PAIR_BYTES_ONLY")
        with self.assertRaisesRegex(experiments.ExperimentError, "motion contract is explicitly on HOLD"):
            experiments.reserve(self.ledger, self.request())
        self.assertEqual(experiments.snapshot(self.ledger)["attempts"], 0)

    def test_actual_v7_request_shape_passes_both_unpaid_input_gates(self):
        """Canonical scissor exercise ID remains stable across V6/V7 spec versions."""
        repo = self.root / "synthetic-repo"
        spec_dir = repo / "photo_motion" / "specs"
        spec_dir.mkdir(parents=True)
        versioned_spec = spec_dir / "chart1-scissor-jump-v7-prepared-pair.json"
        versioned_spec.write_bytes(self.spec.read_bytes())
        identity_policy = repo / "sprites" / "docs" / "PHOTOREALISTIC_AVATAR_DIRECTION_2026-11-25.md"
        identity_policy.parent.mkdir(parents=True)
        identity_policy.write_text("Synthetic photographic identity policy", encoding="utf-8")
        req = self.request()
        req["spec_path"] = str(versioned_spec)
        self.assertEqual(preflight_v7.verify_pair(versioned_spec, self.a, self.c)["preflight_result"],
                         "VERIFIED_DIRECT_PREPARED_PAIR_BYTES_ONLY")
        result = generation_preflight.evaluate(req, repo_root=repo, available_credits="182")
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["generation_authorization"], "NOT_GRANTED_BY_PREFLIGHT")

    def test_validated_v7_settings_detach_from_mutable_caller(self):
        req = self.request()
        normalized = experiments._validate_request(req)
        req["settings"]["variants"] = 99
        req["settings"]["seed"] = "altered after validation"
        self.assertEqual(normalized["settings"],
                         {"duration_seconds": 6, "aspect_ratio": "16:9", "variants": 1, "seed": None})


if __name__ == "__main__":
    unittest.main()
