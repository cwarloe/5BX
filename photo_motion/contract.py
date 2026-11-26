"""Dependency-free structural and movement-specific checks for photographic motion.

These are assertions about the *planned* motion, never machine proof that an
AI-generated still/video obeys the plan. Only the owner can approve actual form.
"""

import json
import math
from pathlib import Path


REQUIRED = ("schema_version", "id", "chart", "exercise", "name", "status",
            "duration_seconds", "fps", "identity_reference", "movement_reference",
            "camera", "phases", "rules", "movement_type")
SUPPORTS = {"grounded", "airborne"}
STATUSES = {"EXPERIMENTAL", "REVIEW", "CANDIDATE", "HOLD"}
# Movement identity is pinned to the original Chart 1 exercise numbering in
# data/5bx-charts.json. Scissor jumps occur within Exercise 5's run interval;
# a motion description for another chart/exercise must not silently validate.
CHART1_MOVEMENT_EXERCISE = {
    "toe_touch": 1,
    "partial_situp": 2,
    "alternate_leg_raise": 3,
    "kneeling_pushup": 4,
    "stationary_run_low": 5,
    "scissor_jump": 5,
}


def load_spec(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def validate(spec):
    """Return stable human-readable error strings. Never silently repair a spec."""
    errors = []
    if not isinstance(spec, dict):
        return ["root must be an object"]
    for key in REQUIRED:
        if key not in spec:
            errors.append(f"missing {key}")
    if errors:
        return errors
    if spec["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if not isinstance(spec["status"], str) or spec["status"] not in STATUSES:
        errors.append("status cannot assert approval; use EXPERIMENTAL/REVIEW/CANDIDATE/HOLD")
    if not isinstance(spec["id"], str) or not spec["id"].strip():
        errors.append("id must be a nonempty string")
    if not isinstance(spec["chart"], int) or isinstance(spec["chart"], bool) or not 1 <= spec["chart"] <= 6:
        errors.append("chart must be an integer from 1 to 6")
    if not isinstance(spec["exercise"], int) or isinstance(spec["exercise"], bool) or not 1 <= spec["exercise"] <= 5:
        errors.append("exercise must be an integer from 1 to 5")
    kind = spec["movement_type"]
    if not isinstance(kind, str) or not kind.strip():
        errors.append("movement_type must be a nonempty string")
    elif kind in CHART1_MOVEMENT_EXERCISE and (
            spec["chart"] != 1 or spec["exercise"] != CHART1_MOVEMENT_EXERCISE[kind]):
        errors.append(f"movement_type {kind!r} belongs to Chart 1 Exercise {CHART1_MOVEMENT_EXERCISE[kind]}, not Chart {spec['chart']} Exercise {spec['exercise']}")
    for field in ("name", "identity_reference", "movement_reference"):
        if not isinstance(spec[field], str) or not spec[field].strip():
            errors.append(f"{field} must be a nonempty string")
    for field in ("duration_seconds", "fps"):
        if isinstance(spec[field], bool) or not isinstance(spec[field], (int, float)) or not math.isfinite(spec[field]) or spec[field] <= 0:
            errors.append(f"{field} must be finite and positive")
    if not isinstance(spec["camera"], dict) or spec["camera"].get("locked") is not True:
        errors.append("camera.locked must be true for current photographic production")
    if not isinstance(spec["camera"], dict) or not isinstance(spec["camera"].get("description"), str) or not spec["camera"].get("description", "").strip():
        errors.append("camera.description must be a nonempty string for reproducible prompt generation")
    if not isinstance(spec["rules"], list) or not spec["rules"] or not all(isinstance(r, str) and r.strip() for r in spec["rules"]):
        errors.append("rules must be a nonempty list of text constraints")
    phases = spec["phases"]
    if not isinstance(phases, list) or len(phases) < 3:
        return errors + ["phases must contain at least three ordered phases"]
    identifiers = set()
    previous_time = -1.0
    for index, phase in enumerate(phases):
        p = f"phases[{index}]"
        if not isinstance(phase, dict):
            errors.append(f"{p} must be an object")
            continue
        for field in ("id", "time_seconds", "pose", "support", "contacts"):
            if field not in phase:
                errors.append(f"{p} missing {field}")
        if any(field not in phase for field in ("id", "time_seconds", "pose", "support", "contacts")):
            continue
        identifier = phase["id"]
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{p}.id must be text")
        elif identifier in identifiers:
            errors.append(f"duplicate phase id {identifier}")
        if isinstance(identifier, str):
            identifiers.add(identifier)
        t = phase["time_seconds"]
        if isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) or t <= previous_time or t > spec["duration_seconds"]:
            errors.append(f"{p}.time_seconds must be finite, increase and not exceed duration")
        else:
            previous_time = t
        if not isinstance(phase["pose"], str) or not phase["pose"].strip():
            errors.append(f"{p}.pose must describe the visible posture")
        if not isinstance(phase["support"], str) or phase["support"] not in SUPPORTS:
            errors.append(f"{p}.support must be grounded or airborne")
        if not isinstance(phase["contacts"], list) or any(not isinstance(c, str) for c in phase["contacts"]):
            errors.append(f"{p}.contacts must be a list of named support points")
        if phase["support"] == "airborne" and phase["contacts"]:
            errors.append(f"{p}: airborne phase cannot have planted contacts")
        if phase["support"] == "grounded" and not phase["contacts"]:
            errors.append(f"{p}: grounded phase must specify contacts")
    if not errors:
        if phases[0]["time_seconds"] != 0 or abs(phases[-1]["time_seconds"] - spec["duration_seconds"]) > 1e-6:
            errors.append("cycle must explicitly span 0 through duration_seconds")
        if phases[0]["support"] != phases[-1]["support"] or set(phases[0]["contacts"]) != set(phases[-1]["contacts"]):
            errors.append("first and last support/contact states differ; loop is not closed")
        if phases[0].get("pose_key") != phases[-1].get("pose_key"):
            errors.append("first and last pose_key differ; loop is not closed")
        if spec["movement_type"] == "scissor_jump":
            provenance = spec.get("track_provenance")
            if (not isinstance(provenance, dict)
                    or provenance.get("source_marker_start_state") != phases[0].get("limbs")):
                errors.append("scissor source marker start-state must match the first physical arm/leg phase; never relabel tags to fit a pose")
            errors.extend(_check_scissor(phases))
        elif spec["movement_type"] == "kneeling_pushup":
            errors.extend(_check_pushup(phases))
        else:
            errors.append(f"unknown movement_type {spec['movement_type']!r}")
    return errors


def _check_scissor(phases):
    errors = []
    # A four-panel A/flight/B/A card lacks the second flight; this is an
    # intentional gate based on the rejected/conditional November 26 pilots.
    expected = ["grounded", "airborne", "grounded", "airborne", "grounded"]
    actual = [p["support"] for p in phases]
    if actual != expected:
        errors.append("scissor jump requires exactly grounded/airborne/grounded/airborne/grounded: two exchanges, no teleport")
    tracks = {"orange_leg", "teal_leg", "orange_arm", "teal_arm"}
    for phase in phases:
        limbs = phase.get("limbs", {})
        if not isinstance(limbs, dict) or set(limbs) != tracks or any(not isinstance(v, str) or v not in {"forward", "back"} for v in limbs.values()):
            errors.append(f"phase {phase['id']}: all four tracked scissor limbs must have explicit FORWARD/BACK states (not neutral/transition)")
            continue
        if limbs["orange_leg"] == limbs["orange_arm"] or limbs["teal_leg"] == limbs["teal_arm"]:
            errors.append(f"phase {phase['id']}: each tracked arm must oppose its same-color leg")
        if limbs["orange_leg"] == limbs["teal_leg"] or limbs["orange_arm"] == limbs["teal_arm"]:
            errors.append(f"phase {phase['id']}: near/far tracks cannot share fore/aft direction")
        if phase.get("arm_form") != "straight_shoulder_high":
            errors.append(f"phase {phase['id']}: historical 5BX requires extended shoulder-high arms")
        if phase["support"] == "grounded" and set(phase["contacts"]) != {"orange_foot", "teal_foot"}:
            errors.append(f"phase {phase['id']}: grounded scissor stance needs both tracked feet")
    if len(phases) == 5 and all(isinstance(p.get("limbs"), dict) and set(p["limbs"]) == tracks for p in phases):
        lead = [phases[i]["limbs"]["orange_leg"] for i in (0, 2, 4)]
        if lead != ["back", "forward", "back"]:
            errors.append("scissor grounded leads must be orange BACK -> FORWARD -> BACK")
        if phases[0]["limbs"] != phases[-1]["limbs"]:
            errors.append("first and last scissor limb states must match")
    return errors


def _check_pushup(phases):
    errors = []
    support = {"left_palm", "right_palm", "left_knee", "right_knee"}
    for phase in phases:
        if phase["support"] != "grounded" or set(phase["contacts"]) != support:
            errors.append(f"phase {phase['id']}: kneeling push-up must keep both palms and knees planted")
        if phase.get("elbows") not in {"extended", "bending", "bent", "straightening"}:
            errors.append(f"phase {phase['id']}: specify synchronized elbow state")
        chest = phase.get("chest_position")
        required_chest = "touch_floor" if phase.get("pose_key") == "bottom" else "clear_of_floor"
        if chest != required_chest:
            errors.append(f"phase {phase['id']}: Chart 1 chest position must be {required_chest}; original booklet requires gentle chest-to-floor contact for a completed repetition")
    if phases[0].get("elbows") != "extended" or phases[-1].get("elbows") != "extended":
        errors.append("kneeling push-up must start and finish with extended elbows")
    if not any(p.get("elbows") == "bent" for p in phases[1:-1]):
        errors.append("kneeling push-up needs a visibly lowered bent-elbow phase")
    if sum(p.get("pose_key") == "bottom" for p in phases) != 1:
        errors.append("kneeling push-up must have exactly one designated chest-to-floor bottom phase")
    return errors


def validate_file(path):
    try:
        return validate(load_spec(path))
    except (json.JSONDecodeError, OSError, TypeError, ValueError, KeyError) as exc:
        return [f"could not validate {Path(path)}: {exc}"]
