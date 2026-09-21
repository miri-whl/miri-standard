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
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / ".generated/checks-wheel"
PKG = "miri_standard_checks"
DIST_NAME = "miri-standard-checks"


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
    for rel, data in files.items():
        p = src / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    digest = hashlib.sha256()
    for rel in sorted(files):
        digest.update(rel.encode()); digest.update(b"\0"); digest.update(files[rel]); digest.update(b"\0")
    counts: dict[str, int] = {}
    for rel in files:
        if rel.startswith("checks/"):
            counts[rel.split("/")[1]] = counts.get(rel.split("/")[1], 0) + 1
    manifest = {
        "schema_version": "1",
        "distribution": DIST_NAME,
        "version": version(),
        "standard_version": declared_version(),
        "checks_commit_sha": git("rev-parse", "HEAD"),
        "content_sha256": digest.hexdigest(),
        "definitions": counts,
        "schemas": sorted(rel.split("/")[1] for rel in files if rel.startswith("schemas/")),
        "source": "https://github.com/miri-whl/miri-standard",
    }
    (src / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (src / "__init__.py").write_text(
        '"""The Miri Standard check definitions and schemas, as installed data.\n\n'
        "Data-only. `root()` is the directory holding checks/<target>/*.yaml and schemas/*.json;\n"
        "`manifest()` pins what was built: the release, the commit sha, and a content hash.\n"
        '"""\nimport json\nimport pathlib\n\n'
        "def root() -> pathlib.Path:\n    return pathlib.Path(__file__).resolve().parent\n\n"
        "def manifest() -> dict:\n    return json.loads((root() / 'manifest.json').read_text())\n"
    )
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
{PKG} = ["manifest.json", "checks/*/*.yaml", "schemas/*.json"]
''')
    (OUT / "README.md").write_text(
        f"# {DIST_NAME}\n\nData-only package carrying the Miri Standard's check definitions and schemas. Built by\n"
        f"`tools/build_checks_wheel.py` from https://github.com/miri-whl/miri-standard at commit\n"
        f"`{manifest['checks_commit_sha']}`; see `manifest.json` for the content hash.\n")
    return OUT, manifest


def main() -> int:
    out, manifest = stage()
    dist = out / "dist"
    # Reproducible bytes: zip entries carry mtimes, so two builds of one tree differed in sha256 while
    # agreeing on content_sha256. SOURCE_DATE_EPOCH pinned to the commit date makes the wheel itself
    # byte-stable, so SHA256SUMS is a property of the tree rather than of the build minute.
    env = dict(os.environ, SOURCE_DATE_EPOCH=git("log", "-1", "--format=%ct"))
    subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir", str(dist), str(out)],
                   check=True, capture_output=True, text=True, env=env)
    wheel = next(dist.glob("*.whl"))
    sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
    (dist / "SHA256SUMS").write_text(f"{sha}  {wheel.name}\n")
    print(f"built {wheel.name}")
    print(f"  version {manifest['version']} | commit {manifest['checks_commit_sha'][:12]} | "
          f"content {manifest['content_sha256'][:12]} | definitions {manifest['definitions']}")
    print(f"  sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
