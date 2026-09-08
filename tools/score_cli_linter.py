#!/usr/bin/env python3
"""Grade a CLI linter against the greetctl goldens.

An adversarial panel found that `examples/fixtures/cli/expected/` was empty while the wheel side shipped
24 goldens, so nothing stated what a linter MUST report. Its verdict: "an inert linter and a screaming
linter score identically because nothing scores them." This is what scores them.

Each golden is a PAIR. A check must be reported on the arm carrying the attack and must NOT be reported on
the conforming arm, which is byte-identical in source. That pairing is what makes the suite discriminating:
the attack arm catches a linter that reports nothing, the control arm catches one that reports everything.
Neither arm decides a case alone.

Usage:
    score_cli_linter.py --report path.json     grade a linter's report
    score_cli_linter.py --self-test            prove the harness discriminates

Report format - what the linter reported, per arm:
    {"adversarial-1.1.0": ["MIRI-CLI-017", ...], "miri-1.1.0": [...]}

A linter that cannot evaluate a check (no previous release, no network) reports it as skipped rather than
omitting it, using the fixed reasons of check-v1.json:
    {"adversarial-1.1.0": {"reported": [...], "skipped": {"MIRI-CLI-037": "previous_release_unavailable"}}}
Skipping is conforming where the capability is genuinely absent; silently omitting is not, and this tool
cannot tell the difference unless the linter says so.
"""
import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
GOLDENS = REPO / "examples/fixtures/cli/expected"


def load_goldens():
    out = []
    for f in sorted(GOLDENS.glob("C*.json"), key=lambda p: int(p.name[1:].split("-")[0])):
        out.append((f.stem, json.loads(f.read_text())))
    return out


def _arm(report, arm):
    """Accept either a bare list of reported checks or the {reported, skipped} form."""
    v = report.get(arm, [])
    if isinstance(v, dict):
        return set(v.get("reported", [])), dict(v.get("skipped", {}))
    return set(v), {}


def grade(report, verbose=True):
    goldens = load_goldens()
    scored = failures = skipped_ok = 0
    for name, g in goldens:
        checks = set(g["checks"])
        if not checks:
            if verbose:
                print(f"  n/a    {name} — no MIRI-CLI check covers this; the gap is the finding")
            continue
        scored += 1
        atk = g["linter_assertion"]["must_report_on"]
        ctl = g["linter_assertion"]["must_not_report_on"]
        got_atk, skips = _arm(report, atk["arm"])
        got_ctl, _ = _arm(report, ctl["arm"])

        missing = checks - got_atk - set(skips)
        forfeited = checks & set(skips)
        false_pos = checks & got_ctl

        if missing or false_pos:
            failures += 1
            why = []
            if missing:
                why.append(f"did not report {sorted(missing)} on {atk['arm']}")
            if false_pos:
                why.append(f"reported {sorted(false_pos)} on the CONFORMING arm {ctl['arm']}")
            if verbose:
                print(f"  FAIL   {name} — {'; '.join(why)}")
        else:
            if forfeited:
                skipped_ok += 1
            if verbose:
                tail = f" (skipped: {sorted(forfeited)})" if forfeited else ""
                print(f"  pass   {name}{tail}")

    if verbose:
        print(f"\n  {scored - failures}/{scored} golden(s) satisfied"
              + (f", {skipped_ok} via a declared capability skip" if skipped_ok else ""))
    return failures, scored


def self_test():
    """The harness is worthless unless it fails both degenerate linters."""
    goldens = load_goldens()
    every = sorted({c for _, g in goldens for c in g["checks"]})

    inert = {"adversarial-1.1.0": [], "miri-1.1.0": []}
    screaming = {"adversarial-1.1.0": every, "miri-1.1.0": every}
    correct = {"adversarial-1.1.0": every, "miri-1.1.0": []}

    print("self-test — the harness must reject both degenerate linters:\n")
    ok = True
    for label, rep, want_fail in (("inert (reports nothing)", inert, True),
                                  ("screaming (reports everything, on both arms)", screaming, True),
                                  ("correct (attacks only, control clean)", correct, False)):
        f, n = grade(rep, verbose=False)
        good = (f > 0) if want_fail else (f == 0)
        ok &= good
        verdict = "rejected" if f else "accepted"
        print(f"  {'PASS' if good else 'FAIL'}  {label:46s} {verdict} ({f}/{n} golden(s) failed)")

    print()
    if not ok:
        print("FAIL: the harness does not discriminate", file=sys.stderr)
        return 1
    print("the harness discriminates: an inert linter and a screaming linter both fail; a correct one passes")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", help="JSON report from a linter, keyed by arm")
    ap.add_argument("--self-test", action="store_true", help="prove the harness discriminates")
    a = ap.parse_args()

    if not GOLDENS.exists() or not any(GOLDENS.glob("C*.json")):
        print("no CLI goldens found — nothing states what a linter must report", file=sys.stderr)
        return 2
    if a.self_test:
        return self_test()
    if not a.report:
        ap.error("one of --report or --self-test is required")
    failures, scored = grade(json.loads(pathlib.Path(a.report).read_text()))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
