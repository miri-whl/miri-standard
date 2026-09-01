# Feedback: MIRI-SURFACE-012's schema clause contradicts six of the standard's own goldens

*Proposal Version: 0.1-draft*
*Status: Draft — submitted for miri-standard discussion*
*Created: 2026-09-01*
*From: the miri-py implementation team*
*Against: `miri-whl/miri-standard` @ `72d17c1` (checks 0.3-draft)*

## Abstract

Implementing Surface conformance in `miri mcp` surfaced a contradiction between one clause of
**MIRI-SURFACE-012** and the executable expectations in **`examples/fixtures/expected/`**. The
clause requires a surface to refuse any document that parses but fails its schema; six of the twelve
adversarial goldens require the surface to **serve** documents that do exactly that. Both cannot
hold, and the conflict is not a matter of interpretation — it is mechanically demonstrable and
reproduced below.

We have implemented the unambiguous half of the check and left the disputed half unenforced, with
the reasoning recorded in code. This document asks the standard to pick a resolution so
implementations do not diverge, and recommends one.

## 1. The contradiction

**MIRI-SURFACE-012** (`level: MUST`, `weight: 7`) declares, among its `fires_when` clauses:

> A document that parses as JSON but fails its schema is reported as absent, repaired, or served as
> though valid, rather than as METADATA_UNREADABLE. Well-formed and valid are different properties:
> a surface that checks only the first hands the consumer a document whose shape it has not
> established.

Read plainly: a schema-invalid document MUST be answered `ok: false` / `METADATA_UNREADABLE`.

The goldens require the opposite for the adversarial fixtures. Each carries a
`surface_expectation` block stating what a conformant surface MUST return; six of them expect
`ok: true, present: true` for a document that fails its published schema:

| Golden | Document served | Schema violations |
|---|---|---|
| `A1-forged-error` | `adversarial/lifecycle.json` | `additionalProperties`, `minItems`, `pattern` |
| `A2-forged-absence` | `adversarial/lifecycle.json` | same |
| `A6-false-clean-bill` | `adversarial/lifecycle.json` | same |
| `A7-ssrf-and-traversal` | `adversarial/lifecycle.json` | same |
| `A4-index-padding` | `adversarial/sdk-manifest.json` | `required`, `type` |
| `A11-escaping-file-pointer` | `adversarial/sdk-manifest.json` | `required`, `type` |

Reproduction (against the vendored fixture pack at the same commit):

```python
import json, jsonschema
schema = json.load(open("schemas/lifecycle-v1.json"))
document = json.load(open("examples/fixtures/metadata/adversarial/lifecycle.json"))
sorted({e.validator for e in jsonschema.Draft7Validator(schema).iter_errors(document)})
# ['additionalProperties', 'minItems', 'pattern']

json.load(open("examples/fixtures/expected/A2-forged-absence.json"))["surface_expectation"]["envelope"]
# {'ok': True, 'present': True}
```

A surface cannot satisfy MIRI-SURFACE-012 and A2 simultaneously.

## 2. Why a narrow reading does not rescue the clause

We looked for a reading that keeps both. None survives:

- **"Only `additionalProperties` violations are tolerated."** Fails: `adversarial/lifecycle.json`
  also violates `minItems` and `pattern`, and `adversarial/sdk-manifest.json` violates `required`
  and `type` — structural violations by any definition.
- **"The clause targets only the `malformed` variant."** That variant is genuinely split across both
  clauses: its `lifecycle.json` is *unparsable*, while its `sdk-manifest.json` (`type`) and
  `usage-patterns.json` (`required`) parse and fail their schemas. So the schema clause does have a
  fixture — but the same property is present in `adversarial`, where the goldens demand the
  opposite outcome. The fixtures do not separate the two behaviors; only the author's intent does.
- **"Validate only when the document declares `$schema`."** Fails: `adversarial/lifecycle.json`
  declares `$schema` and is invalid.

## 3. The consequence that decided our implementation

Enforcing the clause makes the **Consumer profile untestable**.

Every adversarial attack reaches a consumer *through* a surface — that is the architecture the
Discovery Contract sets out, and the consumer goldens' `consumer_assertion` blocks presuppose the
document arrives. A surface that refuses `adversarial/lifecycle.json` neutralizes A1, A2, A6, and
A7 before a consumer ever sees them. MIRI-CONSUMER-003 ("Branches on `ok`/`present`, never on
`reason` text") can then never fail on the forged-absence case, because the consumer is handed an
error envelope rather than the served document whose forged `present: false` is the whole test. A
check whose fixture can no longer reach it is not a check.

There is also a plain-reading tension with **§3.2**, which specifies `document` as serving the named
document **"verbatim"**. Verbatim relay and validity-gating are different postures; the contract
currently states one and MIRI-SURFACE-012 the other.

## 4. What we implemented, and why

`miri mcp` enforces the **parse clause** and not the schema clause:

- A document that does not parse → `ok: false`, `METADATA_UNREADABLE`. This matches the check's own
  `examples.violation` (a file "truncated mid-object"), its `examples.compliant` (which names
  `greet_malformed`), and its `rationale`, all of which are about parse failure.
- A document that parses is served verbatim, whatever its schema says.

We kept the schema-validation code, tested, behind an unused helper, so the behavior can be
switched on the day the standard resolves this. The reasoning is recorded at
`src/miri_py/mcp/provider.py::MetadataProvider._schema_violations` rather than left implicit, and a
test records the shipped behavior explicitly.

Result: 18/18 Surface checks pinned, all twelve goldens' surface expectations satisfied.

## 5. Requested resolution

We recommend **(a)**, but any of these removes the divergence:

**(a) Drop the schema clause from MIRI-SURFACE-012.** Keep the check about readability —
parse failure — which is what its examples and rationale describe. Validity of publisher documents
is already the producer profile's job (MIRI-PY-007/008/018 and friends validate exactly these
documents at build time), and a consumer's own obligation to confine what it dereferences is
MIRI-CONSUMER-021 ("Confines a publisher-authored path before dereferencing it") — A11 tests exactly
that, and needs the invalid manifest delivered to do so. A surface sits between the two and relays.

**(b) Keep the clause and make the adversarial fixtures schema-valid.** The forged fields
(`ok`, `present`, `error`) could live under a nested key the schemas permit, preserving every attack
while making the documents valid. This costs a fixture rebuild and leaves the surface gating on
validity — which we would then implement as specified.

**(c) Scope the clause explicitly.** If the intent is "validate only where the standard publishes a
schema *and* the violation is structural", say so normatively and adjust the adversarial fixtures so
they violate nothing structural. We would not recommend this: "structural" needs a definition the
schema vocabulary does not supply.

Whichever is chosen, we suggest the check's `fires_when` and the golden set be cross-checked
mechanically, since this class of conflict — a prose clause disagreeing with an executable
expectation — is invisible to both doc-linting and schema validation. This is the third such
self-contradiction the reference implementation has surfaced (after MIRI-CLI-018's
`identity.schema_version` and MIRI-CLI-040's forbidden-field-that-a-MUST-requires); each was found
only by building against the text.

## 6. Unrelated observation from the same pass

`MIRI-SURFACE-033` and `expected/cursor.json` are exemplary in a way worth repeating elsewhere: the
`stateless_surface` case states plainly that a surface keeping no cursor state is **conformant**,
provided it emits no `next_cursor` and rejects every cursor as `INVALID_CURSOR`. That let us
implement the check honestly in a few lines instead of faking pagination. Checks that name their
degenerate-but-conformant case are markedly easier to satisfy correctly.
