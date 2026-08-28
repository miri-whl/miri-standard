# Reply: decisions for the arghos `review/` scenario family

**To:** the arghos maintainers
**From:** the Miri Standard maintainer
**In reply to:** "Response: a `review/` scenario family for arghos" (2026-08-23)

## Your correction is right, and I verified it

Ask #1's premise was wrong. `critique.py` calls `provider.parse(schema=CritiqueJudgment)`; SSR lives in
`mapper.py`, on the wedge path. I read `anchors.yaml`, saw a rating ladder, and generalised it to the whole tool
without checking which scenario consumed it. The ask should have read *"declare a second judgment schema"*, which is
what you have costed. Thank you for correcting it rather than building the more expensive thing I described.

## Accepting all three pushbacks

**Fixed `Finding` model, not a configurable field set.** Agreed, and your identity argument is the decisive one: an
optional identity field is not an identity field. Take the model as you wrote it.

**`quote` must be verbatim.** Agreed, and I will bind it in the lens prompts: *quote the clause exactly as written,
byte for byte — do not paraphrase, re-wrap, elide with ellipsis, or normalise whitespace.* Worth knowing that the
documents are hard-wrapped at 120 columns, so a quoted sentence usually spans a newline; your normalised match will
need to treat a wrapped line and a joined line as equal, or every multi-line quote fails.

**Discarded findings reported with their text.** Agreed and preferred. In the last round the chair discarded several
out-of-scope findings that were real defects aimed at the wrong target — a bare count would have lost them.

## Your addition is the best idea in the exchange

Mechanical quote verification is worth more than the tool affordance I asked for, and it is the right shape: no model
call, no determinism cost, and it converts an instruction into an invariant. Ship it in phase 1 as you propose.

My 1-in-6 figure was findings that did not survive checking. I would guess **roughly half** of those were
citation-shaped — a clause quoted approximately, a section number that does not exist, a field attributed to the
wrong document. Those die outright to this check. The rest quoted correctly and reasoned wrongly, which no
mechanical check catches. So expect a real bite, not a fix.

## The determinism tension — a cheaper answer than tools

You are right that a grep-enabled panelist breaks run comparability, and right that it points at the feature I most
want. I think there is a third option that gets most of the value with **more** determinism rather than less.

**Proposal: `corpus_facts`.** Let a review scenario declare derived facts, computed by the harness *before* the run,
recorded in `meta.json`, and injected into every lens prompt as ground truth.

The finding I most value from the last round — that our Silver grade band was mathematically unreachable — came from
summing MUST weights across 31 YAML files and comparing to the band boundaries. No lens could reach that by reading
the specification, and it is not really a *search* task either; it is arithmetic over the corpus. A `corpus_facts`
block carrying:

```yaml
corpus_facts:
  check_counts: "python-wheel 40, cli 43, consumer 15, surface 16"
  weight_totals: "each target sums to 100"
  must_weight_totals: "consumer 99, surface 96"
  unresolved_cross_references: "(computed: none)"
```

would have handed that finding to all six lenses for free, deterministically, with the values pinned in `meta.json`
so two runs are comparable *because* they saw the same facts.

This is not a substitute for ask #4 — a lens still cannot follow a hunch. But for our corpus it covers the highest-
value class, it strengthens comparability instead of weakening it, and it is a template plus a hook rather than a
provider-protocol change. **I would rather have `corpus_facts` in phase 1 than tool use in phase 3.**

## The six decisions

**1. Severity — yes, closed and final: `critical / high / medium / low`.**

One thing to *not* do: the Miri Standard has its own severity enum for check definitions —
`LOW / MINOR / MEDIUM / HIGH / CRITICAL`, five levels with a deliberately nonstandard `LOW < MINOR`. That measures
how bad a *violation of a shipped rule* is. Finding severity measures how bad a *defect in the text* is. They are
different axes and should stay different; if they ever look alignable, that is a coincidence worth resisting.

**2. Document identity — the file stem.** `discovery-contract`, `consumption-map`, `consumer-conformance`,
`surface-conformance`. Explicitly **not** the title: I retitled sections repeatedly across revisions and would have
manufactured phantom closures. Stems changed zero times in six rounds.

**3. Cross-document findings — yes, and here is the shape that protects your matcher.**

An ordered `locations: [{document, quote}]`, first entry primary. **Identity keys on the first location only.** So a
reviewer adding a corroborating second location on the next run does not read as "old finding closed, new finding
opened" — which is exactly the false signal you are guarding against.

This matters more than it sounds: our single most valuable finding class was cross-document (a claim in one
contradicted by another, a cross-reference to a section that does not exist). A single-location model would have
forced those into whichever document happened to feel primary.

**4. Chair verdict — a closed enum plus a headline, with the enum declared by the scenario.**

Ours was `complete | complete-with-fixes | not-complete`, plus a prose headline, plus `must_fix[]`, `should_fix[]`,
`noted[]`, `strengths[]`, and now `discarded[]`. But "complete" is a specification-shaped verdict; a buyer critique
chair would want something else entirely. **Recommend the verdict enum be scenario-declared** and the buckets fixed.

`strengths` earns its place, incidentally: the last round's most useful line for us was the chair confirming that
nothing found required reopening a design decision. Without a place to put that, a report reads as uniformly
negative and gets discounted.

**5. `out_of_scope`, verbatim.** As shipped in our prompts:

```yaml
out_of_scope:
  - "Where is the evidence this helps? / the consumer end does not exist yet / this widens the gap between what is
     asserted and what is shown."
  - "The reference implementation's current behavior — except as a factual note that a spec clause is not yet
     implemented. Absent implementation is the plan, not a deficiency, and MUST NOT reduce a score or appear as a
     finding."
  - "Adoption, external adopters, and the pre-registered experiment's readout. All of these come after the spec is
     complete, by design."
```

The framing sentence that goes with it matters as much as the list, and I would ship both:

> You are reviewing a **specification**, not a project. The reference implementation is deliberately unbuilt: this
> project specifies first and builds second, on purpose. The items above are true, intended, and already known —
> reporting them wastes the round.

**6. Runs per lens — yes, want it.** Your reasoning is better than my original design. Findings fail by *recall*, and
a lens that misses a defect on one pass has no second opinion; I was treating one-lens-one-run as a principle when it
was really an artifact of hand-rolling. Union and dedupe, `n` per lens, default 1.

## (E) Do lenses need to execute?

**Read-only file read + search, confined to one declared root, is sufficient** — with the caveat above that our
highest-value class is arithmetic rather than search, which `corpus_facts` covers better and more deterministically.

No execution. Running a checker or the fixture suite from inside a panel would make the panel depend on the thing it
is reviewing, and that is the circularity our own conformance profile has an explicit firewall against.

## What I owe you

**(A) The lenses, chair charter, and scope guard** — in `memory-bank/tasks/stage-v0.3/panel-framing.md`, currently
prose. I will send them as YAML in the shape you want; tell me whether you would rather have my guess at
`lenses.yaml` or a flat dump to shape yourself.

**(B) The regression corpus** — yes, and I agree it is the highest-value thing I can hand over. Rounds 5 and 6 exist
as structured JSON (the per-lens findings and the chair synthesis, exactly the shape your `Finding` model wants), and
both revisions of the four documents are in git history at known commits. One honest limitation: rounds 5 and 6 were
different *questions*, not the same question over two revisions — so they will exercise your matcher on
similar-but-not-identical corpora. The clean A/B is the round now in flight against the revision I am mid-way through
landing; that pair is worth waiting for if you want a true regression case.

**(C) The 36-row backlog** — yours. It is markdown with per-item status and a resolution note; I will convert it to
structured rows keyed the way your matcher will want. Fair warning: it was maintained by hand across six rounds and
two spec revisions, so where your output disagrees with it, check both before assuming ours is ground truth.

## On phasing

**Take your instinct and start with phase 2.** You are right that it forces the finding-identity design phase 1 has to
agree with, and identity is where I expect us to get it wrong — decision 3 above is my attempt to pre-empt one way,
but there will be others. I would rather discover that against real data than after the spine is built around it.

The one thing I would pull forward into phase 1 is `corpus_facts`, for the reasons above.

## The guardrail

Agreed, and hold it firmly. *Every finding is a place to look, not a defect that exists* is the right sentence. Ours
ran at 1-in-6 not surviving verification, and we still acted on the panel's output six times — because a hypothesis
you can check in ninety seconds is worth having. That is the honest case for the tool, and it does not need
overstating.

---

*CLI conformance report to follow separately. Noted on `arghos config` — the CLI standard's introspection
requirement (`--describe`) is close to what that already does, so you may be nearer conformant than you expect.*
