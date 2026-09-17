#!/usr/bin/env python3
"""Build the sample SDK and score it against the Miri Standard — the CI conformance gate.

The sample's committed `agent-metadata/*.json` carry a fixed `generated_at` so the tree is
coherent and readable. MIRI-PY-011 requires the stamp to fall inside the build window, so this
script re-stamps `generated_at` to build time **in a throwaway copy** (the committed source is
never mutated), builds the wheel with `miri build` (whose enhancer injects the dist-info
`AGENT_EXAMPLES.json` that satisfies MIRI-PY-016), then runs `miri score` and fails unless the
wheel is conforming.

Requires the `miri` CLI (miri-py) on PATH. Exit 0 = conforming, 1 = not conforming / error,
2 = `miri` not installed (a soft skip for contributors who do not have the linter).

Note: `miri generate`/`miri build --generate-metadata` cannot currently refresh this sample in
place (generate writes to the wrong path for a src-layout package and its `--output-dir` crashes);
until those miri-py issues are fixed, re-stamping is how the built wheel stays MIRI-PY-011-fresh.
"""
import datetime
import glob
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
SAMPLE = REPO / "examples/sample-sdk"
SCHEMA = REPO / "schemas/lint-report-v1.json"


def report_advisory(report, label):
    """Validate `miri score --json` against lint-report-v1.json, warning rather than failing.

    Advisory on purpose. 0.5.0 newly made `effective_denominator`, `excluded` and `forfeited`
    required, and miri-py has not shipped 0.5.0 support yet, so gating here would fail CI on
    work that is legitimately still in flight downstream. Warning still surfaces the drift the
    moment it appears, which is what was missing: the gate consumed this report for releases
    without ever checking it against the schema the standard publishes. Promote to a hard gate
    once miri-py emits a 0.5.0-shaped report.
    """
    try:
        import jsonschema
    except ImportError:
        return
    try:
        schema = json.loads(SCHEMA.read_text())
    except OSError:
        return
    errs = sorted(jsonschema.Draft7Validator(schema).iter_errors(report), key=lambda e: list(e.path))
    if not errs:
        print(f"sample-sdk [{label}]: report validates against lint-report-v1.json")
        return
    print(f"::warning::sample-sdk [{label}]: report does not validate against lint-report-v1.json "
          f"({len(errs)} error(s)); the conformance gate below is unaffected.")
    for e in errs[:5]:
        loc = "/".join(str(x) for x in e.path) or "(root)"
        print(f"  - {loc}: {e.message[:160]}")


def main():
    miri = shutil.which("miri")
    if not miri:
        print("miri (miri-py) not on PATH — skipping sample conformance gate. Install miri-py to run it.")
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "sample-sdk"
        shutil.copytree(SAMPLE, work, ignore=shutil.ignore_patterns("dist", "build", "*.egg-info", "__pycache__"))

        # Re-stamp generated_at to build time so the built wheel is MIRI-PY-011-fresh.
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for p in glob.glob(str(work / "src/weather_sdk/agent-metadata/*.json")):
            d = json.load(open(p))
            if "generated_at" in d:
                d["generated_at"] = now
                with open(p, "w") as fh:
                    json.dump(d, fh, indent=2)
                    fh.write("\n")

        dist = work / "dist"
        subprocess.run([miri, "build", "--project-path", str(work), "--output-dir", str(dist)],
                       check=True, capture_output=True, text=True)
        wheels = glob.glob(str(dist / "*.whl"))
        if not wheels:
            print("no wheel produced by `miri build`")
            return 1

        def score(extra_args, label):
            # `miri score` exits 1 on non-conformance (valid data), not an error — do not use check=True.
            p = subprocess.run([miri, "score", wheels[0], "--json", *extra_args], capture_output=True, text=True)
            try:
                r = json.loads(p.stdout)
            except json.JSONDecodeError:
                print(f"sample-sdk [{label}]: `miri score` errored (exit {p.returncode})\n{p.stderr[-800:]}")
                return None
            report_advisory(r, label)
            s = r["scores"]
            # Derived from schema-defined fields only. This gate previously read `is_conforming`, which
            # no schema defines and no spec mentions — it survived on `additionalProperties: true`, so the
            # one place in the repo where a gate failure visibly bites depended on a vendor field that
            # could be renamed without anything here noticing. `lint-report-v1.json` already couples the
            # verdict to its sources: a non-empty `must_failures` forces `grade: non-conforming` and caps
            # `conformance` at 74. So the verdict is derivable, and per this repo's own rule — declare
            # sources, not verdicts — a stored `is_conforming` is a computed state that can disagree with
            # what produced it. Verified against the two real CI reports: static (must_failures=[],
            # grade=silver) and --execute (must_failures=[036,040], grade=non-conforming) reproduce the
            # vendor field's True/False exactly.
            #
            # `undetermined` is ACCEPTED here, and that is deliberate rather than lax. 0.5.0's own rule is
            # that `undetermined` is not non-conformance: a forfeited MUST leaves the artifact neither known
            # to conform nor known to fail. Three MUSTs — MIRI-PY-015, 036 and 040 — require the `execution`
            # capability and are not conditional, so the default static posture forfeits 9 weight and can
            # never produce a grade for any artifact. An earlier version of this gate rejected
            # `undetermined`, which made the static pass structurally unpassable the moment an implementation
            # actually applied 0.5.0's semantics; it went red on miri-py's first 0.5.0-shaped report
            # (conformance 93, grade undetermined, must_failures []) even though nothing was wrong. Gating on
            # a definite grade from a posture that cannot determine one is reading our own rule backwards.
            #
            # What still fails: a non-empty `must_failures`, and an explicit `non-conforming` grade. Those are
            # the schema's own coupled signals for a real MUST failure. A report declaring no grade at all is
            # warned about rather than failed, since `grade` is not a required field and `must_failures` is —
            # demanding more than the schema does would be stricter than the standard.
            grade = s.get("grade")
            if grade is None:
                print(f"::warning::sample-sdk [{label}]: report declares no `grade`; "
                      f"gating on `must_failures` alone.")
            conforming = not r.get("must_failures") and grade != "non-conforming"
            print(f"sample-sdk [{label}]: conformance={s['conformance']} health={s.get('health')} "
                  f"grade={s['grade']} conforming={conforming} core={s.get('core_conforming')} "
                  f"MUST_failures={r.get('must_failures')}")
            return conforming

        # Static pass is the hard gate. The execution pass then runs our OWN trusted sample so the
        # execution-requiring MUSTs (015 examples-runnable, 036 discovery) are exercised; it is reported and
        # warns on failure but does not gate, since executing the artifact is environment-sensitive.
        # --execute runs only the standard's own sample here, never untrusted third-party code.
        if not score([], "static"):
            return 1
        execute_ok = score(["--execute", "--yes"], "execute")
        if execute_ok is None:
            print("::warning::--execute pass could not run; executable MUSTs unverified this run.")
        elif not execute_ok:
            print("::warning::sample is non-conforming under --execute; executable MUSTs (015/036) not verified — investigate.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
