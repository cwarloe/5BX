"""Proposed fail-first gates: audit-only, not part of the production branch.

These deliberately fail against 12fc5b1. They guard a paid run from citing
source geometry that was never verified and require real floor-reaching form.
"""

import copy
import unittest
from pathlib import Path

from photo_motion.__main__ import _check_spec
from photo_motion.contract import load_spec


SPECS = Path(__file__).resolve().parents[1] / "specs"


class ProposedPrecreditRegressions(unittest.TestCase):
    def test_scissor_verified_v6_source_hash_and_crop_are_not_replaceable_by_unverified_values(self):
        spec = copy.deepcopy(load_spec(SPECS / "chart1-scissor-jump.json"))
        spec["track_provenance"]["source_card_sha256"] = "0" * 64
        spec["track_provenance"]["source_panel_a_clean_crop_half_open"] = [100, 100, 500, 500]
        spec["track_provenance"]["anatomical_left_right_proven"] = True

        self.assertTrue(
            _check_spec(spec),
            "A V6-authoritative scissor plan must reject a forged/unverified source pin and crop before generation",
        )

    def test_toe_touch_peak_requires_actual_floor_contact_not_just_between_feet_target(self):
        spec = copy.deepcopy(load_spec(SPECS / "chart1-toe-touch.json"))
        spec["phases"][1]["fingertips_touch_floor"] = False
        spec["phases"][1]["pose"] = "Hands stop above waist, never touching the floor"

        self.assertTrue(
            _check_spec(spec),
            "Chart 1 Exercise 1 specifies touching the floor; a merely directional reach cannot validate",
        )


if __name__ == "__main__":
    unittest.main()
