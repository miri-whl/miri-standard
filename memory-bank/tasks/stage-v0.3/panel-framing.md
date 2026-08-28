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

## The panel personas — spec reviewers, not implementation reviewers

The persona definitions are where scope discipline actually lives. Earlier rounds used implementer-shaped lenses
("a maintainer trying to build a conformant server"), and an implementer lens *invites* "where is the code" — the
reviewer reaches for the implementation because that is what the role would do. The fix is not a longer prohibition
list; it is lenses whose natural question is already about the text.

Each persona below asks a question that can only be answered **by reading the specification**. None of them can be
answered by inspecting an implementation, and none is made easier by one existing.

| Persona | The question it exists to ask |
|---|---|
| **Conformance editor** | Is every normative clause decidable from the text alone? Could a checker be written against this sentence without asking the author what it means? |
| **Two-implementations reader** | If two teams built independently from this text and never spoke, would their results interoperate? Every place the answer is "only by coincidence" is an under-specification. |
| **Adversarial reader** | Reading only the threat model and the normative clauses, what attack does the text fail to forbid? Not "is the code vulnerable" — "does the specification leave it permitted". |
| **Journey completeness reader** | Walk the maintainer's end-to-end scenario using only what the text promises. Where does the text stop providing? |
| **Internal-consistency editor** | Contradictions, dangling cross-references, undefined terms used normatively, counts that disagree between prose and source, clauses that bind no actor. |
| **Scope-and-honesty editor** | Where does the text claim more than it defines? Where is a SHOULD doing a MUST's work, or a MUST unenforceable? Where does a definition exist with nothing depending on it? |

**Reviewers may consult the fixtures and check YAMLs**, but only to verify that a claim the *specification* makes
about them is accurate — for example, that a profile's stated check count matches its YAML. Assessing fixture
coverage, implementation status, or adoption is out of scope; those are separately tracked and are not what this
round is for.

## The sentence to put at the top of every persona prompt

> You are reviewing a **specification**, not a project. The reference implementation is deliberately unbuilt: this
> project specifies first and builds second, on purpose. "This is not implemented yet", "there is no adoption", and
> "where is the evidence" are **out of scope and must not appear in your findings** — they are true, intended, and
> already known. Your entire job is whether the text is complete, decidable, consistent, and sufficient.

## Deferred: run the panel through arghos instead of ad-hoc subagents

`~/work/patitur/code/arghos` is a **general** panel tool (its README: "The tool is general; the sample panel it ships
with is grounded in an industrial-IoT / OT-security domain"). Every v0.3 panel so far was built as ad-hoc Workflow
subagents instead — arghos has not been run since 2026-06-15. That was an oversight, not a decision.

**What fits.** `panel/scenarios/website/` is `kind: critique` — a panel reacting to extracted document artifacts,
with `prompts/system.md` + `prompts/critique.yaml`, artifacts as markdown, and run persistence under
`runs/<timestamp>/` (`report.md`, `report.html`, `responses.jsonl`, `analysis.json`). That is structurally what our
spec reviews do by hand, and it would give versioned personas, run history and report rendering for free.

**What does not fit yet.** `panel/personas.yaml` is buyer-shaped — verticals, role titles, org-size weights,
regulatory weights. The six spec-editor lenses (conformance editor, two-implementations reader, adversarial reader,
journey completeness, internal consistency, scope-and-honesty) have none of those dimensions. Adopting arghos means
either a second persona schema or forcing spec lenses into a buyer shape, and the latter would be worse than the
subagents.

**Two separate follow-ups, both after v0.3 spec fixes land:**

1. Assess whether a `kind: critique` scenario with a non-buyer persona schema is a clean fit for spec review.
2. **Make the `arghos` CLI MIRI-CLI compliant** — an internal CLI scored against our own CLI suite is exactly the
   dogfooding the standard has been missing, and it is a real adopter rather than a sample.
