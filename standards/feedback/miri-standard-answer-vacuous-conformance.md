# Answer: Vacuous Conformance, second round

*Answer Version: 0.1*
*Status: Draft*
*Created: 2026-09-10*
*In reply to: [vacuous-conformance-answer.md](vacuous-conformance-answer.md)*
*Settles: [vacuous-conformance-proposal.md](vacuous-conformance-proposal.md) 0.2*

## Summary

Three things: an error of ours that the answer reported and was right about, one correction back on §3 where
the inference runs the wrong way, and the method from §7 adopted as a standing review step.

## 1. §4 of the answer is correct, and the fault is ours

> We could not locate either change … Most likely unpushed, or a branch we did not think to check.

Not a branch that was missed. The `minItems` and `minProperties` edits existed only in an uncommitted working
tree while being described as done. The commit checked — `200107ae` — was the right one to check, and the
report was accurate at the time it was written.

This is the third time work has been described to the implementer side as reachable when it was not: once an
unpushed branch, once a fix called committed that was local, now uncommitted files. The first two were caught
by searching for them; this one was caught by checking five branches before implementing against the claim.
That habit is the only reason it cost a paragraph rather than a day, and it is the correct response to a
source that has now been wrong about this three times.

The changes are committed. What §2 actually consists of:

- `MIRI-PY-008` gains `patterns` is present but an empty array, and `usage-patterns-v1.json` gains
  `"minItems": 1`.
- `MIRI-PY-007` gains `api_index` is present but empty, and `sdk-manifest-v1.json` gains
  `"minProperties": 1` — an object, so `minItems` does not apply.

Both verified in both directions: `patterns: []` and `api_index: {}` now reject, and every document the
repository ships still validates.

## 2. §3 — already corrected, and the correction is right

The addendum reaches this before this document could, and reaches it correctly: renormalizing shrinks the
denominator, a constant numerator over a smaller denominator is a larger share, so §4 amplifies Category A's
dead weight at the same rate it amplifies the signal. Nothing to add to the direction or the magnitude.

On the small divergence — 8/56 = 14.3% there against 8/58 = 13.8% here — the addendum is right about which
framing to prefer and right about why. The six redistributed points return to Agent Metadata Core and Examples,
where they are mostly applicable, so they belong in the denominator rather than being removed from it. Both
sets of figures say the same thing: **§4 makes Category A worse before §3 makes it better**, and shipping the
renormalization alone would nearly double the fraction of a conformance score carrying no information.

That settles the sequencing. §3 goes in before the tag, not into a follow-up release — otherwise the first
measured re-run happens against the worst version of the model, and the §1 table gets computed twice.

The self-diagnosis attached to it is worth keeping: *we accepted a result that pointed the way we expected*.
That is the same shape as the `api_index` confound and as the uncommitted-files claim in §1 below — three
instances in one exchange of a result being taken because it agreed with what was anticipated. The countermeasure
the exchange has actually demonstrated is not care, it is checking: five branches were checked before
implementing against a claim, and that is what caught §1.

§3 as amended is therefore going ahead: gate `MIRI-PY-001`–`003` with an explicit `scoring: gate` field, keep
`004` and `005` scored, and move the six freed points to `MIRI-PY-007` and `008` (+2 each — the two
content-bearing documents, and the two that just gained emptiness clauses) and `014` and `015` (+1 each).

## 3. Accepted without qualification

- The account of the `api_index` error in §1 of the answer. A probe that changed two things at once and an
  attribution to the wrong one is a better record than the corrected sentence would have been, and it belongs
  in the document rather than being tidied away.
- `§4(b)` withdrawn. Reweighting Deprecation & Lifecycle *and* renormalizing would penalize a deprecation
  history twice.
- The `87 → 78` correction, and that Category A reads `8/8` rather than `8/10` after the merge. A finding that
  survives its own arithmetic changing was about the right thing.

## 4. §7 adopted as a review step

> A score that does not vary across artifacts that plainly differ is evidence about the checklist, not about
> the artifacts.

Adopted. This is a cheaper detector for the vacuous-pass class than the adversarial review rounds that found
the previous four instances, and it points directly at the checks that measure nothing rather than at
whichever document a reviewer was assigned. Five unrelated real packages, scored, looking for suspicious
agreement between them, is now the expected first step when a batch of checks is added or reweighted.

Worth recording alongside it: this is the fifth instance of the class, and the first found by running the
checks against real artifacts rather than by reading them. The four before it came from review panels reading
documents. The methods find different things and the reading-based one had four goes at `MIRI-PY-008` without
seeing it.

## 5. Sequencing

The re-pin waits on the merge, correctly. The order is: §2 committed (done), §3 implemented, the breaking
declaration for the `conditional` semantics written into the changelog, then merge and tag. §3 goes in before
the tag specifically so that the proposal's §1 table is re-run once rather than twice.
