import ast
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from test_grow_snake import svg


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "grow_snake.py"
SVG = "{http://www.w3.org/2000/svg}"


class CommandLineTests(unittest.TestCase):
    def run_renderer(self, *paths):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *(str(path) for path in paths)],
            capture_output=True, text=True, timeout=15, check=False,
        )

    def test_two_themes_share_routes_and_report_written_artwork(self):
        source = svg([
            (0, 0, "c1"), (16, 0, ""),
            (0, 16, ""), (16, 16, ""),
        ])
        with tempfile.TemporaryDirectory() as directory:
            light = Path(directory) / "light.svg"
            dark = Path(directory) / "dark.svg"
            light.write_text(source)
            dark.write_text(source.replace("--c1:#111", "--c1:#abc"))
            completed = self.run_renderer(light, dark)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            lines = completed.stdout.splitlines()
            self.assertEqual(len(lines), 2)
            routes = []
            for path, line, color in zip((light, dark), lines, ("#111", "#abc")):
                with self.subTest(theme=path.name):
                    self.assertTrue(line.startswith(f"{path.name}: "))
                    stats = ast.literal_eval(line.split(": ", 1)[1])
                    self.assertEqual(stats["rounds"], 4)
                    self.assertEqual(stats["food"], 1)
                    self.assertEqual(stats["final_length"], 64)
                    self.assertGreater(stats["duration_ms"], 0)
                    written = path.read_text()
                    self.assertNotEqual(written, source)
                    root = ET.fromstring(written)
                    self.assertEqual(len(root.findall(f"{SVG}rect")), 4)
                    paths = root.findall(f"{SVG}g/{SVG}path")
                    self.assertEqual(len(paths), 4)
                    routes.append([node.get("d") for node in paths])
                    self.assertIn(f"--c1:{color}", root.find(f"{SVG}style").text)
            self.assertEqual(routes[0], routes[1], "both themes must use the invocation's shared seed")

    def test_invalid_input_fails_without_overwriting_that_file(self):
        cases = {
            "malformed": ("<svg", "ParseError"),
            "empty-grid": (svg([]), "No contribution cells"),
            "duplicate": (svg([(0, 0, "c1"), (0, 0, "")]), "Duplicate contribution cell"),
            "interior-gap": (svg([
                (0, 0, ""), (16, 0, ""), (32, 0, ""),
                (0, 16, ""), (32, 16, ""),
                (0, 32, ""), (16, 32, ""), (32, 32, "c1"),
            ]), "missing interior"),
        }
        with tempfile.TemporaryDirectory() as directory:
            for name, (source, error) in cases.items():
                with self.subTest(case=name):
                    path = Path(directory) / f"{name}.svg"
                    path.write_text(source)
                    original_bytes = path.read_bytes()
                    completed = self.run_renderer(path)
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertIn(error, completed.stderr)
                    self.assertEqual(completed.stdout, "")
                    self.assertEqual(path.read_bytes(), original_bytes)


if __name__ == "__main__":
    unittest.main()
