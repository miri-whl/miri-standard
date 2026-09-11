# Vacuous Conformance: Sections That Cannot Discriminate

*Proposal Version: 0.2*
*Status: Answered — all three findings accepted; §4 already landed upstream*
*Created: 2026-09-10*
*Revised: 2026-09-10, after the maintainers' response*
*From: the miri-py implementation team*
*Concerns: MIRI-PY-008, and the weighting of categories A and E*

> **Read the revision note first.** This document was written against
> `cc5d0a4` (origin/main). Its main ask was already implemented on
> `phase-0.4.1`, which was unmerged and which we did not check. Three
> statements below were true at that pin and are not true after it, and
> one was simply wrong. Each is corrected in place and marked
> **[corrected]**; §7 records what changed, what we got wrong, and what
> we could not find.

## Abstract

Scoring five real wheels against the 0.2-draft checklist produced an
uncomfortable result: three unrelated third-party packages returned
**identical section scores in four of six categories**, and two of those
categories returned identical scores for *every* wheel we tried,
including our own conforming one.

Investigating that turned up one implementation bug on our side, which
we have fixed. What remains is three properties of the checklist itself
that we cannot fix in an implementation, because they are questions of
what the standard should require. We raise them here.

1. **A conformant `usage-patterns.json` may declare no usage patterns.**
   MIRI-PY-008's clauses are shape-based; `patterns: []` satisfies all
   of them.
2. **Category A (Packaging Baseline) cannot distinguish a Miri-ready
   wheel from any other correctly built wheel.**
3. **Category E (Deprecation & Lifecycle Coherence) carries 25 points of
   which at most 3 are earnable by a package that has no deprecations,
   and the other 22 are also unloseable.** [corrected: the abstract
   said "Category D", which the legend in §1 maps to Identity &
   Security.]

None of the three is a scoring error. Each is a case where the score
moves for reasons unrelated to whether the package is more useful to an
agent, which is the property the standard exists to measure.

## 1. The empirical ground

Five wheels, scored offline (no `--network`, `--execute` or
`--previous-release`):

| Package | Version | Conformance | A | B | C | D | E | F |
|---|---|---:|---|---|---|---|---|---|
| miri-py | 0.2.0 | 79 | 8/10 | 20/20 | 7/10 | 23/25 | 16/25 | 5/10 |
| patitur-sdk-api-client | 0.10.7 | 47 | 8/10 | 11/20 | 5/10 | 5/25 | 13/25 | 5/10 |
| google-ai-generativelanguage | 0.6.15 | 40 | 8/10 | 11/20 | 0/10 | 5/25 | 13/25 | 3/10 |
| google-api-python-client | 2.181.0 | 40 | 8/10 | 11/20 | 0/10 | 5/25 | 13/25 | 3/10 |
| grpcio | 1.74.0 | 36 | 8/10 | 11/20 | 0/10 | 1/25 | 13/25 | 3/10 |

Categories: A Packaging Baseline · B Agent Metadata Core · C Examples ·
D Identity & Security · E Deprecation & Lifecycle Coherence ·
F Discovery & Degradation.

Categories B, C, D and F discriminate. A and E do not.

### 1.1 What we fixed on our side first

Before raising anything, we checked whether the sameness was our fault.
Partly it was. Seven checks the committee marks `conditional: true`
returned `pass` when their trigger was absent, where the checklist's own
rule is a not-applicable skip (MIRI-PY-028, 029, 030, 031, 032, 034,
035). That is fixed.

**[corrected]** We wrote that this moved no score, "because a
not-applicable skip and a pass both award full weight". That was true at
`cc5d0a4` and is not true on `phase-0.4.1`, where an inapplicable check
leaves both numerator and denominator. Our fix therefore *does* move
scores under the new model, and an offline package with no deprecations
is scored out of **78**, not the 87 this document computed — 87 counted
the four not-applicable checks as leaving the denominator but kept the
three capability forfeits in it, and those leave too.

Three further checks tested a file's presence and skipped the clause in
their own definition about its content: MIRI-PY-006 ("files are present
but unreadable (zero-byte or undecodable)"), MIRI-PY-014 ("contains no
executable statements (empty stub)"), MIRI-PY-037 ("zero-length or
headings with no body content"). Also fixed, and each now has a test per
clause.

We mention this because it establishes the method for what follows: we
treated each `fires_when` clause as normative and tested it empirically.
The three items below are cases where the clause does not exist to test.

## 2. MIRI-PY-008 admits an empty patterns document

### The observation

A wheel shipping this document passes MIRI-PY-008:

```json
{
  "version": "1.0",
  "generated_at": "2026-09-10T00:00:00Z",
  "patterns": []
}
```

MIRI-PY-008's clauses:

- `agent-metadata/usage-patterns.json` is absent
- The top level lacks `version`, `generated_at`, or `patterns`
- A pattern entry lacks any of `id`, `name`, `description`,
  `complexity`, `category`, or `code`
- A `categories` or `learning_paths` entry lists a pattern id that no
  pattern defines

Every clause is satisfied. The third and fourth are quantified over an
empty set. `usage-patterns-v1.json` requires the key and sets no
`minItems`.

### Why it matters

Of the six agent-metadata documents, `usage-patterns.json` is the one
whose entire value is its contents. A `lifecycle.json` with no advisory
sources fails MIRI-PY-021, which states the emptiness clause explicitly
("`advisory_sources` ... is absent, null, or **an empty array**").
Usage patterns has no equivalent.

**[corrected]** This paragraph claimed that a manifest with an empty
`api_index` "fails MIRI-PY-007 on other grounds". It does not, and the
maintainers were right to catch it. Our probe had a confound: it
hand-built a manifest carrying `miri_version: "0.2.0"`, which fails the
schema's `^\d+\.\d+$` pattern, and we read 007's failure as being
about the empty index. Re-run against the valid fixture with only
`api_index` emptied, **007 passes**. 007's clause quantifies over
entries, so an empty index satisfies it vacuously — the same defect as
008, in the same document, missed inside the analysis that found 008.

The standard is therefore inconsistent with itself: it already knows how
to say "an empty array does not count", and says it for advisory sources
and not for usage patterns.

### Proposal

Add a clause to MIRI-PY-008:

> - `patterns` is an empty array

and `"minItems": 1` to `usage-patterns-v1.json`.

We suggest the same review for the other content-bearing arrays —
`api_index` in sdk-manifest, `examples` in AGENT_EXAMPLES.json — with
the caveat that a genuinely tiny package may legitimately have one
pattern and no more, so the threshold should be one, not a proportion.

## 3. Category A cannot discriminate

### The observation

Every one of the five wheels scores 8/10, and so will every wheel that
was built by a current tool and uploaded to PyPI.

| Check | Weight | Level | What it requires |
|---|---:|---|---|
| MIRI-PY-001 | 2 | MUST | Wheel structure valid |
| MIRI-PY-002 | 2 | MUST | Core metadata valid |
| MIRI-PY-003 | 2 | MUST | Version scheme valid |
| MIRI-PY-004 | 2 | SHOULD | Declarative build config |
| MIRI-PY-005 | 2 | SHOULD | Publish attestations (requires network) |

001-003 are properties PyPI enforces at upload. 004 is satisfied by any
wheel built from a `pyproject.toml`. 005 is the only one that varies,
and it forfeits without `--network`; with `--network` all three
third-party wheels *fail* it (no PEP 740 attestations), so the section
still reads 8/10 — the same number meaning something different.

We confirmed the section is not inert. It moves under sabotage: 6/10 for
`Metadata-Version: 1.0`, 6/10 for a non-PEP-440 version, 4/10 for a
missing WHEEL file. The checks work. They just cannot separate packages
that are all correctly built.

**[corrected]** The 8/10 figures throughout this section are at
`cc5d0a4`, where a forfeited check kept its weight in the denominator.
On `phase-0.4.1` an excluded check leaves the denominator, so 005 being
excluded offline makes the category read **8/8**. Still constant, so the
finding stands; the arithmetic in the tables above does not.

### Why it matters

10 of 100 points are effectively a constant for the population the
standard is aimed at. That is 10% of the conformance score carrying no
information, which pushes every real package's score up by the same
amount and compresses the range that does carry information.

We are *not* proposing that the baseline be dropped. Its stated
rationale is sound: "a wheel that violates the baseline cannot carry
trustworthy agent metadata." The baseline is a precondition.

### Proposal

Make it a precondition rather than a scored category. Either:

- **(a) Gate, don't score.** Category A becomes a prerequisite: failing
  any of 001-003 makes the artifact non-conforming (they are already
  MUSTs, so this is nearly the current behavior) and the category
  contributes 0 points to the 100. Redistribute the 10 points across the
  categories that measure agent-readiness.
- **(b) Keep it scored but reweight to 2-3 points.** Less disruptive,
  and preserves the signal that the baseline was checked.

We prefer (a): the two-score model already separates "does it conform"
from "how good is it", and a precondition belongs to the first.

## 4. Category E is 25 points with 3 points of signal

### The observation

| Check | Weight | Conditional | Requires | Fate for a package with no deprecations |
|---|---:|---|---|---|
| MIRI-PY-028 | 4 | yes | — | not applicable |
| MIRI-PY-029 | 4 | yes | — | not applicable |
| MIRI-PY-030 | 5 | yes | previous-release | forfeited offline |
| MIRI-PY-031 | 3 | yes | — | not applicable |
| MIRI-PY-032 | 2 | yes | — | not applicable |
| MIRI-PY-033 | 3 | no | — | **the only check that can fail** |
| MIRI-PY-034 | 2 | yes | previous-release | forfeited offline |
| MIRI-PY-035 | 2 | yes | execution | forfeited offline |

Four of the five wheels score exactly 13/25, and all 13 points come from
the four not-applicable checks. The entire spread between packages in a
25-point category is MIRI-PY-033's 3 points.

This is not an artefact of the offline posture. Even with every
capability enabled, a package that has never deprecated anything gets
13 points automatically and can lose at most 3.

### Why it matters

The checklist awards a not-applicable skip full weight, which is the
right call — a package should not be penalized for having no
deprecations to document. But combined with a 25-point category where 13
points are unconditionally not-applicable for the common case, the
result is that a quarter of the conformance score is decided by whether
a package happens to have a deprecation history.

Two packages, one with an exemplary deprecation inventory and one with
no deprecations at all, score within 3 points of each other in the
category that exists to measure exactly that difference.

### Proposal

**[corrected — this ask is already implemented.]** Option (a) below
landed on `phase-0.4.1` before this document was written: `scores` now
requires `effective_denominator`, `excluded` and `forfeited`, an
inapplicable check leaves both numerator and denominator, and a
forfeited MUST yields a new `undetermined` grade rather than
non-conformance. We verified this by reading the branch, not the
response: `schemas/lint-report-v1.json` at `200107ae` has

```text
scores.required = ["conformance", "effective_denominator",
                   "excluded", "forfeited"]
```

with `undetermined` among its properties, and `linter-checklist.md`
carries the excluded-versus-forfeited distinction. We arrived at the
same design independently, including where the denominator belongs,
which we take as evidence for it rather than credit for it.

Option (b) is **withdrawn**: the maintainers point out that reweighting
Deprecation & Lifecycle *and* renormalizing would penalize a deprecation
history twice, which is right and which we had not seen.

The original three options are kept below as written, for the record.

- **(a) Renormalize per artifact.** Compute the conformance score over
  the checks that were *applicable*, rather than over the fixed 100.
  A package with no deprecations is scored out of 87, not out of 100
  with 13 free points. This is the smallest change to the model and it
  generalizes: it also handles the capability forfeits, which have the
  same shape. It requires the report to carry the applicable denominator,
  which `lint-report-v1` can do in the `scores` block.
- **(b) Reweight category E down** to something proportional to the
  three points of signal it can actually produce for the common case,
  and move the weight to categories that discriminate.
- **(c) Split the category.** "Lifecycle declared" (033 and the
  identity-adjacent checks, which every package can satisfy) scored
  separately from "Deprecation coherence" (028-032, 034, 035), with the
  second contributing only when the package declares deprecations.

Option (a) has a consequence worth stating plainly: scores would stop
being comparable across artifacts with different applicable sets unless
the denominator is published alongside. We think that is honest rather
than a drawback — it is the same argument the count-normalization
proposal made for density, and it is the same principle the standard
already applies in "declare sources, not verdicts".

## 5. What we are not asking for

We are not asking for the not-applicable-awards-full-weight rule to
change. Penalising a package for having no deprecations would be worse
than the current situation, and the rule is correct in isolation. The
problem is the interaction between that rule and category weighting, and
we think the fix belongs in the weighting.

We are also not asking for MIRI-PY-005 to stop requiring network. The
capability model is right. We note only that a category whose only
variable check needs a capability will read as constant in the default
posture, which is the posture most users will run.

## 6. Reproducing this

**[corrected]** Every figure above comes from `miri score` at checklist
0.2-draft @ `cc5d0a4fece97268cbe6983c8f3bcaa7ccc9c29c` — origin/main,
which predates the work answering §4. The numbers are reproducible at
that pin and will not survive the merge: four of the six category scores
move once excluded checks leave the denominator. Re-run then. The wheels
are public:

```text
pip download --no-deps google-api-python-client==2.181.0 grpcio==1.74.0 \
    google-ai-generativelanguage==0.6.15
miri score <wheel> --format json
```

The sabotage matrix that established the checks are content-sensitive
rather than existence-only is in
`tests/unit/linter/checks/test_substance_clauses.py`, and the
conditional-check treatment is pinned in
`tests/unit/linter/checks/test_deprecation_coherence.py`.

## 7. Revision record

Written against `cc5d0a4` (origin/main). The maintainers' response
established that the main ask was already implemented on `phase-0.4.1`
at `200107ae`, which we did not check — ten commits unmerged. Everything
below is verified against that branch directly rather than taken from
the response.

### What we got wrong

| § | The claim | What is true |
|---|---|---|
| Abstract | "Category D (Deprecation & Lifecycle Coherence)" | The legend in §1 maps D to Identity & Security. Deprecation & Lifecycle is E. A plain editing error. |
| 1.1 | Fixing seven conditional checks "moved no score" | True at `cc5d0a4`, false on `phase-0.4.1`, where an inapplicable check leaves the denominator. Our fix now moves scores. |
| 1.1 | An offline no-deprecation package is "scored out of 87" | Out of **78**. We removed the four not-applicable checks from the denominator but left the three capability forfeits in it; those leave too. |
| 2 | An empty `api_index` "fails MIRI-PY-007 on other grounds" | It does not. Our probe hand-built a manifest with `miri_version: "0.2.0"`, failing the schema's `^\d+\.\d+$`; we read that failure as being about the empty index. Against the valid fixture with only `api_index` emptied, 007 passes. |
| 3 | Category A reads 8/10 | 8/8 after the merge, since an excluded check leaves the denominator. The finding survives; the arithmetic does not. |
| 4 | Option (b), reweight category E | Withdrawn. Reweighting *and* renormalizing would penalize a deprecation history twice. |

The `api_index` error is the one worth dwelling on. It is the same
defect class the document is about — a clause quantified over an empty
set — sitting in the same file as the instance we reported, and we
missed it because we accepted a green-to-red transition without checking
*which* clause produced it. The method in §1.1 says to treat each
`fires_when` clause as normative and test it empirically; we did that
for the checks and not for our own evidence. A sabotage that changes two
things at once tests neither.

### What we accepted

- **§3 as amended.** Gate the three MUSTs, keep 004 and 005 scored,
  redistribute 6 points into Agent Metadata Core and Examples, and use
  an explicit `scoring: gate` field rather than overloading `weight: 0`,
  which already means "extension check". Our original option (a) would
  have discarded two SHOULDs by treating the whole category as a
  precondition, which was wrong.
- **§4 as already implemented**, including the `undetermined` grade for
  a forfeited MUST. That distinction — an excluded MUST never applied,
  a forfeited MUST applied and went unassessed — is finer than anything
  we proposed and it is the right one.

### One observation on the corrected arithmetic

The response gives 78 as the denominator for an offline package with no
deprecations (100 − 13 not-applicable − 9 forfeited). That is category
E's contribution, and it corrects our 87 exactly. Across all six
categories the effect is larger, because every category has exclusions:
for the five wheels in §1 the applicable denominator is **56 to 60**,
not 78.

Projecting each wheel onto the new model — earned points over applicable
points, with not-applicable weight removed from both sides:

| Package | Today | Earned | Applicable | Projected |
|---|---:|---:|---:|---:|
| miri-py | 79/100 | 56 | 56 | **100%** |
| patitur-sdk-api-client | 47/100 | 24 | 56 | **43%** |
| google-ai-generativelanguage | 40/100 | 17 | 56 | **30%** |
| google-api-python-client | 40/100 | 17 | 56 | **30%** |
| grpcio | 36/100 | 17 | 60 | **28%** |

Two things follow. The spread widens — 28 to 100 rather than 36 to 79 —
which is the discrimination the document was asking for, arriving from
§4 rather than from §3 or §4(b). And a conforming package can now reach
100%, because the free weight it used to collect from inapplicable
checks is gone from both sides. We think both are right. We flag them
only because a score moving from 79 to 100 without the artifact changing
will need explaining to anyone tracking a number over time, and the
`effective_denominator` field is what makes that explicable.

We have not implemented this yet — the figures above are a projection
computed from the outcomes we already have, not output from a re-pinned
linter. We will replace them with real numbers after the merge.

### One thing we could not find

The response states that MIRI-PY-008 now fires on `patterns: []` with
`minItems: 1` in `usage-patterns-v1.json`, and that 007 gained a clause
with `minProperties: 1`. We could not locate those changes. Checked at
`phase-0.4.1` (`200107ae`), `phase-0.4`, `review/all-four`,
`fix/advisory-coverage-schema` and `main`:

```text
branch                          patterns.minItems   api_index.minProperties
phase-0.4.1                     absent              absent
phase-0.4                       absent              absent
review/all-four                 absent              absent
fix/advisory-coverage-schema    absent              absent
main                            absent              absent
```

Most likely unpushed, or on a branch we did not think to check. Raised
only so the §2 work is not implemented against definitions that turn out
to differ — we are not asking anyone to defend a bookkeeping detail.

### Next steps on our side

1. Re-pin the vendored definitions to `phase-0.4.1` once it merges
   (`make sync-checks`). We are not pinning to an unmerged branch.
2. Implement the excluded/forfeited denominator, the three new required
   `scores` fields, and the `undetermined` grade.
3. Re-run §1's table. Four of the six category scores will move, and the
   conformance numbers for all five wheels will change, since none of
   them was scored against a denominator that excluded anything.
