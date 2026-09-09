# Why the Standard Has a Consumption Half

Versions 0.1 and 0.2 specified what an artifact **ships**. From 0.3 the standard also specifies how an agent
**consumes** it — and this page is the argument for why that half had to exist. Per-release detail lives in the
[changelog](../CHANGELOG.md); the reasoning here does not change from one version to the next.

That is the whole of it. A package could score Gold and help no agent, because nothing in the standard said how the
metadata was supposed to reach a decision, what to read for a given task, or what it means to consume it correctly.
The consumption suite closes that loop with four documents, a fixture set, and thirty-six numbered checks.

## The documents

**Discovery Contract** — how metadata reaches an agent at the moment it is deciding what to call. Eight read-only
operations in three kinds: *retrieval* (`document`, with `lifecycle` and `migration-guide` shorthands), *derived
views* (`api-index`, `patterns`, `graph`), and *determination* (`list`, `resolve`). MCP is the first binding, not
the contract itself.

**Consumption Map** — what to read, per task, and in what order. Six tasks: first use, scaffolding an integration,
upgrading a dependency, diagnosing a runtime failure, answering a security question, and writing tests. Each carries
a read-order, prohibitions, and informative heuristics, and the three are deliberately graded differently.

**Consumer Conformance** — what a conformant consumer *is*: eighteen `MIRI-CONSUMER` checks weighted to 100.

## The idea that shaped everything

**The surface owns the envelope; the publisher owns the payload.**

Every response is a surface-authored envelope with the package's bytes nested inside it. The two never share a
namespace. That sounds like a formatting decision and is actually the security model: because a publisher cannot
write to the top level, a publisher cannot forge the signals a consumer branches on.

Those signals are two independent booleans — `ok` (did the surface serve the request?) and `present` (does the
document exist?). Keeping them separate is what makes **honest degradation** checkable at all. Without it, "this
package ships no lifecycle metadata" and "the lookup failed" are indistinguishable in a consumer's output, and so is
"I did not look."

## Consuming is not the same as inspecting

A producer check reads an artifact: a wheel is a fixed object and a linter opens it. A consumer is a program with
behavior and no file to inspect, so conformance here is established by **driving** it — install a fixture, run a
task, assert on what the consumer says and emits.

Two consequences are written into the profile rather than left implied. Only **observable** claims are checkable, so
every check is phrased as something a consumer must or must not say. And a check needs a fixture that exercises it,
because a check with no executable case passes vacuously.

## The fixtures

One trivial package built three ways — **identical source, different metadata**. The build script byte-compares
every source file across the variants and fails if any differ, so source identity is a verified property rather than
a convention: any difference a consumer shows between variants is attributable to metadata alone.

- **bare** — no metadata. The honest-degradation baseline.
- **miri** — conforming metadata. The comparison arm.
- **adversarial** — metadata that lies: forged envelope signals, symbols that do not exist, an index padded to hide a
  real method past the cap, injection text in fields the map routes a consumer to read, an empty advisory list posing
  as a clean bill of health, a link-local SSRF target, and a deprecation redirecting onto a package in a namespace
  the publisher does not own.

Two of those cases carry a **paired control**, which is the part worth borrowing. The redirect is paired with a
legitimate same-namespace migration, and a dynamically-served symbol is paired with a statically-defined one.
Without the controls, both checks are passable by a consumer that simply refuses to act — and refusing every
migration is not detecting an attack, just as reporting everything unverified is not caution.

## Presence, absence, and the difference between them

Two operations return evidence that is deliberately asymmetric, in opposite directions:

- `api-index` can **confirm a claim** and never refute one. It is capped and filtered, so a symbol missing from a
  response may simply have been dropped — which is exactly how a hostile package can hide a surface by padding.
- `resolve` can **confirm existence** and never refute it. It parses source without importing, so a surface built at
  runtime is invisible to it — `not-in-source` means *not defined statically*, never *does not exist*.

A consumer that collapses either asymmetry is wrong in a specific, predictable way, and the standard names both.

## What this version does not claim

Nothing here asserts that consuming this metadata improves agent outcomes. That is an empirical question with a
pre-registered experiment attached, and the specification deliberately stays on the mechanism side of it. The
specification makes
the experiment *possible* — it could not run without a defined consumption contract — but it does not anticipate the
result.

Two scope decisions are stated rather than left to be discovered: the contract answers only for the **installed**
version, so choosing a package before installing it and asking what breaks on a future upgrade are both out of scope
for 0.3; and several obligations bind the **surface** rather than the consumer, so the consumer profile does not
score them and says which those are. A Surface Conformance profile does not exist yet, and the standard says so.
