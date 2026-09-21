# Changelog

All notable changes to the Miri Standard are recorded here.

Versions follow the policy in [standards/README.md](standards/README.md#versioning): a **major** version marks a
breaking change, a **minor** version a backward-compatible addition, and a **patch** version bug fixes and
clarifications only. That policy is a contract with implementers, and it is worth keeping strictly: a reader
should be able to see `0.3.1` and know it contains no additions without having to check.

While the major version is 0 the standard is in initial development, so a **minor** bump may carry a breaking
change ([Semantic Versioning §4](https://semver.org/#spec-item-4)). Where one does, the entry says **BREAKING** in
its first line and names what breaks. From 1.0.0 onward a breaking change takes a major bump.

## 0.7.0 — unreleased

**BREAKING.** The tier arithmetic changes: `scoring-v2.json` withdraws v1's rule that a parked T2's share is parked
in T1, in favour of renormalizing over the tiers a check declares. Every tiered score moves.

Otherwise, coverage. The `MIRI-PY` family had 43 checks, 100 weight and no artifact that falsified any of them — the
founding family, and the only one with nothing to test against. It now has nine wheels and seven goldens.

### Changed

- **BREAKING — `scoring-v2.json` supersedes `scoring-v1.json` for the tier arithmetic.** A check now earns
  `weight × (shares of its live tiers up to tier_earned) ÷ (shares of ALL its live tiers)` — renormalized over what
  the check *declares*, minus a parked T2. Under v1, `MIRI-PY-007` at weight 5 declaring only T0 and T1 earned
  `5 × (0.2 + 0.6) = 4.0`; it now earns 5.0. A check that declares only T0 and T1 has no higher tier to earn, and
  docking it for absent tiers scores it against a schedule it never claimed.

  **This is a withdrawal, and the record matters more than the rule.** v1 was not silent: its `shares` description
  said a parked T2's share is parked in T1, which is a complete rule producing different numbers. When the reference
  implementation scored a wheel 47/48 against this standard's 45.6/48, **45.6 was what v1 specified and 47 was the
  implementation diverging from it.** The draft that introduced the v2 field deleted the v1 sentence and asserted no
  prior rule had existed — framing the adoption of an implementation's arithmetic as a clarification of a schema
  that had said nothing. It had said something. A panel caught it against `origin/main`.

  `scoring-v1.json` stays published and frozen at its 0.6.0 bytes, because anything that scored under it scored
  under a real rule and must still be able to cite it. v2 also states two things v1 left to the implementation:
  rounding is half-up, applied once at the end, and a **failing** tiered check contributes zero rather than its
  earned tier share.

### Added

- **[`examples/fixtures/python/`](examples/fixtures/python/README.md) — the greetlib wheel fixtures.** Nine arms
  built from one package source: two conforming releases and seven adversarial. `conforming-1.0.0` is the part that
  did not exist before, because `MIRI-PY-030` compares the public surface across releases and nothing in this
  repository had ever shipped two wheel releases of one package. The check fires now, for the first time.
  Counting every active check named by a golden in any of the three suites: untested weight fell from 237 of 400
  to 187, and `MIRI-PY` went from 0/43 checks with material to 18/43, 0 weight to 50. (Earlier drafts of this
  entry said 234 → 195 and 13/43, from a scan that did not count a golden's `also_expected` checks.)
  One arm was removed rather than kept: `support-1.1.0` was written for `MIRI-PY-023` and `033`, and every way of
  violating those two is also `lifecycle-v1`-invalid, so `MIRI-PY-018` fires first and their 4 weight is not
  independently reachable. Recorded in the suite's README, because a weight that cannot be earned separately is
  worth knowing before anyone reads it as measuring something.
- **The definitions wheel conforms, and the release gate enforces it.**
  `miri-standard-checks` now ships its own `agent-metadata/` — `sdk-manifest.json`, `lifecycle.json`,
  `changelog.json`, `api-graph.json` and a first-release `migration-guide.json` omission that is correct rather than
  missing — written by `tools/build_checks_wheel.py` at build time from the definitions it carries, never by hand.
  It scores 98 of an effective 53.0 with zero MUST failures, and `publish-checks.yml` fails the release if that
  regresses, pinned to a fixed `MIRI_PY_REF` so the gate cannot move under the artifact. Dogfooding the standard on
  the only wheel this repository publishes found six things worth telling miri-py, written up in
  [`standards/feedback/`](standards/feedback/README.md) — including a report that told the reader a file was
  *still owed* in the same run that scored its absence as correct.
- **`tools/validate_python_fixtures.py`** asserts each arm still carries its defect — against the built wheel's own
  metadata rather than a linter's opinion, so the gate holds with no linter installed — and that the control carries
  none of them, which is what makes a finding attributable. Mutation-tested.
- **`tools/score_python_fixtures.py`** grades a linter against the goldens on attribution: a finding counts only if
  it names the check *and* points at the declared evidence. Its self-test rejects nine ways of gaming it, two of
  which the grader itself failed first:
  evidence pooled across a case (a shotgun report scored 6/6) and findings credited without checking which arm
  they came from.

### Fixed

- **`changelog-v1.json` rejected the example this specification publishes.** It closed `additionalProperties`
  without listing `$schema`, so the *conforming* fixture arm failed `MIRI-PY-041` on a document written from §4.7
  verbatim. `lifecycle-v1` and `api-graph-v1` already allowed the pointer; the newer schemas did not — the drift a
  new schema inherits when a convention lives in the examples rather than in the schemas. Found on the fixtures'
  first run, which is what they are for.
- **`MIRI-PY-009` had no anti-vacuity clause.** An all-zeros migration guide validates, so presence and schema
  validity passed a document describing no migration at all. `MIRI-PY-008` was given such a clause in the
  vacuous-conformance round and `009` never got the equivalent. It keys on a *measured* delta, since a release that
  genuinely changed nothing is an honest all-zeros case.
- The doc linters were scanning generated fixture arms (79 → 114 files); build trees are excluded and gitignored.
  `opensource.org` 403s every non-browser request, so the README's MIT link joins `gnu.org` in the link-check
  ignore list, with the reason stated.

- **`lint-report-v1` outcomes gain `evidence`** — an array of `<document>:<field>` strings naming what a finding
  points at. A report recorded *which* checks failed and nothing about *why*, so attribution could not be graded
  from a conforming report and both golden harnesses invented a submission shape; a harness needing non-standard
  input is one nobody runs. The form is not invented — it is what the reference linter already emits for its best
  cases. `score_python_fixtures.py --reports` now grades conforming reports directly, falling back to
  `violation_detail[].location` so linters that predate the field are still gradeable.

  Measured immediately: miri-py 0.6.0 reports every fixture case correctly — right checks, right arms, nothing on
  the control — and satisfies **two goldens of six**, both of them cases where the evidence is the document itself
  and the document-only form is what the check's own `violation_unit` names. Detection and attribution are different
  properties, and until this field existed the standard could only ask for the first.

## 0.6.0 — unreleased

**BREAKING.** The check schema is bumped to `check-v3.json` because `weight` changes meaning for any definition that
declares `tiers`, and every score moves once the substance-bearing checks are tiered. What has landed so far is the
schema foundation; the check definitions themselves follow.

### Changed

- **BREAKING — `check-v3.json` supersedes `check-v2.json`.** Two changes of meaning: a substance-bearing check may
  declare [`tiers`](schemas/check-v3.json) and a `conformance_tier`, under which its `weight` is a ceiling earned as a
  cumulative schedule (T0 exists, T1 true, T2 covers, T3 current) rather than a bit; and every `fires_when` and tier
  clause must be a pure function of the artifact. Definitions without `tiers` mean exactly what they meant under v2.
  All 123 definitions now declare `$schema: …/check-v3.json`. `check-v2.json` is retained frozen at its 0.5.0 bytes
  — and its closed `additionalProperties` is the point: a v2-pinned linter handed a tiered definition fails loudly
  instead of scoring it as binary. Design settled with the miri-py team (`substance-and-freshness-answers-1.md`, Q1):
  pass/fail is derived as `tier_earned >= conformance_tier`, default **T1** — the MUST boundary sits at the *lie*, not
  at thinness, so no currently conforming wheel non-conforms for being thin on the day tiers ship, and one shipping
  filler does.
- **`scoring-v1.json` gains `conformance.tiers`.** The four tier shares (`0.2 / 0.3 / 0.3 / 0.2`, provisional
  committee numbers) and the T2 activation trigger (**25 wheels from 10 independent publishers**) live here once, as
  schema defaults, never per check. T2 ships defined but weightless with its share parked in T1: the only corpus
  available was seven wheels, three with an `api_index`, two of those the proposer's own — percentiles over that set
  are habits reflected back, not calibration. The trigger is a count, not a date.
- **Driver semantics stated normatively — `scoring-v1.json` `conformance.coverage`.** Five clauses, every one
  `const: true` so a scoring configuration cannot opt out: every defined check reports an outcome; a check the
  implementation does not verify is *forfeited*, never passed and never excluded; a forfeited MUST withdraws the
  grade; a verification that cannot run fails loudly; coverage is reported per family with a named blocker per
  uncovered check. 0.5.0 defined forfeiting for capability gaps; this extends it to implementation-coverage gaps,
  which is what makes a coverage percentage comparable between two linters. `lint-report-v1.json` gains the skip
  reason `not_implemented` and a required `blocker` beside it. Proposed by miri-py from running their kernel; the
  third clause was added in our response, because without it an implementation covering 24 of 43 CLI checks
  reported `24 pass / 0 fail` instead of `undetermined`.
- **The conformance kernel recorded as a reference artifact** — `reference/conformance-kernel/` holds
  `rule-v1.json` and `operators-v1.json` unmodified from miri-py (pinned at `afc51324`), with the promotion test that
  would make them normative. Not vendoring the 51-file rule corpus: a snapshot goes stale on their next commit and a
  pinned pointer does not.
- **The fixture recipe is normative and its inputs are checksummed.** `examples/fixtures/checksums.json` hashes every
  file under `src/_template/` and `metadata/`, and `validate_fixtures.py` fails on drift. Wheel bytes are deliberately
  not asserted — the build is not reproducible — so the guarantee is the one the recipe can keep: matching inputs plus
  `build_fixtures.py` is the same fixture. No binaries shipped.
- **`lint-report-v1.json` outcomes gain `tier_earned`** — the highest tier whose every clause held. Explains a
  status, never replaces it; the verdict vocabulary stays pass / fail / forfeit / exclude.
- **`MIRI-PY-016` withdrawn** (`withdrawn_in: 0.6.0-draft`). Its both-ways index/file join is `014`'s T3 clause and its
  2 weight moved there — both halves in one change, per the rule that an ID leaves only by withdrawal. The file and ID
  remain; "absorbed" was the proposal's word and was wrong.
- **Twelve weight changes, so the target still sums to exactly 100 with four new checks.** `007` 6→5, `008` 5→4, `012`
  3→2, `019` 4→3, `021` 3→2, `028` 4→3, `029` 4→3, `030` 5→4, `033` 3→2, `038` 2→1; `014` and `015` 4→5 each,
  taking `016`'s weight. Categories: B 24 (unchanged, `041` inside), C 12 (unchanged), D 25→**23**, E 25→**28**,
  F 10→**9**. Every published score moves — the BREAKING line at the top is earned here, not only by the schema.
- **The checklist's category summary was stale and ungated** — it still read A 10 / B 20 / C 10 against actual
  4 / 24 / 12, surviving because its wrong rows totalled 100. Rewritten to the real numbers with the gate-checked
  headings. Checklist stamp `0.2-draft` → `0.3-draft`: 43 active checks.

### Added

- **Four checks, `MIRI-PY-041`–`044`** — the freshness contract's three staleness classes made decidable, plus the
  document they read. `041` *changelog.json valid* (B, 3, conditional on a previous release — the `009` pattern).
  `042` *version silence* (E, 3): `releases[0].version` equals the wheel's version, the single rule that would have
  caught the originating incident. `043` *uncovered delta* (E, 2, `previous-release`): every interface in the measured
  `api_index` delta is named in an entry. `044` *dangling claim* (E, 2): every named symbol resolves in the current or
  previous `api_index`. All MUST. Stamp drift, the fourth class, was already `MIRI-PY-011`.
- **Tier tables on the five substance-bearing checks** — `007`, `014`, `015`, `017`, `037`, all at `conformance_tier:
  T1`. Presence is now T0 and earns a fraction of the weight, never all of it. `007`'s T1 requires every
  `common_imports` line to parse *and resolve*: `from _version.py import WheelContext` is schema-valid text and not a
  valid import, and it now fails a MUST — including in the proposer's own flagship, which they asked for. The
  Deprecation & Lifecycle checks `028`–`034` are deliberately **not** tiered: that family is already decomposed into
  discrete joins (subject existed / replacement resolves / delta covered / versions monotonic), which is the tier
  ladder as separate checks. Tiering them would score the same join twice.
- **Spec §4.7** in the Agent Metadata specification defines `changelog.json`; §8.1 lists it among the required files
  from the second release.
- **The definitions as a data-only wheel, `miri-standard-checks`.** `tools/build_checks_wheel.py` stages the 123
  definitions and 16 schemas at build time — the repository stays the source of truth — and `publish-checks.yml`
  attaches the wheel to the GitHub Release at every release tag, after `make validate` and `make consistency` gate
  the tree it is built from. `manifest.json` pins the release, the full commit sha and a content hash, so a report
  scored from the wheel still carries the `checks_commit_sha` it must. Provenance is attested and `SHA256SUMS`
  published beside it: a definitions package is a supply-chain root. Answers miri-py's 2026-08-18 note; PyPI later,
  other registries declined until a consumer exists. Not a version bump — a derived output, like the site. The
  wheel is scored by the reference linter in the same job, through the one gate `score_sample.py` already has
  rather than a copy — advisory until two structural failures close: `MIRI-PY-020` has no vocabulary for an
  artifact hosted outside an index, and the package ships no `agent-metadata/` yet.
- **[`changelog-v1.json`](schemas/changelog-v1.json)** — machine-readable release history, `changelog.json`, mirroring
  the CLI family's `changelog --since` payload (`MIRI-CLI-029`) so both targets share one shape. Conditional on a
  previous release existing, the `030`/`034` pattern. It makes three staleness classes decidable: *version silence*
  (`releases[0].version` equals the wheel's version — the single rule that would have caught the incident that
  produced this proposal), *uncovered delta* (every removal in the measured API delta has an entry), and *dangling
  claim* (every named symbol resolves in the current or previous `api_index`). The wheel metadata set had seven
  schemas and none was a changelog, so "what was fixed" had nowhere to live.

- **A check verdict MUST be a pure function of the artifact.** `fires_when` in
  [`check-v3.json`](schemas/check-v3.json) now requires every clause to be decidable from the artifact under test
  and, where the check declares `requirements`, from the capabilities those name — a previous release, the network,
  execution. No clause may depend on model inference, on a judgment of style or quality, or on any other
  nondeterministic input. Two conformant linters given the same artifact reach the same verdict bit for bit, and
  that is the only reason a score is comparable between implementations at all.

  **This is an addition, not a clarification, and it was first filed as one.** The draft of this entry called it a
  clarification because all 122 active definitions already satisfy it and no score moves — both true, and neither
  sufficient. It introduces a MUST that narrows what a check definition may be: a `fires_when` clause resting on
  model judgment would have validated before and is non-conforming now, and a rule forbidding something previously
  permitted is new even when nobody has done it yet. The supporting argument was circular as well, leaning on the
  check-authoring guidance under `.claude/skills/` — internal tooling, not a normative source — while citing the
  absence of any normative statement as the reason to write one.

  Raised by the miri-py team, and their argument for settling it before the rest of their proposal is why it comes
  first: the place a future editor would reach for a language model is a check about whether documentation is any
  good, so the prohibition wants to exist before the checks that would tempt it.

  No schema bump. JSON Schema cannot enforce this; it binds the check author and the linter and is verified by
  review rather than by validation. A consumer holding the previous reading of `check-v2.json` computes identical
  verdicts and identical numbers for every definition that declares no `tiers`.

### Fixed

- **The site stopped publishing on changelog-only and spec-only merges.** `publish-site.yml` triggered on checks,
  schemas, `docs/`, `website/` and the generator — not on `CHANGELOG.md` or `standards/*/*.md`, both of which the
  generator renders. Both paths added. Found while confirming this release would publish; it would have, but the
  next small edit would not.
- **The Agent Metadata specification gained §4.7 without a header bump** in the commit that added it — `0.2-draft`
  → `0.3-draft`. Our omission; recorded rather than quietly tidied.

### Deferred by design, not undecided

Every ask of the substance-and-freshness proposal is now decided and built — the four staleness classes, the
document, the tier schedule, and the calibration policy. What is deliberately *not* live is **T2's weight**: the
covers tier is defined on four checks and moves no score until the corpus of published conformant wheels reaches
**25 wheels from 10 independent publishers** (`scoring-v1.json` `t2_activation`). The only corpus available was seven
wheels, three with an `api_index`, two of those the proposer's own; percentiles over that set would be habits
reflected back, not calibration. The trigger is a count, not a date, and until it fires T2's share sits in T1.

Owed by the reference implementation, not blocking the release: tier tables for the `cli`, `surface` and
`consumer` families under the same schedule, and the multi-invocation comparison operator — the first of the three
operator classes whose absence keeps `rule-v1`/`operators-v1` a reference artifact rather than a normative one.

## 0.5.0 — 2026-09-10

**BREAKING.** The first release to earn that label. Two changes alter every conformance score and both
affect anything vendoring the check schema: `conditional` reverses meaning, and three checks move out
of the score entirely. See **Changed** below for what breaks and what to do about it.

It began as 0.4.1 — four fixes from the first binding — and grew through the Production Maps, an executable
CLI fixture suite, six adversarial review panels, and an implementation report that arrived while the panel
findings were being closed. All of it ships as one release because none of it was ever published: the last
tag-equivalent is 0.4.0 on `main`, which is what the reference linter pinned.

### Changed

- **BREAKING — `conditional` semantics reversed, and three checks now gate rather than score.** Both change
  every conformance score, and both affect anything vendoring the check schema — now
  [`check-v2.json`](schemas/check-v2.json), bumped for exactly this reason.

  `conditional: true` previously meant a check *"scores its full weight automatically when the condition does
  not apply"*. It now means the check is **excluded from both the numerator and the denominator**. Not-applicable
  is not a pass: awarding weight for an absence let an artifact collect points for having nothing to declare.
  Twenty-four checks across three targets are affected, and a linter that implemented the old reading produces
  different numbers for every artifact after re-syncing.

  `MIRI-PY-001`, `002` and `003` gain `scoring: gate` and weight 0. They remain MUSTs and still make an artifact
  non-conforming when they fail; they are no longer measured. Six points moved to `MIRI-PY-007` and `008`
  (+2 each) and `014` and `015` (+1 each). `check-v2.json` gains the `scoring` field, because weight 0 already
  meant "extension check" and one value cannot mean two things.

  Reported by the miri-py team from scoring five unrelated wheels that returned an identical 8/10 in the
  Packaging Baseline. The interaction is the part worth knowing: renormalizing shrinks the denominator, so a
  constant numerator becomes a **larger** share — the Baseline went from 8% of a fixed 100 to about 14% of a
  typical applicable 58. Shipping the renormalization alone would have nearly doubled the fraction of a score
  carrying no information. Both sides of the discussion had that backwards at first. Gating brings it to ~4%.

  Reports MUST now carry `effective_denominator`, `excluded` and `forfeited` beside a conformance score, and a
  forfeited MUST yields the new `undetermined` grade rather than a claim of conformance.

#### To upgrade

The algorithm is **not** in this entry. It is in
[`standards/python/linter-checklist.md`](standards/python/linter-checklist.md) and its
[CLI twin](standards/cli/linter-checklist.md), under **Scoring Model** — excluded vs forfeited, the precedence
rule for checks that are both conditional and capability-gated, `undetermined`, and the no-coverage-floor
prohibition. Read those, not this. An earlier version of this section named the changes and linked to nothing,
which meant a reader had to diff against 0.4.0 to reconstruct their own upgrade.

1. **Re-pin.** [`checks_commit_sha`](schemas/lint-report-v1.json) now requires a full 40-character lowercase sha.
   A short sha or a tag is a hard validation failure — if you pin `cc5d0a4` today, your reports stop validating.
   The release name goes in the new `checklist.standard_version` instead.
2. **Re-point at [`check-v2.json`](schemas/check-v2.json), and re-sync the corpus.** The check schema is now
   versioned, because `conditional` reversed meaning without one byte of validating *content* changing — a schema
   is an interpretation contract and this one's contract changed. Every definition declares
   `$schema: …/check-v2.json`, and v2 requires it, so a v2 corpus **fails** against a vendored v1 and a v1 corpus
   **fails** against v2. The pairing that used to validate and score wrongly now breaks on both sides.
   [`check-v1.json`](schemas/check-v1.json) is retained frozen and still describes 0.4.0 semantics: a consumer
   pinned there is old, not wrong, and stays internally consistent.
3. **Change the scorer**, in this order: exclusion leaves both sides of the ratio; the precedence rule decides
   which of exclusion or forfeit applies to the ten dual-flagged checks (five python-wheel, five CLI); a forfeited
   MUST yields `undetermined`; `scoring: gate` checks are in neither sum and a failing one is non-conformance,
   which is representable **only** through `must_failures`.
4. **Change the report.** [`lint-report-v1.json`](schemas/lint-report-v1.json) now requires
   `scores.effective_denominator`, `scores.excluded`, `scores.forfeited` and `must_failures`; `must_failures`
   being non-empty forces `grade: non-conforming` and caps `conformance` at 74; a `skipped` outcome must name its
   `skip_reason`; `grade` gained `undetermined`; `conformance` is bounded 0–100.
5. **Decide about already-published scores.** Every conformance number computed under 0.4.0 semantics is wrong
   under these. The standard does not tell you whether to retract or restate them; it tells you they changed.

**What you will see that looks wrong and is not.** `MIRI-PY-015`, `036` and `040` are MUST-level, require
`execution`, and are not conditional — so a run without execution forfeits three MUSTs and every artifact reports
`grade: undetermined` rather than a band. That is the correct answer: a wheel's runtime behavior cannot be verified
without running it. Do not "fix" it by suppressing forfeits in grading; run with `execution` available, or accept
that a static-only run reports a score and no verdict.

**What will not fail loudly if you skip it.** The three newly required `scores` fields catch a linter that did not
update its *serializer*. Nothing in any schema relates `scores.excluded` to the `outcomes` that were excluded, so
a linter that adds the fields and does not change its *arithmetic* validates clean and reports wrong numbers.
The guard against that is the [`check-v2.json`](schemas/check-v2.json) bump itself, together with the `$schema`
each definition now declares: a linter still applying v1 arithmetic is reading a corpus that says v2, and the
mismatch fails in both directions. It is a tripwire, not a proof — nothing can prove your arithmetic changed.
(An earlier draft of this entry named a `semantics_version` field here. That field was proposed and rejected
during this release — a single global fact copied into 119 files becomes 119 statements that can each go
stale — and the schema bump replaced it. It does not exist; do not look for it.)

### Added

- **`package.replaced` — a seventh trigger kind**, with [Lifecycle and Security Metadata
  §9.6](standards/python/lifecycle-security-metadata.md) and `MIRI-CONSUMER-052` behind it.

  A purl identifies a name and a version, not a byte stream. Uninstall a distribution and install different bytes
  at the same version and nothing a consumer would compare has moved. §9.1's adversary — a package trustworthy
  when adopted and malicious later — already covered this, but every delivery mechanism it named was a
  *publication* event; this one publishes nothing.

  Raised from a maintainer's own workflow: developing a wheel means reinstalling at the same version many times an
  hour, because nobody bumps a version on every edit. That makes it a cache-invalidation problem *and* a trust
  problem, and the trust half is the one the standard owed an answer to. §9.4 already says structured metadata is
  more dangerous than plain documentation because it invites a consumer to lower its guard — which means Miri
  raises the value of this attack. That is a cost of the standard existing, and writing it down is the only
  optional part.

  The exposure is worst where §9.5's foundation is absent: PEP 740 attestation is the only field tying an artifact
  to an independent identity, `MIRI-PY-005` is network-gated and conditional, and a locally built wheel carries
  none — correctly. `MIRI-CONSUMER-052` carries the prohibition that falls out: **no trust determination survives a
  replacement**. Stated as plainly, the trigger is *not* a verification — where no attestation exists, re-reading a
  hostile artifact yields fresher hostile metadata.

- **CLI conformance goldens and a scoring harness.** `examples/fixtures/cli/expected/C1`–`C11` state which check a
  linter must report, on which arm, and — after the harness was rebuilt — pointing at which evidence.
  `make score-cli-linter` rejects seven ways of gaming it.

- **`scoring: gate`** in [`check-v2.json`](schemas/check-v2.json), and the invariant coupling it to
  weight 0 and MUST level — enforced in the schema itself, not only in a repo-local script vendors
  do not run.

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

### Fixed

- **§4.3 of the Agent Integration Contract was unsatisfiable.** It defined trigger behavior as four things a
  publisher may not influence, two of which — *whether* findings are carried and *how many* — are necessarily
  determined by the metadata, since every finding derives from a shipped field. `MIRI-CONSUMER-051` fired on the
  behavior the `E3` golden mandates: pass the golden, fail the check. The regulated quantity is whether the **read
  happens**, never what the read finds, and the evidence that a trigger fired is §4.1's absent envelope. That also
  dissolved a finding tracked separately as needing a third fixture arm — `E3` could not discriminate because the
  rule pointed at the wrong observable, not because the fixture was short.

- **`MIRI-PY-008` and `MIRI-PY-007` admitted empty content arrays.** Reported by the miri-py team from scoring five
  real wheels; verifying the report found the second instance, in the check the report assumed was safe. Fifth
  instance of one defect class, and the first found by running checks against real artifacts rather than reading
  them. See `standards/feedback/`.

- **Four gates that had never run, or ran wrong.** `.githooks/pre-commit` — the file `CLAUDE.md` tells a fresh
  clone to enable first — had a `NameError` and a row regex that read 32 of 40 rows, and had never completed. The
  `--since` validator was defeated by its own regex. `changelog --since` emitted records where CLI Spec §5.2 wants
  string arrays. §6.1 mapped `dependency.add` to a moment the contract's own footnote says has nothing to read.

- **The CLI linter harness graded a set of strings.** Six independent cheats reached a perfect score, one of them
  by emitting every golden's check ID under the hostile arm's name having opened no fixture. Grading now requires
  attribution: the right check *and* the evidence that golden declares.

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

- **That rule's same-session exemption is keyed on bytes, not on the session.** As first written, a consumer that
  had already established the lifecycle facts "in the same session" need not re-fetch them. On a `package.replaced`
  notice the consumer *does* hold them — for the previous artifact's bytes — so the exemption licensed precisely
  the reuse [`MIRI-CONSUMER-052`](standards/consumption/checks/MIRI-CONSUMER-052.yaml) forbids. **Consumer
  implementers:** if you cache these facts per session, a replacement must invalidate that cache.

- **The conformance gate no longer reads a field no schema defines.** `tools/score_sample.py` gated on
  `is_conforming`, which appears in no schema and no specification and survived on `additionalProperties: true`.
  It now derives the verdict from schema-defined fields — `must_failures` empty, and `grade` outside
  `{non-conforming, undetermined}` — a coupling [`lint-report-v1.json`](schemas/lint-report-v1.json) already
  enforces. It also validates each report against that schema, and **warns rather than fails**: 0.5.0 newly
  requires `effective_denominator`, `excluded` and `forfeited`, so gating would fail a linter for 0.5.0 support
  that is legitimately still in flight.

### Specified

- **Batching.** One observable action produces one event per package, with the binding coalescing *output* so a
  caller sees one report about one decision. Settled from implementation data rather than by adding a plural
  `subjects`, because a subject is what an event is about.

- **Release tags carry no `v` prefix** — `0.5.0`, not `v0.5.0` ([CONTRIBUTING.md](CONTRIBUTING.md)). The tag is for
  humans and GitHub releases only; the machine-readable pin is `checks_commit_sha`, which requires a 40-character
  sha and rejects a tag outright. Matching `standard_version` exactly makes a report's version a usable git ref.

- **Per-check revision history stays editorial** ([schemas/README.md](schemas/README.md)). `added_in` records birth
  and nothing records revision, by decision: git is the revision record and `checks_commit_sha` makes it
  addressable, so "what changed between two reports" is a diff rather than a claim. A hand-maintained `changed_in`
  would fail the way `semantics_version` did — one global fact copied into 119 files becomes 119 statements that
  can each go stale.

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
