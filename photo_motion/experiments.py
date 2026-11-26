"""Immutable, private photographic-generation intents and artifact/credit receipts.

The store must live outside the Git checkout. It records *actual submitted*
prompts and source digests, does not call a generator, and never approves form.

Standalone CLI: python3 -m photo_motion.experiments --help
"""

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


SCHEMA_VERSION = 1
HOLD = "HOLD_FOR_HUMAN_FORM_AND_RELEASE_REVIEW"
DIGEST = re.compile(r"^[0-9a-f]{64}$")
REPO_ROOT = Path(__file__).resolve().parents[1]


class ExperimentError(ValueError):
    """Bad or conflicting provenance, policy, or immutable ledger entry."""


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _hash_file(path):
    sha = hashlib.sha256()
    count = 0
    with open(path, "rb") as handle:
        for piece in iter(lambda: handle.read(1 << 20), b""):
            sha.update(piece)
            count += len(piece)
    return sha.hexdigest(), count


def _sha_file(path):
    return _hash_file(path)[0]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _require_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ExperimentError(f"{name} must be nonempty text")
    return value


def _credit(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, str, Decimal)):
        raise ExperimentError(f"{name} must be nonnegative decimal text/integer")
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ExperimentError(f"{name} is not a valid number") from exc
    if not amount.is_finite() or amount < 0:
        raise ExperimentError(f"{name} must be finite and nonnegative")
    return format(amount.normalize(), "f")


def _require_digest(value, name):
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise ExperimentError(f"{name} must be a lowercase 64-hex SHA-256")
    return value


def _resolve_store(folder):
    path = Path(folder).expanduser().resolve()
    if path == REPO_ROOT or REPO_ROOT in path.parents or any(
        (ancestor / ".git").exists() for ancestor in (path, *path.parents)
    ):
        raise ExperimentError("private experiment store must be outside the Git repository")
    return path


def _read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperimentError(f"missing or invalid immutable record {path}: {exc}") from exc


def _create_only(path, record):
    """Durable atomic exclusive create: crash cannot leave half-written JSON.

    Hard-linking a completely fsynced temporary file refuses to overwrite an
    existing record. A stale temp is safe, though later housekeeping may remove
    it only after confirming it is unrelated to an active writer.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = _canonical(record) + b"\n"
    handle, temp_name = tempfile.mkstemp(dir=path.parent, prefix=".pending-", suffix=".json")
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temp_name, path)
        except FileExistsError as exc:
            raise ExperimentError(f"immutable record already exists: {path}") from exc
        os.chmod(path, 0o400)
        # fsync the directory so an acknowledged reservation survives a crash.
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        os.unlink(temp_name)


@contextlib.contextmanager
def _locked_store(folder):
    store = _resolve_store(folder)
    store.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = store / ".experiment-write.lock"
    if lock_path.is_symlink():
        raise ExperimentError("lock file cannot be a symlink")
    with open(lock_path, "a+b") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            yield store
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def initialize(folder, *, provider, credit_limit):
    """Create one immutable provider-specific cap. Never silently raise it."""
    provider = _require_text(provider, "provider")
    limit = _credit(credit_limit, "credit_limit")
    with _locked_store(folder) as store:
        path = store / "policy.json"
        if path.exists():
            policy = _policy(store)
            if policy.get("provider") != provider or policy.get("credit_limit") != limit:
                raise ExperimentError("existing immutable budget policy differs; explicit authorization is required to change it")
            return policy
        policy = {"schema_version": SCHEMA_VERSION, "provider": provider,
                  "credit_limit": limit, "created_at_utc": _now(),
                  "meaning": "Per-provider total actual charges plus pending reservations, not transferable between providers"}
        _create_only(path, policy)
        return policy


def _policy(store):
    policy = _read(store / "policy.json")
    if policy.get("schema_version") != SCHEMA_VERSION:
        raise ExperimentError("unknown ledger schema version")
    _require_text(policy.get("provider"), "policy.provider")
    _credit(policy.get("credit_limit"), "policy.credit_limit")
    return policy


def _validate_request(request):
    if not isinstance(request, dict) or request.get("schema_version") != SCHEMA_VERSION:
        raise ExperimentError("request must have schema_version 1")
    allowed = {"schema_version", "attempt_key", "exercise_id", "spec_path", "submitted_prompt_file",
               "input_assets", "provider", "model", "settings", "estimated_credits", "source_preflight"}
    unknown = set(request) - allowed
    if unknown:
        raise ExperimentError(f"unknown request fields: {sorted(unknown)}")
    for key in ("attempt_key", "exercise_id", "provider", "model"):
        _require_text(request.get(key), key)
    if not isinstance(request.get("settings"), dict) or not request["settings"]:
        raise ExperimentError("settings must be a nonempty JSON object; use null for unknown parameters")
    try:
        _canonical(request["settings"])
    except (TypeError, ValueError) as exc:
        raise ExperimentError(f"settings are not serializable JSON: {exc}") from exc
    estimate = _credit(request.get("estimated_credits"), "estimated_credits")
    spec = Path(_require_text(request.get("spec_path"), "spec_path")).expanduser().resolve()
    prompt = Path(_require_text(request.get("submitted_prompt_file"), "submitted_prompt_file")).expanduser().resolve()
    if not spec.is_file() or not prompt.is_file():
        raise ExperimentError("actual spec and verbatim submitted prompt files must exist locally")
    # The operator supplies the verbatim prompt claimed to have been submitted.
    # Store the exact bytes, including CRLF, not Python's newline-normalized text.
    try:
        prompt_bytes = prompt.read_bytes()
        content = prompt_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ExperimentError("exact submitted prompt must be UTF-8 text") from exc
    if not content.strip():
        raise ExperimentError("exact submitted prompt is empty")
    assets = request.get("input_assets")
    if not isinstance(assets, list) or not assets:
        raise ExperimentError("at least one hashed source/reference image is required")
    clean_assets = []
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict) or set(asset) - {"role", "locator", "sha256", "local_path"}:
            raise ExperimentError(f"input_assets[{index}] has unknown fields")
        role = _require_text(asset.get("role"), f"input_assets[{index}].role")
        locator = _require_text(asset.get("locator"), f"input_assets[{index}].locator")
        expected = asset.get("sha256")
        if expected is not None:
            expected = _require_digest(expected, f"input_assets[{index}].sha256")
        local = asset.get("local_path")
        actual = None
        if local is not None:
            filepath = Path(_require_text(local, f"input_assets[{index}].local_path")).expanduser().resolve()
            if not filepath.is_file():
                raise ExperimentError(f"source image unavailable: {filepath}")
            actual = _sha_file(filepath)
            if expected is not None and expected != actual:
                raise ExperimentError(f"input_assets[{index}] source SHA mismatch")
        if not (expected or actual):
            raise ExperimentError(f"input_assets[{index}] needs actual local bytes or a known SHA-256; URL alone is insufficient")
        clean_assets.append({"role": role, "locator": locator, "sha256": actual or expected,
                             "verification": "rehashed_from_local_bytes" if actual else "declared_unverified"})
    source_preflight = None
    if request["exercise_id"] == "chart1-scissor-jump":
        # For the currently authorized V6 diagnostic, an unbound JSON spec or
        # unverified remote image is not adequate to spend provider credits.
        # This is a content check, not authorization or an exercise approval.
        if Decimal(estimate) <= 0:
            raise ExperimentError("V6 paid Flow attempt requires a positive provider-quoted credit estimate")
        entry = request.get("source_preflight")
        expected_fields = {"original_card", "prepared_png", "manifest"}
        if not isinstance(entry, dict) or set(entry) not in (expected_fields, expected_fields | {"opposite_pose_reference"}):
            raise ExperimentError("V6 scissor attempt requires source_preflight with original_card, prepared_png, manifest, and only optional opposite_pose_reference")
        has_opposite = "opposite_pose_reference" in entry
        opposite_entry = entry.get("opposite_pose_reference")
        if has_opposite and (not isinstance(opposite_entry, dict) or
                             set(opposite_entry) != {"prepared_png", "manifest"}):
            raise ExperimentError("V6 opposite_pose_reference must contain exactly prepared_png and manifest paths")
        from .preflight_v6 import verify, verify_pair, PreflightError
        try:
            if not has_opposite:
                source_preflight = verify(spec, entry["original_card"], entry["prepared_png"], entry["manifest"])
            else:
                source_preflight = verify_pair(spec, entry["original_card"], entry["prepared_png"],
                                               entry["manifest"], opposite_entry["prepared_png"],
                                               opposite_entry["manifest"])
        except (PreflightError, OSError, ValueError, TypeError) as exc:
            raise ExperimentError(f"V6 scissor preflight failed: {exc}") from exc
        expected_assets = [("start-frame", source_preflight["prepared_png_sha256"])]
        if has_opposite:
            expected_assets.append(("opposite-pose-reference", source_preflight["opposite_pose_reference"]["prepared_png_sha256"]))
        if len(clean_assets) != len(expected_assets) or any(
            asset["role"] != role or asset["verification"] != "rehashed_from_local_bytes" or asset["sha256"] != digest
            for asset, (role, digest) in zip(clean_assets, expected_assets)
        ):
            raise ExperimentError("V6 scissor pilot requires a prepared start-frame: ordered verified start-frame A and only optional opposite-pose-reference C matching their panel preflights")
        try:
            requested_spec = json.loads(spec.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ExperimentError(f"invalid V6 specification: {exc}") from exc
        if (request["settings"].get("duration_seconds") != requested_spec["duration_seconds"] or
                request["settings"].get("aspect_ratio") != "16:9"):
            raise ExperimentError("V6 Flow duration/aspect settings must match the six-second 16:9 photographic contract")
    elif "source_preflight" in request:
        raise ExperimentError("V6 source_preflight is only supported for the versioned Chart 1 scissor pilot")
    spec_sha = _sha_file(spec)
    if source_preflight and spec_sha != source_preflight["spec_sha256"]:
        raise ExperimentError("V6 spec changed between preflight and reservation; discard this attempt")
    # Input order is semantically meaningful: many generators treat image 1 as
    # identity and image 2 as pose authority.
    return {"schema_version": SCHEMA_VERSION, "attempt_key": request["attempt_key"],
            "exercise_id": request["exercise_id"], "spec_sha256": spec_sha,
            "spec_reference": spec.name, "submitted_prompt": content, "submitted_prompt_sha256": _digest_bytes(prompt_bytes),
            "input_assets": clean_assets, "provider": request["provider"], "model": request["model"],
            "settings": request["settings"], "estimated_credits": estimate,
            "source_preflight": source_preflight}


def _check_intent_record(intent, run_id):
    request = intent.get("request")
    if (intent.get("schema_version") != SCHEMA_VERSION or not isinstance(request, dict)
            or intent.get("run_id") != run_id or intent.get("request_fingerprint") != run_id
            or intent.get("estimated_credits") != request.get("estimated_credits")
            or _digest_bytes(_canonical(request)) != run_id):
        raise ExperimentError(f"broken immutable intent fingerprint or metadata: {run_id}")
    if intent.get("release_status") != HOLD:
        raise ExperimentError(f"unknown or forged release status: {run_id}")
    return intent


def _snapshot(store):
    policy = _policy(store)
    committed = Decimal(0)
    reserved = Decimal(0)
    planned = list((store / "intents").glob("*.json")) if (store / "intents").exists() else []
    for path in planned:
        intent = _read(path)
        _check_intent_record(intent, path.stem)
        outcome_path = store / "charges" / f"{path.stem}.json"
        if outcome_path.exists():
            receipt = _read(outcome_path)
            if receipt.get("run_id") != path.stem:
                raise ExperimentError(f"charge receipt mismatches intent {path.stem}")
            if receipt.get("release_status") != HOLD or receipt.get("schema_version") != SCHEMA_VERSION:
                raise ExperimentError(f"invalid immutable charge receipt {path.stem}")
            committed += Decimal(_credit(receipt.get("actual_credits"), "actual_credits"))
        else:
            reserved += Decimal(_credit(intent.get("estimated_credits"), "estimated_credits"))
    limit = Decimal(_credit(policy["credit_limit"], "credit_limit"))
    orphans = {path.stem for path in (store / "charges").glob("*.json")} - {path.stem for path in planned} if (store / "charges").exists() else set()
    if orphans:
        raise ExperimentError(f"charge receipt without a known intent: {sorted(orphans)}")
    return {"provider": policy["provider"], "credit_limit": format(limit, "f"),
            "actual_credits": format(committed, "f"), "pending_reserved_credits": format(reserved, "f"),
            "available_credits": format(limit - committed - reserved, "f"),
            "attempts": len(planned), "unsettled_attempts": sum(not (store / "charges" / f"{p.stem}.json").exists() for p in planned)}


def snapshot(folder):
    """Report the immutable ceiling, actual spend and unresolved reservations."""
    with _locked_store(folder) as store:
        return _snapshot(store)


def reserve(folder, request):
    """Idempotently reserve one ATTEMPT's cost; new retries need new attempt_key."""
    data = _validate_request(request)
    fingerprint = _digest_bytes(_canonical(data))
    run_id = fingerprint  # full SHA-256, no short-ID collision ambiguity
    with _locked_store(folder) as store:
        policy = _policy(store)
        if policy["provider"] != data["provider"]:
            raise ExperimentError("provider differs from budget policy; credits are not fungible")
        target = store / "intents" / f"{run_id}.json"
        if target.exists():
            original = _check_intent_record(_read(target), run_id)
            if original.get("request") != data:
                raise ExperimentError("existing run manifest no longer matches its immutable request")
            return original
        for prior_path in (store / "intents").glob("*.json"):
            prior = _read(prior_path)
            if prior.get("request", {}).get("attempt_key") == data["attempt_key"]:
                raise ExperimentError("attempt_key already has an immutable manifest with different inputs; choose a new attempt_key for a real retry")
        current = _snapshot(store)
        # The actual provider charge can exceed the estimate and push remaining
        # credits negative. Preserve that truthful state, then block new runs.
        proposed = Decimal(current["available_credits"])
        estimated = Decimal(data["estimated_credits"])
        if estimated > proposed:
            raise ExperimentError(f"insufficient authorized {policy['provider']} credits: available {proposed}, requested {estimated}")
        manifest = {"schema_version": SCHEMA_VERSION, "run_id": run_id,
                    "request_fingerprint": fingerprint, "created_at_utc": _now(),
                    "release_status": HOLD, "request": data, "estimated_credits": data["estimated_credits"]}
        _create_only(target, manifest)
        return manifest


def _known_run(store, run_id):
    run_id = _require_digest(run_id, "run_id")
    intent = _read(store / "intents" / f"{run_id}.json")
    return _check_intent_record(intent, run_id)


def settle(folder, run_id, *, actual_credits, provider_generation_id, outcome):
    """One immutable actual-charge receipt; no rewriting an earlier estimate.

    An unreported charge remains an open reservation instead of pretending
    that an incomplete or failed generation was free.
    """
    actual = _credit(actual_credits, "actual_credits")
    provider_generation_id = _require_text(provider_generation_id, "provider_generation_id")
    if outcome not in ("COMPLETED", "FAILED"):
        raise ExperimentError("outcome must be COMPLETED or FAILED")
    with _locked_store(folder) as store:
        _known_run(store, run_id)
        target = store / "charges" / f"{run_id}.json"
        payload = {"schema_version": SCHEMA_VERSION, "run_id": run_id, "actual_credits": actual,
                   "provider_generation_id": provider_generation_id, "outcome": outcome, "release_status": HOLD}
        if target.exists():
            current = _read(target)
            for key in payload:
                if current.get(key) != payload[key]:
                    raise ExperimentError("immutable charge receipt already exists with different result")
            return current
        receipt = {**payload, "recorded_at_utc": _now()}
        _create_only(target, receipt)
        return receipt


def record_artifact(folder, run_id, *, artifact_path, role, locator):
    """Receipt for an existing output artifact, without copying media into Git."""
    role = _require_text(role, "role")
    locator = _require_text(locator, "locator")
    source = Path(artifact_path).expanduser().resolve()
    if not source.is_file():
        raise ExperimentError("artifact must exist locally for independent hash verification")
    with _locked_store(folder) as store:
        _known_run(store, run_id)
        source_hash, source_size = _hash_file(source)
        proof = {"schema_version": SCHEMA_VERSION, "run_id": run_id, "role": role,
                 "locator": locator, "sha256": source_hash, "size_bytes": source_size,
                 "verification": "rehashed_from_local_bytes", "release_status": HOLD}
        artifact_id = _digest_bytes(_canonical(proof))
        target = store / "artifacts" / run_id / f"{artifact_id}.json"
        if target.exists():
            current = _read(target)
            if current.get("proof") != proof:
                raise ExperimentError("immutable artifact receipt already exists with mismatched proof")
            return current
        receipt = {"artifact_id": artifact_id, "created_at_utc": _now(), "proof": proof}
        _create_only(target, receipt)
        return receipt


def _main(argv=None):
    parser = argparse.ArgumentParser(description="Immutable photographic experiment provenance and authorized credits")
    actions = parser.add_subparsers(dest="command", required=True)
    init = actions.add_parser("init", help="Set an immutable provider-specific budget ceiling")
    init.add_argument("--store", required=True)
    init.add_argument("--provider", required=True)
    init.add_argument("--credit-limit", required=True)
    plan = actions.add_parser("reserve", help="Record exact submitted prompt/sources and reserve estimated credits")
    plan.add_argument("--store", required=True)
    plan.add_argument("--request", required=True, help="Private request JSON, see EXPERIMENTS.md")
    state = actions.add_parser("status", help="Read current credit ceiling, spent, and pending reservations")
    state.add_argument("--store", required=True)
    charged = actions.add_parser("settle", help="Record provider's actual charge once known")
    charged.add_argument("--store", required=True)
    charged.add_argument("--run-id", required=True)
    charged.add_argument("--actual-credits", required=True)
    charged.add_argument("--provider-generation-id", required=True)
    charged.add_argument("--outcome", choices=("COMPLETED", "FAILED"), required=True)
    output = actions.add_parser("artifact", help="Hash existing generated media; never copy source files")
    output.add_argument("--store", required=True)
    output.add_argument("--run-id", required=True)
    output.add_argument("--artifact", required=True)
    output.add_argument("--role", required=True)
    output.add_argument("--locator", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = initialize(args.store, provider=args.provider, credit_limit=args.credit_limit)
        elif args.command == "reserve":
            result = reserve(args.store, _read(Path(args.request)))
        elif args.command == "status":
            result = snapshot(args.store)
        elif args.command == "settle":
            result = settle(args.store, args.run_id, actual_credits=args.actual_credits,
                            provider_generation_id=args.provider_generation_id, outcome=args.outcome)
        else:
            result = record_artifact(args.store, args.run_id, artifact_path=args.artifact,
                                     role=args.role, locator=args.locator)
    except (ExperimentError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
