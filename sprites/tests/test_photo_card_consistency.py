"""Small synthetic regression tests; no generated image is required."""

import tempfile
import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
if (HERE.parent / "kit").is_dir():
    sys.path.insert(0, str(HERE.parent / "kit"))

try:
    from PIL import Image, ImageDraw
    from photo_card_consistency import audit, compare
    OPTIONAL_MEDIA_DEPENDENCIES = True
except ImportError:
    OPTIONAL_MEDIA_DEPENDENCIES = False


def synthetic_card(second_top_track: int = 75, shirt_rgb=(28, 110, 218)):
    im = Image.new("RGB", (404, 404), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    for row in range(2):
        for col in range(2):
            left, top = col * 202 + 2, row * 202 + 2
            draw.rectangle((left, top, left + 195, top + 195), fill=(50, 115, 49))
            track_start = 75 if (row, col) != (0, 1) else second_top_track
            draw.rectangle((left, top + track_start, left + 195, top + 195),
                           fill=(167, 65, 43))
            draw.rectangle((left + 70, top + 10, left + 125, top + 65),
                           fill=shirt_rgb)
    return im


@unittest.skipUnless(OPTIONAL_MEDIA_DEPENDENCIES,
                     "Optional photographic QA requires Pillow, NumPy and SciPy")
class PhotoCardTest(unittest.TestCase):
    def test_aligned_card_reports_track_and_shirt_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "card.png"
            synthetic_card().save(p)
            report = audit(p)
        self.assertEqual(report["checks"]["track"]["status"], "PASS")
        self.assertEqual(report["checks"]["blue_shirt"]["status"], "PASS")
        self.assertEqual(report["checks"]["anatomy_and_age"]["status"],
                         "HUMAN REVIEW REQUIRED")

    def test_misaligned_track_is_flagged(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "card.png"
            synthetic_card(second_top_track=102).save(p)
            report = audit(p)
        self.assertEqual(report["checks"]["track"]["status"], "REVIEW")

    def test_lying_subject_does_not_shift_detected_track_edge(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "card.png"
            img = synthetic_card()
            draw = ImageDraw.Draw(img)
            # Long, gray horizontal torso hides >70% of first red track row
            # in panel A, but outer margins still show the true track edge.
            draw.rectangle((30, 74, 171, 92), fill=(88, 94, 101))
            img.save(p)
            report = audit(p)
        self.assertEqual(report["checks"]["track"]["status"], "PASS")

    def test_same_color_two_cards_show_zero_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "one.png"
            q = Path(temp) / "two.png"
            synthetic_card().save(p)
            synthetic_card().save(q)
            result = compare(audit(p), audit(q))
        for item in result["panels"].values():
            self.assertEqual(item["shirt_median_channel_max_absolute_delta"], 0)
            self.assertEqual(item["track_boundary_delta_px"], 0)


if __name__ == "__main__":
    unittest.main()
