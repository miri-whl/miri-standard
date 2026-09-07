# Agent Integration Contract

*Specification Version: 0.4.0-draft*
*Status: Draft*
*Created: 2026*

## Abstract

The producer standards specify what an artifact ships. The [Discovery Contract](discovery-contract.md) specifies how
a surface serves it. The [Consumption Map](consumption-map.md) specifies what a consumer reads, in what order, for
which task. None of them specifies **what causes the reading to start**.

That gap is not cosmetic. The Discovery Contract's binding is *pull*: an agent must decide to ask before adding a
dependency, and nothing in the ecosystem makes it. A conformant producer, a conformant surface and a conformant
consumer can coexist with metadata that is never read, and every score in the standard stays green. The standard
cannot presently tell a working integration from an unused one.

This document specifies the missing half: an **event contract** naming the observable moments at which each map task
becomes actionable, what a conforming integration owes its caller at those moments, and what it must never do. It
carries one binding — Claude Code — as §6, in the same way the Discovery Contract carries MCP as its §6.

## Table of Contents

1. [Why Not "Hooks"](#1-why-not-hooks)
2. [What This Reuses](#2-what-this-reuses)
3. [The Event Contract](#3-the-event-contract)
4. [Obligations](#4-obligations)
5. [What a Binding Document Specifies](#5-what-a-binding-document-specifies)
6. [The Claude Code Binding](#6-the-claude-code-binding)
7. [Conformance](#7-conformance)

## 1. Why Not "Hooks"

A hook is a *host's* mechanism. Claude Code has hooks; git has hooks; a language server has code actions; a CI runner
has steps; an editor extension has activation events. A specification written around hooks would bake one host's
vocabulary into a document meant to outlive it — the same error as writing the Discovery Contract *about* MCP rather
than giving MCP a binding.

The portable unit is a **trigger**: a specified moment at which a map task becomes actionable. A hook *delivers* a
trigger. So does a code action, a pre-commit script, a CI step, or a person typing a command.

Three terms, each doing one job, and the first two complete a vocabulary the Consumption Map already had:

| Term | Answers | Where it is defined |
|---|---|---|
| **task** | *what work* | [Consumption Map §3](consumption-map.md) |
| **vehicle** | *how the data arrives* | [Consumption Map §1.1](consumption-map.md) |
| **trigger** | *when the work starts* | §3.1 of this document |
| **event** | the message a host sends when a trigger fires | §3.2 of this document |
| **binding** | a host's implementation of the contract | §5, and [Discovery Contract §6](discovery-contract.md) |

"Hook" is not on that list and should not join it. It is what one host calls its delivery mechanism, and the
sentence that has to keep working is *"Claude Code delivers a trigger via a hook; a CI runner delivers the same
trigger via a step."* That sentence only parses if hook is theirs and trigger is ours. The word appears elsewhere in
this standard exactly seven times, every one of them describing git or setuptools — never a Miri concept.

> **The test this document is held to:** if a normative clause names a mechanism, the clause is wrong.

## 2. What This Reuses

Three primitives already exist and are not reinvented here:

| Need | Already specified |
|---|---|
| Getting a request to a local process | [Discovery Contract §7 and §7.1](discovery-contract.md) — `stdio` and `loopback`, with the connection file, token, permissions and staleness rules |
| A response shape a consumer may trust | [Discovery Contract §4](discovery-contract.md) — the surface-owned envelope, and [`discovery-envelope-v1.json`](../../schemas/discovery-envelope-v1.json) |
| What to read for a given task | [Consumption Map §3](consumption-map.md) — the six tasks |

This contract therefore adds exactly two things: a **vocabulary of events**, and a **payload key** for what comes
back. Everything else is reuse, which is the point — a third transport or a parallel response format would be two
more things for two implementations to diverge on.

## 3. The Event Contract

### 3.1 Triggers

Six triggers, one per map task, each named for the **observable action** rather than the intention behind it. An
intention is not observable and cannot be a trigger.

| Trigger (`kind`) | Fires when | Map task | Level |
|---|---|---|---|
| `dependency.add` | a dependency is about to be added | [§3.5](consumption-map.md) security and trust | REQUIRED |
| `dependency.version_change` | a dependency's version is about to change | [§3.3](consumption-map.md) upgrading | REQUIRED |
| `package.first_reference` | a package not yet used in this session is first referenced | [§3.1](consumption-map.md) first use | SHOULD |
| `integration.begin` | new code is about to be written against a package | [§3.2](consumption-map.md) scaffolding | SHOULD |
| `runtime.error` | an error naming an installed package is observed | [§3.4](consumption-map.md) diagnosing | SHOULD |
| `test.author` | a test touching a package is about to be written | [§3.6](consumption-map.md) tests | SHOULD |

The set is **closed**. A binding MUST NOT invent a seventh kind, for the same reason the servable set and the error
codes are closed: an open vocabulary is one every binding extends differently, and two bindings that disagree about
what an event *is* do not interoperate.

**Two are REQUIRED** because their triggers are observable without inference and their findings are actionable only
before the decision they inform becomes expensive to reverse — a migration guide is worthless after the upgrade, and a
foreign-namespace `replacement` is
cheapest to catch while the dependency does not yet exist. REQUIRED means **the binding implements the kind**, not
that the kind produces output; combined with §4.1, a binding that finds nothing says nothing, so the cost of
requiring two is close to zero.

### 3.2 An Event Is a Request

```json
{
  "schema_version": "1",
  "kind": "dependency.add",
  "phase": "before",
  "subject": { "package": "requests", "version": ">=2.31" }
}
```

- **`phase`** is `before` or `after`, describing whether the action that produced the event has landed.
  `runtime.error` is necessarily `after`. Every kind other than `runtime.error` and `dependency.add` is `before`.

  **`dependency.add` is the exception, and it was found by building the thing.** The taxonomy originally claimed
  the trigger point was "before the dependency exists — the only moment before it does". That is unsatisfiable: a
  package that is not yet installed ships nothing a local surface can read, so there is no `lifecycle.json` to
  consult until the install lands. A conforming binding therefore fires it **after the install and before any code
  is written against it**, which is still before the decision that is expensive to reverse — an install is undone
  with an uninstall; a codebase written against a package is not. A genuinely pre-install trigger requires a
  registry-side surface, which is a different contract than the one this standard defines, and the schema permits
  `before` so that such a surface is not forbidden in advance.
- **`subject`** carries only what the event is *about* — a package name, and where the kind implies one, a version
  constraint or a symbol. It MUST NOT carry a file path, a diff, a buffer, or the user's source. A binding that needs
  the user's code to decide what to say has left this standard's scope and entered the host's.
- There is **no host field**, no editor state, no session identifier. A payload a CI runner cannot construct as
  easily as an editor can is over-specified, and the absence of those fields is what makes one binding process serve
  every host.

### 3.3 The Response Is the Existing Envelope

No new response format. The [§4 envelope](discovery-contract.md), with one payload key:

```json
{
  "schema_version": "1", "ok": true, "present": true,
  "findings": [
    { "task": "3.5", "level": "must",
      "purl": "pkg:pypi/greet-adversarial@1.0.0",
      "summary": "declared replacement is in a different purl namespace",
      "source": "lifecycle.json",
      "quote": "pkg:pypi/attacker-successor@9.0.0" }
  ]
}
```

Everything §4 says applies unchanged, and for the same reasons. The top level is surface-owned, so a package cannot
forge `ok` or `present`. `quote` holds publisher bytes and is attributed rather than adopted
(`MIRI-CONSUMER-020`, `MIRI-CONSUMER-022`). `findings[].level` is `must` or `should`, matching the conformance
vocabulary rather than the check-severity one, because the question a caller asks here is *may I proceed*, not *how
bad is this*.

`findings[].task` is the map section that produced the finding, written as the bare section number — `"3.1"`
through `"3.6"`, matching the six tasks and nothing else. It is not free text: a caller routing on it needs a closed
set, and a task number is the only identifier the map guarantees is stable.

`present` follows §4.2 unchanged: `true` when `findings` is present and non-empty, `false` when the trigger found
nothing (§4.1). A response MUST NOT carry `present: true` with no `findings` key, and MUST NOT carry `findings`
alongside `present: false` — the same payload/absence coupling the envelope schema already enforces for every other
payload key.

`findings` is a new payload key, which the envelope schema permits: its root is deliberately open so that a new
operation or channel can add one without a schema change forbidding it.

## 4. Obligations

### 4.1 Silence Is the Existing Absence Shape

A trigger with nothing to report MUST answer with the §4.2 absent shape — `ok: true`, `present: false`, a `reason`,
and no payload key. It MUST NOT emit an empty `findings` array, and MUST NOT emit prose confirming that it checked.

The shape is §4.2's; the *meaning* is narrower, and conflating them would be a mistake. In the Discovery Contract
`present: false` says **the document does not exist**. Here it says **this trigger found nothing to report**, which
may be because the package ships no metadata, or because it ships metadata containing nothing relevant to this
event. A consumer MUST NOT read a trigger's `present: false` as evidence about what the package ships; that question
is `list`'s to answer, and the presence-only rule ([Consumption Map §4](consumption-map.md)) applies unchanged.

Reusing the shape is still right — a caller branching on `ok`/`present` needs no new code path. What a trigger
response deliberately does **not** do is distinguish the two causes mechanically. `reason` is free text for humans
and never a machine field ([Discovery Contract §4.2](discovery-contract.md)), and adding a machine-readable cause
here would contradict that rule for the convenience of a caller that does not need it: a consumer wanting to know
what a package ships asks `list`, which is the operation whose answer that is. A trigger reports what it found, not
an inventory of what exists.

Stating the obligation this way is deliberate. A binding that
announces *"checked, nothing found"* on every edit is a context tax, and the predictable result is that a user
disables it — after which the conformant producer, surface and consumer are all still green and the metadata is
again never read. The failure this whole document exists to close is reachable through its own remedy.

### 4.2 A Trigger Reports; It Does Not Block

A trigger MUST NOT block, cancel, or veto the action that produced the event.

The obligation not to proceed unilaterally already exists and already binds the **consumer**:
`MIRI-CONSUMER-032` requires that a consumer never install or rewrite call sites onto a declared `replacement`
*without human confirmation*. That is a rule about the consumer acting, not a licence for a binding to interrupt a
human. Conflating the two would grant the binding a power the checks never gave it, and would be unimplementable in
the many hosts that expose no veto at all.

The binding's job at MUST level is to ensure the finding **reaches the point where that confirmation is asked for**.

Observably, and this is what a suite asserts: drive the binding with an event whose task yields a `must`-level
finding, and **the action that produced the event still completes**. Together with §4.4 — exit zero, envelope only,
no host control key — that is the whole test. "Did not block" is not a claim about the binding's intent; it is a
claim about whether the host's action ran, which is observed at the host boundary like any other.

### 4.3 The Publisher Does Not Control the Trigger

No field in any shipped document may determine whether, when, or how loudly a trigger fires. A binding MUST derive
**trigger behavior** solely from the observable event and its own configuration.

*Trigger behavior* is the decidable part, and is exactly four things: **whether** an event produces a response
carrying `findings` at all; **which** `kind` was reported; **how many** findings were raised; and **what `level`**
each carries. Nothing else. The *content* of a finding — its `summary`, its `quote`, the purl it names — is derived
from the metadata by design, and is governed separately below.

**Publisher influence over content is permitted; over `level` it is not.** A finding's prose comes from the served
document — that is the whole point of reporting it — but a shipped field MUST NOT determine a finding's `level`,
because `level` is what decides whether a caller may proceed. A package that could mark its own finding `should`
would be grading its own exam, and one that could mark an unrelated finding `must` would be blocking a competitor.
`level` is assigned by the consumer from the Consumer Conformance profile, never read from metadata.

Every item in the [Agent Metadata](../python/miri-agent-metadata-specification.md) threat model concerns **what the
metadata says**: narrative files inject, `api_index` can lie, execution is not sandboxed, provenance anchors trust.
This is the first concerning **what the metadata makes happen**. Content and control are different axes, and a
package that can demand the agent's attention has a denial-of-context channel that no existing rule closes.

### 4.4 Output Is Data, Including Its Shape

A binding MUST NOT emit output whose *shape* a host interprets as control. Hosts assign meaning to more than message
text: an exit status, a reserved key in a JSON response, a control sequence, a documented "deny" or "stop" field.
§4.2 forbids blocking; this forbids reaching the same effect through a channel the host reads structurally rather
than as prose.

The rule is stated on shape rather than on intent because intent is not observable: a binding that emits a
host's deny-key has blocked the action whether or not it meant to. Concretely, a conforming binding exits zero
whatever it found, and emits only the §3.3 envelope.

### 4.5 Degradation Is the Map's, Unchanged

A trigger that cannot complete its task reports the skipped step with a reason from the map's closed set
([§4](consumption-map.md), `MIRI-CONSUMER-002`). A push channel has one further vehicle that can be absent — the
event itself — and `unavailable-vehicle` covers it. No new reason is added.

## 4.6 Worked Example: What a Trigger Actually Does

The three documents compose, and this is the chain end to end. A trigger names a **task**; the task's read-order
names **operations**; the operations are served by the **surface**. Nothing here is new machinery — the point of the
example is that there is none.

`dependency.add` for `greet_adversarial`, whose task is [§3.5 security and trust](consumption-map.md):

```text
host observes an edit adding a requirement
  └─ event  { kind: "dependency.add", phase: "before", subject: { package: "greet_adversarial" } }
      └─ task 3.5 of the Consumption Map, read in order:
          1. lifecycle          → identity, support.status, advisory_sources, update_check
          2. document           → migration-guide.json, where support.status is deprecated
          3. (C) the consumer's own SSRF guard on any URL it resolves — never the surface's
      └─ findings
          { task: "3.5", level: "must",
            summary: "declared replacement is in a different purl namespace",
            source: "lifecycle.json", quote: "pkg:pypi/attacker-successor@9.0.0" }
```

The operations are the Discovery Contract's, unchanged and uncoordinated with this document: `lifecycle` and
`document` are two of the eight, called over `stdio` or `loopback` exactly as any other consumer calls them. A
binding is a *caller*, not a new kind of surface, which is why it needs no new transport and no new envelope.

Two other tasks, to show the shape holds:

| Trigger | Task | Operations its read-order uses |
|---|---|---|
| `dependency.version_change` | [Map §3.3](consumption-map.md) upgrading | `migration-guide`, then `list` and `resolve` to bridge a replacement purl to an import name and confirm the surface exists |
| `runtime.error` | [Map §3.4](consumption-map.md) diagnosing | `patterns` filtered to the failing surface, then `api-index`, then `resolve` where the entry lacks `signature` or `file` |

`graph` appears in no REQUIRED trigger's read-order. That is worth stating rather than leaving to inspection: it
serves §3.2 scaffolding, whose trigger is SHOULD and which the Claude Code binding does not implement (§6.2). A
binding that never calls `graph` is not deficient — it has no trigger that reaches it.

**What the binding adds is the first line and the last.** Everything between them already existed and was already
specified; the gap this document closes is that nothing caused the first line to happen.

## 5. What a Binding Document Specifies

By analogy with [Discovery Contract §6](discovery-contract.md), and no more than this:

1. The **host**, named.
2. The **mapping** from each supported `kind` to an observable moment in that host.
3. **Which kinds it does not support, and why.**
4. **How output reaches the agent**, and that it arrives as data rather than instruction.
5. **How a user turns it off.**

Item 3 is the one to insist on. A binding that silently omits a kind is indistinguishable from one where the kind
never fired — which is the same *cannot tell working from unused* failure this document exists to close, reproduced
one level down.

## 6. The Claude Code Binding

The first binding of the §3 contract. Claude Code exposes **hooks**: shell commands registered against named
lifecycle events in `settings.json`, receiving JSON on stdin.

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "miri agent-event", "timeout": 30 } ] }
    ],
    "PostToolUse": [
      { "matcher": "Bash",
        "hooks": [ { "type": "command", "command": "miri agent-event", "timeout": 30 } ] }
    ]
  }
}
```

### 6.1 Kind Mapping

| Contract `kind` | Claude Code event | How the binding recognizes it |
|---|---|---|
| `dependency.add` | `PreToolUse`, matcher `Edit\|Write` | the target is a **dependency manifest** (below) and the proposed content adds a requirement absent from the current file |
| `dependency.version_change` | `PreToolUse`, matcher `Edit\|Write` | same target, and a requirement's version specifier differs |
| `runtime.error` | `PostToolUse`, matcher `Bash` | command output contains a traceback naming an installed package |
| `test.author` | `PreToolUse`, matcher `Edit\|Write` | the target path matches the project's test discovery configuration |

A **dependency manifest** is a file this binding recognizes as declaring the project's dependencies. For Python that
is `pyproject.toml`, `requirements*.txt`, `setup.cfg`, `setup.py`, `Pipfile`, and `environment.yml`. The list is
this *binding's*, not the contract's — another host or ecosystem will have a different one — and a binding MUST
publish its list rather than leaving it to be inferred, because a manifest the binding does not recognize is a
`dependency.add` that silently never fires.

Both REQUIRED kinds are carried by `PreToolUse` on the edit tools, which is the only moment in this host at which a
dependency change is observable **and** has not yet happened.

### 6.2 Kinds This Binding Does Not Support

Stated rather than approximated, per §5 item 3:

- **`package.first_reference`** — Claude Code exposes no event for "a symbol was referenced". The nearest available
  signal is an `Edit` whose content contains a new import, which fires on any edit that happens to add one and misses
  every reference to an already-imported package. That is not the event; a binding that mapped it anyway would be
  reporting a different thing under the contract's name.
- **`integration.begin`** — the moment "new code is about to be written against a package" has no observable
  boundary in this host. It is inferable from a sequence of edits, and inference is what §3.1 excludes.

A conforming binding **omits these and says so**. It does not fire them approximately.

That is a general rule, not a note about this host: a binding MUST NOT map a trigger to an observable moment that
fires at materially different times than §3.1 specifies. Reporting a different event under a contract kind's name is
worse than omitting the kind, because a caller cannot tell the two apart — the omission is visible in the binding
document (§5 item 3) and the approximation is not. Where a host's nearest signal is close but not equivalent, the
binding says so and omits it.

### 6.3 Output and the Non-Blocking Rule

`PreToolUse` in this host **can** deny the tool call. This binding MUST NOT use that capability (§4.2). Findings are
written to the hook's stdout as attributed data and reach the agent as context; the tool call proceeds.

That the host offers a veto the contract forbids is worth stating plainly: the constraint is on the binding, not on
the host, and a reviewer checking this binding should confirm the denial path is absent rather than merely unused.

### 6.4 Transport

The binding invokes the metadata surface over `stdio` or `loopback` exactly as
[Discovery Contract §7](discovery-contract.md) specifies. It introduces no transport of its own. The `timeout` in the
hook registration is the host's, and a binding that exceeds it MUST fail silent rather than partial — a truncated
finding is a finding a caller cannot act on.

### 6.5 Disabling

Removing the hook entry from `settings.json` disables the binding completely. A binding MUST NOT install a second
mechanism that survives that removal.

## 7. Conformance

No new check family. The obligations in §4 restate existing `MIRI-CONSUMER` requirements for a new channel, and are
scored through that family — with two exceptions, which had no analogue in the consumer family before this document and
are
the two it adds — `MIRI-CONSUMER-050` and `MIRI-CONSUMER-051`, bringing the family to seventeen:

- **Silence by default** (§4.1) — drive the binding with a `dependency.add` event naming the `bare` fixture, which
  ships no `agent-metadata/` at all, and assert the absent shape with no `findings` key.
- **Publisher-independent triggers** (§4.3) — drive the same event against `adversarial` and against `miri`, and
  assert the *trigger* behavior is identical. Every `.py` is byte-identical across the fixture variants, so any
  difference is metadata-attributable by construction.

Both are drivable with the existing fixture set. The second needs one new adversarial element: a document carrying a
field that attempts to force or amplify a trigger. That is a new attack case, not a new check family.

Because an event is a request and a response is an envelope, a conforming binding is testable **with no host at
all**: feed it an event, read the envelope. The goldens are therefore event/envelope pairs authored from this
specification rather than captured from any implementation — which is what keeps a binding's author from also being
the author of its acceptance criteria.
