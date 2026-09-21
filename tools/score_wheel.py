#!/usr/bin/env python3
"""Score an arbitrary wheel with the reference linter, through the sample SDK's gate - not a copy of it.

Used by publish-checks.yml on the definitions wheel (miri-standard-checks): the standard's own artifact held
to the standard it carries. GATING: a wheel with a failing MUST does not reach the release page.

It was advisory while two MUSTs were known to fail - the package shipped no agent-metadata/, and its registry
named a GitHub Releases page, which MIRI-PY-020 rejects because a registry a consumer cannot install from is
not a registry. Both are closed: the build writes agent-metadata/, examples/ and docs/, and the site publishes
a PEP 503 index the registry now names. Measured under miri-py 0.6.0: 98 of 48.0, health 100, zero MUST
failures, grade `undetermined` because six MUSTs need --execute or a previous release.

`undetermined` passes this gate deliberately - it is not non-conformance, and the default static posture
structurally forfeits those six for every artifact. What fails: a non-empty must_failures, or an explicit
non-conforming grade.

Exit 0 after scoring; 1 if `miri score` produced no parsable report (a tooling failure, which IS worth failing
on); 2 if miri is not on PATH.
"""
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from score_sample import score_wheel  # noqa: E402

ADVISORY = False


def main(argv: list[str]) -> int:
    miri = shutil.which("miri")
    if not miri:
        print("miri (miri-py) not on PATH - wheel not scored.")
        return 2
    if not argv:
        print("usage: score_wheel.py <wheel> [...]", file=sys.stderr)
        return 2
    worst = 0
    for w in argv:
        name = pathlib.Path(w).name
        ok = score_wheel(miri, w, [], "static", subject=name)
        if ok is None:
            worst = 1
        elif not ok and not ADVISORY:
            worst = max(worst, 1)
        elif not ok:
            print(f"::warning::{name}: not conforming in the static posture (advisory; see docstring).")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
