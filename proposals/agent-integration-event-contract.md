# Design sketch: a host-agnostic event contract for agent integration

*Proposal Version: 0.1-draft*
*Status: Draft — design sketch for discussion, not normative*
*Created: 2026-09-06*
*From: the miri-standard maintainers*

## 1. "Hook" is the wrong noun

A hook is a *host's* mechanism. Claude Code has hooks; git has hooks; an LSP server has code actions;
a CI runner has steps; an editor extension has activation events. Writing a "hook interface" into the
standard would bake one host's vocabulary into a document that is supposed to outlive it — the same
mistake as writing the Discovery Contract *about* MCP instead of giving MCP a binding.

The generic thing is not a hook. It is an **event**: a named, observable moment with a defined
payload. Hooks *deliver* events. So does a code action, a CI step, a pre-commit script, or a human
typing a command. The standard specifies the event; each host's binding specifies the delivery.

The test we would hold this to: **if the specification names a mechanism, it is written wrong.**

## 2. What already exists, and should not be reinvented

Three primitives are in the standard today and cover most of this:

| Need | Already specified |
|---|---|
| Getting a request to a local process | Discovery Contract §7 — `stdio` and `loopback`, with the connection file, token, and staleness rules in §7.1 |
| A response shape a consumer can trust | §4 — the surface-owned envelope, plus `discovery-envelope-v1.json` |
| What to read for a given task | Consumption Map §3 — the six tasks |

So the event contract needs to add exactly two things: **a vocabulary of events**, and **a payload
key for what comes back**. Everything else is reuse.

## 3. The event contract

### 3.1 An event is a closed set of kinds

Six kinds, one per map task, named for the observable action rather than the intention behind it:

| `kind` | Fires when | Map task |
|---|---|---|
| `dependency.add` | a dependency is about to be added | §3.5 security/trust |
| `dependency.version_change` | a dependency's version is about to change | §3.3 upgrading |
| `package.first_reference` | a package not yet used in this session is first referenced | §3.1 first use |
| `integration.begin` | new code is about to be written against a package | §3.2 scaffolding |
| `runtime.error` | an error naming a package is observed | §3.4 diagnosing |
| `test.author` | a test touching a package is about to be written | §3.6 tests |

Closed, for the same reason the servable set and the error codes are closed: an open vocabulary is
one every binding extends differently, and two bindings that disagree about what an event *is* do not
interoperate.

### 3.2 An event is a request, not a notification

```json
{ "schema_version": "1",
  "kind": "dependency.add",
  "phase": "before",
  "subject": { "package": "requests", "version": ">=2.31" } }
```

- **`phase`** is `before` or `after`. Every REQUIRED trigger is `before`: a migration guide is
  worthless after the upgrade lands, and a foreign-namespace `replacement` is only actionable while
  the dependency does not yet exist. `after` exists for `runtime.error`, which cannot be anything
  else.
- **`subject`** carries only what the event is about. A package name, sometimes a version
  constraint or a symbol. Deliberately not a file path, a diff, or a buffer: a binding that needs
  the user's source to decide what to say has left the standard's scope and entered the host's.
- There is **no host field**, no editor state, no session identifier. If a payload cannot be
  constructed by a CI runner as easily as by an editor, it is over-specified.

### 3.3 The response is the existing envelope

No new response format. The §4 envelope, with one payload key added:

```json
{ "schema_version": "1", "ok": true, "present": true,
  "findings": [
    { "task": "3.5", "severity": "must",
      "purl": "pkg:pypi/requests@2.31.0",
      "summary": "declared replacement is in a different purl namespace",
      "source": "lifecycle.json",
      "quote": "pkg:pypi/attacker-successor@9.0.0" } ] }
```

Everything §4 already says applies unchanged and for the same reasons: the top level is
surface-owned, so a package cannot forge `ok`; `quote` is publisher bytes and is attributed rather
than adopted (`MIRI-CONSUMER-020/022`); and **silence is `present: false` with a `reason`** — the
existing absence shape, not a new one. That is worth noticing, because §3.2.1 of the proposal wanted
silence-by-default as a new obligation and the envelope already expresses it.

`findings` is a new payload key, which the envelope schema permits: its root is deliberately open,
precisely so a new operation or channel can add one without a schema change forbidding it.

### 3.4 The transport is one of the two that exist

`stdio` or `loopback`, exactly as Discovery Contract §7 defines them, including §7.1's connection
file, token, permissions and staleness rules. A binding does not get to invent a third.

This is the part that makes the interface genuinely host-agnostic rather than nominally so: **the
same binding process serves a Claude Code hook, a git pre-commit, a CI step and an editor extension,
because all four can spawn a subprocess or open a loopback socket.** The host differs in what it
observes, never in how it asks.

## 4. What a binding document specifies

By analogy with §6.3, and no more than this:

1. **The host**, named.
2. **The mapping** from each event `kind` it supports to the host's own observable moment.
3. **Which kinds it does not support**, and why — a binding that cannot observe `test.author` says
   so rather than firing it approximately.
4. **How output reaches the agent**, and that it arrives as data rather than instruction.
5. **How the user turns it off.**

Item 3 is the one worth insisting on. A binding that silently omits a kind is indistinguishable from
one where the kind never fired, which is the same "cannot tell working from unused" failure the whole
proposal exists to close.

## 5. Why this is testable without a host

Because the event is a request and the response is an envelope, a conforming binding can be driven
with **no host at all**: feed it an event, read the envelope.

That is what makes the fixture counter-offer work. The goldens become event/envelope pairs authored
from this specification — an `dependency.add` for `greet_adversarial` must produce a `must`-severity
finding naming the namespace mismatch; the same event for `greet_bare` must produce silence. Neither
golden mentions a host, so neither can be captured from one implementation's behavior.

Two existing fixture properties do the heavy lifting, unchanged:

- **`bare` ships no metadata**, so silence-by-default is a fixture drive, not a claim.
- **every `.py` is byte-identical across variants**, so driving `adversarial` and `miri` with the
  same event and asserting identical *trigger* behavior tests publisher-independence directly. Any
  difference is metadata-attributable by construction.

## 6. Open questions we do not answer here

- Whether `phase: after` earns its place, or whether `runtime.error` should be the only `after` event
  and the field dropped in favour of naming that one kind specially.
- Whether `findings[].severity` should reuse the check severity vocabulary (`LOW`…`CRITICAL`) or the
  conformance level vocabulary (`must`/`should`). They answer different questions and picking the
  wrong one will be hard to undo.
- Whether a binding may batch events. A CI runner sees fifty dependency additions at once; firing
  fifty separate requests may be correct, or may be the noise failure mode in a different costume.
