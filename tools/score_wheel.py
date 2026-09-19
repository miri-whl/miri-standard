#!/usr/bin/env python3
"""Score an arbitrary wheel with the reference linter, through the sample SDK's gate - not a copy of it.

Used by publish-checks.yml on the definitions wheel (miri-standard-checks): the standard's own artifact held
to the standard it carries. ADVISORY: the verdict is printed and the exit code does not depend on it, because
two MUSTs are known to fail for structural reasons recorded in the response to
upstream-artifact-publishing-feedback.md section 4 - MIRI-PY-020 has no vocabulary for an artifact distributed
outside an index, and a data-only package still owes agent-metadata/. When both close, flip ADVISORY to False.

Exit 0 after scoring; 1 if `miri score` produced no parsable report (a tooling failure, which IS worth failing
on); 2 if miri is not on PATH.
"""
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from score_sample import score_wheel  # noqa: E402

ADVISORY = True


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
