#!/usr/bin/env python3
"""Build the check definitions as a data-only wheel: `miri-standard-checks`.

The repository stays the source of truth. This script STAGES a copy of `standards/*/checks/*.yaml` and
`schemas/*.json` into `.generated/checks-wheel/` at build time, writes a manifest that pins the commit and a
content hash, and builds a wheel from the staging tree. Nothing is hand-maintained inside the package; a
wheel that differs from the tree it was built from is a build bug, not a second edition.

Why a wheel: `main` moves and scores must not. A linter that vendors definitions by commit works, but every
downstream re-implements the pin. A versioned artifact gives teams one definition to `pip install`, and the
manifest gives their reports the `checks_commit_sha` lint-report-v1 requires - a full 40-character sha, never
a tag, because a tag is a movable label and the point of the field is that a reader can fetch the exact
definitions a score was computed against.

Version: the standard's release from website/site.yaml (the single declared version). Built exactly at a
release tag, that is the version; built anywhere else it becomes `<version>.dev0+g<sha>`, a PEP 440 local
version that cannot be mistaken for a release and cannot be uploaded to an index by accident.

Content hash: sha256 over every staged file's relative path and bytes, in sorted order - the same shape
miri-py's sync_checks.py computes, so a consumer can confirm the wheel it installed is the tree it names.
"""
import base64
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / ".generated/checks-wheel"
PKG = "miri_standard_checks"
DIST_NAME = "miri-standard-checks"


INIT_PY = '''"""The Miri Standard check definitions and schemas, as installed data.

Data-only: no rules are implemented here, only carried. `root()` is the directory holding
`checks/<target>/*.yaml` and `schemas/*.json`; `manifest()` pins what was built — the release, the
full commit sha, and a content hash over every file — so a report can cite what it scored against.
"""
# No PEP 604 unions in signatures: `str | None` is evaluated at def time and raises TypeError on
# Python 3.9, which this package advertises as its floor. The wheel installed cleanly on 3.9 and
# died on first import - a false Requires-Python is worse than a high one, because pip resolves it.
import hashlib
import json
import pathlib

__all__ = ["root", "manifest", "checks", "schema", "content_digest", "verify_content",
           "checklist_version", "families"]


def root() -> pathlib.Path:
    """Directory holding the installed definitions and schemas."""
    return pathlib.Path(__file__).resolve().parent


def _carried() -> dict:
    """Every file this package installs, except manifest.json, which carries the digest.

    `.dist-info/` is outside the package directory and already hashed entry-by-entry by RECORD;
    `__pycache__` appears only after import and is not part of what was installed.
    """
    base = root()
    out = {}
    for f in sorted(base.rglob("*")):
        rel = f.relative_to(base).as_posix()   # as_posix() IS the / spelling; no escaping games
        if f.is_file() and rel != "manifest.json" and "__pycache__" not in rel.split("/"):
            out[rel] = f.read_bytes()
    return out


def content_digest() -> str:
    """Recompute `manifest()["content_sha256"]` from the files on disk.

    The algorithm, stated once so it is never reconstructed from prose again: sha256 over each
    (path, content) pair in ascending path order, each of the two prefixed by its own 8-byte
    big-endian length; paths UTF-8 with "/" separators, relative to this directory.
    """
    h = hashlib.sha256()
    for rel, data in sorted(_carried().items()):
        key = rel.encode()
        h.update(len(key).to_bytes(8, "big")); h.update(key)
        h.update(len(data).to_bytes(8, "big")); h.update(data)
    return h.hexdigest()


def verify_content() -> bool:
    """True when the installed files still hash to what the manifest claims.

    What this does and does not prove: it detects a package edited after installation, and it is a
    self-consistency check, not provenance. An attacker who rewrites a file can rewrite manifest.json
    too. For provenance, verify the release's SHA256SUMS or the build attestation against the wheel.
    """
    return content_digest() == manifest()["content_sha256"]


def families() -> dict:
    """Every check family: its checklist revision, its directory here, and its id prefix.

    `checks/consumption/` carries two families on two separate 100-point scales, so a consumer that
    reads one directory per family sums 200 and fails a weight invariant with a message about
    arithmetic. Filter by `id_prefix` and check the totals against `weight_total` declared here.
    """
    return manifest()["families"]


def checklist_version(family: str) -> str:
    """The checklist revision a family implements, e.g. checklist_version("MIRI-PY") -> "0.3-draft".

    Not derivable from the definitions: max(added_in) gives the newest check's release, which is a
    different question and a different answer.
    """
    return manifest()["families"][family]["checklist_version"]


def manifest() -> dict:
    """What this package was built from: release, commit sha, content hash.

    Raises FileNotFoundError if the package is incomplete, and
    json.JSONDecodeError if the manifest is corrupt. Both are worth catching:
    an installed package that cannot say what it is should not be trusted to
    say what the rules are.
    """
    return json.loads((root() / "manifest.json").read_text())


def checks(target=None, family=None):
    """Paths of the check definitions, optionally for one target or one family.

    Filter by FAMILY, not by directory, when you mean a scoring family: `checks/consumption/` holds
    MIRI-SURFACE and MIRI-CONSUMER, each on its own 100-point scale, so a per-directory read sums 200.
    """
    paths = sorted(root().glob(f"checks/{target or '*'}/*.yaml"))
    if family:
        paths = [p for p in paths if p.stem.startswith(f"{family}-")]
    return paths


def schema(name: str) -> dict:
    """One JSON Schema by file name, e.g. "check-v3.json"."""
    return json.loads((root() / "schemas" / name).read_text())
'''

QUICKSTART = '''"""Read one check definition from the installed package — install to first result."""
import miri_standard_checks as msc

print("pinned to", msc.manifest()["checks_commit_sha"][:12])

paths = msc.checks("python")
print(f"{len(paths)} python check definitions")
print("first:", paths[0].name)
print(paths[0].read_text().splitlines()[2])  # the `id:` line
'''

ERROR_HANDLING = '''"""What to catch when the installed definitions are incomplete or corrupt."""
import json

import miri_standard_checks as msc

try:
    pin = msc.manifest()["checks_commit_sha"]
except FileNotFoundError:
    print("manifest.json is missing - the install is incomplete; reinstall the wheel")
except json.JSONDecodeError as exc:
    print(f"manifest.json is not valid JSON ({exc}); do not trust these definitions")
except KeyError:
    print("manifest.json carries no checks_commit_sha; it was not built by build_checks_wheel.py")
else:
    print("definitions pinned to", pin[:12])

try:
    msc.schema("check-v99.json")
except FileNotFoundError:
    print("no such schema - schema() takes a file name like check-v3.json")
'''


def write_agent_metadata(src: pathlib.Path, manifest: dict) -> None:
    """Write agent-metadata/, examples/ and docs/ into the staged package.

    Written against the specifications rather than generated by the reference implementation.
    That is deliberate: if `miri score` passes metadata authored from the spec text alone, it is
    evidence the spec is implementable from the text; if the generator had written it, a pass would
    only show the reference tool agreeing with itself. Every claim here is true of this package -
    the api_index names the four functions that exist, and the patterns are runnable.
    """
    stamp = manifest["generated_at"]
    version = manifest["version"]
    meta = src / "agent-metadata"
    meta.mkdir(parents=True, exist_ok=True)

    (meta / "lifecycle.json").write_text(json.dumps({
        "$schema": "https://miri-whl.github.io/schemas/lifecycle-v1.json",
        "miri_lifecycle_version": "0.1",
        "generated_at": stamp,
        "identity": {
            "purl": f"pkg:pypi/{DIST_NAME}@{version}",
            "distribution": "open-source",
            # A PEP 503 simple index published on the standard's own site by tools/generate_site.py.
            # MIRI-PY-020 rejects a project page, correctly - a registry a consumer cannot install
            # from is not a registry - and the earlier declaration here named the GitHub Releases page,
            # which their 0.6.0 linter caught. This is the honest fix rather than a PyPI URL we do not
            # publish to: `pip install --index-url https://miri-whl.github.io/simple/ miri-standard-checks`
            # resolves through it to the release asset.
            "registry": "https://miri-whl.github.io/simple/",
            "source_repository": "https://github.com/miri-whl/miri-standard",
        },
        "advisory_sources": [
            {"type": "osv", "ecosystem": "PyPI", "url": "https://api.osv.dev/v1/query"},
        ],
        # The PEP 700 project detail beside the simple index: `versions` is what a consumer polls to
        # learn a newer release exists. Not pypi-json, because this package is not on PyPI and saying
        # so would be a claim that fails the moment anyone follows it.
        "update_check": {"type": "pep700-index",
                         "url": f"https://miri-whl.github.io/simple/{DIST_NAME}/index.json"},
        "support": {
            "status": "active",
            "supported_versions": [">=0.6"],
            "security_policy": "https://github.com/miri-whl/miri-standard/security/policy",
        },
    }, indent=2) + "\n")

    (meta / "sdk-manifest.json").write_text(json.dumps({
        "$schema": "https://miri-whl.github.io/schemas/sdk-manifest-v1.json",
        "sdk_version": version,
        "generated_at": stamp,
        "miri_version": "1.0",
        "quick_reference": {
            "primary_classes": [],
            "key_methods": ["root", "manifest", "checks", "schema"],
            "common_imports": ["import miri_standard_checks"],
        },
        "api_index": {
            "root": {"type": "function", "purpose": "Directory holding the installed definitions and schemas",
                     "complexity": "beginner"},
            "manifest": {"type": "function", "purpose": "Release, commit sha and content hash this package was built from",
                         "complexity": "beginner"},
            "checks": {"type": "function", "purpose": "Paths of the check definitions, optionally for one target",
                       "complexity": "beginner"},
            "schema": {"type": "function", "purpose": "One JSON Schema by file name", "complexity": "beginner"},
        },
        "error_handling": {
            "FileNotFoundError": {
                "when": "manifest() is called on an incomplete install, or schema() is given a name no file carries",
                "common_causes": ["the wheel was partially extracted", "a schema file name was misspelled"],
                "solutions": ["reinstall the wheel", "list root()/'schemas' to see the names carried"]},
            "JSONDecodeError": {
                "when": "manifest.json or a schema file is corrupt",
                "common_causes": ["the install was truncated", "a carried file was edited after packaging"],
                "solutions": ["reinstall the wheel", "treat the definitions as untrusted until the pin verifies"]},
            "KeyError": {
                "when": "manifest() returns a mapping with no checks_commit_sha",
                "common_causes": ["the package was not built by tools/build_checks_wheel.py"],
                "solutions": ["install a released wheel from the GitHub Release for a tag"]},
        },
    }, indent=2) + "\n")

    (meta / "usage-patterns.json").write_text(json.dumps({
        "$schema": "https://miri-whl.github.io/schemas/usage-patterns-v1.json",
        "version": "1.0",
        "generated_at": stamp,
        "patterns": [
            {"id": "read_the_pin", "name": "Read the pin", "complexity": "beginner", "category": "provenance",
             "description": "Cite the exact definitions a score was computed against",
             "code": "import miri_standard_checks as msc\nsha = msc.manifest()['checks_commit_sha']"},
            {"id": "load_definitions", "name": "Load a family's definitions", "complexity": "beginner",
             "category": "definitions", "description": "Iterate the check YAML files for one target",
             "code": "import miri_standard_checks as msc\nfor p in msc.checks('python'):\n    text = p.read_text()"},
            {"id": "validate_against_schema", "name": "Validate a definition", "complexity": "intermediate",
             "category": "schemas", "description": "Check a definition against the schema it declares",
             "code": ("import jsonschema, yaml\nimport miri_standard_checks as msc\n"
                      "s = msc.schema('check-v3.json')\n"
                      "d = yaml.safe_load(msc.checks('python')[0].read_text())\n"
                      "jsonschema.validate(d, s)")},
        ],
        "categories": {
            "provenance": {"name": "Provenance", "description": "Citing the exact definitions a score was computed against",
                           "patterns": ["read_the_pin"]},
            "definitions": {"name": "Definitions", "description": "Reading the carried check definitions",
                            "patterns": ["load_definitions"]},
            "schemas": {"name": "Schemas", "description": "Validating a definition against the schema it declares",
                        "patterns": ["validate_against_schema"]},
        },
        "learning_paths": {
            "getting_started": {"name": "Getting started", "description": "Pin, read, then validate",
                                "patterns": ["read_the_pin", "load_definitions", "validate_against_schema"]},
        },
    }, indent=2) + "\n")

    # Section 4.7 makes changelog.json conditional on a previous release and lets a first release ship
    # it with its initial entry. Shipping it is the better choice: MIRI-PY-042 (version silence) is
    # conditional on the DOCUMENT being present, so shipping it puts our own newest freshness check
    # under test instead of leaving it excluded. releases[0].version is the wheel's own version, which
    # is what 042 compares.
    (meta / "changelog.json").write_text(json.dumps({
        "$schema": "https://miri-whl.github.io/schemas/changelog-v1.json",
        "schema_version": "1",
        "generated_at": stamp,
        "releases": [{
            "version": version,
            "added": [
                {"summary": "The check definitions and JSON Schemas as an installable data-only package",
                 "symbols": ["root", "manifest", "checks", "schema"]},
            ],
        }],
    }, indent=2) + "\n")

    ex = src / "examples"
    ex.mkdir(exist_ok=True)
    (ex / "quickstart.py").write_text(QUICKSTART)
    (ex / "error_handling.py").write_text(ERROR_HANDLING)
    # NOT written here: Miri Wheel Extensions section 3.2 puts AGENT_EXAMPLES.json in the
    # `.dist-info/` directory, beside METADATA and RECORD, not inside the import package. It is
    # injected into the built wheel by `inject_dist_info()` below, because a dist-info file cannot be
    # carried as package data. Writing it to the package root - which is what this build did first -
    # produces a file no consumer looks for; the linter's layout section says so in as many words.
    (src / "_agent_examples.json.src").write_text(json.dumps({
        "examples": {
            "quickstart": {"file": "examples/quickstart.py", "complexity": "beginner",
                           "description": "Read one check definition from the installed package"},
            "error_handling": {"file": "examples/error_handling.py", "complexity": "beginner",
                               "description": "What to catch when the install is incomplete or corrupt"},
        },
        "categories": {"getting_started": ["quickstart"], "reliability": ["error_handling"]},
        "learning_paths": {"first_use": ["quickstart", "error_handling"]},
    }, indent=2) + "\n")


    docs = src / "docs"
    docs.mkdir(exist_ok=True)
    worked = _digest({"a.txt": b"hi", "b/c.txt": b"x"})
    (docs / "api_reference.md").write_text(f"""# API reference

`miri_standard_checks` carries the Miri Standard's check definitions and JSON Schemas as installed
data. It implements no rules; it is the one definition teams read instead of cloning at a commit.

## `root() -> pathlib.Path`

The directory holding `checks/<target>/*.yaml` and `schemas/*.json`.

## `manifest() -> dict`

What this package was built from: `version`, `standard_version`, `checks_commit_sha` (the full
40-character commit, never a tag), `content_sha256` over every carried file, and the per-target
definition counts. Raises `FileNotFoundError` if the install is incomplete and
`json.JSONDecodeError` if the manifest is corrupt.

## `checks(target=None, family=None) -> list[pathlib.Path]`

Paths of the check definitions, sorted; `target` is one of `python`, `cli`, `consumption`, and
`family` one of `MIRI-PY`, `MIRI-CLI`, `MIRI-SURFACE`, `MIRI-CONSUMER`.

**Filter by family, not by directory, when you mean a scoring family.** `checks/consumption/` holds
MIRI-SURFACE and MIRI-CONSUMER, 18 checks each, each summing to 100 on its own scale — so reading
one directory per family sums 200 and trips a weight invariant with a message about arithmetic
rather than about layout.

## `families() -> dict`

One row per family: `checklist_version`, `governing_document`, `directory`, `id_prefix`,
`active_checks`, `weight_total`. The checklist revision is prose in this repository and is not
packaged, so this is where it travels. It is not `max(added_in)` over the definitions — that is the
newest check's release, a different question with a different answer.

## `checklist_version(family) -> str`

For example `checklist_version("MIRI-PY")` -> `"0.3-draft"`.

## `content_digest() -> str` and `verify_content() -> bool`

Recompute `manifest()["content_sha256"]` from the installed files, and compare it to what the
manifest claims. Call these rather than reimplementing the algorithm.

**The algorithm, and a worked example.** For each file installed under the package directory except
`manifest.json`, in ascending order of its path: feed the 8-byte big-endian path length, the path
(UTF-8, `/` separators, relative to the package root), the 8-byte big-endian content length, then
the content. `.dist-info/` is out of scope — RECORD already hashes it entry by entry — and so is
`__pycache__`, which appears only after import.

Over exactly two files, `a.txt` containing `hi` and `b/c.txt` containing `x`:

```text
sha256 of the concatenation of
  0000000000000005  "a.txt"    0000000000000002  "hi"
  0000000000000007  "b/c.txt"  0000000000000001  "x"
= {worked}
```

```python
import hashlib
files = {{"a.txt": b"hi", "b/c.txt": b"x"}}
h = hashlib.sha256()
for path in sorted(files):
    key = path.encode()
    h.update(len(key).to_bytes(8, "big")); h.update(key)
    h.update(len(files[path]).to_bytes(8, "big")); h.update(files[path])
print(h.hexdigest())
```

What this proves: the installed files have not been edited since installation. What it does not:
provenance. An attacker who rewrites a file can rewrite `manifest.json` too. For provenance, verify
the release's SHA256SUMS or the build attestation against the wheel.

## `schema(name) -> dict`

One JSON Schema by file name, for example `check-v3.json`. Raises `FileNotFoundError` for a name no
file carries.

Built from `{manifest["source"]}` at `{manifest["checks_commit_sha"]}`.
""")
    (docs / "troubleshooting.md").write_text("""# Troubleshooting

## `FileNotFoundError` from `manifest()`

The install is incomplete. Reinstall the wheel; do not fall back to definitions from another source,
because a score is only comparable when it cites the commit it was computed against.

## `json.JSONDecodeError` from `manifest()` or `schema()`

A carried file is corrupt. Treat the definitions as untrusted and reinstall: these files decide what
"conforming" means, so a package that cannot parse its own manifest cannot be relied on to carry
them faithfully.

## The definitions do not match what I expected

Compare `manifest()["checks_commit_sha"]` against the commit you meant to pin. Recompute
`content_sha256` over the carried files in sorted order to confirm the package is the tree it names.

## `KeyError` on `checks_commit_sha`

The manifest was not produced by `tools/build_checks_wheel.py`. An unpinned definitions package
should not be used to score anything.
""")


def _digest(mapping):
    """sha256 over LENGTH-PREFIXED (path, bytes) pairs in sorted order.

    For each path in ascending order of its UTF-8 bytes, feed: an 8-byte big-endian path length, the
    path (UTF-8, separators normalized to "/"), an 8-byte big-endian content length, the content.

    Length-prefixed rather than delimiter-framed: with NUL separators, {"a": b"x", "b": b"y"} and
    {"a": b"x\\0b\\0y"} hash identically. Not reachable through YAML or JSON, which cannot carry a
    NUL, but nothing enforced that and the fix is one line. Paths are normalized to "/" so a
    Windows build does not produce a different digest for an identical tree.

    Both lengths are 8 bytes. They were 4 and 8 - an asymmetry no reader guesses and the prose did
    not state, which is half of why miri-py could not reproduce this field from its own description
    in 36 attempts. A field a second implementation cannot recompute is decoration.
    """
    h = hashlib.sha256()
    for rel in sorted(mapping):
        key = rel.replace("\\", "/").encode()
        h.update(len(key).to_bytes(8, "big")); h.update(key)
        h.update(len(mapping[rel]).to_bytes(8, "big")); h.update(mapping[rel])
    return h.hexdigest()


# One row per check family: the document that governs it, the directory that holds it, and the id
# prefix that identifies it. Keyed by family rather than by target because `checks/consumption/` holds
# TWO families on TWO separate 100-point scales - a consumer reading one directory per family sums 200
# and fails a weight invariant with a message about arithmetic rather than about layout. The prefix was
# the only discriminator and had to be known out of band; declared here, it can be verified instead.
FAMILIES = {
    "MIRI-PY": ("python", "standards/python/linter-checklist.md"),
    "MIRI-CLI": ("cli", "standards/cli/linter-checklist.md"),
    "MIRI-SURFACE": ("consumption", "standards/consumption/surface-conformance.md"),
    "MIRI-CONSUMER": ("consumption", "standards/consumption/consumer-conformance.md"),
}


def families() -> dict:
    """What each family is, where it lives in this package, and which document revision it implements.

    A vendor installing the wheel alone could report "standard 0.7.0, checks at 41aa2682" and not which
    checklist revision those checks implement, where a vendor who clones could. The checklists are prose
    and are not packaged, so the revision travels here or nowhere. It is NOT max(added_in) over the
    definitions: that is the newest check's release, a different question with a different answer
    (0.6.0-draft where the python checklist says 0.3-draft).
    """
    out = {}
    for family, (target, doc) in FAMILIES.items():
        text = (REPO / doc).read_text()
        m = re.search(r"\*Specification Version: ([^*]+)\*", text)
        if not m:
            raise SystemExit(f"{doc}: no `*Specification Version: ...*` header to read")
        active = [c for c in _family_checks(target, family)]
        out[family] = {
            "checklist_version": m.group(1).strip(),
            "governing_document": doc,
            "directory": f"checks/{target}",
            "id_prefix": f"{family}-",
            "active_checks": len(active),
            "weight_total": sum(c.get("weight", 0) for c in active),
        }
    return out


def _family_checks(target: str, family: str) -> list:
    out = []
    for f in sorted((REPO / "standards" / target / "checks").glob("*.yaml")):
        d = yaml.safe_load(f.read_text())
        if d.get("status") == "active" and d["id"].startswith(f"{family}-"):
            out.append(d)
    return out


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True).stdout.strip()


def declared_version() -> str:
    for line in (REPO / "website/site.yaml").read_text().splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip()
    raise SystemExit("website/site.yaml declares no version")


def version() -> str:
    base = declared_version()
    sha = git("rev-parse", "HEAD")
    tag = subprocess.run(["git", "-C", str(REPO), "describe", "--tags", "--exact-match"],
                         capture_output=True, text=True).stdout.strip()
    if tag == base:
        return base
    return f"{base}.dev0+g{sha[:12]}"


def stage() -> tuple[pathlib.Path, dict]:
    if OUT.exists():
        shutil.rmtree(OUT)
    src = OUT / "src" / PKG
    files: dict[str, bytes] = {}
    for f in sorted(REPO.glob("standards/*/checks/*.yaml")):
        rel = pathlib.Path("checks") / f.parent.parent.name / f.name
        files[str(rel)] = f.read_bytes()
    for f in sorted((REPO / "schemas").glob("*.json")):
        files[str(pathlib.Path("schemas") / f.name)] = f.read_bytes()
    # Every carried file, not just the corpus. api_reference.md and __init__.py both state that
    # content_sha256 covers "every carried file", and hashing only checks/ and schemas/ left the
    # package's ONLY executable code outside the digest - poison __init__.py so that checks() omits
    # a definition and the hash still matched. The generated documents are added after this point,
    # so they are folded in by _finalize_digest() once written.
    for rel, data in files.items():
        p = src / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    counts: dict[str, int] = {}
    for rel in files:
        if rel.startswith("checks/"):
            counts[rel.split("/")[1]] = counts.get(rel.split("/")[1], 0) + 1
    # The commit date, not the wall clock: the same stamp SOURCE_DATE_EPOCH gives the wheel, so the
    # build stays byte-reproducible. MIRI-PY-011 allows a 24-hour build window, which a release build
    # at a tag satisfies comfortably. A rebuild of an old commit will fall outside it and fail 011 —
    # correctly, since the metadata would then be older than the artifact carrying it. Reproducibility
    # and build-window freshness pull against each other here, and freshness is the one the standard
    # can check, so the tension is real rather than resolved by picking a convenient stamp.
    stamp = datetime.datetime.fromtimestamp(
        int(git("log", "-1", "--format=%ct")), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = {
        "schema_version": "1",
        "generated_at": stamp,
        # Per target, because they differ - python is 0.3-draft and cli is 0.2-draft - and because the
        # obvious fallback answers a different question: max(added_in) over the definitions gives the
        # newest check's release (0.6.0-draft), not the checklist's own version. Read from the one
        # place each checklist states it, so this cannot drift from the prose it mirrors.
        "families": families(),
        "distribution": DIST_NAME,
        "version": version(),
        "standard_version": declared_version(),
        "checks_commit_sha": git("rev-parse", "HEAD"),
        "content_sha256": _digest(files),  # provisional; recomputed over every carried file below
        "definitions": counts,
        "schemas": sorted(rel.split("/")[1] for rel in files if rel.startswith("schemas/")),
        "source": "https://github.com/miri-whl/miri-standard",
    }
    (src / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (src / "__init__.py").write_text(INIT_PY)
    write_agent_metadata(src, manifest)

    # Recompute over EVERY file the package carries, now that the generated documents exist. The
    # provisional value above covered only checks/ and schemas/, which is what api_reference.md and
    # __init__.py already claimed it covered - they were wrong, and this makes them true rather than
    # softening the claim. manifest.json is excluded because it carries the digest.
    # NOT_SHIPPED is the staging intermediate inject_dist_info() moves into `.dist-info/` and deletes
    # from the wheel. Hashing it made content_sha256 a digest of a tree no consumer receives, so the
    # value could not be reproduced from an installed package by ANY encoding - which is what miri-py
    # hit, and why their 36 combinations were 36 wrong answers to a question with no right one. The
    # field claimed to cover "every file in the installed package" and covered something else.
    NOT_SHIPPED = {"_agent_examples.json.src"}
    carried = {}
    for f in sorted(src.rglob("*")):
        rel = str(f.relative_to(src))
        if f.is_file() and f.name != "manifest.json" and rel not in NOT_SHIPPED:
            carried[rel] = f.read_bytes()
    manifest["content_sha256"] = _digest(carried)
    manifest["content_sha256_covers"] = (
        "every file installed under the package directory except manifest.json itself, which carries "
        "this digest; .dist-info/ is excluded because RECORD already hashes it, and __pycache__ is "
        "excluded because it is created after installation. sha256 over each (path, content) pair in "
        "ascending path order, each prefixed by its 8-byte big-endian length, paths UTF-8 with / "
        "separators. miri_standard_checks.verify_content() recomputes it; do not reimplement this.")
    (src / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (OUT / "pyproject.toml").write_text(f'''[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "{DIST_NAME}"
version = "{manifest["version"]}"
description = "The Miri Standard check definitions and schemas, as a data-only package"
readme = "README.md"
requires-python = ">=3.9"
license = {{text = "Apache-2.0"}}
classifiers = ["Development Status :: 3 - Alpha", "Intended Audience :: Developers", "Topic :: Software Development :: Quality Assurance"]

[project.urls]
Homepage = "https://miri-whl.github.io"
Source = "https://github.com/miri-whl/miri-standard"

[tool.setuptools]
package-dir = {{"" = "src"}}
packages = ["{PKG}"]
include-package-data = true

[tool.setuptools.package-data]
{PKG} = ["manifest.json", "_agent_examples.json.src", "checks/*/*.yaml", "schemas/*.json", "agent-metadata/*.json", "examples/*.py", "docs/*.md"]
''')
    (OUT / "README.md").write_text(
        f"# {DIST_NAME}\n\nData-only package carrying the Miri Standard's check definitions and schemas. Built by\n"
        f"`tools/build_checks_wheel.py` from https://github.com/miri-whl/miri-standard at commit\n"
        f"`{manifest['checks_commit_sha']}`; see `manifest.json` for the content hash.\n")
    return OUT, manifest


def inject_dist_info(wheel: pathlib.Path, staged: pathlib.Path) -> None:
    """Move AGENT_EXAMPLES.json into the wheel's `.dist-info/`, where the spec puts it.

    setuptools can carry package data but not dist-info data, so the file is written into the staged
    package under a non-shipping name and relocated here. RECORD is rewritten to match - MIRI-PY-001
    checks the archive against it, so an injected file that RECORD does not know about would trade one
    failure for a worse one. Entry timestamps are fixed rather than current so the rewritten wheel
    stays byte-reproducible.
    """
    payload = (staged / "src" / PKG / "_agent_examples.json.src").read_bytes()
    fixed = (1980, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(wheel) as z:
        names = z.namelist()
        items = {n: z.read(n) for n in names}
    dist_info = next(n.split("/")[0] for n in names if n.endswith(".dist-info/RECORD"))
    target = f"{dist_info}/AGENT_EXAMPLES.json"
    items[target] = payload
    items.pop(f"{PKG}/_agent_examples.json.src", None)

    digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode()
    record = f"{dist_info}/RECORD"
    lines = [ln for ln in items[record].decode().splitlines()
             if ln and not ln.startswith(f"{PKG}/_agent_examples.json.src,")]
    lines.insert(-1, f"{target},sha256={digest},{len(payload)}")
    items[record] = ("\n".join(lines) + "\n").encode()

    with zipfile.ZipFile(wheel, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(items):
            info = zipfile.ZipInfo(name, date_time=fixed)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, items[name])


def verify_shipped_digest(wheel: pathlib.Path) -> None:
    """Recompute content_sha256 from the FINISHED wheel and fail the build if it disagrees.

    The claim "this digest covers what you installed" was false for two releases and nothing caught
    it, because the only computation of it ran over the staging tree and agreed with itself. This
    reads the wheel back - after inject_dist_info() has removed the staging intermediate - and
    recomputes over exactly the entries a consumer receives. An unverifiable integrity field is worse
    than none: it invites a consumer to check something that cannot be checked and conclude the
    package is corrupt when it is not.
    """
    with zipfile.ZipFile(wheel) as z:
        entries = {n[len(PKG) + 1:]: z.read(n) for n in z.namelist()
                   if n.startswith(f"{PKG}/") and not n.endswith("/")}
    claimed = json.loads(entries.pop("manifest.json"))["content_sha256"]
    recomputed = _digest(entries)
    if recomputed != claimed:
        raise SystemExit(
            f"content_sha256 does not describe the shipped package:\n"
            f"  manifest claims : {claimed}\n"
            f"  wheel hashes to : {recomputed}\n"
            f"  entries hashed  : {len(entries)}")
    print(f"  content_sha256 verified against the wheel's own {len(entries)} entries")


def main() -> int:
    out, manifest = stage()
    dist = out / "dist"
    # Reproducible on one machine, not across machines. Entry timestamps are fixed by
    # inject_dist_info(), which is what actually makes repeat builds byte-identical - SOURCE_DATE_EPOCH
    # below is set for the build backend but every entry is rewritten afterwards, so it is not the
    # operative mechanism. setuptools is unpinned (`requires = ["setuptools>=69"]`), and its version is
    # embedded in WHEEL, so a rebuild against a newer setuptools produces different bytes with an
    # identical content_sha256. Claiming tag-level reproducibility would require pinning it exactly.
    # Original note: zip entries carry mtimes, so two builds of one tree differed in sha256 while
    # agreeing on content_sha256. SOURCE_DATE_EPOCH pinned to the commit date makes the wheel itself
    # byte-stable, so SHA256SUMS is a property of the tree rather than of the build minute.
    env = dict(os.environ, SOURCE_DATE_EPOCH=git("log", "-1", "--format=%ct"))
    subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir", str(dist), str(out)],
                   check=True, capture_output=True, text=True, env=env)
    wheel = next(dist.glob("*.whl"))
    inject_dist_info(wheel, out)
    verify_shipped_digest(wheel)
    sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
    (dist / "SHA256SUMS").write_text(f"{sha}  {wheel.name}\n")
    print(f"built {wheel.name}")
    print(f"  version {manifest['version']} | commit {manifest['checks_commit_sha'][:12]} | "
          f"content {manifest['content_sha256'][:12]} | definitions {manifest['definitions']}")
    print(f"  sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
