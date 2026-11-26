"""Zero-credit, direct-source authority for one experimental Flow image outpaint.

Only the *input* A or C PNG is authenticated. Generated pixels, anatomy,
identity, framing and any later video use require separate independent review.
No provider calls, image edits, reservations or credits occur in this module.
"""

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .source_authority import (
    V7_PARENT_V6_STATUS, V7_PREPARED_A_SHA256, V7_PREPARED_C_SHA256,
    V7_PREPARED_SIZE,
)


class OutpaintPreflightError(ValueError):
    """V9 must not use unverified or substituted photographic source bytes."""


AUTHORITY = "V9_DIRECT_A_OR_C_OUTPAINT_IMAGE_EDIT"
SOURCE_SHA256 = {"A": V7_PREPARED_A_SHA256, "C": V7_PREPARED_C_SHA256}
IMAGE_EDIT_SETTINGS = {
    "generation_mode": "Image editor",
    "aspect_ratio": "Original",
    "thinking_level": "High",
    # This is the operator's *requested* single output, not a claimed
    # provider-visible selector. Verify the returned number independently.
    "requested_outputs": 1,
}


def _expected_spec():
    return {
        "schema_version": 1,
        "authority": AUTHORITY,
        "exercise_id": "chart1-scissor-jump",
        "artifact_kind": "EXPERIMENTAL_DERIVED_STILL_NOT_VIDEO",
        "source_authority": "V7_DIRECT_PREPARED_PAIR",
        "source_png_sha256": dict(SOURCE_SHA256),
        "source_size": list(V7_PREPARED_SIZE),
        "source_format": "RGB PNG",
        "provider": "Google Flow",
        "model": "Nano Banana 2.1",
        "settings": dict(IMAGE_EDIT_SETTINGS),
        "provider_quote_credits": "0",
        "parent_v6_card_status": V7_PARENT_V6_STATUS,
        "status": "EXPERIMENTAL_UNREVIEWED_DERIVED_STILL",
    }


def _read_regular(path, label):
    path = Path(path).expanduser()
    if path.is_symlink():
        raise OutpaintPreflightError(f"{label} must not be a symlink")
    path = path.resolve()
    if not path.is_file():
        raise OutpaintPreflightError(f"{label} does not exist")
    return path, path.read_bytes()


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def verify_source(spec_path, source_png, *, source_pose):
    """Return evidence for one A-or-C original, not a derived image pass."""
    if source_pose not in SOURCE_SHA256:
        raise OutpaintPreflightError("source_pose must be exactly A or C")
    spec_file, spec_bytes = _read_regular(spec_path, "V9 image-edit specification")
    try:
        spec = json.loads(spec_bytes)
    except (UnicodeDecodeError, ValueError) as exc:
        raise OutpaintPreflightError(f"invalid V9 specification: {exc}") from exc
    if spec != _expected_spec():
        raise OutpaintPreflightError("V9 specification differs from the pinned image-edit authority")
    image_file, image_bytes = _read_regular(source_png, f"original {source_pose} PNG")
    actual_sha = _sha(image_bytes)
    if actual_sha != SOURCE_SHA256[source_pose]:
        raise OutpaintPreflightError(f"original {source_pose} SHA-256 differs from the direct-source authority")
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            if image.format != "PNG" or image.mode != "RGB" or image.size != V7_PREPARED_SIZE:
                raise OutpaintPreflightError("original source must be an RGB 1280x720 PNG")
            image.load()
            pixels_sha = _sha(image.tobytes())
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        if isinstance(exc, OutpaintPreflightError):
            raise
        raise OutpaintPreflightError(f"original source PNG does not decode fully: {exc}") from exc
    # Detect changed local bytes while verifying; image-source claims cannot
    # silently switch between preflight and immutable intent creation.
    if _sha(spec_file.read_bytes()) != _sha(spec_bytes) or _sha(image_file.read_bytes()) != actual_sha:
        raise OutpaintPreflightError("V9 specification or source bytes changed during verification")
    return {
        "authority": AUTHORITY,
        "source_pose": source_pose,
        "spec_sha256": _sha(spec_bytes),
        "source_png_sha256": actual_sha,
        "source_png_pixels_sha256": pixels_sha,
        "source_size": list(V7_PREPARED_SIZE),
        "parent_v6_card_status": V7_PARENT_V6_STATUS,
        "parent_crop_replay_verified": False,
        "preflight_result": "VERIFIED_ORIGINAL_SOURCE_BYTES_ONLY",
        "derived_still_framing_identity_and_form_approval": "NOT_EVALUATED",
        "paid_video_source_authority": "NOT_GRANTED",
    }


def _main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("source_png", type=Path)
    parser.add_argument("--source-pose", choices=("A", "C"), required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(verify_source(args.spec, args.source_png, source_pose=args.source_pose),
                         indent=2, sort_keys=True))
    except (OutpaintPreflightError, OSError, TypeError) as exc:
        print(f"V9 source outpaint preflight FAIL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_main())
