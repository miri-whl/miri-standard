# Why the Standard Has a Consumption Half

Versions 0.1 and 0.2 specified what an artifact **ships**. From 0.3 the standard also specifies how an agent
**consumes** it. This page is the argument for that second half. Per-release detail lives in the
[changelog](../CHANGELOG.md), and the reasoning here does not change from one version to the next.

A package could score Gold and help no agent. Nothing in the standard said how the metadata was supposed to reach a
decision, what to read for a given task, or what it means to consume it correctly. Five documents, a fixture set and
thirty-six numbered checks now make correct consumption verifiable.

## The documents

**[Discovery Contract](../standards/consumption/discovery-contract.md):** how metadata reaches an agent at the moment
it is deciding what to call. It defines eight read-only operations in three kinds: *retrieval* (`document`, with
`lifecycle` and `migration-guide` shorthands), *derived views* (`api-index`, `patterns`, `graph`), and
*determination* (`list`, `resolve`). MCP is the first binding of the contract.

**[Consumption Map](../standards/consumption/consumption-map.md):** what to read for each task, and in what order.
It covers six tasks: first use, scaffolding an integration, upgrading a dependency, diagnosing a runtime failure,
answering a security question, and writing tests. Each task carries a read-order, prohibitions and informative
heuristics, and the three are graded differently on purpose.

**[Agent Integration Contract](../standards/consumption/agent-integration-contract.md):** when the reading starts.
It names the events that make an integration consult the metadata before an agent acts.

**[Consumer Conformance](../standards/consumption/consumer-conformance.md):** what a conformant consumer *is*,
verified by eighteen `MIRI-CONSUMER` checks weighted to 100.

**[Surface Conformance](../standards/consumption/surface-conformance.md):** what a conformant surface is, verified by
eighteen `MIRI-SURFACE` checks weighted to 100. These are the obligations a consumer cannot be held to, because the
surface is the program that serves the metadata.

## The idea that shaped everything

**The surface owns the envelope; the publisher owns the payload.**

Every response is a surface-authored envelope with the package's bytes nested inside it, and the two never share a
namespace. That rule is the security model. A publisher cannot write to the top level, and so a publisher cannot forge
the signals a consumer branches on.

Those signals are two independent booleans: `ok` (did the surface serve the request?) and `present` (does the
document exist?). Keeping them separate makes **honest degradation** checkable. Without it, "this package ships no
lifecycle metadata" and "the lookup failed" look the same in a consumer's output, and so does "I did not look."

## Consuming is not the same as inspecting

A producer check reads an artifact: a wheel is a fixed object and a linter opens it. A consumer is a program with
behavior and no file to inspect. Its conformance is established by **driving** it: install a fixture, run a task, and
assert on what the consumer says and emits.

The profile writes down two consequences of this. Only **observable** claims are checkable, and every check is
therefore phrased as something a consumer must or must not say. A check also needs a fixture that exercises it,
because a check with no executable case passes vacuously.

## The fixtures

The consumption fixtures are eleven builds of one trivial package. Nine of them have **identical source and different
metadata**, and the build script byte-compares every source file across those nine and fails if any differ. Any
difference a consumer shows between them comes from the metadata alone. Three are the base trio:

- **bare:** no metadata. The honest-degradation baseline.
- **miri:** conforming metadata. The comparison arm.
- **adversarial:** metadata that lies. It carries forged envelope signals, symbols that do not exist, an index padded
  to hide a real method past the cap, injection text in fields the map routes a consumer to read, an empty advisory
  list posing as a clean bill of health, a link-local SSRF target, and a deprecation redirecting onto a package in a
  namespace the publisher does not own.

The others each cover one case the trio cannot express: malformed documents, a spoofed identity, a symlink escape, a
replaced artifact at the same purl, and two distributions that share an import name. Two outliers differ in source on
purpose (a symbol served at runtime, and a module that fails on import), and the
[fixtures README](../examples/fixtures/README.md) lists all eleven.

Two of the attacks carry a **paired control**. The redirect is paired with a legitimate same-namespace migration, and
a dynamically served symbol is paired with a statically defined one. Without the controls, a consumer that refuses to
act would pass both checks. Refusing every migration does not detect an attack, and reporting everything as
unverified is not caution.

## Presence, absence, and the difference between them

Two operations return evidence that is asymmetric in opposite directions:

- `api-index` can **confirm a claim** and never refute one. It is capped and filtered, and a symbol missing from a
  response may have been dropped. A hostile package can hide part of its API this way, by padding the index.
- `resolve` can **confirm existence** and never refute it. It parses source without importing, and a surface built at
  runtime is invisible to it. `not-in-source` means *not defined statically*, never *does not exist*.

A consumer that collapses either asymmetry is wrong in a specific, predictable way, and the standard names both.

## What the standard does not claim

Nothing here asserts that consuming this metadata improves agent outcomes. That is an empirical question, and a
measurement study is planned. The specification defines the mechanism such a study needs, and the study could not run
without a defined consumption contract.

The contract also has two limits. It answers only for the **installed** version: choosing a package before installing
it, and asking what breaks on a future upgrade, are both out of scope. Several obligations bind the **surface** rather
than the consumer. The consumer profile does not score them, and Surface Conformance does.
