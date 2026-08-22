#!/usr/bin/env python3
"""Materialize the three consumption fixtures from one shared source tree.

Variants — identical code, different shipped metadata:

  bare         no `agent-metadata/` at all. The honest-degradation baseline: a conformant
               consumer must report every document as absent and synthesize nothing.
  miri         a conforming `agent-metadata/`. The comparison arm.
  adversarial  a hostile `agent-metadata/` whose contents attack the consumer rules
               (see metadata/adversarial/*.json and the attack table in README.md).

The point of building from ONE template is that "identical source" is enforced
mechanically rather than by discipline: after materializing, this script byte-compares
every .py file across the three variants and fails if any differ. So any behavioral
difference a consumer shows between variants is attributable to metadata alone.

Usage:
    python3 examples/fixtures/build_fixtures.py [--out DIR]

Writes source trees only. Building wheels is the caller's job (the fixtures are
useful uninstalled, and wheel-building needs a backend the standard repo does not
otherwise require).
"""
import argparse
import filecmp
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "src/_template"
METADATA = HERE / "metadata"

VARIANTS = {
    # variant: (distribution name, import package name, metadata dir or None)
    "bare": ("greet-bare", "greet_bare", None),
    "miri": ("greet-miri", "greet_miri", METADATA / "miri"),
    "adversarial": ("greet-adversarial", "greet_adversarial", METADATA / "adversarial"),
}

PYPROJECT = """\
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "{dist}"
version = "1.0.0"
description = "Consumption fixture ({variant} variant) — identical source, {meta} metadata."
requires-python = ">=3.9"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"{pkg}" = ["agent-metadata/*.json"]
"""


def build(out: pathlib.Path) -> int:
    if not TEMPLATE.is_dir():
        print(f"template source missing: {TEMPLATE}", file=sys.stderr)
        return 1

    built = {}
    for variant, (dist, pkg, meta_dir) in VARIANTS.items():
        root = out / variant
        if root.exists():
            shutil.rmtree(root)
        pkg_dir = root / "src" / pkg
        shutil.copytree(TEMPLATE, pkg_dir)

        if meta_dir is not None:
            shutil.copytree(meta_dir, pkg_dir / "agent-metadata")

        (root / "pyproject.toml").write_text(
            PYPROJECT.format(
                dist=dist,
                pkg=pkg,
                variant=variant,
                meta="no" if meta_dir is None else variant,
            )
        )
        built[variant] = pkg_dir
        n = len(list((pkg_dir / "agent-metadata").glob("*.json"))) if meta_dir else 0
        print(f"  {variant:12s} -> {root}  ({n} metadata document(s))")

    # The honesty check: identical source across every variant, verified byte-for-byte.
    names = sorted(p.name for p in TEMPLATE.glob("*.py"))
    reference = built["bare"]
    for variant, pkg_dir in built.items():
        if variant == "bare":
            continue
        diff = [n for n in names if not filecmp.cmp(reference / n, pkg_dir / n, shallow=False)]
        if diff:
            print(f"FAIL: {variant} source differs from bare in {diff}", file=sys.stderr)
            return 1
    print(f"verified: {len(names)} source file(s) byte-identical across all "
          f"{len(VARIANTS)} variants — any consumer difference is metadata-attributable")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=pathlib.Path, default=HERE / "build",
                    help="output directory (default: examples/fixtures/build)")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    print(f"building consumption fixtures into {args.out}")
    return build(args.out)


if __name__ == "__main__":
    sys.exit(main())
