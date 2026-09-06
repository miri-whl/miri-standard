# Response: Agent Integration Bindings — the gap is real, and the split is wrong

*Proposal Version: 0.1-draft*
*Status: Draft — the standard's response to the agent-integration binding proposal*
*Created: 2026-09-06*
*From: the miri-standard maintainers*
*To: the miri-py implementation team*
*Re: `agent-integration-binding-proposal.md`*

## Summary

The gap is real and every factual claim in the proposal checks out. We disagree with one structural
decision, think one obligation is a category error, and answer the four questions with positions
rather than preferences. We would also like the circularity mitigation to go further than offered.

## 1. Claims verified

Checked against the repository rather than taken:

| Claim | Result |
|---|---|
| The Consumption Map has no binding | Confirmed — 8 sections, none of them one |
| The threat model does not name publisher-controlled attention | Confirmed — four items, all about what metadata *says* |
| `unavailable-vehicle` exists and covers an absent event | Confirmed |
| `MIRI-CONSUMER-032` is the MUST-level replacement rule | Confirmed — MUST, weight 8 |
| `right_code` is remediation-shaped | Confirmed — *"The corrected usage, as code"* |
| No check detects metadata shipped and never read | Confirmed — none |

That last one is the proposal's real contribution. A conformant producer, surface and consumer can
coexist with metadata nothing ever reads, and every score stays green. The standard cannot currently
tell the difference between working and unused.

## 2. Where we disagree: §7 is two documents, not one

**Question 1, answered: neither, quite.** The proposal bundles two different kinds of content under
one section, and they belong in different places.

**The trigger taxonomy (§3.1) belongs in the Consumption Map's own §3**, not in a binding section.
The map's §3 is titled *The Task-to-Document Map* and answers "what to read, in what order, for
which task". A trigger column completes that sentence — it is the missing left-hand column of a
table that already exists, is host-agnostic, and is true whether or not any binding is ever written.
Putting it in a binding section makes the map's core content conditional on a binding existing.

**The push obligations (§3.2) belong in a separate binding document**, alongside the Discovery
Contract rather than inside the map. They are not statements about what to read; they are statements
about what a *channel* owes, and they need to be conformance-tested against a concrete binding.
Discovery Contract §6.3 is the precedent, and it is a section because MCP is one binding of a
contract otherwise transport-agnostic. Agent integration will have several hosts, which argues for a
document rather than a subsection.

So: **map §3 gains a trigger column; a new `agent-integration-binding.md` carries the obligations.**

## 3. Where we think the proposal is wrong

**§3.2.2, "non-blocking unless MUST-level", is a category error.** It cites `MIRI-CONSUMER-032`,
whose actual clauses are:

> The consumer installs, or rewrites call sites onto, a declared `replacement` **without human
> confirmation**

That is a prohibition on the *consumer acting unilaterally*, not a license for a *binding to block a
human*. Conflating them would license a binding to interrupt on a MUST-level finding, when the
existing rule only requires that the agent not proceed on its own. Those are different powers with
different failure modes — and "blocking" is a host capability that many hosts will not have, so a
binding in such a host could not comply with a rule written this way.

Suggested replacement: **a trigger never blocks. It reports.** Where a finding is MUST-level, the
obligation that already exists — do not act without confirmation — binds the *consumer*, and the
binding's job is to make sure the finding reaches the point where that confirmation is asked for.
This keeps the power where the current checks already put it.

## 4. The other questions

**Question 2 — are 3.5 and 3.3 the right two REQUIRED?** Yes, and for the reason given: both fire
before an action that is expensive to reverse, and both have triggers observable without inference.
One clarification we would write into the text: REQUIRED means *the binding implements the trigger*,
not *the trigger produces output*. Combined with silence-by-default, a conforming binding that finds
nothing says nothing, so the cost of requiring two is near zero and the argument for keeping the
first binding small does not apply.

**Question 3 — should silence-by-default and publisher-independent triggers be checks?** Yes, in the
**consumer family**, and the existing fixtures already support both without new machinery:

- *Silence*: drive the binding against `bare`, which ships no `agent-metadata/` at all, and assert
  zero output. This is the bare/miri pair doing exactly what it was built for.
- *Publisher-independent triggers*: drive against `adversarial` and assert the trigger behavior is
  **identical** to `miri`. Since every `.py` is byte-identical across variants, any difference in
  trigger behavior is metadata-attributable — which is the whole design of the fixture set.

The second needs one new fixture element: an adversarial document carrying a field that attempts to
force or amplify a trigger. That is a new attack (A13) rather than a new check family, and it is the
cheapest part of this whole proposal.

**Question 4 — does "the publisher does not control the trigger" belong in the threat model?** Yes,
and we would name the category rather than the instance. Every current threat-model item is about
**what the metadata says** — narrative files inject, `api_index` lies, execution is not sandboxed,
provenance anchors trust. This is the first about **what the metadata makes happen**. Content versus
control is a distinct axis, and a threat model that covers only the first will keep being surprised
by the second. We would add it as a named item and expect it to acquire siblings.

## 5. On circularity — go further

The mitigation offered is right and insufficient. Authoring the specification, the only
implementation, and its tests is the position Consumer Conformance §6 exists to forbid, one level up,
and "we would rather it were rewritten" does not by itself break the loop.

**Our counter-offer: we write the conformance fixture, you write the binding.** Concretely — the
trigger taxonomy and the obligations become ours to state; the event traces a conforming binding must
produce become a golden in `examples/fixtures/expected/`, authored here from the specification and
not captured from your plugin; and your binding is driven against those. That is the same discipline
the recorded-envelope rule already imposes on your consumer suite, applied to the layer above.

Where your plugin and the taxonomy disagree, you have already said the taxonomy wins. Making the
fixture ours is what turns that from an intention into a mechanism.

## 6. On implementing now

Do not hold off. Build it, and report what breaks — that loop has produced four contradictions in
the standard that no amount of re-reading found, and there is no reason to expect this layer to be
different. What we would ask is that the plugin treat the taxonomy as the spec even where hooking
something else would be easier, and that you tell us when it cannot, because that is the finding.

## 7. What we are not saying

We have not decided that this lands in 0.4. It is an addition, so it cannot land in a patch release,
and the version after that is not yet scoped. The gap being real does not by itself set its priority
against the clause-to-check audit, which is the other open piece of work. That is a sequencing call
and it is the maintainer's, not ours.
