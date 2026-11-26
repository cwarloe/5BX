"""Versioned, source-verified photographic motion authority.

These values describe one *specific* archived V6 diagnostic card. Changing to
a different photographic master or pose source requires a new authority entry
and a new experiment version; it must not silently redefine V6 evidence.

This module deliberately has no image-processing or paid-provider dependency.
"""

V6_TAGGED_CARD_SHA256 = "4f27260bd19da14bc80a75944dc8f7e2bf790a7e148caa223017fbde130cb0f2"
V6_TAGGED_CARD_SIZE = (1536, 1024)
V6_PANEL_A_CROP = (4, 4, 764, 508)  # half-open: left, top, right, bottom
V6_PANEL_C_CROP = (4, 516, 764, 1020)  # verified lower-left opposite grounded stance
V6_PANEL_A_START_STATE = {
    "orange_leg": "back", "teal_leg": "forward",
    "orange_arm": "forward", "teal_arm": "back",
}
V6_PANEL_C_OPPOSITE_STATE = {
    "orange_leg": "forward", "teal_leg": "back",
    "orange_arm": "back", "teal_arm": "forward",
}
V6_ANATOMICAL_LEFT_RIGHT_PROVEN = False

# V7 is a new, strictly narrower direct-image authority. The original V6
# 1536x1024 card was lost with ephemeral workspace state. These hashes pin
# independently archived, byte-exact prepared PNGs; they do NOT reconstruct or
# independently verify the parent V6 crop/padding/resampling provenance.
V7_PREPARED_PAIR_AUTHORITY = "V7_DIRECT_PREPARED_PAIR"
V7_PREPARED_A_SHA256 = "7758266ca6b27ee7601b4635e5df9e7ee8de09aa4f3bea95caea353e4bf78f2f"
V7_PREPARED_C_SHA256 = "c0ede374ee3a65266c19b27fc0f295a44a5a95e9d3aa0c1b41982b64f4a155a0"
V7_PREPARED_SIZE = (1280, 720)
V7_PARENT_V6_STATUS = "UNAVAILABLE_NOT_BYTE_REPLAY_VERIFIED"
