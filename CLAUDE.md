# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

The Miri Standard: multi-language packaging standards that make software artifacts (Python wheels, CLIs, eventually Go
modules and Rust crates) legible to AI agents — structured metadata, identity/vulnerability signaling, lifecycle and
deprecation contracts. It is a **documentation and specification repo**: there is no application code, build, or test
suite. The deliverables are markdown specifications, JSON Schemas, and a sample SDK. Python 3 one-liners are used for
verification scripting.

## CI and Local Verification

CI (`.github/workflows/ci.yml`) runs three jobs; all must pass:

```bash
# Markdown lint — same ruleset as CI (config: .markdownlint.json)
npx -y markdownlint-cli@0.41.0 "**/*.md"

# Spell check (config: .cspell.json — add new legitimate jargon/proper nouns to its words list)
npx -y cspell@8 "**/*.md" --no-progress

# Link check runs in CI (gaurav-nelson action, config .markdown-link-check.json).
# Locally, at minimum verify relative links resolve:
python3 -c "
import re, pathlib
for md in pathlib.Path('.').rglob('*.md'):
    for _, t in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', md.read_text()):
        if not t.startswith(('http','mailto:','#')) and not (md.parent/t.split('#')[0]).resolve().exists():
            print(md, t)"
```

Lint rules that shape writing here: prose is hard-wrapped at **120 chars** (MD013; tables and code blocks are exempt),
code fences need a language, no emphasis-only lines as headings, no links to files that don't exist yet — planned
documents are listed as **plain text** with a *(Planned)* marker, never as links (the CI link checker fails on them).
`gnu.org` URLs are in the link-checker ignore list (403s for CI crawlers).

Validate schema/example changes together:

```bash
python3 -m venv /tmp/v && /tmp/v/bin/pip -q install jsonschema
/tmp/v/bin/python -c "
import json, jsonschema
schema = json.load(open('schemas/lifecycle-v1.json'))
jsonschema.Draft7Validator.check_schema(schema)
jsonschema.validate(json.load(open('examples/sample-sdk/src/weather_sdk/agent-metadata/lifecycle.json')), schema)"
```

Verify checklist weights after editing a linter checklist (each must sum to exactly 100):

```bash
python3 -c "
import re
for f, p in [('standards/python/linter-checklist.md','MIRI-PY'), ('standards/cli/linter-checklist.md','MIRI-CLI')]:
    w = re.findall(r'^\| ' + p + r'-\d+ \|.*\| (\d+) \|$', open(f).read(), re.M)
    print(f, sum(map(int, w)))"
```

## Architecture: How the Documents Fit Together

Each artifact type gets a parallel suite under `standards/<type>/`. Python (`standards/python/`) and CLI
(`standards/cli/`) are developed; Go and Rust are scope-sketch READMEs deliberately mapping "what the ecosystem already
provides" vs "what Miri adds".

A suite has four layers that must stay coherent when any one changes:

1. **Core specs** — Python: `miri-wheel-extensions.md` + `agent-metadata-specification.md` (the `agent-metadata/`
   directory in wheels); CLI: `cli-lifecycle-specification.md` (`--describe`, `check-update`, `changelog --since`,
   per-flag `lifecycle` blocks). Plus `lifecycle-security-metadata.md` (Python) defining `lifecycle.json`.
2. **JSON Schemas** (`schemas/*.json`, Draft-07) — one per metadata file. `lifecycle-v1.json` is shared across
   languages. A spec's example JSON, its schema, and the sample SDK copy
   (`examples/sample-sdk/src/weather_sdk/agent-metadata/`) must validate together.
3. **Linter checklists** (`linter-checklist.md` per suite) — numbered checks `MIRI-PY-NNN` / `MIRI-CLI-NNN` with
   weights summing to exactly 100. **IDs are never renumbered**; retired checks are marked withdrawn and weight is
   redistributed. Every conformance rule added to a spec should get a check here.
4. **Artifact lifecycles** (`artifact-lifecycle.md` per suite) — stage tables + mermaid diagrams. The PDFs in
   `assets/` are generated renderings (HTML + inline SVG → headless Chrome); the markdown is the source of truth —
   regenerate PDFs when lifecycle docs change.

Background research lives in `standards/cli/landscape-and-prior-art.md` and `update-and-vulnerability-signaling.md`;
specs cite these by section, so section numbers there are load-bearing.

## Recurring Design Principles (apply to new spec work)

- **Declare sources, not verdicts.** Artifacts never claim "no vulnerabilities" or embed computed state; they declare
  identity (purl) and pointers to live sources (OSV-format `advisory_sources`, `update_check`). Verdicts are computed
  by consumers at call time.
- **Reuse the existing stack.** Identity is purl; advisories are OSV records; SBOMs follow PEP 770 (wheels) or
  CycloneDX/SPDX (CLIs). Miri defines no parallel formats.
- **Same shape for open source and private.** Private artifacts differ only in *values* (private purl namespace,
  internal OSV endpoint), never in structure. Every spec has parallel "Open Source" and "Private and Internal"
  sections.
- **Schema as data, derived outputs.** One source generates human docs and machine metadata (`--help` and `--describe`
  from one struct; `migration-guide.json` from PEP 702 markers). Never specify parsing one derived output to produce
  another.
- **Deprecation coherence.** Markers, changelog, and removals must agree; no silent removals. Two-phase lifecycle:
  `deprecated_since` → grace period → `removed_in`, always with `replacement`.
- **Citation trail.** Every normative statement cites the standard it derives from (PEP, RFC, POSIX/GNU, OSV, K8s
  policy). Community practice with no normative authority (clig.dev, anc.dev, Agent-First CLI) is marked
  *(informative)*.

## Conventions

- Spec headers: `*Specification Version: X.Y-draft*` / `*Status: Draft*` / `*Created: YYYY*` (note the trailing periods
  inside emphasis where lint requires them).
- Commit messages use `feat:` / `fix:` / `chore:` prefixes.
- The top-level `standards/README.md` indexes every spec (sections per language + a Draft Standards list); per-suite
  READMEs index their own directory. New documents must be added to both.
- `.vscode/settings.json` (muted-gold workspace theme) is intentionally committed; the rest of `.vscode/` is ignored.
- The project name collides with Miri, the Rust UB interpreter — `standards/rust/README.md` carries the disambiguation
  note; keep it when touching Rust material.
