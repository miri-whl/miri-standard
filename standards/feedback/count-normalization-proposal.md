# Count Normalization for the Baseline Health Method

*Proposal Version: 0.1-draft*
*Status: Draft — submitted for miri-standard discussion*
*Created: 2026-08-18*
*From: the miri-py implementation team*
*Answers: maintainers' response §3.1 (count normalization must be defined in the baseline)*

## Abstract

The maintainers' response to the two-score proposal left one design question open and assigned it to us: the baseline
health method `max(0, 100 − Σ(wᵢ × countᵢ))` over raw violation counts penalizes large artifacts — 40 broken examples
out of 400 scores the same as 40 out of 40 — and whatever stance the baseline takes must be defined centrally, or
comparability leaks out the same door severity almost did.

Our proposal: **the baseline health score uses raw counts, unchanged — and the report format carries the countable
population per outcome, with violation *density* defined as a derived report field that never enters the score.**
Normalization becomes declared data for consumers, not arithmetic inside the number. This preserves the already-validated
Wheel A/B semantics, avoids creating ~18 new per-check normative definitions where implementations would diverge, and
gives the fairness use-case a home that matches the standard's own "declare sources, not verdicts" principle.

## 1. The Empirical Ground

We measured 400 wheels from real local caches (a working developer machine's pip and Poetry caches — a fair sample of
the ecosystem a linter meets in practice):

| Population | min | median | p90 | max |
|---|---|---|---|---|
| Total files per wheel | 5 | 26 | 206 | 14,591 |
| Python files | 0 | 17 | 97 | 1,402 |
| Example files | 0 | 0 | 0 | 55 |
| `Requires-Dist` entries | 0 | 3 | 21 | 56 |

Two facts matter:

1. **Populations span 3.5 orders of magnitude.** Any fixed normalization constant, cap table, or scaling curve is
   tuned for one region of this range and wrong for the rest.
2. **The countable populations concentrate in a minority of checks.** Of the 40 checks, roughly 18 have per-instance
   violation units (each example, each schema violation, each removed interface); the other 22 are per-artifact
   singletons ("the wheel archive", "the update_check declaration") where a count above 1 cannot occur and
   normalization is meaningless. The normalization question is really a question about ~18 checks.

## 2. Why Raw Counts Should Stay in the Score

**2.1 Health is an absolute magnitude by design.** The two-score split assigned health the question *"how bad is what's
wrong?"* — not *"how does this artifact compare, size-adjusted, to others?"*. Forty broken examples are forty traps an
agent can step into and forty items of repair work, whether or not 360 healthy examples exist alongside them. An agent
sampling the examples directory does experience the *fraction* — which is exactly why density belongs in the report
(§3) — but the score's semantics are magnitude, and raw counts are the only magnitude that needs no further definition.

**2.2 Population definitions are a divergence surface.** To normalize inside the score, the standard must define the
population for every per-instance unit: does "each example" count generated examples? conditional ones? templates? Does
"each interface" count re-exports? private-but-imported names? Each definition is a place where two conforming linters
can disagree — precisely the failure mode the standard closed for severity by shipping the check definitions
(response §2). Normalizing in the score reopens it, eighteen times. Declaring the population as *reported data* keeps
the score's inputs fully fixed while still publishing everything a consumer needs.

**2.3 The validated numbers survive.** The Wheel A/B example (health 95.6 vs 17.6 under `balanced@1`) was computed with
raw counts, validated by the maintainers as the reproduction target, and is now enforced by tests in the reference
implementation against shipped severity data. Every normalization alternative we examined (population-proportional
scaling, per-severity caps, log saturation) changes those published numbers; renegotiating them buys fairness-in-the-
score at the cost of the baseline's first stable anchor.

**2.4 Saturation is signal.** Raw counts can drive health to 0. For a diagnostic magnitude that is correct behavior —
"the examples directory is broken end to end" *should* saturate. Consumers who want asymptotic degradation instead have
the exponential-decay annex method, safely, because no-naked-scores forces the method declaration.

**2.5 Caps are an annex method, not the baseline.** The response noted our tiered-penalty method already contains the
per-severity-cap idea. We agree it is useful — as the declared, optional method it already is. Making caps normative in
the baseline adds a central cap table: a second parameter surface that must be versioned and agreed, with the same
divergence risk as populations and no benefit density-in-the-report does not already provide.

## 3. The Normative Proposal

For `scoring-v1.json` (baseline method definition):

1. **Count**: the number of violations of the check, in the check definition's `violation_unit`, with no scaling,
   caps, or population adjustment. (This is a definition, not a default — implementations MUST NOT normalize inside
   the baseline score.)

For `lint-report-v1.json` (report format):

<!-- markdownlint-disable MD029 -->

2. **Population** (optional, per check outcome): when a check's `violation_unit` has a countable population in the
   artifact (e.g. total examples for MIRI-PY-015, total public interfaces for MIRI-PY-030), the report SHOULD carry it
   as `population`. Per-artifact units omit it.
3. **Density** (derived): `violation_density = count / population`, defined by the report schema, computable by any
   consumer, and explicitly **not** an input to any score. Cross-artifact, size-adjusted comparison — the 40/400 vs
   40/40 case — is served by this field.
4. **Promotion path**: if ecosystem experience shows consumers converge on density and want it scored, a future minor
   version can introduce a density-based method *as a new named method* (no-naked-scores makes this additive), leaving
   the baseline stable.
<!-- markdownlint-enable MD029 -->

## 4. Worked Example (the maintainers' 40/400 case)

Wheel C has 400 examples, 40 broken; Wheel B has 40 examples, all broken. Under this proposal both report health
`100 − (40×2 + …)` — identical magnitude, because the brokenness is identical in absolute terms — but their reports
differ: C carries `population: 400, violation_density: 0.10`, B carries `population: 40, violation_density: 1.0`. A
registry ranking wheels size-adjusted uses density; an agent estimating repair effort uses the score. Both consumers
get a number whose meaning is defined, and neither number is vendor-invented.

## 5. Reference Implementation

miri-py's shipped baseline already computes raw counts (`miri_py.linter.checks.scoring`), reproduces Wheel A/B exactly
from the vendored check definitions, and its `CheckOutcome` model carries the optional `population` field feeding the report
schema draft. The `lint-report-v1.json` draft (in progress, per response §3.2) includes `population` and
`violation_density` as specified above.

---

*Prepared by the miri-py team. Measurement script and raw data available on request; the 400-wheel scan is
reproducible against any developer machine's pip/Poetry caches.*
