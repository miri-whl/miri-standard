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

The project is early (0.1-draft, Incubation) and has a single maintainer: where these documents describe what the
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
- `upstream-artifact-publishing-feedback.md` — a note arguing for publishing the check definitions as a versioned
  artifact.

Accepted outcomes are folded into the normative sources (`schemas/`, the check YAMLs, the linter checklists); these
notes are the record of *why*, not a second source of truth.
