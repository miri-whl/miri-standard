#!/usr/bin/env python3
"""Materialize the greetctl CLI fixture arms and verify they share one implementation.

Four arms from one implementation file:

  bare               no Miri metadata at all - no --describe, no check-update, no changelog
  miri-1.0.0         conforming, the PREVIOUS release
  miri-1.1.0         conforming, the CURRENT release
  adversarial-1.1.0  hostile metadata, eleven attacks (C1-C11)

Two of these are the same tool at two points in its life, which is what the wheel fixtures have no need of and the
CLI fixtures cannot do without: five MIRI-CLI checks (030, 033, 035, 036, 037 - fourteen of the hundred weight)
are claims about what the binary USED TO DO, and a single release contains no evidence of that.

Like the wheel builder, this byte-compares greetctl.py across every arm. If the implementation is identical then any
difference a consumer observes is attributable to the metadata and not to the code.
"""
import hashlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "src/_template/greetctl.py"
DATA = HERE / "data"
BUILD = HERE / "build"

# arm -> (describe data file or None, fixture control file)
ARMS = {
    "bare": (None, "bare.fixture.json"),
    "miri-1.0.0": ("miri-1.0.0.json", "miri-1.0.0.fixture.json"),
    "miri-1.1.0": ("miri-1.1.0.json", "miri-1.1.0.fixture.json"),
    "adversarial-1.1.0": ("adversarial-1.1.0.json", "adversarial-1.1.0.fixture.json"),
}


def build():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    digests = {}
    for arm, (describe, fixture) in ARMS.items():
        out = BUILD / arm
        out.mkdir(parents=True)
        target = out / "greetctl.py"
        shutil.copy2(TEMPLATE, target)
        target.chmod(0o755)
        digests[arm] = hashlib.sha256(target.read_bytes()).hexdigest()
        if describe:
            shutil.copy2(DATA / describe, out / "describe.json")
        shutil.copy2(DATA / fixture, out / "fixture.json")
        print(f"  built {arm:<20} {'describe.json + ' if describe else ''}fixture.json")

    unique = set(digests.values())
    if len(unique) != 1:
        print("\nFAIL: greetctl.py differs across arms - a consumer difference would not be "
              "metadata-attributable", file=sys.stderr)
        for arm, d in digests.items():
            print(f"  {arm:<20} {d[:16]}", file=sys.stderr)
        return 1
    print(f"\n  implementation identical across {len(ARMS)} arms  sha256:{unique.pop()[:16]}")
    return 0


def main():
    if not TEMPLATE.exists():
        print(f"missing template: {TEMPLATE}", file=sys.stderr)
        return 2
    for _, (describe, fixture) in ARMS.items():
        for f in (describe, fixture):
            if f and not (DATA / f).exists():
                print(f"missing data file: {DATA / f}", file=sys.stderr)
                return 2
    print("greetctl CLI fixtures:")
    rc = build()
    if rc == 0:
        # A last guard: the conforming arms must not carry fixture-control keys in the served document.
        for arm in ("miri-1.0.0", "miri-1.1.0"):
            doc = json.loads((BUILD / arm / "describe.json").read_text())
            leaked = [k for k in doc if k.startswith("_")]
            if leaked:
                print(f"FAIL: {arm} describe.json leaks control keys {leaked}", file=sys.stderr)
                return 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
