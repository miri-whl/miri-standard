# Production Map

*Specification Version: 0.5.0-draft*
*Status: Draft*
*Created: 2026*

## Abstract

The [Consumption Map](../consumption/consumption-map.md) gives a consumer an ordered model: six tasks, each a
sequence of read-steps, each step labelled with the vehicle that supplies it. The producer side has a
[checklist](linter-checklist.md) — forty numbered checks in six categories, scored additively — and no ordered model
at all. Nothing says what an author does first, what depends on what, or which obligations cannot be evaluated yet.

That asymmetry was reported by an implementation team building both halves: *"the consumer side was straightforward
because the Map told us the order; the author side we had to invent an order for, and nothing checks whether we
invented a good one."*

This document is the minimal counterpart they asked for — **the dependency order among the documents, and which must
exist before which can be verified**. It is not a second checklist. Every ordering below is *derived from an existing
check*, and each stage names the checks that impose it; a stage with no check behind it would be advice, and advice
does not belong in a specification.

## Table of Contents

1. [What This Is Not](#1-what-this-is-not)
2. [The Stages](#2-the-stages)
3. [What Cannot Be Verified Yet](#3-what-cannot-be-verified-yet)
4. [The Provisional Document](#4-the-provisional-document)

## 1. What This Is Not

**It is not a new conformance surface.** No check scores an author on following this order. Two authors who arrive at
the same artifact by different routes are equally conformant, because the checklist grades the artifact and not the
process. What this map removes is the need to *discover* the order by hitting a check that cannot pass yet.

**It is not the checklist reordered.** The checklist is organized by category — identity, metadata, deprecation — which
is the right shape for scoring and the wrong shape for building. A category groups obligations that are *similar*; a
stage groups obligations that are *ready at the same time*.

## 2. The Stages

Each stage lists what must be settled, and the checks that make it a dependency rather than a preference.

### Stage 0 — The distribution decides its own identity

**Settled:** the distribution name and version in `.dist-info/METADATA`.

Every document that carries a version or an identity is checked against this file, so nothing downstream can be
correct until it is. `MIRI-PY-019` requires `identity.purl` to match `METADATA` exactly; `MIRI-PY-012` requires
`sdk_version` in *every* metadata file to equal the wheel version; `MIRI-PY-003` requires that version to parse under
the canonical scheme.

An author who generates metadata before the version is settled generates metadata that is wrong in a way three
separate checks will report.

### Stage 1 — Source-level declarations

**Settled:** PEP 702 `@deprecated` markers on any interface being retired.

These live in the source and are the *input* to a later document, not an output of one. `MIRI-PY-028` requires every
interface listed as deprecated to carry a marker, and `MIRI-PY-029` requires every marker to appear in the
migration guide — a two-way obligation that can only be satisfied if the markers exist first.

### Stage 2 — The surface

**Settled:** `sdk-manifest.json`, the public API index.

It depends only on the source and Stage 0's version (`MIRI-PY-007`, `MIRI-PY-012`), and **the migration guide depends
on it**: `MIRI-PY-031` requires every `deprecations[].replacement` to name an interface present in the *new*
manifest. Generating the guide first means writing replacements that cannot yet be checked.

### Stage 3 — Identity and history

**Settled:** `lifecycle.json`, then `migration-guide.json`.

`lifecycle.json` needs Stage 0 only (`MIRI-PY-018`, `MIRI-PY-019`, `MIRI-PY-021`).

`migration-guide.json` is the most constrained document in the standard, and is last for that reason. It needs
Stage 1's markers (`MIRI-PY-028`, `MIRI-PY-029`), Stage 2's manifest (`MIRI-PY-031`), Stage 0's version
(`MIRI-PY-032`, which requires every `removal_version` to exceed it) — and, for two of its obligations, a previous
release that may not exist (§3).

### Stage 4 — Views over the surface

**Settled:** `usage-patterns.json`, `api-graph.json`.

Both describe the surface Stage 2 declared, and **neither is depended upon by any other document** — no check
couples them to one. They are last in dependency order and may be generated in either order, or in parallel. An
author blocked here is not blocked on anything else.

## 3. What Cannot Be Verified Yet

Two checks require a **previous release** and are therefore not evaluable on a project's first one:
`MIRI-PY-030` (every public interface removed since the prior release was listed as deprecated in an earlier one)
and `MIRI-PY-034` (deprecated interfaces survive at least two releases before removal).

A linter without access to a prior release **MUST skip these and report the skip** with the reason
`previous_release_unavailable`, never pass them. Under the scoring model a forfeited check leaves both the numerator
and the denominator, so a first release is scored over what could actually be evaluated. **A first release cannot
score 100 on a suite that includes them and should not appear to.**

Four further checks require `execution` (`MIRI-PY-015`, `035`, `036`, `040`) and four require `network`
(`MIRI-PY-005`, `009`, `026`, `027`). Those are capability gates rather than ordering constraints — they do not
change what an author builds first — but an author choosing when to run a linter should know that a sandbox with
neither capability evaluates thirty of the forty checks.

## 4. The Provisional Document

`test-patterns.json` appears in no stage above, because **no producer check requires it, gates it, or reads it**.
It has a schema and nothing else, and the Discovery Contract marks it provisional for exactly that reason.

It is named here rather than omitted, because its absence from this map is the fact worth knowing: an author has no
obligation to produce it, and a consumer nevertheless has obligations that reference it
([Consumer Conformance](../consumption/consumer-conformance.md) `MIRI-CONSUMER-020`, `MIRI-CONSUMER-041`). That
asymmetry is recorded in those checks — `041` is conditional and scores only where a double is declared — but the
underlying gap is a producer specification that does not exist yet, and this document is where a reader should
expect to find it once it does.
