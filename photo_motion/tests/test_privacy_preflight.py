"""Synthetic private-locator test fixtures; never copy real source IDs here."""

import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest

from photo_motion.privacy_preflight import (
    PrivacyPreflightError, diff_for_check, main, scan_added_lines,
)


def _fake_url(host, suffix):
    # Assemble only at test execution. Source diff never contains a live URL.
    return "https://" + host + "/" + suffix


def _patch(*additions):
    body = "\n".join("+" + text for text in additions)
    return ("diff --git a/example.md b/example.md\n"
            "--- a/example.md\n+++ b/example.md\n"
            f"@@ -0,0 +1,{len(additions)} @@\n{body}\n")


class ScanAddedLinesTests(unittest.TestCase):
    def test_url_types_are_detected_without_exposing_content(self):
        fake = "SYNTHETIC_" + "A" * 32
        examples = (
            _fake_url("drive.google.com", "file/d/" + fake + "/view"),
            _fake_url("docs.google.com", "document/d/" + fake + "/edit"),
            _fake_url("flow.google.com", "project/" + fake + "/edit/example"),
            _fake_url("sdmntpr.example.oaiusercontent.com", "files/" + fake + "/raw?sig=synthetic"),
            "private" + "://synthetic/asset",
        )
        findings = scan_added_lines(_patch(*examples))
        self.assertEqual(len(findings), len(examples))
        self.assertTrue(all(f.file_number == 1 for f in findings))
        self.assertEqual([f.new_line for f in findings], [1, 2, 3, 4, 5])
        self.assertNotIn(fake, repr(findings))

    def test_explicit_drive_id_detected_but_sha256_not_blanket_banned(self):
        fake_id = "SYNTHETIC_" + "Z" * 32
        diff = _patch("Drive ID: " + fake_id, "SHA-256: " + "a" * 64,
                      "A regular publication URL: https://example.org/docs")
        self.assertEqual([(f.new_line, f.rule) for f in scan_added_lines(diff)],
                         [(1, "EXPLICIT_DRIVE_ID")])

    def test_deleted_and_context_lines_not_reported(self):
        link = _fake_url("drive.google.com", "file/d/" + "SYNTHETIC" * 5)
        diff = ("diff --git a/x b/x\n--- a/x\n+++ b/x\n"
                "@@ -1,2 +1,2 @@\n-" + link + "\n " + link + "\n+ordinary text\n")
        self.assertEqual(scan_added_lines(diff), [])

    def test_source_headers_not_reported_as_added_content(self):
        link = _fake_url("drive.google.com", "file/d/" + "SYNTHETIC" * 5)
        diff = ("diff --git a/x b/x\n--- a/x\n+++ " + link + "\n"
                "@@ -0,0 +1 @@\n+safe text\n")
        self.assertEqual(scan_added_lines(diff), [])

    def test_bad_hunk_fails_closed(self):
        with self.assertRaises(PrivacyPreflightError):
            scan_added_lines("diff --git a/x b/x\n@@ malformed @@\n+safe\n")

    def test_binary_diff_cannot_be_misreported_as_safe(self):
        patch = ("diff --git a/asset.png b/asset.png\n"
                 "new file mode 100644\n"
                 "Binary files /dev/null and b/asset.png differ\n")
        self.assertEqual([f.rule for f in scan_added_lines(patch)],
                         ["UNINSPECTABLE_BINARY"])


class GitDiffTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="fivebx-privacy-test-")
        self.addCleanup(directory.cleanup)
        self.repo = Path(directory.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Synthetic QA")
        self.git("config", "user.email", "synthetic@example.invalid")
        self.file = self.repo / "note.md"

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.repo, capture_output=True,
                                text=True, check=False)
        if result.returncode:
            raise AssertionError(result.stderr)
        return result.stdout.strip()

    def commit(self, msg="fixture"):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def test_staged_only_scans_new_lines_not_baseline(self):
        old = _fake_url("drive.google.com", "file/d/" + "SYNTHETIC" * 5)
        self.file.write_text("historical: " + old + "\n", encoding="utf-8")
        self.commit("old public baseline")
        self.file.write_text("historical: " + old + "\nnew safe explanation\n", encoding="utf-8")
        self.git("add", "note.md")
        self.assertEqual(scan_added_lines(diff_for_check(self.repo)), [])
        self.file.write_text("historical: " + old + "\n" + old + "\n", encoding="utf-8")
        self.git("add", "note.md")
        self.assertEqual(len(scan_added_lines(diff_for_check(self.repo))), 1)

    def test_base_sha_checks_only_pr_additions(self):
        old = _fake_url("drive.google.com", "file/d/" + "SYNTHETIC" * 5)
        self.file.write_text("historical: " + old + "\n", encoding="utf-8")
        base = self.commit("base")
        self.file.write_text("historical: " + old + "\n" + old + "\n", encoding="utf-8")
        self.commit("feature")
        found = scan_added_lines(diff_for_check(self.repo, base=base))
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].new_line, 2)

    def test_pr_merge_checkout_compares_against_exact_base_sha(self):
        self.file.write_text("baseline\n", encoding="utf-8")
        self.commit("initial")
        self.git("checkout", "-q", "-b", "feature")
        link = _fake_url("docs.google.com", "spreadsheets/d/" + "SYNTHETIC" * 5 + "/edit")
        self.file.write_text("baseline\nnew " + link + "\n", encoding="utf-8")
        self.commit("feature")
        self.git("checkout", "-q", "main")
        (self.repo / "unrelated.txt").write_text("base evolved\n", encoding="utf-8")
        base = self.commit("advance base")
        self.git("merge", "-q", "--no-ff", "feature", "-m", "PR merge checkout")
        findings = scan_added_lines(diff_for_check(self.repo, base=base))
        self.assertEqual(len(findings), 1)

    def test_missing_base_or_same_head_never_passes(self):
        self.file.write_text("fixture\n", encoding="utf-8")
        sha = self.commit()
        with self.assertRaises(PrivacyPreflightError):
            diff_for_check(self.repo, base="0" * 40)
        with self.assertRaises(PrivacyPreflightError):
            diff_for_check(self.repo, base=sha)
        with self.assertRaises(PrivacyPreflightError):
            diff_for_check(self.repo, base="main")

    def test_cli_does_not_print_private_source_content(self):
        self.file.write_text("baseline\n", encoding="utf-8")
        self.commit()
        fake = _fake_url("flow.google.com", "project/" + "SYNTHETIC" * 5)
        self.file.write_text("baseline\n" + fake + "\n", encoding="utf-8")
        self.git("add", "note.md")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = main(["--cached", "--repo-root", str(self.repo), "--check"])
        self.assertEqual(status, 1)
        self.assertIn("content redacted", out.getvalue())
        self.assertNotIn(fake, out.getvalue())


if __name__ == "__main__":
    unittest.main()
