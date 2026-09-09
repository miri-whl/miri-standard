#!/usr/bin/env python3
"""Grade a CLI linter against the greetctl goldens.

Each golden is a PAIR: a check must be reported on the arm carrying the attack and must NOT be reported on
the conforming arm, whose `greetctl.py` is byte-identical. The attack arm catches a linter that reports
nothing; the control arm catches one that reports everything.

A first version of this tool graded a SET of check IDs and nothing else, and an adversarial panel defeated
it six ways - most simply by emitting the union of every golden's check IDs under the key
"adversarial-1.1.0" and an empty list under the other, scoring full marks having never opened a fixture.
Its self-test built a "correct" linter FROM the goldens, so it compared three dictionaries with each other
and reported that the harness discriminated.

So grading now requires ATTRIBUTION: a finding satisfies a golden only if it names the right check AND
points at the evidence that golden declares. Reporting the right ID for the wrong reason is not detection.
Two goldens (C3, C4) cite the same check via different clauses and have different evidence, so one report
cannot satisfy both.

Report format - per arm, the findings and any declared skips:

    {
      "adversarial-1.1.0": {
        "findings": [{"check": "MIRI-CLI-017", "evidence": "identity.version"}, ...],
        "skipped":  {"MIRI-CLI-037": "previous_release_unavailable"}
      },
      "miri-1.1.0": {"findings": [], "skipped": {}}
    }

Both arms are required. A skip is accepted only for a golden that declares it may be skipped, only with the
reason it declares, and only if the SAME check is skipped on both arms - capability belongs to the linter
and its environment, not to the artifact under test, so a check evaluable on one arm is evaluable on both.

Usage:
    score_cli_linter.py --report path.json
    score_cli_linter.py --self-test
"""
import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
GOLDENS = REPO / "examples/fixtures/cli/expected"
SKIP_REASONS = {"network_unavailable", "previous_release_unavailable", "execution_disabled",
                "condition_not_applicable"}


def load_goldens():
    out = []
    for f in sorted(GOLDENS.glob("C*.json"), key=lambda p: int(p.name[1:].split("-")[0])):
        out.append((f.stem, json.loads(f.read_text())))
    return out


def _arm(report, arm):
    """Return (findings, skipped) for an arm, or None if the arm is absent.

    Absence is not emptiness. An earlier version returned an empty set for a missing arm, so omitting the
    control arm entirely passed every golden's must-not-report half.
    """
    v = report.get(arm)
    if not isinstance(v, dict):
        # Absent, the old bare-ID list, or any other shape: not gradeable. A wrongly-typed arm used to raise
        # AttributeError and exit 1, which is the same code as "your linter failed the goldens" - so a
        # harness fault was indistinguishable from a conformance failure.
        return None
    f = v.get("findings", [])
    sk = v.get("skipped", {})
    return ([x for x in f if isinstance(x, dict)] if isinstance(f, list) else [],
            sk if isinstance(sk, dict) else {})


def grade(report, verbose=True):
    goldens = load_goldens()
    scored = failures = skipped_ok = 0
    problems = []

    for name, g in goldens:
        checks = set(g["checks"])
        la = g["linter_assertion"]
        atk_arm, ctl_arm = la["must_report_on"]["arm"], la["must_not_report_on"]["arm"]
        if not checks:
            if verbose:
                print(f"  n/a    {name} — no MIRI-CLI check covers this; the gap is the finding")
            continue
        scored += 1

        atk, ctl = _arm(report, atk_arm), _arm(report, ctl_arm)
        if atk is None or ctl is None:
            failures += 1
            missing = [a for a, v in ((atk_arm, atk), (ctl_arm, ctl)) if v is None]
            if verbose:
                print(f"  FAIL   {name} — arm(s) absent or in the ungradeable bare-ID form: {missing}")
            continue
        atk_f, atk_s = atk
        ctl_f, ctl_s = ctl

        want_ev = set(la["must_report_on"].get("evidence") or [])
        may_skip = la.get("may_be_skipped_with")

        why = []
        for c in sorted(checks):
            # a skip is a declared, reasoned, arm-symmetric abstention - or it is a miss
            if c in atk_s:
                if not may_skip:
                    why.append(f"skipped {c}, which this golden does not permit skipping")
                elif atk_s[c] != may_skip:
                    why.append(f"skipped {c} with reason {atk_s[c]!r}, expected {may_skip!r}")
                elif atk_s.get(c) != ctl_s.get(c):
                    why.append(f"skipped {c} on {atk_arm} but not on {ctl_arm}; capability is a property "
                               f"of the linter, not of the artifact")
                else:
                    skipped_ok += 1
                continue
            hits = [f for f in atk_f if f.get("check") == c]
            if not hits:
                why.append(f"did not report {c} on {atk_arm}")
            elif want_ev and not any(f.get("evidence") in want_ev for f in hits):
                got = sorted({f.get("evidence") for f in hits})
                why.append(f"reported {c} but pointed at {got}, not {sorted(want_ev)}")

        false_pos = sorted({f.get("check") for f in ctl_f} & checks)
        if false_pos:
            why.append(f"reported {false_pos} on the CONFORMING arm {ctl_arm}")

        for c, r in sorted(atk_s.items()) + sorted(ctl_s.items()):
            if r not in SKIP_REASONS:
                problems.append(f"{name}: skip reason {r!r} for {c} is outside the closed set")

        if why:
            failures += 1
            if verbose:
                print(f"  FAIL   {name} — {'; '.join(why)}")
        elif verbose:
            print(f"  pass   {name}")

    for p in dict.fromkeys(problems):
        failures += 1
        if verbose:
            print(f"  FAIL   {p}")

    if verbose:
        print(f"\n  {scored - failures}/{scored} golden(s) satisfied"
              + (f", {skipped_ok} via a declared capability skip" if skipped_ok else ""))
    return failures, scored


def _honest():
    """A report a linter would produce if it actually detected each attack."""
    rep = {"adversarial-1.1.0": {"findings": [], "skipped": {}},
           "miri-1.1.0": {"findings": [], "skipped": {}}}
    for _, g in load_goldens():
        la = g["linter_assertion"]
        ev = (la["must_report_on"].get("evidence") or [None])[0]
        for c in g["checks"]:
            rep["adversarial-1.1.0"]["findings"].append({"check": c, "evidence": ev})
    return rep


def self_test():
    """Prove the harness rejects linters that game it, not just ones that say nothing.

    The cases below are the ones an adversarial panel used to defeat the previous version. A self-test whose
    only failing case is "reports nothing" proves almost nothing, because almost anything passes it.
    """
    honest = _honest()
    every = sorted({c for _, g in load_goldens() for c in g["checks"]})

    inert = {"adversarial-1.1.0": {"findings": [], "skipped": {}},
             "miri-1.1.0": {"findings": [], "skipped": {}}}
    shotgun = {"adversarial-1.1.0": {"findings": [{"check": c, "evidence": "identity.version"} for c in every],
                                     "skipped": {}},
               "miri-1.1.0": {"findings": [], "skipped": {}}}
    screaming = {a: {"findings": [{"check": c, "evidence": "identity.version"} for c in every], "skipped": {}}
                 for a in ("adversarial-1.1.0", "miri-1.1.0")}
    skip_everything = {"adversarial-1.1.0": {"findings": [], "skipped": {c: "previous_release_unavailable"
                                                                        for c in every}},
                       "miri-1.1.0": {"findings": [], "skipped": {c: "previous_release_unavailable"
                                                                 for c in every}}}
    no_control = {"adversarial-1.1.0": honest["adversarial-1.1.0"]}
    bare_ids = {"adversarial-1.1.0": every, "miri-1.1.0": []}
    # right checks, evidence rotated between goldens: detects nothing, attributes everything wrongly
    permuted = json.loads(json.dumps(honest))
    evs = [f["evidence"] for f in permuted["adversarial-1.1.0"]["findings"]]
    for f, e in zip(permuted["adversarial-1.1.0"]["findings"], evs[1:] + evs[:1]):
        f["evidence"] = e

    cases = [
        ("inert — reports nothing", inert, True),
        ("shotgun — every check ID on the hostile arm, one evidence", shotgun, True),
        ("screaming — everything on both arms", screaming, True),
        ("skip-everything — declared skips with a plausible reason", skip_everything, True),
        ("no control arm", no_control, True),
        ("bare-ID form — no evidence to attribute", bare_ids, True),
        ("permuted evidence — right checks, wrong reasons", permuted, True),
        ("honest — each attack detected and attributed", honest, False),
    ]
    print("self-test — the harness must reject every linter that games it:\n")
    ok = True
    for label, rep, want_fail in cases:
        f, n = grade(rep, verbose=False)
        good = (f > 0) if want_fail else (f == 0)
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'}  {label:56s} "
              f"{'rejected' if f else 'accepted'} ({f}/{n} failed)")
    print()
    if not ok:
        print("FAIL: the harness does not discriminate", file=sys.stderr)
        return 1
    print("the harness grades attribution: only a linter that names each check AND points at that attack's "
          "evidence passes")
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
    try:
        report = json.loads(pathlib.Path(a.report).read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read report: {e}", file=sys.stderr)
        return 2
    if not isinstance(report, dict):
        print("report must be a JSON object keyed by arm", file=sys.stderr)
        return 2
    failures, _ = grade(report)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
