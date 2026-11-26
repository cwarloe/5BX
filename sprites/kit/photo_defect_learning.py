"""Check optional, in-place defect-learning evidence in photographic QA notes.

This does not create a second status database, approve exercise form, or mutate
media.  One ``5bx-learning`` comment can live inside an existing photographic
QA Markdown note, alongside (but separate from) its ``5bx-production`` handoff.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFECT_CODES = frozenset(
    {"FORM", "LIMB_ID", "HAND", "OCCLUSION", "IDENTITY", "FRAMING",
     "CONTACT", "LOOP", "RECOVERY", "SOURCE"}
)
METHODS = frozenset({"PROMPT_ONLY", "REFERENCE_CONTROL", "POSE_CONTROL",
                     "MODEL_CHANGE", "SOURCE_CAPTURE", "OTHER"})
OUTCOMES = frozenset({"FAIL", "PASS", "INCONCLUSIVE"})
COUNTERMEASURE_STATES = frozenset({"PROPOSED", "TESTED", "CONFIRMED", "REJECTED"})
IMPACTS = frozenset({"CRITICAL", "HIGH", "MEDIUM", "LOW"})
DETECTABILITY = frozenset({"HUMAN_REVIEW", "AUTOMATED", "UNKNOWN"})
_BLOCK = re.compile(r"<!--\s*5bx-learning\s*\n(?P<json>.*?)\n\s*-->", re.DOTALL)
_OPEN = re.compile(r"<!--\s*5bx-learning\b")


def _meaningful(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _text(obj: dict[str, Any], key: str, location: str, issues: list[str]) -> None:
    if not _meaningful(obj.get(key)):
        issues.append(f"{location}.{key}: nonblank text required")


def _evidence(value: Any, location: str, issues: list[str]) -> None:
    """Require a locator, not a claimed visual proof or fabricated content."""
    if not _meaningful(value):
        issues.append(f"{location}: evidence locator required")
    elif not (value.startswith("https://") or
              (not value.startswith(("http:", "/", "../")) and ".." not in Path(value).parts)):
        issues.append(f"{location}: use an HTTPS link or repo-relative path")


def validate_note(markdown: str, source: str = "QA note") -> tuple[int, list[str]]:
    """Return (annotated defect count, issues). Missing annotation is valid."""
    matches = list(_BLOCK.finditer(markdown))
    issues: list[str] = []
    openings = len(_OPEN.findall(markdown))
    if openings != len(matches):
        issues.append(f"{source}: malformed or unclosed 5bx-learning comment")
    if len(matches) > 1:
        issues.append(f"{source}: exactly one current 5bx-learning comment allowed")
    if not matches:
        return 0, issues
    try:
        document = json.loads(matches[0].group("json"))
    except json.JSONDecodeError as exc:
        return 0, [f"{source}: invalid 5bx-learning JSON ({exc.msg})"]
    if not isinstance(document, dict):
        return 0, [f"{source}: 5bx-learning must be an object"]
    if document.get("schema_version") != 1:
        issues.append(f"{source}: schema_version must be 1")
    defects = document.get("defects")
    if not isinstance(defects, list):
        return 0, issues + [f"{source}: defects must be an array"]
    seen: set[str] = set()
    for i, defect in enumerate(defects):
        where = f"{source}.defects[{i}]"
        if not isinstance(defect, dict):
            issues.append(f"{where}: defect must be an object")
            continue
        for key in ("id", "code", "symptom", "first_seen_revision"):
            _text(defect, key, where, issues)
        identity = defect.get("id")
        if _meaningful(identity):
            if identity in seen:
                issues.append(f"{where}.id: duplicate defect identity {identity!r}")
            seen.add(identity)
        if defect.get("code") not in DEFECT_CODES:
            issues.append(f"{where}.code: use an established 5BX defect code")
        _evidence(defect.get("first_seen_evidence"), f"{where}.first_seen_evidence", issues)

        risk = defect.get("risk")
        if not isinstance(risk, dict):
            issues.append(f"{where}.risk: qualitative risk/containment object required")
        else:
            if risk.get("impact") not in IMPACTS:
                issues.append(f"{where}.risk.impact: CRITICAL, HIGH, MEDIUM, or LOW required")
            if risk.get("detection") not in DETECTABILITY:
                issues.append(f"{where}.risk.detection: HUMAN_REVIEW, AUTOMATED, or UNKNOWN required")
            _text(risk, "consequence", f"{where}.risk", issues)
            _text(risk, "containment", f"{where}.risk", issues)

        mechanism = defect.get("mechanism")
        if not isinstance(mechanism, dict):
            issues.append(f"{where}.mechanism: object required")
        else:
            _text(mechanism, "finding", f"{where}.mechanism", issues)
            if mechanism.get("confidence") not in {"HYPOTHESIS", "EVIDENCED"}:
                issues.append(f"{where}.mechanism.confidence: use HYPOTHESIS or EVIDENCED")
            if mechanism.get("confidence") == "EVIDENCED":
                _evidence(mechanism.get("evidence"), f"{where}.mechanism.evidence", issues)

        attempts = defect.get("corrections")
        if not isinstance(attempts, list):
            issues.append(f"{where}.corrections: array required (may be empty)")
            attempts = []
        revisions: set[str] = set()
        failed_since_last_pass = 0
        for j, attempt in enumerate(attempts):
            a_where = f"{where}.corrections[{j}]"
            if not isinstance(attempt, dict):
                issues.append(f"{a_where}: correction must be an object")
                continue
            for key in ("revision", "changed_variable"):
                _text(attempt, key, a_where, issues)
            revision = attempt.get("revision")
            if _meaningful(revision):
                if revision in revisions:
                    issues.append(f"{a_where}.revision: duplicate correction revision")
                revisions.add(revision)
            if attempt.get("method") not in METHODS:
                issues.append(f"{a_where}.method: unknown correction method")
            if attempt.get("outcome") not in OUTCOMES:
                issues.append(f"{a_where}.outcome: use FAIL, PASS, or INCONCLUSIVE")
            _evidence(attempt.get("evidence"), f"{a_where}.evidence", issues)
            if attempt.get("outcome") == "FAIL":
                failed_since_last_pass += 1
            elif attempt.get("outcome") == "PASS":
                failed_since_last_pass = 0

        escalation = defect.get("escalation")
        if failed_since_last_pass >= 2 and not isinstance(escalation, dict):
            issues.append(f"{where}: two failed corrections require an escalation and alternate method")
        if escalation is not None:
            if not isinstance(escalation, dict):
                issues.append(f"{where}.escalation: object required")
            else:
                _text(escalation, "reason", f"{where}.escalation", issues)
                _text(escalation, "alternative_method", f"{where}.escalation", issues)
                _evidence(escalation.get("evidence"), f"{where}.escalation.evidence", issues)
                if escalation.get("alternative_method") == "PROMPT_ONLY":
                    issues.append(f"{where}.escalation: next method cannot be prompt-only retry")

        countermeasure = defect.get("countermeasure")
        if not isinstance(countermeasure, dict):
            issues.append(f"{where}.countermeasure: object required")
            continue
        for key in ("description", "prevention_test"):
            _text(countermeasure, key, f"{where}.countermeasure", issues)
        state = countermeasure.get("status")
        if state not in COUNTERMEASURE_STATES:
            issues.append(f"{where}.countermeasure.status: unknown state")
        verification = countermeasure.get("verification")
        if state in {"TESTED", "CONFIRMED", "REJECTED"}:
            if not isinstance(verification, dict):
                issues.append(f"{where}.countermeasure.verification: required for {state}")
            else:
                if verification.get("result") not in {"PASS", "FAIL"}:
                    issues.append(f"{where}.countermeasure.verification.result: PASS or FAIL required")
                _evidence(verification.get("evidence"), f"{where}.countermeasure.verification.evidence", issues)
                if state == "CONFIRMED":
                    _text(verification, "independent_batch", f"{where}.countermeasure.verification", issues)
                    if verification.get("result") != "PASS":
                        issues.append(f"{where}.countermeasure: CONFIRMED requires a PASS")
                    if verification.get("independent_batch") in ({defect.get("first_seen_revision")} | revisions):
                        issues.append(f"{where}.countermeasure: confirmation must cite a later independent batch")
                if state == "REJECTED" and verification.get("result") != "FAIL":
                    issues.append(f"{where}.countermeasure: REJECTED requires a failed verification")
    return len(defects), issues


def check_paths(paths: list[Path]) -> dict[str, Any]:
    issues: list[str] = []
    defects = annotated = 0
    for path in paths:
        source = path.read_text(encoding="utf-8")
        count, problems = validate_note(source, str(path))
        if _OPEN.search(source):
            annotated += 1
        defects += count
        issues.extend(problems)
    return {"notes_checked": len(paths), "notes_with_learning": annotated,
            "defects": defects, "issues": issues,
            "scope": "metadata consistency only; no exercise-form or human approval"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Existing photographic QA Markdown notes")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--all", action="store_true", help="Inspect QA Markdown notes in the canonical photo_batches directory")
    args = parser.parse_args(argv)
    if not args.all and not args.paths:
        parser.error("pass explicit QA paths or --all")
    paths = list(args.paths)
    if args.all:
        root = args.repo_root / "sprites" / "docs" / "photo_batches"
        if not root.is_dir():
            parser.error(f"missing photographic QA root: {root}")
        paths.extend(p for p in root.rglob("*.md") if p.is_file())
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        print(json.dumps({"issues": [f"missing note: {path}" for path in missing]}, indent=2))
        return 2
    result = check_paths(sorted(set(paths)))
    print(json.dumps(result, indent=2))
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    sys.exit(main())
