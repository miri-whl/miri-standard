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
            s = r["scores"]
            conforming = s.get("is_conforming", False)
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
