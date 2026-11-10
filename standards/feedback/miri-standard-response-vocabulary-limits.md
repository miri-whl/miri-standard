# Response: the fields stand, and your schema finding was one of three

*Responding to: `miri-py-consumer-surface-vocabulary-limits.md` and the reply carrying the payloads*
*Status: Asks 1 and 3 standardized as shipped. Ask 2 accepted, landing in 0.9.0. One divergence back.*
*Created: 2026*

## Disposition

**Keep both fields.** `resolution.may_be_inherited` and `resolution.definitions` are in
`discovery-envelope-v1.json` at 0.9.0, which is also the first time that payload has had a schema at all.

**The line you drew was right**, and it is now a property of the schema rather than an argument about one. §3.6
shows `resolution` by example rather than as a closed list, `resolution` is a payload key so it sits below the
reserved top level, and `additionalProperties` stays open on it for the reason §4.1 gives for the envelope root:
closing it would schedule the failure mode where a schema forbids a field a MUST requires. An unknown field
validates. An invented `evidence` value does not. Declining to add one was correct.

**Ask 2 is accepted and ships in the same release**, as `matched`. It was drafted for a later one, on the reasoning
that a new reserved key is an addition and the payload work was a patch; folding both into 0.9.0 is simpler and the
policy only forbids a patch carrying an addition, never a minor carrying fixes.

`MIRI-SURFACE-003` needs no change, which we expected it would. It fires on a top-level key outside the reserved set
in §4.1, written by reference rather than by enumeration, so adding the row updates what it enforces.

## `definitions` carries your corrected rule

Required when `found` is true, including when it is 1, because an omitted count cannot be told apart from a surface
that does not count and the two warrant different trust. Forbidden when `found` is false.

The second half is yours and is better reasoned than the rule we would have written. Reporting `0` for a name that
was not found would be a claim about the package, and §3.6.1 says `found: false` is weak: it means *not defined
statically*, never *does not exist*. A count of zero would have smuggled an absence claim into the one operation
that never makes one.

## Your schema finding was one of three, and it had a consequence

`resolution` had no schema. Neither did `patterns` or `graph`. §4.1 names six payload keys and the schema defined
three.

The consequence you did not follow it to:

```text
§4.2  an absent response carries a reason and NO payload key

      absent + document     rejected
      absent + entries      rejected
      absent + packages     rejected
      absent + resolution   ACCEPTED
      absent + patterns     ACCEPTED
      absent + graph        ACCEPTED
```

A surface could return `present: false` carrying a fully-formed `resolution` and the schema called it valid. §4.2 is
where the envelope's un-forgeability argument lives, so the rule was unenforced in the half of the payload space
nobody had written down. All six are covered at 0.9.0, and all six payloads are now defined.

## On the payloads you sent, one correction each way

**`patterns`: your caution was right and we took it.** The entries are publisher bytes projected from
`usage-patterns.json`, so a schema written from your output would specify what your fixtures declare rather than
what the producer schema permits. The envelope now fixes the keys around the payload, mirrors only the required
keys as a shape check, and leaves `usage-patterns-v1.json#/definitions/usage_pattern` owning the entry. Writing a
second definition of a document we already specify is how `AGENT_EXAMPLES.json` ended up with three shapes.

**`graph`: one divergence is yours and one is ours.**

Yours is the nesting. You emit `nodes` and `edges` at the envelope's top level; §3.8 nests them under `graph`, and
§4.1's reserved table is exhaustive and names neither. Two unreserved keys in the surface-owned namespace is what
`MIRI-SURFACE-003` exists to catch, so the schema specifies the nested form and your surface needs the change.

Ours is the edge key. §3.8's example spelled it `kind`. `api-graph-v1.json` has always spelled it `relationship`,
with a six-value vocabulary, and that schema governs. You match the schema; our prose was the outlier. The example
is corrected at 0.9.0, and the envelope uses `relationship`.

We note which way each one went because the first would have been easy to report as two of your defects.

## The blended aggregate: agreed, no third number

Your measurement closes the question, and closes a row that has been open since the count-normalization exchange
marked it *awaiting your production view*.

```text
two wheels, byte-identical Python, differing only in whether data files
sit inside the import package or go through the PEP 427 .data scheme

the second raises FileNotFoundError on first call

both scored 28% of 48
after scoping two checks to shipped import-package roots: 74% and 25%,
with nine checks separating the pair where one did before
```

A summary number exists so two artifacts can be compared before anything else is read. One that cannot separate a
working wheel from a broken one has failed at the only job it has, and any blend including conformance reopens that
by construction. Add the moving denominator, `19% of 58.0` under `--execute` against `18% of 55.0` under
`--network`, and a third number would hide the denominator that makes the first two comparable.

The fallback stands as you state it: a vendor metric MAY exist where it is named, versioned, its formula published,
and structurally separate from the two standard scores, never inside `scores` in `lint-report-v1`.

## On the correction you sent against yourselves

Recorded, because the shape of it matters more than the instance. You were drafting a reply saying your own blend
was clearly labeled, found it was reachable through `miri analyze-code` and folded into an `average_score` with no
vendor label at all, and sent the correction instead of the claim.

That is the second time in this exchange that checking a sentence before sending it caught something a round
earlier than review would have. The first was ours: `MIRI-PY-043`'s fix shipped stating the opposite for the common
case, and you read it.

## What we decided differently from your proposal

Three, each said here rather than left for you to notice in the schema.

**One count, not two.** You proposed `matched` and `indexed`. Both consequences your consumer reported are answered
by the first: a view's completeness is `matched` against `cap`, and an empty filtered view is `matched: 0` beside
`present: true`, which already says the document exists. `indexed` describes filter selectivity, and nothing across
four rounds asked for it. We would rather decline an addition than ship one on a hypothesis.

**At the top level, not inside the payload.** You wrote root-level fields and backed them out because §4.1 reserves
that namespace. It reserves it against a *surface*, not against this document, so the row is ours to add. Nesting
also has a flaw worth naming: `api-index`'s payload is keyed by symbol name, so a count inside it collides with a
package that defines a symbol called `matched`.

**The consistency rule is linter-enforced and says so.** `matched` exceeds `cap` exactly when `truncated` is true.
Draft-07 cannot compare two properties of one object, so the schema cannot express it, and the field description
states that rather than letting a consumer validating against the schema alone infer a guarantee it does not get.

## What ships

| Change | Where | Version |
|---|---|---|
| `resolution`, `graph` and `patterns` payloads defined | `discovery-envelope-v1.json` | 0.9.0 |
| §4.2's no-payload rule extended to all six keys | `discovery-envelope-v1.json` | 0.9.0 |
| `may_be_inherited` and `definitions` standardized | `discovery-envelope-v1.json` | 0.9.0 |
| `kind` corrected to `relationship` in §3.8's example | `discovery-contract.md` | 0.9.0 |
| `matched`, reserved once for every capped operation | `discovery-contract.md` §4.1 and §3.5.1 | 0.9.0 |
| `kind` corrected to `relationship` in §3.5.1's ordering table too | `discovery-contract.md` | 0.9.0 |
| Graph payload nesting | your surface | yours |
