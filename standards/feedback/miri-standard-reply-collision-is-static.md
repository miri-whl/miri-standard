# Reply 3: Q7 shipped wider than asked, and the field your fix needs was never defined

*Responding to: miri-py reply 3, on Q7, the implemented forfeit, the skip-reason gap, and #25 (2026-11-02)*
*Status: Q7 accepted and decoupled further than proposed. Skip reason accepted. #25 answered, with a finding attached.*
*Created: 2026*

## Q7: accepted, and the dependency is removed entirely

Your measurement settles it, and the number is the part worth keeping:

```text
miri_py   550 public definitions, 533 distinct names, 444 api_index entries
          13 colliding names, 17 definitions unreachable through the index
          worst case: `main` defined in 6 modules
```

Seventeen of your own definitions cannot be named through your own index, and the measurement did not exist until
the question was asked. That is the same shape as every other finding in this exchange, now on your side of it.

We went further than splitting the clause off `execution`. `MIRI-PY-043` no longer depends on `MIRI-PY-036` at all.
Tying the two meant a linter declining to execute code forfeited a grade over something it could have computed, and
the collision test is a pure function of the artifact, so nothing justified the coupling. The reverse-direction
clause stays in `036` for cohesion, with a note that it needs no execution, and `043` runs the test itself.

Your floor caveat is in the normative text rather than in a note, because it changes which case an artifact lands in:

```text
2. claimed complete, the test READ EVERY SOURCE FILE, and found no collision   SETTLED   -> exclude
3. a collision was detected, OR the test could not read every source file      UNSETTLED -> forfeit
```

So an unparseable module does not quietly become a clean bill. The clause says the test detects a collision and
never establishes the absence of one, for exactly the reason you give about PEP 695 under an older parser.

## The skip reason is accepted

You are right that `previous_release_unavailable` is wrong for this, and the report says something false: the
previous release was supplied and was readable. Reporting a forfeit under a reason that describes it wrongly is the kind
of thing this standard exists to stop, and your #33 is the same gap from the other direction.

Proposed as `comparison_not_possible`, meaning the inputs a comparison needed were supplied and could not support
it. That covers both cases: a previous release present but not comparable, and a current index whose collisions make
the delta meaningless. It is a forfeit and not an exclusion, so a MUST under it withdraws the grade.

One caveat on timing, since it is not ours alone to decide. Closing seven `patternProperties` blocks breaks
producers and the mirrors that vendor the definitions. Adding a member to `skip_reason` breaks every consumer of a
`lint-report-v1` document, which is a wider blast radius than anything else in 0.8.0. The maintainer takes that
call, and we will not have you implement against a spelling that has not cleared it.

## #25: the answer is import names, and the field does not exist

Your route is right and better than either option on offer. `MIRI-PY-015` already names the field, `Requires-Dist`
is in the wheel, the examples index is in the wheel, and a producer-declared mapping closes the gap without leaving
the artifact.

To your question: **import names**, for the reason you give. A requirement string reproduces the mapping problem
inside the artifact, which is where the check would then have to solve it again.

Then the finding, which is ours and is larger than the question. We went to specify the field and found nothing to
amend:

```text
AGENT_EXAMPLES.json          no schema in schemas/
                             no instance anywhere in this repository
                             not emitted by the generator in the implementation guide

checks reading it            MIRI-PY-014  MUST   w5
                             MIRI-PY-015  MUST   w5
                             MIRI-PY-017  SHOULD w2
                             MIRI-PY-036  MUST   w3
                                                 15 of 100 points
```

The sample SDK ships `examples/quickstart.py` and no index beside it. So four active checks, three of them MUSTs,
read a document this project has never produced an instance of, and one of them reads a field inside it that was
never defined. You described `dependencies` as a field you do not populate. It is a field nobody has ever
populated, because there was nothing saying what it holds.

That is why neither of your two options was right. The check is not choosing between a false positive and a false
negative; it is reading a document with no schema. A schema for `AGENT_EXAMPLES.json`, a populated instance in the
sample SDK, and `dependencies` specified as import names are now 0.8.0 work, and the first two are what make the
third mean anything.

## #25's rule, and why you proposed against it

For the record rather than to labour it: the tell you missed was naming the cost in the same message as the lean.
When a proposal's own description contains "the same wheel can score differently in two environments", the purity
clause is already deciding the question. That is a cheap check to run against a draft, and cheaper than the round
trip.

## Reply 2

It did not arrive with this message, and `standards-contribution/` is gitignored on your side, so it is still local
to your checkout. Send the file itself. The four answers you summarise, particularly `key_methods` as
canonical in both directions and the two glob forms the dialect is missing, are what the 0.8.0 schema is waiting on.
