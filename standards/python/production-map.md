# Production Map

*Specification Version: 0.5.0-draft*
*Status: Draft*
*Created: 2026*

## Abstract

The [Consumption Map](../consumption/consumption-map.md) gives a consumer an ordered model of six tasks. Each task is
a sequence of read-steps, and each step is labelled with the vehicle that supplies it. The producer side has a
[checklist](linter-checklist.md) of 45 numbered check definitions in six categories, and 43 of them are active
(`MIRI-PY-010` and `MIRI-PY-016` are withdrawn). A wheel's score is the sum of the weights of its passing checks over
the weights of the checks that applied. Nothing on the producer side gives an ordered model. No document says what an
author does first, what depends on what, or which obligations cannot be evaluated yet.

An implementation team building both halves reported that asymmetry: *"the consumer side was straightforward
because the Map told us the order; the author side we had to invent an order for, and nothing checks whether we
invented a good one."*

This document is the minimal counterpart they asked for: **the dependency order among the documents, and which must
exist before which can be verified**. It is not a second checklist. Every ordering below is *derived from an existing
check*, and each stage names the checks that impose it. A stage with no check behind it would be advice, and a
specification carries no advice.

## Table of Contents

1. [What This Is Not](#1-what-this-is-not)
2. [The Stages](#2-the-stages)
3. [What Cannot Be Verified Yet](#3-what-cannot-be-verified-yet)
4. [The Provisional Document](#4-the-provisional-document)

## 1. What This Is Not

**It is not a new conformance surface.** No check scores an author on following this order. Two authors who arrive at
the same artifact by different routes are equally conformant, because the checklist grades the artifact and not
the process. This map removes the need to *discover* the order by hitting a check that cannot pass yet.

**It is not the checklist reordered.** The checklist is organized by category (identity, metadata, deprecation). That
shape suits scoring and does not suit building. A category groups obligations that are *similar*; a stage groups
obligations that are *ready at the same time*.

## 2. The Stages

Each stage lists what must be settled, and the checks that make it a dependency rather than a preference.

### Stage 0: The distribution decides its own identity

**Settled:** the distribution name and version in `.dist-info/METADATA`.

Every document that carries a version or an identity is checked against this file. Nothing downstream can be correct
until it is. `MIRI-PY-019` requires `identity.purl` to match `METADATA` exactly; `MIRI-PY-012` requires
`sdk_version` in *every* metadata file to equal the wheel version; `MIRI-PY-003` requires that version to parse under
the canonical scheme.

An author who generates metadata before the version is settled generates metadata that is wrong in a way three
separate checks will report.

### Stage 1: Source-level declarations

**Settled:** PEP 702 `@deprecated` markers on any interface being retired.

These live in the source and are the *input* to a later document rather than the output of one. `MIRI-PY-028`
requires every interface listed as deprecated to carry a marker, and `MIRI-PY-029` requires every marker to appear in
the migration guide. That two-way obligation can only be satisfied if the markers exist first.

### Stage 2: The surface

**Settled:** `sdk-manifest.json` (the public API index) and the precomputed code index that the manifest's
`code_index` field declares.

The manifest depends only on the source and Stage 0's version (`MIRI-PY-007`, `MIRI-PY-012`). **The migration guide
depends on it**: `MIRI-PY-031` requires every `deprecations[].replacement` to name an interface present in the
*new* manifest. Generating the guide first means writing replacements that cannot yet be checked.

The code index is built from the same source, and the manifest declares it. `MIRI-PY-045` fires when the wheel ships
no precomputed code index under `.dist-info/` and `sdk-manifest.json` carries no `code_index`. It also fires when
`code_index` names a path that is absent from the wheel or unlisted in RECORD, when `code_index.format` is outside the
closed set the schema declares, and when an index file under `.dist-info/` has no `code_index` pointer
([Wheel Extensions §5.5](miri-python-wheel-extensions.md)). The index and its declaration are settled together in
this stage. No other producer check reads the index.

### Stage 3: Identity and history

**Settled:** `lifecycle.json`, then `migration-guide.json`.

`lifecycle.json` needs Stage 0 only (`MIRI-PY-018`, `MIRI-PY-019`, `MIRI-PY-021`).

`migration-guide.json` is the most constrained document a wheel author produces, and it comes last in this stage for
that reason. It needs Stage 1's markers (`MIRI-PY-028`, `MIRI-PY-029`), Stage 2's manifest (`MIRI-PY-031`) and Stage
0's version (`MIRI-PY-032`). `MIRI-PY-032` requires every `removal_version` to exceed that version. For three of its
obligations (`MIRI-PY-009`, `030`, `034`) the guide also needs a previous release that may not exist (§3).

### Stage 4: Views over the surface

**Settled:** `usage-patterns.json`. (`api-graph.json` was withdrawn at 0.7.3; see Agent Metadata §4.5.)

`usage-patterns.json` describes the surface Stage 2 declared. It is last in dependency order, and no *metadata
document* is generated from it.

Two checks couple it to the rest of the wheel. One of `MIRI-PY-039`'s `fires_when` clauses is "A template references
a metadata file the wheel does not ship (e.g. cites migration-guide.json on a first release, or api-graph.json,
withdrawn at 0.7.3)". `MIRI-PY-036` checks the discovery functions against the whole of `agent-metadata/`. An author
who ships a template or a discovery function naming a Stage 4 document, and then does not generate it, fails both.

## 3. What Cannot Be Verified Yet

Four checks require a **previous release** and are therefore not evaluable on a project's first one:
`MIRI-PY-009` (`migration-guide.json` is present for any non-initial release and is not empty when the API measurably
changed), `MIRI-PY-030` (every public interface removed since the prior release was listed as deprecated in an earlier
one), `MIRI-PY-034` (deprecated interfaces survive at least two releases before removal) and `MIRI-PY-043` (every
interface in the measured API delta is named in the changelog's `releases[0]`).

A linter without access to a prior release **MUST skip these and report the skip** with the reason
`previous_release_unavailable`, never pass them. Under the scoring model a forfeited check leaves both the numerator
and the denominator ([checklist, Scoring Model](linter-checklist.md#scoring-model)). **A first release is scored over
the checks that could be evaluated, and on that basis it can reach 100 and Gold. Its report shows the smaller
effective denominator and the skipped checks.**

Four checks require `execution` (`MIRI-PY-015`, `035`, `036`, `040`) and four require `network` (`MIRI-PY-005`,
`009`, `026`, `027`). `MIRI-PY-009` also requires a previous release. These are capability gates rather than
ordering constraints, and they do not change what an author builds first. They matter to an author choosing when to
run a linter. Of the 43 active checks, a sandbox with neither capability evaluates 35. On a first release the same
sandbox also forfeits the three remaining `previous-release` checks (`030`, `034`, `043`) and evaluates 32.

## 4. The Provisional Document

`test-patterns.json` appears in no stage above, because **no producer check requires it, gates it, or reads it**.
It has a schema and nothing else, and the Discovery Contract marks it provisional for that reason.

This section names it because an author has no obligation to produce it, while a consumer has obligations that
reference it ([Consumer Conformance](../consumption/consumer-conformance.md) `MIRI-CONSUMER-020`,
`MIRI-CONSUMER-041`). Those checks account for the asymmetry: `041` is conditional and scores only where a double
is declared. The underlying gap is a producer specification that does not exist yet. When it exists, this document is
where a reader should expect to find it.
