# Response: the key space was already dotted, and the schema never implemented it

*Responding to: `api_index` keys by bare name lose symbols (miri-py, 2026-11-01)*
*Status: All three asks accepted. Ask 1 resolved differently from the shape proposed.*
*Created: 2026*

## Disposition

The report is accurate on every claim we could check. The validation table reproduces exactly, the schema quote is
character for character, and the commit cited is `main` at the time of writing.

**Ask 1 is accepted, but not as flat qualified keys.** The dotted key space being asked for is already the standard's
position, written into the Discovery Contract, and the schema never implemented it. The fix is to make the schema say
what the contract already says, and to nest module members instead of flattening them into the key.

**Ask 2 is accepted** and is wider than reported: the hole runs through seven `patternProperties` blocks across
two schemas.

**Ask 3 is answered no.** `api_index` was never "every public top-level definition", and a producer may declare a
narrower surface. Three passages imply it. None states it. That omission is ours.

There is also a finding the report does not contain, and it is worse than the one it does.

## Ask 1: the answer was already written, in a document the schema does not follow

Discovery Contract §3.6 defines the input to `resolve`:

```text
Input: { "package": "<import-name>", "symbol": "<dotted-name>" }

`symbol` is a dotted qualified name in the same key space `api_index` uses
(e.g. `Greeter`, `Greeter.greet`), which is also the space a code index's symbol names project onto.
```

§3.5 repeats it for the graph: node keys "share the dotted key space used by `api_index` and `resolve` (§3.6)".

So the contract states that the `api_index` key space is dotted, and gives a qualified method as its example.
`sdk-manifest-v1.json` states that a key is a bare Python identifier. Both cannot hold, and the schema is the one that
is wrong.

The reason this went unnoticed is the hole in ask 2. A dotted key matches no pattern, so it is validated against
nothing, so it neither works nor fails. Our own adversarial fixture ships one:

```text
examples/fixtures/metadata/adversarial/sdk-manifest.json  ships api_index key "Greeter.greet"

  that entry declares      "type": "method"
  api_component allows     class | function | module | constant

  entry under key "Greeter.greet"   VALIDATES    (the key matches no pattern, so nothing is checked)
  same entry under "Greeter_greet"  rejected     ('method' is not one of ['class','function','module','constant'])

  validation errors reported in that fixture under api_index/Greeter.greet:   none
```

That fixture is adversarial by design, so we checked whether this is one of the things it is adversarial about. It is
not: its recorded `api_index` errors are `_attack_note_padding`, `_attack_note_phantom` and `_attack_note_traversal`.
`Greeter.greet` is not a planted defect. It is the contract's own example, carrying a `type` the enum forbids, passing
because its key exempts it from the enum.

## What the shape becomes

Flat `module.path:name` is declined for the reason the proposal anticipates. Every consumer resolving a bare name
today would have to change, and `resolve` would need an answer to "which one". Nesting costs neither.

`api_component` already nests, and `module` is already a value in its `type` enum. `MIRI-PY-031` resolves
`Client.legacy_fetch` by walking key `Client` into `key_methods`. A module gets the same treatment:

```json
{
  "api_index": {
    "api.tenants.list_tenants": {
      "type": "module",
      "purpose": "Tenant listing endpoint",
      "members": {
        "sync": { "type": "function", "purpose": "List tenants" },
        "sync_detailed": { "type": "function", "purpose": "List tenants, with the raw response" }
      }
    },
    "WeatherClient": {
      "type": "class",
      "purpose": "Client for the forecast API",
      "key_methods": { "fetch": { "purpose": "Fetch one forecast" } }
    }
  }
}
```

Three schema changes follow:

- the `api_index` key pattern admits the dotted space the contract already describes;
- `api_component` gains `members`, keyed by identifier, for entries of `type: module`;
- `additionalProperties: false` on both, so a key outside the space is refused rather than exempted.

Existing manifests stay valid, because a bare key is still a key. A consumer resolving `WeatherClient` is unaffected.
A consumer that wants `sync` has to walk module entries, which is new work, and it is work `MIRI-CONSUMER-010`
(MUST, weight 8) already requires: that check fires when a consumer emits a call to a symbol present in `api_index`
but absent from the source. Index membership has never settled existence. `resolve` settles it.

## Ask 2: seven blocks, not one

Accepted without qualification, and independent of ask 1 as the report says. It is wider than `api_index`:

```text
patternProperties blocks carrying no additionalProperties

sdk-manifest-v1.json    properties.api_index
sdk-manifest-v1.json    properties.error_handling
sdk-manifest-v1.json    properties.configuration.properties.environment_variables
sdk-manifest-v1.json    definitions.api_component.properties.key_methods
sdk-manifest-v1.json    definitions.parameters
usage-patterns-v1.json  properties.categories
usage-patterns-v1.json  properties.learning_paths
```

An eighth block, `configuration.config_files`, uses the pattern `.*`, which matches every key, so nothing escapes it.
Measured against the shipped sample manifest:

```text
api_index["mod:sync"] = 42                       ACCEPTED
error_handling["some.dotted.key"] = "garbage"    ACCEPTED
key_methods["NotLowerCase"] = 99                 ACCEPTED
environment_variables["lower_case_key"] = null   ACCEPTED

api_index["sync"] = 42                           rejected     (control: the key matches, so it is validated)
```

"It would silently stop being validated, which is worse than being refused" is correct, and it generalizes past the
field it was found in.

This is a downstream-affecting change. A vendored copy of these schemas will begin refusing keys it previously
accepted, so the mirrors need regenerating with the 0.8.0 pin rather than drifting.

## Ask 3: the population was never every public definition

No, and a producer may declare a narrower surface. Three passages already imply it:

- Agent Metadata §5.4 mandates an exclusion: console-script entry points MUST be excluded from `api_index`, because
  the CLI surface is described by the CLI standard's `--describe`. An index with a mandatory exclusion is not an
  inventory of every public definition.
- The same passage calls `api_index` "a name→file→signature map that a consumer can resolve against the installed
  package by import".
- `consumption-map.md` calls it a phone book, and records that "a name-keyed index cannot see" a signature-only
  change, which is the reason `code_index` exists.

So option 3 needs no permission from us. Build it. We will state the rule normatively in 0.8.0 so the behavior rests
on a sentence rather than on an inference from three.

The scoping rule carries one condition: a declared surface must record that it is one. A scoped index that does
not say it is scoped cannot be told apart from a complete one, and a consumer reading it cannot tell whether an
absent symbol is absent from the package or absent from the scope.

## The finding the report does not contain

`MIRI-PY-043` measures its delta from the index:

```text
fires_when:  an `api_index` key present in one release and absent from the other is named in
             no `releases[0]` entry's `symbols`
```

The population it polices is the set of index keys. The 1,760 missing definitions are therefore outside it. Those
symbols can be added, changed or removed between any two releases and `043` cannot fire, because they were never on
either side of the comparison.

That is a vacuous pass, inside the check family built to catch silent removal. "Nothing reports the loss" understates
it: the loss also shrinks the population of the MUST whose job is to report change.

`MIRI-PY-036` does not cover it either. Its clause fires when an index entry fails to resolve against the installed
package. It has no clause for the reverse direction, so an index missing half its package passes `036` cleanly.

Repairing the key space does not settle this by itself, because a scoped index, which we have just blessed,
legitimately narrows the population. `043` needs its delta measured against a stated population, and the artifact
needs to state one. That pairing is open, and it is why the scoping rule above carries its condition.

## Two corrections

**`Client.legacy_fetch` is not a flat key.** The report cites it as a convention `MIRI-PY-043`'s example already uses.
It belongs to `MIRI-PY-031`, and it resolves structurally: key `Client`, then `key_methods`, then `legacy_fetch`. The
distinction is what makes nesting available as an answer, so it is worth having exactly.

**The blast radius is thirteen active checks, not six.** The six listed are right, and all are active MUSTs. Eight
further definitions read `api_index`: `MIRI-PY-014`, `015`, `017`, `037` and `045`, the withdrawn `010`, and two
consumer checks. `MIRI-CONSUMER-010` is the one to read first, because it decides half of ask 3 on its own.
`MIRI-CONSUMER-021` bears on ask 1: it requires a consumer to confine a publisher-authored path before dereferencing
it, and a dotted key resembles a module path. Widening the key pattern MUST NOT widen what a consumer will treat as a
path to open.

## On the `rglob` fix

Agreed, and it is yours to make. Sorting the walk makes the surviving entry deterministic without reducing the loss,
which is how the report describes it. One addition: until the index can express a collision, a deterministic survivor
is still a wrong answer arrived at reproducibly, so the count of dropped definitions is worth emitting now, before the
standard offers somewhere to record them.

## What ships

| Change | Where | Version |
|---|---|---|
| `additionalProperties: false` on seven blocks | `sdk-manifest-v1.json`, `usage-patterns-v1.json` | 0.8.0 |
| `api_index` key pattern admits the dotted space | `sdk-manifest-v1.json` | 0.8.0 |
| `members` on `api_component`, for `type: module` | `sdk-manifest-v1.json` | 0.8.0 |
| `api_index` stated as a routing map; scoping permitted, and declared when used | Agent Metadata §5.4 | 0.8.0 |
| The `Greeter.greet` fixture entry, whose `type` is outside the enum | `examples/fixtures/` | 0.8.0 |
| `MIRI-PY-043` delta population, and a reverse-direction clause for `036` | the check definitions | open |

The last row is open because the answer depends on what a declared surface looks like, and that is being specified in
the same release. We would rather leave it open here than close it with a rule the scoping change contradicts a
version later.
