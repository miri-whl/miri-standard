#!/usr/bin/env python3
"""Assert the greetlib wheel fixtures still demonstrate what their goldens claim.

The MIRI-PY family had 43 checks, 100 weight and no artifact that falsified any of them. These
fixtures are that artifact. This validator is what keeps them honest: a fixture whose defect has been
accidentally repaired is worse than no fixture, because the suite still reports green.

It checks three things without needing a linter installed:

  1. Every golden names checks that exist and are active.
  2. Every arm still carries its defect, asserted against the built wheel's own metadata rather than
     against a linter's opinion of it - so this gate holds even when no linter is available.
  3. The conforming control does NOT carry any of them, which is what makes a linter's report on an
     adversarial arm attributable to the defect rather than to the package.

Run tools/score_python_fixtures.py for the other half: grading a linter against the goldens.
"""
import json
import pathlib
import re
import sys
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from checks_source import checks_dir  # noqa: E402 — after sys.path is set

REPO = pathlib.Path(__file__).resolve().parent.parent
FIX = REPO / "examples/fixtures/python"
BUILD = FIX / "build"
DATA = FIX / "data"
CONTROL = "conforming-1.1.0"

failures = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global failures
    if not ok:
        failures += 1
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{(' — ' + detail) if (detail and not ok) else ''}")


def wheel_docs(arm: str) -> dict:
    """The agent-metadata documents inside an arm's built wheel, by file name."""
    whl = next((BUILD / arm / "dist").glob("*.whl"), None)
    if whl is None:
        return {}
    out = {}
    with zipfile.ZipFile(whl) as z:
        # Native components and SBOM state, read from the archive rather than from the arm's data
        # directory: `.dist-info/sboms/` does not exist until the backend writes dist-info, so the
        # only honest place to assert it is the built wheel.
        out["_native"] = [n for n in z.namelist() if n.endswith((".so", ".pyd", ".dylib"))]
        out["_sboms"] = [n for n in z.namelist() if "/sboms/" in n]
        out["_sbom_components"], out["_sbom_purls"] = [], []
        for n in out["_sboms"]:
            doc = json.loads(z.read(n))
            for c in doc.get("components", []):
                out["_sbom_components"].append(c.get("name", ""))
                out["_sbom_purls"].append(c.get("purl", ""))
        for n in z.namelist():
            if "/agent-metadata/" in n and n.endswith(".json"):
                out[n.rsplit("/", 1)[1]] = json.loads(z.read(n))
        out["_version"] = next(
            (line.split(": ", 1)[1].strip()
             for name in z.namelist() if name.endswith(".dist-info/METADATA")
             for line in z.read(name).decode().splitlines() if line.startswith("Version: ")), "")
    return out


# Each arm's defect, expressed against the artifact. Keyed to the golden that claims it.
def defects(arm: str, d: dict) -> dict[str, bool]:
    man, life = d.get("sdk-manifest.json", {}), d.get("lifecycle.json", {})
    use, chg = d.get("usage-patterns.json", {}), d.get("changelog.json", {})
    mig, ver = d.get("migration-guide.json"), d.get("_version", "")
    ident = life.get("identity", {})
    api = set(man.get("api_index", {}))
    return {
        "skew-1.1.0": {
            "sdk_version disagrees with the wheel": man.get("sdk_version") != ver,
            "purl version disagrees with the wheel": not str(ident.get("purl", "")).endswith("@" + ver),
        },
        "vacuous-1.1.0": {
            "api_index is empty": api == set(),
            "patterns is empty": use.get("patterns") == [],
        },
        "silent-removal-1.1.0": {
            "farewell is gone from api_index": "farewell" not in api,
            "no migration guide announces it": mig is None,
            "changelog names a symbol that resolves in neither release":
                any("farewell" in e.get("symbols", [])
                    for e in chg.get("releases", [{}])[0].get("added", [])),
        },
        "stale-1.1.0": {
            "stamps predate the build window": str(man.get("generated_at", "")).startswith("2021"),
            "newest changelog entry is not this release":
                chg.get("releases", [{}])[0].get("version") != ver,
        },
        "native-nosbom-1.1.0": {
            "bundles a native component": bool(d.get("_native")),
            "ships no .dist-info/sboms/": not d.get("_sboms"),
        },
        "native-mismatch-1.1.0": {
            "bundles a native component": bool(d.get("_native")),
            "ships an SBOM": bool(d.get("_sboms")),
            "its SBOM covers no bundled library":
                not any(c.lower() in " ".join(d.get("_native", [])).lower()
                        for c in d.get("_sbom_components", [])),
        },
        "native-badpurl-1.1.0": {
            "its SBOM covers a bundled library":
                any(c.lower() in " ".join(d.get("_native", [])).lower()
                    for c in d.get("_sbom_components", [])),
            "a component purl does not parse":
                any(not re.match(r"^pkg:[a-zA-Z][a-zA-Z0-9.+-]*/", u) for u in d.get("_sbom_purls", [])),
        },
        "native-sbom-1.1.0": {
            # The control for the three above: it must keep BOTH properties, or the pairing that
            # makes those findings attributable stops holding.
            "bundles a native component": bool(d.get("_native")),
            "its SBOM covers a bundled library":
                any(c.lower() in " ".join(d.get("_native", [])).lower()
                    for c in d.get("_sbom_components", [])),
        },
        "identity-1.1.0": {
            "registry is a project page, not an index": "/project/" in str(ident.get("registry", "")),
            "distribution claims private": ident.get("distribution") == "private",
            "advisory_sources is empty": life.get("advisory_sources") == [],
        },
        "empty-migration-1.1.0": {
            "a public symbol was really removed": "farewell" not in api,
            "the guide reports no deprecations": (mig or {}).get("deprecations") == [],
            "every summary count is zero":
                all(v == 0 for v in (mig or {}).get("summary", {}).values() if isinstance(v, int)),
        },
    }.get(arm, {})


def main() -> int:
    if not BUILD.exists():
        print("fixtures not built — run examples/fixtures/python/build_python_fixtures.py", file=sys.stderr)
        return 2

    print("greetlib wheel fixture invariants:")

    active = set()
    for f in checks_dir("python").glob("*.yaml"):
        text = f.read_text()
        if "status: active" in text:
            active.add(f.stem)

    goldens = sorted((FIX / "expected").glob("P*.json"))
    check("goldens present", bool(goldens), "expected/P*.json is empty")
    for g in goldens:
        d = json.loads(g.read_text())
        unknown = [c for c in d["checks"] if c not in active]
        check(f"golden {g.stem}: cites only active checks", not unknown, f"unknown: {unknown}")
        check(f"golden {g.stem}: declares evidence a finding must point at",
              bool(d["linter_assertion"]["must_report_on"]["evidence"]))
        # The paired control is not always `conforming-1.1.0`. MIRI-PY-024 is conditional on the
        # wheel carrying a native component, so a pure-Python control cannot pair with it: it does
        # not fail the check, it is excluded from it, and "excluded" is not the same evidence as
        # "passed". The SBOM cases therefore pair against an arm bundling the SAME library, which
        # is what makes the finding attributable to the SBOM rather than to the presence of a .so.
        pair = d.get("paired_control")
        check(f"golden {g.stem}: names a paired control", bool(pair))
        check(f"golden {g.stem}: its control is a real arm", (DATA / pair).is_dir() if pair else False,
              f"{pair} is not an arm")
        check(f"golden {g.stem}: its control is not the arm under test",
              pair != d["linter_assertion"]["must_report_on"]["arm"])

    control = wheel_docs(CONTROL)
    check(f"control {CONTROL} was built", bool(control))

    for arm in sorted(p.name for p in BUILD.iterdir() if p.is_dir()):
        d = wheel_docs(arm)
        for label, live in defects(arm, d).items():
            check(f"{arm}: {label}", live, "the fixture no longer demonstrates its own case")

    # The control must carry NONE of the defects, or a finding on an adversarial arm proves nothing.
    for arm in sorted(defects_arm for defects_arm in
                      ("skew-1.1.0", "vacuous-1.1.0", "stale-1.1.0", "identity-1.1.0")):
        for label, live in defects(arm, control).items():
            check(f"control does not carry [{arm}] {label}", not live,
                  "the control shares the defect — a finding would not be attributable")

    print(f"\n  {'all greetlib fixture invariants hold' if not failures else str(failures) + ' invariant(s) broken'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
