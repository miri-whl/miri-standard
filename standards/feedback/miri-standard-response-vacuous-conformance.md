# Response: Vacuous Conformance (0.1-draft)

*Response Version: 0.1*
*Status: miri-standard maintainers' response*
*Created: 2026-09-10*
*In reply to: [vacuous-conformance-proposal.md](vacuous-conformance-proposal.md)*

All three findings verified against the checklist and accepted. Before the substance, one thing that changes what you
need to do:

Your §4 fix already exists, and you scored against a commit that predates it. You pinned `cc5d0a4`, which is
`origin/main`; ten commits sit unmerged on `phase-0.4.1`. Your preferred option (a) — score over the checks that were
applicable, denominator carried in `lint-report-v1`'s `scores` block — is exactly what landed. You named the same design
independently, including where the denominator belongs, which is good evidence it's right. Please re-pin before
implementing §4. Three things changed that your analysis predates:

- A conditional check whose condition does not apply is now excluded from both numerator and denominator, never awarded
  weight.
- `scores` now requires `effective_denominator`, `excluded` and `forfeited`, and a skipped outcome must name its reason.
- A forfeited MUST leaves conformance `undetermined` — a new grade value. Not non-conformance: the obligation applied
  and went unassessed.

That last one bears on your §1.1. You wrote that fixing seven conditional checks moved no score "because a
not-applicable skip and a pass both award full weight." True at your pin; not any more. Your fix now changes scores, and
an offline no-deprecation package is scored out of 78, not the 87 you computed — 87 counts the four not-applicable
checks; the three capability forfeits also leave the denominator.

**§2 accepted, and verifying it found a second instance.** MIRI-PY-008 now fires on `patterns: []`, and
`usage-patterns-v1.json` carries `minItems: 1`.

Your consistency argument is the part that decided it: MIRI-PY-021 already says "absent, null, or an empty array", so
the standard knew how to say this and said it in one place out of three. But you wrote that an empty `api_index` "fails
MIRI-PY-007 on other grounds" — it does not. 007's clause quantifies over entries, so an empty index satisfies it
vacuously, and it validated against the schema. Fixed too: a clause on 007 and `minProperties: 1` (it's an object, so
`minItems` wouldn't apply). `AGENT_EXAMPLES.json` has no schema at all, which we're recording rather than fixing here.

This is the fifth instance of one defect class — a check testing the form of a thing without testing that the thing
occurs. The others were MIRI-CLI-013, 034, 022 and MIRI-CONSUMER-041. Yours is the first found by an implementer rather
than a review panel, and the method is the transferable part: treat each `fires_when` clause as normative and test it
empirically.

**§3 accepted with one change.** Your diagnosis holds — 001–003 are properties PyPI enforces at upload, and your
sabotage matrix showing the checks do move is what makes the argument rather than assumption. But option (a) as written
would discard 004 and 005, which are SHOULDs, not preconditions, and 005 is the only check in the category that varies.

So: gate the three MUSTs, keep the two SHOULDs scored, redistribute 6 points into Agent Metadata Core and Examples.
`weight: 0` means "extension check" today, so gating gets an explicit `scoring: gate` field rather than overloading
zero. One thing you'll see after merge that your analysis predates: 005 is now excluded offline rather than
auto-passed, so Category A reads 8/8 rather than 8/10 — still constant, so your point survives, but the arithmetic
differs.

**We are not taking your §4(b):** reweighting Deprecation & Lifecycle and renormalizing would penalize a deprecation
history twice.

Two small things in your document. The abstract calls Deprecation & Lifecycle Coherence "Category D" while your legend
maps D to Identity & Security. And the reproduction block pins a commit that predates the work answering your main ask
— worth re-running once we merge, because four of your six category scores will move.
