# Reply: the six points are not awarded, and the rule behind them was superseded at 0.5.0

*Responding to: "both corrections accepted, and the vacuous pass is a vacuous exclusion" (miri-py, 2026-11-01)*
*Status: The finding is accepted and the arithmetic is not. The repair proposed is the right one.*
*Created: 2026*

## Disposition

The substance is right and the arithmetic is from a schema version that was superseded three releases ago. Those
separate cleanly, and the second matters well beyond this check pair.

The classification argument is accepted in full: an absent trigger is being paid rather than forfeited, and the
proposed repair is narrower and better than a new population rule. The declaration shape needed to implement it is
given below, with a precedent that already exists in the standard.

## The arithmetic describes pre-0.5.0 semantics

> which the vocabulary defines as an **exclusion**: the obligation does not exist for this artifact, nothing is
> unknown, and the weight is scored in full

The first two clauses are right. The third was true until 0.5.0 and has not been since. `check-v1.json` carries the
rule and its own retraction, in its title:

```text
title:  "Miri Standard Check Definition (v1 - SUPERSEDED)"

        SUPERSEDED by check-v2.json at 0.5.0. Retained unchanged because a consumer pinned here is
        internally consistent rather than wrong: it describes PRE-0.5.0 scoring semantics, under which
        `conditional: true` meant a check scored its full weight automatically when its condition did
        not apply.
```

`check-v3.json`, which is the governing schema, states the opposite:

```text
When the condition does not apply, the check is EXCLUDED FROM BOTH the numerator and the denominator.
It is removed from the calculation, exactly as a capability-forfeited check is. It is NOT awarded its
weight. This is the not-applicable-is-not-a-pass rule: a check whose condition does not hold has not
been satisfied, and scoring it as passed would let an artifact earn weight for an absence.
```

`scoring-v2.json` agrees and names the same rule: excluded and forfeited checks leave both sides, so the denominator
is at most 100 and two scores are comparable only alongside their denominators.

So the release in the worked example is awarded nothing. The sentence forbidding exactly that reading is the one the
rule is named after.

## Which makes the question larger than this check pair

A report labelled `excluded (weight scored)` reads as though the scorer credits the weight. If that is what it does,
the effect is not confined to `MIRI-PY-030` and `MIRI-PY-043`:

```text
family           active   conditional   weight carried by conditional checks
MIRI-PY              43            15       39   of 100
MIRI-CLI             43            10       26   of 100
MIRI-CONSUMER        18             4       12   of 100
MIRI-SURFACE         18             0        0
```

Thirty-nine of a Python wheel's hundred points sit on checks that are excluded whenever their condition does not
hold. Under the v1 rule every one of those is credited; under v3 none of them is, and the denominator shrinks
instead. The two models diverge on any artifact with an inapplicable conditional check, which is most artifacts.

This is worth settling before the next published score. Please confirm which schema version the scorer implements. If
it is v1, the correction is larger than the one this exchange started from, and the example given understates the
defect by a factor of six.

## Why the finding survives the arithmetic being wrong

Removing the credit does not rescue the artifact. Under v3 the obligation leaves the ratio, so a release that
silently deleted a module and its public function is graded out of a denominator that no longer contains the two
checks written to catch it. It gains nothing. It also loses nothing, and it is not marked `undetermined`, because an
exclusion asserts that nothing was left unknown.

That assertion is the defect, and it is stated precisely:

> a delta that cannot be measured is not the same as a delta that is empty, and only the second is an exclusion

Accepted, and it is a better repair than a new population rule. An empty delta is an exclusion: the obligation
genuinely did not arise. A delta computed over a surface known to be partial is a measurement that could not be
taken, which is a forfeit, and for a MUST a forfeit withdraws the grade rather than discounting the score.

`freshness.py` is correct as written for the first case. It becomes wrong only once the index it reads is known to be
partial, which is the condition that does not exist in the artifact yet.

## The declaration shape, which is what makes the repair possible

The condition in the previous response, that a declared surface must record that it is one, is not bookkeeping. It is
the input a linter needs to tell an empty delta from an unmeasurable one. Without it, both look like an index with no
difference across releases.

The standard already has a spelling for this, in `cli-describe-v1.json`:

```json
"advisory_coverage": {
  "type": "string",
  "enum": ["authoritative", "none"],
  "description": "Defaults to \"authoritative\" when omitted. \"none\" declares that no machine-queryable
                  source covers this artifact, and REQUIRES support.security_policy."
}
```

Three properties make it the right precedent: it defaults to the strong claim when absent, so no existing document
becomes invalid; it makes the weak claim explicit rather than inferable; and it couples the weak claim to the field
that makes it actionable. `sdk-manifest-v1.json` takes the same shape:

```json
"surface_coverage": {
  "type": "string",
  "enum": ["complete", "declared"],
  "description": "Defaults to \"complete\" when omitted. \"declared\" states that api_index describes a
                  producer-declared subset of the importable surface, and REQUIRES surface_scope."
},
"surface_scope": {
  "type": "object",
  "required": ["exclude"],
  "properties": {
    "exclude": { "type": "array", "items": { "type": "string" }, "minItems": 1 }
  },
  "description": "The patterns excluded from api_index, relative to the package directory."
}
```

`[tool.miri] exclude` as shipped maps onto `surface_scope.exclude` without translation, so the producer side is
already built. Carry it.

What it then buys, and the reason the two asks were coupled from the start:

- `surface_coverage: complete` and an empty delta is an exclusion, unchanged from today;
- `surface_coverage: declared` and an empty delta is a forfeit, reported, and for a MUST the grade is withdrawn;
- a consumer reading an absent symbol can tell "not in this package" from "not in the declared scope".

## `MIRI-PY-036` gets the reverse-direction clause

Agreed, and the argument for ordering it first is accepted:

> the first signal that a manifest is incomplete is a downstream consumer failing to find a symbol that exists

A clause firing when an importable public definition is absent from `api_index`, and not covered by a declared
exclusion, turns a silent incompleteness into a reported one at build time. It also cannot be written honestly before
`surface_coverage` exists, because without it every scoped index would fire the clause. Both land in 0.8.0, in that
dependency order.

## Where to look, if the scorer does implement v1

There is no stale guidance behind this on our side: the repository's check-authoring notes already name
`check-v3.json` and already carry the correction, including the sentence that the earlier definition said "scores
full weight automatically" and that it let an artifact earn points for an absence. We checked before writing this,
because asserting a defect in our own documentation would have been the easier story.

Which leaves the likelier cause worth checking first. `check-v1.json` is retained on purpose and is internally
consistent, so a consumer pinned to it reads a complete and coherent rule that happens to be three releases old.
Nothing about reading v1 announces that v1 is superseded except its title. If the scorer was written against a
vendored copy taken before 0.5.0, it would behave exactly as the worked example describes, and no validation step
anywhere would object. That is the first place we would look.

## What ships, updated

| Change | Where | Version |
|---|---|---|
| `surface_coverage` and `surface_scope` | `sdk-manifest-v1.json` | 0.8.0 |
| Empty delta against a declared surface forfeits rather than excludes | `MIRI-PY-043` | 0.8.0 |
| Reverse-direction clause, gated on `surface_coverage` | `MIRI-PY-036` | 0.8.0 |
| `additionalProperties: false`, dotted key pattern, `members` nesting, fixture fix | schemas and fixtures | 0.8.0 |
