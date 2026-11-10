# Three vocabulary limits a consumer hit, and what we could not route around

**From:** miri-py (reference implementation), 2026-11-08
**Against:** Discovery Contract §3.5.1, §3.6.1, §4.1
**Evidence:** four field rounds by a consumer team running 0.8.6 through 0.10.0
against a production OpenAPI SDK of roughly 1,300 api_index entries. Their symbol names and the
size of their package are generalized here at their request; the shapes are theirs.

All three asks have the same shape. A closed vocabulary cannot express a distinction the
consumer needs, the surface has no reserved key to put it in, and the only honest
answer collapses two different facts into one value. We have shipped around neither,
because routing around a vocabulary limit is how two surfaces stop agreeing.

## Ask 1: `resolve` cannot say "defined outside this package"

§3.6.1 closes `ResolutionEvidence` to `static-source`, `not-in-source` and
`module-unreadable`. A consumer asked us about three symbols and got `not-in-source`
for all three:

| asked | what is true |
|---|---|
| `NoSuchThing` | the name does not exist |
| `Cell.model_dump` | inherited from `pydantic.BaseModel`, outside the package |
| `models.terrain.Cell` | exists, and the form was not supported |

The third was our defect and is fixed: module-qualified forms resolve as of 0.10.0.
The first two remain indistinguishable, and they are different facts. An agent that
reads `not-in-source` for `model_dump` and concludes the method is unavailable is
wrong in a way the vocabulary invited.

This is the same asymmetry §3.6.1 already protects. The section exists so that
`not-in-source` is never read as proof of absence. A symbol defined in a dependency
is a case where the surface knows more than that: it knows the name was not found
**in this package's source**, and it can see the class declares a base it did not
parse. Reporting that as the generic value discards information the scan already has.

**Proposed:** one added value, `defined-elsewhere`, for a member reached through a
base class the package does not define. Added, never repurposed, so a consumer that
does not know it falls back to treating the response as unprocessable exactly as
§3.6.1 already requires.

A narrower alternative, if growing the closed set is unwelcome: a surface-owned
boolean beside `evidence` rather than inside it. We would rather have the value, but
either settles the distinction.

## Ask 2: `api-index` cannot say how much it cut

§3.5.1 gives `truncated` and `cap`. On an index of roughly 1,300 entries, a query
matching a couple of dozen and a query matching everything both come
back `truncated: true, cap: 25`. The
consumer's words: it cannot distinguish a couple of dozen matches from the whole index.

Two consequences they reported:

1. An agent cannot tell a nearly-complete view from a sample of a few per cent. It cannot decide
   whether to narrow the query or to stop reading.
2. An empty filtered view reads as absence, though this operation never proves
   absence. `MIRI-CONSUMER-012` tells consumers not to treat a truncated index as
   complete, and the envelope gives them nothing to act on beyond the flag.

§4.1 reserves the envelope's top-level keys, and `reason` is "free text for humans;
consumers MUST NOT branch on it". So there is no slot a surface may add and no slot
an agent may act on. We considered `matched` and `indexed` top-level fields, wrote
them, and backed them out for exactly that reason.

**Proposed:** two optional integers inside the existing payload rather than at the
root: `matched` (entries the filter selected) and `indexed` (entries the document
holds). Both describe the surface's own view rather than publisher bytes. That is the line
§4.1.1 already draws.

This also answers the cursor question the same team raised: `{cursor: "25"}` returns
`INVALID_CURSOR` because the surface is stateless by §3.5.1. With `matched` present, a
consumer can size what it is missing without paging. That is most of what they
wanted paging for.

## What we shipped, and why it is not enough

Two of these are implemented in miri-py 0.10.1, as FIELDS. We are not
asking the committee to imagine them.

`resolution.may_be_inherited` is true when a member was not found, its
owner is defined in the package, and the owner's ancestry reaches a
base the surface never parsed. That separates the second row of the
table above from the first.

`resolution.definitions` is how many definitions of the name the scan
found, present on every resolved symbol.

Neither touches `evidence`, and that distinction is the whole of our
reasoning. §3.6.1 closes that vocabulary. A consumer meeting an
unknown value there must treat the response as unprocessable, so a new
value breaks every peer that has not shipped it. An unknown FIELD is
ignorable by construction. We think that makes a field safe to add
ahead of the committee and an evidence value not, and we would rather
be told we drew that line wrong than draw it silently.

For the third we have no field, only honesty: `truncated` is true when
either of two caps applied, and the reported `cap` is the tighter of
them, because naming the looser describes a bound that did not bite.
That makes the flag honest about WHETHER something was cut. It still
cannot say how much. §4.1 reserves the top level, so there is nowhere
for us to put it.

## Ask 3: `resolve` cannot say "there is more than one of these"

Reported in the same team's third round. Their SDK defines seventeen public
class names in more than one module. `ErrorResponse` is an attrs model
in `models/` and a Pydantic model in `utils/`, and a bare `resolve` of
that name answers for one of them without saying the other exists.

The scan knows. It parsed both, it chose between them using the index's
file pointer where there was one, and the envelope has no field in
which to report that a choice was made. Their words: "an answer that
silently picks one reads as complete."

This is the same failure as the other two. A consumer that knows a name
is ambiguous asks a qualified question. §3.6 now accepts one. A
consumer that does not know is told something true about one class and
reads it as true about the name.

**Proposed:** an integer in the resolution called `definitions`,
giving how many definitions of the name the surface found. Always
present on a resolved symbol, and never omitted as a shorthand for
one: an absent count means either "exactly one" or "this surface does
not count definitions", and those warrant different trust. That is the
same rule §4.1 states for `truncated`, and it is this ask's own
argument turned on itself.

We shipped it omitted below two and corrected that before standardizing
it. More than one tells the consumer to ask again with a
module-qualified name.

## What we are asking for

Standardize the two fields, or tell us to withdraw them. A surface
carrying a key its peers lack produces consumers that only work
against one implementation. That is worse for the standard than the
gap was. We shipped them because a field cannot break a reader that
does not know it, and because the alternative was leaving a consumer
unable to tell "absent" from "somewhere I cannot see". If that
reasoning is wrong, the fields come out.

For the third, we have shipped nothing and will not without a place to
put it.

All three are additive, all three come from production use rather than
review, and we have the fixtures if the committee wants the failing
cases reproduced.

## One thing we would like written down

`resolution` has no schema. `discovery-envelope-v1.json` defines
`entries`, `packages`, `document` and `api_index_entry`, and nothing
for the payload §3.6 has described since 0.3. Our two fields therefore
validate against nothing, and so does every field the contract already
specifies there.

That is an argument for standardizing rather than against it, and the
schema is the committee's to write. We will conform to whatever shape
it takes, including dropping both fields.
