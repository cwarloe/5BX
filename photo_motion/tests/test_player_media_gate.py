"""Private synthetic videos/QA only: never fixture-train a real owner approval."""

import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from photo_motion import player_media_gate as gate
from photo_motion.video_qa import file_sha256, probe


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                     "FFmpeg/ffprobe required to verify actual MP4 bytes")
class PlayerMediaAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="5bx-photo-gate-synthetic-")
        self.addCleanup(self.temp.cleanup)
        temp = Path(self.temp.name)
        self.root = temp / "repo"
        self.root.mkdir()
        self.private = temp / "private"
        self.private.mkdir()
        levels = self.root / "game/src/lib/levels.ts"
        levels.parent.mkdir(parents=True)
        levels.write_bytes((gate.REPO_ROOT / "game/src/lib/levels.ts").read_bytes())
        # Mimic the two existing source-of-truth diagnostic notes with
        # entirely fabricated digest values (never copy private real hashes).
        self.synthetic_failed_hashes = ("4" * 64, "5" * 64)
        for relative, digest in zip(gate.FAILED_DIAGNOSTIC_NOTES, self.synthetic_failed_hashes):
            diagnostic = self.root / relative
            diagnostic.parent.mkdir(parents=True, exist_ok=True)
            diagnostic.write_text("| Original SHA-256 | `" + digest + "` | Synthetic failure |\n")
        self.video_path = self._make_video("synthetic-1s.mp4", 1)
        self.hash = file_sha256(self.video_path)
        self.url = "https://example.invalid/private/current-review.mp4"
        observed = probe(self.video_path)
        self.candidate = {
            "schema_version": 1, "chart": 1, "exercise": 5, "action": "scissor",
            "revision": "synthetic-scissor-v1",
            "video": {
                "local_path": str(self.video_path), "url": self.url, "sha256": self.hash,
                "media_type": "video/mp4", "duration_seconds": observed["duration_seconds"],
                "width": observed["width"], "height": observed["height"],
                "fps": observed["fps"], "codec": observed["codec"],
                "audio_stream_count": observed["audio_stream_count"], "frame_count": 12,
            },
            "playback": {"mode": "repeat_full_clip", "runtime_slot_seconds": 5},
        }
        spec = self.root / "photo_motion/specs/chart1-scissor-synthetic.json"
        spec.parent.mkdir(parents=True)
        spec.write_text(json.dumps({"chart": 1, "exercise": 5,
                                    "movement_type": "scissor_jump", "status": "EXPERIMENTAL",
                                    "duration_seconds": 1}), encoding="utf-8")
        evidence = self.root / "photo_motion/diagnostics/private-qa-summary.md"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("Synthetic test-only inspection; never real owner evidence.")
        batch = self.root / "sprites/docs/photo_batches/fixture"
        batch.mkdir(parents=True)
        # The canonical inventory requires an actual visible Markdown link,
        # not a naked URL or incidental text substring (photo_workflow #73).
        self.index_path = batch / "MOBILE_REVIEW_INDEX.md"
        self.index_path.write_text("[Synthetic private review](" + self.url + ")\n")
        self.qa_path = batch / "CURRENT_QA.md"
        self.qa = {
            "schema_version": 1, "chart": 1, "exercise": 5,
            "revision": "synthetic-scissor-v1", "status": "DONE", "agent": "synthetic-producer",
            "contract": "photo_motion/specs/chart1-scissor-synthetic.json",
            "video": {"url": self.url, "sha256": self.hash, "media_type": "video/mp4"},
            "inspection": {"video_sha256": self.hash, "report_sha256": file_sha256(evidence),
                           "evidence": "photo_motion/diagnostics/private-qa-summary.md"},
            "checks": {g: {"verdict": "PASS", "evidence": "synthetic fixture only"}
                       for g in ("technical", "form", "motion", "loop", "identity")},
            "review": {"summary": "Synthetic QA data only", "recommendation": "Never release",
                       "question": "Does the recorded owner independently accept the real bytes?"},
            "owner_decision": {"reviewer": "cwarloe", "decision": "ACCEPT",
                               "video_sha256": self.hash,
                               "decided_at": "2026-11-26T12:00:00Z",
                               "evidence_url": "https://github.com/cwarloe/5BX/issues/0#issuecomment-fake"},
        }
        self.qa["checks"]["form"]["reviewer"] = "synthetic-form-reviewer"
        self.qa["checks"]["motion"]["reviewer"] = "synthetic-motion-reviewer"
        self._write_qa()

    def _make_video(self, name, seconds, audio=False):
        path = self.private / name
        args = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "testsrc=size=144x80:rate=12"]
        if audio:
            args += ["-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=8000"]
        args += ["-t", str(seconds), "-c:v", "libx264", "-pix_fmt", "yuv420p"]
        if audio:
            args += ["-c:a", "aac"]
        else:
            args += ["-an"]
        subprocess.run(args + [str(path)], check=True, capture_output=True)
        return path

    def _write_qa(self):
        self.qa_path.write_text(
            "# Explicitly synthetic; not Charles's approval.\n\n<!-- 5bx-production\n" +
            json.dumps(self.qa) + "\n-->\n", encoding="utf-8")

    def evaluate(self, candidate=None):
        return gate.evaluate(copy.deepcopy(candidate if candidate is not None else self.candidate),
                             repo_root=self.root)

    def assert_held(self, report):
        self.assertEqual(report["admission"], "HOLD")
        self.assertEqual(report["owner_authentication"], "NOT_EVALUATED")
        self.assertEqual(report["historical_diagnostic_integrity"], "NOT_EVALUATED")
        self.assertEqual(report["delivered_url_byte_integrity"], "NOT_EVALUATED")
        self.assertEqual(report["form_and_release_approval"], "NOT_EVALUATED")
        self.assertFalse(report["public_release_authorized"])
        self.assertEqual(report["player_manifest"], {"schemaVersion": 1, "clips": {}})

    def test_even_perfect_static_done_is_not_authenticated_owner_acceptance(self):
        report = self.evaluate()
        self.assert_held(report)
        self.assertEqual(report["technical_evidence"], "PASS")
        self.assertEqual(report["verified_video"]["full_stream_decode"], "PASS")
        self.assertEqual(report["canonical_qa_source"],
                         "sprites/docs/photo_batches/fixture/CURRENT_QA.md")
        self.assertIn("NOT_EVALUATED", " ".join(report["blockers"]))

    def test_bare_index_url_is_not_a_canonical_review_link(self):
        self.index_path.write_text("Unlinked URL only: " + self.url + "\n")
        report = self.evaluate()
        self.assert_held(report)
        self.assertIn("not registered in the canonical mobile index", " ".join(report["blockers"]))

    def test_modified_inspection_report_cannot_pass_canonical_qa(self):
        evidence = self.root / self.qa["inspection"]["evidence"]
        evidence.write_text("Modified after synthetic inspection was recorded.")
        report = self.evaluate()
        self.assert_held(report)
        self.assertIn("validation errors", " ".join(report["blockers"]))

    def test_absent_or_pending_or_stale_canonical_record_is_held(self):
        self.qa_path.unlink()
        self.assertIn("lacks one valid canonical QA DONE", " ".join(self.evaluate()["blockers"]))
        self.qa["status"] = "READY_FOR_REVIEW"
        self.qa["owner_decision"] = None
        self._write_qa()
        self.assertIn("lacks one valid canonical QA DONE", " ".join(self.evaluate()["blockers"]))
        self.qa["status"] = "DONE"
        self.qa["owner_decision"] = {"reviewer": "cwarloe", "decision": "ACCEPT",
                                      "video_sha256": "f" * 64,
                                      "decided_at": "2026-11-26T12:00:00Z",
                                      "evidence_url": "https://example.invalid/fake-approval"}
        self._write_qa()
        self.assertIn("validation errors", " ".join(self.evaluate()["blockers"]))

    def test_candidate_revision_url_and_hash_are_exact_version_locked(self):
        item = copy.deepcopy(self.candidate)
        item["revision"] = "v2-replaced"
        self.assertIn("revision differs", " ".join(self.evaluate(item)["blockers"]))
        item = copy.deepcopy(self.candidate)
        item["video"]["url"] = "https://example.invalid/different.mp4"
        self.assertIn("hash/URL differs", " ".join(self.evaluate(item)["blockers"]))
        item = copy.deepcopy(self.candidate)
        item["video"]["sha256"] = "d" * 64
        self.assertIn("SHA-256 mismatch", " ".join(self.evaluate(item)["blockers"]))

    def test_replaced_bytes_without_manifest_update_are_blocked(self):
        original_sha = self.hash
        self.video_path.write_bytes(self.video_path.read_bytes() + b"replacement")
        report = self.evaluate()
        self.assert_held(report)
        self.assertNotEqual(report["verified_video"]["sha256"], original_sha)
        self.assertIn("SHA-256 mismatch", " ".join(report["blockers"]))

    def test_forged_owner_field_is_not_a_valid_candidate_schema(self):
        item = copy.deepcopy(self.candidate)
        item["owner_approved"] = True
        self.assertIn("untrusted extra fields", " ".join(self.evaluate(item)["blockers"]))
        self.assert_held(self.evaluate(item))

    def test_nonfinite_or_wrong_numeric_types_do_not_bypass_checks_or_crash(self):
        for invalid in (float("nan"), float("inf"), "1", None, True):
            item = copy.deepcopy(self.candidate)
            item["video"]["duration_seconds"] = invalid
            report = self.evaluate(item)
            self.assert_held(report)
            self.assertIn("invalid values", " ".join(report["blockers"]))
        for invalid in (float("nan"), float("inf"), "5", None, True):
            item = copy.deepcopy(self.candidate)
            item["playback"]["runtime_slot_seconds"] = invalid
            report = self.evaluate(item)
            self.assert_held(report)
            self.assertIn("full-native-duration", " ".join(report["blockers"]))

    def test_unhashable_digest_also_produces_structured_hold(self):
        item = copy.deepcopy(self.candidate)
        item["video"]["sha256"] = []
        report = self.evaluate(item)
        self.assert_held(report)
        self.assertIn("exact lowercase SHA-256", " ".join(report["blockers"]))

    def test_source_replacement_during_ffprobe_cannot_pass(self):
        real_probe = gate.probe

        def mutate_after_probe(path):
            details = real_probe(path)
            path.write_bytes(path.read_bytes() + b"synthetic-race-replacement")
            return details

        with mock.patch.object(gate, "probe", side_effect=mutate_after_probe):
            report = self.evaluate()
        self.assert_held(report)
        self.assertIn("media bytes changed during", " ".join(report["blockers"]))

    def test_midstream_decoder_failure_blocks_even_when_probe_and_frame_count_pass(self):
        # Container metadata and countable frames do not establish that the
        # encoded payload is safely decodable from beginning to end.
        with mock.patch.object(gate, "_verify_full_video_decode",
                               side_effect=RuntimeError("synthetic midstream decoder failure")):
            report = self.evaluate()
        self.assert_held(report)
        self.assertEqual(report["technical_evidence"], "HOLD")
        self.assertIn("synthetic midstream decoder failure", " ".join(report["blockers"]))
        self.assertNotEqual(report["verified_video"].get("full_stream_decode"), "PASS")

    def test_six_second_scissor_cannot_be_silently_cut_to_five_seconds(self):
        longer = self._make_video("six-second-test.mp4", 6)
        item = copy.deepcopy(self.candidate)
        item["video"].update({"local_path": str(longer), "sha256": file_sha256(longer),
                              "duration_seconds": probe(longer)["duration_seconds"],
                              "frame_count": 72})
        report = self.evaluate(item)
        self.assert_held(report)
        self.assertIn("complete repeats", " ".join(report["blockers"]))
        self.assertIn("verified native clip", " ".join(report["blockers"]))

    def test_candidate_cannot_change_runtime_slot_to_six_seconds(self):
        item = copy.deepcopy(self.candidate)
        item["playback"]["runtime_slot_seconds"] = 6
        report = self.evaluate(item)
        self.assert_held(report)
        self.assertIn("differs from active player", " ".join(report["blockers"]))

    def test_mismatched_fps_frame_count_and_audio_are_rejected(self):
        item = copy.deepcopy(self.candidate)
        item["video"]["fps"] = 60
        item["video"]["frame_count"] = 100
        report = self.evaluate(item)
        self.assertIn("ffprobe fps mismatch", " ".join(report["blockers"]))
        self.assertIn("ffprobe frame_count mismatch", " ".join(report["blockers"]))
        audio = self._make_video("audio-test.mp4", 1, audio=True)
        item = copy.deepcopy(self.candidate)
        item["video"].update({"local_path": str(audio), "sha256": file_sha256(audio),
                              "audio_stream_count": 1})
        self.assertIn("contains audio", " ".join(self.evaluate(item)["blockers"]))

    def test_decoded_frame_timing_must_match_browser_native_duration(self):
        # A forged plausible count can match the asserted metadata while
        # count/FPS implies a different clip length. The browser rejects this
        # too; the offline gate must never claim technical PASS for it.
        item = copy.deepcopy(self.candidate)
        item["video"]["frame_count"] = 60
        with mock.patch.object(gate, "_decoded_frame_count", return_value=60):
            report = self.evaluate(item)
        self.assert_held(report)
        self.assertEqual(report["technical_evidence"], "HOLD")
        self.assertIn("frame count/FPS differs", " ".join(report["blockers"]))

    def test_diagnostic_hashes_rejected_even_with_owner_looking_claim(self):
        for digest in self.synthetic_failed_hashes:
            item = copy.deepcopy(self.candidate)
            item["video"]["sha256"] = digest
            report = self.evaluate(item)
            self.assert_held(report)
            self.assertIn("failed diagnostic", " ".join(report["blockers"]))

    def test_missing_or_mutated_source_diagnostic_is_not_silently_ignored(self):
        diagnostic = self.root / gate.FAILED_DIAGNOSTIC_NOTES[0]
        diagnostic.write_text("Unstructured document with hash omitted\n")
        report = self.evaluate()
        self.assert_held(report)
        self.assertIn("cannot verify failed diagnostic exclusions", " ".join(report["blockers"]))

    def test_valid_but_forged_diagnostic_hash_cannot_authenticate_exclusion(self):
        """A syntactically valid changed note is NOT a trusted historical anchor.

        Exercise the known source-tampering limitation without any real asset
        hashes. The offline release remains blocked even after tampering.
        """
        diagnostic = self.root / gate.FAILED_DIAGNOSTIC_NOTES[0]
        diagnostic.write_text("| Original SHA-256 | `" + self.hash + "` | Test-only failed video |\n")
        report = self.evaluate()
        self.assert_held(report)
        self.assertIn("known failed diagnostic", " ".join(report["blockers"]))
        diagnostic.write_text("| Original SHA-256 | `" + "8" * 64 + "` | Forged but valid |\n")
        changed = self.evaluate()
        self.assert_held(changed)
        self.assertNotIn("known failed diagnostic", " ".join(changed["blockers"]))
        self.assertEqual(changed["historical_diagnostic_integrity"], "NOT_EVALUATED")

    def test_contract_action_and_duration_must_match_version(self):
        spec = self.root / self.qa["contract"]
        data = json.loads(spec.read_text())
        data["movement_type"] = "stationary_run_low"
        spec.write_text(json.dumps(data))
        self.assertIn("different player action", " ".join(self.evaluate()["blockers"]))
        data["movement_type"] = "scissor_jump"
        data["duration_seconds"] = 6
        spec.write_text(json.dumps(data))
        self.assertIn("native duration differs", " ".join(self.evaluate()["blockers"]))

    def test_unreadable_or_repo_embedded_video_is_not_admitted(self):
        item = copy.deepcopy(self.candidate)
        item["video"]["local_path"] = str(self.root / "committed-media.mp4")
        (self.root / "committed-media.mp4").write_bytes(self.video_path.read_bytes())
        self.assertIn("outside the Git repository", " ".join(self.evaluate(item)["blockers"]))
        item["video"]["local_path"] = str(self.private / "missing.mp4")
        self.assertIn("outside the Git repository", " ".join(self.evaluate(item)["blockers"]))


if __name__ == "__main__":
    unittest.main()
