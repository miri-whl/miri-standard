#!/usr/bin/env python3
"""The fixture suites as one release asset.

The definitions wheel ships the rules for four check families. It does not ship anything to run them
against, so a vendor installing from releases could read every rule and exercise only the ones their
own corpus happened to cover — miri-py reported vendoring all four families' rules and being able to
run two. Rules without material are a reading exercise.

What goes in: the inputs and the goldens, never a build tree. The suites are *recipes* — each builds
its artifacts from one template and then asserts byte-identity across the variants — so shipping the
built wheels would ship the one thing the suites are designed to derive. The pack carries the
templates, the per-arm metadata, the goldens, the build scripts, and the validators that gate them,
which is exactly what `make check` runs here.
"""
import gzip
import hashlib
import io
import json
import pathlib
import sys
import tarfile

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / ".generated/fixture-pack"

# Build trees are outputs of the recipes in this pack, and __pycache__ is an artifact of running them.
SKIP_DIRS = {"build", "__pycache__", ".pytest_cache"}

# The validators and graders, so the pack can be checked and used without cloning the repository.
TOOLS = [
    "tools/checks_source.py",
    "tools/validate_fixtures.py",
    "tools/validate_cli_fixtures.py",
    "tools/validate_python_fixtures.py",
    "tools/score_cli_linter.py",
    "tools/score_python_fixtures.py",
]

README = """# Miri Standard fixture pack {version}

The three fixture suites, as shipped. Built by `tools/build_fixture_pack.py` from
{repo} at commit `{commit}`.

| Suite | Artifact | Arms | Goldens | Drives |
|---|---|---|---|---|
| `examples/fixtures/` | `greet` wheels | 11 | 22 | a consumer — `MIRI-CONSUMER`, `MIRI-SURFACE` |
| `examples/fixtures/cli/` | `greetctl` | 4 | 11 | a CLI linter — `MIRI-CLI` |
| `examples/fixtures/python/` | `greetlib` wheels | 9 | 7 | a wheel linter — `MIRI-PY` |

## Prerequisites

```bash
pip install build pyyaml jsonschema
pip install --index-url https://miri-whl.github.io/simple/ miri-standard-checks
```

`build` materializes the wheel and CLI arms; `miri-standard-checks` carries the check definitions and
schemas the validators resolve against, which this pack deliberately does not duplicate.

These are recipes, not built artifacts. Each suite materializes its arms from one template and then
verifies every `.py` is byte-identical across the source-sharing variants, so a difference in a
tool's behavior is attributable to metadata and nothing else. Build and check them:

```bash
python3 examples/fixtures/build_fixtures.py         && python3 tools/validate_fixtures.py
python3 examples/fixtures/cli/build_cli_fixtures.py && python3 tools/validate_cli_fixtures.py
python3 examples/fixtures/python/build_python_fixtures.py && python3 tools/validate_python_fixtures.py
```

Then grade a linter against the goldens on attribution — a finding counts only if it names the right
check *and* points at the declared evidence:

```bash
python3 tools/score_python_fixtures.py --reports <dir of lint-report-v1 documents>
python3 tools/score_cli_linter.py --reports <dir of lint-report-v1 documents>
```

Both graders carry a `--self-test` that rejects every way of gaming them found so far. Run it first:
a grader you have not tried to cheat is a grader you do not know the strength of.

## What this pack does not carry

**Check definitions.** They ship in `miri-standard-checks`, and two copies of a definition is two
sources of truth. The CLI and Python validators resolve them from the installed wheel when they are
not run inside a checkout, so install it alongside:

```bash
pip install --index-url https://miri-whl.github.io/simple/ miri-standard-checks
```

**The specifications.** `tools/validate_fixtures.py` asserts the consumption fixtures against prose
in `standards/consumption/` — the profile tables and the conformance sections — so it runs inside a
checkout and not from this pack. The consumption fixtures and goldens themselves are here and are
what you drive a consumer against; it is their *validator* that needs the specs.

`MANIFEST.json` pins the commit and a content digest over every file in this pack, computed the same
way as the definitions wheel's: sha256 over each (path, content) pair in ascending path order, each
prefixed by its 8-byte big-endian length, paths UTF-8 with `/` separators.
"""


def collect() -> dict:
    files = {}
    for base in [REPO / "examples/fixtures"]:
        for f in sorted(base.rglob("*")):
            if not f.is_file() or SKIP_DIRS & set(f.relative_to(REPO).parts):
                continue
            files[f.relative_to(REPO).as_posix()] = f.read_bytes()
    for rel in TOOLS:
        files[rel] = (REPO / rel).read_bytes()
    return files


def digest(mapping: dict) -> str:
    """Identical to the definitions wheel's content_sha256. One algorithm, stated once."""
    h = hashlib.sha256()
    for rel in sorted(mapping):
        key = rel.encode()
        h.update(len(key).to_bytes(8, "big")); h.update(key)
        h.update(len(mapping[rel]).to_bytes(8, "big")); h.update(mapping[rel])
    return h.hexdigest()


def main() -> int:
    sys.path.insert(0, str(REPO / "tools"))
    from build_checks_wheel import declared_version, git  # one source for both

    version, commit = declared_version(), git("rev-parse", "HEAD")
    files = collect()
    manifest = {
        "schema_version": "1",
        "distribution": "miri-standard-fixtures",
        "version": version,
        "standard_version": version,
        "checks_commit_sha": commit,
        "content_sha256": digest(files),
        "content_sha256_covers": (
            "every file in this pack except MANIFEST.json itself; sha256 over each (path, content) "
            "pair in ascending path order, each prefixed by its 8-byte big-endian length, paths "
            "UTF-8 with / separators — the same algorithm as the definitions wheel"),
        # Goldens, not every file in expected/: the consumption suite keeps cap.json, cursor.json and
        # requests.json there as calibration data, and counting them would publish 25 where 22 is the
        # number a reader checks by listing the cases.
        "goldens": {
            "consumption": len([f for f in (REPO / "examples/fixtures/expected").glob("*.json")
                                if f.name[0] in "AE" and f.name[1].isdigit()]),
            "cli": len([f for f in (REPO / "examples/fixtures/cli/expected").glob("*.json")
                        if f.name.startswith("C") and f.name[1].isdigit()]),
            "python": len([f for f in (REPO / "examples/fixtures/python/expected").glob("*.json")
                           if f.name.startswith("P") and f.name[1].isdigit()]),
        },
        "source": "https://github.com/miri-whl/miri-standard",
    }
    files["MANIFEST.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    files["README.md"] = README.format(
        version=version, commit=commit, repo=manifest["source"]).encode()

    OUT.mkdir(parents=True, exist_ok=True)
    name = f"miri-standard-fixtures-{version}.tar.gz"
    out = OUT / name
    # Fixed metadata: a pack of one tree must not differ because it was built on a different minute
    # or by a different user. The digest above already covers content; this makes the bytes stable.
    # gzip stamps the wall clock into its header, so two builds of one tree produced two different
    # sha256 values while the content digest agreed - the same defect the wheel has and the reason its
    # index hash has to come from the release rather than a rebuild. Here it is one argument, so it is
    # fixed rather than documented: mtime=0 and an empty stored filename make the bytes a property of
    # the tree. Verified by building twice and comparing.
    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=raw, mtime=0) as gz:
      with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for rel in sorted(files):
            info = tarfile.TarInfo(f"miri-standard-fixtures-{version}/{rel}")
            info.size = len(files[rel])
            info.mtime = 0
            info.mode = 0o755 if rel.endswith(".py") else 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(files[rel]))
    out.write_bytes(raw.getvalue())
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    (OUT / "SHA256SUMS").write_text(f"{sha}  {name}\n")
    print(f"built {name}")
    print(f"  {len(files)} files | content {manifest['content_sha256'][:12]} | "
          f"goldens {manifest['goldens']}")
    print(f"  sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
