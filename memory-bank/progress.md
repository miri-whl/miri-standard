# Progress

_Last updated: 2026-08-20._

## What exists

- **Check corpus**: per-check YAML definitions for the Python and CLI targets under `standards/<target>/checks/`,
  governed by `schemas/check-v1.json`, with weights summing to 100 per target.
- **Specs**: Python wheel extensions, agent metadata, lifecycle/security metadata, artifact lifecycle, and CLI
  lifecycle/signaling documents under `standards/`.
- **Schemas**: draft-07 schemas for each metadata file (`lifecycle`, `sdk-manifest`, `usage-patterns`,
  `migration-guide`, `api-graph`) and for the check-definition format.
- **Checklists**: weighted `linter-checklist.md` per target.
- **Site**: `tools/generate_site.py` renders the check pages, indexes, landing page, and origin story; published
  live to the Pages repo by CI. `Makefile` wraps build/preview/verify.
- **CI**: markdownlint, cspell, link check, and structure/required-file checks.
- **Reference linter**: implemented in the separate `miri-py` repo (all Python checks bound); not yet public / on
  PyPI at time of writing.

## What is planned

- Go and Rust standards (currently scope sketches only).
- A CLI `--describe` introspection schema (many CLI checks reference it).
- A getting-started guide and a linter pointer on the site and README.
- An achievable "Core" conformance profile / adoption on-ramp.
- A threat model / security-considerations section.
- Agent-metadata JSON schemas listed as planned but referenced by some checks
  (`agent-examples`, `templates`) — ship or de-reference them.

## Known issues and open risks

Engineering backlog, stated factually so it does not get lost:

- **Sample SDK** is not yet buildable/conforming — it should pass its own checklist and be gated in CI.
- **Spec ↔ linter drift**: the reference linter has resolved ambiguities and, in places, ships behavior that differs
  from the current spec text; these need reconciliation so a second implementer would not diverge.
- **Known check-level items to reconcile** (surfaced in review): a version-pattern that can conflict with an
  exact-match check; a build-timestamp check that covers only one direction; hardcoded-registry assumptions; and
  examples that should be cross-checked against sibling checks for contradictions.
- **Scoring semantics** for capability-forfeited MUST checks are underspecified.
- **Governance/onboarding docs** contain placeholders (Quick Start, some governance fields) to be filled.
- **Schema-enforcement gaps**: some constraints described as "schema-enforced" are enforced only by the linter;
  either tighten the schema or correct the prose.

## Verification status

- Check YAMLs validate against `check-v1.json`; weights sum to 100 per target (verify with the `schema-governance`
  snippets after any change).
- Doc CI (markdownlint/cspell/link) is the gate for prose changes.
