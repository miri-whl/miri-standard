# Changelog

All notable changes to the Miri Standard are recorded here.

Versions follow the policy in [standards/README.md](standards/README.md#versioning): a **major** version marks a
breaking change, a **minor** version a backward-compatible addition, and a **patch** version bug fixes and
clarifications only. That policy is a contract with implementers, and it is worth keeping strictly: a reader
should be able to see `0.3.1` and know it contains no additions without having to check.

## 0.5.0 — 2026-09-08

A **minor** version. It began as 0.4.1 — four fixes from the first binding — and became 0.5.0 when it gained the
Production Map, which is an addition. The number followed the content rather than the content being trimmed to fit
the number.

### Added

- **[Production Map](standards/python/production-map.md)** — the producer counterpart to the Consumption Map. The
  consumer side had an ordered model; the producer side had a checklist and no statement of what an author does
  first. Reported by a team implementing both halves: *"the consumer side was straightforward because the Map told
  us the order; the author side we had to invent an order for, and nothing checks whether we invented a good one."*

  Five stages, and **every ordering is derived from an existing check** rather than asserted — the version must be
  settled first because `MIRI-PY-019` and `MIRI-PY-012` check documents against `METADATA`; the manifest precedes the
  migration guide because `MIRI-PY-031` requires replacements to name interfaces in the *new* manifest; the guide is
  last because it depends on all three. A stage with no check behind it would be advice.

  It also states what a checklist cannot: **two checks require a previous release and are not evaluable on a first
  one**, so a first release is scored over what could be evaluated and cannot honestly show 100.

  It is explicitly not a conformance surface. No check scores an author on following it, because the checklist grades
  the artifact and not the process.

- **[CLI Production Map](standards/cli/production-map.md)** — the same document for the largest target in the
  standard. `MIRI-CLI` carries forty-three checks, more than any other suite, and had no ordered model at all.

  Six stages, every ordering derived from a check: `--version` is settled first because `MIRI-CLI-017` compares
  `identity.version` against what the binary actually prints; the JSON envelope precedes `--describe` because
  `MIRI-CLI-010` fires when the two disagree, and `--describe` is one of the payloads it governs; the deprecation
  blocks are last because `MIRI-CLI-038` resolves every replacement against the current `--describe` *and*
  `MIRI-CLI-036` requires every deprecation to appear in `changelog --since` — the only surface depending on every
  other one, which is the same reason `migration-guide.json` is last on the wheel side.

  §3 records that **five CLI checks require a previous release**, carrying fourteen of the hundred weight, against
  two on the wheel side. A CLI's deprecation contract is a claim about what the binary used to do, and one release
  contains no evidence of it.

  §4 names the one conformance requirement that is normative and **ungraded**: CLI Lifecycle Specification §9 item 6
  requires `--help` and `--describe` to derive from one schema-as-data source, and no check can verify it — two
  hand-maintained outputs that agree are indistinguishable from two derived ones when all a linter may do is run the
  binary. An author looking for the check that enforces item 6 has not missed one. One observable shadow of it *is*
  decidable and currently unchecked, and is recorded there rather than left to be discovered.

- **[`agent-findings-v1.json`](schemas/agent-findings-v1.json) and the event-trace goldens** — the Agent
  Integration Contract defined the response as the envelope plus a `findings` key, and nothing pinned it down. No
  schema for the response, no rule mapping check IDs to `findings[].level`, and no goldens — which left the first
  binding implementing against prose and blocked on acceptance criteria it could not write for itself.

  The schema enforces the coupling §3.3 states normatively, in both directions: `present: true` requires
  `findings`, `present: false` forbids it and requires a `reason`, and **an empty `findings` array is rejected** —
  so a binding cannot satisfy the silence obligation by emitting one. `task` is closed to the six map sections;
  `level` is closed to `must`/`should`, the conformance vocabulary rather than the check-severity one, so a
  publisher's `priority: "critical"` cannot reach it even if a consumer passed it through unexamined. What the
  schema cannot enforce — that `level` was *derived* from the profile rather than copied — is said plainly in the
  schema rather than implied to be covered.

  Eight goldens, `E1`–`E8`, authored from the specification rather than captured from an implementation, which is
  what keeps a binding's author from also being the author of its acceptance criteria. Every event validates
  against `agent-event-v1` and every response against `agent-findings-v1` under `make validate-fixtures`; the gate
  is mutation-tested.

  Two are worth naming. `E6` is the only trace driving the **conforming** arm: every other asks whether a consumer
  resists what metadata claims, and `E6` asks whether it uses what metadata declares — a suite made entirely of
  adversarial traces cannot tell a careful consumer from an inert one, which is the defect `MIRI-CONSUMER-041`
  itself carried. `E3` makes the trigger-forcing case discriminating: `A13` alone asserts only that output does not
  echo the bid, which a consumer that never reads satisfies trivially, so `E3` requires a *response* on both arms:
  findings where the bid is, and §4.1's absent envelope where it is not. The discriminator is **absent envelope
  versus silence** — a consumer that reads only when summoned produces nothing at all on the control arm.

- **[CLI conformance fixtures](examples/fixtures/cli/README.md)** — `greetctl`, four arms, and the first executable
  thing a CLI linter can be driven against. Every fixture in the repository was a Python wheel, so
  `make validate-fixtures` could not touch a CLI. The three vacuous-pass defects found in `MIRI-CLI-013`, `034` and
  `022` were all found by hand across four review rounds, because no fixture could find them.

  Unlike the wheel fixtures it ships a **release history** — `miri-1.0.0` and `miri-1.1.0` — because the five
  previous-release checks cannot be exercised without one. `--shout` is deprecated in 1.0.0 and removed in 1.1.0, so
  invoking it against the current release yields the structured teaching error of `MIRI-CLI-033` naming a
  replacement that resolves; `legacy-greet` is deprecated in 1.1.0 and that deprecation reaches
  `changelog --since 1.0.0`, which is what `MIRI-CLI-036` requires and nothing could previously test.

  One implementation file, copied byte-identically into all four arms, so any observed difference is
  metadata-attributable. Eleven attacks (C1–C11), each asserted live by `tools/validate_cli_fixtures.py` and
  mutation-tested: disarming any one of them fails the validator. Wired into `make check` via
  `make validate-cli-fixtures`.

### Changed

- **BREAKING — `conditional` semantics reversed, and three checks now gate rather than score.** Both change
  every conformance score, and both affect anything vendoring `schemas/check-v1.json`.

  `conditional: true` previously meant a check *"scores its full weight automatically when the condition does
  not apply"*. It now means the check is **excluded from both the numerator and the denominator**. Not-applicable
  is not a pass: awarding weight for an absence let an artifact collect points for having nothing to declare.
  Twenty-four checks across three targets are affected, and a linter that implemented the old reading produces
  different numbers for every artifact after re-syncing.

  `MIRI-PY-001`, `002` and `003` gain `scoring: gate` and weight 0. They remain MUSTs and still make an artifact
  non-conforming when they fail; they are no longer measured. Six points moved to `MIRI-PY-007` and `008`
  (+2 each) and `014` and `015` (+1 each). `check-v1.json` gains the `scoring` field, because weight 0 already
  meant "extension check" and one value cannot mean two things.

  Reported by the miri-py team from scoring five unrelated wheels that returned an identical 8/10 in the
  Packaging Baseline. The interaction is the part worth knowing: renormalizing shrinks the denominator, so a
  constant numerator becomes a **larger** share — the Baseline went from 8% of a fixed 100 to about 14% of a
  typical applicable 58. Shipping the renormalization alone would have nearly doubled the fraction of a score
  carrying no information. Both sides of the discussion had that backwards at first. Gating brings it to ~4%.

  Reports MUST now carry `effective_denominator`, `excluded` and `forfeited` beside a conformance score, and a
  forfeited MUST yields the new `undetermined` grade rather than a claim of conformance.

### Fixed

Four defects found by the miri-py team building the first binding, plus one process failure of ours that let two of
them ship, one vacuous check they found implementing `test.author`, and one latent bug in the site generator that
adding the second Production Map exposed.

- **The schemas index listed 7 of 13 schemas.** `cli-describe-v1`, `discovery-envelope-v1`, `agent-event-v1`,
  `scoring-v1` and `lint-report-v1` were never added to `schemas/README.md`, so five schemas the specs depend on
  were discoverable only by listing the directory. All thirteen are now indexed, and `make consistency` now fails if a schema
  lacks an index entry. An earlier draft called the index "verified complete" when nothing verified
  it — the repo's own thesis violated in the sentence claiming to have closed it.

- **The site generator silently overwrote pages whose sources shared a basename.** Output names were derived from
  the source filename alone, so `standards/python/production-map.md` and `standards/cli/production-map.md` both
  rendered to `production-map.html` and one page vanished from the site with no error. Specs may now set a `slug:`,
  and a collision is a hard failure naming both sources rather than a silent loss.

- **Two fixes described as committed were not in the release.** They were committed to a branch that was never
  pushed, so a search of every remote branch correctly found nothing. The work existed on one machine and was
  reported as done. Both are now in: §3.3's `lifecycle` step and the event schema's `phase` rule.

- **Consumption Map §3.3 had no `lifecycle` step**, so a consumer following the upgrade task exactly could upgrade a
  package that is deprecated and names a successor in a foreign purl namespace and never be told — the producer
  standard's highest-severity documented attack, reachable through correct adherence. The namespace prohibition was
  already in §3.3's must-not block with no read-step supplying its evidence. **A prohibition whose input the
  read-order does not fetch is unenforceable.** 0.4.0 made this worse by making §3.3 REQUIRED.

- **`agent-event-v1.json` could not express a real dependency.** `subject.package` required an import name, but a
  manifest contains **distribution** names, and the mapping between them lives in the installed distribution's own
  metadata — unavailable for a package that is not yet installed. `miri-py`, `python-dateutil`, `ruamel.yaml` and
  our own `greet-adversarial` fixture were all rejected. `subject.package_kind` now says which kind of name is
  carried, with PEP 503 grammar for the distribution case.

- **`dependency.add` is demoted from REQUIRED to SHOULD.** At the moment a dependency is added it is not installed,
  so it ships nothing a local surface can read and §3.5 has no subject. The trigger fired correctly and found
  nothing, every time, for the case that motivated requiring it. Requiring a structurally silent kind buys a
  conformance obligation and no safety. It becomes REQUIRED when a registry-side surface exists; the kind stays in
  the vocabulary so that surface has somewhere to plug in. **`dependency.version_change` is now the only REQUIRED
  trigger**, because it is the one where the change is both observable and checkable — the old version is installed.

- **§4.1 required the behavior it forbids, in Claude Code.** A hook's stdout enters the agent's context, so an
  adapter printing the absent envelope on every manifest edit announces *checked, nothing found* in JSON — the
  context tax §4.1 exists to prevent, reached by obeying its letter. The contract answer and what a host emits are
  now explicitly two layers: the absent envelope is what a golden asserts against, and a Claude Code adapter emits
  nothing.

- **`MIRI-CONSUMER-041` was satisfiable only by abstention.** No producer check requires any package to ship
  `test-patterns.json`, so a consumer could be driven against a conforming wheel that ships none — or, as this
  project's own reference fixture did, one that ships it with an empty `supported_test_doubles`. In either state the
  only conforming behavior is to present no double, which is also what an inert consumer does. The check could not
  tell a careful consumer from one that never looked.

  It is now **conditional**: scored where a double is declared, excluded from both numerator and denominator
  otherwise. The `miri` fixture declares `FakeGreeter`, which gives the affirmative path something to exercise.
  `MIRI-CONSUMER-020`'s test-pattern clause is scoped the same way; its other clauses are independent, so that check
  stays scorable for every package.

  **This is the fourth instance of one defect class this month**, after `MIRI-CLI-013`, `034` and `022`: a check that
  tests the *form* of a behavior without testing that the behavior *occurs*. Found by the miri-py team implementing
  `test.author` and discovering no fixture could exercise either MUST's affirmative path.

- **Four tasks could act without knowing a package was deprecated.** §3.3's missing `lifecycle` step turned out to be
  an instance rather than a one-off — §3.1, §3.2, §3.4 and §3.6 omit it too. Rather than patch four read-orders,
  §4 gains a normative rule: **every task establishes the lifecycle facts**, whatever its read-order says. A task
  author writes the read-order for the question the task asks, and "is this package deprecated, and is its successor
  someone else's" qualifies every answer without being any single task's subject.

### Specified

- **Batching.** One observable action produces one event per package, with the binding coalescing *output* so a
  caller sees one report about one decision. Settled from implementation data rather than by adding a plural
  `subjects`, because a subject is what an event is about.

## 0.4.0 — 2026-09-06

A **minor** version: it adds. The Agent Integration Contract is new, two consumer checks are added, and every
consumer score computed before this release shifts as a result — which is precisely what a minor version is for and
why none of it could be back-ported to 0.3.1.

The specifications remain **draft** (`0.4.0-draft` in their headers). The contract is specified but the reference
binding does not exist yet, and two review findings are open against it: no schema governs the `findings` array, and
no rule maps Consumer Conformance check IDs to `findings[].level`. Both are recorded here rather than left for a
reader to discover.

### Added

- **[Agent Integration Contract](standards/consumption/agent-integration-contract.md)** — the missing *when*. The
  standard specified what an artifact ships, how a surface serves it, and what a consumer reads; nothing specified
  what causes the reading to start. A conformant producer, surface and consumer could coexist with metadata that was
  never read, and every score stayed green.

  Six **triggers**, one per Consumption Map task, naming the observable moment at which each becomes actionable. Two
  were REQUIRED at 0.4.0 — a dependency being added, and a version changing. **0.5.0 demotes the first to SHOULD**
  (this release, which began as 0.4.1);
  see that entry for why.

  The vocabulary matters and *hook* is deliberately not part of it. A hook is a host's mechanism; the word appears
  elsewhere in this standard seven times, every one describing git or setuptools. The sentence that has to keep
  working is *"Claude Code delivers a trigger via a hook; CI delivers the same trigger via a step"*, and it only
  parses if hook is theirs and trigger is ours.

- **[`agent-event-v1.json`](schemas/agent-event-v1.json)** — the event a host sends. It **closes**
  `additionalProperties`, which is the opposite of the response envelope's open root and deliberately so: the
  envelope is open so a new operation can add a payload key, and the event is closed so a host **cannot send a file
  path, a diff, or the user's source**. A prohibition that was prose is now a validation failure.

- **Two consumer checks**, `MIRI-CONSUMER-050` (a trigger with nothing to report answers absent, never empty) and
  `MIRI-CONSUMER-051` (trigger behavior is independent of what the publisher ships). Both **conditional**: a consumer
  with no binding has no trigger to answer, so by the not-applicable-is-not-a-pass rule they leave both the numerator
  and the denominator. The consumer family is now 17 checks, still summing to exactly 100 — six points came from one
  point off each of six large MUSTs, so no category absorbs the change.

  **This shifts every consumer score computed before it**, which is why it is a minor-version change and cannot be
  back-ported to a patch.

- **Attack A13** — a shipped field bidding for the agent's attention, planted in the adversarial twin and nowhere
  else. Every `.py` stays byte-identical across the fixture variants, so driving the same trigger against
  `adversarial` and `miri` isolates the metadata as the only possible cause.

### Changed

- The **Agent Metadata threat model** gains the axis it was missing. Every item in it concerned what the metadata
  *says* — narrative files inject, `api_index` can lie, execution is not sandboxed. This is the first concerning
  what the metadata *makes happen*. A package that can force a trigger has a denial-of-context channel, and a threat
  model covering only content will keep being surprised by control.

- **Consumption Map §3** gains a trigger column. It belongs there rather than in a binding document because it
  completes the map's own sentence — task answers *what*, vehicle answers *how*, trigger answers *when* — and is
  true whether or not any binding is ever written.

### Fixed

- **An IPv6 hole in the SSRF guard.** Link-local was written as `169.254.0.0/16` and `fd00::/8`. `fd00::/8` is
  unique-local; `fe80::/10`, the actual IPv6 link-local range, was **missing entirely**, so an IPv6 link-local
  address passed the guard. Now split into private, loopback, link-local and cloud-metadata.

- **A cross-document contradiction** introduced in the same session: the integration contract made `reason`
  machine-meaningful, which the Discovery Contract forbids outright. Resolved by dropping the claim rather than the
  rule — a consumer wanting to know what a package ships asks `list`, which is the operation whose answer that is.

### Verification

- `tools/check_consistency.py` gains the section-opener count rule it had been blind to for two rounds, and loses a
  bug: it counted an escaped pipe as a table-cell separator, reporting a defect markdownlint correctly accepts. A
  first attempt at the wider count rule produced **twelve false positives** on this corpus and was replaced with a
  precise one. A checker that cries wolf is worse than no checker.

## 0.3.1 — 2026-09-01

Bug fixes and clarifications. **No additions to the standard.** Every change either corrects something that was
wrong or makes an existing rule mechanically checkable.

Four of the six defects below were found by the miri-py team building an implementation against the text, and one
by scoring a real CLI. None was reachable by re-reading our own documents, which is the point worth recording.

### Fixed

- **`MIRI-SURFACE-012` required surfaces to refuse documents that six goldens require them to serve.** A clause
  added during 0.3's review demanded `METADATA_UNREADABLE` for any document that parses but fails its schema,
  while the adversarial fixtures expect those same documents served. Ten of the fifteen consumer checks are
  driven *through* the surface, so enforcing it would have disabled most of the consumer profile. The check is
  now scoped to readability, which is what its own examples, its rationale, and §3.2's verbatim rule already
  said. Reported by the miri-py team.
- **All 33 consumption checks advertised a `urls.html` that returns 404.** Linter reports link findings to that
  address, so every consumption finding pointed at a missing page. The 83 producer checks were correct; the
  consumption suite copied the wrong pattern when it was authored.
- **`cli-describe-v1.json` forbade `advisory_coverage`, which `MIRI-CLI-022` requires.** The schema closes
  `additionalProperties` and never declared the field, so a CLI doing what the standard tells it failed the
  standard's own schema. Not hypothetical: arghos had been failing validation since adopting it.
- **`schema_version` was unconstrained in three schemas, and three surfaces had diverged.** Two emitted `"1.0"`,
  one `"1"`, and all three validated. The integer-string convention lived only in prose and examples. Now pinned
  to `^[0-9]+$` in `cli-describe-v1`, `lint-report-v1` and `discovery-envelope-v1`. The `lint-report` pin matters
  most: it governs the report every `miri score` emits.
- **Five check citations pointed at sections that do not exist, or at the wrong one.** `MIRI-CLI-014` and
  `MIRI-CLI-034` cited a section with no such number; `MIRI-PY-019` used a notation that reads as a subsection;
  and `MIRI-CLI-013`, a check about the general error envelope, cited only §6 *Deprecation Metadata*.
- **The `MIRI-CONSUMER-032` namespace rule failed to detect the attack it exists to catch.** PyPI has no
  namespace component, so `pkg:pypi/a` redirecting to `pkg:pypi/b` compared as the same namespace. The
  comparison now falls back to the PEP 503-normalized package name where the type has no namespace.

### Verification made mechanical

Every gate below is new, and each exists because a defect of its exact shape shipped. The standard has four kinds
of normative artifact — check `fires_when`, spec prose, schemas, and goldens — and each pair that can disagree now
has a cross-check.

- **`tools/check_consistency.py`** — count claims against what is enumerated, sets declared complete against every
  member used, local section references, list numbering, table integrity, and check-demanded fields against every
  schema property. That last sweep is what found `advisory_coverage`.
- **`tools/check_references.py`** — gates that every check's spec citation resolves to a real document and
  section; **reports** the semantic half as a check-to-section list for a person. The split is deliberate: a
  falsely confident gate is worse than none, because nobody looks behind a green tick.
- **`tools/validate_fixtures.py`** — gains a check-versus-golden cross-check, so no check can demand refusing a
  document the goldens require served.
- **These validators had never run in CI.** All of them, plus the fixture invariants, gated nothing until this
  release. That was worth more than any single defect they now catch.

### Contributed

- **`schemas/discovery-envelope-v1.json`** and **`tools/validate_envelope_schema.py`**, from the miri-py
  implementation team, derived from a working surface rather than from this specification a second time. The
  envelope was the one normative wire format with no schema: every `MIRI-SURFACE` check validated a shape that
  existed only in prose.

  *Present on `main` but **not** part of the 0.3.1 release surface.* A schema is a backward-compatible addition,
  which makes it 0.4 material by the policy above, and the policy is kept rather than bent.

## 0.3.0 — 2026-08-28

The consumption suite: the half of the standard that says how an artifact is **read**. Versions 0.1 and 0.2
specified what an artifact ships; this specifies how an agent consumes it, and what a conformant consumer and a
conformant metadata surface are.

### Added

- **[Discovery Contract](standards/consumption/discovery-contract.md)** — the transport-agnostic wire contract.
  Eight operations in three kinds, the surface-owned envelope, absence-versus-error, caps and continuation, and
  MCP and loopback bindings.

  The central mechanism is that publisher bytes nest under a payload key, so a hostile package writing
  `ok: false` into its own document cannot forge a served, absent or failed signal. The bytes are still relayed
  intact — the surface does not edit what a publisher wrote. They are one level down, where they are data rather
  than signal.

- **[Consumption Map](standards/consumption/consumption-map.md)** — six tasks, each a read-order plus a set of
  prohibitions, with a vehicle label recording what a consumer must possess to perform each step.
- **[Consumer Conformance](standards/consumption/consumer-conformance.md)** — 15 `MIRI-CONSUMER` checks. A
  consumer is *driven*, not inspected, so every check is written against observable output.
- **[Surface Conformance](standards/consumption/surface-conformance.md)** — 18 `MIRI-SURFACE` checks in six
  categories, ordered as the path a request takes through a surface.
- **Fixtures** — ten variants built from one template, with every `.py` verified byte-identical across the
  source-sharing ones, so any difference in a consumer's behavior is attributable to the metadata and nothing
  else. Fifteen goldens covering attacks A1–A12.
- **The site renders the specifications**, with diagrams, sticky outlines, and per-target check pages for all
  four targets.

### Changed

- **Not-applicable is not a pass.** A conditional check whose condition does not apply is excluded from both the
  numerator and the denominator, rather than credited. Under the old model a CLI could earn 20 points for never
  deprecating anything.
- **Conformance is a gate, not a band.** A failing MUST makes an artifact non-conforming and no grade is
  reported — only the score, capped, to show distance.
