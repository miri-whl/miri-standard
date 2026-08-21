# Active Context

_Last updated: 2026-08-21._

## Current focus

Working the v0.2 backlog (`tasks/stage-v0.2/`) on the `stage-0.2` branch. **42 of 44 standard-side items are done**
and committed; the site regenerates, all schemas and 83 checks validate, and both weight tables sum to 100. Highlights
from the v0.2 pass: the honesty/committee/governance cleanup; the whole CLI-contradiction cluster; the Python check
refinements; the §9 Security Considerations threat model; conformance profiles (Miri Core vs Full) with first-release
Gold reachability; the CLI `--describe` schema (`cli-describe-v1.json`); manifest↔code verification folded into
MIRI-PY-036; a buildable, Miri-conforming sample SDK; and de-referenced/added JSON Schemas.

Only two backlog items remain, both genuine **decisions** left for review:

- **The stash / `standards/python` renames** — the "fix cross-links broken by the renames" item only applies if the
  stashed `miri-*` rename work is adopted. Left untouched; check `git stash list`.

Next: the `miri-py.md` items (linter conformance + fixes in the miri-py repo), then re-run the developer panel audit
once miri-py is caught up.

## Recent decisions

- **Site hosting**: the site is published to the dedicated `miri-whl/miri-whl.github.io` Pages repo (clean root
  URLs). The generated HTML is never committed to this repo — it is a derived artifact published by CI.
- **Local build**: `.generated/` is the local test-render target (gitignored); `make site` / `make serve` build and
  preview it.
- **Tooling scope**: this repo is docs/specs, so only documentation-relevant skills were brought in; the
  Python-application skills from the linter repo were intentionally not copied. New skills were authored for what
  this repo actually does (check YAML authoring, schema/checklist governance).

## Next steps (roadmap, not yet done)

The full v0.2 backlog is staged in `memory-bank/tasks/stage-v0.2/` as three lists (88 items, priority-tagged and
sourced from the two-round panel review): `standard.md` (this repo), `miri-py.md` (linter conformance + fixes), and
`other-issues.md` (miri-py pre-publication, evidence, hygiene). Highlights:

- P0 honesty: drop the "committee" framing, fill governance/security placeholders, replace the README Quick Start
  placeholder, strip unvalidated performance claims.
- Make `examples/sample-sdk` a buildable, checklist-passing artifact and gate it in CI.
- Fix the shipped 007↔012 version-pattern contradiction (release blocker) and reconcile the other check/spec drifts.
- Define an achievable "Core" conformance profile; ship the CLI `--describe` introspection schema.
- Write the threat model / security-considerations section for the metadata agents consume.
- Before miri-py goes public: scrub git history, quarantine the invalid validation evidence, publish to PyPI.

## Open questions

- Whether to split the standard so the lifecycle/deprecation/identity layer stands as a core profile with the
  API-surface layer optional.
- How conformance tiers should treat capability-forfeited MUST checks (score semantics).

## Working-tree note

Earlier local edits (a set of `standards/python` file renames and related doc changes) are parked in a git stash,
not yet committed. Check `git stash list` before assuming the tree is clean.
