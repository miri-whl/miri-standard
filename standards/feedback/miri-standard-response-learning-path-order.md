# Response: `order` ships, and it binds the array rather than advising the producer

*Responding to: `miri-py-learning-path-order.md`*  
*Status: Accepted. Ships at 0.9.0, with one property tightened and two added.*  
*Created: 2026*

## Disposition

**`order` is wanted, and "ordered" means ordered.** Your first question offers us the easier answer, that
`learning_paths[*].patterns` is a list rather than a set and the sequence is the producer's business. We decline it.
A consumer reading a beginner path reads it top to bottom and starts from the first entry, which is a reader-facing
sequence whatever the schema calls it, and a sequence a reader depends on cannot be left to whatever the generator
read first.

The field is in `usage-patterns-v1.json` at 0.9.0, and [Agent Metadata
§4.2.1](../python/miri-agent-metadata-specification.md) states the rules.

**The same question would have arrived about the document's other arrays**, so the schema now answers it once for
each. `learning_paths[*].patterns` is ordered and reader-facing. `categories[*].patterns`, `prerequisites` and
`related_patterns` are sets rendered as arrays, where position carries no meaning. That distinction was readable
from nothing but the word "Ordered" appearing in one description and not the others, which is not a place to leave
it.

## The three properties, confirmed

All three stand as you wrote them, and one is stated in your words because the reasoning is better than ours
would have been: `complexity` already answers the coarse question, and two fields deciding one order is how they
come to disagree. So `order` is comparable only within a complexity level. A `beginner` pattern declaring 9 still
precedes an `advanced` one declaring 0, and comparing the field across levels is undefined rather than merely
discouraged.

An absent value is not zero. A pattern declaring none sorts after every pattern of equal complexity that declares
one, which is the half that protects the one author who declared something from the majority who declared nothing.

A tie is not an error, and the producer breaks it. We tightened the verb: you wrote that a producer *should* break
it the same way on every build, and §4.2.1 says MUST, because the order of `patterns` and of every learning path
MUST be a function of the package's content rather than of the build host. Your sorted walk is therefore the
requirement now rather than hygiene, and the next producer does not get to rediscover this the way yours did.

## What we tightened

**Your field advises a producer. Ours binds the published array.**

As you proposed it, `order` is an input to a decision the producer still owns: "absent means the producer orders
it", with nothing said about what a *declared* value obliges. Read strictly, a producer could read every `order` in
the document and publish any sequence it liked, and the author who wrote `order: 0` would have exactly the
guarantee they had before, which is none. The field would describe an intention rather than carry one.

So §4.2.1 makes it a constraint on the document:

```text
within one learning_paths[*].patterns array

  two patterns of equal complexity, both declaring order
      → the lower value MUST appear earlier

  one declaring no order, one of equal complexity declaring one
      → the undeclared pattern MUST NOT appear first
```

That is decidable from the document alone, which the producer-input reading is not. It is also the version an
author can rely on: the reason to declare `order: 0` is that the published path will open with it.

## What we added

**The array as published is what a consumer reads.** A consumer MUST NOT re-sort it, by `order` or by `complexity`.
Without that sentence `order` becomes a second ordering, and a consumer applying it would silently overrule a path
the producer composed. A learning path is also not obliged to run beginner-first: this standard's own sample SDK
has a `production` path that opens on an `intermediate` pattern, because that is where production concerns start,
and a consumer sorting by `complexity` would have rewritten it.

Your capped line is on the right side of this. Leading with the beginner path's patterns is a selection from an
array, not a re-sort of one, as long as it keeps them in the order that path published.

**One `order` serves every path the pattern appears in.** The field sits on the pattern rather than on a path's
entry, so a pattern in three paths carries one value into all three. An author wanting a pattern early in one path
and late in another has only the arrays themselves, which carry that difference already. We considered the
alternative, turning `learning_path.patterns` into an array of objects with a per-path order, and declined it: it
breaks every existing reader of that array for a case nothing has reported. The array rule above is stated pairwise
for the same reason. It holds independently in each path the pattern appears in and never requires two paths to
agree about anything.

## What scores this

Nothing, and the spec says so rather than letting a reader assume otherwise. `MIRI-PY-008` validates
`usage-patterns.json` against its schema, which settles the field's type and says nothing about its relation to the
arrays, and JSON Schema draft-07 cannot compare one array's members against another array's contents.

The array rule is statically decidable, so a linter MAY report a violation and we would read a report that did. It
is not a check yet because the 43 active Python checks sum to exactly 100, so weighting this would take a point
from something already decided, for a field most documents will not declare. If it earns a definition it belongs in
the extension namespace `check-v3.json` already defines, `MIRI-PYX`, which carries weight 0 and scores health
rather than conformance, and which has no members yet.

The reproducibility requirement is a separate case: it is decidable only by building the same tree twice, which is
outside the artifact-inspection model, so §4.2.1 states it as a producer obligation and names why no wheel check
can see it. A build-system check could.

## What we are not standardizing

**The docstring convention.** `Order:` beside `Complexity:` is a sound place to put it and nothing stops you
documenting it as miri-py's authoring format. It does not belong in this standard, which specifies the document a
wheel ships and never how a generator read the package to produce it. A producer that extracts patterns from tests,
from notebooks or from fenced blocks in a README is conforming today, and codifying one extraction source would
make an authoring format part of the contract those producers are held to.

This is the same line the standard draws for `migration-guide.json`, which is derived from PEP 702 markers without
the markers becoming the schema.

## One thing back

**Do not sort the `patterns` operation's output by `order`.** Discovery Contract §3.7 now says this explicitly,
because the field looks like exactly the improvement a surface would make unprompted. The operation's ordering key
is the pattern `id`, the cursor is defined over that ordering, and `order` is optional and admits ties, so it is
not a total order over the array and cannot carry a continuation. A surface that sorted by it would make page
boundaries unstable for any document declaring the field on some patterns and not others, which is every document
that adopts it gradually.

The graph nesting from the previous round is still yours: `nodes` and `edges` at the envelope's reserved top level,
where §3.8 nests them under `graph`.

## Two notes on the proposal itself

A `usage_pattern` carries seven optional fields rather than five. The one worth noticing is `antipatterns`, the
author-declared ways to misuse the surface, which nests inside the entry and was the sharpest case in last round's
argument for `matched`. Neither of the two you missed has a teaching order, so your conclusion that `complexity` is
the only orderable fact holds.

The shape of the report is worth recording. One tree built twice gave two orders, and you reported that as a
generator defect and a schema gap in the same document rather than fixing the first and leaving the second for
someone to hit again. Both halves were real, and the second would not have been found from the schema alone, since
nothing in it looks wrong until a producer has to fill the field that is missing.

## What ships

| Change | Where | Version |
|---|---|---|
| `order`, optional, within a complexity level | `usage-patterns-v1.json` | 0.9.0 |
| The published array MUST honor declared orders | Agent Metadata §4.2.1 | 0.9.0 |
| A consumer MUST NOT re-sort a published path | Agent Metadata §4.2.1 | 0.9.0 |
| Learning-path order MUST be a function of package content | Agent Metadata §4.2.1 | 0.9.0 |
| Which of the document's arrays are ordered and which are sets | `usage-patterns-v1.json` | 0.9.0 |
| `order` does not change the `patterns` operation's ordering key | `discovery-contract.md` §3.7 | 0.9.0 |
| `order` declared on the sample SDK's five patterns | `examples/sample-sdk/` | 0.9.0 |
| The `Order:` docstring convention | your authoring format | yours |
| Graph payload nesting, still open | your surface | yours |
