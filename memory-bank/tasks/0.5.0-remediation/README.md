# 0.5.0 remediation

_Opened: 2026-09-08. Status: first pass complete; residue tracked below._

## Pass 1 — closed

| Defect | How |
| --- | --- |
| P0-1 conditional semantics | `check-v1.json` now says excluded-from-both; `MIRI-CLI-024` and the CLI map's auto-pass wording removed. **Downstream-affecting** — miri-py must re-sync the vendored schema, and any linter that implemented auto-pass changes every score involving one of the 24 conditional checks. |
| P0-3 golden phase | E1/E2/E3/E7 moved to `phase: after`, with the reason recorded in each. |
| P0-4/5 E5 | Re-sourced to `usage-patterns.json` (what task 3.4 step 1 actually serves) and the quote now carries the directive span, not the benign prefix. |
| P0-6 E6 level | `should` -> `must`, matching both the YAML and the profile table. |
| P0-7 E4 | Finding re-sourced to `lifecycle.json`, which carries a real purl; the prospective guide is now reported as not-answerable rather than answered from. |
| C2 phantom double | `examples/fixtures/src/_template/testing.py` ships a real `FakeGreeter`. The declared import path resolves; byte-identity across the 8 source-sharing variants still holds. |
| P1-1 inert linter passes | The validator now drives the binary for 013/025/029/030/033 and fails cleanly. A do-nothing stub went from **34 PASS / 0 FAIL** to **11 named FAIL**. |
| P1-2 conforming arm | `greetctl` now rejects an unparseable `--since`, emits `current`/`latest`, and returns the 5.2 record shape with all five categories. Fixing the shape broke the validator, proving it had been written against the implementation. |
| P1-3 CI | `make validate-cli-fixtures` and `make findings-schema` added to `ci.yml`. |
| P1-4 dead assertions | `validate_fixtures.py` now checks E-series `checks` IDs, compiles assertion regexes, and verifies `source` exists and `quote` appears in it. Mutation-tested against all five original defects. |
| P1-6/7/8 schema | `agent-findings-v1` rebuilt by copying the envelope's rules verbatim; 11 of 12 divergences closed, plus a 12th (`present` required on success). Host-control shapes denied. |
| P1-9 reject harness | `tools/validate_findings_schema.py`, 27/27, wired to `make findings-schema`. |
| P1-10/11 false universals | Both maps corrected; the CLI map now derives an ordering _within_ Stage 5 from `MIRI-CLI-041` -> `039`/`042`. |
| P1-12/13 | Self-contradiction resolved; arithmetic 30 -> 32. |
| H3/H4/H5/H7 | 33 -> 35 in two files; Python map indexed in its suite README; the "verified complete" claim replaced by an actual gate; dangling 0.4.1 reference fixed. |
| M8 dead guard | Two independent bugs (hyphen, required emphasis) had kept it dead. Replaced with a targeted suite-total rule; `SPECS` widened from 6 to 9 documents. |
| M3 site statuses | Five stale `status:` values corrected. |
| P2-1/2 | Two overstated README claims corrected in place. |

New gates added, all mutation-tested: golden ground-truth (level/source/quote/check-IDs), schema-index completeness,
envelope-inheritance drift, suite totals.

## Still open after pass 1

- **P0-2** `MIRI-CONSUMER-041` remains abstention-passable in the path where it applies: both `fires_when` clauses
  require the consumer to present something, so an inert consumer fires neither.
- **P0-8 / C-1** the CLI fixtures still have **no goldens** — `examples/fixtures/cli/expected/` is empty, so nothing
  states what a linter must report. The wheel side has 24. This is the largest remaining gap.
- **E3 discrimination** needs a third arm: a package carrying the attention bid with nothing genuine to report.
- **Derivation residue**: `MIRI-CLI-021`'s asserted resolution dependency, `MIRI-PY-028/029` markers-first, `MIRI-
  CLI-010` directionality, and the uncited checks that impose orderings (`MIRI-CLI-008`/`009`/`016`/`025`/`029`,
  `MIRI-PY-009`/`011`).
- **C3/C6** attack assertions still piggyback on C2's banner.
- **H1** the contract's REQUIRED-kind paragraph still contradicts itself ("the cost of requiring two").
- **M4** the "hook appears exactly seven times" meta-claim is false.
- **M5** the `whats-new.html` -> `why-consumption.html` URL break is unrecorded.
- 28 weight of CLI checklist is behaviorally identical across all four arms; the `bare` arm is still never driven.

Six adversarial panels reviewed the 0.5.0 changeset. Four have reported; every finding checked so far was
**confirmed by direct verification** and none was a false positive. Scores: schema 34, derivation 55, goldens 26,
vacuous-pass 34.

0.5.0 MUST NOT merge until P0 and P1 are closed.

## The root cause, stated once

All four panels found the same habit under different names:

> Assertions are written against the artifact the author just wrote, not against a behavior an implementation
> must produce.

Its signature is **one-directional verification**: every claim made was checked, and nothing was checked against
what was _not_ claimed. Cited checks were verified; uncited checks that impose orderings were not. Quotes were
verified to exist; they were not verified to be _reachable_. Envelope rules that were re-typed were verified;
the ones dropped were not. This is the same containment asymmetry the CLI Production Map §4 identifies in
`MIRI-CLI-004` — committed by the document that identifies it.

## P0 — systemic, or actively misleading a downstream team

| # | Defect | Where | Panel |
| --- | --- | --- | --- |
| P0-1 | `conditional: true` means "score full weight **automatically**" in `check-v1.json`, and "excluded from **both** numerator and denominator" in `consumer-conformance.md`. 0.5.0 used this flag as the _remedy_ for a vacuous pass. Affects every conditional check on every target. | `schemas/check-v1.json:85` vs `standards/consumption/consumer-conformance.md:284` | vacuous |
| P0-2 | `MIRI-CONSUMER-041` still abstention-passable in the path where it now applies: both `fires_when` clauses require the consumer to _present_ something. | `standards/consumption/checks/MIRI-CONSUMER-041.yaml` | vacuous |
| P0-3 | E1/E2/E3/E7 use `dependency.add` at `phase: before`, where the contract's own footnote says the package is not installed and the trigger "correctly finds nothing every time" — yet they demand findings sourced from `lifecycle.json`. | `examples/fixtures/expected/E{1,2,3,7}*.json` | goldens |
| P0-4 | E5 sources its finding from `sdk-manifest.json` `summary`, which no `api-index` response carries — the exact defect the A-series already diagnosed and fixed by relocating A5 to `usage-patterns.json`. | `E5-runtime-error.json` | goldens |
| P0-5 | E5's `quote` is `"Builds greetings."` — the benign prefix — under a finding that says the document carries directive text. | `E5-runtime-error.json` | goldens |
| P0-6 | E6 emits `level: should` and justifies it as the profile's value; `MIRI-CONSUMER-041` is `MUST` in both YAML and the profile table. A correct implementer fails E6. | `E6-test-author.json` | goldens, vacuous |
| P0-7 | E4 answers from a **prospective** migration guide (`1.0.0 → 2.0.0`, installed is `1.0.0`), which Map §3.3 says MUST NOT be answered from the shipped file. | `E4-upgrade.json` | goldens |
| P0-8 | E3 does not discriminate. Bid-presence and finding-existence are perfectly correlated across the only two arms, so a consumer firing _because of_ the bid produces byte-identical output to a correct one. Needs a third arm: the bid with nothing genuine to report. | `E3-*.json`, fixture set | goldens |

## P1 — the test material does not test what it claims

| # | Defect | Where | Panel |
| --- | --- | --- | --- |
| P1-1 | All 34 CLI invariants pass a 28-line do-nothing stub. Eight of eleven attack assertions read `describe.json` off disk and never invoke the binary. | `tools/validate_cli_fixtures.py` | vacuous |
| P1-2 | The **conforming** arm is non-conforming: `check-update --help` and `changelog --help` exit 1 while appearing in root help (`MIRI-CLI-004`), and both are absent from `--describe` — the very divergence CLI map §4 documents. | `examples/fixtures/cli/src/_template/greetctl.py` | vacuous |
| P1-3 | CI never runs `make check`, so `validate-cli-fixtures` gates nothing. | `.github/workflows/ci.yml` | vacuous |
| P1-4 | E-series `assertions` are dead JSON: regexes never compiled, `checks` never verified against real IDs, `quote` never checked against `source`, `source` never checked to exist. The A-series guards exist 18 lines away. | `tools/validate_fixtures.py:445` | vacuous, goldens |
| P1-5 | C3 and C6 survive disarming — the mutation-test claim in the README is false for 2 of 11. C6's third conjunct is decided by C2's banner, not by the changelog. | `tools/validate_cli_fixtures.py:172,182` | vacuous |
| P1-6 | `agent-findings-v1` claims to BE the envelope but has zero `$ref`; 11 documents it accepts the envelope rejects, incl. `schema_version: "1.0"` (the exact divergence the envelope pins against), `ok:false` with no error, invented error codes. | `schemas/agent-findings-v1.json` | schema |
| P1-7 | Coupling enforced one way only: `{"ok":true,"findings":[…]}` with no `present` validates, as does `{"schema_version":"1","ok":true}`. | same | schema |
| P1-8 | Open root accepts host control keys (`hookSpecificOutput.permissionDecision: "deny"`, `decision: "block"`) on the response §4.4 governs. The cited backstop `MIRI-SURFACE-003` is `target: surface` and does not bind a consumer. | same | schema |
| P1-9 | No reject-direction validator for `agent-findings-v1`; pointed at the envelope's, it scores 4 genuine catches of 16. | `tools/` | schema |
| P1-10 | CLI map Stage 5: "no check makes any other surface depend on them. Nothing reads them" — `MIRI-CLI-039` (MUST, w4) and `042` draw their population from `--describe`'s `mutating` field. The map tells authors to defer a field a w4 MUST consumes. | `standards/cli/production-map.md:145` | derivation |
| P1-11 | Python map Stage 4: "neither is depended upon by any other document" — `MIRI-PY-039` couples a template to `api-graph.json` presence. | `standards/python/production-map.md:87` | derivation |
| P1-12 | Self-contradiction 32 lines apart: "four of its eight" (:136) vs "every one of them lives in Stage 4" (:168). `MIRI-CLI-030` is `Update & Changelog`. | `standards/cli/production-map.md` | derivation |
| P1-13 | "thirty of the forty" — arithmetic gives 32. | `standards/python/production-map.md:105` | derivation |
| P1-14 | `MIRI-CLI-021` "must resolve against a command surface" is not in the YAML (form test, not resolution) and would target a _different binary_. Also `MIRI-PY-028/029` markers-first, and `MIRI-CLI-010` directionality — three orderings asserted, not derived. | both maps | derivation |
| P1-15 | Stage 1 ordering inverted by two uncited MUST checks: `MIRI-CLI-008` (w4) and `009` (w2) both key on `--describe`. Plus MISS-C2..C5, MISS-P1..P4. | `standards/cli/production-map.md` | derivation |
| P1-16 | `MIRI-CLI-006` placed in Stage 0 but has a `--describe` clause; `MIRI-PY-028` in Stage 1 but its population is drawn from the migration guide. | both maps | derivation |

## P2 — prose that overstates what shipped

| # | Defect | Where |
| --- | --- | --- |
| P2-1 | "the validator is mutation-tested: disarming any attack must fail it" — true for 9 of 11. | `examples/fixtures/cli/README.md` |
| P2-2 | "`--help` … derived from that one `describe.json` … true by construction" — `render_help()` hardcodes `check-update`, `changelog` and the global-options block. | same |
| P2-3 | "What the schema cannot enforce is that `level` was derived" — singular; at least eight more, two of them clauses actively dropped from the envelope's field descriptions (`reason` MUST NOT carry publisher bytes; `purl` never read from a served document). | `agent-integration-contract.md` §3.3, `CHANGELOG.md` |
| P2-4 | Commit `50c00f3`'s message states the 041 fix applies "not-applicable-is-not-a-pass". Under `check-v1.json`'s definition it does the opposite. History; correct in the remediation commit rather than rewriting. |  |
| P2-5 | `MIRI-CLI-004` misquoted in CLI map §4 (population is `--describe` **or root help**). The converse gap finding itself is correct. | `standards/cli/production-map.md:193` |
| P2-6 | `MIRI-CLI-023` described as "fires only when" but declared `conditional: false`; `MIRI-CONSUMER-020` flag/prose disagree. | check YAMLs |

## Still outstanding

Two panels have not reported: the fixture adversary and the coherence reviewer. Their findings land here before the
remediation is called complete.

## Decisions needed from the maintainer

1. **P0-1 semantics.** Which is normative — auto-pass, or excluded-from-both? The project's stated rule is
   "not-applicable is not a pass", which makes `check-v1.json`'s description the defect. Changing it is
   **downstream-affecting**: miri-py vendors this schema, and any linter that implemented auto-pass will change
   every score involving a conditional check.
2. **P0-3 phase.** Either the four goldens move to `phase: after`, or the suite states that arms are pre-installed.
   The contract's §3.1 footnote and §6.1's `PreToolUse` mapping currently disagree about whether `before` can work.
