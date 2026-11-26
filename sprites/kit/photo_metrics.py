#!/usr/bin/env python3
"""Evidence-only quality and throughput measurements for the photo traveler.

The existing photographic QA Markdown is the record of truth. The report is a
*measurement*, not a release decision, work-order database, or asset registry.
Missing times, costs, and first-attempt verdicts remain null rather than zero.

Future producers may write ONE machine-readable comment beside their existing
QA narrative, for example::

    <!-- 5bx-metric id=C1-19V1 chart=1 exercise=5 stage=video gate=motion trial=1 quality=fail provider=Google_Flow model=Omni-1.2-Flash credits=18 defect_code=LIMB_ID defect_id=C1-E5-near-leg-switch -->
    <!-- 5bx-metric id=C1-19V2 chart=1 exercise=5 stage=video gate=motion trial=2 quality=pass reviewer=independent-form-reviewer start=2026-11-26T15:00:00Z end=2026-11-26T15:04:00Z manual_minutes=1 -->

The `quality` field means the named *internal* inspection gate; it never means
Charles's exercise-form approval. Record dates as actual timestamps, not
inferred batch dates. `trial` is the attempt number within that exercise and
production stage; `gate` narrows comparisons to the same quality criterion.
Costs expressed as provider credits are never added across different providers.
"""

import argparse
from collections import Counter, defaultdict
import json
import math
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
EXPECTED_KEYS = {"id", "chart", "exercise", "stage", "trial", "gate", "quality",
                 "credits", "cost_usd", "manual_minutes", "start", "end",
                 "provider", "model", "reviewer", "defect_code", "defect_id"}
STAGES = {"brief", "still", "intake", "form_qa", "human_review", "video", "release"}
GATES = STAGES | {"technical", "form", "motion", "loop", "identity", "contact"}
QUALITIES = {"pass", "fail", "hold", "unknown"}
DEFECT_CODES = {"FORM", "LIMB_ID", "HAND", "OCCLUSION", "IDENTITY", "FRAMING",
                "CONTACT", "LOOP", "RECOVERY", "SOURCE"}


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
    number = float(value)
    return number if math.isfinite(number) else None


def _metric(value, unit, samples, note):
    return {"value": value, "unit": unit, "sample_size": samples, "note": note}


def _known_field(fields, key):
    value = fields.get(key)
    return value if value and value.lower() != "unknown" else None


def _yield(records):
    """Technical/internal first-pass yield for a *single comparable gate*."""
    first = [r for r in records if r["trial"] == 1]
    return _metric(round(sum(r["quality"] == "pass" for r in first) / len(first), 4)
                   if first else None, "fraction", len(first),
                   "Passes among explicitly numbered first attempts assessed at this gate; "
                   "not owner acceptance.")


def _read_annotations(folder, charts):
    """Read optional measurements from canonical QA files; skip bad markers."""
    records, warnings = {}, []
    for path in sorted(folder.rglob("*.md")):
        source = path.relative_to(folder).as_posix()
        for match in MARKER.finditer(path.read_text(encoding="utf-8")):
            try:
                tokens = shlex.split(match.group(1))
                pairs = [token.split("=", 1) for token in tokens if "=" in token]
                fields = dict(pairs)
                if (len(pairs) != len(tokens) or len(fields) != len(pairs)
                        or not set(fields).issubset(EXPECTED_KEYS)):
                    raise ValueError("unexpected or malformed fields")
                chart = int(fields["chart"])
                trial = int(fields["trial"])
                exercise = int(fields["exercise"])
                if chart not in range(1, 7) or exercise not in range(1, 6) or trial < 1:
                    raise ValueError("invalid chart/exercise/trial")
                asset_id = fields["id"]
                stage = fields["stage"].lower()
                gate = fields.get("gate", stage).lower()
                quality = fields.get("quality", "unknown").lower()
                if not asset_id or stage not in STAGES or gate not in GATES or quality not in QUALITIES:
                    raise ValueError("invalid id/stage/gate/quality")
                values = {name: (_number(fields[name]) if name in fields and
                                 fields[name].lower() != "unknown" else None)
                          for name in ("credits", "cost_usd", "manual_minutes")}
                if any(name in fields and values[name] is None and
                       fields[name].lower() != "unknown" for name in values):
                    raise ValueError("invalid nonnegative credits/cost_usd/minutes")
                provider = _known_field(fields, "provider")
                model = _known_field(fields, "model")
                reviewer = _known_field(fields, "reviewer")
                defect_code = _known_field(fields, "defect_code")
                defect_id = _known_field(fields, "defect_id")
                if any(name in fields and not fields[name].strip() for name in
                       ("provider", "model", "reviewer", "defect_code", "defect_id")):
                    raise ValueError("empty provider/model/reviewer/defect")
                if defect_code and defect_code.upper() not in DEFECT_CODES:
                    raise ValueError("unknown defect_code")
                if gate in {"form", "motion"} and quality == "pass" and not reviewer:
                    raise ValueError("form/motion PASS requires a named independent reviewer")
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
            key = (chart, exercise, stage, gate, asset_id)
            if key in records:
                warnings.append(f"{source}: duplicate measurement for {asset_id}; ignored")
                continue
            records[key] = {"id": asset_id, "chart": chart, "exercise": exercise,
                            "stage": stage, "gate": gate, "trial": trial, "quality": quality,
                            "credits": values["credits"], "cost_usd": values["cost_usd"],
                            "manual_minutes": values["manual_minutes"],
                            "provider": provider, "model": model, "reviewer": reviewer,
                            "defect_code": defect_code.upper() if defect_code else None,
                            "defect_id": defect_id,
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


def _deduplicate_attempt_costs(records, warnings):
    """A video measured at multiple QA gates must not be charged multiple times.

    Matching `(chart, exercise, id)` means the same attempt, even when it has
    separate technical, motion or form inspections. Conflicting values/provider
    attribution make the cost unknowable; fail closed rather than picking one.
    """
    for field in ("credits", "cost_usd"):
        first_by_attempt = {}
        conflicts = set()
        for record in records:
            if record[field] is None:
                continue
            key = (record["chart"], record["exercise"], record["id"])
            if key in conflicts:
                record[field] = None
                continue
            prior = first_by_attempt.get(key)
            if prior is None:
                first_by_attempt[key] = record
                continue
            if prior[field] == record[field] and prior["provider"] == record["provider"]:
                warnings.append(f'{record["source"]}: duplicate {field} for attempt '
                                f'{record["id"]}; counted once across QA gates')
            else:
                warnings.append(f'{record["source"]}: conflicting {field} for attempt '
                                f'{record["id"]}; all conflicting measurements excluded')
                prior[field] = None
                conflicts.add(key)
            record[field] = None


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
    _deduplicate_attempt_costs(records, warnings)
    # A source can contain multiple outputs accidentally marked "trial=1".
    # In that case their order is unresolved, so none can contribute to the
    # first-pass numerator or denominator until the production record is fixed.
    ordinals = Counter((r["chart"], r["exercise"], r["stage"], r["gate"], r["trial"])
                       for r in records)
    ambiguous = {key for key, count in ordinals.items() if count > 1}
    for chart_id, exercise_id, stage, gate, trial in sorted(ambiguous):
        warnings.append(f"Chart {chart_id} exercise {exercise_id}, {stage}/{gate} trial {trial}: "
                        "ambiguous attempt number, excluded from QA rate")
    quality_records = [r for r in records if r["quality"] in ("pass", "fail")
                       and (r["chart"], r["exercise"], r["stage"], r["gate"], r["trial"]) not in ambiguous]
    quality_ids = {id(r) for r in quality_records}
    first_records = [r for r in quality_records if r["trial"] == 1]
    repeat_records = [r for r in quality_records if r["trial"] > 1]
    gate_groups = defaultdict(list)
    provider_groups = defaultdict(list)
    credit_groups = defaultdict(list)
    defect_counts = Counter()
    distinct_defects = defaultdict(set)
    for record in records:
        key = f'{record["stage"]}/{record["gate"]}'
        gate_groups[key].append(record)
        provider = record["provider"] or "unattributed"
        provider_groups[provider].append(record)
        if record["credits"] is not None:
            credit_groups[provider].append(record["credits"])
        if record["defect_code"]:
            defect_counts[record["defect_code"]] += 1
        if record["defect_id"]:
            distinct_defects[(record["chart"], record["exercise"], record["defect_id"])].add(
                record["id"])
    comparable_gates = {(r["stage"], r["gate"]) for r in quality_records}
    gate_breakdown = {}
    for gate, gate_records in sorted(gate_groups.items()):
        evaluated = [r for r in gate_records if id(r) in quality_ids]
        gate_breakdown[gate] = {
            "observed_attempts": len(gate_records),
            "assessed_quality_attempts": len(evaluated),
            "first_pass_yield": _yield(evaluated),
        }
    provider_breakdown = {}
    for provider, provider_records in sorted(provider_groups.items()):
        assessed = [r for r in provider_records if id(r) in quality_ids]
        by_gate = defaultdict(list)
        for record in assessed:
            by_gate[f'{record["stage"]}/{record["gate"]}'].append(record)
        provider_breakdown[provider] = {
            "observed_attempts": len(provider_records),
            "with_model": sum(r["model"] is not None for r in provider_records),
            "with_credit_measurement": sum(r["credits"] is not None for r in provider_records),
            "documented_credits": round(sum(credit_groups.get(provider, [])), 4)
                                  if credit_groups.get(provider) else None,
            "documented_cost_usd": round(sum(r["cost_usd"] for r in provider_records
                                              if r["cost_usd"] is not None), 4)
                                   if any(r["cost_usd"] is not None for r in provider_records)
                                   else None,
            "first_pass_yield_by_gate": {gate: _yield(group)
                                         for gate, group in sorted(by_gate.items())},
        }
    durations = [round((r["end"] - r["start"]).total_seconds() / 3600, 6)
                 for r in records if r["start"] and r["end"]]
    measured_credits = [r["credits"] for r in records if r["credits"] is not None]
    measured_usd = [r["cost_usd"] for r in records if r["cost_usd"] is not None]
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
            _yield(quality_records)["value"] if len(comparable_gates) == 1 else None,
            "fraction", len(first_records),
            "Single comparable stage/gate only; see gate_breakdown for all inspected gates. "
            "Never owner approval." if len(comparable_gates) == 1
            else "Mixed or missing quality-gate definitions; combined yield would be misleading."),
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
            round(sum(measured_credits), 4) if len(credit_groups) == 1 else None,
            "credits (known subset, not total)", len(measured_credits),
            "One attributed provider; omitted generations are unknown."
            if len(credit_groups) == 1 else
            "Mixed providers or no observations; provider credits have incompatible units. "
            "Use provider_breakdown instead."),
        "documented_attempt_cost_usd": _metric(
            round(sum(measured_usd), 4) if measured_usd else None,
            "USD (known subset, not total)", len(measured_usd),
            "Sum of actual annotated dollar charges only; prepaid credits are not dollars "
            "unless the provider measured them as such."),
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
        "gate_breakdown": gate_breakdown,
        "provider_breakdown": provider_breakdown,
        "defect_breakdown": {
            "observed_attempts_by_code": dict(sorted(defect_counts.items())),
            "distinct_stable_defect_ids": len(distinct_defects),
            "repeated_stable_defects": sum(len(ids) > 1 for ids in distinct_defects.values()),
            "note": "Only exact annotated defect IDs can be counted as repeats; broad codes "
                    "do not identify the same underlying defect."
        },
        "instrumentation": {"annotated_attempts": len(records),
                            "numbered_quality_outcomes": len(quality_records),
                            "with_stage_timestamps": len(durations),
                            "with_cost": len(measured_credits),
                            "with_cost_usd": len(measured_usd),
                            "with_provider": sum(r["provider"] is not None for r in records),
                            "with_model": sum(r["model"] is not None for r in records),
                            "with_explicit_gate": sum(r["gate"] != r["stage"] for r in records),
                            "with_defect_id": sum(r["defect_id"] is not None for r in records),
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
