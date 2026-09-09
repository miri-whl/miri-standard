# Agent Integration Contract

*Specification Version: 0.5.0-draft*
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

Seven triggers, each named for the **observable action** rather than the intention behind it. An intention is not
observable and cannot be a trigger.

Six of them are one-per-map-task. `package.replaced` is the exception and routes to two tasks, because a replaced
artifact raises two independent questions — *what is the surface now* and *may it still be trusted* — and answering
one does not answer the other.

| Trigger (`kind`) | Fires when | Map task | Level |
|---|---|---|---|
| `dependency.add` | a dependency is about to be added | [§3.5](consumption-map.md) security and trust | SHOULD † |
| `dependency.version_change` | a dependency's version is about to change | [§3.3](consumption-map.md) upgrading | REQUIRED |
| `package.replaced` | an installed artifact is replaced **without its version changing** | [§3.1](consumption-map.md) first use *and* [§3.5](consumption-map.md) security and trust | SHOULD |
| `package.first_reference` | a package not yet used in this session is first referenced | [§3.1](consumption-map.md) first use | SHOULD |
| `integration.begin` | new code is about to be written against a package | [§3.2](consumption-map.md) scaffolding | SHOULD |
| `runtime.error` | an error naming an installed package is observed | [§3.4](consumption-map.md) diagnosing | SHOULD |
| `test.author` | a test touching a package is about to be written | [§3.6](consumption-map.md) tests | SHOULD |

**`package.replaced` reads both of its tasks, and the order matters.** Take [Map §3.1](consumption-map.md) first —
`list`, then `patterns`, then the surface — because the question *what is here now* has to be answered before any
judgment about it means anything. Then [Map §3.5](consumption-map.md), because the artifact is new bytes and the
previous verdict was about the old ones.

That second half is a prohibition, not just a read: **a consumer MUST NOT carry a trust determination across a
`package.replaced` event.** "This package was checked and is fine" is a claim about bytes and does not survive the
bytes changing, and `identity.purl` will not have moved
([Lifecycle and Security Metadata §9.6](../python/lifecycle-security-metadata.md)).

Two things this trigger is **not**. It is not a verification: where no attestation is present the standard binds
nothing about an artifact's contents, so re-reading a hostile artifact yields fresher hostile metadata and a consumer
MUST NOT present the re-read as a check having passed. And it is not a diff — the event says the artifact was
replaced, never what changed. A consumer that read the surface earlier in the session holds that comparison itself;
the contract stays stateless and does not pretend to remember.

The frequency is the design constraint. A maintainer developing a wheel locally reinstalls at the same version many
times an hour, because bumping a version on every edit is not a thing anyone does. So this trigger fires constantly
and must be **silent by default** — §4.1's absent envelope for every replacement that changed nothing a consumer had
cached. Firing is host-observed and unconditional; whether there are `findings` is metadata-determined (§4.3). Without
that separation this kind would be a context tax and a user would disable it, which is the failure §4.1 describes as
reachable through its own remedy.

The set is **closed**. A binding MUST NOT invent an eighth kind, for the same reason the servable set and the error
codes are closed: an open vocabulary is one every binding extends differently, and two bindings that disagree about
what an event *is* do not interoperate. Extending it is a change to this document and to the `kind` enum in
[`agent-event-v1.json`](../../schemas/agent-event-v1.json), which is vendored downstream — not something a binding
does locally.

† **`dependency.add` was REQUIRED in 0.4.0 and is not any more, because it cannot do its job yet.** At the moment
a dependency is added it is not installed, so it ships nothing a local surface can read: no `agent-metadata/`, no
`lifecycle.json`, no successor whose namespace could be checked. [Map §3.5](consumption-map.md)'s read-order has no
subject, and the trigger
correctly finds nothing every time — for exactly the case that motivated requiring it. Requiring a kind that is
structurally silent buys a conformance obligation and no safety.

It becomes REQUIRED when a **registry-side surface** exists, which the Discovery Contract does not define today. The
kind stays in the vocabulary at SHOULD rather than being removed, because a binding that observes an install (as
opposed to a manifest edit) *can* answer it, and because removing it would lose the place where that future surface
plugs in. This was found by an implementer building the binding and reporting that the trigger fired correctly and
found nothing.

**One kind is REQUIRED** — `dependency.version_change` — because it is the case where the change is both observable
and *checkable*: the old version is installed, so there is metadata to read, and the decision is still reversible.
Its findings are actionable only before the decision they inform becomes expensive to reverse — a migration guide is
worthless after the upgrade, and a
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
- **One observable action produces one event**, carrying one subject. Where an action names several packages —
  `pip install a b c`, a manifest edit adding three requirements — a binding emits one event **per package** but
  coalesces its *output*, so the caller sees one report about one decision. Three notifications for one install is
  three interruptions for a single choice, and under §4.1 two of them would be silence, which the caller has no way
  to associate with the third. Settled this way rather than by adding a plural `subjects` because a subject is what
  an event is *about*, and an event about three packages is about three things; the coalescing belongs in the host
  adapter, where the rest of the presentation already lives (§4.1).
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

The shape is schema-enforced by [`agent-findings-v1.json`](../../schemas/agent-findings-v1.json), which **carries
the envelope's rules verbatim** rather than restating them — `make consistency` fails if any of them drifts, so the
"no new response format" claim above is enforced rather than asserted. On top of them it closes `task` to the six
map sections and `level` to `must`/`should`, couples payload and absence in both directions, requires any
successful response to state `present`, and denies the host-control shapes §4.4 governs.

Three consequences are worth stating. An empty `findings` array is **rejected**, so a binding cannot satisfy §4.1 by
emitting one. A publisher's `priority: "critical"` cannot reach `level` even if a consumer passed it through
unexamined. And a response carrying `findings` must assert `present: true`, so a caller branching on `ok`/`present`
can never take neither branch.

**What the schema does not enforce, stated in full rather than by example**, because naming one gap implies the rest
are covered: that `level` was *derived* from the profile rather than copied; that `reason` carries no publisher
bytes; that a consumer does not branch on `reason`; that `source` names a genuinely served document; that `quote`
is bytes actually present in it; that `task` is the section that really produced the finding; and that the *number*
of findings is publisher-independent (§4.3 names count as trigger behavior, and no `maxItems` expresses it). These
are behavioral. `MIRI-CONSUMER-051` and the `E3` golden cover the first; `make validate-fixtures` now checks
`source`, `quote` and `level` against ground truth for every golden; the rest are unenforced today and are listed
here so a reader does not assume otherwise.

One limit of that golden gate is worth naming in the same spirit. It verifies a `quote` is a span of the field the
golden names, which catches a quote drawn from the wrong document or the wrong field. It cannot decide whether the
span is the *right* span: a benign prefix of an injected string is a genuine span of the same field and would pass
while carrying none of the evidence its finding claims. That is a reviewer's judgment, recorded as each golden's
required `why_this_span`, and not something the gate checks.

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

**The contract response and what a host emits are two layers, and §4.1 governs only the first.** A trigger's
*answer* is the absent envelope — that is what a golden asserts against, and what makes a binding testable with no
host at all (§7). What a **host adapter** does with an absent envelope is the binding document's business, and for
most hosts the right answer is to emit nothing at all.

That distinction is not a technicality. In Claude Code a hook's stdout enters the agent's context, so an adapter
that printed the absent envelope on every manifest edit would be announcing *checked, nothing found* in JSON —
which is precisely the context tax this section forbids, arrived at by obeying its letter. The host's own mechanism
for silence is exit 0 with no output. A conforming Claude Code adapter therefore receives the absent envelope from
the contract layer and emits nothing (§6.3).

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

*Trigger behavior* is the decidable part, and it is **whether the read happens** — never what the read finds. A
trigger fires because the host observed a change: a requirement was added, a version specifier moved. That
observation belongs to the host, and no shipped field participates in it. What the trigger reports once it has
fired is derived from the metadata, because that is the entire function.

So three things a publisher MUST NOT influence: **whether** the trigger reads at all; **which** `kind` was
reported; and **what `level`** each finding carries.

And two it necessarily does influence, legitimately: **whether** the response carries `findings`, and **how many**.
A package declaring a namespace-divergent successor produces a finding; a clean package produces none; a package
with two problems produces two.

An earlier version of this section listed those last two among the forbidden set. That made the rule
**unsatisfiable**: every finding is derived from a shipped field, so a consumer obeying it literally could never
report anything, and `MIRI-CONSUMER-051` fired on the behavior the `E3` golden mandates. The error was treating the
*outcome of the read* as though it were the *decision to read*. It is recorded rather than quietly corrected
because the two are easy to conflate and the conflation is invisible until someone tries to implement both.

**The evidence that a trigger fired is the absent envelope.** §4.1 already requires a trigger that reads and finds
nothing to answer with `ok: true`, `present: false` and a `reason` rather than staying silent — and that is what
makes this clause observable. Drive a consumer against a package carrying an attention bid and against a clean one:
both must produce a *response*. One that produces findings for the first and **nothing at all** for the second did
not read the second; it was summoned. **Silence is the violation, not the absence of findings.**

The *content* of a finding — its `summary`, its `quote`, the purl it names — is derived from the metadata by
design, and is governed separately below.

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
| `package.replaced` | `PostToolUse`, matcher `Bash` | the command installed a distribution that was already installed, and the version afterwards equals the version before |
| `runtime.error` | `PostToolUse`, matcher `Bash` | command output contains a traceback naming an installed package |
| `test.author` | `PreToolUse`, matcher `Edit\|Write` | the target path matches the project's test discovery configuration |

A manifest carries **distribution** names, so this binding emits `subject.package_kind: "distribution"` and the
name exactly as written. It does not attempt a distribution-to-import join, because the mapping lives in the
installed distribution's own metadata and `dependency.add` fires for a package that is not installed. The consumer
performs the join where it can and reports honestly where it cannot.

A **dependency manifest** is a file this binding recognizes as declaring the project's dependencies. For Python that
is `pyproject.toml`, `requirements*.txt`, `setup.cfg`, `setup.py`, `Pipfile`, and `environment.yml`. The list is
this *binding's*, not the contract's — another host or ecosystem will have a different one — and a binding MUST
publish its list rather than leaving it to be inferred, because a manifest the binding does not recognize is a
`dependency.add` that silently never fires.

The REQUIRED kind and the `dependency.add` SHOULD are both carried by `PreToolUse` on the edit tools, which is the only
moment in this host at which a
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
the two it adds — `MIRI-CONSUMER-050` and `MIRI-CONSUMER-051`, bringing the family to seventeen — and `MIRI-CONSUMER-052`
with the `package.replaced` trigger, bringing it to eighteen:

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

They are the `E*` files in [`examples/fixtures/expected/`](../../examples/fixtures/expected/), and every event and
every response in them is validated against `agent-event-v1` and `agent-findings-v1` by `make validate-fixtures`. A
golden that does not itself validate is worse than no golden, because it hands an implementer a target the schema
will reject.

| Trace | Clause | What it pins |
|---|---|---|
| `E1` | §4.1 | Silence is the absent shape — and at the host layer, no output at all |
| `E2` | §4.6 | The worked example end to end: trigger → task → operations → finding |
| `E3` | §4.3 | The same event against both arms; the trigger does not move |
| `E4` | [Map §3.3](consumption-map.md) | The redirect reached through `migration-guide.json` rather than `lifecycle.json` |
| `E5` | [Map §3.4](consumption-map.md) | The only `after`-phase trigger, against a document that tries to instruct |
| `E6` | [Map §3.6](consumption-map.md) | The one trace whose subject is the **conforming** arm |
| `E7` | §4.2, §4.4 | The host-boundary rules an envelope alone cannot express |
| `E8` | §5 item 3, §6.2 | The kinds this binding omits rather than approximates |

`E6` is the one to notice when reading the set: every other trace drives the adversarial arm and asks whether the
consumer *resists* what the metadata claims. `E6` drives the conforming arm and asks whether it *uses* what the
metadata declares. A suite made entirely of adversarial traces cannot tell a careful consumer from an inert one —
which is the same defect `MIRI-CONSUMER-041` itself carried until 0.5.0.

`E3` is what makes the trigger-forcing case discriminating, and the discriminator is **the absent envelope versus
silence** rather than findings versus no findings. `A13` alone asserts only that output does not echo the bid, which
a consumer that never reads satisfies trivially. `E3` requires a *response* on both arms: findings where the bid is,
and §4.1's absent envelope where it is not. A consumer that never reads fails the first; one that reads only when
summoned produces nothing at all on the second, and silence is the tell.

An earlier draft claimed a bid-reading consumer "fails on count, on level, or on the regex". It would not — reading
the bid to decide whether to look, then reporting what it finds, is byte-identical to correct behavior on both arms.
That claim was false because §4.3 named the wrong observable, and correcting the clause is what made this pair
discriminating.
