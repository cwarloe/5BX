#!/usr/bin/env python3
"""Evidence-only quality and throughput measurements for the photo traveler.

The existing photographic QA Markdown is the record of truth. The report is a
*measurement*, not a release decision, work-order database, or asset registry.
Missing times, costs, and first-attempt verdicts remain null rather than zero.

Future producers may write ONE machine-readable comment beside their existing
QA narrative, for example::

    <!-- 5bx-metric id=C1-19V1 chart=1 exercise=5 stage=still trial=1 quality=fail credits=2 -->
    <!-- 5bx-metric id=C1-19V2 chart=1 exercise=5 stage=still trial=2 quality=pass credits=2 start=2026-11-26T15:00:00Z end=2026-11-26T15:04:00Z manual_minutes=1 -->

The `quality` field means the named *technical* gate; it never means human
exercise-form approval. Record dates as actual timestamps, not inferred batch
dates. `trial` is the attempt number within that exercise and production stage.
"""

import argparse
from collections import Counter
import json
import re
import shlex
from datetime import datetime, timezone
from pathlib import Path

try:
    from . import photo_traveler
except ImportError:  # Direct `python sprites/kit/photo_metrics.py` execution.
    import photo_traveler


MARKER = re.compile(r"<!--\s*5bx-metric\s+([^<>]*?)\s*-->", re.I)
FLOAT = re.compile(r"^(?:0|[1-9]\d*)(?:\.\d+)?$")
EXPECTED_KEYS = {"id", "chart", "exercise", "stage", "trial", "quality",
                 "credits", "manual_minutes", "start", "end"}
STAGES = {"brief", "still", "intake", "form_qa", "human_review", "video", "release"}
QUALITIES = {"pass", "fail", "hold", "unknown"}


def _timestamp(value):
    """Only actual ISO8601 timestamps with a timezone can measure duration."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def _number(value):
    if not isinstance(value, str) or not FLOAT.fullmatch(value):
        return None
    return float(value)


def _metric(value, unit, samples, note):
    return {"value": value, "unit": unit, "sample_size": samples, "note": note}


def _read_annotations(folder, charts):
    """Read optional measurements from canonical QA files; skip bad markers."""
    records, warnings = {}, []
    for path in sorted(folder.rglob("*.md")):
        source = path.relative_to(folder).as_posix()
        for match in MARKER.finditer(path.read_text(encoding="utf-8")):
            try:
                tokens = shlex.split(match.group(1))
                fields = dict(token.split("=", 1) for token in tokens if "=" in token)
                if len(fields) != len(tokens) or not set(fields).issubset(EXPECTED_KEYS):
                    raise ValueError("unexpected or malformed fields")
                chart = int(fields["chart"])
                trial = int(fields["trial"])
                if chart not in range(1, 7) or trial < 1:
                    raise ValueError("invalid chart/trial")
                asset_id = fields["id"]
                exercise = fields["exercise"]
                stage = fields["stage"].lower()
                quality = fields.get("quality", "unknown").lower()
                if (not asset_id or not exercise or stage not in STAGES or
                        quality not in QUALITIES):
                    raise ValueError("invalid id/exercise/stage/quality")
                credits = _number(fields["credits"]) if "credits" in fields else None
                minutes = _number(fields["manual_minutes"]) if "manual_minutes" in fields else None
                if ("credits" in fields and credits is None or
                        "manual_minutes" in fields and minutes is None):
                    raise ValueError("invalid nonnegative credits/minutes")
                start, end = _timestamp(fields.get("start")), _timestamp(fields.get("end"))
                if ("start" in fields and start is None or
                        "end" in fields and end is None or
                        start and end and end < start):
                    raise ValueError("invalid timestamp or reverse duration")
            except (KeyError, ValueError) as error:
                warnings.append(f"{source}: ignored malformed 5bx-metric ({error})")
                continue
            if chart not in charts:
                continue
            key = (chart, exercise, stage, asset_id)
            if key in records:
                warnings.append(f"{source}: duplicate measurement for {asset_id}; ignored")
                continue
            records[key] = {"id": asset_id, "chart": chart, "exercise": exercise,
                            "stage": stage, "trial": trial, "quality": quality,
                            "credits": credits, "manual_minutes": minutes,
                            "start": start, "end": end, "source": source}
    return list(records.values()), warnings


def _known_pilot_cost(folder, charts):
    """The explicitly documented Flow 20 cost is a single observation.

    Don't sum duplicated mentions of the same experiment in the mobile index,
    QA report and inventory. Nor treat it as total production spend.
    """
    if 1 not in charts:
        return []
    source = folder / "REVIEW_INVENTORY.md"
    if not source.exists():
        return []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*\*\*20\*\*\s*\|", line):
            continue
        match = re.search(r"\b(\d+(?:\.\d+)?)\s+credits\b", line, re.I)
        if match and "Flow" in line:
            return [{"chart": 1, "test": "20", "credits": float(match.group(1)),
                     "source": (photo_traveler.PHOTO_DIR / source.name).as_posix(),
                     "note": "One reported 6-second Flow pilot; not an approved video or total spend."}]
    return []


def collect_metrics(repo_root, chart=None):
    """Return JSON-serializable documented observations and measurement gaps.

    The inventory counts describe only *indexed* experiments, not all tool
    generations. A valid optional 5bx-metric marker documents a single attempt
    without promoting that attempt to a production-approved asset.
    """
    root = Path(repo_root)
    charts = [chart] if chart is not None else list(range(1, 7))
    if any(n not in range(1, 7) for n in charts):
        raise ValueError("chart must be 1 through 6")
    folder = root / photo_traveler.PHOTO_DIR
    gallery = photo_traveler.gallery_data(root, chart)
    records, warnings = _read_annotations(folder, charts)
    # A source can contain multiple outputs accidentally marked "trial=1".
    # In that case their order is unresolved, so none can contribute to the
    # first-pass numerator or denominator until the production record is fixed.
    ordinals = Counter((r["chart"], r["exercise"], r["stage"], r["trial"])
                       for r in records)
    ambiguous = {key for key, count in ordinals.items() if count > 1}
    for chart_id, exercise_id, stage, trial in sorted(ambiguous):
        warnings.append(f"Chart {chart_id} exercise {exercise_id}, {stage} trial {trial}: "
                        "ambiguous attempt number, excluded from QA rate")
    quality_records = [r for r in records if r["quality"] in ("pass", "fail")
                       and (r["chart"], r["exercise"], r["stage"], r["trial"]) not in ambiguous]
    first_records = [r for r in quality_records if r["trial"] == 1]
    repeat_records = [r for r in quality_records if r["trial"] > 1]
    durations = [round((r["end"] - r["start"]).total_seconds() / 3600, 6)
                 for r in records if r["start"] and r["end"]]
    measured_credits = [r["credits"] for r in records if r["credits"] is not None]
    measured_minutes = [r["manual_minutes"] for r in records if r["manual_minutes"] is not None]
    stage_cycles = {}
    for stage in sorted(STAGES):
        values = [(r["end"] - r["start"]).total_seconds() / 3600
                  for r in records if r["stage"] == stage and r["start"] and r["end"]]
        stage_cycles[stage] = _metric(
            round(sum(values) / len(values), 4) if values else None,
            "hours (mean per measured attempt)", len(values),
            "Observed stage time only; not an estimate for missing attempts.")
    pilot = _known_pilot_cost(folder, charts)
    # Avoid counting the named test twice if later explicitly instrumented.
    if any(r["id"].upper() in ("20", "C1-20", "C1-20-FLOW") for r in records):
        pilot = []
    metric_dict = {
        "first_pass_yield": _metric(
            round(sum(r["quality"] == "pass" for r in first_records) / len(first_records), 4)
            if first_records else None, "fraction", len(first_records),
            "Technical QA pass on explicitly numbered first attempts only; not human approval."
            if first_records else "No complete first-attempt technical QA outcomes recorded."),
        "repeat_attempt_share": _metric(
            round(len(repeat_records) / len(quality_records), 4) if quality_records else None,
            "fraction", len(quality_records),
            "Share of measured QA attempts explicitly numbered trial >1; not an end-to-end rework rate."
            if quality_records else "No complete numbered-attempt QA outcomes recorded."),
        "cycle_time_hours": _metric(
            round(sum(durations) / len(durations), 4) if durations else None,
            "hours (mean per measured stage attempt)", len(durations),
            "Elapsed from recorded stage start to finish; not total exercise lead time."
            if durations else "No actual per-stage start/end timestamps recorded."),
        "credits_per_approved_video": _metric(None, "credits/video", 0,
            "No exact human-approved video with linked full production credit spend."),
        "human_minutes_per_approval": _metric(None, "minutes/approval", 0,
            "No exact human-approved asset with linked complete manual-touch time."),
        "documented_attempt_credits": _metric(
            round(sum(measured_credits), 4) if measured_credits else None,
            "credits (known subset, not total)", len(measured_credits),
            "Sum of optional annotated per-attempt credits only; omitted generations are unknown."
            if measured_credits else "No annotated per-attempt credit values."),
        "documented_manual_minutes": _metric(
            round(sum(measured_minutes), 4) if measured_minutes else None,
            "minutes (known subset, not total)", len(measured_minutes),
            "Sum of optional annotated manual-touch minutes only; missing work is unknown."
            if measured_minutes else "No annotated manual-touch minutes."),
    }
    return {
        "scope": {"charts": charts, "source": photo_traveler.PHOTO_DIR.as_posix(),
                  "coverage": "Indexed photographic traveler plus opt-in annotations in existing QA notes; not every generated file."},
        "indexed_outputs": {"numbered_review_entries": len(gallery["items"]),
                            "latest_refinements": len(gallery["latest"]),
                            "human_questions": len(gallery["review_queue"]),
                            "explicit_hold_or_reject_labels": sum(
                                r["state"] in ("HOLD", "REJECT") for r in gallery["items"])},
        "measurements": metric_dict,
        "stage_cycle_times": stage_cycles,
        "instrumentation": {"annotated_attempts": len(records),
                            "numbered_quality_outcomes": len(quality_records),
                            "with_stage_timestamps": len(durations),
                            "with_cost": len(measured_credits),
                            "with_manual_minutes": len(measured_minutes)},
        "other_known_cost_observations": pilot,
        "warnings": warnings,
        "release_caution": "No technical PASS or image metric is a human-approved 5BX exercise or validated video."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--chart", type=int, choices=range(1, 7))
    parser.add_argument("--out", type=Path, help="Output JSON report; stdout if omitted")
    args = parser.parse_args(argv)
    data = collect_metrics(args.repo_root, args.chart)
    report = json.dumps(data, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"Wrote {args.out}: {data['instrumentation']['annotated_attempts']} annotated attempts; "
              "unmeasured values remain null")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
