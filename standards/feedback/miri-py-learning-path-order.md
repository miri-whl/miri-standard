# Proposal: let a usage pattern declare its place in a learning path

*Proposal Version: 0.1-draft*  
*Status: Draft, submitted for miri-standard discussion*  
*Created: 2026-11-10*  
*From: the miri-py implementation team*  
*Against: `miri-whl/miri-standard` @ `84fd390e` (standard 0.8.0)*  
*Raised by: the Patitur engine team, consuming a 1,259-class OpenAPI SDK (their C15)*

## Abstract

`usage-patterns-v1` makes `learning_path.patterns` an **ordered** list of pattern ids and gives a
producer no way to decide that order from the document's own content. The only orderable fact a
pattern carries is `complexity`. It has three values. Every pattern at one level is therefore
tied, and the tie goes to whatever the producer read first.

A consumer measured the result. On their SDK the order of `os.listdir` decided the beginner
path's first entry. The pattern an author wrote to come first landed fourth. The same tree built
on another machine could order it differently again.

We have fixed the half that is ours. This document asks for the half that is the schema's.

## What the schema says

`learning_path.patterns` is described as an "Ordered list of pattern IDs". The word carries weight:
a consumer reading a beginner path reads it top to bottom, and the first entry is the one an agent
or a person starts from.

A `usage_pattern` carries `id`, `name`, `description`, `complexity`, `category`, `code` and five
optional fields. `complexity` is the only one with an ordering, and `LearnerLevel` has three
values. An SDK with seventy examples therefore has seventy patterns in three buckets, and nothing
in the document says which comes first inside a bucket.

## What a producer is left to do

Guess, and the guess shows. Our generator kept patterns in extraction order, and extraction
followed a directory walk. The consumer's report:

> `_build_learning_paths` keeps patterns in extraction order, and extraction follows the unsorted
> directory walk. On the SDK's tree, the category order and the beginner path match `os.listdir`
> exactly. So `first_typed_call` lands fourth on the API team's Mac, and could land elsewhere on
> CI.

Two problems sit underneath that, and only one of them is ours. One tree built twice gave two
orders. That is a generator defect, and sorting the walk fixes it: the same tree now produces the
same document on any machine. Sorting only makes the order stable, though. It follows the author's
filenames, which is no more meaningful than following the disk. An author who wants "First typed
call: build a client and read a page of devices" to come first still has no way to say so.

That second half is the schema's, and we are asking rather than shipping a field of our own. A
producer that invented one would be publishing vocabulary no consumer reads. Inventing vocabulary
is the thing the standard exists to prevent.

## What we propose

An optional integer on `usage_pattern`:

```json
"order": {
  "type": "integer",
  "minimum": 0,
  "description": "Where this pattern sits among patterns of equal complexity in a learning path. Lower comes first. Absent means the producer orders it."
}
```

We would ask the wording to keep three properties. It stays optional, and an absent value is not
zero: most authors will declare nothing, and a pattern with no declared order must not jump ahead
of one that declared `order: 5`, so patterns without it sort after those with it. It orders within
a complexity level and never across one, so a beginner pattern declaring `order: 9` still comes
before an advanced one declaring `order: 0`. `complexity` already answers the coarse question,
and two fields deciding one order is how they come to disagree. And a tie is the producer's to
break: two patterns declaring the same order are not an error, and a producer should break that tie
the same way on every build.

For an authoring convention, a pattern's own docstring is where `complexity` is already declared,
so `Order:` sits beside `Complexity:` and needs no new mechanism:

```python
"""First typed call: build a client and read a page of devices.

Complexity: beginner
Order: 0
"""
```

## Why not solve it producer-side

We considered three alternatives and each is worse. Sorting by `estimated_time` reads a free-text
optional string, and a short example is not a first one: the pattern that introduces a client is
short because building a client is short. Sorting by `prerequisites` would be principled, since a
topological sort over them has the right shape. But almost no pattern declares any, and on the SDK
in question none did. A sort with no input is the filesystem again. Adding the field under a
vendor prefix would work for us and for nobody else. A consumer reading `x-miri-order` has to know
our generator wrote it, and that is the coupling `agent-metadata` removes.

## What we have shipped meanwhile

The walk is sorted in miri-py 0.10.8, which makes `usage-patterns.json` reproducible from one
tree. The order within a complexity level is the sorted path order. We document that order as
arbitrary, because it is.

One more thing came out of the same report. Our consumer prints a line naming the usage patterns
that mention a symbol, and for a client class every example in the package matched: the line ran
to about seventy titles with the useful one last. It is capped now, and leads with the
beginner-path patterns. A capped line puts the ordering question in front of a reader, where a
full document buried it.

## What we are asking

1. Whether `order` (or another spelling) is wanted on `usage_pattern` at all, or whether the
   standard's position is that `learning_path.patterns` is ordered at the producer's discretion and
   the word "ordered" means only "a list, not a set".
2. If it is wanted, confirmation of the three properties above. Producers and consumers need to
   agree on what an absent value means.

Either answer is usable. We would ask only that it not be left unstated, because an order a
reader depends on and a producer gets no input for is a field every implementation fills
differently.
