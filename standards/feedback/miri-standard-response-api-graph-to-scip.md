# Response: the graph is withdrawn, the index is a SHOULD, and the delta gap was ours

*Responding to: `standards-contribution/api-graph-to-scip.md` (miri-py, 359 lines)*
*Status: §1 accepted in full — `api-graph.json` withdrawn at 0.7.3. The format swap declined as proposed and
adopted in the narrower shape your own §8 identified.*
*Created: 2026*

## Answers to your three questions

**1. Does the standard want to specify a published index format rather than maintain its own graph?**
Yes for the format, and more than you asked for on the graph: **`api-graph.json` is withdrawn**, not replaced.
`MIRI-PY-010` is withdrawn with it and its 1 weight moved to **`MIRI-PY-045`** (SHOULD) — a precomputed index
under `.dist-info/`, declared in `sdk-manifest.json` `code_index`, with SCIP as the format and **no indexer
named**. That is your §7, taken exactly as argued.

**2. Guidance on the reduction — full, occurrences stripped, or references stripped?**
Declared, not prescribed. `code_index.reduction` is a closed set of `none` / `occurrences-stripped` /
`references-stripped`, and the wheel says which it applied. Prescribing one now would mean guessing the answer
to your §8's first question, and a standard that guesses is worse than one that carries the uncertainty in a
field. When the third-party-reader question is settled by measurement, the schema can narrow the set.

**3. Should the delta checks (030, 043, 044) be re-specified against the index?**
No — and this is the part of your report we need to correct, because the answer is a defect of ours.

## `MIRI-PY-043` already asks for what you could not compute

Clause 2, unchanged since it was written:

> An `api_index` entry whose `type` or **signature-bearing fields** changed between the two releases is named in
> no `releases[0]` entry's `symbols`

So the standard never asked for key-set diffing. What it asked for is a signature comparison — and then made
the field optional: `signature` in `sdk-manifest-v1` is not required, its own description says *"a consumer MUST
NOT assume its presence"*, and **our shipped sample SDK omits it on every `api_index` entry**.

Your delta detection was therefore not an approximation you chose. It is the only thing our documents support.
A MUST keying on a field we made optional and never populated ourselves is the same defect class as the scoring
one you sent the day before: a rule specified beyond what the format carries.

Two consequences we are naming rather than leaving you to find:

- **`MIRI-PY-043` currently passes vacuously** where `signature` is absent on both releases. No measured delta,
  no finding, full weight. That is a vacuous pass inside a MUST, in the check that exists to catch the largest
  class of API change.
- **Requiring `signature` is the fix, and it is not in 0.7.3.** Tightening an optional field newly fails
  producers who conform today, which is a bigger break than anything else in this release. It lands in 0.8.0
  with the sample SDK populated in the same change — the two halves together, because shipping the requirement
  while our own example violates it is how the current state happened.

**This gets you the 128 modifications without a protobuf decoder**, in a field every consumer can already parse.
Which is why the delta checks are not being re-specified against the index: the index makes the delta *cheaper*
for a producer's CI to compute, and `api_index` makes it *possible* for everyone.

## Why the swap is declined as proposed, from your own §5

You measured it and published the result that cut against you:

> Read end to end, **SCIP is only 1.3x cheaper than reading the source**, and **5x more expensive than the
> manifest we already ship**… The entire benefit is conditional on the consumer having a reader.

That is the objection, and it is decisive for the consumer-facing surface. This standard's premise is that the
wheel is the whole story because the consumer has nothing else; a payload whose value depends on tooling the
consumer may not have contradicts the premise rather than extending it. `api_index` stays the readable surface,
in JSON, and nothing in 0.7.3 deprecates it.

**Where the reader dependency does belong is a surface.** The Discovery Contract's `graph` operation now reads
the declared index (Discovery Contract §6) and is explicitly optional: where no `code_index` is declared it
returns `present: false` with a reason, and it is **never synthesized from `api_index`**, because a name-keyed
index cannot express an edge and inventing one would put a guess behind a field a consumer uses to plan a
change. A surface is a server: it can afford a protobuf decoder and it answers in the envelope's JSON. The
asymmetry lands where it is cheap, and the consumer keeps a JSON-only contract.

So your §5 finding did not weaken the proposal. It located it.

## §6 is the case, and we checked it before repeating it

We read the paper rather than the summary. arXiv 2604.09515, *"When LLMs Lag Behind: Knowledge Conflicts from
Evolving APIs in Code Generation"*: 270 real API updates across eight Python libraries, 42.55% executable
without documentation and 66.36% with it. Title, scope and both numbers are as you quote them.

It is now the standard's own argument, in Miri Wheel Extensions §5.5, with the attribution: adding structured
API documentation moved *executable* generated code by 24 points where chain-of-thought moved it by 2.34, and
**128 of the 270 updates were modifications** — the class a name-keyed graph cannot see, and the one that
produces the 12.3% "mixed old and new API in the same file" failure, because the name still resolves and the
call is wrong. That last sentence is the whole reason `api-graph.json` is withdrawn rather than extended.

§5.5 states the limits in the same breath as the case, because a case that needs its limits hidden is not one we
want implementers acting on: read whole an index costs more than the source, it is 22x cheaper only when queried,
which reduction is safe is unsettled, and cross-indexer symbol stability is untested.

## Your §8, item by item

- **Stripped index accepted by third-party consumers** — unresolved, and now recorded in the schema rather than
  in a document. `code_index.reduction` tells a consumer what it was handed, so if definition occurrences turn
  out to be load-bearing the answer is a narrowed enum rather than a silent re-cut of every wheel.
- **Index stability across indexer versions** — `code_index.produced_by` records the indexer and version, for
  exactly the reason you give: two producers emitting different symbol IDs for the same code breaks a
  cross-release delta. Untested on our side too, and named as untested in §5.5.
- **Non-pure-Python packages** — unmeasured by both of us. Stated as a limit, not papered over.
- **Whether consumers will have a SCIP reader** — this is the one your proposal turned on, and putting the
  decoder in the surface is our answer to it. A consumer with no surface and no decoder is exactly the case
  `api_index` serves, unchanged.

## What we take from the exchange

Three of your last four findings have the same shape: the rule could not be exercised by our own artifact. Every
tiered check on your wheel earns its top tier, so the tier divergence only appears on wheels a linter exists to
judge. Our sample SDK omits `signature`, so the delta clause that needs it has never been exercised by the
example we ship. The graph survived a Consumption Map review in 0.3 by being given a consumption role, and the
role turned out to be servable from somebody else's format.

We are closing that from the fixture end rather than by resolving to be more careful. 0.7.2 added an arm that
earns T0 and fails T1; 0.8.0 owes an arm whose `api_index` carries signatures that change, which is the artifact
that would have made your §4 unnecessary to write.

Two things about how you wrote this, because they are the reason it was actionable: §5 published a negative
result you could have omitted, and §8 put the potentially disqualifying uncertainty before the ask rather than
after it. The renumbering was right too — the arguments in §5 and §6 do not read as sub-points.
