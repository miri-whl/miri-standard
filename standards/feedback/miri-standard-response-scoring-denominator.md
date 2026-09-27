# Response: the numerator had no field, and the word "denominator" meant two things

*Responding to: `standards-contribution/scoring-v2-vs-lint-report-denominator.md` (miri-py)*
*Status: Accepted as a defect. Resolved differently from the option you preferred — reasoning below.*
*Created: 2026*

## Disposition

**The blocker is real and it is ours.** The resolution is not option 1.

`effective_denominator` is correct as an integer and stays one. The field that was missing is the
**numerator**, and `lint-report-v1` had none at all — so a report carrying a rounded `conformance` and an
integer denominator could not be recomputed by its reader, which is precisely what `scoring-v2` asks a
consumer to be able to do. `scores.earned` is added: MUST when any tiered check contributed, optional
otherwise. Shipping in 0.7.3.

## Where the two readings diverge

`scoring-v2` uses the word *denominator* for two different quantities, and your report applied one rule to
the other's field. That ambiguity is ours, not a misreading on your part:

- the **share** denominator — `sum of the shares of ALL its live tiers` — is per check, and is what
  renormalization divides by;
- the **score** denominator — `conformance.formula` — is the sum of the integer **weights** of every check
  that applied.

Tier arithmetic touches only the first. A tiered check contributes its **full integer weight** to the score
denominator whether it earns T0 or T3, and its **earned fraction** to the numerator. Worked on the case your
table describes — a weight-5 check declaring T0–T3 and earning T0, beside two untiered passing checks of 8
and 4:

```text
tiered check earns            5 × 0.2 / (0.2 + 0.3 + 0.2) = 1.428571…
numerator (sum earned)        8 + 4 + 1.428571… = 13.428571…
denominator (sum of WEIGHTS)  5 + 8 + 4 = 17          ← integer, always
conformance                   78.9916…% → 79 (half-up, once)
```

The 56.57 you emitted is the numerator. It failed validation in the right place for the wrong reason.

## Why not option 1

Widening `effective_denominator` to `"type": "number"` was your preference and we are declining it, for a
reason worth stating rather than asserting: the denominator is what makes two scores comparable. *"Two scores
are comparable only alongside their denominators"* is the sentence that field exists to serve. If one linter
reports a tier-adjusted fractional denominator and another reports the sum of integer weights, both validate
and neither is comparable to the other — and the standard would have blessed the ambiguity instead of
removing it. It would also have been a wire break for a problem that is additive.

Option 2 (round the denominator) we declined for the reason you anticipated: a reported denominator that is
not the one the percentage was computed from is worse than no denominator. Option 3 (bound the arithmetic to
stay integral) would undo the renormalization 0.7.0 was published to introduce.

## What you did, and our read of it

Keeping the v1 fold rather than emitting a report that fails the published schema was the right call, and
recording the deviation at the point of implementation — so it reads as a decision rather than an oversight —
is what made this reviewable at all. We would have made the same choice.

Your point about why it stayed invisible is the one we have taken hardest:

> The two rules agree wherever a check earns its **top** declared tier… Every tiered check on our own wheel
> earns its top tier, so no dogfood pin moves… The divergence only appears on a wheel partway up a ladder —
> which is to say, on the wheels a linter exists to judge.

That is the same shape as three of the last four findings from your side: our own artifact is the one case
that cannot exercise the rule. We have started closing it from the fixture end — 0.7.2 added
`example-lies-1.1.0`, an arm that earns T0 and fails T1, so a wheel partway up a ladder now exists in the
suite. It is one arm against five tiered checks, and tier *earning* above the conformance boundary is still
untested: no arm reaches T3, and the goldens grade pass/fail rather than `tier_earned`.

**Concretely, that is the next thing we would rather build than argue about.** A golden that asserts a
reported `tier_earned` and a reported `earned` would have caught this defect from our side, before you had to
implement against it.

## Your new question: a tier above the obligation that the run cannot assess

You took reading 1 — the check applied, so it takes full weight — and asked rather than quietly picking.
Right call, and the answer follows from a rule `scoring-v2` already states rather than from choosing between
your three.

**A tier is live if the check declares it, it is not parked, AND THE RUN COULD ASSESS IT.** Liveness was
already per check; it is now per *run*. An unassessable tier leaves the check's share denominator exactly as
a parked T2 does — same treatment, same reason: what could not be assessed must not move the ratio. Then the
answer splits on where the tier sits relative to `conformance_tier`:

- **at or below** it — the check's own obligation went unassessed, so the **check** forfeits under
  `coverage`: never passed, never excluded, and for a MUST the grade is withdrawn;
- **above** it — the tier drops from the live set, so a check earning the highest tier that *was* live takes
  full weight and is not docked for a ceiling the run could not reach.

Your concern — that reading 1 "charges the wheel for weight the run couldn't assess" — is exactly right, and
renormalizing is what answers it. The unassessed tier is removed from the ceiling rather than credited. The
opposite error is equally forbidden: docking the artifact because *your* environment lacked a capability
would make forfeiting a discount, which `forfeited_must_withdraws_grade` rules out.

`outcomes[].tiers_unassessable` is now required when a tier was dropped. Without it, two runs of one wheel
report the same percentage over different assessable sets and the numbers silently stop being comparable —
which is the same failure `effective_denominator` exists to prevent one level up.

### This agrees with your number and disagrees with your rule

On your wheel the two coincide. As a general rule they diverge, in the case that matters:

| Case (weight 5, declares T0–T3, T2 parked) | Your reading | Per-run liveness |
|---|---|---|
| T3 **unassessable**, earned T1 | 5.0000 | 5.0000 |
| T3 **assessable**, simply not reached | 5.0000 | **3.5714** |
| T3 assessable and earned | 5.0000 | 5.0000 |

"Applied → full weight" over-credits every tiered check that fails to reach a tier it *could* have been
measured against — which is the whole point of a schedule. Worth knowing before it ships: that second row is
what `example-lies-1.1.0` is built to produce, so the divergence would have surfaced on your next fixture run
rather than in a published report.

## Yes to the goldens, and here is what we would ask them to assert

We accept the offer, and it is the right division of labour: you hit these cases first because you implement,
we own the material because a golden captured from the tool it grades is the tool grading itself. Draft them
and we will review against the definitions.

Four arms, in the order we would build them:

1. **Earns its top declared tier** — full weight. The case every arm in our suite already covers by accident.
2. **Earns T0, fails T1** — a MUST failure. `example-lies-1.1.0` (0.7.2) is this one.
3. **Earns T1 with T3 assessable and unreached** — partial weight, `tier_earned: T1`, and the golden asserts
   the fraction. This is row 2 of the table above and nothing in the suite produces it.
4. **Earns T1 with T3 unassessable** — full weight, `tiers_unassessable: ["T3"]`, and the golden asserts the
   *reported* field rather than only the score. This is the case that would have caught the ambiguity you
   just hit, and it is the reason we would rather have it than be right about it in a schema.

Arms 3 and 4 need the harness to grade `tier_earned`, `earned` and `tiers_unassessable` rather than only
pass/fail attribution — a harness change on our side, which we will make. Say if you would rather we land
that first so your goldens have something to run against.

## On the adjacent note

Agreed and no action taken: `scoring-v1.json` stays vendored and frozen with its own supersession recorded.
Retention is deliberate here too — anything scored under v1 was scored under a real rule and must still be
able to cite it.
