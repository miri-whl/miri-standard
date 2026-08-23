# Feature request: expand arghos to review specifications and RFCs

**To:** the arghos maintainers
**From:** the Miri Standard maintainer
**Date:** 2026-08-23
**Context:** we ran six panel rounds over a draft standard between 2026-08-20 and 2026-08-23. We built them as
ad-hoc agent workflows because we did not think arghos covered this. Having now read arghos properly, we think it
is **most of the way there** — and we would rather use it than keep rebuilding. This is what we did, what we would
have done in arghos, and the specific gaps.

## Why we are asking

arghos already says of itself: *"The tool is general; the sample panel it ships with is grounded in an
industrial-IoT / OT-security domain."* We agree — the general machinery is the valuable part, and a
document-critique panel is not intrinsically about buyers. What we want is a second scenario family alongside
`buyers/` and `website/`: **`review/`**, where the artifact is a specification and the panel is a set of editorial
lenses rather than a market.

The value we would get immediately is the part we most conspicuously lack: **run persistence, versioned personas,
and run-over-run comparison.** We have run six panels and can compare them only by reading two PDFs side by side.

## What we did locally

Six rounds, each a fan-out of six persona agents plus a chair that consolidates:

| Round | Question | Output |
|---|---|---|
| 1–2 | Naming coherence; substantive defects in two draft specs | 10 must-fix defects |
| 3 | Does the end-to-end user journey work? | 8 wants scored delivered / partial / not-delivered |
| 4 | Fixture coverage — which claims have no test | 13 gaps |
| 5–6 | **Is the specification complete?** (text only) | verdict + 16 must-fix, 13 should-fix |

Each persona returned **structured findings**, not prose: `{title, severity, document, quote, defect, fix}`. The
chair de-duplicated across personas, resolved disagreements, and returned a single verdict. We rendered the result
to PDF with pandoc + headless Chrome.

The most valuable single design decision: **personas were defined by the question they exist to ask**, not by who
they are. "Conformance editor — could a checker be written against this sentence without asking the author what it
means?" produces sharper findings than "a senior engineer reviewing a spec."

## What maps onto arghos today

Genuinely close, and we want to be specific about it:

- **`kind: critique`** is the right shape. `panel/scenarios/website/` already reacts to extracted document
  artifacts with `prompts/system.md` + `prompts/critique.yaml`.
- **Artifacts as markdown** is exactly our input: four specification documents.
- **`runs/<timestamp>/`** with `report.md`, `report.html`, `responses.jsonl`, `analysis.json` is better run
  hygiene than we have.
- **`critique-compare`** is the feature we most want and did not build. Comparing round 5 against round 6 to see
  which findings closed and which are new is exactly our workflow, and you already have the concept.
- Cost caps, seeds, temperature, and concurrency are all things we hand-rolled or did without.

## The gaps, as feature requests

Ordered by how much they block us.

### 1. A finding-shaped output, not a rating-shaped one

**The core gap.** arghos maps free-text responses onto **numeric ratings** via SSR anchor ladders — `urgency`,
`vacuum`, `budget`, each a worst-to-best statement ladder. That is the right instrument for eliciting a *market
signal* from a synthetic buyer.

Specification review produces something structurally different: a **list of located defects**. There is no ladder,
because "this clause contradicts that one" is not a position on a scale. What we need per response is:

```yaml
finding_schema:
  severity: [critical, high, medium, low]
  fields: [title, document, quote, defect, fix]
  required: [quote, defect]
```

The `quote` requirement matters more than it looks: it is what stops a reviewer asserting a defect that is not in
the text. Our instruction *"a finding with no quote is noise — omit it"* materially raised finding quality.

**Ask:** let a scenario declare `output: findings` with a configurable field set, alongside the existing
`output: ratings`. Keep SSR for the scenarios it fits.

### 2. Personas defined by a question, not by a demographic

`panel/personas.yaml` is buyer-shaped: `verticals`, `role_titles`, `responsibilities`, `org_size_weights`,
`regulatory_weights`, `stack_weights`. Our six lenses have none of those dimensions and are not sampled — there is
exactly one conformance editor, not ten drawn from a distribution.

**Ask:** support a persona family declared as a flat list of named lenses, each with a `question` and a `charter`,
with no sampling and no weights:

```yaml
lenses:
  conformance-editor:
    question: >-
      Is every normative clause decidable from the text alone? Could a checker be
      written against this sentence without asking the author what it means?
  two-implementations:
    question: >-
      If two teams built independently from this text and never spoke, would their
      results interoperate? Every "only by coincidence" is an under-specification.
```

This is a smaller change than it sounds: the sampling machinery is bypassed, not replaced.

### 3. A synthesis stage

Six panelists produce overlapping findings. Ours were consolidated by a **chair** with its own charter:
de-duplicate across panelists, rank, resolve disagreement, and return one verdict. In the last round the chair also
*discarded* out-of-scope findings that panelists had smuggled in, and reported that it had done so.

**Ask:** a `synthesis:` block in the scenario — a final pass over all responses with its own prompt and its own
output schema. This is the difference between a transcript and a report.

### 4. Verification affordance — let a panelist check a claim

**The single highest-value thing we did.** Our reviewers could read the repository, and our best findings came from
one actually checking rather than inferring: that a check ID pattern excluded a namespace, that a stated cap
contradicted an example twenty lines above it, that a scoring band was mathematically unreachable given the
weights.

A panelist confined to the artifact text can only report suspicions. One that can run `grep` reports facts.

**Ask:** an opt-in, read-only tool affordance for panelists — at minimum file read and search, scoped to a declared
root. This changes the class of finding a critique panel can produce, and we suspect it would improve the buyer
scenarios too (a buyer who can read the linked pricing page is a better buyer).

### 5. Declared out-of-scope, enforced at synthesis

Our specification is deliberately unimplemented — it is a spec-first project. Early rounds burned effort on "where
is the code", "no adoption", "no evidence", which are true, intended, and useless. We fixed it by naming the
out-of-scope classes in every persona prompt *and* instructing the chair to discard them.

**Ask:** a scenario-level `out_of_scope:` list, injected into every panelist prompt and enforced at synthesis, with
the count of discarded findings reported. Generalizes cleanly: a buyer panel might exclude "the price is too high"
when price is not what is being tested.

### 6. Multi-document artifacts with cross-references

Our artifact is four documents that reference each other by section number. Several of the best findings were
*between* documents — a claim in one contradicted by another, a cross-reference to a section that does not exist.

`website/` treats artifacts as independent per-vertical copy. We need a scenario where **all panelists read all
documents as one corpus**, and where the prompt can say "check that every cross-reference resolves."

**Ask:** an artifact set that is shared rather than partitioned, with stable document names the findings can cite.

### 7. Finding-level comparison between runs

`critique-compare` compares resonance and keep deltas. The review analogue is: **which findings closed, which are
new, which are unchanged** between two revisions of the same document.

That is the metric we actually manage the work by — we currently track it by hand in a backlog file with 36 rows.

**Ask:** `review-compare RUN_A RUN_B` producing closed / new / persisting, matched on finding identity (document +
quote, or an explicit id).

## What we are not asking for

- **Not a validated predictor.** Your README's caveat applies here too, and more sharply: a synthetic panel's
  reading of a specification is a hypothesis about where the defects are, not proof. Every finding we acted on, we
  verified against the files first — and roughly one in six did not survive that check. We would want a review
  scenario to carry the same warning.
- **Not domain knowledge.** We do not need arghos to understand packaging standards. The lenses carry the
  expertise; the tool carries the machinery.
- **Not SSR.** We are asking for a second output mode beside it, not a replacement.

## What we would contribute

We have six tuned lenses, a scope-guard framing, and a chair charter that have been through six rounds and are
producing findings we act on. If a `review/` scenario family is welcome, we would contribute ours as the worked
example — the way `buyers/` grounds the sample panel today.

---

*Separately, we intend to make the `arghos` CLI conformant with the Miri CLI standard — an internal CLI scored
against our own suite. We will send that as its own report.*
