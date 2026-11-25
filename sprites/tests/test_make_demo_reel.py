"""Reel caption filters must not re-interpret punctuation as FFmpeg syntax."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kit"))
import make_demo  # noqa: E402


class ReelCaptionTest(unittest.TestCase):
    def test_caption_files_preserve_colons_and_commas(self):
        calls = []
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            work = root / "work"
            work.mkdir()
            output = root / "out"
            output.mkdir()

            def record_only(command):
                calls.append(command)
                if command and command[-1] == str(output / "reel.part.mp4"):
                    (output / "reel.part.mp4").write_bytes(b"test-reel")

            with mock.patch.object(make_demo, "sh", side_effect=record_only), mock.patch.object(
                make_demo.tempfile, "mkdtemp", return_value=str(work)
            ):
                make_demo.build_reel("fixture-chart-data.json", str(output))

            filters = [command[command.index("-vf") + 1] for command in calls if "-vf" in command]
            self.assertEqual(len(filters), 5)
            for value in filters:
                self.assertIn("drawtext=", value)
                self.assertIn(":textfile=", value)
                self.assertNotIn(":text='", value)
                caption_path = value.split(":textfile=", 1)[1].split(":fontcolor=", 1)[0]
                self.assertTrue(os.path.isfile(caption_path))

            caption = (work / "caption-0.txt").read_text(encoding="utf-8")
            self.assertIn("Chart 1 level A+: four exercises", caption)
            self.assertIn(", ", caption)
            self.assertEqual((output / "reel.mp4").read_bytes(), b"test-reel")


if __name__ == "__main__":
    unittest.main()
