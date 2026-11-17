# Contribution-snake renderer maintenance

`grow_snake.py` transforms the fresh contribution-grid SVGs produced by the
generator in [the publishing workflow](../.github/workflows/contribution-snake.yml).
It uses only the Python standard library. Run checks from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The four regressions cover complete grids, legitimate partial edge weeks,
missing interior cells, and duplicate coordinates. These synthetic checks do
not fetch the current GitHub calendar or publish artwork.

## Transforming local copies

The command-line interface **overwrites every input file in place**. Work only
on disposable copies of fresh generator output, not on tracked artwork or the
already transformed SVGs from the `output` branch. Transformed SVGs are not
valid inputs for a second transformation.

```bash
python3 scripts/grow_snake.py /tmp/snake-light-copy.svg /tmp/snake-dark-copy.svg
```

Those two files must already exist and contain fresh contribution-grid SVGs.
The script chooses one random seed for the invocation, so both themes share
the same routes, and renders four scenes per loop by default. It prints food
count, scene count, final length, and duration for each file.

For repeatable debugging, import `build(source, seed=7, rounds=1)` from
`scripts.grow_snake`. It returns `(svg_text, stats)` without writing a file.
The seed and scene count are Python API arguments, not CLI flags.

## Validation and publishing boundaries

Duplicate coordinates and missing interior cells are rejected before route
generation; missing cells in the first or last column are allowed. Spacing
must match the generator's 16-pixel grid. If upstream SVG structure changes,
inspect the fresh input and update tests rather than bypassing the guards.

The [PR workflow](../.github/workflows/renderer-tests.yml) runs the unit suite
with read-only permissions. The publishing workflow also runs it before
generation, transforms both themes, and commits the resulting files to
`output`. Local unit tests and documentation-only changes do not publish SVGs.
