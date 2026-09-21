# Progress

_Last updated: 2026-09-21._

## What exists

- **Check corpus**: per-check YAML definitions for the Python and CLI targets under `standards/<target>/checks/`,
  governed by `schemas/check-v3.json`, with weights summing to 100 per target. Since 0.6.0 a substance-bearing
  check may declare `tiers` and earn its weight as a cumulative schedule rather than a bit.
- **Specs**: Python wheel extensions, agent metadata, lifecycle/security metadata, artifact lifecycle, and CLI
  lifecycle/signaling documents under `standards/`.
- **Schemas**: seventeen draft-07 schemas, all indexed in `schemas/README.md` (the index is gated) — `check-v3.json`
  current, `check-v2.json` and `check-v1.json` retained frozen at their published bytes because a consumer pinned
  there is old rather than wrong, `changelog-v1.json` new at 0.6.0, `scoring-v2.json` new at 0.7.0 superseding v1
  for the tier arithmetic (v1 stays published and frozen) — one per metadata file, the
  check-definition format, the CLI `--describe` document, the surface envelope, the agent event, the trigger
  response, and the two report formats.
- **Consumption suite** (`standards/consumption/`): Discovery Contract, Consumption Map, Consumer Conformance,
  Surface Conformance, Agent Integration Contract. Four check families now — `MIRI-PY` (43 active, `016`
  withdrawn), `MIRI-CLI` (43), `MIRI-SURFACE` (18), `MIRI-CONSUMER` (18), each summing to exactly 100.
- **Production Maps** for both producer targets: the dependency order among the artifacts an author builds, every
  ordering derived from an existing check rather than asserted.
- **Executable fixtures**, three suites, each built from one template: eleven `greet` consumption variants (nine
  verified byte-identical, two outliers that exist to differ in source); `greetctl` — four CLI arms including a
  two-release history, since five `MIRI-CLI` checks are claims about a previous release; and, new at 0.7.0, nine
  `greetlib` wheels, the first artifacts the `MIRI-PY` family could ever be run against.
- **Goldens**: fourteen `A_` attack cases and eight `E_` event/envelope traces for the consumer, plus eleven CLI and
  seven Python cases that grade a linter. All authored from the specification rather than captured from any
  implementation. Since 0.7.0 the linter goldens grade **attribution**, not only detection: a finding counts only
  if it names the right check and points at the declared evidence, keyed per check.
- **Checklists**: weighted `linter-checklist.md` per target.
- **Site**: `tools/generate_site.py` renders the check pages, indexes, landing page, and origin story; published
  live to the Pages repo by CI. `Makefile` wraps build/preview/verify.
- **CI**: markdownlint, cspell, link check, and structure/required-file checks.
- **Reference linter**: implemented in the separate `miri-py` repo (all Python checks bound). The release job runs
  it against the definitions wheel from a pinned `MIRI_PY_REF`, so the gate cannot move under the artifact.
- **The definitions wheel** (`miri-standard-checks`): every check YAML and schema, packaged, with its own
  `agent-metadata/` written at build time from the definitions it carries. Scores 98 of an effective 53.0 with zero
  MUST failures. Published from a tag to `miri-whl.github.io/simple/` as a PEP 503 index with PEP 700 JSON.

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
- **Coverage**: 187 of 400 weight has no test material (was 237 before the wheel fixtures). By family:
  `MIRI-CONSUMER` 85/100 covered, `MIRI-SURFACE` 52/100, `MIRI-PY` 50/100, `MIRI-CLI` 26/100 — the CLI family is now
  the thinnest, and every tier clause added at 0.6.0 is still untested. The sample SDK has no previous release, so
  `041`–`044` are excluded for it.
- **`MIRI-PY-023` and `033` carry 4 weight that is not independently reachable.** Every way of violating either is
  also `lifecycle-v1`-invalid, so `MIRI-PY-018` fires first. Found while building an arm for them, which was removed
  rather than contorted; recorded in the Python fixtures README.
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

As of 0.7.0 (`phase-0.7-stage-1`), `make check` runs all of this locally and is green:

- 123 check definitions valid against `check-v3.json`; all four targets sum to exactly 100.
- All seventeen schemas are valid draft-07; the envelope is round-tripped 24/24 by `make envelope`.
- Consumption, CLI and Python fixture invariants all hold, including the eight event traces. Every validator is
  mutation-tested: disarming any attack must fail it.
- Both linter graders reject every way of gaming them that has been thought of — nine for the Python harness,
  seven for the CLI one. Two of the nine are cheats the Python grader itself failed before the panel found them:
  evidence pooled across a case, and findings credited without checking which arm they came from.
- `make consistency` (9 specs clean, plus the schema index, category totals and checklist↔YAML coherence) and
  `make references` (140 citations resolve across 107 checks) catch drift the linters cannot see.
- `make check` includes the link check since 0.5.0's tail; `make links` had used `find -exec` and had never failed.
- Doc CI (markdownlint/cspell/link) is the gate for prose changes. `make lint` is pinned to the version the CI
  action bundles; unpinned, npx resolves to a newer release whose added rules fail files CI accepts.
