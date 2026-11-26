"""Unpaid, provider-neutral *input* gate before photographic 5BX generation.

This checks the existing ``photo_motion.experiments`` request format: one
motion contract, one exact submitted-prompt file and ordered, hashed source
images. It does **not** reserve credits, contact a model, acquire a runner
lease, decide exercise form, or approve media. A paid runner must independently
use the existing provider-specific reservation mechanism and WIP lease.

    python3 -m photo_motion.generation_preflight --request private.json \
        --repo-root . --available-credits 18 --check

The request and private sources can stay outside Git; only a sanitized receipt
with hashes and errors is printed. This is a *precondition*, not permission to
spend or proof that an AI generator will follow the prompt.
"""

import argparse
import hashlib
import json
import math
import sys
import warnings
from decimal import Decimal, InvalidOperation
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from . import experiments
from .__main__ import _check_spec


SPEC_ROOT = Path("photo_motion/specs")
PHOTO_IDENTITY_POLICY = Path("sprites/docs/PHOTOREALISTIC_AVATAR_DIRECTION_2026-11-25.md")
MIN_FRAME = (640, 360)
IMAGE_TYPES = {"JPEG", "PNG", "WEBP"}


def _sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _nonnegative(value, label, errors):
    if value is None or isinstance(value, bool):
        errors.append(f"{label} must be an explicitly supplied nonnegative finite credit balance")
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        errors.append(f"{label} must be a nonnegative finite credit balance")
        return None
    if not amount.is_finite() or amount < 0:
        errors.append(f"{label} must be a nonnegative finite credit balance")
        return None
    return amount


def _under(child, parent):
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _inspect_image(path, role, expected_ratio, errors):
    """Read source bytes, decode, and enforce start-frame framing only.

    Other references can legitimately be portrait or multi-panel cards; do
    not silently crop/reformat them or pretend that a contact card is HD.
    """
    if path.is_symlink():
        errors.append(f"{role} local source cannot be a symlink")
        return None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as img:
                kind = img.format
                size = img.size
                img.verify()
        if kind not in IMAGE_TYPES or not all(isinstance(x, int) and x > 0 for x in size):
            errors.append(f"{role} must be a valid JPEG, PNG, or WebP image")
            return None
        if role == "start-frame":
            if size[0] < MIN_FRAME[0] or size[1] < MIN_FRAME[1]:
                errors.append(f"start-frame image too small: {size[0]}x{size[1]} (minimum 640x360)")
            if expected_ratio and abs(size[0] / size[1] - expected_ratio) > 0.025:
                errors.append(f"start-frame aspect ratio {size[0]}:{size[1]} differs from requested {expected_ratio:g}:1; prepare it deliberately before generation")
        return {"width": size[0], "height": size[1], "format": kind}
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        errors.append(f"{role} source image cannot be independently decoded: {exc}")
        return None


def evaluate(request, *, repo_root, available_credits=None):
    """Return a deterministic PASS/HOLD input receipt without side effects.

    PASS means reproducible *inputs* fit the declared motion plan and a caller-
    supplied availability bound, not that the credits have been reserved or
    paid use authorized. Existing ``experiments.reserve`` must still reserve
    under the provider's independently authorized immutable policy.
    """
    root = Path(repo_root).resolve()
    errors, warnings_out, assets_out = [], [], []
    receipt = {
        "schema_version": 1,
        "tool": "photo_motion.generation_preflight",
        "status": "HOLD",
        "errors": errors,
        "warnings": warnings_out,
        "motion_contract": None,
        "contract_sha256": None,
        "submitted_prompt_sha256": None,
        "input_assets": assets_out,
        "generation_authorization": "NOT_GRANTED_BY_PREFLIGHT",
        "form_and_release_approval": "NOT_EVALUATED",
    }
    if not isinstance(request, dict):
        errors.append("generation request must be an object in the existing experiments schema")
        return receipt

    # Reuse the immutable experiment request decoder instead of creating a
    # second competing schema, budget ledger or prompt/input normalization.
    normalized = None
    try:
        normalized = experiments._validate_request(request)
        receipt["submitted_prompt_sha256"] = normalized["submitted_prompt_sha256"]
    except (experiments.ExperimentError, OSError, ValueError, TypeError, KeyError) as exc:
        errors.append(f"experiment request: {exc}")

    spec_raw = request.get("spec_path")
    spec = None
    if not isinstance(spec_raw, str) or not spec_raw.strip():
        errors.append("spec_path must identify an existing versioned motion contract")
    else:
        spec_path = Path(spec_raw).expanduser()
        if spec_path.is_symlink():
            errors.append("motion contract cannot be a symlink")
        try:
            actual = spec_path.resolve(strict=True)
            allowed = (root / SPEC_ROOT).resolve(strict=True)
            if not _under(actual, allowed) or actual.suffix != ".json":
                errors.append("motion contract must be a JSON file under photo_motion/specs")
            elif not actual.is_file():
                errors.append("motion contract must be a file")
            else:
                receipt["motion_contract"] = actual.relative_to(root).as_posix()
                raw = actual.read_bytes()
                receipt["contract_sha256"] = _sha_bytes(raw)
                spec = json.loads(raw.decode("utf-8"))
                issues = _check_spec(spec)
                if issues:
                    errors.extend("invalid motion contract: " + issue for issue in issues)
                if isinstance(spec, dict):
                    if PHOTO_IDENTITY_POLICY.as_posix() not in str(spec.get("identity_reference", "")):
                        errors.append("identity_reference must name the current approved photographic avatar direction, never a legacy cartoon master")
                    if not (root / PHOTO_IDENTITY_POLICY).is_file():
                        errors.append("approved photographic identity policy reference missing in repository")
                    if spec.get("status") == "HOLD":
                        errors.append("motion contract is explicitly on HOLD")
                    expected_id = actual.stem
                    if request.get("exercise_id") != expected_id:
                        errors.append(f"exercise_id does not match versioned contract {expected_id!r}")
                    settings = request.get("settings")
                    if not isinstance(settings, dict):
                        errors.append("settings must be an object")
                    else:
                        duration = settings.get("duration_seconds")
                        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration != spec.get("duration_seconds"):
                            errors.append("settings.duration_seconds must match motion contract duration_seconds")
                        if settings.get("aspect_ratio") != "16:9":
                            errors.append("settings.aspect_ratio must be explicit 16:9 for the current photographic pilot")
                        if "fps" in settings and settings["fps"] != spec.get("fps"):
                            errors.append("settings.fps differs from motion contract fps")
                        if spec.get("audio_policy") == "forbid" and (
                                settings.get("audio") is True or settings.get("generate_audio") is True):
                            errors.append("audio_policy=forbid prohibits requesting generated audio")
                        elif spec.get("audio_policy") == "forbid" and not (
                                settings.get("audio") is False or settings.get("generate_audio") is False):
                            warnings_out.append("audio forbidden by contract, but provider-side audio disable is unverified; inspect MP4 audio streams before review")
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
            errors.append(f"motion contract cannot be verified: {exc}")

    assets = request.get("input_assets")
    if isinstance(assets, list):
        # No hidden provider-specific defaults or missing reference checks.
        ratio = 16 / 9 if isinstance(request.get("settings"), dict) and request["settings"].get("aspect_ratio") == "16:9" else None
        for index, asset in enumerate(assets):
            if not isinstance(asset, dict):
                errors.append(f"input_assets[{index}] must be an object")
                continue
            role = asset.get("role")
            entry = {"role": role, "verification": "NOT_VERIFIED"}
            assets_out.append(entry)
            local = asset.get("local_path")
            if not isinstance(local, str) or not local.strip():
                errors.append(f"input_assets[{index}] requires local hashed source bytes; remote-only declarations are insufficient before generation")
                continue
            path = Path(local).expanduser()
            if not path.is_file():
                errors.append(f"input_assets[{index}] local reference missing: {path}")
                continue
            if path.is_symlink():
                errors.append(f"input_assets[{index}] local reference cannot be a symlink")
                continue
            dimensions = _inspect_image(path, role, ratio, errors)
            if dimensions:
                entry.update(dimensions)
                entry["sha256"] = _sha_bytes(path.read_bytes())
                entry["verification"] = "rehashed_from_local_bytes"
                if normalized and index < len(normalized.get("input_assets", [])) and (
                        normalized["input_assets"][index]["sha256"] != entry["sha256"]):
                    errors.append(f"input_assets[{index}] changed during preflight; repeat before any reservation")
        if not any(asset.get("role") == "start-frame" for asset in assets if isinstance(asset, dict)):
            errors.append("at least one explicit start-frame is required for the current photographic pilot")
    else:
        errors.append("input_assets must be a list of versioned image references")

    budget = _nonnegative(available_credits, "available_credits", errors)
    estimate = None
    if normalized:
        estimate = _nonnegative(normalized.get("estimated_credits"), "estimated_credits", errors)
    if estimate is not None and budget is not None and estimate > budget:
        errors.append(f"insufficient available_credits: need {estimate}, caller supplied {budget}")
    # This caller-provided number is not evidence that a plan, account, or
    # credit reservation exists. The immutable experiments store is authoritative.

    # The versioned QA records are the only production WIP source. Existing
    # rows are incomplete for unregistered agents, so no preflight may promise
    # that a runner lease is held or an untracked agent is idle.
    try:
        from sprites.kit.photo_workflow import ACTIVE, MAX_ACTIVE, collect

        queue = collect(root)
        if queue["errors"]:
            errors.append("existing production queue has invalid handoffs or WIP: " + "; ".join(queue["errors"]))
        active = [row for row in queue["other_recorded"] if row.get("status") in ACTIVE]
        chart, exercise = (spec.get("chart"), spec.get("exercise")) if isinstance(spec, dict) else (None, None)
        same = any(row.get("chart") == chart and row.get("exercise") == exercise for row in active)
        if len(active) >= MAX_ACTIVE and not same:
            errors.append(f"production WIP limit {MAX_ACTIVE} already filled; another exercise must not start")
        if not any(row.get("chart") == chart and row.get("exercise") == exercise for row in active):
            warnings_out.append("exercise is unregistered as active production WIP; runner must claim the existing QA handoff and acquire a lease before dispatch")
        warnings_out.append("QA queue is incomplete for external/unregistered workers; this preflight cannot acquire or prove an exclusive runner lease")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"existing production queue cannot be checked: {exc}")

    # Detect files modified after request normalization. This is still a
    # preflight snapshot rather than an execution-time lock; the paid runner
    # must re-validate or reserve with the immutable experiment ledger.
    if normalized:
        if spec is not None and normalized["spec_sha256"] != receipt["contract_sha256"]:
            errors.append("motion contract changed during preflight; restart with a stable version")
        prompt_path = Path(request["submitted_prompt_file"]).expanduser()
        if prompt_path.is_symlink():
            errors.append("submitted prompt cannot be a symlink")
        else:
            try:
                if _sha_bytes(prompt_path.read_bytes()) != receipt["submitted_prompt_sha256"]:
                    errors.append("submitted prompt changed during preflight; restart with a stable version")
            except OSError as exc:
                errors.append(f"submitted prompt cannot be rechecked: {exc}")

    if not errors:
        receipt["status"] = "PASS"
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path, help="Existing private experiments request JSON")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--available-credits", help="Explicit caller-supplied availability for this provider; not authorization or a reservation")
    parser.add_argument("--check", action="store_true", help="Exit nonzero if input preflight holds")
    args = parser.parse_args(argv)
    try:
        request = json.loads(args.request.read_text(encoding="utf-8"))
        result = evaluate(request, repo_root=args.repo_root, available_credits=args.available_credits)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {"status": "HOLD", "errors": [f"request unavailable/invalid: {exc}"],
                  "generation_authorization": "NOT_GRANTED_BY_PREFLIGHT"}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if args.check and result["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
