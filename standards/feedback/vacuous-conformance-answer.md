# Answer: Vacuous Conformance Response

*Answer Version: 0.2*
*Status: Draft — miri-py's reply, with an addendum answering the second note*
*Created: 2026-09-10*
*In reply to: [miri-standard-response-vacuous-conformance.md](miri-standard-response-vacuous-conformance.md)*
*Revises: [vacuous-conformance-proposal.md](vacuous-conformance-proposal.md) to 0.2*

## Summary

All corrections accepted. The proposal is revised to 0.2 with six
`[corrected]` markers in place and a §7 revision record.

We verified each of your statements against `phase-0.4.1` directly
rather than taking them from this response, because the failure that
produced our errors was accepting a result without checking what
produced it. One of your claims we could not confirm, reported in §4
below.

The **addendum** at the end answers your second note: your correction to
our §3 inference is right and we have measured it, the denominator and
the 25 → 3 figure are confirmed, and our answer on opening the PR is
yes — with one condition on when §3 must follow.

## 1. The `api_index` error is ours, and it is the instructive one

You are right, and the way we got it wrong matters more than the fact.

Our probe hand-built a manifest to test an empty `api_index`. It carried
`miri_version: "0.2.0"`, which fails the schema's `^\d+\.\d+$` pattern.
MIRI-PY-007 went red, and we recorded that as the empty index being
caught "on other grounds".

Re-run against the valid fixture with only `api_index` emptied:

```text
  valid fixture          007 -> passed
  api_index = {} only    007 -> passed
```

007 passes. A sabotage that changes two things at once tests neither.

This is the same defect class the document is about — a clause
quantified over an empty set — in the same file as the instance we
reported, and we missed it inside the analysis that found the other one.
The method we proposed in §1.1 is to treat each `fires_when` clause as
normative and test it empirically; we applied that to the checks and not
to our own evidence. We have added it to §7 rather than quietly fixing
the sentence, because the failure mode is the transferable part.

## 2. §4 confirmed, and withdrawn as an ask

Read at `200107ae`, not taken from your response:

```text
schemas/lint-report-v1.json
  scores.required = ["conformance", "effective_denominator",
                     "excluded", "forfeited"]
  scores.properties includes "undetermined"

standards/python/linter-checklist.md
  "excluded from both the numerator and the denominator"
  "a forfeited MUST leaves conformance undetermined"
  "undetermined is not non-conformance"
```

The excluded-versus-forfeited distinction is finer than what we
proposed. We had one bucket for "did not run"; you have two, separated
by whether the obligation applied. A forfeited MUST yielding
`undetermined` rather than non-conformance is the part we would not have
arrived at — we would have had to choose between failing an artifact for
a capability the linter lacked and silently passing it, and both are
wrong.

Our §1.1 claim that fixing the seven conditional checks moved no score
is corrected: true at `cc5d0a4`, false after. The fix changes scores
under the new model. 87 → 78 is confirmed by arithmetic:

```text
  checklist total            100
  category E not-applicable  -13   (028, 029, 031, 032)
  category E forfeited        -9   (030, 034, 035)
  we said                     87   (removed n/a only)
  correct                     78
```

## 3. One observation on the corrected arithmetic

78 is category E's contribution. Across all six categories the effect is
larger, because every category has exclusions. For the five wheels in
the proposal's §1, the applicable denominator is **56 to 60**.

Projected onto the new model — earned points over applicable points,
with not-applicable weight removed from both sides:

| Package | Today | Earned | Applicable | Projected |
|---|---:|---:|---:|---:|
| miri-py | 79/100 | 56 | 56 | **100%** |
| patitur-sdk-api-client | 47/100 | 24 | 56 | **43%** |
| google-ai-generativelanguage | 40/100 | 17 | 56 | **30%** |
| google-api-python-client | 40/100 | 17 | 56 | **30%** |
| grpcio | 36/100 | 17 | 60 | **28%** |

Two consequences worth naming before anyone meets them in a report.

The spread widens from 36–79 to 28–100. That is the discrimination the
proposal asked for, and it arrives from §4 rather than from §3 — which
is a reason to expect §3's redistribution to matter less than we argued,
not more.

> **[superseded — see the addendum, §1.]** The second sentence is
> wrong. Renormalizing shrinks the denominator, which amplifies a
> constant numerator as much as it amplifies the signal: Category A's
> dead share goes from 8.0% to 14.3% under §4, and only §3 collapses it
> to 4.0%. §3 gets *stronger* under §4, not weaker.

A conforming package can now reach 100%, because the free weight it used
to collect from inapplicable checks is gone from both sides. miri-py
moves from 79 to 100 without the artifact changing. We think that is
correct and we are not asking for it to change; we flag it because
anyone tracking a score over time will need `effective_denominator` to
explain it, which is precisely why the field is required.

These are projections computed from outcomes we already have, not output
from a re-pinned linter. We will replace them with measured numbers.

## 4. One thing we could not find

You state that MIRI-PY-008 now fires on `patterns: []` with
`minItems: 1` in `usage-patterns-v1.json`, and that 007 gained a clause
with `minProperties: 1`. We could not locate either change:

```text
branch                          patterns.minItems   api_index.minProperties
phase-0.4.1 (200107ae)          absent              absent
phase-0.4                       absent              absent
review/all-four                 absent              absent
fix/advisory-coverage-schema    absent              absent
main (cc5d0a4)                  absent              absent
```

Most likely unpushed, or a branch we did not think to check. Raised only
so we do not implement §2 against definitions that turn out to differ.
No answer needed if it is in flight.

## 5. What we accept without qualification

**§3 as amended.** Our option (a) treated the whole category as a
precondition and would have discarded two SHOULDs to do it. Gating the
three MUSTs while keeping 004 and 005 scored is the correct cut, and
`scoring: gate` rather than overloading `weight: 0` is right for a
reason we should have seen: zero already means something.

**§4(b) withdrawn.** Reweighting Deprecation & Lifecycle *and*
renormalizing would penalize a deprecation history twice. We did not see
that, and it is obvious once stated.

**Category A reads 8/8 after the merge**, not 8/10. The finding survives
the arithmetic changing, which is the test of whether a finding was
about the right thing.

**The "Category D" slip** in our abstract is an editing error; the
legend in §1 is correct and the body is consistent with it.

## 6. What we will do

1. **Re-pin** to `phase-0.4.1` once it merges (`make sync-checks`). We
   are not pinning to an unmerged branch, so the work below waits on the
   merge rather than on us.
2. **Implement the model**: exclusion from both numerator and
   denominator, the three newly required `scores` fields, a skip reason
   on every skipped outcome, and the `undetermined` grade. Our
   `CheckOutcome` already carries `skip_reason` and distinguishes
   `condition_not_applicable` from the capability forfeits, so the
   classification exists; what changes is the scorer and the report.
3. **Implement §2** once we can see the 007/008 definitions.
4. **Re-run the proposal's §1 table** and replace the projection in §3
   above with measured output.
5. **Carry the method forward.** We are treating "does each `fires_when`
   clause have a test that fails without it" as a standing check on our
   own implementation rather than a one-off audit. Three clauses were
   unimplemented when we looked (006, 014, 037); we would rather find
   the fourth ourselves than have it reported to us.

## 7. On the defect class

You note this is the fifth instance of a check testing the form of a
thing without testing that the thing occurs, and the first found by an
implementer.

The reason it surfaced here is worth recording, because it was not
diligence. We scored five unrelated wheels and three returned identical
section scores. That looked wrong, and chasing why it looked wrong is
what produced everything in the proposal — the seven conditional checks,
the three unimplemented clauses, and MIRI-PY-008.

The transferable part is therefore not only "test each clause". It is
that **a score that does not vary across artifacts that plainly differ
is evidence about the checklist, not about the artifacts.** Running a
handful of real, unrelated packages and looking for suspicious agreement
is cheap, and it points at exactly the checks that measure nothing. We
would suggest it as a review step for new check batches.

---

## Addendum: §3 gets stronger under §4, not weaker

Added 2026-09-10, after the maintainers' second note.

### 1. Our inference was backwards

We wrote, in §3 above:

> The spread widens from 36–79 to 28–100. That is the discrimination the
> proposal asked for, and it arrives from §4 rather than from §3 — which
> is a reason to expect §3's redistribution to matter less than we
> argued, not more.

That is wrong, and the correction is the useful part of this exchange.

Renormalizing shrinks the denominator. A constant numerator over a
smaller denominator is a *larger* share, so §4 amplifies the dead weight
in Category A at the same rate it amplifies the signal. Measured across
the five wheels:

| Model | Category A's constant share |
|---|---:|
| Fixed 100 | 8/100 = **8.0%** |
| After §4 renormalization | 8/56 = **14.3%** |
| §4 with §3's gate and redistribution | 2/50 = **4.0%** |

(grpcio, whose denominator is 60 rather than 56: 8.0% → 13.3% → 3.7%.)

Our figures differ slightly from the maintainers' 8% → 13.8% → 3.5% at
58/57, and the difference is only where the six redistributed points
land: we removed them from the denominator entirely, the response
returns them to Agent Metadata Core and Examples where they are mostly
applicable. Their framing is the correct one. The direction and the
magnitude are the same either way.

**So §4 makes Category A worse before §3 makes it better.** Shipping the
renormalization alone nearly doubles the fraction of a conformance score
that carries no information. That is an argument for sequencing §3
close behind §4, not for deprioritizing it.

We should have caught this. We had both models in front of us and
reasoned about the spread — the visible number — without checking what
happened to the constant. The same shape as the `api_index` mistake:
we accepted a result that pointed the way we expected.

### 2. Confirming the rest

**Denominator.** We get 56 for four wheels and 60 for grpcio, inside the
58 band. Confirmed.

**Deprecation & Lifecycle offline: 25 → 3 applicable points.** Confirmed
— 13 not applicable, 9 forfeited, leaving MIRI-PY-033's 3. That is the
proposal's §4 case stated more sharply than our own table managed: we
reported the section as scoring a constant 13/25, when the truer
statement is that 22 of its 25 points are not in play at all.

## 3. On opening the PR now

**Yes — open it with the breaking declaration, hold §3 for the
follow-up.** Three reasons, and one condition.

It unblocks us today. §4 is finished and §3 is not: where the six
redistributed points land is a decision that wants its own discussion,
and it should not hold up a change that is already designed and
verified.

The re-scoring cost you are trying to spare us is not a real cost. We
have no tags and nothing published; re-running the five wheels takes
seconds and regenerating the reports is one command. Two re-scores cost
us nothing.

The cost that would be real is a *published* score moving under someone
tracking it, and that has not started yet. So the condition is not
"bundle them" but: **§3 lands before any release that publishes
conformance numbers externally.** Given §1 above, shipping §4 alone and
leaving it would be the worst of the three states — the dead fraction at
14.3% rather than 8% or 4%.

We would rather re-score twice than have the first published baseline be
the one where Category A is at its least informative.

## 4. On the review step

Adopting the "identical scores across artifacts that plainly differ"
check as a standing review step for new check batches is the outcome we
would have hoped for. One caveat from having run it: the signal is
*suspicious agreement*, not agreement. Categories B, C, D and F agreed
across the three Google wheels too, and there the agreement was true —
they fail as an ecosystem, for the same reason, and that is a finding
about the ecosystem rather than about the checklist. What distinguished
A and E was agreement that survived a package which differs in every
respect that the category measures. The step is cheap; the judgement
about which agreement is meaningful is not automatable, and we would not
want it written down as though it were.

## 5. Our state

Nine commits on `phase-0.4-stage-3`, no tags, working tree clean. The
conditional-semantics fix, the three substance clauses, and the reports
are all in. We are waiting only on the merge to re-pin.
