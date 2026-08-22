# Miri Standard: CLI Lifecycle and Vulnerability Signaling

*Specification Version: 0.2-draft*
*Status: Draft*
*Created: 2026*

## Abstract

This specification defines how a Miri-compliant CLI declares its identity, advisory sources, update state, and
deprecation metadata so that agents and scanners can answer at call time: **"is this tool vulnerable?"**, **"is this
tool current?"**, and **"is this flag going away?"**. It is the normative counterpart to the two background documents in
this directory ([landscape](landscape-and-prior-art.md), [signaling](update-and-vulnerability-signaling.md)).

The library world's security machinery — [purl](https://github.com/package-url/purl-spec) identity joined against
[OSV](https://ossf.github.io/osv-schema/) advisories — cannot see a standalone CLI binary because nothing standard makes
the binary legible. This specification supplies the missing legs: mandatory self-identification in the introspection
output, declared advisory sources, a standard update-check primitive, a machine-readable changelog, and structured
deprecation metadata. It covers both open source and private/internal CLIs with the same structure.

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Design Principles](#2-design-principles)
3. [Self-Identification](#3-self-identification)
4. [Advisory Sources](#4-advisory-sources)
5. [Update Check and Machine-Readable Changelog](#5-update-check-and-machine-readable-changelog)
6. [Deprecation Metadata](#6-deprecation-metadata)
7. [Open Source CLIs](#7-open-source-clis)
8. [Private and Internal CLIs](#8-private-and-internal-clis)
9. [Conformance Requirements](#9-conformance-requirements)

---

## 1. Problem Statement

An agent's knowledge of a CLI comes from three sources that go stale at different rates: frozen model weights (never
updatable), skill files (updated only when regenerated), and live introspection (current only if consulted). For
libraries, staleness and vulnerability are detected externally by joining installed identity+version against advisory
databases. For CLIs that join usually cannot be performed:

- A standalone binary has no standard identity a scanner can read (Go's embedded buildinfo is the lone exception).
- No standard exists for asking a CLI whether a newer version exists; every vendor ships a homegrown notifier against a
  homegrown endpoint.
- Deprecations live in changelogs and release notes that a meaningful fraction of consumers — frozen weights — are
  structurally incapable of reading.

## 2. Design Principles

### 2.1 Declare Sources, Not Verdicts

A CLI MUST NOT embed claims about its own security status. It declares identity and pointers to live sources; verdicts
are computed by the consumer at call time.

### 2.2 Reuse the Existing Stack

Identity is a purl. Advisories are OSV records. This specification defines no advisory format, no version-comparison
rules, and no vulnerability-severity vocabulary.

### 2.3 One Source of Truth, Derived Outputs

The identity, deprecation, and lifecycle data specified here MUST come from the same schema-as-data structure that
generates `--help` and `--describe` — never from parsing the CLI's own help text. Skill files regenerated from the
binary (landscape doc §4.5) inherit the same data.

### 2.4 Same Shape for Open Source and Private

A private CLI differs from a public one only in values (a private purl, an internal advisory endpoint, an internal
release manifest) — never in structure.

### 2.5 Machine Channel Discipline

All output defined here is JSON on **stdout** with exit code 0 on success. Deprecation and update *warnings* go to
**stderr** only, so they never corrupt a payload.

### 2.6 Structured Error Envelope

When a command fails, its machine channel (stdout, per §2.5) MUST emit a single JSON object carrying a top-level
`schema_version` and an `error` object:

```json
{
  "schema_version": "1",
  "ok": false,
  "error": {
    "code": "CONFIRMATION_REQUIRED",
    "retryable": false,
    "suggestions": ["re-run with --force"]
  }
}
```

`error.retryable` states whether re-running the **identical** invocation may later succeed. It is `true` only for
transient failures (network error, timeout, rate limit) — never for failures that require the caller to change the
command or the environment first. Agents branch on this field, so a wrong value causes either blind retry loops or
premature give-up.

Standard error codes:

| `code` | `retryable` | Meaning |
| --- | --- | --- |
| `TRANSIENT` | `true` | Network error, timeout, or rate limit; the same call may succeed later |
| `VALIDATION` | `false` | Malformed or invalid arguments; the caller must fix the input |
| `AUTH` | `false` | Missing or rejected credentials; the caller must authenticate |
| `CONFIRMATION_REQUIRED` | `false` | A destructive action needs `--force`/`--yes`; the caller must add it |
| `FLAG_REMOVED` | `false` | The flag or subcommand was removed; the caller must use its replacement (§6) |

Code-specific fields (e.g. `flag` and `removed_in` for `FLAG_REMOVED`) are added alongside these. This envelope is the
canonical error format referenced by the error-handling checks. `schema_version` is the ecosystem convention for the
wire-schema version of *any* machine-readable JSON document these tools emit — including linter reports and other
tooling output — so no document substitutes a per-format alias such as `report_version`.

## 3. Self-Identification

The CLI's introspection output (`<cli> --describe`, or the Miri introspection command once specified) carries a
top-level `schema_version` (§2.6, per MIRI-CLI-010) and an `identity` block. The complete document — identity,
`support` (§3.2), `advisory_sources` (§4), and the `commands` surface (§6) — is defined by
[`cli-describe-v1.json`](../../schemas/cli-describe-v1.json):

```json
{
  "schema_version": "1",
  "identity": {
    "purl": "pkg:generic/acme/acme-cli@3.2.0?repository_url=https://releases.acme.example",
    "version": "3.2.0",
    "distribution": "private",
    "source_repository": "https://github.com/acme/acme-cli",
    "sbom": "https://releases.acme.example/acme-cli/3.2.0/sbom.cdx.json",
    "build_info": {
      "commit": "adc17ee",
      "toolchain": "go1.25.1",
      "embedded_modules": true
    }
  }
}
```

### 3.1 Field Definitions

| Field | Required | Meaning |
|---|---|---|
| `purl` | Yes | The join key for advisory lookups. Use the purl type of the actual distribution channel (`pkg:npm/`, `pkg:pypi/`, `pkg:cargo/`, `pkg:golang/`…); `pkg:generic/` with a `repository_url` qualifier for direct binary distribution or channels OSV does not index (e.g. Homebrew). |
| `version` | Yes | The CLI's release version (one of the three clocks — see landscape doc §5). |
| `schema_version` (top-level) | Yes | The wire-schema version of the whole introspection document — a top-level field, not inside `identity` — versioned independently of `version`. |
| `distribution` | Yes | `"open-source"` or `"private"`. |
| `sbom` | MUST for direct binary distribution without embedded module info; SHOULD otherwise | URL or embedded path of a CycloneDX/SPDX SBOM for this release, making the dependency tree scannable for non-Go binaries (§7.1). Complementary to `purl`: the purl identifies the tool itself, the SBOM identifies what it bundles. |
| `build_info.embedded_modules` | SHOULD | `true` when the binary carries toolchain-embedded dependency info (e.g. Go buildinfo) readable without the SBOM. |

This single block is what converts a CLI from CPE-guessing territory into a normal scanner target.

### 3.2 Artifact-Level Support Status

The introspection output MUST also carry a `support` block — the CLI's own end-of-life state, same shape and semantics
as the Python specification's [`support` object](../python/lifecycle-security-metadata.md):

```json
{
  "support": {
    "status": "active",
    "supported_versions": [">=3.0,<4.0"],
    "eol_date": null,
    "replacement": null,
    "security_policy": "https://github.com/acme/acme-cli/blob/main/SECURITY.md"
  }
}
```

`status` is `"active"`, `"maintenance"`, `"deprecated"`, or `"eol"`; `deprecated`/`eol` require `replacement` (a purl
for a successor tool, or a subcommand path when the successor is absorption into another CLI). This is the one lifecycle
statement the artifact carries directly rather than pointing to — it is vendor-authored *intent*, not a computed
verdict. The status values are deliberately mappable onto the [OpenEoX](https://www.oasis-open.org/tc-openeox/) stages
(GA / End-of-Sales / EoL / End-of-Security-Support; Core Schema 1.0 in public review as of July 2026, ratification
expected 2027) — a pointer field to published OpenEoX statements will be added once that standard is ratified.

EOL is thereby handled at three levels, each with its own mechanism: the **CLI itself** via `support` (read locally from
`--describe`); the CLI's **bundled components** via the SBOM-purl join against external EoL sources (endoflife.date
today, OpenEoX once ratified) — never written into the SBOM itself, per §6.2; and **deprecated surfaces within the CLI**
via the per-flag `lifecycle` blocks of §6.

## 4. Advisory Sources

The introspection output MUST include `advisory_sources` — the same structure as the Python specification's [lifecycle.json](../python/lifecycle-security-metadata.md):

```json
{
  "advisory_sources": [
    { "type": "osv", "ecosystem": "npm", "url": "https://api.osv.dev/v1/query", "authoritative": true },
    { "type": "osv-internal", "url": "https://advisories.corp.acme.example/v1/query", "authoritative": true }
  ]
}
```

Types: `"osv"` (public OSV.dev), `"osv-internal"` (private endpoint serving OSV-schema records), `"osv-local"` (offline
OSV database archive). At least one entry is required. Consumers MUST NOT treat an empty public-OSV result as "not
vulnerable" for a `distribution: "private"` CLI unless public OSV is explicitly listed.

## 5. Update Check and Machine-Readable Changelog

### 5.1 `check-update`

A conforming CLI MUST implement:

```text
<cli> check-update --json
```

```json
{
  "schema_version": "1",
  "current": "3.2.0",
  "latest": "3.4.1",
  "update_available": true,
  "urgency": "security",
  "advisories": ["ACME-2026-0007"],
  "manifest": "https://releases.acme.example/acme-cli/manifest.json",
  "install_hint": "brew upgrade acme-cli"
}
```

- `urgency`: `"none"`, `"routine"`, `"recommended"`, or `"security"`. `"security"` MUST be set when any listed advisory
  affects the running version.
- The check MUST be **passive by default**: never run implicitly on normal invocations in non-interactive contexts,
  never print to stdout of other commands. An offline environment returns `"update_available": null` with exit code 0,
  not an error.
- `manifest` names the latest-version manifest consulted — the standard replacement for per-vendor notifier endpoints.

### 5.2 `changelog --since`

A conforming CLI MUST implement:

```text
<cli> changelog --since <version> --json
```

returning, per release between `<version>` and the current version: added/removed/deprecated subcommands and flags,
wire-schema changes (`schema_version` bumps), and exit-code meaning changes. This is the primitive that lets an agent
that has been away for three releases ask *what moved* — the counterpart of `check-update`, which only says *that* it
moved. The output is a top-level object with a `schema_version` (§2.6) and an ordered `releases` array (oldest first), one
entry per release in range. Each release entry carries `version`, string arrays `added` and `removed` (surface names),
a `deprecated` array of `{surface, removed_in, replacement}` objects, a `schema_version_change` object (`{from, to}`
or null), and an `exit_code_changes` array of `{code, was, now}` objects:

```json
{
  "schema_version": "1",
  "releases": [
    {
      "version": "3.2.0",
      "added": ["--format"],
      "removed": ["--export"],
      "deprecated": [{"surface": "--legacy", "removed_in": "4.0.0", "replacement": "--modern"}],
      "schema_version_change": {"from": "1", "to": "2"},
      "exit_code_changes": [{"code": 3, "was": "not found", "now": "permission denied"}]
    }
  ]
}
```

The five categories above are normative.

## 6. Deprecation Metadata

Every subcommand and flag entry in the introspection output MUST support a `lifecycle` sub-object:

```json
{
  "name": "--export",
  "lifecycle": {
    "status": "deprecated",
    "deprecated_since": "1.14.0",
    "removed_in": "1.18.0",
    "replacement": "--output archive",
    "migration": "https://docs.acme.example/migrate-export"
  }
}
```

Additionally, invoking a **removed** flag or subcommand MUST produce a structured error that teaches:

```json
{
  "ok": false,
  "error": { "code": "FLAG_REMOVED", "flag": "--export",
             "removed_in": "1.18.0", "retryable": false,
             "suggestions": ["use --output archive instead"] }
}
```

This converts the frozen-weights failure mode — agent constructs a command from stale knowledge, hits a dead-end error,
retries blind — into a one-turn recovery. Deprecation *warnings* during the grace period go to stderr only (§2.5).

### 6.1 Prior Art and Field Vocabulary

The `lifecycle` block deliberately mirrors the converged deprecation shape of the adjacent standards, so each field
carries a citation trail rather than being invented here:

- `deprecated_since` / `removed_in` are the CLI equivalent of the two-phase HTTP lifecycle: the `Deprecation` header
  field ([RFC 9745](https://www.rfc-editor.org/info/rfc9745/)) marking the start, the `Sunset` header ([RFC
  8594](https://www.rfc-editor.org/info/rfc8594/)) marking end-of-life, with `migration` playing RFC 9745's deprecation
  link relation.
- `replacement` plus a human-readable reason follows Python's [PEP 702](https://peps.python.org/pep-0702/) `@deprecated`
  decorator, GraphQL's `@deprecated(reason:)` directive, Java's `@Deprecated(since, forRemoval)`, and Rust's
  `#[deprecated(since, note)]`.
- The grace-period requirement (§7.3) follows the
  [Kubernetes deprecation policy for CLI elements](https://kubernetes.io/docs/reference/using-api/deprecation-policy/),
  the only shipped CLI-specific deprecation policy.

### 6.2 Where Deprecation State Lives

Deprecation is *interface lifecycle*, not *composition*: it is carried in the introspection output and in
`changelog --since`, both derived from the same schema-as-data source (§2.3). It MUST NOT be recorded in the SBOM, which
describes bundled components — a scanner reading the SBOM asks "what is inside this binary?", while an agent reading
`--describe` asks "which of these surfaces is going away?". Keeping the two artifacts single-purpose keeps both joins
clean.

The same rule covers end-of-life: the artifact's own EOL is the `support` block (§3.2); EOL of *bundled components* is
computed by joining the SBOM's purls against external EoL sources — neither is ever written into the SBOM.

### 6.3 Deprecation Coherence (Verification)

No existing tooling verifies that deprecation markers, the changelog, and actual removals agree — for CLIs or otherwise;
ecosystem prior art stops at changelog-entry bots (towncrier-style CI, which enforce that *an entry exists*) and
API-diff tools (cargo-semver-checks, griffe, japicmp, which detect changes without cross-checking declarations). The
Miri conformance tool MUST therefore verify, per release:

1. Every surface whose `lifecycle.status` is `deprecated` appears in the `changelog --since` output of the release that
   introduced the deprecation.
2. Every surface removed since a prior version appeared as `deprecated` in at least one earlier release (the §7.3 grace
   period) — **no silent removals**.
3. Every `replacement` names a surface that exists in the current introspection output.
4. Invoking each removed surface produces the structured teaching error of §6, not a generic parse failure.

In a conforming implementation, checks 1–3 hold *by construction*, because help, `--describe`, and `changelog` all
derive from one schema struct (§2.3); the verifier exists to catch drift in implementations that hand-maintain any of
the three.

### 6.4 Marking Danger and Mutation (Normative)

An agent driving a CLI must be able to tell, *before* invoking a surface, whether it is safe to run — the
frozen-weights failure mode is worst when the mistaken command deletes data or runs untrusted code. Each `command`
and `flag` entry in `--describe` therefore carries two boolean markers, both defaulting to `false` (absent means
false):

- **`destructive`** — `true` when invoking the command, or passing the flag, is destructive, irreversible, or runs
  untrusted code (for example a `purge` command, or an `--execute` flag that runs a downloaded artifact's code). A
  conformant consumer MUST obtain confirmation, or match a pre-approved policy, before acting on a `destructive: true`
  surface — it MUST NOT auto-invoke it on the metadata's say-so. This mirrors the `CONFIRMATION_REQUIRED` error posture
  (§2.6). Verified by **MIRI-CLI-040**.
- **`mutating`** — `true` when the command writes or changes state rather than reading only. It lets a consumer
  separate safe read-only introspection from state-changing operations without parsing help prose. Verified by
  **MIRI-CLI-041**.

Both markers derive from the same schema struct as help and `changelog` (§2.3), so they cannot drift from behavior in
a conforming implementation. They are structured fields, not free text: a marker that lives only inside a flag's
`description` string does not satisfy the checks. Below is the relevant `commands` excerpt of a `--describe` document
(the surrounding top-level fields are per §3):

```json
{
  "commands": [
    {
      "name": "score",
      "description": "Score a wheel against the standard (read-only)",
      "mutating": false,
      "flags": [
        { "name": "--execute", "description": "Run the wheel's code to evaluate execution checks", "destructive": true }
      ]
    },
    {
      "name": "init",
      "description": "Scaffold Miri configuration into the current project",
      "mutating": true
    }
  ]
}
```

The vocabulary follows the Agent-First CLI convention of machine-legible side-effect declaration (landscape §2.1, P16);
Miri makes it normative and mechanically checkable.

## 7. Open Source CLIs

For `distribution: "open-source"` CLIs:

### 7.1 Distribution and Identity

- When distributed through a package registry that OSV indexes (npm, PyPI, crates.io, Go…), `purl` MUST use that
  registry's purl type; the CLI then inherits the registry's update and advisory machinery, and `check-update` SHOULD
  consult the registry rather than a bespoke endpoint.
- When distributed as direct binaries (GitHub Releases, download page), each release MUST publish an SBOM and reference
  it from `identity.sbom`; the latest-version manifest referenced by `check-update` SHOULD be the forge's releases API
  or a static manifest adjacent to the artifacts.

### 7.2 Publishing Advisories

Vulnerabilities follow the standard home-database path: a repository security advisory (GHSA, optionally with CVE) or
the distribution ecosystem's advisory database, flowing to OSV.dev automatically. `advisory_sources` lists public OSV
with the matching ecosystem. No Miri-specific publication step exists.

### 7.3 Deprecation in Public

Because open source CLIs cannot know their consumers, the grace period between `deprecated_since` and `removed_in` MUST
span at least one minor release in which the deprecated surface still functions while emitting the stderr warning and
carrying the `lifecycle` block — so both live-introspecting agents and skill-file regeneration cycles have a release in
which to observe the change before it breaks.

## 8. Private and Internal CLIs

For `distribution: "private"` CLIs (internal developer tools, org-specific automation):

### 8.1 Identity

- `purl` uses `pkg:generic/<org>/<name>@<version>?repository_url=<internal releases URL>`, or the internal registry's
  purl type if distributed through one (private npm/PyPI/Artifactory).
- Internal CLIs are exactly the population where CPE-guessing scanners fail completely and public OSV silently returns
  empty — self-identification is therefore MANDATORY, not merely useful.

### 8.2 Internal Advisory Sources

`advisory_sources` points at the organization's OSV-compatible endpoint or offline OSV database (same options as the
Python spec §5.2). Organization-local record IDs (e.g. `ACME-2026-0007`) attach to the CLI's private purl. Public OSV
MAY be listed additionally to cover the CLI's open source dependency tree (via the SBOM or embedded buildinfo).

### 8.3 Update Checks

`check-update` consults an internal release manifest — a static JSON file adjacent to the release artifacts is sufficient:

```json
{ "name": "acme-cli", "latest": "3.4.1",
  "releases": { "3.4.1": { "urgency": "security", "advisories": ["ACME-2026-0007"] } } }
```

This replaces the per-vendor notifier pattern with a declared, auditable endpoint. Air-gapped environments set
`advisory_sources` to `osv-local` and `check-update` degrades to `"update_available": null`.

### 8.4 Fleet Enforcement

Because internal CLIs have a known consumer population, organizations SHOULD couple `check-update`'s
`urgency: "security"` with policy: CI images and agent harnesses refuse to run a CLI whose running version is covered by
an open internal advisory. The structured output exists precisely so this can be a mechanical gate rather than a wiki
page.

## 9. Conformance Requirements

A CLI conforms to this specification if:

1. Its introspection output contains a valid `identity` block whose `purl` version matches the binary's actual version,
   and a `support` block per §3.2 (with `replacement` when status is `deprecated`/`eol`).
2. `advisory_sources` has at least one entry; private CLIs do not rely solely on public OSV.
3. `check-update --json` and `changelog --since <v> --json` are implemented per §5, passive by default, JSON-on-stdout, warnings-on-stderr.
4. Every deprecated surface carries a `lifecycle` block, and every removed surface produces the structured teaching
   error of §6.
5. The deprecation coherence checks of §6.3 pass: introspection lifecycle state, `changelog --since` output, and actual
   removals agree, with no silent removals.
6. All of the above derive from the same schema-as-data source as `--help` (§2.3).

A conformance test suite is a planned deliverable alongside the introspection schema (landscape doc §4.1).

---

## References

- Background: [landscape-and-prior-art.md](landscape-and-prior-art.md) · [update-and-vulnerability-signaling.md](update-and-vulnerability-signaling.md)
- Companion Python spec: [lifecycle-security-metadata.md](../python/lifecycle-security-metadata.md)
- purl spec — <https://github.com/package-url/purl-spec>
- OSV schema — <https://ossf.github.io/osv-schema/> · OSV.dev API — <https://google.github.io/osv.dev/api/>
- Go embedded buildinfo / govulncheck — <https://go.dev/blog/govulncheck>
- CycloneDX — <https://cyclonedx.org/> · SPDX — <https://spdx.dev/>
- OpenEoX TC (OASIS) — <https://www.oasis-open.org/tc-openeox/> · Core Schema 1.0 CSD01 — <http://www.oasis-open.org/2026/07/14/invitation-to-comment-on-openeox-core-schema-version-1-0-csd01/>
- OWASP CLE and OpenEoX — <https://owasp.org/blog/2026/04/15/end-of-life-cle-and-openeox>
- endoflife.date — <https://endoflife.date/>
- OpenVEX — <https://github.com/openvex/spec>
- RFC 9745 — The Deprecation HTTP Response Header Field — <https://www.rfc-editor.org/info/rfc9745/>
- RFC 8594 — The Sunset HTTP Header Field — <https://www.rfc-editor.org/info/rfc8594/>
- PEP 702 — Marking deprecations using the type system — <https://peps.python.org/pep-0702/>
- Kubernetes deprecation policy (CLI elements) — <https://kubernetes.io/docs/reference/using-api/deprecation-policy/>
- The `kubectl get --export` removal case study — <https://www.infoq.com/articles/ai-agent-cli/>
