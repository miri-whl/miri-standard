# Changelog

All notable changes to the Miri Standard are recorded here.

Versions follow the policy in [standards/README.md](standards/README.md#versioning): a **major** version marks a
breaking change, a **minor** version a backward-compatible addition, and a **patch** version bug fixes and
clarifications only. That policy is a contract with implementers, and it is worth keeping strictly: a reader
should be able to see `0.3.1` and know it contains no additions without having to check.

## 0.3.1 — 2026-09-01

Bug fixes and clarifications. **No additions to the standard.** Every change either corrects something that was
wrong or makes an existing rule mechanically checkable.

Four of the six defects below were found by the miri-py team building an implementation against the text, and one
by scoring a real CLI. None was reachable by re-reading our own documents, which is the point worth recording.

### Fixed

- **`MIRI-SURFACE-012` required surfaces to refuse documents that six goldens require them to serve.** A clause
  added during 0.3's review demanded `METADATA_UNREADABLE` for any document that parses but fails its schema,
  while the adversarial fixtures expect those same documents served. Ten of the fifteen consumer checks are
  driven *through* the surface, so enforcing it would have disabled most of the consumer profile. The check is
  now scoped to readability, which is what its own examples, its rationale, and §3.2's verbatim rule already
  said. Reported by the miri-py team.
- **All 33 consumption checks advertised a `urls.html` that returns 404.** Linter reports link findings to that
  address, so every consumption finding pointed at a missing page. The 83 producer checks were correct; the
  consumption suite copied the wrong pattern when it was authored.
- **`cli-describe-v1.json` forbade `advisory_coverage`, which `MIRI-CLI-022` requires.** The schema closes
  `additionalProperties` and never declared the field, so a CLI doing what the standard tells it failed the
  standard's own schema. Not hypothetical: arghos had been failing validation since adopting it.
- **`schema_version` was unconstrained in three schemas, and three surfaces had diverged.** Two emitted `"1.0"`,
  one `"1"`, and all three validated. The integer-string convention lived only in prose and examples. Now pinned
  to `^[0-9]+$` in `cli-describe-v1`, `lint-report-v1` and `discovery-envelope-v1`. The `lint-report` pin matters
  most: it governs the report every `miri score` emits.
- **Five check citations pointed at sections that do not exist, or at the wrong one.** `MIRI-CLI-014` and
  `MIRI-CLI-034` cited a section with no such number; `MIRI-PY-019` used a notation that reads as a subsection;
  and `MIRI-CLI-013`, a check about the general error envelope, cited only §6 *Deprecation Metadata*.
- **The `MIRI-CONSUMER-032` namespace rule failed to detect the attack it exists to catch.** PyPI has no
  namespace component, so `pkg:pypi/a` redirecting to `pkg:pypi/b` compared as the same namespace. The
  comparison now falls back to the PEP 503-normalized package name where the type has no namespace.

### Verification made mechanical

Every gate below is new, and each exists because a defect of its exact shape shipped. The standard has four kinds
of normative artifact — check `fires_when`, spec prose, schemas, and goldens — and each pair that can disagree now
has a cross-check.

- **`tools/check_consistency.py`** — count claims against what is enumerated, sets declared complete against every
  member used, local section references, list numbering, table integrity, and check-demanded fields against every
  schema property. That last sweep is what found `advisory_coverage`.
- **`tools/check_references.py`** — gates that every check's spec citation resolves to a real document and
  section; **reports** the semantic half as a check-to-section list for a person. The split is deliberate: a
  falsely confident gate is worse than none, because nobody looks behind a green tick.
- **`tools/validate_fixtures.py`** — gains a check-versus-golden cross-check, so no check can demand refusing a
  document the goldens require served.
- **These validators had never run in CI.** All of them, plus the fixture invariants, gated nothing until this
  release. That was worth more than any single defect they now catch.

### Contributed

- **`schemas/discovery-envelope-v1.json`** and **`tools/validate_envelope_schema.py`**, from the miri-py
  implementation team, derived from a working surface rather than from this specification a second time. The
  envelope was the one normative wire format with no schema: every `MIRI-SURFACE` check validated a shape that
  existed only in prose.

  *Present on `main` but **not** part of the 0.3.1 release surface.* A schema is a backward-compatible addition,
  which makes it 0.4 material by the policy above, and the policy is kept rather than bent.

## 0.3.0 — 2026-08-28

The consumption suite: the half of the standard that says how an artifact is **read**. Versions 0.1 and 0.2
specified what an artifact ships; this specifies how an agent consumes it, and what a conformant consumer and a
conformant metadata surface are.

### Added

- **[Discovery Contract](standards/consumption/discovery-contract.md)** — the transport-agnostic wire contract.
  Eight operations in three kinds, the surface-owned envelope, absence-versus-error, caps and continuation, and
  MCP and loopback bindings.

  The central mechanism is that publisher bytes nest under a payload key, so a hostile package writing
  `ok: false` into its own document cannot forge a served, absent or failed signal. The bytes are still relayed
  intact — the surface does not edit what a publisher wrote. They are one level down, where they are data rather
  than signal.

- **[Consumption Map](standards/consumption/consumption-map.md)** — six tasks, each a read-order plus a set of
  prohibitions, with a vehicle label recording what a consumer must possess to perform each step.
- **[Consumer Conformance](standards/consumption/consumer-conformance.md)** — 15 `MIRI-CONSUMER` checks. A
  consumer is *driven*, not inspected, so every check is written against observable output.
- **[Surface Conformance](standards/consumption/surface-conformance.md)** — 18 `MIRI-SURFACE` checks in six
  categories, ordered as the path a request takes through a surface.
- **Fixtures** — ten variants built from one template, with every `.py` verified byte-identical across the
  source-sharing ones, so any difference in a consumer's behavior is attributable to the metadata and nothing
  else. Fifteen goldens covering attacks A1–A12.
- **The site renders the specifications**, with diagrams, sticky outlines, and per-target check pages for all
  four targets.

### Changed

- **Not-applicable is not a pass.** A conditional check whose condition does not apply is excluded from both the
  numerator and the denominator, rather than credited. Under the old model a CLI could earn 20 points for never
  deprecating anything.
- **Conformance is a gate, not a band.** A failing MUST makes an artifact non-conforming and no grade is
  reported — only the score, capped, to show distance.
