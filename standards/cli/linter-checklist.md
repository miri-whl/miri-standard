# Miri Linter Checklist: Command-Line Tools

*Specification Version: 0.2-draft*
*Status: Draft*
*Created: 2026*

## Purpose

The explicit, numbered list of every check a Miri-conformance linter runs against a CLI, with the standard each check
derives from and a scoring weight. Linter projects implement checks by number (`MIRI-CLI-001` … `MIRI-CLI-043`); the
weights sum to exactly **100**, so a CLI's Miri score is the sum of the weights of its passing checks.

## Scoring Model

Identical to the [Python checklist](../python/linter-checklist.md): **Score** = Σ weights of passing checks; **M**
checks are required for conformance (any M failure caps the reported score at 74); *conditional* checks score
automatically when inapplicable. The previous-release checks (MIRI-CLI-030, 033, 035, 036, 037) are *conditional*, so a
first release — with no prior release to diff against — scores them at full weight and can reach Gold; they forfeit
weight only when a prior release exists but the linter cannot fetch it.

**Grade bands**: 90–100 **Gold** (agent-native) · 75–89 **Silver** (agent-ready) · 50–74 **Bronze** (partially legible)
· <50 non-conforming.

## Conformance Profiles

- **Miri Core** — the conventions, machine-readable output, self-identification, and safety layer: Baseline Conventions
  (MIRI-CLI-001–007), Machine Output (008–014), Identity & Introspection (015–024), and Safety (039–043). A CLI is
  **Core-conforming** when it passes every MUST check in this set. Core is the recommended adoption target and the
  standard's most defensible layer.
- **Miri Full** — all 43 checks, adding the Update & Changelog (025–030) and Deprecation Coherence (031–038) machinery
  that tracks lifecycle history across releases. The Bronze/Silver/Gold score is computed over the Full set.

The two profiles share one check corpus and one weighting; Core is a named subset, not a separate standard.

## The Checks

### A. Baseline Conventions (12 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-CLI-001 | M | POSIX option syntax | `-` short options, `--` terminator, options-before-operands accepted | [POSIX XBD §12.2](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html) | 2 |
| MIRI-CLI-002 | M | Conforming --help | `--help` prints to stdout, exits 0, never pages or blocks | [GNU Coding Standards §4.7](https://www.gnu.org/prep/standards/html_node/_002d_002dhelp.html) | 2 |
| MIRI-CLI-003 | M | --version | Prints version to stdout, exits 0 | [GNU Coding Standards §4.7](https://www.gnu.org/prep/standards/html_node/_002d_002dversion.html) | 1 |
| MIRI-CLI-004 | S | Per-subcommand help | `<cli> <sub> --help` works for every subcommand | [clig.dev](https://clig.dev/) *(informative)* | 1 |
| MIRI-CLI-005 | S | Color & TTY discipline | Honors `NO_COLOR`; detects non-TTY and drops decoration | [no-color.org](https://no-color.org/) / [clig.dev](https://clig.dev/) | 2 |
| MIRI-CLI-006 | M | Non-interactive default | No command blocks on a prompt when stdin is not a TTY | [CLI Spec §2.5](cli-lifecycle-specification.md) / [anc.dev](https://anc.dev/) *(informative)* | 3 |
| MIRI-CLI-007 | S | Pipeline composability | Handles SIGPIPE cleanly; accepts stdin where input is expected | [clig.dev](https://clig.dev/) *(informative)* | 1 |

### B. Machine Output (18 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-CLI-008 | M | JSON everywhere | Every command supports JSON output | [CLI Spec §2.5](cli-lifecycle-specification.md) | 4 |
| MIRI-CLI-009 | M | One output flag | The same flag (e.g. `--json`) selects it on every command — no per-command variants | [Landscape §2.3 (Chow)](landscape-and-prior-art.md) | 2 |
| MIRI-CLI-010 | M | schema_version stamped | Every JSON payload carries top-level `schema_version` | [CLI Spec §3.1](cli-lifecycle-specification.md) | 3 |
| MIRI-CLI-011 | M | Clean payload channel | No ANSI codes, prose, or warnings mixed into stdout JSON | [CLI Spec §2.5](cli-lifecycle-specification.md) | 2 |
| MIRI-CLI-012 | S | Deterministic ordering | Same inputs produce identically ordered output | [Landscape §2.1 P03](landscape-and-prior-art.md) *(informative)* | 2 |
| MIRI-CLI-013 | M | Structured errors | Failures emit JSON with a stable machine `error.code` | [CLI Spec §6](cli-lifecycle-specification.md) | 3 |
| MIRI-CLI-014 | S | Recoverable errors | Errors carry `retryable` and `suggestions` | [CLI Spec §6](cli-lifecycle-specification.md) / [Signaling §3.3-3](update-and-vulnerability-signaling.md) | 2 |

### C. Identity & Introspection (22 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-CLI-015 | M | --describe implemented | Machine-readable introspection output exists and is valid JSON | [CLI Spec §3](cli-lifecycle-specification.md) | 3 |
| MIRI-CLI-016 | M | Identity purl | `identity.purl` present, well-formed, matches distribution channel | [CLI Spec §3.1](cli-lifecycle-specification.md) / [purl spec](https://github.com/package-url/purl-spec) | 3 |
| MIRI-CLI-017 | M | Version coherence | `identity.version` equals the binary's actual `--version` | [CLI Spec §9-1](cli-lifecycle-specification.md) | 2 |
| MIRI-CLI-018 | M | Wire schema versioned | Top-level `schema_version` is independent of the release version | [CLI Spec §3.1](cli-lifecycle-specification.md) | 1 |
| MIRI-CLI-019 | M | Distribution declared | `identity.distribution` is `open-source` or `private` | [CLI Spec §3.1](cli-lifecycle-specification.md) | 1 |
| MIRI-CLI-020 | M | Support block | `support` present with valid `status` | [CLI Spec §3.2](cli-lifecycle-specification.md) | 2 |
| MIRI-CLI-021 | M | EOL coherence | `support.status` `deprecated`/`eol` ⇒ `replacement` present | [CLI Spec §3.2](cli-lifecycle-specification.md) | 2 |
| MIRI-CLI-022 | M | Advisory sources | ≥1 valid entry in `advisory_sources` | [CLI Spec §4](cli-lifecycle-specification.md) / [OSV schema](https://ossf.github.io/osv-schema/) | 3 |
| MIRI-CLI-023 | M | Private-source rule | `distribution: private` does not rely solely on public OSV | [CLI Spec §4](cli-lifecycle-specification.md) | 2 |
| MIRI-CLI-024 | M | Composition legible | Standalone binary carries embedded module info or references a release SBOM (*conditional*: registry-distributed CLIs pass automatically) | [CLI Spec §3.1/§7.1](cli-lifecycle-specification.md) / [CycloneDX](https://cyclonedx.org/)/[SPDX](https://spdx.dev/) | 3 |

### D. Update & Changelog (14 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-CLI-025 | M | check-update implemented | `check-update --json` returns the specified shape | [CLI Spec §5.1](cli-lifecycle-specification.md) | 4 |
| MIRI-CLI-026 | M | Passive by default | No implicit update check on normal invocations; nothing printed to other commands' stdout | [CLI Spec §5.1](cli-lifecycle-specification.md) | 2 |
| MIRI-CLI-027 | M | Offline degradation | Offline returns `update_available: null`, exit 0 — not an error | [CLI Spec §5.1](cli-lifecycle-specification.md) | 1 |
| MIRI-CLI-028 | M | Security urgency | `urgency: security` set when an advisory covers the running version | [CLI Spec §5.1](cli-lifecycle-specification.md) | 2 |
| MIRI-CLI-029 | M | changelog --since | `changelog --since <v> --json` implemented | [CLI Spec §5.2](cli-lifecycle-specification.md) | 4 |
| MIRI-CLI-030 | M | Changelog coverage | Output covers added/removed/deprecated surfaces, schema bumps, exit-code changes | [CLI Spec §5.2](cli-lifecycle-specification.md) | 1 |

### E. Deprecation Coherence (22 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-CLI-031 | M | Lifecycle blocks | Every deprecated flag/subcommand carries a `lifecycle` object | [CLI Spec §6](cli-lifecycle-specification.md) | 3 |
| MIRI-CLI-032 | M | Two-phase fields | `deprecated_since` and `removed_in`/`replacement` populated | [CLI Spec §6.1](cli-lifecycle-specification.md) / [RFC 9745](https://www.rfc-editor.org/info/rfc9745/) + [RFC 8594](https://www.rfc-editor.org/info/rfc8594/) | 2 |
| MIRI-CLI-033 | M | Teaching errors | Invoking a removed surface yields the structured error (code, `retryable: false`, `suggestions`) — not a generic parse failure | [CLI Spec §6/§6.3-4](cli-lifecycle-specification.md) | 4 |
| MIRI-CLI-034 | M | Warnings on stderr | Grace-period deprecation warnings never touch stdout | [CLI Spec §2.5](cli-lifecycle-specification.md) / [Signaling §3.3-5](update-and-vulnerability-signaling.md) | 2 |
| MIRI-CLI-035 | M | Grace period | Deprecated surfaces function for ≥1 minor release before removal | [CLI Spec §7.3](cli-lifecycle-specification.md) / [K8s deprecation policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/) *(informative)* | 3 |
| MIRI-CLI-036 | M | Changelog coherence | Every deprecation appears in `changelog --since` of the deprecating release | [CLI Spec §6.3-1](cli-lifecycle-specification.md) | 3 |
| MIRI-CLI-037 | M | No silent removals | Every removed surface was deprecated in ≥1 earlier release | [CLI Spec §6.3-2](cli-lifecycle-specification.md) | 3 |
| MIRI-CLI-038 | M | Replacements resolve | Every `replacement` names a surface in the current `--describe` | [CLI Spec §6.3-3](cli-lifecycle-specification.md) | 2 |

### F. Safety (12 points)

| # | Level | Check | What it verifies | Reference | Weight |
|---|---|---|---|---|---|
| MIRI-CLI-039 | M | Dry run on writes | Every mutating command supports `--dry-run` with faithful simulation | [Landscape §2.2 (anc.dev)](landscape-and-prior-art.md) / [CLI Spec §9](cli-lifecycle-specification.md) | 4 |
| MIRI-CLI-040 | M | Danger marked | Destructive operations flagged as such in `--describe` | [Landscape §2.1 P16](landscape-and-prior-art.md) | 3 |
| MIRI-CLI-041 | M | Read/write visible | The read-vs-write nature of each command is determinable from `--describe`/`--help` alone | [Landscape §2.2 (anc.dev)](landscape-and-prior-art.md) | 2 |
| MIRI-CLI-042 | S | Safe retries | Mutations support idempotency keys or optimistic-lock version guards | [Landscape §2.3 (desk) / §2.4 (Docker)](landscape-and-prior-art.md) | 2 |
| MIRI-CLI-043 | S | Graceful cancellation | SIGINT/SIGTERM cleans up partial state before exit | [Landscape §2.1 P11](landscape-and-prior-art.md) | 1 |

## Category Summary

| Category | Points | Checks |
|---|---|---|
| A. Baseline Conventions | 12 | 001–007 |
| B. Machine Output | 18 | 008–014 |
| C. Identity & Introspection | 22 | 015–024 |
| D. Update & Changelog | 14 | 025–030 |
| E. Deprecation Coherence | 22 | 031–038 |
| F. Safety | 12 | 039–043 |
| **Total** | **100** | **43** |

## Check Definitions (Source of Truth)

The standard's vocabulary: each *requirement* in a spec is verified by a *check*; each check failure instance is a
*violation*. (The word "alert" is deliberately unused, left to tooling layers such as code-scanning dashboards.)

Every check in this table has a canonical definition file in [`checks/`](checks/) — one YAML document per check
(`checks/MIRI-CLI-NNN.yaml`), validated against [check-v1.json](../../schemas/check-v1.json). Each file carries the check's
name, level, category, weight, short and long descriptions, an example violation, a suggested fix, the standards
references, versioning (`added_in`/`withdrawn_in`), canonical
URLs (`urls.definition` on GitHub, `urls.html` on the published site — for linter reports to link), and — critically —
the **canonical severity**: a default
severity (`LOW`/`MINOR`/`MEDIUM`/`HIGH`/`CRITICAL`, numeric 1–5) and the `violation_unit` defining what counts as one
violation.

The severity assignment exists so that magnitude-aware health scoring is comparable across implementations: severity is
defined by the standard, never by the linter. Linter implementations MUST consume these definitions rather than
maintaining their own copies, and MUST NOT override severity or violation units. Per-instance checks additionally carry a
canonical `population_unit` — the denominator for report-level violation density; populations are reported,
never scored, and never invented by implementations. Definitions also declare `requirements` — the operating capabilities
(`network`, `previous-release`, `execution`) beyond the target's baseline analysis mode a check needs; a linter
lacking one MUST skip with the fixed reason, and MUST NOT skip otherwise.

This table is the human rendering of the same data; the YAML files are authoritative, and coherence between the two
(IDs, levels, weights, and the 100-point sum) is verified mechanically.

## Notes for Linter Implementers

- Report each check by its stable ID (`MIRI-CLI-NNN`); IDs are never renumbered — retired checks are marked *withdrawn*
  and their weight redistributed in a new minor version of this checklist.
- Checks declaring `previous-release` in their definition's `requirements` (030/033/035/036/037) need a prior
  release; linters SHOULD obtain it via `check-update`'s `manifest` and degrade to *skipped (weight forfeited,
  reported)* when unavailable. The `requirements` field in each check definition is the authoritative list of such
  constraints and their fixed skip reasons.
- References marked *(informative)* cite community practice (clig.dev, anc.dev, Agent-First CLI principles) that has no
  normative authority — the normative source for those checks is the Miri CLI specification itself; the citation records
  lineage per the [landscape survey](landscape-and-prior-art.md).
- Machine-readable form: the [`checks/`](checks/) directory is the per-check source of truth; an aggregated
  `checklist.json` remains a planned convenience deliverable — this document and the
  JSON must be generated from one source.

## Companion

- [Python Linter Checklist](../python/linter-checklist.md) — the same model for wheels (`MIRI-PY-NNN`).
