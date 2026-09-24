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
  native-sbom-1.1.0      bundles a shared library AND covers it in an SBOM   (024 control)
  native-nosbom-1.1.0    bundles a shared library, ships no sboms/           (024)
  native-mismatch-1.1.0  an SBOM covering a library the wheel does not carry (024)
  native-badpurl-1.1.0   a covering SBOM whose component purl does not parse (025)

Each arm is built into a real wheel because `miri score` takes a wheel, not a source tree: the
checks read dist-info, RECORD and the installed layout, none of which exist before the build.
"""
import base64
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import zipfile

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
greetlib = ["agent-metadata/*.json", "examples/*.py", "docs/*.md"{native_data}]
'''

# A stub, not a real shared library. MIRI-PY-024 fires on the PRESENCE of a native component in
# the file inventory - `.so`/`.pyd`/`.dylib` or an auditwheel-style libs directory - and never
# loads it, so compiling one would add a toolchain dependency to the fixture suite and prove
# nothing the stub does not. It carries the ELF magic so a scanner sniffing bytes rather than
# reading extensions also classifies it, and says what it is so nobody mistakes it for a build
# product.
NATIVE_STUB = (b"\x7fELF" + bytes(12)
               + b"greetlib fixture stub - not a real shared object\n")


# CycloneDX, because MIRI-PY-024's remediation names CycloneDX or SPDX and PEP 770 puts either
# at `.dist-info/sboms/`. The bundled library is fictional - `libgreet` at a version no registry
# carries - so no purl here can ever join against a real advisory.
def sbom(component: str, purl: str) -> dict:
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {"component": {"type": "library", "name": "greetlib",
                                   "purl": "pkg:pypi/greetlib@1.1.0"}},
        "components": [{"type": "library", "name": component, "version": "2.1.0",
                        "purl": purl}],
    }



def inject_sboms(wheel: pathlib.Path, mode: str) -> str:
    """Write `.dist-info/sboms/` into a built wheel, the way PEP 770 places it.

    It has to happen here rather than as package data: `.dist-info/` does not exist until the
    backend writes it, and PEP 770 puts SBOM documents inside it precisely so scanners find them
    without a package-specific pointer. Putting them in the package instead would produce an arm
    that no conforming linter looks at - a fixture that cannot fail is worse than no fixture.

    The `unlisted` mode deliberately does NOT add a RECORD line, which is MIRI-PY-024's third
    clause and also makes the wheel fail MIRI-PY-001. Two checks on one arm is normally bad
    attribution; here it is the point, because a file smuggled past RECORD is exactly how a
    component inventory gets into a wheel the manifest does not account for.
    """
    if mode == "missing":
        return "no sboms/ - the defect"
    documents = {
        # The library this wheel actually bundles, with a parseable purl: the control.
        "covering": ("libgreet", "pkg:generic/libgreet@2.1.0"),
        # A library the wheel does not carry. The directory exists, the document validates, and it
        # covers nothing in the file inventory - the shape a linter that checks for a directory
        # rather than for coverage will pass.
        "mismatched": ("libssl", "pkg:generic/libssl@3.1.3"),
        # Right library, purl missing its type: `pkg:` with no type does not parse.
        "bad-purl": ("libgreet", "pkg:@2.1.0"),
        "unlisted": ("libgreet", "pkg:generic/libgreet@2.1.0"),
    }[mode]
    payload = (json.dumps(sbom(*documents), indent=2) + "\n").encode()

    with zipfile.ZipFile(wheel) as z:
        items = {n: z.read(n) for n in z.namelist()}
    dist_info = next(n.split("/")[0] for n in items if n.endswith(".dist-info/RECORD"))
    target = f"{dist_info}/sboms/greetlib.cdx.json"
    items[target] = payload

    record = f"{dist_info}/RECORD"
    if mode != "unlisted":
        digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode()
        lines = items[record].decode().splitlines()
        lines.insert(-1, f"{target},sha256={digest},{len(payload)}")
        items[record] = ("\n".join(lines) + "\n").encode()

    fixed = (1980, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(wheel, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(items):
            info = zipfile.ZipInfo(name, date_time=fixed)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, items[name])
    return f"sboms/ covers {documents[0]}" + ("" if mode != "unlisted" else ", unlisted in RECORD")


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
            (root / "pyproject.toml").write_text(
                PYPROJECT.format(version=version, arm=arm, native_data=""))
            digests[arm] = hashlib.sha256((pkg / "__init__.py").read_bytes()).hexdigest()
            print(f"  {arm:24s} v{version:<7} 0 document(s)   [ships no agent-metadata/ by design]")
            continue

        # Native components. The `.so` in the package and the one under `libs/` are what make
        # MIRI-PY-024 APPLICABLE at all: it is conditional, so a pure-Python arm is excluded from
        # both sides of the ratio rather than passing. That is the property the control arms prove
        # and the reason a fixture for a conditional check needs both kinds of arm.
        # MIRI-PY-014 is TIERED and its conformance_tier is T1: a thin example earns less weight and
        # still conforms, while an example NAMING A SYMBOL THE PACKAGE DOES NOT HAVE fails T1 and is
        # a MUST failure. That distinction is the whole point of the tier model - "the MUST boundary
        # sits at the lie, not at thinness" - and no arm demonstrated it, so the boundary was a
        # sentence in a schema rather than a property of an artifact. This arm is the lie; the
        # conforming arms are the thin-but-honest control, unchanged.
        if json.loads((arm_dir / "_arm.json").read_text()).get("example_lies"):
            (pkg / "examples" / "quickstart.py").write_text(
                '"""Install to first result, in four lines."""\n'
                "import greetlib\n\n"
                'print(greetlib.greet("world"))\n'
                "# `shout` appears in no api_index of any release. py_compile still succeeds and the\n"
                "# import still resolves; only the T1 clause catches it.\n"
                'print(greetlib.shout("world"))\n')

        native = json.loads((arm_dir / "_arm.json").read_text()).get("native")
        native_data = ""
        if native:
            (pkg / "_speedups.abi3.so").write_bytes(NATIVE_STUB)
            (pkg / "libs").mkdir()
            (pkg / "libs" / "libgreet-2.1.so").write_bytes(NATIVE_STUB)
            native_data = ', "*.so", "libs/*.so"'

        meta = pkg / "agent-metadata"
        meta.mkdir()
        for doc in sorted(arm_dir.glob("*.json")):
            if doc.name == "_arm.json":
                continue
            d = json.loads(doc.read_text())
            if not stamps_frozen and "generated_at" in d:
                d["generated_at"] = now
            (meta / doc.name).write_text(json.dumps(d, indent=2) + "\n")

        (root / "pyproject.toml").write_text(
            PYPROJECT.format(version=version, arm=arm, native_data=native_data))
        if not source_differs:
            digests[arm] = hashlib.sha256((pkg / "__init__.py").read_bytes()).hexdigest()

        n = len(list(meta.glob("*.json")))
        note = ""
        if source_differs:
            note = "   [source differs by design: the removal is real]"
        elif native:
            note = f"   [bundles a shared library; sboms: {native['sboms']}]"
        print(f"  {arm:24s} v{version:<7} {n} document(s){note}")

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
    # Named prerequisite, not a traceback 600 characters deep. Run from the fixture pack rather than a
    # checkout, `build` is frequently absent, and the failure arrived as "No module named build" from
    # a subprocess after eight arms had already been materialized - work that looked like progress.
    try:
        import build  # noqa: F401
    except ImportError:
        print("    needs the PyPA build frontend: pip install build", file=sys.stderr)
        return 1
    for arm_dir in arms:
        root = BUILD / arm_dir.name
        r = subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir",
                            str(root / "dist"), str(root)], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    {arm_dir.name}: build failed\n{r.stdout[-600:]}{r.stderr[-600:]}", file=sys.stderr)
            return 1
        whl = next((root / "dist").glob("*.whl"))
        native = json.loads((arm_dir / "_arm.json").read_text()).get("native")
        extra = f"  [{inject_sboms(whl, native['sboms'])}]" if native else ""
        print(f"    {arm_dir.name:24s} -> {whl.name}{extra}")
    return 0


def main() -> int:
    print("greetlib wheel fixtures:")
    return build(build_wheels="--no-wheels" not in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
