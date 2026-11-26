"""Strict, unpaid V8 Frames-to-Video segment authority; V7 cycle stays intact."""

import hashlib
import json
from pathlib import Path

from .preflight_v7 import verify_pair
from .source_authority import V7_PREPARED_A_SHA256, V7_PREPARED_C_SHA256


class SegmentPreflightError(ValueError):
    pass


_SEGMENTS = {
    "A_TO_C": ("A", "C", V7_PREPARED_A_SHA256, V7_PREPARED_C_SHA256),
    "C_TO_A": ("C", "A", V7_PREPARED_C_SHA256, V7_PREPARED_A_SHA256),
}


def verify_segment(spec_path, a_png, c_png, *, expected_role=None):
    spec_path = Path(spec_path).resolve()
    try:
        original = spec_path.read_bytes()
        spec = json.loads(original)
    except (OSError, UnicodeError, ValueError) as exc:
        raise SegmentPreflightError(f"invalid V8 segment specification: {exc}") from exc
    role = spec.get("segment_role") if isinstance(spec, dict) else None
    if role not in _SEGMENTS or (expected_role and expected_role != role):
        raise SegmentPreflightError("V8 segment role must match A_TO_C or C_TO_A request")
    start, end, start_sha, end_sha = _SEGMENTS[role]
    expected = {
        "schema_version": 1, "authority": "V8_FRAMES_DIRECT_A_C_SEGMENTS",
        "exercise_id": "chart1-scissor-jump", "duration_seconds": 3,
        "fps": 24, "aspect_ratio": "16:9", "resolution": "720p",
        "model": "Omni 1.2 Flash", "generation_mode": "Frames to Video",
        "segment_role": role, "start_pose": start, "end_pose": end,
        "start_sha256": start_sha, "end_sha256": end_sha,
        "phase_support_sequence": [f"{start}_grounded", "airborne_exchange", f"{end}_grounded"],
        "form_rules": ["one true airborne exchange with both shoes off ground",
                       "physical orange/teal arm and leg identity preserved",
                       "straight shoulder-high opposing arms", "fixed full-body camera",
                       "no fade, ghost, audio or extra person"],
        "parent_v7_cycle_spec": "photo_motion/specs/chart1-scissor-jump-v7-prepared-pair.json",
        "status": "EXPERIMENTAL",
    }
    if set(spec) != set(expected) or any(spec.get(k) != v for k, v in expected.items()):
        raise SegmentPreflightError("V8 segment specification differs from pinned endpoint contract")
    # Reuse V7's unchanged direct-byte verification, including full RGB PNG
    # decoding and its explicit warning about the missing V6 parent card.
    v7_spec = Path(__file__).resolve().parent / "specs/chart1-scissor-jump-v7-prepared-pair.json"
    source = verify_pair(v7_spec, a_png, c_png)
    if (source["prepared_png_sha256"] != V7_PREPARED_A_SHA256 or
            source["opposite_pose_reference"]["prepared_png_sha256"] != V7_PREPARED_C_SHA256):
        raise SegmentPreflightError("V7 direct prepared source hashes do not match V8")
    return {
        "authority": expected["authority"], "segment_role": role,
        "spec_sha256": hashlib.sha256(original).hexdigest(),
        "start_sha256": start_sha, "end_sha256": end_sha,
        "source_preflight": source,
        "preflight_result": "VERIFIED_DIRECT_ENDPOINT_BYTES_ONLY_NOT_MOTION",
        "form_and_release_approval": "NOT_EVALUATED",
    }
