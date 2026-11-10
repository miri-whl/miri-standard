# Design Notes and Decision Records

This directory holds working notes in which specific design decisions for the standard were reasoned through. Each
decision is recorded as a paired **proposal** and **response**: a proposal that surfaces a gap or tension, and a
response that decides how the standard resolves it, with the disposition and rationale written down so the reasoning
survives.

## How to read these documents

The Miri Standard and its reference linter (`miri-py`) are built by the same single maintainer (Emiliano Berenbaum,
@y3bishop3y). The "implementation team" and "maintainers' response" labels in these files denote **two perspectives
held deliberately apart**, not two independent organizations or a plural body:

- the *implementer* perspective surfaces a problem found while building the linter — a place where the standard is
  underspecified and conforming tools would have to invent semantics;
- the *standard* perspective decides how to close that gap in a way that keeps independent implementations
  interoperable.

Separating the two forces every decision to be justified from both sides — the side that has to implement it and the
side that has to keep it coherent. That is the value of the format, and the honest way to read these files is as
**decision records authored from two viewpoints**, not as correspondence between separate parties or as a record of
outside review.

The project is early (0.2-draft, Incubation) and has a single maintainer: where these documents describe what the
standard decides, that means the maintainer acting in the standard-governance role, not a chartered body. Outside
proposals and review are welcome; when they arrive, they will be recorded here the same way, and attributed to their
authors.

## Contents

Decisions worked through so far, each as a proposal plus the response that settled it:

- `miri-py-scoring-model-proposal.md` / `miri-standard-response-scoring-model.md` — the two-score architecture
  (a Conformance score and a Health score).
- `count-normalization-proposal.md` / `miri-standard-response-count-normalization.md` — how the health baseline
  treats artifact size (raw counts in the score; population and density as report-level data).
- `check-requirements-proposal.md` / `miri-standard-response-check-requirements.md` — the machine-readable
  `requirements` field for check skip semantics.
- `upstream-artifact-publishing-feedback.md` / `miri-standard-response-artifact-publishing.md` — publishing the
  check definitions as a versioned artifact. Answered a month late: tags yes, a gated data-only wheel on GitHub
  Releases yes, PyPI later, npm and crates declined until a consumer exists.
- `vacuous-conformance-proposal.md` / `miri-standard-response-vacuous-conformance.md` /
  `vacuous-conformance-answer.md` / `miri-standard-answer-vacuous-conformance.md` — sections that cannot
  discriminate: empty content arrays passing shape-only checks, and the weighting of the Packaging Baseline.
  Four documents rather than two, because the exchange ran a second round: the proposal was found to contain an
  error of its own, and the answer corrected an inference the response had not yet challenged.
  `vacuous-conformance-answer-2.md` closes it: the pin format after a tag, and a prediction placed on
  record before the measurement that will test it.
- `0.5.0-measured-rerun.md` — miri-py's implementation report against 0.5.0, closing the loop
  `vacuous-conformance-answer-2.md` opened. Five real wheels rescored at the release pin; every figure landed on the
  number filed in advance, so the measurement did not contradict the prediction. Reported, not yet answered.
- `conformance-interop-contract-proposal.md` / `miri-standard-response-conformance-interop.md` — miri-py offers
  the interop contract their linter now runs on: rule files owning verification, a four-operator vocabulary
  executing them, and driver semantics whose core is forfeit-never-silence. The two schemas it delivers are
  recorded verbatim under `conformance-interop-schemas/`. The response accepts the driver semantics and adds the
  clause the proposal left out — a forfeited MUST withdraws the grade rather than discounting the score, which
  makes all three of their behavioral families `undetermined` rather than "N pass / 0 fail". It declines to freeze
  the operator vocabulary while a third of the behavioral checks need operator classes that do not exist, and
  sets the promotion test. Fixture recipe blessed and checksummed; no binaries shipped. Nothing in `schemas/`
  derives from the delivered files.

- `miri-standard-response-compare-operator.md` — our response to miri-py's `compare` draft (the first of the three
  missing operator classes). Shape accepted, all five of their questions answered favourably, and three findings:
  their `MIRI-CONSUMER-051` rule is satisfied by a consumer that never fires, because it compares two arms and
  anchors neither; two of the four checks need a per-arm `env` the grammar does not have; and a rule covering one
  `fires_when` clause of three currently reports pass, which is the vacuous pass at rule level. The first finding is
  a defect in **our** check, not their rule — `051`'s clause 1 is weaker than the `E3` golden it points at, and
  drafting against it is what exposed that.

- `miri-standard-dogfooding-the-definitions-wheel.md` — what happened when the standard's own definitions wheel was
  scored by the reference linter. Three of miri-py's fixes confirmed from a clean install; six findings back,
  three of which correct earlier drafts of this same document. The
  first is the one that matters: the report's layout section advises shipping a document the report's own check
  excludes, and the empty version of that document validates — so following the advice manufactures the vacuous
  artifact. The second is that layout guidance fires no check, which is why we missed a real misplacement. The third
  was ours, and is fixed: `scoring-v1.json` declared the tier shares without the formula.

- `miri-standard-response-checks-wheel-gaps.md` — answers miri-py's four blockers to depending on the
  definitions wheel rather than copying out of it: the checklist revision per family, a `content_sha256`
  that hashed the staging tree instead of the package, two families sharing one directory with nothing to
  tell them apart, and the fixture pack that was never shipped. All four invisible from inside a checkout.

- `miri-standard-note-integrity-semantics.md` — what a linter may conclude from `MIRI-PY-001` and what it may
  not. Passing means the archive agrees with its own `RECORD`, which is carried inside the archive it
  describes, so it detects corruption and an edit nobody hid — not a deliberate one. Provenance is decided
  outside the artifact. Records why `MIRI-PY-005` was considered for MUST and left at SHOULD.

- `miri-standard-response-api-graph-to-scip.md` — miri-py proposed replacing `api-graph.json` with SCIP. The
  graph is withdrawn outright and the index is a SHOULD (`MIRI-PY-045`), with the format named and the indexer
  not; the consumer-facing swap is declined on their own measurement, and the reader dependency moved to the
  surface, where a server can afford a decoder. Corrects their §4: `MIRI-PY-043` already asks for a signature
  comparison, and the field it needs is optional and unpopulated in our own sample — which is why their delta
  detection could only diff key sets.

- `miri-standard-response-scoring-denominator.md` — miri-py implemented scoring-v2 and hit a report that
  fails the standard's own wire schema. The blocker is real; the diagnosis was one field off. The numerator
  had no field at all, `effective_denominator` is an integer by definition, and this schema used the word
  *denominator* for two different quantities. Records why widening the wire field was declined.

- `miri-standard-response-check-references.md` — accepts miri-py's finding that 21 PEPs are named in check
  prose and missing from that check's `references`, and gates the rule so it cannot reopen. Asks them to
  relabel their fix card from "Defined by" to "References", because four of the 21 are tooling
  instructions, cautionary examples, or cross-ecosystem prior art rather than the authority for the rule.
- `miri-standard-response-api-index-keys.md` — miri-py reports that `api_index`, keyed by bare name, dropped about
  1,760 definitions of a generated client, because 431 endpoint modules each define `sync` and the index holds one
  entry per name. Accepted, with the lead finding reversed: the Discovery Contract §3.6 already defines the key space
  as **dotted** and gives `Greeter.greet` as its example, so the schema, which admits only a bare identifier, never
  implemented the standard's own position. Nobody noticed because the keys that escape the pattern escape validation
  with it, which is their second ask and is seven `patternProperties` blocks rather than one. Resolved by nesting
  module members instead of flattening them into the key, so no bare-name consumer breaks. Adds the finding the
  report did not carry: `MIRI-PY-043` measures its delta *from* the index, so the dropped symbols fall outside the
  population of the MUST that exists to catch silent removal.

- `miri-standard-reply-conditional-exclusion.md` — miri-py accepts both corrections and reports that the vacuous
  pass is worse than described: an empty delta is classified `condition_not_applicable`, which the vocabulary makes
  an *exclusion*, so a release that silently deleted a module was "awarded six points". The finding holds and the
  arithmetic does not. Awarding the weight is the PRE-0.5.0 rule, which `check-v1.json` carries along with its own
  SUPERSEDED label; `check-v3.json` and `scoring-v2.json` both say an excluded check leaves the numerator and the
  denominator. So nothing is credited, and the obligation vanishes from the ratio instead, which is the defect their
  repair actually describes. Their distinction is adopted: an empty delta is an exclusion, a delta over a surface
  known to be partial is a forfeit. Answers the declaration shape they are blocked on with `surface_coverage` and
  `surface_scope`, modelled on `advisory_coverage` in `cli-describe-v1.json`. Sizes the open question beyond this
  exchange: 15 of 43 active MIRI-PY checks are conditional and carry 39 of the 100 points, so the two scoring models
  diverge on most artifacts, not on this pair.

- `miri-standard-reply-coverage-is-not-a-claim.md` — miri-py withdraws the "six points awarded" finding (the cause
  was a `SkipReason` docstring repeating the pre-0.5.0 sentence, not the vendored schema we pointed them at) and
  returns a sharper one: our `MIRI-PY-043` is wrong *today*, because it excludes on any empty delta while an empty
  delta over a collided index settles nothing. Accepted, and the 0.8.0 draft of the fix is recorded as half a fix:
  it forfeited for a declared surface and restated the defect for the default case. A claim of complete coverage is
  a claim and not evidence, so an empty delta now settles the condition only where `MIRI-PY-036` verified coverage.
  Answers their #25 from the `fires_when` purity rule they themselves raised at 0.6.0: an environment-dependent
  lookup is not available, so the false negative stands. Leaves #38 to the maintainer, while recording the identity
  hazard inside it.

- `miri-standard-reply-collision-is-static.md` — miri-py answers Q7 with a measurement: collision-freedom is
  decidable from the wheel alone, and 17 of their own 550 public definitions are unreachable through their own
  index. Accepted, and decoupled further than they proposed: `MIRI-PY-043` no longer depends on `MIRI-PY-036` at
  all, so a linter declining to execute code can still settle coverage. Their floor caveat is normative, not a
  note, because it decides the case an artifact lands in: the test detects a collision and never establishes the
  absence of one, so an unparseable source file forfeits rather than passing. Accepts a new `comparison_not_possible`
  skip reason, flagging that a `lint-report-v1` enum change breaks every report consumer and is the maintainer's
  call. Answers #25 with `dependencies` as import names, and attaches the finding behind it: `AGENT_EXAMPLES.json`
  has no schema, no instance anywhere in the repository, and is not emitted by the implementation guide's own
  generator, while four active checks worth 15 of 100 points read it.

- `miri-py-consumer-surface-vocabulary-limits.md` / `miri-standard-response-vocabulary-limits.md` — a consumer
  team running miri-py against a production OpenAPI SDK hit three closed vocabularies that could not express a
  distinction they needed. miri-py shipped two of them as FIELDS on `resolution` rather than as `evidence` values,
  on the reasoning that an unknown field is ignorable where an unknown value in a closed set makes the response
  unprocessable, and asked to be told if they drew that line wrong. They did not: the response standardizes both
  and keeps `resolution` open for the reason §4.1 gives for the envelope root. Their schema finding turned out to
  be one of three — `resolution`, `patterns` and `graph` all lacked payload schemas — and the gap hid a live
  defect, since §4.2's no-payload-on-an-absent-response rule was enforced for only the three keys that had been
  written down. On `graph`, one divergence was theirs (nesting `nodes`/`edges` at the reserved top level) and one
  was ours (§3.8's example spelled the edge key `kind` where `api-graph-v1.json` has always said `relationship`).
  Closes the blended-aggregate row with their measurement: two wheels from byte-identical Python, one raising
  `FileNotFoundError` on first call, both scoring 28% of 48.

- `miri-py-learning-path-order.md` / `miri-standard-response-learning-path-order.md` —
  `learning_paths[*].patterns` is described as ordered, and the only orderable fact a pattern carried was
  `complexity`, which has three values. Every pattern at one level was tied, and the tie went to whatever the
  generator read first: on a consumer's SDK the beginner path matched the build host's directory order, and the
  pattern its author wrote to come first landed fourth. `order` is accepted and ships, with the ask tightened. As
  proposed the field advised a producer that still owned the sequence, so a declared value obliged nothing and the
  author who wrote `order: 0` kept the guarantee they had before, which was none. Agent Metadata §4.2.1 makes it
  bind the published array instead, which is decidable from the document alone. Adds the two properties the
  proposal left out (the array as published is what a consumer reads, and one `order` serves every path the pattern
  appears in), declines to standardize the docstring convention that produces it, and asks them not to sort the
  `patterns` operation by a field that admits ties and so cannot carry a cursor.

Accepted outcomes are folded into the normative sources (`schemas/`, the check YAMLs, the linter checklists); these
notes are the record of *why*, not a second source of truth.
