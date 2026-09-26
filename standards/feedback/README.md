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
  makes all three of their behavioural families `undetermined` rather than "N pass / 0 fail". It declines to freeze
  the operator vocabulary while a third of the behavioural checks need operator classes that do not exist, and
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

- `miri-standard-response-scoring-denominator.md` — miri-py implemented scoring-v2 and hit a report that
  fails the standard's own wire schema. The blocker is real; the diagnosis was one field off. The numerator
  had no field at all, `effective_denominator` is an integer by definition, and this schema used the word
  *denominator* for two different quantities. Records why widening the wire field was declined.

- `miri-standard-response-check-references.md` — accepts miri-py's finding that 21 PEPs are named in check
  prose and missing from that check's `references`, and gates the rule so it cannot reopen. Asks them to
  relabel their fix card from "Defined by" to "References", because four of the 21 are tooling
  instructions, cautionary examples, or cross-ecosystem prior art rather than the authority for the rule.
Accepted outcomes are folded into the normative sources (`schemas/`, the check YAMLs, the linter checklists); these
notes are the record of *why*, not a second source of truth.
