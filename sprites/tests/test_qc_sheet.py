"""Optional media checks exercise the production keyer, not an alternate one."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import qc_sheet

try:
    import numpy as np
    from PIL import Image, ImageDraw
except ImportError:
    np = None


@unittest.skipIf(np is None, "Media QC tests require Pillow and NumPy")
class SheetQCTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "sheet.png"

    def sheet(self, rectangles, *, colour=(5, 160, 242, 255)):
        im = Image.new("RGBA", (600, 320), (255, 0, 255, 0))
        draw = ImageDraw.Draw(im)
        for coords in rectangles:
            draw.rectangle(coords, fill=colour)
        im.save(self.path)

    @staticmethod
    def row(report, name):
        return next(r for r in report["checks"] if r["name"] == name)

    def test_separated_figures_pass_count_floor_and_palette(self):
        self.sheet([(60, 70, 130, 245), (420, 70, 490, 245)])
        qc = qc_sheet.inspect_sheet(self.path, 2, qc={"floor_check": True, "grounded": [0, 1]},
                                    palette=[{"name": "tank", "hex": "#05a0f2", "tol": 20, "min_frac": .1}])
        self.assertEqual(qc["status"], "PASS")
        for name in ("figure count", "floor alignment", "character palette", "figure clearance"):
            self.assertEqual(self.row(qc, name)["status"], "PASS")

    def test_touching_figures_fail_count(self):
        self.sheet([(55, 70, 190, 245), (190, 70, 325, 245)])
        qc = qc_sheet.inspect_sheet(self.path, 2)
        self.assertEqual(self.row(qc, "figure count")["status"], "FAIL")

    def test_close_but_separate_figures_warn(self):
        self.sheet([(70, 60, 145, 245), (161, 60, 236, 245)])
        qc = qc_sheet.inspect_sheet(self.path, 2)
        self.assertEqual(self.row(qc, "figure count")["status"], "PASS")
        self.assertEqual(self.row(qc, "figure clearance")["status"], "WARN")

    def test_missing_palette_colour_is_flagged(self):
        self.sheet([(60, 70, 130, 245), (420, 70, 490, 245)])
        qc = qc_sheet.inspect_sheet(self.path, 2,
                                    palette=[{"name": "red shorts", "hex": "#ff0000", "tol": 20, "min_frac": .1}])
        self.assertEqual(self.row(qc, "character palette")["status"], "FAIL")

    def test_grounded_and_airborne_poses(self):
        self.sheet([(45, 65, 110, 245), (180, 50, 245, 175),
                    (320, 65, 385, 245), (465, 50, 530, 175)])
        qc = qc_sheet.inspect_sheet(self.path, 4, qc={"floor_check": True,
                    "grounded": [0, 2], "airborne": {"1": .06, "3": .06}})
        self.assertEqual(self.row(qc, "floor alignment")["status"], "PASS")
        self.assertTrue(all(r["status"] == "PASS" for r in qc["checks"] if r["name"] == "airborne lift"))

    def test_missing_and_invalid_files_cannot_pass(self):
        self.assertEqual(qc_sheet.inspect_sheet(self.path, 2)["status"], "NOT_RUN")
        self.path.write_text("not a picture", encoding="utf-8")
        self.assertEqual(qc_sheet.inspect_sheet(self.path, 2)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
