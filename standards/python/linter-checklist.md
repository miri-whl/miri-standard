# Miri Linter Checklist: Python Wheels

*Specification Version: 0.1-draft*
*Status: Draft*
*Created: 2026*

## Purpose

The explicit, numbered list of every check a Miri-conformance linter runs against a Python wheel, with the standard each check derives from and a scoring weight. Linter projects implement checks by number (`MIRI-PY-001` … `MIRI-PY-040`); the weights sum to exactly **100**, so a wheel's Miri score is simply the sum of the weights of its passing checks.

## Scoring Model

- **Score** = Σ weights of passing checks (0–100).
- **Level** column: **M** (MUST — required for conformance) or **S** (SHOULD — quality signal).
- A wheel with any failing **M** check is **non-conforming regardless of score**; its score is still reported, capped at 74, to show distance from conformance.
- Checks marked *conditional* (e.g. SBOM only when bundling non-Python components) score their full weight automatically when the condition does not apply.

**Grade bands**: 90–100 **Gold** (agent-native) · 75–89 **Silver** (agent-ready) · 50–74 **Bronze** (partially legible) · <50 non-conforming.

## The Checks

### A. Packaging Baseline (10 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-PY-001 | M | Wheel structure valid | `.dist-info/` with `METADATA`, `WHEEL`, `RECORD`; archive matches RECORD | [PEP 427](https://peps.python.org/pep-0427/) / [PEP 491](https://peps.python.org/pep-0491/) | 2 |
| MIRI-PY-002 | M | Core metadata valid | `METADATA` parses as Core Metadata 2.x; name normalized | [PEP 566](https://peps.python.org/pep-0566/) / [PEP 503](https://peps.python.org/pep-0503/) | 2 |
| MIRI-PY-003 | M | Version scheme valid | Version parses under the canonical scheme | [PEP 440](https://peps.python.org/pep-0440/) | 2 |
| MIRI-PY-004 | S | Declarative build config | `pyproject.toml` with `[project]` table drives the build | [PEP 621](https://peps.python.org/pep-0621/) / [PEP 517](https://peps.python.org/pep-0517/) | 2 |
| MIRI-PY-005 | S | Publish attestations | Release carries index-hosted attestations (provenance) | [PEP 740](https://peps.python.org/pep-0740/) | 2 |

### B. Agent Metadata Core (20 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-PY-006 | M | agent-metadata/ present | Directory exists in the package | [Miri Wheel Ext. §3.2](miri-wheel-extensions.md) | 2 |
| MIRI-PY-007 | M | sdk-manifest.json valid | Present and validates against schema | [Agent Metadata §4.1](agent-metadata-specification.md) / [schema](../../schemas/sdk-manifest-v1.json) | 4 |
| MIRI-PY-008 | M | usage-patterns.json valid | Present and validates against schema | [Agent Metadata §4.2](agent-metadata-specification.md) / [schema](../../schemas/usage-patterns-v1.json) | 3 |
| MIRI-PY-009 | M | migration-guide.json valid | Present for any non-initial release; validates against schema (*conditional*) | [Agent Metadata §4.3](agent-metadata-specification.md) / [schema](../../schemas/migration-guide-v1.json) | 3 |
| MIRI-PY-010 | S | api-graph.json valid | If present, validates against schema | [Agent Metadata §4.5](agent-metadata-specification.md) / [schema](../../schemas/api-graph-v1.json) | 1 |
| MIRI-PY-011 | M | Build-time generation | `generated_at` timestamps within the build window; not hand-edited afterward | [Agent Metadata §5](agent-metadata-specification.md) | 2 |
| MIRI-PY-012 | M | Version coherence | `sdk_version` in every metadata file equals the wheel version | [Agent Metadata §4.1](agent-metadata-specification.md) | 3 |
| MIRI-PY-013 | M | JSON hygiene | All metadata files parse as strict UTF-8 JSON (no NaN/Infinity, no comments) | RFC 8259 | 2 |

### C. Examples (10 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-PY-014 | M | Quickstart exists | `examples/quickstart.py` present | [Miri Wheel Ext. §5.1](miri-wheel-extensions.md) | 3 |
| MIRI-PY-015 | M | Examples runnable | Every example compiles; executes in sandbox (except external credentials) | [Miri Wheel Ext. §7.2.2](miri-wheel-extensions.md) | 3 |
| MIRI-PY-016 | M | Example index coherent | `AGENT_EXAMPLES.json` entries ↔ files on disk, both directions | [Miri Wheel Ext. §4.1](miri-wheel-extensions.md) | 2 |
| MIRI-PY-017 | S | Error handling shown | Examples demonstrate the package's error/exception handling | [Miri Wheel Ext. §7.2.2](miri-wheel-extensions.md) | 2 |

### D. Identity & Security (25 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-PY-018 | M | lifecycle.json valid | Present and validates against schema | [Lifecycle Spec §3](lifecycle-security-metadata.md) / [schema](../../schemas/lifecycle-v1.json) | 4 |
| MIRI-PY-019 | M | purl coherence | `identity.purl` name+version exactly match `METADATA` | [purl spec](https://github.com/package-url/purl-spec) / [Lifecycle §8.2](lifecycle-security-metadata.md) | 4 |
| MIRI-PY-020 | M | Distribution & registry declared | `distribution` set; `registry` a well-formed index URL | [Lifecycle §3.1](lifecycle-security-metadata.md) | 2 |
| MIRI-PY-021 | M | Advisory sources present | ≥1 entry in `advisory_sources`, valid type and URL | [Lifecycle §3.1](lifecycle-security-metadata.md) / [OSV schema](https://ossf.github.io/osv-schema/) | 3 |
| MIRI-PY-022 | M | Private-source rule | `distribution: private` does not rely solely on public OSV | [Lifecycle §5.1](lifecycle-security-metadata.md) | 3 |
| MIRI-PY-023 | M | Update check declared | `update_check` type/URL valid (PyPI JSON or PEP 700 index) | [Lifecycle §3.1](lifecycle-security-metadata.md) / [PEP 691](https://peps.python.org/pep-0691/)/[700](https://peps.python.org/pep-0700/) | 2 |
| MIRI-PY-024 | M | SBOM when bundling | Wheels with non-Python components carry `.dist-info/sboms/` (*conditional*; binary-extension detection triggers it) | [PEP 770](https://peps.python.org/pep-0770/) / [Lifecycle §3.2](lifecycle-security-metadata.md) | 4 |
| MIRI-PY-025 | S | SBOM purls resolvable | SBOM component purls are well-formed (*conditional*) | [PEP 770](https://peps.python.org/pep-0770/) / [purl spec](https://github.com/package-url/purl-spec) | 1 |
| MIRI-PY-026 | S | VEX well-formed | `vex` URL, if present, serves an OpenVEX/CycloneDX VEX document | [OpenVEX](https://github.com/openvex/spec) | 1 |
| MIRI-PY-027 | S | Security policy declared | `support.security_policy` present and resolvable | [Lifecycle §3.1](lifecycle-security-metadata.md) | 1 |

### E. Deprecation & Lifecycle Coherence (25 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-PY-028 | M | PEP 702 markers | Every interface listed as deprecated carries `@deprecated`; decorator message names replacement + removal version | [PEP 702](https://peps.python.org/pep-0702/) / [Lifecycle §6.1](lifecycle-security-metadata.md) | 4 |
| MIRI-PY-029 | M | Inventory derived | Every PEP 702 marker appears in `migration-guide.json` `deprecations` | [Lifecycle §6.2/§6.4-1](lifecycle-security-metadata.md) | 4 |
| MIRI-PY-030 | M | No silent removals | Every public interface removed since the prior release was listed in an earlier release's `deprecations` | [Lifecycle §6.4-2](lifecycle-security-metadata.md) | 5 |
| MIRI-PY-031 | M | Replacements resolve | Every `deprecations[].replacement` exists in the new `sdk-manifest.json` | [Lifecycle §6.4-3](lifecycle-security-metadata.md) | 3 |
| MIRI-PY-032 | M | Removal versions sane | Every `removal_version` is greater than the current release | [Lifecycle §6.4-3](lifecycle-security-metadata.md) / [PEP 440](https://peps.python.org/pep-0440/) | 2 |
| MIRI-PY-033 | M | Support status coherent | `support.status` in enum; `deprecated`/`eol` ⇒ `replacement` present | [Lifecycle §3.1](lifecycle-security-metadata.md) / [schema](../../schemas/lifecycle-v1.json) | 3 |
| MIRI-PY-034 | S | Grace period | Deprecated interfaces survive ≥2 releases before removal | [PEP 387](https://peps.python.org/pep-0387/) / [Lifecycle §6.1](lifecycle-security-metadata.md) | 2 |
| MIRI-PY-035 | S | Runtime warnings fire | Importing/calling deprecated interfaces emits `DeprecationWarning` | [PEP 565](https://peps.python.org/pep-0565/) | 2 |

### F. Discovery & Degradation (10 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-PY-036 | M | Discovery APIs work | Package-level discovery functions importable and return coherent data | [Miri Wheel Ext. §6](miri-wheel-extensions.md) | 3 |
| MIRI-PY-037 | S | Embedded docs present | `docs/` directory with API reference and troubleshooting | [Miri Wheel Ext. §5.3](miri-wheel-extensions.md) | 2 |
| MIRI-PY-038 | S | Templates coherent | `TEMPLATES.json` entries ↔ template files; placeholders documented | [Miri Wheel Ext. §4.4](miri-wheel-extensions.md) | 2 |
| MIRI-PY-039 | S | Prompt templates valid | `prompt-templates.md`, if present, follows the specified structure | [Agent Metadata §4.4](agent-metadata-specification.md) | 1 |
| MIRI-PY-040 | M | Graceful degradation | Package imports and functions normally with all Miri metadata stripped | [Miri Wheel Ext. §8.3](miri-wheel-extensions.md) | 2 |

## Category Summary

| Category | Points | Checks |
|---|---|---|
| A. Packaging Baseline | 10 | 001–005 |
| B. Agent Metadata Core | 20 | 006–013 |
| C. Examples | 10 | 014–017 |
| D. Identity & Security | 25 | 018–027 |
| E. Deprecation & Lifecycle Coherence | 25 | 028–035 |
| F. Discovery & Degradation | 10 | 036–040 |
| **Total** | **100** | **40** |

## Notes for Linter Implementers

- Report each check by its stable ID (`MIRI-PY-NNN`); IDs are never renumbered — retired checks are marked *withdrawn* and their weight redistributed in a new minor version of this checklist.
- Checks E-029/030/031 require the *previous* release for comparison; linters SHOULD fetch it via the declared `update_check` endpoint and degrade to *skipped (weight forfeited, reported)* when unavailable.
- Machine-readable form: a `checklist.json` derived from this table is a planned deliverable, following the same schema-as-data rule as everything else in Miri — this document and the JSON must be generated from one source.

## Companion

- [CLI Linter Checklist](../cli/linter-checklist.md) — the same model for command-line tools (`MIRI-CLI-NNN`).
