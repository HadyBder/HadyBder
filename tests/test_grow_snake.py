import unittest

from scripts.grow_snake import build


def svg(cells):
    rects = "".join(
        f'<rect class="c {level}" x="{x}" y="{y}" width="12" height="12"/>'
        for x, y, level in cells
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" '
        'viewBox="0 0 64 64">'
        '<style>:root{--c1:#111;--c2:#222;--c3:#333;--c4:#444}'
        '.c.c1{fill:var(--c1)}</style>'
        f'{rects}</svg>'
    )


class BuildTests(unittest.TestCase):
    def test_complete_grid_builds(self):
        source = svg([
            (0, 0, "c1"), (16, 0, ""),
            (0, 16, ""), (16, 16, ""),
        ])
        result, stats = build(source, seed=7, rounds=1)
        self.assertIn("<svg", result)
        self.assertEqual(stats["food"], 1)

    def test_missing_grid_cell_is_rejected(self):
        source = svg([
            (0, 0, "c1"), (16, 0, ""),
            (0, 16, ""),
        ])
        with self.assertRaisesRegex(ValueError, "incomplete"):
            build(source, seed=7, rounds=1)


if __name__ == "__main__":
    unittest.main()
