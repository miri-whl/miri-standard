#!/usr/bin/env python3
"""Grade a linter against the greetlib wheel goldens, on attribution rather than on check IDs.

validate_python_fixtures.py keeps the fixtures honest. This is the other half: whether a linter
actually detects what they demonstrate. A finding satisfies a golden only if it names the right
check AND points at the evidence the golden declares - the right check ID for the wrong reason is
not detection, and a harness that accepts it cannot tell a linter from a lookup table.

Submission shape, per arm:

    {"skew-1.1.0":       {"findings": [{"check": "MIRI-PY-012", "evidence": "sdk-manifest.json sdk_version"}],
                          "skipped": {}},
     "conforming-1.1.0": {"findings": [], "skipped": {}}}

A conforming lint-report-v1 report is accepted directly: pass --reports with a directory holding one
report per arm, named <arm>.json. That became possible at 0.7.0, when lint-report-v1 gained an
`evidence` field on outcomes. Before it, a report recorded WHICH checks failed and nothing about what
each finding pointed at, so attribution could not be graded from a conforming report at all and both
golden harnesses invented a submission shape. A harness that needs a non-standard input is one most
implementations will not run, so the native path is the one to prefer.

    score_python_fixtures.py --reports reports/      # one lint-report-v1 per arm, <arm>.json
    score_python_fixtures.py --report submission.json
    score_python_fixtures.py --self-test             # prove the harness rejects linters that game it
"""
import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
GOLDENS = REPO / "examples/fixtures/python/expected"
SKIP_REASONS = {"network_unavailable", "previous_release_unavailable", "execution_disabled",
                "condition_not_applicable", "not_implemented"}


def load_goldens():
    return [(p.stem, json.loads(p.read_text())) for p in sorted(GOLDENS.glob("P*.json"))]


def from_lint_reports(directory: pathlib.Path) -> dict:
    """Fold one lint-report-v1 per arm into the submission shape this harness grades.

    The translation is mechanical and lossless for grading: an outcome's `evidence` array becomes one
    finding per evidence string, so a linter that names the check and points at the location satisfies
    a golden without anyone hand-writing a submission. An outcome that fails with no `evidence` yields
    a single finding with none, which fails any golden declaring evidence - correctly, since a check ID
    reported for an unstated reason is not attributable detection.
    """
    out = {}
    for f in sorted(directory.glob("*.json")):
        report = json.loads(f.read_text())
        findings, skipped = [], {}
        for o in report.get("outcomes", []):
            cid = o.get("id") or o.get("check_id")
            if o.get("status") == "fail":
                # `evidence` is the standard field. `violation_detail[].location` is accepted as a
                # fallback because it predates it and the reference implementation already emits the
                # right shape there for its best cases. This grades linters that exist rather than
                # only linters that have adopted 0.7.0 - and it costs nothing, since a location
                # naming the whole wheel fails a golden exactly as a missing one does.
                ev = list(o.get("evidence") or [])
                if not ev:
                    ev = [d.get("location") for d in (o.get("violation_detail") or [])
                          if isinstance(d, dict) and d.get("location")]
                for e in (ev or [None]):
                    findings.append({"check": cid, "evidence": e})
            elif o.get("status") == "skipped" and o.get("skip_reason"):
                skipped[cid] = o["skip_reason"]
        out[f.stem] = {"findings": findings, "skipped": skipped}
    return out


def _arm(report, arm):
    d = report.get(arm)
    if not isinstance(d, dict):
        return None
    findings = d.get("findings")
    if not isinstance(findings, list) or any(not isinstance(f, dict) for f in findings):
        return None                      # bare-ID form: ungradeable, not merely wrong
    return findings, (d.get("skipped") or {})


def grade(report, verbose=True):
    scored = failures = unreported_ok = 0
    problems = []

    for name, g in load_goldens():
        checks = set(g["checks"])
        la = g["linter_assertion"]
        atk_arm = la["must_report_on"]["arm"]
        ctl_arm = la["must_not_report_on"]["arm"]

        # A golden may record an obligation no implementation reports yet. It is still graded - a
        # linter that detects it should get credit - but a miss is reported as forfeited coverage
        # rather than as a failure, which is the standard's own rule for what it has not verified.
        aspirational = g.get("reported_by_any_implementation") is False

        arms = (_arm(report, atk_arm), _arm(report, ctl_arm))
        if any(a is None for a in arms):
            failures += 1
            missing = [a for a, v in ((atk_arm, arms[0]), (ctl_arm, arms[1])) if v is None]
            if verbose:
                print(f"  FAIL   {name} — arm(s) absent or in the ungradeable bare-ID form: {missing}")
            continue
        (atk_f, atk_s), (ctl_f, ctl_s) = arms
        # Evidence is keyed per check. It used to be one pooled set per golden, so a finding
        # satisfied check C by carrying ANY check's evidence - a shotgun submitting every check with
        # the union of evidence strings scored 6/6 while analysing nothing, and _honest() below had
        # the same bug, which is why the self-test could not catch it even in principle.
        want_by_check = la["must_report_on"].get("evidence") or {}
        if isinstance(want_by_check, list):      # pre-0.7 goldens: pooled. Refuse rather than guess.
            problems.append(f"{name}: evidence is a pooled list; goldens must key it per check")
            want_by_check = {}
        scored += 1
        why = []

        for c in sorted(checks):
            if c in atk_s:
                if atk_s[c] not in SKIP_REASONS:
                    problems.append(f"{name}: skip reason {atk_s[c]!r} for {c} is outside the closed set")
                elif atk_s.get(c) != ctl_s.get(c):
                    why.append(f"skipped {c} on {atk_arm} but not on {ctl_arm}; a capability is a property "
                               f"of the linter, not of the artifact")
                else:
                    why.append(f"skipped {c}, which this golden does not permit skipping")
                continue
            hits = [f for f in atk_f if f.get("check") == c]
            if not hits:
                why.append(f"did not report {c} on {atk_arm}")
            else:
                want = set(want_by_check.get(c) or [])
                if want and not any(f.get("evidence") in want for f in hits):
                    got = sorted({f.get("evidence") for f in hits})
                    why.append(f"reported {c} but pointed at {got}, not one of {sorted(want)}")

        false_pos = sorted({f.get("check") for f in ctl_f} & checks)
        if false_pos:
            why.append(f"reported {false_pos} on the CONFORMING arm {ctl_arm}")

        # The arm must report ONLY its own checks. Without this, a linter that fires every check from
        # every golden on every adversarial arm - while staying silent on the control - satisfies all
        # of them, because each check does carry its own correct evidence. It discriminates the
        # control from the rest and nothing else. The arms are minimal enough that their full failure
        # set is known and measured, so exactness is assertable; `also_expected` lets a golden declare
        # a check it trips that another golden owns, rather than the harness guessing.
        universe = {c for _, gg in load_goldens() for c in gg["checks"]}
        allowed = checks | set(g.get("also_expected") or [])
        stray = sorted({f.get("check") for f in atk_f} & (universe - allowed))
        if stray:
            why.append(f"reported {stray} on {atk_arm}, which this arm does not trip — an arm that "
                       f"reports every check discriminates nothing")

        if why and aspirational and not false_pos:
            unreported_ok += 1
            scored -= 1
            if verbose:
                print(f"  n/a    {name} — no implementation reports this yet; forfeited, not failed")
        elif why:
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
              + (f", {unreported_ok} forfeited as unimplemented" if unreported_ok else ""))
    return failures, scored


def _honest():
    """What a linter that actually detects each case would submit."""
    rep = {"conforming-1.1.0": {"findings": [], "skipped": {}}}
    # Seed every arm a golden names as its control, not just the default one. The SBOM cases pair
    # against `native-sbom-1.1.0` because MIRI-PY-024 is conditional on a native component and a
    # pure-Python control is EXCLUDED from it rather than passing it. Without this, the honest
    # submission was silent on an arm it was required to have analysed, and the harness rejected
    # its own reference answer — the ceiling failing, not the linter.
    for _, g in load_goldens():
        control = g["linter_assertion"].get("must_not_report_on", {}).get("arm")
        if control:
            rep.setdefault(control, {"findings": [], "skipped": {}})
    for name, g in load_goldens():
        la = g["linter_assertion"]["must_report_on"]
        arm = rep.setdefault(la["arm"], {"findings": [], "skipped": {}})
        by_check = la.get("evidence") or {}
        for c in g["checks"]:
            # Each check gets ITS OWN evidence. An earlier version handed every check in a case the
            # case's first evidence string, so the reference "perfect linter" attributed MIRI-PY-030
            # to a changelog `added` array - the harness's own ceiling was a misattribution.
            arm["findings"].append({"check": c, "evidence": (by_check.get(c) or [None])[0]})
    return rep


def self_test():
    """The harness must reject every linter that games it.

    Built the same way the CLI harness had to be rebuilt after a panel defeated it: the honest
    submission is derived FROM the goldens, so this proves the harness discriminates between
    shapes of answer, not that any real linter is correct. That limit is real and is stated rather
    than hidden - replicating this harness per family replicates the limit per family.
    """
    honest = _honest()
    all_checks = sorted({c for _, g in load_goldens() for c in g["checks"]})
    arms = sorted(honest)

    cases = {
        "inert — reports nothing at all":
            {a: {"findings": [], "skipped": {}} for a in arms},
        "shotgun — every check on every arm, control included":
            {a: {"findings": [{"check": c, "evidence": "x"} for c in all_checks], "skipped": {}} for a in arms},
        "screaming — right on the adversarial arms, also fires on the control":
            {**honest, "conforming-1.1.0": {
                "findings": [{"check": c, "evidence": "x"} for c in all_checks], "skipped": {}}},
        "skip-everything — declared reasons, no work":
            {a: {"findings": [], "skipped": {c: "execution_disabled" for c in all_checks}} for a in arms},
        "bare-ID — findings as strings, no evidence to attribute":
            {a: {"findings": [c for c in all_checks], "skipped": {}} for a in arms},
        "permuted evidence — right checks, wrong reasons":
            {a: {"findings": [{"check": f["check"], "evidence": "some other field"}
                              for f in d["findings"]], "skipped": {}} for a, d in honest.items()},
        # Both of these ACCEPTED under the pooled-evidence harness. They are the reason it changed.
        "shotgun carrying the union of every evidence string, silent on the control":
            {**{a: {"findings": [{"check": c, "evidence": e}
                                 for _, g in load_goldens() for c in g["checks"]
                                 for e in (g["linter_assertion"]["must_report_on"]["evidence"].get(c) or [])],
                    "skipped": {}} for a in arms if a != "conforming-1.1.0"},
             "conforming-1.1.0": {"findings": [], "skipped": {}}},
        "within-case permutation — each check blamed on another check's evidence":
            {**{la["arm"]: {"findings": [
                    {"check": c, "evidence": (la["evidence"].get(other) or [None])[0]}
                    for i, c in enumerate(g["checks"])
                    for other in [g["checks"][(i + 1) % len(g["checks"])]]],
                 "skipped": {}}
                for _, g in load_goldens() if len(g["checks"]) > 1
                for la in [g["linter_assertion"]["must_report_on"]]},
             "conforming-1.1.0": {"findings": [], "skipped": {}}},
        "invented skip reason — outside the closed set":
            {**honest, "skew-1.1.0": {"findings": [], "skipped": {"MIRI-PY-012": "too_hard",
                                                                  "MIRI-PY-019": "too_hard"}}},
    }

    print("self-test — the harness must reject every linter that games it:\n")
    bad = 0
    for label, rep in cases.items():
        f, s = grade(rep, verbose=False)
        ok = f > 0
        bad += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {label:58s} {'rejected' if f else 'ACCEPTED'} ({f}/{s} failed)")
    f, s = grade(honest, verbose=False)
    ok = f == 0
    bad += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  {'honest — each case detected and attributed':58s} "
          f"{'accepted' if ok else 'REJECTED'} ({f}/{s} failed)")
    print(f"\n  {'the harness grades attribution: only a linter that names each check AND points at that '
                'case’s evidence passes' if not bad else str(bad) + ' self-test case(s) wrong'}")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=pathlib.Path, help="a linter submission to grade")
    ap.add_argument("--reports", type=pathlib.Path,
                    help="a directory of lint-report-v1 reports, one per arm, named <arm>.json")
    ap.add_argument("--self-test", action="store_true", help="prove the harness discriminates")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.reports:
        failures, scored = grade(from_lint_reports(args.reports))
        return 1 if failures else 0
    if not args.report:
        ap.error("one of --reports, --report or --self-test is required")
    failures, scored = grade(json.loads(args.report.read_text()))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
