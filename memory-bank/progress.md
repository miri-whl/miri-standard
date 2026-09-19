# Progress

_Last updated: 2026-09-18._

## What exists

- **Check corpus**: per-check YAML definitions for the Python and CLI targets under `standards/<target>/checks/`,
  governed by `schemas/check-v3.json`, with weights summing to 100 per target. Since 0.6.0 a substance-bearing
  check may declare `tiers` and earn its weight as a cumulative schedule rather than a bit.
- **Specs**: Python wheel extensions, agent metadata, lifecycle/security metadata, artifact lifecycle, and CLI
  lifecycle/signaling documents under `standards/`.
- **Schemas**: sixteen draft-07 schemas, all indexed in `schemas/README.md` (the index is gated) — `check-v3.json`
  current, `check-v2.json` and `check-v1.json` retained frozen at their published bytes because a consumer pinned
  there is old rather than wrong, `changelog-v1.json` new at 0.6.0 — one per metadata file, the
  check-definition format, the CLI `--describe` document, the surface envelope, the agent event, the trigger
  response, and the two report formats.
- **Consumption suite** (`standards/consumption/`): Discovery Contract, Consumption Map, Consumer Conformance,
  Surface Conformance, Agent Integration Contract. Four check families now — `MIRI-PY` (43 active, `016`
  withdrawn), `MIRI-CLI` (43), `MIRI-SURFACE` (18), `MIRI-CONSUMER` (18), each summing to exactly 100.
- **Production Maps** for both producer targets: the dependency order among the artifacts an author builds, every
  ordering derived from an existing check rather than asserted.
- **Executable fixtures**: ten wheel build variants from one template with byte-identical sources, plus `greetctl`
  — four CLI arms including a two-release history, since five `MIRI-CLI` checks are claims about a previous release.
- **Goldens**: sixteen `A_` attack cases and eight `E_` event/envelope traces, the latter authored from the Agent
  Integration Contract rather than captured from any implementation.
- **Checklists**: weighted `linter-checklist.md` per target.
- **Site**: `tools/generate_site.py` renders the check pages, indexes, landing page, and origin story; published
  live to the Pages repo by CI. `Makefile` wraps build/preview/verify.
- **CI**: markdownlint, cspell, link check, and structure/required-file checks.
- **Reference linter**: implemented in the separate `miri-py` repo (all Python checks bound); not yet public / on
  PyPI at time of writing.

## What is planned

- Go and Rust standards (currently scope sketches only).
- **A conformance suite for the harness-configuration generator.** Discovery Contract §7 binds it with four
  normative rules and nothing scores them; Consumer Conformance §4 records this as bounded and deliberate. The
  largest named hole in the standard.
- A getting-started guide and a linter pointer on the site and README.
- An achievable "Core" conformance profile / adoption on-ramp.
- A threat model / security-considerations section. Note the Agent Integration Contract added the first threat
  concerning what metadata _makes happen_ rather than what it _says_; the existing model covers only the latter.
- Agent-metadata JSON schemas listed as planned but referenced by some checks
  (`agent-examples`, `templates`) — ship or de-reference them.

Shipped since this list was last written: the CLI `--describe` schema (`cli-describe-v1.json`), the Surface
Conformance profile, and both Production Maps.

## Known issues and open risks

Engineering backlog, stated factually so it does not get lost:

- **Sample SDK** is not yet buildable/conforming — it should pass its own checklist and be gated in CI.
- **Spec ↔ linter drift**: the reference linter has resolved ambiguities and, in places, ships behavior that differs
  from the current spec text; these need reconciliation so a second implementer would not diverge.
- **Known check-level items to reconcile** (surfaced in review): a version-pattern that can conflict with an
  exact-match check; a build-timestamp check that covers only one direction; hardcoded-registry assumptions; and
  examples that should be cross-checked against sibling checks for contradictions.
- **Scoring semantics** for a forfeited MUST were settled in 0.5.0 (`undetermined`, not a discount) and extended
  to implementation-coverage forfeits in the 0.6.0 interop reply — the driver-semantics clauses are promised in
  `scoring-v1` and not yet written.
- **Coverage**: 361 of 400 weight has no test material; `MIRI-PY` at zero, and 0.6.0's four new checks and every
  tier clause add to it. The sample SDK has no previous release, so `041`–`044` are excluded for it.
- **Governance/onboarding docs** contain placeholders (Quick Start, some governance fields) to be filled.
- **Schema-enforcement gaps**: some constraints described as "schema-enforced" are enforced only by the linter;
  either tighten the schema or correct the prose.
- **The vacuous pass** — a check testing the _form_ of a behavior without testing that the behavior _occurs_. Four
  found in one cycle (`MIRI-CLI-013`, `034`, `022`, `MIRI-CONSUMER-041`). Three were CLI and all three were found by
  hand, because no CLI fixture existed until 0.5.0. Treat as a live drafting hazard, not a closed set.
- **Nothing detects metadata that is never read.** Three checks come near it and none tests it. This is the failure
  the standard exists to prevent, and the Agent Integration Contract closes the mechanism without being able to
  verify the outcome. The deepest open risk.
- **`MIRI-CLI-004`'s converse is decidable and unchecked** — a subcommand in `--help` but absent from `--describe`.
  Recorded in CLI Production Map §4; closing it needs a new ID and a weight redistribution.
- **Adversarial review does not converge.** Across thirteen tracked rounds, roughly 450 findings closed against 460
  raised. The useful signal is the _class_ of finding shifting, not the count falling.

## Verification status

As of 0.6.0 (`phase-0.6`), `make check` runs all of this locally and is green:

- 123 check definitions valid against `check-v3.json`; all four targets sum to exactly 100.
- All sixteen schemas are valid draft-07; the envelope is round-tripped 24/24 by `make envelope`.
- Wheel and CLI fixture invariants hold, including 34 CLI invariants and the eight event traces. Both validators are
  mutation-tested: disarming any attack must fail them.
- `make consistency` (9 specs clean, plus the schema index, category totals and checklist↔YAML coherence) and
  `make references` (140 citations resolve across 107 checks) catch drift the linters cannot see.
- `make check` includes the link check since 0.5.0's tail; `make links` had used `find -exec` and had never failed.
- Doc CI (markdownlint/cspell/link) is the gate for prose changes. `make lint` is pinned to the version the CI
  action bundles; unpinned, npx resolves to a newer release whose added rules fail files CI accepts.
