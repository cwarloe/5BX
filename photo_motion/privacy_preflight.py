"""Fail-closed pre-publication check for newly ADDED private photo locators.

Checks staged lines locally, or the added lines of a GitHub PR diff from its
known base commit. Historical unmodified lines and deletions are not scanned.
No network calls, private media reads, writes, upload, or approval decisions.

    python3 -m photo_motion.privacy_preflight --cached --check
    python3 -m photo_motion.privacy_preflight --base <verified-base-sha> --check

Patterns intentionally cover identifiable private-resource locators, not raw
SHA-256 values: content hashes are legitimate reproducibility evidence.
Results report only rule and diff location, NEVER the matching source line.
"""

import argparse
from dataclasses import dataclass
import re
import subprocess
import sys
from pathlib import Path


# Maintain rules as literal patterns, not examples copied from private files.
# Human review remains required: a real public Drive resource can still have a
# private-looking locator, while an unlabeled opaque token can evade patterns.
RULES = {
    "DRIVE_OR_FLOW_URL": re.compile(
        r"https?://(?:drive\.google\.com/|docs\.google\.com/"
        r"(?:document|spreadsheets|presentation)/d/|flow\.google\.com/project/)"
    ),
    "PRIVATE_STORAGE_URL": re.compile(
        r"https?://[^\s\]\[<>\"']*(?:oaiusercontent\.com/files/|blob\.core\.windows\.net/)"
    ),
    "PRIVATE_URI": re.compile(r"(?:gdrive|sediment|private)://[^\s\]\[<>\"']+", re.I),
    "EXPLICIT_DRIVE_ID": re.compile(
        r"\b(?:google[ -]?drive(?:[ -]?file)?[ -]?(?:id|identifier)|"
        r"drive[ -]?(?:file[ -]?)?id|fileId)\b\s*[:=]\s*[`'\"]?"
        r"[A-Za-z0-9_-]{20,}", re.I
    ),
}


class PrivacyPreflightError(ValueError):
    """The Git input is incomplete, missing or cannot be safely examined."""


@dataclass(frozen=True)
class Finding:
    file_number: int
    new_line: int
    rule: str


def scan_added_lines(patch: str) -> list[Finding]:
    """Return potential private locators from true added hunk lines only.

    Paths and matching text never appear in Finding or normal CLI output.
    Unified-zero diffs are preferred, though the parser tolerates context.
    """
    if not isinstance(patch, str):
        raise PrivacyPreflightError("Git diff must be decoded text")

    findings: list[Finding] = []
    file_number, new_line = 0, None
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            file_number += 1
            new_line = None
            continue
        if file_number and (line.startswith("Binary files ") or
                            line == "GIT binary patch"):
            # Git cannot expose added bytes as diff lines. Fail closed even
            # when this is a harmless binary; inspect the asset separately.
            findings.append(Finding(file_number, 0, "UNINSPECTABLE_BINARY"))
            continue
        if line.startswith("@@ "):
            match = re.search(r"\+(\d+)(?:,\d+)?\s@@", line)
            if not match:
                raise PrivacyPreflightError("Cannot parse an added-line hunk location")
            new_line = int(match.group(1))
            continue
        if new_line is None:
            continue  # diff metadata, including +++ destination header
        if line.startswith("+"):
            source = line[1:]
            for rule, pattern in RULES.items():
                if pattern.search(source):
                    findings.append(Finding(file_number, new_line, rule))
            new_line += 1
        elif line.startswith(" "):
            new_line += 1
        elif line.startswith("-"):
            continue  # deletions are never publication of a new locator
        elif line.startswith("\\ No newline at end of file"):
            continue
        else:
            new_line = None
    return findings


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode:
        # Git diagnostics can include a user-controlled ref/path. Do not echo.
        raise PrivacyPreflightError("Git diff/reference check failed; no privacy PASS")
    return result.stdout.strip()


def diff_for_check(repo: Path, *, base: str | None = None) -> str:
    """Read staged additions or base...HEAD; missing base fails closed.

    PR CI must pass the *event's exact base SHA* and use checkout fetch-depth
    zero so both the base and checkout HEAD are available locally. A PR merge
    ref checkout is supported: base...HEAD captures its feature additions.
    """
    repo = Path(repo).resolve()
    _git(repo, "rev-parse", "--is-inside-work-tree")
    if base is None:
        return _git(repo, "diff", "--cached", "--no-ext-diff", "--no-textconv",
                    "--no-color", "--unified=0", "--diff-filter=ACMRT", "--")

    # Restrict user-supplied base to a complete commit SHA. Never accept ref
    # syntax as option flags, incomplete names or an unspecified moving ref.
    if not re.fullmatch(r"[0-9a-fA-F]{40,64}", base):
        raise PrivacyPreflightError("--base requires the explicit PR base commit SHA")
    base_commit = _git(repo, "rev-parse", "--verify", f"{base}^{{commit}}")
    head_commit = _git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    if base_commit == head_commit:
        raise PrivacyPreflightError("PR base and HEAD resolve to the same commit")
    _git(repo, "merge-base", base_commit, head_commit)
    return _git(repo, "diff", "--no-ext-diff", "--no-textconv", "--no-color",
                "--unified=0", "--diff-filter=ACMRT", f"{base_commit}...{head_commit}", "--")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Scan added Git diff lines for private photographic locators")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--cached", action="store_true", help="Inspect locally staged additions")
    source.add_argument("--base", metavar="COMMIT_SHA", help="Inspect PR additions since an exact base SHA")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--check", action="store_true", help="Return a nonzero status on findings (default behavior)")
    args = parser.parse_args(argv)
    try:
        patch = diff_for_check(args.repo_root, base=args.base)
        findings = scan_added_lines(patch)
    except (OSError, PrivacyPreflightError) as exc:
        print(f"HOLD privacy preflight: {exc}", file=sys.stderr)
        return 2
    if findings:
        for finding in findings:
            print(f"HOLD potential private input: diff file #{finding.file_number}, "
                  f"added line {finding.new_line}, rule {finding.rule} (content redacted)")
        print(f"HOLD {len(findings)} potential private locator(s); review locally before publication")
        return 1
    print("PASS added-line private-locator patterns (not a general privacy or media approval)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
