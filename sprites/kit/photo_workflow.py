#!/usr/bin/env python3
"""Read-only production/review handoffs embedded in existing photographic QA.

No independent status database, owner-approval button, image generation, or
release operation. Automated checks validate evidence *references* and source
attestations; private MP4 motion/form cannot be certified by this scanner.
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


QA_ROOT = Path("sprites/docs/photo_batches")
SPEC_ROOT = Path("photo_motion/specs")
MARKER = re.compile(r"^<!-- 5bx-production\s*\n(.*?)\n-->\s*$", re.M | re.S)
SHA256 = re.compile(r"[0-9a-fA-F]{64}\Z")
# A READY video must be the exact target of a clickable Markdown link in the
# canonical index. A prose mention or prefix of another take's URL is not a
# registered review artifact. Angle brackets support URLs with parentheses.
REVIEW_LINK = re.compile(r"\[[^\]\r\n]+\]\(\s*(?:<(?P<angle>https://[^<>\s]+)>|(?P<plain>https://[^()\s]+))\s*\)")
HTML_COMMENT = re.compile(r"<!--(?:.*?-->|.*\Z)", re.S)
FENCE_LINE = re.compile(r"^ {0,3}(?P<run>`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+).*?\1")
ACTIVE = {"PRODUCING", "QA", "BLOCKED", "REWORK"}
STATES = ACTIVE | {"READY_FOR_REVIEW", "DONE"}
GATES = ("technical", "form", "motion", "loop", "identity")
MAX_ACTIVE = 2


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _sha(value):
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def _actor_id(value):
    """Canonicalize reviewer labels for the limited producer-separation check.

    This detects trivial whitespace/case aliases; it does not authenticate
    reviewer identity, which must be established by external evidence.
    """
    return " ".join(value.split()).casefold() if _nonempty(value) else ""


def _timestamp(value):
    """Require a timezone-aware ISO-8601 timestamp, not arbitrary prose."""
    if not _nonempty(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _https(value):
    if not _nonempty(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _relative_existing(root, value):
    if not _nonempty(value) or value.startswith("/") or "\\" in value:
        return False
    target = (root / value).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return False
    return target.is_file()


def _visible_review_targets(source):
    """Find exact Markdown link targets, ignoring non-rendered code/comments.

    Conservatively skip indented code and multiline links. This is a narrow
    registry check, not a Markdown renderer or a playable-MP4 inspection.
    """
    source = HTML_COMMENT.sub("", source)
    fence = None
    for line in source.splitlines():
        marker = FENCE_LINE.match(line)
        if fence is not None:
            if (marker and marker.group("run")[0] == fence[0]
                    and len(marker.group("run")) >= len(fence)
                    and not line[marker.end():].strip()):
                fence = None
            continue
        if marker:
            fence = marker.group("run")
            continue
        if line.startswith("    ") or line.startswith("\t"):
            continue
        for match in REVIEW_LINK.finditer(INLINE_CODE.sub("", line)):
            yield match.group("angle") or match.group("plain")


def _indexed(root, chart, url):
    """A review-ready output must have its exact link in the canonical index."""
    batch = root / QA_ROOT
    for folder in sorted(batch.glob("*")):
        if not folder.is_dir():
            continue
        for name in ("MOBILE_REVIEW_INDEX.md", "REVIEW_INVENTORY.md",
                     f"CHART{chart}_PILOT_INVENTORY.md"):
            path = folder / name
            if path.is_file():
                if url in _visible_review_targets(path.read_text(encoding="utf-8")):
                    return True
    return False


def _ready_evidence(root, item):
    errors = []
    video = item.get("video")
    if not isinstance(video, dict):
        return ["ready/released item needs exact video object"]
    url, digest = video.get("url"), video.get("sha256")
    if not _https(url) or video.get("media_type") != "video/mp4":
        errors.append("video must have a direct HTTPS review link and media_type video/mp4")
    if not _sha(digest):
        errors.append("video.sha256 must be exact 64-character SHA-256")
    if _https(url) and not _indexed(root, item["chart"], url):
        errors.append("video not registered in the canonical mobile index/inventory")
    contract = item.get("contract")
    if not _relative_existing(root, contract):
        errors.append("existing versioned motion contract is required")
    else:
        try:
            spec = json.loads((root / contract).read_text(encoding="utf-8"))
            if spec.get("chart") != item["chart"] or spec.get("exercise") != item["exercise"]:
                errors.append("motion contract chart/exercise mismatch")
        except (OSError, ValueError):
            errors.append("motion contract cannot be decoded")
    inspection = item.get("inspection")
    if not isinstance(inspection, dict) or not _sha(inspection.get("report_sha256")):
        errors.append("hashed inspection report evidence is required")
    elif (inspection.get("video_sha256") != digest or
          not _relative_existing(root, inspection.get("evidence"))):
        errors.append("inspection must bind the exact video hash and existing QA evidence")
    checks = item.get("checks")
    if not isinstance(checks, dict):
        errors.append("all five internal quality gates need evidence")
    else:
        for gate in GATES:
            entry = checks.get(gate)
            if not isinstance(entry, dict) or entry.get("verdict") != "PASS" or not _nonempty(entry.get("evidence")):
                errors.append(f"{gate} gate requires a recorded PASS and evidence")
            elif gate in ("form", "motion") and (
                not _actor_id(entry.get("reviewer")) or
                _actor_id(entry.get("reviewer")) == _actor_id(item.get("agent"))
            ):
                errors.append(f"{gate} needs a named independent reviewer, not the producer")
    review = item.get("review")
    if not isinstance(review, dict) or any(not _nonempty(review.get(k)) for k in
                                           ("summary", "recommendation", "question")):
        errors.append("review packet needs summary, recommendation and one concrete question")
    return errors


def _validate(root, item):
    errors = []
    if item.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    chart, exercise = item.get("chart"), item.get("exercise")
    if type(chart) is not int or chart not in range(1, 7) or type(exercise) is not int or exercise not in range(1, 6):
        errors.append("chart and exercise must be integers in 1..6 and 1..5")
    if not _nonempty(item.get("revision")) or not _nonempty(item.get("agent")):
        errors.append("revision and producing agent are required")
    state = item.get("status")
    if not isinstance(state, str) or state not in STATES:
        errors.append("status must be PRODUCING, QA, BLOCKED, REWORK, READY_FOR_REVIEW or DONE")
    if errors:
        return errors
    if state in ("READY_FOR_REVIEW", "DONE"):
        errors.extend(_ready_evidence(root, item))
    if state == "BLOCKED":
        block = item.get("blocker")
        if not isinstance(block, dict) or any(not _nonempty(block.get(k)) for k in
                                               ("reason", "question", "recommendation")):
            errors.append("BLOCKED requires reason, one question and recommended option")
        elif type(block.get("owner_needed")) is not bool:
            errors.append("BLOCKED requires boolean owner_needed")
    if state == "REWORK" and not _nonempty(item.get("defect")):
        errors.append("REWORK needs a named defect")
    decision = item.get("owner_decision")
    if state == "DONE":
        video_record = item.get("video")
        exact_sha = video_record.get("sha256") if isinstance(video_record, dict) else None
        if not isinstance(decision, dict) or any(not _nonempty(decision.get(k)) for k in
                                                 ("reviewer", "decided_at", "evidence_url")):
            errors.append("DONE needs a separate named owner decision and evidence link")
        elif (decision.get("reviewer") != "cwarloe" or decision.get("decision") != "ACCEPT" or
              exact_sha is None or decision.get("video_sha256") != exact_sha or
              not _https(decision.get("evidence_url"))):
            errors.append("DONE requires Charles's recorded ACCEPT of this exact video hash")
        if isinstance(decision, dict) and not _timestamp(decision.get("decided_at")):
            errors.append("DONE needs a timezone-aware ISO-8601 decision timestamp")
    elif decision is not None:
        errors.append("owner_decision must remain null until exact owner acceptance")
    return errors


def collect(repo_root):
    """Project source-embedded handoffs into a fail-closed, read-only queue."""
    root = Path(repo_root).resolve()
    records, errors = [], []
    seen = {}
    for path in sorted((root / QA_ROOT).rglob("*.md")):
        # Canonical indexes link outputs; detailed QA notes own the handoff.
        if path.name.endswith("INVENTORY.md") or path.name == "MOBILE_REVIEW_INDEX.md":
            continue
        for marker in MARKER.finditer(path.read_text(encoding="utf-8")):
            source = path.relative_to(root).as_posix()
            try:
                entry = json.loads(marker.group(1))
                if not isinstance(entry, dict):
                    raise ValueError("marker must be an object")
            except ValueError as exc:
                errors.append(f"{source}: invalid production marker: {exc}")
                continue
            findings = _validate(root, entry)
            chart, exercise = entry.get("chart"), entry.get("exercise")
            key = (repr(chart), repr(exercise))
            if key in seen:
                findings.append(f"duplicate chart/exercise handoff already in {seen[key]}")
                for previous in records:
                    if (repr(previous["chart"]), repr(previous["exercise"])) == key:
                        previous["status"] = "INVALID"
                        previous["errors"].append("duplicate chart/exercise current handoff")
            else:
                seen[key] = source
            if findings:
                errors.extend(f"{source}: {x}" for x in findings)
            # Never promote a malformed declared READY/DONE to an owner queue.
            records.append({"chart": chart, "exercise": exercise,
                            "revision": entry.get("revision"), "agent": entry.get("agent"),
                            "status": entry.get("status") if not findings else "INVALID",
                            "requested_status": entry.get("status"),
                            "source": source,
                            "video_url": (entry.get("video") or {}).get("url") if isinstance(entry.get("video"), dict) else None,
                            "video_sha256": (entry.get("video") or {}).get("sha256") if isinstance(entry.get("video"), dict) else None,
                            "review": entry.get("review") if not findings else None,
                            "blocker": entry.get("blocker") if not findings else None,
                            "errors": findings})
    # Invalid active handoffs still occupy *declared* capacity until repaired.
    # Excluding them would incorrectly present an available production slot.
    active = [x for x in records if isinstance(x["requested_status"], str)
              and x["requested_status"] in ACTIVE]
    if len(active) > MAX_ACTIVE:
        errors.append(f"production WIP exceeded: {len(active)} declared active exercises, limit {MAX_ACTIVE}")
    owner_ready = [x for x in records if x["status"] == "READY_FOR_REVIEW"]
    owner_blockers = [x for x in records if x["status"] == "BLOCKED" and
                      (x.get("blocker") or {}).get("owner_needed") is True]
    specs = []
    known = {(x["chart"], x["exercise"]) for x in records
             if type(x["chart"]) is int and type(x["exercise"]) is int}
    for path in sorted((root / SPEC_ROOT).glob("*.json")):
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{path.relative_to(root)}: invalid motion spec: {exc}")
            continue
        if (not isinstance(spec, dict) or type(spec.get("chart")) is not int or
                type(spec.get("exercise")) is not int or
                spec.get("chart") not in range(1, 7) or spec.get("exercise") not in range(1, 6)):
            errors.append(f"{path.relative_to(root)}: invalid motion spec chart/exercise")
            continue
        if (spec["chart"], spec["exercise"]) not in known:
            specs.append({"chart": spec.get("chart"), "exercise": spec.get("exercise"),
                          "name": spec.get("name"), "spec": path.relative_to(root).as_posix(),
                          "status": "UNREGISTERED"})
    return {"schema_version": 1, "source": str(QA_ROOT),
            "coverage": "Only explicitly embedded current QA handoffs; absent markers do not mean inactive agents.",
            "active_wip": {"declared": len(active), "limit": MAX_ACTIVE,
                           "complete": False},  # External/unregistered agents are not observable.
            "ready_for_review": owner_ready, "owner_blockers": owner_blockers,
            "done": [x for x in records if x["status"] == "DONE"],
            "other_recorded": [x for x in records if x["status"] not in ("READY_FOR_REVIEW", "DONE")],
            "unregistered_specs": specs, "errors": errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, help="Write a JSON snapshot; otherwise print to stdout")
    parser.add_argument("--check", action="store_true", help="Fail CI on invalid handoffs or declared WIP")
    args = parser.parse_args(argv)
    result = collect(args.repo_root)
    raw = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(raw, encoding="utf-8")
        print(f"Wrote {args.out}: {len(result['ready_for_review'])} owner-ready; "
              f"{len(result['owner_blockers'])} owner blockers; {len(result['errors'])} errors")
    else:
        print(raw, end="")
    return 1 if args.check and result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
