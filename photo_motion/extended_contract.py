"""Additional Chart 1 photographic motion checks.

The common structural validator currently registers only the initial scissor
and kneeling-push-up pilots. This companion module composes its structural
checks without changing the active validator during parallel development.

All checks validate the *requested* motion contract. They cannot verify an
AI-generated clip or approve exercise form.

Run: python3 -m photo_motion.extended_contract photo_motion/specs/chart1-*.json
"""

import argparse
import sys
from .contract import load_spec, validate


EXTENDED = {"toe_touch", "partial_situp", "alternate_leg_raise", "stationary_run_low"}


def validate_extended(spec):
    """Validate common shape, then exercise-specific physical sequence rules."""
    if not isinstance(spec, dict):
        return ["motion contract must be an object"]
    kind = spec.get("movement_type")
    if kind not in EXTENDED:
        return [f"unsupported extended movement_type {kind!r}"]
    # The core already does all generic timestamp, support/contact, fixed
    # camera and loop-closure checking. Its only expected extra diagnostic is
    # that the new kind is not yet registered in the core dispatch table.
    errors = validate(spec)
    unknown = f"unknown movement_type {kind!r}"
    if unknown in errors:
        errors.remove(unknown)
    if errors:
        return errors
    phases = spec["phases"]
    checks = {
        "toe_touch": _toe_touch,
        "partial_situp": _partial_situp,
        "alternate_leg_raise": _alternate_leg_raise,
        "stationary_run_low": _stationary_run,
    }
    return checks[kind](phases)


def _expected(phases, field, values, name):
    actual = [p.get(field) for p in phases]
    return [] if actual == values else [f"{name}: {field} phases must be {values}, got {actual}"]


def _stable_contacts(phases, required, name):
    errors = []
    for p in phases:
        if p["support"] != "grounded" or set(p["contacts"]) != required:
            errors.append(f"{name} phase {p['id']}: support must stay planted at {sorted(required)}")
    return errors


def _toe_touch(phases):
    errors = _expected(phases, "motion", ["upright", "forward_fold", "upright", "gentle_backbend", "upright"], "toe touching")
    errors += _expected(phases, "fingertips_touch_floor", [False, True, False, False, False],
                        "toe touching: fingertips must actually TOUCH the floor between feet at the forward-fold peak")
    errors += _stable_contacts(phases, {"left_sole", "right_sole"}, "toe touching")
    for p in phases:
        if p.get("feet_fixed") is not True:
            errors.append(f"toe touching phase {p['id']}: feet must remain at the original track points")
        if p.get("range") == "hyperextended":
            errors.append(f"toe touching phase {p['id']}: do not demand an extreme backbend or body-length change")
    if len(phases) == 5:
        if phases[1].get("hand_target") != "between_feet":
            errors.append("toe touching: Chart 1 hands must reach toward BETWEEN both shoes, not outside either shoe")
        if phases[3].get("range") != "modest":
            errors.append("toe touching: Chart 1 backward lean must be modest, not gymnastics-grade")
        if phases[0].get("arms") != "up" or phases[-1].get("arms") != "up":
            errors.append("toe touching: return to original arms-overhead posture")
    return errors


def _partial_situp(phases):
    errors = _expected(phases, "shoulders", ["down", "lifting", "slightly_raised", "down"], "partial sit-up")
    errors += _stable_contacts(phases, {"left_heel", "right_heel", "pelvis"}, "partial sit-up")
    for p in phases:
        if p.get("legs") != "straight":
            errors.append(f"partial sit-up phase {p['id']}: knees remain straight")
        if p.get("arms") != "at_sides":
            errors.append(f"partial sit-up phase {p['id']}: arms remain at sides, not overhead or behind head")
        if p.get("full_situp") is True:
            errors.append(f"partial sit-up phase {p['id']}: do not turn Chart 1 curl into a full sit-up")
    if len(phases) == 4 and phases[2].get("heel_visibility") != "see_heels":
        errors.append("partial sit-up: peak is just high enough to see heels, with head and shoulders clear")
    return errors


def _alternate_leg_raise(phases):
    errors = _expected(phases, "head", ["rest", "raised", "rest", "raised", "rest"], "alternate leg raise")
    errors += _stable_contacts(phases, {"pelvis", "left_palm", "right_palm"}, "alternate leg raise")
    if len(phases) == 5:
        expected = [
            {"orange_leg": "rest", "teal_leg": "rest"},
            {"orange_leg": "raised", "teal_leg": "rest"},
            {"orange_leg": "rest", "teal_leg": "rest"},
            {"orange_leg": "rest", "teal_leg": "raised"},
            {"orange_leg": "rest", "teal_leg": "rest"},
        ]
        actual = [p.get("limbs") for p in phases]
        if actual != expected:
            errors.append("alternate leg raise: the SAME physical orange leg raises first, teal leg second, with a neutral return between; screen-left shoe is not an identity")
    for p in phases:
        if p.get("knees") != "straight":
            errors.append(f"alternate leg raise phase {p['id']}: lifted and grounded knees must stay straight")
        if p.get("palms") != "under_thighs":
            errors.append(f"alternate leg raise phase {p['id']}: both palms remain under thighs")
    return errors


def _stationary_run(phases):
    errors = []
    # Eight left-foot cycles in a six-second *illustrative* loop correspond to
    # 80 left contacts/min; app timing is level-specific and remains sourced
    # from data/5bx-charts.json, not imposed by this form demonstration.
    if len(phases) != 17:
        errors.append("low run: six-second illustrative gait requires 17 alternating contact states (8 complete left/right pairs)")
        return errors
    for i, p in enumerate(phases):
        expected_foot = "orange_foot" if i % 2 == 0 else "teal_foot"
        expected_limb = (
            {"orange_leg": "planted", "teal_leg": "low_lift", "orange_arm": "forward", "teal_arm": "back"}
            if i % 2 == 0 else
            {"orange_leg": "low_lift", "teal_leg": "planted", "orange_arm": "back", "teal_arm": "forward"}
        )
        if p["support"] != "grounded" or p["contacts"] != [expected_foot]:
            errors.append(f"low run phase {p['id']}: plant physical {expected_foot} in alternation; do not relabel by screen position")
        if p.get("limbs") != expected_limb:
            errors.append(f"low run phase {p['id']}: wrong physical leg or opposite arm tracking")
        if p.get("foot_lift_class") != "low_about_four_inches":
            errors.append(f"low run phase {p['id']}: Chart 1 requires small four-inch-style foot clearance, not waist-high knees")
    if phases[0].get("limbs") != phases[-1].get("limbs"):
        errors.append("low run first/last physical arm and leg states differ")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate additional photographic Chart 1 exercise contracts")
    parser.add_argument("specs", nargs="+", help="JSON photographic motion contracts")
    args = parser.parse_args(argv)
    any_errors = False
    for path in args.specs:
        try:
            spec = load_spec(path)
            errors = validate_extended(spec)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors = [str(exc)]
        print(f"{'FAIL' if errors else 'PASS'} {path}")
        for error in errors:
            print(f"  - {error}")
        any_errors |= bool(errors)
    return 1 if any_errors else 0


if __name__ == "__main__":
    sys.exit(main())
