# Miri Standard: Surface Conformance (Consumption)

*Specification Version: 0.3-draft*
*Status: Draft*
*Created: 2026*

## Abstract

The [Discovery Contract](discovery-contract.md) places obligations on two programs. The
[Consumer Conformance](consumer-conformance.md) profile numbers the ones that bind a **consumer** and states plainly
that it does not score the rest. This document is that rest: sixteen checks, `MIRI-SURFACE-001` through
`MIRI-SURFACE-051`, weighted to 100, defining what a conformant **metadata-query surface** is.

Without it the contract's most load-bearing guarantees — that the envelope cannot be forged, that absence is
distinguishable from failure, that discovery never executes an unvetted package — are normative prose with nothing
verifying them. A reference implementation could regress on every one and no check in this standard would fire.

## Table of Contents

1. [What This Document Is](#1-what-this-document-is)
2. [The Verification Model](#2-the-verification-model)
3. [Scoring Model](#3-scoring-model)
4. [The Checks](#4-the-checks)
5. [Why These Are Not Consumer Checks](#5-why-these-are-not-consumer-checks)
6. [Check Definitions](#6-check-definitions)

---

## 1. What This Document Is

A **surface** is any program that answers the [Discovery Contract §3](discovery-contract.md) operations: the MCP
context server that is the contract's first binding, and any future binding of the same operations over a different
transport. It sits between an installed environment and a consumer, and its job is narrow — read metadata, wrap it,
relay it, and never do anything else.

That narrowness is the point. Most of what this profile checks is the surface **not** doing something: not executing
the package it is describing, not fetching what the package's metadata points at, not merging publisher bytes into
its own namespace, not serving a document outside a closed set, not repairing what it could not parse.

## 2. The Verification Model

A surface, unlike a consumer, has a **specified output**. Every operation's response shape is fixed by §4 of the
contract, so conformance can be checked by issuing a request and inspecting the envelope that comes back — no
judgment about phrasing, no assertion on natural language.

Verification is a **driven suite**, like the consumer profile, but the assertions are exact:

1. Install a fixture from [`examples/fixtures/`](../../examples/fixtures/) into the environment the surface serves.
2. Issue a request — including deliberately hostile ones, which is what a request-trace fixture is for.
3. Assert on the returned envelope against the golden in `examples/fixtures/expected/`.

This is the profile where goldens do the most work: a consumer assertion is necessarily partly about wording, while a
surface assertion is a structural comparison. Where a check below says a field MUST be present or absent, that is
mechanically decidable from one response.

## 3. Scoring Model

Identical to the sibling profiles, so one grading vocabulary spans the standard:

- **Score** = Σ weights of passing checks, over the *effective denominator* (see forfeits below).
- **Level**: **M** (MUST — required for conformance) or **S** (SHOULD — quality signal).
- **Conformance is a gate, not a band.** A program failing any **M** check is **non-conforming**, and a
  non-conforming result carries **no grade** — only the score, capped at 74, to show distance. Grades describe
  conforming programs only.
- **Grade bands (conforming programs only)**: 90–100 **Gold** · 75–89 **Silver** · 50–74 **Bronze**.

Because nearly all weight in this profile sits on MUST checks, a conforming program will in practice land in Gold
and the lower bands will rarely be occupied. That is intended: the bands exist so the vocabulary matches the
producer checklists, not because a conforming consumer is expected to score badly. A profile whose SHOULD weight
grows will occupy them naturally.

**Forfeits.** A check whose fixture cannot be driven is **forfeited and reported, never silently passed**. A
forfeited check leaves **both** the numerator and the denominator: the score is computed over what was actually
exercised, so forfeiting cannot inflate or deflate it. The report MUST carry the forfeited count and the effective
denominator beside the score, and a forfeited **M** check means **conformance is undetermined** — reported as such,
never as conforming and never as a failure.

## 4. The Checks

Sixteen checks, weights summing to 100. IDs are stable and are never renumbered.

### A. Envelope Integrity (20 points)

The surface owns the top level of every response. This is the category the whole anti-forgery argument rests on.

| ID | Level | Check | Weight | Case |
|---|---|---|---|---|
| MIRI-SURFACE-001 | M | Stamps `schema_version` on every response | 6 | any |
| MIRI-SURFACE-002 | M | Nests the payload; never merges publisher bytes into the envelope | 8 | `adversarial` (A1/A2) |
| MIRI-SURFACE-003 | M | Emits only reserved keys at the top level | 6 | any |

### B. Absence and Error (22 points)

The discrimination the contract calls its single most consequential clause.

| ID | Level | Check | Weight | Case |
|---|---|---|---|---|
| MIRI-SURFACE-010 | M | Reports absence as `ok: true, present: false` — never as an error | 8 | `bare` |
| MIRI-SURFACE-011 | M | Reports failure as `ok: false` with a coded `error` object | 7 | request trace |
| MIRI-SURFACE-012 | M | Reports an document it could not parse as `METADATA_UNREADABLE`, never absent or repaired | 7 | `malformed` |

### C. Boundaries (24 points)

What the surface will and will not do. Every check here is a refusal.

| ID | Level | Check | Weight | Case |
|---|---|---|---|---|
| MIRI-SURFACE-020 | M | Serves only the closed servable set; refuses anything else | 8 | request trace |
| MIRI-SURFACE-021 | M | Confines the resolved path; rejects symlinks and traversal | 8 | `symlinked` |
| MIRI-SURFACE-022 | M | Discovers import-free; executes nothing and fetches nothing | 8 | import canary |

### D. Bounded Answers (16 points)

| ID | Level | Check | Weight | Case |
|---|---|---|---|---|
| MIRI-SURFACE-030 | M | Declares and enforces its caps, and sets `truncated` when it drops content | 6 | `adversarial` (A4) |
| MIRI-SURFACE-031 | S | Orders entries stably and offers cursor continuation | 4 | `adversarial` (A4) |
| MIRI-SURFACE-032 | M | Distinguishes an absent `api-index` from an empty one | 6 | `bare`, `miri` |

### E. Provenance and Identity (11 points)

| ID | Level | Check | Weight | Case |
|---|---|---|---|---|
| MIRI-SURFACE-040 | M | Derives `purl` from the installed distribution; never reads it from a document | 6 | identity skew |
| MIRI-SURFACE-041 | M | Emits one row per import package; errors rather than picking among ambiguous ones | 5 | multi-distribution |

### F. Binding (7 points)

| ID | Level | Check | Weight | Case |
|---|---|---|---|---|
| MIRI-SURFACE-050 | M | Advertises the surface version at the normative path | 4 | any |
| MIRI-SURFACE-051 | M | Carries absence and error as tool results, never as protocol errors | 3 | `bare`, request trace |

### Category Summary

| Category | Checks | Points |
|---|---|---|
| A. Envelope Integrity | 3 | 20 |
| B. Absence and Error | 3 | 22 |
| C. Boundaries | 3 | 24 |
| D. Bounded Answers | 3 | 16 |
| E. Provenance and Identity | 2 | 11 |
| F. Binding | 2 | 7 |
| **Total** | **16** | **100** |

Several cases above name fixtures that do not exist yet — the `malformed` variant, the `symlinked` document, the
import canary, the identity-skew document, the multi-distribution pair, and the request-trace set. Those checks are
**defined but not yet scorable**, and a report MUST forfeit them rather than crediting them. Building them is the
remaining fixture work, and this profile is what gives that work something to be evidence *for*.

## 5. Why These Are Not Consumer Checks

It would be simpler to keep one profile. The split exists because the two programs fail differently, and a single
score would obscure which one is broken.

A consumer emits no responses, so it cannot be held to the shape of one. A surface makes no decisions about what to
call, so it cannot be held to the judgment a consumer exercises. Scoring them together would produce a number that
answers neither "can I trust this server" nor "can I trust this agent" — and when it dropped, would not say which.

The division follows the actor table in [Consumer Conformance §4](consumer-conformance.md): every obligation marked
there as binding the **Surface** is numbered here, and every category in §4 appears in that table. The one obligation
named on both sides is absence — a surface must *signal* it correctly and a consumer must *report* it correctly,
which are different failures that can occur independently. That table was written as a declared gap; this document
closes it.

## 6. Check Definitions

The authoritative definition of each check is its YAML file in `standards/consumption/checks/`, governed by
`schemas/check-v1.json` with `target: surface`. The tables in §4 are the derived rendering: where the two disagree,
the YAML is correct.

Surface and consumer checks share a directory because they share a suite and a contract; they are separated by
`target`, and their weights sum to 100 independently.
