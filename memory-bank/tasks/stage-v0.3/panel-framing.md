# Panel framing — read before running any v0.3 review

The Miri Standard is being built **spec-first, deliberately**. Every panel prompt from here on MUST carry the
following framing, because two rounds have now spent effort on a question that is out of scope at this stage.

## The stage we are at

Set up the problem → propose how to tackle it → **verify the proposal actually solves the stated problem, end to
end** → get a solid plan → *then* implement → see results → iterate the spec from what is learned.

We are at the third step. The deliverable is a **fully realized end-to-end document** before anything is built.

## What to tell the panel

**In scope — this is what we want attacked:**

- Does the proposed mechanism actually solve the stated problem, end to end?
- Can a developer's real journey be walked from start to finish using only what the spec promises?
- Is anything missing, unreachable, self-contradictory, or unspecified to the point that two conformant
  implementations would diverge?
- Would an implementer building strictly to these documents write dead or wrong code?
- Is any clause un-checkable, or does any security claim lack a mechanism?

**Out of scope — do not score on this:**

- "Where is the evidence this helps?" / "the consumer end does not exist yet" / "this widens the gap between what is
  asserted and what is shown."
- The reference implementation's current behavior, **except** as a factual note that a spec clause is not yet
  implemented. Absent implementation is the plan, not a deficiency, and MUST NOT reduce a score or appear as a
  finding.
- Adoption, external adopters, and the pre-registered experiment's readout. All of these come **after** the spec is
  complete, by design.

## Why the distinction is worth drawing

It is not that the panel has been wrong — the most valuable findings so far were exactly the in-scope kind. The
journey walk-through, the composition break between the two pillars, the missing testing element, the forgeable
envelope: all of those asked *"does the proposal solve the problem?"* and all of them were right and worth the run.

What has been unproductive is the proof-demanding lens applied to a design-stage document — it produces the same
finding every round ("no evidence yet"), it cannot be resolved by any amount of spec work, and it crowds out the
completeness critique that is genuinely useful. Bound it explicitly in the prompt.

## Measuring progress

Progress is measured against **spec completeness and end-to-end coherence**, never against implementation status.
A want is "delivered" when the specification fully and coherently provides for it — implementation and empirical
validation are separately tracked, later phases.
