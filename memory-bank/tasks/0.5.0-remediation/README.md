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

## The `conditional` sweep (round 2, blast-radius panel)

Round 1's fix changed `check-v1.json` and `MIRI-CLI-024` and stopped. Six further sites still asserted the reverted
rule; the register itself had framed P0-1 as _"affects every conditional check on every target"_ and then changed one
check on one target. Swept 2026-09-08:

| Site | Why it mattered |
| --- | --- |
| `.claude/skills/check-authoring/SKILL.md` | CLAUDE.md mandates loading it before writing any check, so the defect regenerated on the next one written |
| `schemas/scoring-v1.json` | The schema whose only job is this arithmetic; described the repudiated additive model and had no denominator concept at all |
| `standards/python/checks/MIRI-PY-005.yaml` | A check's own text, in the machine-readable source of truth |
| `standards/python/linter-checklist.md` Purpose | Contradicted its own Scoring Model eight lines below |
| `standards/cli/linter-checklist.md` Purpose | Same |
| `standards/cli/linter-checklist.md` MIRI-CLI-024 row | The derived rendering of the one check that had been fixed |
| `standards/feedback/miri-standard-response-check-requirements.md` | **Our** normative answer to miri-py said "full weight"; corrected inline rather than silently |

Two inbound proposals (`check-requirements-proposal.md`, `miri-py-scoring-model-proposal.md`) carry the old reading
and were **annotated as superseded, text preserved** — they are a record of what was proposed and when, and rewriting
them would falsify it.

`lint-report-v1.json` gained what the checklists already made mandatory and it could not express:
`effective_denominator`,
`excluded`, `forfeited`, all required alongside a conformance score, plus a rule that a skipped outcome MUST name its
reason. Both verified to reject the shapes they exist to forbid.

## Structural questions the sweep exposed and did NOT resolve

These need a decision, not an edit, and are recorded so they are not rediscovered a third time:

- **What an excluded or forfeited MUST does to conformance is unspecified for the producer targets.** The consumption
  profiles call a forfeited MUST `undetermined`; the word appears nowhere in `standards/python/` or `standards/cli/`.
  The 74-point cap is defined for a MUST that FAILED. An excluded MUST left the denominator and was never evaluated —
  it plainly should not cap, but nothing says so.
- **There is no coverage floor.** Once exclusions and forfeits compound, a python-wheel can be scored over 58 of 100
  weight and a CLI over 72, and nothing forbids awarding Gold on that base. `scoring-v1.json` now has a
  `minimum_coverage` field so an implementation can set one and say that it did; the standard sets none.
  The checklists' own argument for abandoning auto-pass was that two scores of 75 could not be compared. Exclusion
  moves that incomparability from the numerator to the denominator rather than removing it.
- **Conditionals and forfeits are now arithmetically identical, and ten checks carry both flags** (five MIRI-CLI, five
  MIRI-PY) with no precedence rule. The stated difference is one sentence per checklist. A conditional's predicate is
  English in `fires_when` while a forfeit has a fixed machine-readable reason, and that asymmetry is unacknowledged.
- **`lint-report-v1.json` cannot represent the consumption profiles**: its `target` enum is `python-wheel`/`cli` and
  its outcome-id pattern excludes `CONSUMER`/`SURFACE`, so those profiles' own denominator MUSTs are unreportable.

## Round three — narrow scope, three lenses (2026-09-10)

Scoped to the diff since round two and told what rounds one and two had covered. Scores: gate mechanism 34,
security claims 34, implementer-reading-the-release 52. Every critical verified before acting; no false positives.

The narrow scope paid: three reviewers found more than round two's six, because they were pointed at material that
had never been reviewed rather than at documents two rounds had already walked.

| Finding | Disposition |
| --- | --- |
| The gate mechanism was inert — a failed gate validated alongside `grade: gold`, and `scoring-v1` did not know gates existed | `must_failures` required and coupled to grade + the 74 cap; the 0/0 trap named in `scoring-v1`; the gate invariant moved into `check-v2` where vendors see it |
| `MIRI-CONSUMER-052` could not be driven, and as a MUST it made every consumer verdict `undetermined` | `replaced` fixture arm sharing `miri`'s purl; golden `A14`; Case cell `(A14)`; `052` now conditional |
| Its Case cell evaded the coverage gate by citing a spec section, which the gate's `(A` substring test could not see | Gate now fails any Case cell citing a specification section. A first, broader attempt false-positived on three behaviorally-driven checks and was narrowed |
| The breaking change was machine-undetectable — `conditional` reversed meaning with byte-identical validating content | `check-v2.json`, with `$schema` required per definition so a mismatched corpus and schema fail both ways. Proved itself immediately: `make validate` and the pre-commit hook both broke on the stale pointer |
| "A purl identifies a name and a version, **never** a byte stream" — refuted by the `checksum` qualifier in the spec the check cites | Corrected, and the qualifier addressed rather than ignored |
| §6.1's recognizer missed `pip uninstall && pip install` — the sequence §9.6 describes — and fired on no-op installs | Keyed on the session rather than the single command |
| Category headings and both summary tables carried the pre-gate weighting, summing to 100 | Regenerated from YAML; `check_category_totals()` added so they cannot drift again |
| The BREAKING section was the only part of the entry with no links, no named schema, and no migration path | "To upgrade" block, five ordered steps, and an explicit statement of what will not fail loudly |
| Three execution-gated MUSTs are not conditional, so the default posture reports `undetermined` for every artifact and nothing said so | Stated in the Scoring Model and pre-empted in the migration block |
| The 8/58 and 2/57 figures were derivable from no artifact | Replaced with profile-stated, derived denominators: 57 and 75 |

### Not fixed, recorded

- `tools/score_sample.py` reads `is_conforming`, which no schema defines — it survives on
  `additionalProperties: true`, and it is the only place in the repo where a gate failure would visibly bite.
- `weight: 0` is documented as colliding with "extension check", and the corpus contains **no** X-namespace
  checks — so the collision the discriminator was introduced for has zero instances today.
- `MIRI-CONSUMER-052` voids a determination about replacement legitimacy, which lives in Map §3.3 — a task
  neither of its two read-orders reaches.
- Per-check revision history. `added_in` records birth; nothing records revision, so a downstream cannot tell
  which of the 119 definitions changed this release. Whether `changed_in` is normative or editorial is a
  governance decision, deliberately not made as a side effect of the schema bump.

## Coverage, measured

The number that matters most for what comes after 0.5.0, and it is worse than "the P-series is missing":

| Family | Checks untested | Weight untested |
| --- | --- | --- |
| `MIRI-PY` | 40 of 40 | 100 of 100 |
| `MIRI-CLI` | 30 of 43 | 68 of 100 |
| `MIRI-SURFACE` | 9 of 18 | 48 of 100 |
| `MIRI-CONSUMER` | 3 of 18 | 15 of 100 |

**361 of 400 weight has no test material.** The consumer family is genuinely covered; the CLI harness grades 11
checks of 43, which is less than its existence suggests; the founding suite is at zero. That is the next project,
and the caveat to carry into it is that the attribution harness took two attempts and its self-test still derives
"correct" from the goldens — replicating it four times would replicate that limit four times.
