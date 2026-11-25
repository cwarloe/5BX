"""Reel caption filters must not re-interpret punctuation as FFmpeg syntax."""

import ast
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path


def isolated_reel_function(work, recorder):
    """Execute the real function without importing optional Pillow/FFmpeg kit deps.

    The repository's definition/preflight job intentionally has no image
    packages installed; a caption-only regression must remain dependency-free.
    """
    path = Path(__file__).resolve().parents[1] / "kit" / "make_demo.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build_reel")
    scope = {
        "os": os,
        "sys": sys,
        "json": json,
        "tempfile": types.SimpleNamespace(mkdtemp=lambda: str(work)),
        "HERE": str(path.parent),
        "ROOT": str(path.parents[1]),
        "jload": lambda src: json.loads(Path(src).read_text(encoding="utf-8")),
        "sh": recorder,
    }
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(path), "exec"), scope)
    return scope["build_reel"]


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

            build_reel = isolated_reel_function(work, record_only)
            build_reel("fixture-chart-data.json", str(output))

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
