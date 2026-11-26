"""Versioned, source-verified photographic motion authority.

These values describe one *specific* archived V6 diagnostic card. Changing to
a different photographic master or pose source requires a new authority entry
and a new experiment version; it must not silently redefine V6 evidence.

This module deliberately has no image-processing or paid-provider dependency.
"""

V6_TAGGED_CARD_SHA256 = "4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2"
V6_TAGGED_CARD_SIZE = (1536, 1024)
V6_PANEL_A_CROP = (4, 4, 764, 508)  # half-open: left, top, right, bottom
V6_PANEL_A_START_STATE = {
    "orange_leg": "back", "teal_leg": "forward",
    "orange_arm": "forward", "teal_arm": "back",
}
V6_ANATOMICAL_LEFT_RIGHT_PROVEN = False
