#!/usr/bin/env python3
"""One quick, read-only view of the 5BX sprite production line.

From the repository root:
  python3 sprites/kit/line.py status   # what is ready, missing or needs review?
  python3 sprites/kit/line.py check    # validate structure; nonzero only for real data errors
  python3 sprites/kit/line.py release-check --chart 2  # strict artwork gate before publishing

No images, paid calls, network, image libraries or extra database required.
Raw art is intentionally stored outside Git; absence from a clean clone is a
warning for status/check, not a corrupted project. The separate release-check
requires restored sheets and named form review. See ART.md for restoration.
"""

import argparse
import hashlib
import json
from pathlib import Path


SLOTS = ("ex1", "ex2", "ex3", "ex4", "run", "jump")


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def pose_number(value):
    """A cycle step is a positive pose number, optionally suffixed 'm' (mirror)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return (value, False) if value > 0 else None
    if isinstance(value, str) and value.endswith("m") and value[:-1].isdigit():
        number = int(value[:-1])
        return (number, True) if number > 0 else None
    return None


def reviewed_by_human(entry):
    """Existing library flag, or a future explicit human review attribution."""
    return bool(entry.get("form_reviewed_by") or (entry.get("expert_reviewed") and entry.get("graded_by")))


def analyze(plan, registry, prompt_data, library, sheets_dir):
    """Pure checks plus local sheet availability. Never changes project state."""
    errors, warnings, charts = [], [], []
    strips = registry.get("strips", {})
    mappings = registry.get("charts", {})
    prompts = prompt_data.get("strips", {})
    entries = library.get("entries", [])
    plan_ids = {str(c["id"]) for c in plan.get("charts", [])}

    for name, strip in strips.items():
        if name not in prompts:
            errors.append(f"{name}: no prompt specification")
        n = strip.get("poses")
        if type(n) is not int or n < 1:
            errors.append(f"{name}: invalid registered pose count {n!r}")
            continue
        for field in ("cycle", "cycle_reverse"):
            steps = strip.get(field, [])
            if field == "cycle" and not steps:
                errors.append(f"{name}: missing movement cycle")
            for step in steps:
                parsed = pose_number(step)
                if not parsed or parsed[0] > n:
                    errors.append(f"{name}: invalid {field} pose {step!r} (1–{n})")
                elif parsed[1] and parsed[0] not in strip.get("mirror", []):
                    errors.append(f"{name}: mirrored pose {step!r} not declared in 'mirror'")
        if "rows" in strip and (type(strip.get("rows")) is not int or strip["rows"] < 1 or
                                type(strip.get("row")) is not int or not 0 <= strip["row"] < strip["rows"]):
            errors.append(f"{name}: row must be within the declared number of rows")
        if name in prompts and len(prompts[name].get("poses", [])) != n:
            warnings.append(f"{name}: prompt describes {len(prompts[name].get('poses', []))} poses; registry uses {n} (verify intentional extra pose)")

    known_ids = set()
    for entry in entries:
        item = entry.get("id")
        if item in known_ids:
            errors.append(f"duplicate library asset ID {item}")
        known_ids.add(item)

    for cid in mappings:
        if cid not in plan_ids:
            errors.append(f"chart {cid}: not found in 5bx-charts.json")

    for cid in sorted(plan_ids, key=int):
        mapped = mappings.get(cid, {})
        missing = [s for s in SLOTS if s not in mapped]
        unknown = [s for s in mapped if s not in SLOTS]
        if unknown:
            errors.append(f"chart {cid}: invalid slot(s): {', '.join(unknown)}")
        if missing:
            warnings.append(f"chart {cid}: unmapped slots: {', '.join(missing)}")
        chosen = 0
        needs_review = []
        absent_art = []
        for slot, name in mapped.items():
            if name not in strips:
                errors.append(f"chart {cid} {slot}: unknown strip {name}")
                continue
            if not (sheets_dir / strips[name].get("file", "")).is_file():
                absent_art.append(slot)
            options = [e for e in entries if e.get("strip") == name and e.get("verdict") == "chosen"]
            if len(options) > 1:
                errors.append(f"chart {cid} {slot}: several 'chosen' assets for {name}")
            if options:
                chosen += 1
                if not any(reviewed_by_human(e) for e in options):
                    needs_review.append(slot)
            else:
                needs_review.append(slot)
        if needs_review:
            warnings.append(f"chart {cid}: chosen/human review still needed for {', '.join(needs_review)}")
        if absent_art:
            warnings.append(f"chart {cid}: {len(absent_art)} mapped sheet(s) unavailable locally; see ART.md")
        charts.append({"chart": int(cid), "mapped": len(mapped), "total": len(SLOTS),
                       "chosen": chosen, "missing": missing, "needs_review": needs_review,
                       "absent_art": absent_art})

    return {"errors": errors, "warnings": warnings, "charts": charts,
            "registered": len(strips), "prompted": len(prompts), "library_entries": len(entries)}


def repository_report(repo_root):
    sprites = repo_root / "sprites"
    report = analyze(read_json(repo_root / "data" / "5bx-charts.json"),
                     read_json(sprites / "config" / "strips.json"),
                     read_json(sprites / "prompts" / "strips.json"),
                     read_json(sprites / "library" / "index.json"),
                     sprites / "sheets")
    missing = missing_backdrop_images(read_json(sprites / "config" / "theme.json"),
                                      sprites, [c["chart"] for c in report["charts"]])
    for chart in report["charts"]:
        cid = chart["chart"]
        chart["missing_backdrop"] = missing.get(cid)
        if cid in missing:
            report["warnings"].append(f"chart {cid}: backdrop picture {missing[cid]} unavailable locally; see ART.md")
    return report


def missing_backdrop_images(theme, sprites_dir, chart_ids):
    """Flag archived image backdrops used by the builder; code-drawn rooms need no file."""
    missing = {}
    for cid in chart_ids:
        look = theme.get("chart_looks", {}).get(str(cid), {})
        backdrop = look.get("backdrop") or theme.get("backdrop", {})
        if backdrop.get("style") != "image":
            continue
        source = backdrop.get("image")
        if not source or not (sprites_dir / source).is_file():
            missing[cid] = source or "(image path not configured)"
    return missing


def release_readiness(report, registry, library, sheets_dir, chart=None):
    """Strict artwork gate: verify selected bytes and a positive human form grade.

    The normal preflight allows work in progress. This command intentionally
    fails on incomplete charts or art that is only stored in Drive. It does not
    replace final-video playback or mechanical pose QC.
    """
    candidates = [c for c in report["charts"] if chart is None or c["chart"] == chart]
    if not candidates:
        return [{"chart": chart, "blockers": [f"chart {chart}: not found in the 5BX plan"]}]
    strips = registry.get("strips", {})
    entries = library.get("entries", [])
    results = []
    for item in candidates:
        cid = item["chart"]
        mapped = registry.get("charts", {}).get(str(cid), {})
        blockers = []
        for slot in SLOTS:
            name = mapped.get(slot)
            if not name:
                blockers.append(f"{slot}: exercise not mapped")
                continue
            spec = strips.get(name)
            if not spec:
                blockers.append(f"{slot}: unknown strip {name}")
                continue
            sheet = sheets_dir / spec["file"]
            if not sheet.is_file():
                blockers.append(f"{slot}: source sheet {spec['file']} not restored (see ART.md)")
            chosen = [e for e in entries if e.get("strip") == name and e.get("verdict") == "chosen"]
            if len(chosen) != 1:
                blockers.append(f"{slot}: expected one chosen asset for {name}, found {len(chosen)}")
                continue
            selected = chosen[0]
            asset_id = selected.get("id", "unknown")
            if not reviewed_by_human(selected):
                blockers.append(f"{slot}: {asset_id} lacks a named human form review")
            else:
                form = selected.get("grades", {}).get("form")
                if type(form) is not int or form < 4:
                    blockers.append(f"{slot}: {asset_id} needs a passing form grade (4 or 5)")
            recorded = selected.get("measured", {}).get("sha")
            if not recorded:
                blockers.append(f"{slot}: {asset_id} has no recorded source-image hash")
            elif sheet.is_file():
                actual = hashlib.sha1(sheet.read_bytes()).hexdigest()[:len(recorded)]
                if actual != recorded:
                    blockers.append(f"{slot}: {spec['file']} differs from chosen asset {asset_id}; inspect version before release")
        results.append({"chart": cid, "blockers": blockers})
    return results


def show_release(report, results):
    print("5BX artwork release gate — not a substitute for final-video review")
    for item in results:
        blockers = item["blockers"]
        print(f"  Chart {item['chart']}: " + (f"HOLD ({len(blockers)} item(s))" if blockers else "ART READY"))
        for issue in blockers:
            print(f"    HOLD: {issue}")
    for error in report["errors"]:
        print(f"  ERROR: {error}")
    print("Final video still requires playback, timing and mobile-legibility review.")


def show(report, detailed=False):
    print("5BX production line — read-only readiness")
    print(f"{report['registered']} registered strips, {report['prompted']} prompt recipes, {report['library_entries']} library records")
    for chart in report["charts"]:
        print(f"  Chart {chart['chart']}: {chart['mapped']}/{chart['total']} slots mapped; "
              f"{chart['chosen']} chosen; {len(chart['needs_review'])} need human form review; "
              f"{len(chart['absent_art'])} sheets not local" +
              ("; backdrop picture not local" if chart.get("missing_backdrop") else ""))
        if chart["missing"]:
            print(f"    unmapped: {', '.join(chart['missing'])}")
    print(f"Structural errors: {len(report['errors'])}; follow-up warnings: {len(report['warnings'])}")
    for error in report["errors"]:
        print(f"  ERROR: {error}")
    if detailed:
        for warning in report["warnings"]:
            print(f"  WARN: {warning}")
    else:
        print("Run 'check' to see all warnings. Missing Drive art does not mean a broken clone.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("status", "check", "release-check"))
    parser.add_argument("--chart", type=int, help="for release-check, validate just this chart")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2],
                        help="override repository root for tests")
    args = parser.parse_args(argv)
    try:
        report = repository_report(args.repo_root)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"unable to inspect production inputs: {exc}\n")
    if args.command == "release-check":
        sprites = args.repo_root / "sprites"
        results = release_readiness(report, read_json(sprites / "config" / "strips.json"),
                                    read_json(sprites / "library" / "index.json"),
                                    sprites / "sheets", chart=args.chart)
        show_release(report, results)
        return 1 if report["errors"] or any(c["blockers"] for c in results) else 0
    if args.chart is not None:
        parser.error("--chart is only for release-check")
    show(report, detailed=args.command == "check")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
