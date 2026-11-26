"""CLI: python3 -m photo_motion {validate,prompt,inspect} ..."""

import argparse
import json
import sys
from pathlib import Path

from .contract import load_spec, validate
from .extended_contract import EXTENDED, validate_extended


def _check_spec(spec):
    """Route additional photographic movements through their own form rules."""
    if not isinstance(spec, dict):
        return validate(spec)
    return validate_extended(spec) if spec.get("movement_type") in EXTENDED else validate(spec)


def _prompt(spec):
    """Deterministic, tool-neutral prompt draft; no AI call and no credited spend."""
    lines = [
        f"Generate ONE uninterrupted {spec['duration_seconds']:g}-second real photographic video of {spec['name']}, at about {spec['fps']} fps.",
        f"IDENTITY AUTHORITY (attach its actual image separately): {spec['identity_reference']}.",
        f"MOVEMENT AUTHORITY (inspect source separately): {spec['movement_reference']}.",
        f"CAMERA: {spec['camera']['description']}",
        "Required chronological physical phases; times are targets, never permission to dissolve between stills.",
        "Structured physical states below are mandatory: SUPPORT and CONTACTS describe actual foot/hand/body contact, and LIMBS name the same physical anatomy across time. Resolve any conflict with the descriptive pose text BEFORE submitting the prompt:"
    ]
    if spec.get("track_provenance"):
        lines.append("ORIGINAL SOURCE MARKER AUTHORITY: "
                     + json.dumps(spec["track_provenance"], sort_keys=True, separators=(",", ":")))
    for phase in spec["phases"]:
        physical = {key: value for key, value in phase.items()
                    if key not in ("id", "time_seconds", "pose")}
        lines.append(f"  {phase['time_seconds']:g}s [{phase['id']}] MANDATORY_PHYSICAL_STATE "
                     f"{json.dumps(physical, sort_keys=True, separators=(',', ':'))}")
        lines.append(f"    Visual description: {phase['pose']}")
    lines.append("Hard rules:")
    for rule in spec["rules"]:
        lines.append(f"  - {rule}")
    lines.append("Perform actual continuous motion between key phases; preserve physical limb ownership and contacts. End in the original start pose. No voice, captions or music.")
    lines.append("This text is a proposed generation input, NOT evidence that the model obeyed it or that the output is approved.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Photographic 5BX motion specification, prompt and MP4 QA")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("validate", help="Check one or more independent motion contracts")
    check.add_argument("spec", nargs="+", type=Path)
    prompt = sub.add_parser("prompt", help="Draft a repeatable video-generation prompt from a valid contract")
    prompt.add_argument("spec", type=Path)
    inspect = sub.add_parser("inspect", help="Inspect a real MP4 and create timestamped sample evidence")
    inspect.add_argument("spec", type=Path)
    inspect.add_argument("video", type=Path)
    inspect.add_argument("--out", type=Path, required=True, help="Directory for frame evidence; no source files modified")
    inspect.add_argument("--recipe", type=Path, help="Optional actual generator run record with exact submitted prompt and input refs")
    args = parser.parse_args(argv)
    if args.command == "validate":
        ok = True
        for path in args.spec:
            try:
                spec = load_spec(path)
                issues = _check_spec(spec)
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
                issues = [str(error)]
            print(f"{'FAIL' if issues else 'PASS'} {path}")
            for issue in issues:
                print(f"  - {issue}")
            ok = ok and not issues
        return 0 if ok else 1
    try:
        spec = load_spec(args.spec)
        issues = _check_spec(spec)
        if issues:
            for issue in issues:
                print(f"ERROR: {issue}", file=sys.stderr)
            return 1
        if args.command == "prompt":
            print(_prompt(spec), end="")
            return 0
        from .video_qa import inspect as inspect_video
        result = inspect_video(spec, args.spec, args.video, args.out, args.recipe)
        print(json.dumps({"output": str(args.out.resolve()), "video": result["video"],
                          "technical_warnings": result["technical_warnings"],
                          "provenance_warning": result["provenance_warning"],
                          "form_and_release_approval": result["form_and_release_approval"]}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
