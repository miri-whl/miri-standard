# Miri Standard: Discovery Contract (Consumption)

*Specification Version: 0.3-draft*
*Status: Draft*
*Created: 2026*

## Abstract

The producer standards define the `agent-metadata/` directory an artifact ships. This specification defines how an
agent **obtains** that metadata at the moment it is deciding what to call: a **transport-agnostic metadata-query
contract** of eight read-only operations — retrieval (`document`, with `lifecycle` and `migration-guide`
shorthands), derived views (`api-index`, `patterns`, `graph`), and determination (`list`, `resolve`) — of which an
**MCP context server** is the first binding. The contract adds the wire discipline the producer surfaces already carry:
a **surface-owned response envelope** that versions and frames every answer without reshaping the publisher's bytes, a
structured **absence-versus-error** discriminator that a hostile package cannot forge, and **import-free discovery** so
that a hostile or broken package never executes during lookup.

This document specifies *mechanism*, not benefit. Whether decision-time consumption improves agent outcomes is an
empirical question gated on the pre-registered experiment; no clause here asserts effectiveness.

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Design Principles](#2-design-principles)
3. [The Metadata-Query Contract](#3-the-metadata-query-contract)
4. [The Response Envelope](#4-the-response-envelope)
5. [Import-Free Discovery](#5-import-free-discovery)
6. [The MCP Binding](#6-the-mcp-binding)
7. [Project Declaration](#7-project-declaration)
8. [Discovery Measurement](#8-discovery-measurement)
9. [Security Considerations](#9-security-considerations)
10. [Conformance](#10-conformance)

---

## 1. Problem Statement

The metadata ships inside the wheel, but shipping is not reaching. An agent deciding which method to call, whether a
package is deprecated, or how to migrate a call site needs that metadata **at decision time**, in its context, without
first knowing the file layout or spending turns spelunking the installed tree. Three delivery vehicles exist:

1. **In-wheel** — the agent opens `agent-metadata/*.json` directly. Requires the agent to know the path and to have
   filesystem access to site-packages.
2. **In-process** — the package's `_miri` discovery functions (Wheel Extensions §6) return the metadata to code
   running inside the same interpreter.
3. **Context server** — a process that serves the metadata to the agent over a tool surface, so it arrives as
   structured tool output at decision time without file spelunking.

The context server is the decision-time vehicle, and a reference implementation exists (`miri mcp`). But **a server's
behavior is not a contract**: without a specified wire shape, two implementations diverge and a consumer built against
one breaks against the other. This document defines the contract those implementations must share, and binds it to
MCP as the first transport.

A consumer reading through vehicle 1 or 2 reads the producer documents directly and is governed by the producer
standards. **This contract governs vehicle 3**, and the [Consumption Map](consumption-map.md) labels each of its
read-steps with the vehicle that supplies it, so that no reading order depends on a document no operation can serve.

## 2. Design Principles

- **Declare sources, not verdicts.** A query returns the package's declared metadata; the consumer computes any
  verdict (vulnerable? current? safe to call?) at call time.
- **Metadata is untrusted input.** Every payload is publisher-authored data, never instructions; it inherits the
  threat model in full (§9).
- **The surface owns the envelope; the publisher owns the payload.** Every response is a surface-authored envelope
  with the publisher's bytes nested inside it (§4). The two never share a namespace, so no publisher can forge a
  surface signal.
- **Pointers, not dumps.** Routing answers are context-budgeted: capped, filterable, and pointing into the source
  rather than reproducing it. The saving this yields is a **function of the ratio between a package's source size and
  its metadata size**, and is therefore largest on big packages and small — occasionally negative — on tiny ones. No
  clause of this standard asserts a particular saving; where one is claimed it must be measured on the package in
  question.
- **Import-free discovery.** Locating a package's metadata MUST NOT import or execute the package (§5).
- **One shape across bindings.** The operations and their envelopes are defined independently of transport; MCP is one
  binding, and any future binding carries the same operations and the same envelopes (§6).

## 3. The Metadata-Query Contract

A conformant metadata-query surface exposes these eight read-only operations, and no others (§9). Each is defined by its
input, its payload, and its semantics; every response is wrapped in the §4 envelope.

| Operation | Input | Payload key | Serves |
|---|---|---|---|
| `list` | optional `query` | `packages` | Which installed packages ship agent-metadata, and which documents each has |
| `document` | `package`, `name` | `document` | Any single whitelisted agent-metadata document, verbatim |
| `lifecycle` | `package` | `document` | Shorthand for `document` with `name: "lifecycle.json"` |
| `migration-guide` | `package` | `document` | Shorthand for `document` with `name: "migration-guide.json"` |
| `api-index` | `package`, optional `query` | `entries` | A capped, filtered routing view derived from `sdk-manifest.json` |
| `resolve` | `package`, `symbol` | `resolution` | Whether a symbol exists in the installed package's **source**, and where |
| `patterns` | `package`, optional `category`/`complexity`/`query` | `patterns` | A capped, filtered view of `usage-patterns.json` |
| `graph` | `package`, `symbol`, optional `depth`/`direction` | `graph` | The neighborhood of one symbol in `api-graph.json` |

`lifecycle` and `migration-guide` are **named shorthands**, not distinct capabilities: each MUST return exactly what
`document` would return for the same package and document name. They exist because they are the two highest-traffic
queries and because the reference binding already ships them.

The operations fall into three kinds, and the distinction is what keeps the set from growing arbitrarily:

- **Retrieval** — `document`, and its `lifecycle`/`migration-guide` shorthands. Returns a document **verbatim**. These
  are shorthands, not distinct capabilities: each MUST return exactly what `document` would for the same name.
- **Derived views** — `api-index`, `patterns`, `graph`. Each projects **one large document** into a capped, filtered
  answer to a question a consumer actually asks, rather than making it read the whole file to find the part it needs.
- **Determination** — `list`, `resolve`. Answers the surface computes from the environment, not from any single
  document.

A new operation is justified only when it is a **derived view whose parent document is large enough that verbatim
retrieval defeats the purpose of asking** (§3.2.3), or a determination no document can answer. Anything else belongs
in `document`.

### 3.1 `list`

**Input:** `{ "query": "<optional substring>" }` — an optional case-insensitive filter on the package name.

**Payload:** `packages`, an array of installed packages that ship agent-metadata:

```json
{
  "schema_version": "1", "ok": true, "truncated": false, "cap": 100,
  "packages": [
    { "package": "weather_sdk", "distribution_name": "weather-sdk", "version": "1.2.0",
      "purl": "pkg:pypi/weather-sdk@1.2.0",
      "documents": ["lifecycle.json", "migration-guide.json", "sdk-manifest.json"] }
  ]
}
```

`package` is the top-level import name; `distribution_name` the installed distribution name (spelled in full to avoid
collision with the CLI `identity.distribution` enum, [CLI Spec §3.1](../cli/cli-lifecycle-specification.md)); `version`
its installed version; `purl` its resolved package URL (§9); `documents` the agent-metadata documents present, which
is the **input domain for `document`** (§3.2).

`list` is the entry point for an agent that knows nothing else. Because a large environment can hold hundreds of
metadata-shipping packages, `list` is capped exactly as `api-index` is (§3.5): the surface MUST declare `cap`, MUST set
`truncated: true` when it drops entries, and SHOULD accept `query` to narrow rather than paginate.

Where one distribution provides several metadata-bearing import packages, the surface MUST emit **one row per import
package**, each with its own `purl`. Where an import name is provided by more than one installed distribution, the
surface MUST return an `AMBIGUOUS_PACKAGE` error (§4.3) rather than silently picking one.

### 3.2 `document`

**Input:** `{ "package": "<import-name>", "name": "<document-name>" }`.

**Payload:** `document` — the named agent-metadata document, **verbatim**, nested inside the envelope:

```json
{
  "schema_version": "1", "ok": true, "present": true,
  "package": "weather_sdk", "purl": "pkg:pypi/weather-sdk@1.2.0",
  "name": "usage-patterns.json",
  "document": { "…the package's usage-patterns.json, byte-for-byte…": "…" }
}
```

#### 3.2.1 The Servable Set

`name` MUST be a member of the servable set below.

`list.documents` is the **input domain** for `document` — what a package advertises is what an agent has reason to
ask for — but it is **not a precondition**. A servable `name` that the package does not ship returns an *absent*
response (§4.2), never `DOCUMENT_NOT_SERVABLE`. Requiring membership would classify the contract's flagship absence
case as an error and collapse exactly the distinction §4.2 exists to protect: asking a bare package for its
`lifecycle.json` is a well-formed question with the answer "it ships none".

| Servable | Not servable |
|---|---|
| `lifecycle.json`, `migration-guide.json`, `sdk-manifest.json`, `usage-patterns.json`, `api-graph.json`, `test-patterns.json` | everything else, including `prompt-templates.md` and `README.md` |

The servable set is **closed and exhaustive**: it is not a sample, and a surface MUST NOT extend it. Membership is
governed by one criterion, so that future document types are adjudicated by principle rather than by whether anyone
remembered to list them:

> **Only schema-governed documents are servable.** A document is servable only if this standard defines a JSON Schema
> for it and a linter check gates it. **No free-form natural-language document is ever servable** — not
> `prompt-templates.md`, not `README.md`, not embedded prose docs.

The reason is injection, not tidiness. Free prose is the highest-risk payload a publisher controls, and a document
with no schema and no check has no property a consumer can verify before putting it in a model's context. A
schema-governed document can at least be validated, field-typed, and reasoned about.

Two consequences worth stating, because both were previously specified wrong:

- **`README.md` is not servable, and the inventory is surface-composed.** An agent that knows nothing else does not
  need a publisher-authored index: `list` (§3.1) already reports each package's `documents`, and that answer is
  composed by the surface from the directory listing. A publisher-authored inventory would be a schema-less prose
  file served as step one of the highest-traffic task — a near-exact substitute for the `prompt-templates.md` this
  contract refuses.
- **`AGENT_EXAMPLES.json` is not servable by this operation.** It is a `.dist-info/` file
  (Wheel Extensions §3.1.1, §3.2), so it lies outside the `agent-metadata/` directory this operation is confined to
  (§3.2.2) and can never appear in `list.documents`. It remains reachable through the filesystem vehicle; the served
  path to working code is `usage-patterns.json`. The [Consumption Map](consumption-map.md) labels it accordingly.

#### 3.2.2 Name Grammar and Path Confinement

The `name` argument is a **single path segment**, matching `^[A-Za-z0-9_.-]+$` and containing no `/`, no `\`, and no
`..`. It is a document name, never a path: a surface MUST reject any `name` carrying a directory prefix, an absolute
prefix, or a traversal sequence, and MUST NOT attempt to normalize one into an acceptable form.

Confinement MUST be enforced on the **resolved path**, not on the name string. A surface MUST:

1. resolve `name` against the package's `agent-metadata/` directory;
2. fully resolve the result (following no symbolic links, or resolving and then re-checking — `realpath`);
3. require the resolved path to be a **regular file physically inside** that directory;
4. reject symbolic links outright.

Name-string filtering alone is not sufficient and MUST NOT be relied on: a whitelisted `usage-patterns.json` shipped
as a **symlink to a file outside the package** contains no `..`, carries no absolute prefix, is advertised by `list`,
and would otherwise be served verbatim. Editable and source-tree installs preserve symlinks, so this is a live shape,
not a theoretical one.

Any `name` failing the grammar, the servable set, or the confinement check MUST return `DOCUMENT_NOT_SERVABLE`
(§4.3) — never a filesystem error, never a path in the message, and never the file. A name that passes every check
but that the package does not ship returns an **absent** response (§4.2).

`document` is what makes the [Consumption Map](consumption-map.md)'s reading orders executable over a context server:
every document the Map routes to is either servable here or explicitly labelled as another vehicle's.

#### 3.2.3 Size Bound

`document` returns a whole document, so it is the operation most able to blow a context budget — `sdk-manifest.json`,
`usage-patterns.json` and `api-graph.json` are all on the servable set, and on a large package each can run to
hundreds of kilobytes. A capped router (§3.5) beside an uncapped bulk fetch is not "pointers, not dumps"; it is a
pointer with an unbounded escape hatch beside it.

The default `max_bytes` is **262144** (256 KiB), measured on the document's serialized bytes as read from disk. A
surface MAY declare a different value and MUST report the value in force as `max_bytes` on every `document` response
(§4.1). Pinning a number matters for the same reason §3.5.1 pins the caps: an unstated bound means two conformant
surfaces disagree about the same document, and a check written against one is vacuous on the other.

Where a document exceeds the bound the surface MUST set `truncated: true` and **MUST omit the `document` key
entirely**. It MUST NOT return a partial object, a truncated string, or a repaired fragment: a payload key that
sometimes holds a document and sometimes holds a prefix of one is a shape no consumer can parse safely, and repairing
publisher bytes invents content the publisher did not write. A truncated response is therefore a response *about* a
document rather than one containing it — `reason` SHOULD state the document's actual size so a consumer can say
something useful.

**A truncated response MUST NOT be presented, by surface or consumer, as the complete document.**

Truncation is a backstop, not the intended path. Where a consumer needs part of a large document, the derived views
are the right tool: `api-index` (§3.5) for routing, `patterns` (§3.7) for usage, `graph` (§3.8) for relationships —
each capped and filterable, and each existing precisely so that `document` is rarely the right call on a large
package. The honest scaling statement in §2 applies.

### 3.3 `lifecycle`

**Input:** `{ "package": "<import-name>" }`. Equivalent to `document` with `name: "lifecycle.json"`.

**Payload:** `document` — the package's `lifecycle.json` (identity, support status, advisory sources, update check) as
specified in [Lifecycle and Security Metadata](../python/lifecycle-security-metadata.md), or an **absent** response
(§4.2). This answers "is this package alive, and whom do I ask about it?" — facts an agent cannot derive from source.

### 3.4 `migration-guide`

**Input:** `{ "package": "<import-name>" }`. Equivalent to `document` with `name: "migration-guide.json"`.

**Payload:** `document` — the package's `migration-guide.json` (breaking changes, structured deprecations with
replacements, version deltas) as specified in
[Agent Metadata §4.3](../python/miri-agent-metadata-specification.md), or an absent response (§4.2). It answers "what
changed, and what replaces what?" for a mechanical cross-reference against the consumer's own call sites.

### 3.5 `api-index`

**Input:** `{ "package": "<import-name>", "query": "<optional substring>" }`.

**Payload:** `entries` — a routing view **derived** from the package's `sdk-manifest.json` `api_index` (not the raw
document; use `document` for that), filtered by the optional case-insensitive `query`, capped, and marked when
truncated:

```json
{
  "schema_version": "1", "ok": true, "present": true,
  "package": "weather_sdk", "purl": "pkg:pypi/weather-sdk@1.2.0",
  "truncated": false, "cap": 25,
  "entries": {
    "WeatherClient": { "type": "class", "purpose": "Main API entry point",
                       "signature": "WeatherClient(api_key: str, timeout: float = 10.0)",
                       "file": "client.py" }
  }
}
```

Each entry carries `type` and `purpose` (both required), and `signature` and `file` where the producer's `api_index`
supplies them — both are **optional**, because the producer's canonical `api_index`
([Agent Metadata §4.1](../python/miri-agent-metadata-specification.md)) does not guarantee either. A consumer MUST NOT
assume a `file` pointer or a `signature` is present.

**`api-index` confirms presence; it can never prove absence.** A conformant surface MUST declare its `cap`, MUST set
`truncated: true` when it drops entries, and MUST NOT return more than `cap` entries — so a symbol may be missing from
a response merely because it was capped out or filtered out by `query`. It follows that:

- A consumer MUST NOT treat a truncated or filtered `api-index` response as the package's complete surface.
- A consumer MUST NOT conclude from a symbol's absence here that the symbol does not exist. Existence is settled by
  introspecting the **installed package** (the MIRI-PY-036 discipline applied consumer-side), never by index
  membership — see [Consumption Map §3.2](consumption-map.md).

The entries are pointers into the installed source; a consumer MUST verify a claimed surface against the installed
package before relying on it, never treating the index as ground truth.

#### 3.5.1 Cap, Ordering, and Continuation

A cap whose value, ordering and continuation are unspecified is not a contract: two conformant surfaces disagree, and
a conformance check written against one is vacuous on the other. The following are therefore normative.

- **Value.** The default `cap` is **25**. A surface MAY accept a caller-supplied `limit` up to a declared maximum, and
  MUST NOT return more than the effective cap. The value in force MUST be reported as `cap` on every response.
- **Ordering.** Entries are ordered **lexicographically by entry name**, and the ordering MUST be stable across
  identical requests. Without this, "the first 25" is a different 25 per surface and per call, and truncation is
  unreproducible.
- **Matching.** `query` matches, case-insensitively, against the **entry name only** — not `purpose`, not `file`. A
  surface MUST NOT widen the match, because a consumer cannot distinguish "absent" from "matched on a field I did not
  intend" (and §3.5's presence-only rule already forbids reading absence as non-existence).
- **Continuation.** Where a surface drops entries it MUST return a `next_cursor` string alongside `truncated: true`,
  and MUST accept that value as an optional `cursor` input to continue the same ordering. A surface that cannot
  continue MUST still set `truncated: true` — silently returning a partial answer as though complete is the failure
  this whole section exists to prevent.

A consumer MUST NOT infer the size of a package's surface from `cap`, from the number of entries returned, or from
`truncated` being `false` after a `query` — a filtered response is complete only *with respect to that filter*.

### 3.6 `resolve`

**Input:** `{ "package": "<import-name>", "symbol": "<dotted-name>" }` — `symbol` is a dotted qualified name in the
same key space `api_index` and `api-graph.json` nodes use (e.g. `Greeter`, `Greeter.greet`).

**Payload:** `resolution` — whether the symbol exists in the installed package, **determined from its source**:

```json
{
  "schema_version": "1", "ok": true, "present": true,
  "package": "greet_miri", "purl": "pkg:pypi/greet-miri@1.0.0",
  "symbol": "Greeter.greet",
  "resolution": {
    "found": true, "evidence": "static-source", "kind": "method",
    "file": "core.py", "line": 10,
    "signature": "greet(name: str) -> str"
  }
}
```

`resolve` exists because every other operation reports what the **publisher declared**, and none of them can settle
what the package **actually contains**. Without it the anti-hallucination rule in
[Consumption Map §3.2](consumption-map.md) cannot be discharged at all: a consumer is told not to call a symbol
that does not exist, while the only surface available to it — `api-index` — is a capped, publisher-authored view that
§3.5 forbids
reading as proof of anything.

#### 3.6.1 Static Evidence, and Its Limits

`resolve` MUST determine existence by **parsing the installed package's source** — reading and analyzing the module
that would define the symbol — and MUST NOT import or execute it (§5). Static parsing is what makes this operation
compatible with import-free discovery: an unvetted package is read, never run.

The evidence is therefore **asymmetric, and the response MUST NOT obscure this**:

- **`found: true` is strong.** The symbol is defined in the installed source at the reported location. A consumer may
  rely on it.
- **`found: false` is weak.** It means *"not defined statically in the source"* — **not** *"does not exist."* A
  surface constructed at runtime (`__getattr__`, `setattr`, a metaclass, a re-export resolved on import) is invisible
  to static analysis by construction.

A surface MUST report the distinction rather than collapsing it, using `evidence`:

| `found` | `evidence` | Means |
|---|---|---|
| `true` | `static-source` | Defined in source at `file`/`line` |
| `false` | `not-in-source` | No static definition found; the symbol may still exist dynamically |
| `false` | `module-unreadable` | The module could not be read or parsed — nothing is known either way |

A consumer MUST NOT report a `not-in-source` result as proof the symbol does not exist, and MUST NOT report a
`module-unreadable` result as either existence or absence. The honest consumer-side outcome for both is
**unverified**, and [Consumption Map §3.2](consumption-map.md) states what may be done with it.

This asymmetry is the same shape as `api-index`'s (§3.5) but the opposite way round, and the difference matters:
`api-index` can confirm a **claim** and never refute it; `resolve` can confirm **existence** and never refute it.
Between them, a positive from `resolve` is the strongest existence evidence the contract offers, because it comes
from the source rather than from the publisher's description of the source.

### 3.7 `patterns`

**Input:** `{ "package": "<import-name>", "category": "<optional>", "complexity": "<optional>",
"query": "<optional substring>" }`.

**Payload:** `patterns` — a filtered view of `usage-patterns.json`'s `patterns` array, each entry carried whole:

```json
{
  "schema_version": "1", "ok": true, "present": true,
  "package": "greet_miri", "purl": "pkg:pypi/greet-miri@1.0.0",
  "truncated": false, "cap": 10,
  "patterns": [
    { "id": "reused_greeter", "name": "Reused greeter", "complexity": "beginner",
      "category": "basic_usage", "code": "…", "explanation": { "key_points": ["…"] } }
  ]
}
```

`usage-patterns.json` is typically the **largest** document a package ships — 14 KB on this standard's own
three-class sample SDK — and the [Consumption Map](consumption-map.md) asks a consumer to read "the idiomatic
sequence **matching the task**", which is a filter, not a file read. Serving the whole array to answer a question
about one pattern is the case §3.2.3 exists to prevent.

Filters compose (all supplied filters must match). `category` and `complexity` match exactly; `query` matches
case-insensitively against `id`, `name`, and `description` — **not** against `code`, so a consumer cannot use it to
grep the package's source by proxy. Ordering, capping, truncation and continuation follow §3.5.1, with a default
`cap` of **10**.

A pattern entry is returned **whole**: the `explanation.key_points`, `security_note` and `performance_note` fields
are the package's best-practice content ([Consumption Map §5](consumption-map.md)), and a surface MUST NOT strip them
to save space. The filter selects *which* patterns, never *which parts of* a pattern.

### 3.8 `graph`

**Input:** `{ "package": "<import-name>", "symbol": "<dotted-name>", "depth": <optional int>,
"direction": "<optional>" }` — `direction` is `out` (edges from the symbol), `in` (edges to it), or `both`
(default). `depth` defaults to `1`.

**Payload:** `graph` — the neighborhood of `symbol` in `api-graph.json`, as nodes and the edges connecting them:

```json
{
  "schema_version": "1", "ok": true, "present": true,
  "package": "greet_miri", "purl": "pkg:pypi/greet-miri@1.0.0",
  "symbol": "RateLimitError", "depth": 2, "direction": "out",
  "truncated": false, "cap": 50,
  "graph": {
    "nodes": { "RateLimitError": { "type": "class", "file": "exceptions.py" },
               "APIError": { "type": "class", "file": "exceptions.py" } },
    "edges": [ { "from": "RateLimitError", "to": "APIError", "kind": "extends" } ]
  }
}
```

The audit row for `api-graph.json` claims it lets a consumer reason about blast radius and plan multi-file changes
**"without loading all source"** — a claim its only previous access path defeated, since `document("api-graph.json")`
loads the entire graph to answer a question about one symbol. On a small package that is cheap; on a large one the
graph scales with the whole public surface, and the element's stated purpose is spent obtaining it. `graph` is what
makes that claim true rather than aspirational.

`symbol` MUST be resolved against the graph's node keys, which share the dotted key space used by `api_index` and
`resolve` (§3.6). A `symbol` absent from the graph is **not** an error and **not** document-absence: it is
`present: true` with an empty `nodes`/`edges` — the graph exists, the symbol is simply not in it. Traversal is capped
per §3.5.1 (default `cap` **50** nodes); where the neighborhood exceeds the cap the surface MUST set
`truncated: true`, and a consumer MUST NOT read a truncated neighborhood as the complete blast radius.

## 4. The Response Envelope

Every response from every operation in §3 is a JSON object — never a bare array — whose top level is **owned entirely
by the surface**. The publisher's bytes appear only nested under a payload key. This separation is what makes the
absence/error signal trustworthy: a publisher cannot write to the top level, so a publisher cannot forge it.

### 4.1 Reserved Envelope Fields

This table is **exhaustive**: these are the only keys that may appear at a response's top level. The
un-forgeability argument in §4.2 depends on the surface owning a *known, closed* key set — a publisher cannot forge a
signal it cannot write, but only if "which keys are the surface's" is fully stated rather than sampled.

`ok` and `present` answer different questions and are evaluated in order: **`ok` first.** A surface MUST omit
`present` entirely when `ok` is `false`, and a consumer MUST treat `present` as meaningful only when `ok` is `true`.
Without that order a consumer reading `present` first reports a parse failure as "the package ships no such document"
— the absent-versus-failed collapse §4.2 exists to prevent.

| Field | Presence | Meaning |
|---|---|---|
| `schema_version` | Always | The wire-schema version of the **envelope**, owned and stamped by the surface |
| `ok` | Always | `true` for a served answer, `false` for a failure (§4.3) |
| `present` | `document` and its shorthands, `api-index`, `patterns`, `graph`, `resolve` — and **MUST be omitted whenever `ok` is `false`** | Whether the subject exists: the document for `document`, the parent document for a derived view, the module for `resolve` (§4.2) |
| `package` | Where a package was named or resolved | The import name the answer is about |
| `purl` | Where identity resolved (§4.1.1) | Surface-derived provenance (§9.1) |
| `name` | `document` and its shorthands | The document name the answer is about |
| `reason` | Absent responses (§4.2) | Free-text explanation for humans — **never a machine field** |
| `truncated` | `list`, `api-index`, `patterns`, `graph`, `document` | Whether the payload was cut (§3.2.3, §3.5.1) |
| `cap` | `list`, `api-index`, `patterns`, `graph` | The entry bound in force (§3.5.1) |
| `max_bytes` | `document` and its shorthands | The serialized-size bound in force (§3.2.3) |
| `next_cursor` | `list`, `api-index`, `patterns`, when truncated | Continuation token for the same ordering (§3.5.1). `graph` has no cursor (§3.8). |
| `error` | Failures only | The structured error object (§4.3) |
| `symbol` | `resolve`, `graph` | The symbol the answer is about |
| `depth`, `direction` | `graph` | The traversal actually performed |
| `packages` / `document` / `entries` / `resolution` / `patterns` / `graph` | Per operation | The payload |

#### 4.1.1 `purl` Is Surface-Derived, Never Publisher-Read

`purl` is the input to a per-namespace trust policy (§9.1), which makes it a **security decision** and therefore the
one field in this table that must not come from the publisher. A surface MUST derive it from the **installed
distribution's own recorded name and version**, never by reading `identity.purl` out of `lifecycle.json` or any other
served document. Otherwise a package declaring `pkg:pypi/requests@2.31.0` inherits requests' trust tier by simply
saying so — a forgery inside the very namespace §4 claims is un-forgeable.

Where a served `identity.purl` disagrees with the derived value, the surface MUST serve the derived value, and SHOULD
signal the mismatch (it is a strong tampering indicator). `purl` MUST be present on every response whose subject
package resolved — including `DOCUMENT_NOT_SERVABLE` and `METADATA_UNREADABLE` — and MUST be omitted where identity
did not resolve: `PACKAGE_NOT_INSTALLED`, `AMBIGUOUS_PACKAGE`, `NOT_DISCOVERABLE`.

`schema_version` is the envelope's own version, stamped by the surface and versioned independently of the transport's
protocol version and of any version field inside the payload — per the ecosystem convention in
[CLI Spec §2.6](../cli/cli-lifecycle-specification.md) and MIRI-CLI-010. A consumer pins on it to detect a wire-shape
change.

Because the envelope wraps rather than merges, a producer document keeps whatever top-level fields it already
has — `lifecycle.json`'s `miri_lifecycle_version`, `migration-guide.json`'s `from_version`/`to_version`, either file's
`$schema` — and the surface neither adds to nor strips from them. **A surface MUST NOT inject envelope fields into a
payload document, and MUST NOT hoist payload fields into the envelope.** The producer schemas set
`additionalProperties: false`, so injection would make a conforming document invalid; wrapping avoids the problem
entirely.

### 4.2 Absence Is Not Error

A query for a document a package does not ship is a **normal, successful answer**, and MUST be mechanically
distinguishable — without string-sniffing prose — from a **failure**. A surface MUST NOT signal "no such document" as
an error, nor as a silent empty success. Two independent booleans carry the two axes:

- `ok` — did the surface serve the request?
- `present` — does the requested document exist?

An **absent** response (the package ships no such document) is `ok: true`, `present: false`, with no payload key and a
free-text `reason` for humans:

```json
{ "schema_version": "1", "ok": true, "present": false,
  "package": "weather_sdk", "purl": "pkg:pypi/weather-sdk@1.2.0",
  "name": "lifecycle.json",
  "reason": "package ships no lifecycle.json" }
```

A consumer MUST branch on `ok` and `present`, never on `reason`, which is explicitly not a machine field.

This is the single most consequential clause in this document: a consumer's **honest-degradation** conformance — that
it reports an absent document as absent and never synthesizes one — is only checkable if the surface itself tells
absent from failed, and only trustworthy if a hostile package cannot forge either signal. *(The current reference
implementation returns absence as a `tools/call` success whose text is an ad-hoc `{"error": …}` object with no code and
no `present` flag — indistinguishable from a real error; conforming it to this clause is the first implementation
task.)*

#### 4.2.1 Absence for `api-index`

`api-index` is derived from `sdk-manifest.json`, so it has an absent case like any document-returning operation: a
package that ships no `sdk-manifest.json` gets `ok: true`, `present: false`, **no `entries` key**, and a `reason`.

A surface MUST NOT signal that absence with `present: true` and an empty `entries` object. The two mean different
things and a consumer cannot recover the difference: `entries: {}` says *"this package's surface, as filtered, is
empty"* — a statement about the package — whereas `present: false` says *"there is no manifest to derive an index
from."* Reading the former as the latter is exactly the absence-implies-non-existence inference §3.5 forbids.

Equally, a `query` that matches nothing is **not** absence: the manifest exists, so the response is `present: true`
with `entries: {}` and `truncated: false`. That is the one case where an empty `entries` is correct.

### 4.3 The Error Envelope

A failure reuses the [CLI §2.6](../cli/cli-lifecycle-specification.md) error envelope — `ok: false` plus a top-level
`error` object carrying a machine `code` and a `retryable` boolean:

```json
{ "schema_version": "1", "ok": false,
  "package": "weather_sdk",
  "error": { "code": "PACKAGE_NOT_INSTALLED", "retryable": false } }
```

`retryable` follows §2.6 exactly: `true` only for transient failures where the identical call may later succeed.
Contract-specific codes, alongside the §2.6 standard codes:

| `code` | `retryable` | Meaning |
| --- | --- | --- |
| `PACKAGE_NOT_INSTALLED` | `false` | No installed package provides that import name |
| `AMBIGUOUS_PACKAGE` | `false` | Several installed distributions provide that import name (§3.1) |
| `DOCUMENT_NOT_SERVABLE` | `false` | The requested name is outside the §3.2 whitelist |
| `NOT_DISCOVERABLE` | `false` | The package could not be resolved without importing it (§5) |
| `METADATA_UNREADABLE` | `false` | The document exists but could not be read or parsed as declared |

`METADATA_UNREADABLE` is the honest answer for a malformed document: a surface MUST NOT repair, re-serialize, or
partially serve a document it could not parse, and MUST NOT report it as absent.

### 4.4 A Surface Version Independent of the Transport

A metadata-query surface MUST advertise its own **surface version** — the contract version of the §3 operations —
distinct from any transport protocol version and from `schema_version` (which versions the envelope). Under the MCP
binding the MCP `protocolVersion` is the transport's version, not this contract's; §6.3 fixes where the surface
version is carried. This lets a consumer negotiate the metadata contract without conflating it with the transport it
happens to ride.

## 5. Import-Free Discovery

Discovery MUST locate a package's metadata **without importing or executing the package**. A surface MUST resolve a
package's location through the import system's path finders (e.g. `importlib.util.find_spec`, which returns a spec
without running module code) and read files from the resolved `agent-metadata/` directory; it MUST NOT `import` the
target, run its `__init__`, or invoke any of its code to answer a query.

This is a load-bearing security property, not an optimization: discovery routinely runs over *every* installed
package, including ones the consumer has not vetted, and a hostile or broken package must not gain code execution
merely by being installed and enumerated. A surface that cannot resolve a package without importing it MUST return
`NOT_DISCOVERABLE` (§4.3) rather than import it. *(The reference provider implements exactly this — `find_spec` plus
file reads, no imports.)*

## 6. The MCP Binding

The [Model Context Protocol](https://modelcontextprotocol.io/) is the first binding of the §3 contract. A conformant
MCP binding exposes the operations as MCP tools over JSON-RPC 2.0 (stdio):

| Contract operation | MCP tool |
|---|---|
| `list` | `miri_list_packages` |
| `document` | `miri_document` |
| `lifecycle` | `miri_lifecycle` |
| `migration-guide` | `miri_migration_guide` |
| `api-index` | `miri_api_index` |
| `resolve` | `miri_resolve` |
| `patterns` | `miri_patterns` |
| `graph` | `miri_graph` |

### 6.1 Mapping

- Each operation's input (§3) is the tool's `inputSchema`.
- Each operation's **§4 envelope is carried intact** as the tool result. MCP delivers a tool result as
  `content: [{ "type": "text", "text": "<json>" }]`; the `text` MUST be the complete envelope — `schema_version`, `ok`,
  and the payload nested under its key. A binding MUST NOT strip the envelope, hoist the payload to the top level, or
  reshape the payload document; a consumer parses the transport envelope, then the §4 envelope, then the payload.
- A binding MUST NOT signal a §4.3 error as an MCP protocol error, nor a §4.2 absence as either: both are served
  answers and travel as ordinary tool results carrying the envelope. Protocol errors are reserved for malformed
  requests (unknown tool, schema-invalid input).

### 6.2 Read-Only, Local Surface

The MCP binding is read-only and MUST execute nothing on the artifact's behalf (§5, §9). It binds a local transport
(stdio, or a loopback socket) and serves only the metadata of packages installed in its own environment.

#### 6.2.1 Installed Scope Only — What This Contract Does Not Answer

Every operation in §3 resolves a package through the local import system (§5), so **this contract answers only for the
version currently installed**. Two questions a developer genuinely asks are therefore **out of scope in 0.3-draft**,
and are stated here rather than left to be discovered at an unanswerable read-step:

| Question | Status |
|---|---|
| "Is this candidate package on the index MIRI-compatible, before I install it?" | Out of scope. No operation accepts a purl, a registry, or an uninstalled package. |
| "I am on 1.2.0 — what breaks if I move to 1.5.0?" | Out of scope. `migration-guide` reports the transition *into* the installed version, not a prospective one. |

This is a deliberate consequence of the surface fetching nothing (§9.2) and executing nothing (§5): answering either
question means reading an artifact from a registry, which would turn publisher-controlled input into server-side
network requests and require its own threat model. A future version may add a separately-scoped operation for this;
until it does, **no normative read-order in the [Consumption Map](consumption-map.md) may depend on a pre-install or
target-version answer**, and a consumer MUST NOT synthesize one.

### 6.3 Surface Version in `initialize`

The MCP `initialize` result advertises the transport's `protocolVersion` (an MCP date) and `serverInfo`. The binding
MUST additionally advertise the **metadata-query surface version** (§4.4) at the normative path
`capabilities.miri.surface_version`, as a string — not merely as `serverInfo.version`, which names the implementation
rather than the contract. A client negotiates the contract version from that field alone. *(The reference server today
advertises only `serverInfo.version`; adding the capability is a binding task.)*

## 7. Project Declaration

A *consuming* project declares which context server serves its dependencies' metadata in a **`[tool.miri.consume]`**
table in its `pyproject.toml`. TOML nests this table under the *producer* `[tool.miri]` table
(Wheel Extensions §7.1.1) while keeping the two roles in separate key spaces, so a project that both produces and
consumes Miri metadata never mixes them. From this declaration, tooling MAY generate agent-harness configuration
(e.g. an `.mcp.json`).

Because a project file arrives with every `git pull` and is editable by any pull request, the declaration is a trust
boundary. Its grammar is therefore closed:

```toml
[tool.miri.consume]
server = "miri"      # REQUIRED. Closed enumeration; "miri" selects the standard context server.
transport = "stdio"  # OPTIONAL. One of: "stdio", "loopback". Default "stdio".
```

- `server` MUST be a value from a **closed enumeration** defined by this specification; `"miri"` is the only value in
  0.3-draft, and it selects "run the standard Miri context server for this environment."
- The table MUST NOT contain any other key. In particular, `command`, `args`, `env`, `url`, and `path` are
  **structurally excluded**: a declaration can select a known server, never describe an arbitrary process to execute.
  A consumer encountering an unknown key MUST reject the declaration rather than ignore the key.
- Generated harness configuration MUST NOT be auto-launched; generation is an explicit user action, never a side
  effect of opening the project.
- A *dependency's* metadata MUST NOT influence the *consumer project's* harness configuration; the generator acts only
  on the consuming project's own declaration.

## 8. Discovery Measurement

A surface MAY record an append-only, JSONL **invocation log** — one entry per query — as instrumentation for the
pre-registered experiment's organic-discovery question (H5: do agents reach the metadata at all, and by which
vehicle?). Where a surface logs, each entry carries:

| Field | Meaning |
|---|---|
| `timestamp` | RFC 3339 UTC instant of the query |
| `operation` | The §3 operation name — one of the eight in the §3 table — **never** the binding's tool name, so logs are comparable across bindings. Stated by reference rather than enumerated here, so the vocabulary cannot go stale when the operation set changes. |
| `arguments` | The operation's input as received |
| `outcome` | `served`, `absent`, or `error` — the §4 result class, so reach and success are distinguishable |
| `session` | An opaque correlation id for the invoking session, so entries can be grouped into runs and treatment arms |

The log is measurement only: it MUST NOT influence any response, and a logging failure MUST NOT break a query.
*(The reference server implements this behind `miri mcp --log`.)*

Two limits are normative for anyone analyzing it. The log observes **only the context-server vehicle**: in-wheel file
reads and in-process `_miri` calls (§1) are invisible to it, so it can measure reach *through this surface* and MUST
NOT be read as measuring metadata reach overall. And because logging is optional, **an absent or empty log licenses no
conclusion** — neither that agents did not reach the metadata, nor that they did.

## 9. Security Considerations

### 9.1 Threat Model

Served metadata is publisher-authored, untrusted data, and a context server *frames it as tool output* — a channel
harnesses tend to treat as trusted. That framing makes the producer threat model
([Lifecycle and Security Metadata §9.1](../python/lifecycle-security-metadata.md);
[Agent Metadata §9](../python/miri-agent-metadata-specification.md)) more, not less, important. A conformant context
server:

- **Owns the envelope** (§4). Publisher bytes are nested under a payload key and never share a namespace with `ok`,
  `present`, or `error`, so a hostile package cannot forge a served, absent, or failed signal by writing those keys
  into its own document.
- **Labels every payload as untrusted, package-authored data**, never as directive text; a consumer MUST NOT execute
  a command or follow a step drawn from a payload without out-of-band verification.
- **Carries per-response provenance** — the resolved `purl` on every single-package envelope (§4.1) and on every
  `list` row (§3.1) — so a consumer can apply a per-namespace trust policy rather than collapsing every installed
  package's trust into one undifferentiated stream. `list` carries provenance per entry, since one response spans
  many packages.
- **Never serves `prompt-templates.md`.** That file is the highest-risk injection surface (Agent Metadata §9); it is
  excluded from the §3.2 whitelist, and a server MUST NOT add an operation that serves it.
- **Executes nothing** (§5): it reads and relays, and it discovers import-free.
- **Binds a local transport only** (stdio or loopback), scoped to its own environment.

### 9.2 Network Fetches Are Outside This Contract

No operation in §3 resolves a package-declared URL. The surface **fetches nothing**: it serves in-wheel bytes only, and
a surface that fetched an advisory or update-check endpoint on the publisher's say-so would be turning
publisher-controlled data into server-side requests — precisely the SSRF exposure the producer standard guards.

Resolving those URLs is the **consumer's** act, performed at decision time under the SSRF guard in
[Lifecycle and Security Metadata §9.2](../python/lifecycle-security-metadata.md) (HTTPS-only, block private,
link-local and cloud-metadata ranges, re-validate after redirects, forward no credentials). The Consumption Map's
security task ([§3.5](consumption-map.md)) states the consumer-side obligation, and Consumer Conformance numbers the
check; this contract's obligation is simply that the surface never performs the fetch itself.

## 10. Conformance

The checkable requirements for a *consumer* of this contract — branches on `ok`/`present` rather than message text,
never treats a truncated `api-index` as a complete surface, settles symbol existence with `resolve` rather than with
the index and never reports a `not-in-source` result as proof of absence, never synthesizes an absent document, never
executes on a payload's say-so, applies the §9.2 guard to any URL it resolves — will be numbered
`MIRI-CONSUMER-NNN` in the forthcoming Consumer Conformance document and verified against the reference consumer
(`miri consume`) driven on a paired bare/miri fixture and an adversarial-metadata twin. Capping and envelope
integrity are the **surface's** obligations, checked against a reference surface; a consumer emits no responses and
cannot be checked for them.

This document specifies the surface those checks are written against.
