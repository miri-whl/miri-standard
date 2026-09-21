#!/usr/bin/env python3
"""Materialize the greetlib wheel fixture arms and build a wheel from each.

The MIRI-PY family had no test material at all: 43 checks, 100 weight, and no artifact that
falsifies any of them. The existing wheel fixtures under examples/fixtures/ drive the CONSUMER and
SURFACE families - they test what a reader does with metadata - and nothing tested what the
checklist says about a wheel.

Nine arms from one package source, byte-compared after materialization so any finding a linter
reports is attributable to metadata rather than to code:

  conforming-1.0.0       the PREVIOUS release, so previous-release checks have something to compare
  conforming-1.1.0       the current release, conforming
  skew-1.1.0             sdk_version and purl disagree with the wheel        (012, 019)
  vacuous-1.1.0          empty api_index and empty patterns                  (007, 008)
  silent-removal-1.1.0   a public symbol gone with no deprecation trail      (030, 043, 044)
  stale-1.1.0            changelog a release behind; stamps years old        (042, 011)
  identity-1.1.0         project page as registry; private on public OSV     (020, 021, 022)
  empty-migration-1.1.0  an all-zeros migration guide that validates         (009)

Each arm is built into a real wheel because `miri score` takes a wheel, not a source tree: the
checks read dist-info, RECORD and the installed layout, none of which exist before the build.
"""
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "src/_template"
DATA = HERE / "data"
BUILD = HERE / "build"

PYPROJECT = '''[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "greetlib"
version = "{version}"
description = "Fixture library for the MIRI-PY conformance suite - arm: {arm}"
requires-python = ">=3.9"

[tool.setuptools]
package-dir = {{"" = "src"}}
packages = ["greetlib"]
include-package-data = true

[tool.setuptools.package-data]
greetlib = ["agent-metadata/*.json", "examples/*.py", "docs/*.md"]
'''


def build(build_wheels: bool = True) -> int:
    if not TEMPLATE.is_dir():
        print(f"template source missing: {TEMPLATE}", file=sys.stderr)
        return 1
    if BUILD.exists():
        shutil.rmtree(BUILD)

    digests: dict[str, str] = {}
    arms = sorted(p for p in DATA.iterdir() if p.is_dir())
    for arm_dir in arms:
        arm = arm_dir.name
        version = json.loads((arm_dir / "_arm.json").read_text())["version"]
        root = BUILD / arm
        pkg = root / "src" / "greetlib"
        shutil.copytree(TEMPLATE, pkg)

        # The silent-removal arm is the one place the SOURCE must differ: MIRI-PY-030 compares the
        # public surface across releases, and a metadata-only removal would be a lie about the code
        # rather than the removal the check exists to catch. It is therefore exempt from the
        # byte-identity check below, and says so rather than being quietly skipped.
        source_differs = arm.startswith(("silent-removal", "empty-migration"))
        if source_differs:
            init = pkg / "__init__.py"
            text = init.read_text()
            text = text.replace('__all__ = ["greet", "farewell"]', '__all__ = ["greet"]')
            text = text[: text.index("def farewell")].rstrip() + "\n"
            init.write_text(text)

        # MIRI-PY-011 requires generated_at inside the build window (24 hours), so the stamps are
        # written HERE rather than committed. A committed stamp ages: every arm, including the
        # conforming ones, failed 011 the first time this ran because the data files carried a fixed
        # date that was 29 hours old by the time the wheels were built. The stale arm keeps its
        # committed stamps on purpose - being outside the window is the thing it demonstrates.
        stamps_frozen = arm.startswith("stale")
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        # One arm ships no agent-metadata/ at all. MIRI-PY-006 is CRITICAL and had no artifact,
        # while costing exactly this `if` - the suite had covered the checks that were interesting
        # to write about rather than the ones that were cheap to cover.
        if json.loads((arm_dir / "_arm.json").read_text()).get("no_agent_metadata"):
            (root / "pyproject.toml").write_text(PYPROJECT.format(version=version, arm=arm))
            digests[arm] = hashlib.sha256((pkg / "__init__.py").read_bytes()).hexdigest()
            print(f"  {arm:24s} v{version:<7} 0 document(s)   [ships no agent-metadata/ by design]")
            continue

        meta = pkg / "agent-metadata"
        meta.mkdir()
        for doc in sorted(arm_dir.glob("*.json")):
            if doc.name == "_arm.json":
                continue
            d = json.loads(doc.read_text())
            if not stamps_frozen and "generated_at" in d:
                d["generated_at"] = now
            (meta / doc.name).write_text(json.dumps(d, indent=2) + "\n")

        (root / "pyproject.toml").write_text(PYPROJECT.format(version=version, arm=arm))
        if not source_differs:
            digests[arm] = hashlib.sha256((pkg / "__init__.py").read_bytes()).hexdigest()

        n = len(list(meta.glob("*.json")))
        print(f"  {arm:24s} v{version:<7} {n} document(s)"
              + ("   [source differs by design: the removal is real]" if source_differs else ""))

    unique = set(digests.values())
    if len(unique) != 1:
        print("\nFAIL: greetlib source differs across arms that should share it - a finding would "
              "not be metadata-attributable", file=sys.stderr)
        for arm, d in sorted(digests.items()):
            print(f"  {arm:24s} {d[:16]}", file=sys.stderr)
        return 1
    print(f"\n  source identical across {len(digests)} arms  sha256:{unique.pop()[:16]}")

    if not build_wheels:
        return 0
    print("\n  building wheels:")
    for arm_dir in arms:
        root = BUILD / arm_dir.name
        r = subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir",
                            str(root / "dist"), str(root)], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    {arm_dir.name}: build failed\n{r.stdout[-600:]}{r.stderr[-600:]}", file=sys.stderr)
            return 1
        whl = next((root / "dist").glob("*.whl"))
        print(f"    {arm_dir.name:24s} -> {whl.name}")
    return 0


def main() -> int:
    print("greetlib wheel fixtures:")
    return build(build_wheels="--no-wheels" not in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
