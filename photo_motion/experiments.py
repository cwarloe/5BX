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


def _create_only_bytes(path, encoded):
    """Durable atomic exclusive create for immutable private bytes.

    Hard-linking a completely fsynced temporary file refuses to overwrite an
    existing record. A stale temp is safe, though later housekeeping may remove
    it only after confirming it is unrelated to an active writer.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink() or path.is_symlink():
        raise ExperimentError(f"immutable record path must not be a symlink: {path}")
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


def _create_only(path, record):
    """Create an immutable JSON record without partial writes or overwrites."""
    _create_only_bytes(path, _canonical(record) + b"\n")


def _opening_snapshot_path(store, digest):
    # The immutable policy already pins the digest. This path is derived, not
    # a second user-editable authority, and can be backed up with the ledger.
    return store / "opening-evidence" / f"{digest}.bin"


def _archive_opening_evidence(store, evidence_file, digest):
    """Create/reuse a byte-exact append-only evidence snapshot inside ledger."""
    source = Path(evidence_file).expanduser()
    try:
        if source.is_symlink() or not source.is_file():
            raise ExperimentError(f"opening debit source evidence unavailable or symlink: {source}")
        payload = source.read_bytes()
    except OSError as exc:
        raise ExperimentError(f"opening debit source evidence unavailable: {source}: {exc}") from exc
    if _digest_bytes(payload) != digest:
        raise ExperimentError("opening debit evidence SHA-256 differs from immutable policy; archive refused")
    target = _opening_snapshot_path(store, digest)
    if target.exists() or target.is_symlink():
        if target.is_symlink() or not target.is_file() or _sha_file(target) != digest:
            raise ExperimentError("opening debit private evidence snapshot is missing or altered; restore it from trusted backup")
    else:
        _create_only_bytes(target, payload)
    return target


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


def initialize(folder, *, provider, credit_limit, opening_spent_credits=None,
               opening_evidence_path=None, opening_run_ids=None):
    """Create one immutable provider-specific cap with explicit continuity.

    A missing ledger is *not* evidence of zero provider charges. Every fresh
    store requires an explicit opening amount. A positive amount represents an
    operator-reconciled debit from prior observed spending, not a forged run
    receipt; it is linked to an existing, rehashed evidence document and prior
    run fingerprints so those attempts cannot be reserved twice.
    """
    provider = _require_text(provider, "provider")
    limit = _credit(credit_limit, "credit_limit")
    with _locked_store(folder) as store:
        path = store / "policy.json"
        if path.exists():
            policy = _policy(store)
            if policy.get("provider") != provider or policy.get("credit_limit") != limit:
                raise ExperimentError("existing immutable budget policy differs; explicit authorization is required to change it")
            if (opening_spent_credits is not None and
                    _credit(opening_spent_credits, "opening_spent_credits") != policy["opening_spent_credits"]):
                raise ExperimentError("opening spend differs from the immutable budget policy")
            return policy
        if opening_spent_credits is None:
            raise ExperimentError("new ledger requires explicit opening_spent_credits; missing records do not prove zero prior charges")
        opening = _credit(opening_spent_credits, "opening_spent_credits")
        prior_ids = opening_run_ids if opening_run_ids is not None else []
        if not isinstance(prior_ids, list):
            raise ExperimentError("opening_run_ids must be a list")
        for run_id in prior_ids:
            _require_digest(run_id, "opening_run_ids entry")
        if len(set(prior_ids)) != len(prior_ids):
            raise ExperimentError("opening_run_ids must not contain duplicates")
        provenance = None
        if Decimal(opening) > 0:
            if not opening_evidence_path or not prior_ids:
                raise ExperimentError("positive opening spend requires evidence file and prior run IDs")
            evidence = Path(opening_evidence_path).expanduser().resolve()
            if not evidence.is_file():
                raise ExperimentError(f"opening spend evidence unavailable: {evidence}")
            # Capture the evidence itself *inside the private ledger* before
            # publishing policy.json. The external scratch checkout may vanish.
            evidence_sha = _sha_file(evidence)
            _archive_opening_evidence(store, evidence, evidence_sha)
            provenance = {
                "classification": "operator_reconciled_prior_spend_not_native_receipts",
                "evidence_reference": str(evidence),
                "evidence_sha256": evidence_sha,
                "prior_run_ids": sorted(prior_ids),
            }
        elif opening_evidence_path is not None or prior_ids:
            raise ExperimentError("zero opening spend must not claim prior debit evidence or run IDs")
        policy = {"schema_version": SCHEMA_VERSION, "provider": provider,
                  "credit_limit": limit, "created_at_utc": _now(),
                  "opening_spent_credits": opening, "opening_provenance": provenance,
                  "meaning": "Per-provider prior reconciled debit plus native actual charges plus pending reservations; not transferable between providers"}
        _create_only(path, policy)
        return _policy(store)


def _policy(store, *, verify_evidence=True):
    policy = _read(store / "policy.json")
    if policy.get("schema_version") != SCHEMA_VERSION:
        raise ExperimentError("unknown ledger schema version")
    _require_text(policy.get("provider"), "policy.provider")
    _credit(policy.get("credit_limit"), "policy.credit_limit")
    # Existing stores predate the continuity fields; their native intents and
    # charge receipts remain authoritative and are never reclassified.
    opening = _credit(policy.get("opening_spent_credits", "0"), "policy.opening_spent_credits")
    provenance = policy.get("opening_provenance")
    if Decimal(opening) > 0:
        if not isinstance(provenance, dict) or set(provenance) != {
                "classification", "evidence_reference", "evidence_sha256", "prior_run_ids"}:
            raise ExperimentError("positive opening debit has no valid immutable provenance")
        if provenance["classification"] != "operator_reconciled_prior_spend_not_native_receipts":
            raise ExperimentError("unknown opening debit classification")
        _require_text(provenance["evidence_reference"], "opening_provenance.evidence_reference")
        _require_digest(provenance["evidence_sha256"], "opening_provenance.evidence_sha256")
        run_ids = provenance["prior_run_ids"]
        if not isinstance(run_ids, list) or not run_ids or run_ids != sorted(set(run_ids)):
            raise ExperimentError("opening debit requires distinct sorted prior run IDs")
        for run_id in run_ids:
            _require_digest(run_id, "opening_provenance.prior_run_id")
        evidence_status = "NOT_CHECKED_FOR_ARCHIVAL_OPERATION"
        if verify_evidence:
            evidence = Path(provenance["evidence_reference"])
            private = _opening_snapshot_path(store, provenance["evidence_sha256"])
            has_snapshot = private.exists() or private.is_symlink()
            if has_snapshot:
                if private.is_symlink() or not private.is_file():
                    raise ExperimentError("opening debit private evidence snapshot is not a regular file")
                try:
                    private_hash = _sha_file(private)
                except OSError as exc:
                    raise ExperimentError(f"opening debit private evidence snapshot unavailable: {exc}") from exc
                if private_hash != provenance["evidence_sha256"]:
                    raise ExperimentError("opening debit private evidence snapshot SHA-256 differs from immutable policy")
            if evidence.is_symlink():
                raise ExperimentError("opening debit original evidence reference was replaced with a symlink")
            if evidence.exists() and not evidence.is_file():
                raise ExperimentError("opening debit original evidence reference is no longer a regular file")
            if evidence.is_file():
                try:
                    external_hash = _sha_file(evidence)
                except OSError as exc:
                    raise ExperimentError(f"opening debit original evidence unreadable: {exc}") from exc
                if external_hash != provenance["evidence_sha256"]:
                    raise ExperimentError("opening debit evidence SHA-256 differs from immutable policy; stop new reservations")
                evidence_status = "VERIFIED_PRIVATE_SNAPSHOT_AND_EXTERNAL" if has_snapshot else "LEGACY_EXTERNAL_ONLY_ARCHIVE_REQUIRED"
            elif has_snapshot:
                # A pruned external scratch worktree is expected. Do not
                # erase its historical reference or treat it as tampered
                # *bytes*: a verified independent private snapshot is enough.
                evidence_status = "EXTERNAL_MISSING_USING_VERIFIED_PRIVATE_SNAPSHOT"
            else:
                raise ExperimentError(f"opening debit evidence unavailable: {evidence}; run archive-evidence with a byte-exact copy before spending")
    elif provenance is not None:
        raise ExperimentError("zero opening debit cannot claim prior charge provenance")
    else:
        evidence_status = "NOT_APPLICABLE"
    policy = {**policy, "opening_spent_credits": opening, "opening_provenance": provenance,
              "opening_evidence_status": evidence_status}
    return policy


def archive_evidence(folder, *, evidence_path):
    """Upgrade an old positive-opening ledger without rewriting its policy.

    Works even when the old absolute evidence path has disappeared. The
    supplied replacement bytes must match the *existing* immutable digest;
    there is no way to change a debit, cap or prior run ID via this command.
    """
    with _locked_store(folder) as store:
        policy = _policy(store, verify_evidence=False)
        provenance = policy["opening_provenance"]
        if provenance is None:
            raise ExperimentError("opening evidence archive applies only to a positive reconciled debit")
        target = _archive_opening_evidence(store, evidence_path, provenance["evidence_sha256"])
        return {"result": "VERIFIED_IMMUTABLE_PRIVATE_EVIDENCE_SNAPSHOT",
                "opening_spent_credits": policy["opening_spent_credits"],
                "original_evidence_reference": provenance["evidence_reference"],
                "evidence_snapshot_reference": str(target),
                "evidence_sha256": provenance["evidence_sha256"],
                "prior_run_ids": provenance["prior_run_ids"]}


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
    entry = request.get("source_preflight")
    if isinstance(entry, dict) and entry.get("authority") == "V10_REPLAYED_SHARED_CANVAS_FRAMES":
        # This is NOT a V7/V8 direct-source exception. Both sent endpoints
        # must be exactly replayed derivative PNGs, independently QA-attested,
        # and linked to pinned original A/C + generated canvas provenance.
        from .preflight_v10_shared_canvas import (
            verify_segment as verify_v10_segment, SharedCanvasPreflightError,
            V10_SETTINGS,
        )
        required = {"authority", "original_a_png", "original_c_png", "canvas_jpeg",
                    "a_annotation", "c_annotation", "canvas_annotation",
                    "shared_manifest", "derived_a_png", "derived_c_png",
                    "independent_qa_report", "segment_role"}
        if request["exercise_id"] != "chart1-scissor-jump" or set(entry) != required:
            raise ExperimentError("V10 requires the exact replayable A/C/canvas source and independent QA paths")
        try:
            source_preflight = verify_v10_segment(
                spec, entry["original_a_png"], entry["original_c_png"],
                entry["canvas_jpeg"], entry["shared_manifest"],
                entry["derived_a_png"], entry["derived_c_png"],
                a_annotation=entry["a_annotation"], c_annotation=entry["c_annotation"],
                canvas_annotation=entry["canvas_annotation"],
                independent_qa_report=entry["independent_qa_report"],
                expected_role=entry["segment_role"])
        except (SharedCanvasPreflightError, OSError, ValueError, TypeError) as exc:
            raise ExperimentError(f"V10 shared-canvas source preflight failed: {exc}") from exc
        expected_assets = [("start-frame", source_preflight["start_sha256"]),
                           ("end-frame", source_preflight["end_sha256"])]
        if len(clean_assets) != 2 or any(
                asset["role"] != role or asset["verification"] != "rehashed_from_local_bytes"
                or asset["sha256"] != digest
                for asset, (role, digest) in zip(clean_assets, expected_assets)):
            raise ExperimentError("V10 requires exactly two ordered locally rehashed A*/C* derived endpoints")
        if (request["provider"] != "Google Flow" or request["model"] != "Omni 1.2 Flash"
                or request["settings"] != V10_SETTINGS or Decimal(estimate) != Decimal("9")):
            raise ExperimentError("V10 differs from the observed Omni 1.2 Flash Frames/720p/3s/x1 nine-credit quote")
    elif isinstance(entry, dict) and entry.get("authority") == "V9_DIRECT_A_OR_C_OUTPAINT_IMAGE_EDIT":
        # A new, zero-credit still-image experiment. Its *input* is a directly
        # authenticated V7 A or C PNG. A generated outpaint is never promoted
        # into a V7/V8 motion input or an accepted identity master here.
        from .preflight_v9_outpaint import verify_source, OutpaintPreflightError, IMAGE_EDIT_SETTINGS
        if request["exercise_id"] != "chart1-scissor-jump" or set(entry) != {
                "authority", "source_png", "source_pose"}:
            raise ExperimentError("V9 outpaint requires Chart 1 scissor and exact source_png/source_pose fields")
        try:
            source_preflight = verify_source(spec, entry["source_png"], source_pose=entry["source_pose"])
        except (OutpaintPreflightError, OSError, ValueError, TypeError) as exc:
            raise ExperimentError(f"V9 source outpaint preflight failed: {exc}") from exc
        if (len(clean_assets) != 1 or clean_assets[0]["role"] != "source-photo"
                or clean_assets[0]["verification"] != "rehashed_from_local_bytes"
                or clean_assets[0]["sha256"] != source_preflight["source_png_sha256"]):
            raise ExperimentError("V9 requires exactly one locally rehashed original A or C source-photo PNG")
        if (request["provider"] != "Google Flow" or request["model"] != "Nano Banana 2.1"
                or request["settings"] != IMAGE_EDIT_SETTINGS or Decimal(estimate) != 0):
            raise ExperimentError("V9 requires the exact observed Nano Banana 2.1 image-edit settings, one requested output and live zero-credit quote")
    elif request["exercise_id"] == "chart1-scissor-jump":
        # For V6/V7 diagnostics, an unbound JSON spec or
        # unverified remote image is not adequate to spend provider credits.
        # This is a content check, not authorization or an exercise approval.
        if Decimal(estimate) <= 0:
            raise ExperimentError("V6/V7 paid Flow attempt requires a positive provider-quoted credit estimate")
        entry = request.get("source_preflight")
        if isinstance(entry, dict) and entry.get("authority") == "V8_FRAMES_DIRECT_A_C_SEGMENTS":
            from .preflight_v8_segments import verify_segment, SegmentPreflightError
            if set(entry) != {"authority", "a_png", "c_png", "segment_role"}:
                raise ExperimentError("V8 segment preflight requires exact A/C paths and segment_role")
            try:
                source_preflight = verify_segment(
                    spec, entry["a_png"], entry["c_png"], expected_role=entry["segment_role"])
            except (SegmentPreflightError, OSError, ValueError, TypeError) as exc:
                raise ExperimentError(f"V8 Frames endpoint preflight failed: {exc}") from exc
            expected_assets = [("start-frame", source_preflight["start_sha256"]),
                               ("end-frame", source_preflight["end_sha256"])]
            authority_name = "V8 Frames endpoints"
        elif isinstance(entry, dict) and entry.get("authority") == "V7_DIRECT_PREPARED_PAIR":
            # New versioned authority, NOT an exception to or relaxation of
            # V6's immutable original-card byte-replay rules.
            from .preflight_v7 import verify_pair as verify_v7_pair, PreflightError as V7Error
            permitted = {"authority", "prepared_png", "opposite_pose_reference"}
            if set(entry) not in (permitted, permitted | {"historical_manifests"}):
                raise ExperimentError("V7 source_preflight requires exactly authority, prepared_png, opposite_pose_reference, and optional historical_manifests")
            opposite_entry = entry.get("opposite_pose_reference")
            if not isinstance(opposite_entry, dict) or set(opposite_entry) != {"prepared_png"}:
                raise ExperimentError("V7 opposite_pose_reference requires exactly prepared_png")
            historical = entry.get("historical_manifests")
            if historical is not None and (not isinstance(historical, dict) or
                                           set(historical) != {"start", "opposite"}):
                raise ExperimentError("V7 historical_manifests must contain exactly start and opposite paths")
            try:
                source_preflight = verify_v7_pair(
                    spec, entry["prepared_png"], opposite_entry["prepared_png"],
                    historical["start"] if historical else None,
                    historical["opposite"] if historical else None)
            except (V7Error, OSError, ValueError, TypeError) as exc:
                raise ExperimentError(f"V7 prepared-pair preflight failed: {exc}") from exc
            expected_assets = [
                ("start-frame", source_preflight["prepared_png_sha256"]),
                ("opposite-pose-reference", source_preflight["opposite_pose_reference"]["prepared_png_sha256"]),
            ]
            authority_name = "V7 prepared-pair"
        else:
            # Existing V6 replay paths remain unchanged, including old A-only
            # run receipts and optional verified two-image A+C requests.
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
            authority_name = "V6 scissor"
        if len(clean_assets) != len(expected_assets) or any(
            asset["role"] != role or asset["verification"] != "rehashed_from_local_bytes" or asset["sha256"] != digest
            for asset, (role, digest) in zip(clean_assets, expected_assets)
        ):
            if authority_name == "V6 scissor":
                raise ExperimentError("V6 scissor pilot requires a prepared start-frame: ordered verified start-frame A and only optional opposite-pose-reference C matching their panel preflights")
            if authority_name == "V7 prepared-pair":
                raise ExperimentError("V7 prepared-pair pilot requires exactly ordered verified start-frame A and opposite-pose-reference C matching their preflights")
            raise ExperimentError(f"{authority_name} requires exactly ordered locally verified photographic endpoint images")
        try:
            requested_spec = json.loads(spec.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ExperimentError(f"invalid V6 specification: {exc}") from exc
        if (request["settings"].get("duration_seconds") != requested_spec["duration_seconds"] or
                request["settings"].get("aspect_ratio") != "16:9"):
            if authority_name != "V8 Frames endpoints":
                raise ExperimentError("V6/V7 Flow duration/aspect settings must match the six-second 16:9 photographic contract")
            raise ExperimentError("Flow duration/aspect settings must match the versioned 16:9 photographic contract")
        if requested_spec.get("status") == "HOLD":
            raise ExperimentError("V6/V7 motion contract is explicitly on HOLD; do not reserve provider credits")
        if authority_name == "V7 prepared-pair":
            # The V7 quote and controlled comparison are for ONE generation.
            # Unknown provider settings may hide batch/output multipliers;
            # version a different experiment instead of silently adding them.
            allowed_v7_settings = {"duration_seconds", "aspect_ratio", "variants", "seed"}
            unknown_settings = set(request["settings"]) - allowed_v7_settings
            if unknown_settings:
                raise ExperimentError(f"unsupported V7 settings (potential unquoted extra output): {sorted(unknown_settings)}")
            variants = request["settings"].get("variants")
            if type(variants) is not int or variants != 1:
                raise ExperimentError("V7 paid two-image pilot requires exactly one quoted output (settings.variants=1)")
        elif authority_name == "V8 Frames endpoints":
            allowed = {"duration_seconds", "aspect_ratio", "variants", "seed",
                       "generation_mode", "resolution"}
            if set(request["settings"]) != allowed:
                raise ExperimentError("V8 Frames request requires six exact quoted settings and no extra output modes")
            if (request["provider"] != "Google Flow" or request["model"] != "Omni 1.2 Flash"
                    or request["settings"]["generation_mode"] != "Frames to Video"
                    or request["settings"]["resolution"] != "720p"
                    or type(request["settings"]["variants"]) is not int
                    or request["settings"]["variants"] != 1
                    or request["settings"]["seed"] is not None):
                raise ExperimentError("V8 Frames provider/model/mode/720p/x1/seed settings differ from qualified quote")
    elif "source_preflight" in request:
        raise ExperimentError("V6 source_preflight is only supported for the versioned Chart 1 scissor pilot")
    spec_sha = _sha_file(spec)
    if source_preflight and spec_sha != source_preflight["spec_sha256"]:
        raise ExperimentError("photographic motion spec changed between preflight and reservation; discard this attempt")
    # Input order is semantically meaningful: many generators treat image 1 as
    # identity and image 2 as pose authority.
    return {"schema_version": SCHEMA_VERSION, "attempt_key": request["attempt_key"],
            "exercise_id": request["exercise_id"], "spec_sha256": spec_sha,
            "spec_reference": spec.name, "submitted_prompt": content, "submitted_prompt_sha256": _digest_bytes(prompt_bytes),
            "input_assets": clean_assets, "provider": request["provider"], "model": request["model"],
            # Do not retain the caller's mutable dict across verification and
            # reservation fingerprinting; a concurrent edit could otherwise
            # inject an unquoted output multiplier after validation.
            "settings": json.loads(_canonical(request["settings"])), "estimated_credits": estimate,
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
    opening = Decimal(policy["opening_spent_credits"])
    native_charges = Decimal(0)
    reserved = Decimal(0)
    planned = list((store / "intents").glob("*.json")) if (store / "intents").exists() else []
    prior_run_ids = set((policy["opening_provenance"] or {}).get("prior_run_ids", []))
    for path in planned:
        if path.stem in prior_run_ids:
            raise ExperimentError(f"prior opening-debit run is also in native intents: {path.stem}; possible double count")
        intent = _read(path)
        _check_intent_record(intent, path.stem)
        outcome_path = store / "charges" / f"{path.stem}.json"
        if outcome_path.exists():
            receipt = _read(outcome_path)
            if receipt.get("run_id") != path.stem:
                raise ExperimentError(f"charge receipt mismatches intent {path.stem}")
            if receipt.get("release_status") != HOLD or receipt.get("schema_version") != SCHEMA_VERSION:
                raise ExperimentError(f"invalid immutable charge receipt {path.stem}")
            native_charges += Decimal(_credit(receipt.get("actual_credits"), "actual_credits"))
        else:
            reserved += Decimal(_credit(intent.get("estimated_credits"), "estimated_credits"))
    limit = Decimal(_credit(policy["credit_limit"], "credit_limit"))
    orphans = {path.stem for path in (store / "charges").glob("*.json")} - {path.stem for path in planned} if (store / "charges").exists() else set()
    if orphans:
        raise ExperimentError(f"charge receipt without a known intent: {sorted(orphans)}")
    committed = opening + native_charges
    return {"provider": policy["provider"], "credit_limit": format(limit, "f"),
            "actual_credits": format(committed, "f"), "pending_reserved_credits": format(reserved, "f"),
            "available_credits": format(limit - committed - reserved, "f"),
            "opening_spent_credits": format(opening, "f"),
            "opening_evidence_status": policy["opening_evidence_status"],
            "native_receipts_actual_credits": format(native_charges, "f"),
            "opening_reconciled_attempts": len(prior_run_ids),
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
        if policy["opening_evidence_status"] == "LEGACY_EXTERNAL_ONLY_ARCHIVE_REQUIRED":
            raise ExperimentError("positive opening debit needs private evidence snapshot; run archive-evidence before reserving credits")
        if run_id in (policy["opening_provenance"] or {}).get("prior_run_ids", []):
            raise ExperimentError("run already accounted for by opening prior-spend debit; never reserve it again")
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
        _policy(store)  # Revalidate private evidence before recording an actual charge.
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
    init.add_argument("--opening-spent-credits", help="REQUIRED for a fresh store: explicit zero or prior documented debits")
    init.add_argument("--opening-evidence", help="Existing evidence document; rehashed for a positive prior debit")
    init.add_argument("--opening-run-id", action="append", help="Prior immutable run fingerprint for an opening debit; repeat as needed")
    evidence = actions.add_parser("archive-evidence", help="Portably snapshot exact existing opening-debit evidence in the private ledger")
    evidence.add_argument("--store", required=True)
    evidence.add_argument("--evidence", required=True, help="Existing file with SHA matching immutable policy, even if old path was lost")
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
            result = initialize(args.store, provider=args.provider, credit_limit=args.credit_limit,
                                opening_spent_credits=args.opening_spent_credits,
                                opening_evidence_path=args.opening_evidence,
                                opening_run_ids=args.opening_run_id)
        elif args.command == "archive-evidence":
            result = archive_evidence(args.store, evidence_path=args.evidence)
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
