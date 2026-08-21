# Miri Standard: Package Lifecycle and Security Metadata (Python)

*Specification Version: 0.1-draft*
*Status: Draft*
*Created: 2026*

## Abstract

This specification defines how a Miri-compliant Python package declares its identity, advisory sources, and lifecycle
state so that agents and scanners can answer two questions at call time: **"is this package vulnerable?"** and **"is
this package current?"**. It adds one file, `agent-metadata/lifecycle.json`, to the structure defined in the
[Agent Metadata Specification](agent-metadata-specification.md).

The design reuses the existing open source security stack — [purl](https://github.com/package-url/purl-spec) for
identity and the [OSV schema](https://ossf.github.io/osv-schema/) for advisories — rather than inventing a parallel one.
The package never asserts its own security status; it declares **who it is** and **where authoritative answers live**,
for both open source and private distribution. Background and rationale:
[CLI Update and Vulnerability Signaling](../cli/update-and-vulnerability-signaling.md).

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Design Principles](#2-design-principles)
3. [The lifecycle.json File](#3-the-lifecyclejson-file)
4. [Open Source Packages](#4-open-source-packages)
5. [Private and Internal Packages](#5-private-and-internal-packages)
6. [Deprecating Interfaces](#6-deprecating-interfaces)
7. [Agent Consumption Workflow](#7-agent-consumption-workflow)
8. [Conformance Requirements](#8-conformance-requirements)
9. [Security Considerations](#9-security-considerations)

---

## 1. Problem Statement

"This package must be updated" is never knowledge the package holds. It is computed externally as a join:

> (installed identity + version) × (advisory database with affected ranges and a `fixed` version)

For public PyPI packages the join works today because both legs are standardized: `dist-info/METADATA` provides
identity+version, and OSV.dev (aggregating PYSEC, GHSA, and CVE data) provides advisories. But three gaps remain that
this specification closes:

1. **Agents don't know where to look.** A scanner has OSV hardcoded; an agent working with an arbitrary package does not
   know which advisory sources are authoritative for it — especially for packages from private indexes, where OSV.dev
   has no data and will silently return "no vulnerabilities."
2. **Private packages have no identity convention.** Internal packages lack a purl namespace agreement, so internal
   advisory records have nothing reliable to attach to.
3. **Lifecycle state beyond vulnerabilities is undeclared.** Deprecation, end-of-life, and successor packages live in
   READMEs and changelogs — invisible to an agent that resolves the package from frozen weights.

## 2. Design Principles

### 2.1 Declare Sources, Not Verdicts

A package MUST NOT embed claims like "no known vulnerabilities" — such a claim is stale the moment it is built.
`lifecycle.json` declares *identity* and *pointers to live sources*; the verdict is always computed by the consumer at
call time.

### 2.2 Reuse the Existing Stack

Identity is a purl. Advisories are OSV records. Update state comes from the package index the package was installed
from. This specification defines no new advisory format and no new version-comparison rules.

### 2.3 Same Shape for Open Source and Private

A private package differs from a public one only in *values* (a private purl namespace, an internal OSV endpoint, an
internal index URL) — never in *structure*. Tooling written against this spec works unchanged in both worlds.

### 2.4 Build-Time Generation

Like all Miri agent metadata, `lifecycle.json` SHOULD be generated at build time from `pyproject.toml` plus
Miri-specific configuration, never hand-maintained per release.

## 3. The lifecycle.json File

**Location**: `package/agent-metadata/lifecycle.json` (alongside `sdk-manifest.json`).

**Schema**:

```json
{
  "$schema": "https://miri-standard.org/schemas/lifecycle-v1.json",
  "miri_lifecycle_version": "0.1",
  "generated_at": "2026-08-18T12:00:00Z",

  "identity": {
    "purl": "pkg:pypi/example-package@2.1.0",
    "distribution": "open-source",
    "registry": "https://pypi.org/simple/",
    "source_repository": "https://github.com/example/example-package"
  },

  "advisory_sources": [
    {
      "type": "osv",
      "ecosystem": "PyPI",
      "url": "https://api.osv.dev/v1/query",
      "authoritative": true
    }
  ],

  "update_check": {
    "type": "pypi-json",
    "url": "https://pypi.org/pypi/example-package/json"
  },

  "support": {
    "status": "active",
    "supported_versions": [">=2.0,<3.0"],
    "eol_date": null,
    "replacement": null,
    "security_policy": "https://github.com/example/example-package/blob/main/SECURITY.md"
  },

  "vex": null
}
```

### 3.1 Field Definitions

| Field | Required | Meaning |
|---|---|---|
| `identity.purl` | Yes | Package URL including version. The join key for all advisory lookups. |
| `identity.distribution` | Yes | `"open-source"` or `"private"`. Signals which defaults in §4/§5 apply. |
| `identity.registry` | Yes | The index this artifact is published to. An agent finding a mismatch with the installed origin should treat the package as untrusted (dependency-confusion signal). |
| `advisory_sources[]` | Yes | Ordered list of OSV-compatible query endpoints authoritative for this package. At least one entry. |
| `advisory_sources[].type` | Yes | `"osv"` (public OSV.dev), `"osv-internal"` (private endpoint serving OSV-schema records), or `"osv-local"` (path/URL to an offline OSV database archive). |
| `update_check` | Yes | Where to learn the latest published version. `type`: `"pypi-json"` or `"pep700-index"` for private indexes supporting PEP 691/700. |
| `support.status` | Yes | `"active"`, `"maintenance"`, `"deprecated"`, or `"eol"`. |
| `support.replacement` | When deprecated/eol | Purl of the successor package. |
| `vex` | No | URL of an OpenVEX / CycloneDX VEX document with vendor exploitability statements. |

The advisory-source list has these semantics:

- **Order is preference, not exclusivity.** Consumers SHOULD query every listed source and union the results — a hit
  from any authoritative source is a hit; the first entry is preferred for display and metadata.
- **`authoritative` defaults to `true`** when omitted. A source marked `authoritative: false` covers only the package's
  dependency tree, not advisories against the package itself (used for public OSV under a `private` package, §5).
- **`osv-local` paths** resolve relative to the directory containing `lifecycle.json` (the wheel's `agent-metadata/`)
  when relative; absolute paths and `file:` URLs are used as given. An archive older than the consumer's freshness
  policy MUST be treated as unknown, never as "no advisories".

### 3.2 Relationship to SBOMs (PEP 770)

`lifecycle.json` identifies the package itself; it does not describe what the package *bundles*. That is the job of an
SBOM, and Python already has a standard for it: [PEP 770](https://peps.python.org/pep-0770/) (accepted 2025) places SBOM
documents in `.dist-info/sboms/`, discoverable by scanners without any Miri-specific pointer.

- A pure-Python package MAY omit SBOMs — `Requires-Dist` plus installed dist-info already expose its dependency tree,
  and a Miri requirement here would duplicate PyPA machinery.
- A package bundling **non-Python components** (vendored C libraries, statically linked OpenSSL, Rust extensions — the
  "phantom dependency" problem) MUST ship PEP 770 SBOM data covering them. Build tooling makes this nearly free:
  auditwheel (≥6.5.0) generates it automatically when repairing wheels.

The two artifacts divide cleanly: advisories against the *package* join on `identity.purl` via `advisory_sources`;
advisories against *bundled components* join on the purls inside the PEP 770 SBOM. Consumers performing a full
vulnerability check evaluate both.

The same division applies to **end-of-life of bundled components**: whether a vendored OpenSSL is past its support
window is never written into the SBOM — the SBOM contributes the component purls, and the consumer joins them against
external EoL data sources (endoflife.date today; [OpenEoX](https://www.oasis-open.org/tc-openeox/) once ratified). The
SBOM makes the join possible; the verdict is computed at call time, like every other verdict in this specification.

### 3.3 End-of-Life Signaling for the Package Itself

The package's own end-of-life is the one lifecycle statement the artifact carries directly, because it is a
vendor-authored *intent*, not a computed verdict: `support.status: "eol"` with `eol_date` and `replacement` (§3.1).
Emerging prior art:

- **[OpenEoX](https://www.oasis-open.org/tc-openeox/)** (OASIS) standardizes machine-readable EoL exchange with four
  stages — General Availability, End-of-Sales, End-of-Life, End-of-Security-Support.
  Core Schema 1.0 entered
  [public review](http://www.oasis-open.org/2026/07/14/invitation-to-comment-on-openeox-core-schema-version-1-0-csd01/)
  in July 2026; ratification is expected in 2027. Miri's `support.status` values map onto it deliberately: `active` ≈ GA,
  `maintenance` ≈ the window where only security support remains (pre-EoSSec), `eol` ≈ EoL/EoSSec passed. Organizations
  MAY additionally publish OpenEoX statements; a future version of this specification will add a pointer field to them
  once OpenEoX 1.0 is ratified, rather than pre-standardizing against a draft.
- **OWASP CLE** (Common Lifecycle Enumeration) is the complementary effort for naming lifecycle states across vendors;
  see [how the two compose](https://owasp.org/blog/2026/04/15/end-of-life-cle-and-openeox).

Consumers therefore handle EOL at three levels, each with its own mechanism: the **package itself** via `support` (read
locally, no network); **direct dependencies** via their own `lifecycle.json`/`support` blocks; **bundled components**
via the SBOM-purl join against external EoL sources (above).

## 4. Open Source Packages

For `distribution: "open-source"` packages published to PyPI:

### 4.1 Defaults

- `advisory_sources` MUST include the public OSV endpoint with `ecosystem: "PyPI"`. Build tools SHOULD inject this entry
  automatically.
- `update_check` MUST point at the PyPI JSON API for the package.
- `identity.purl` MUST use the `pkg:pypi/` type with the normalized (PEP 503) project name.

### 4.2 Publishing Advisories

Maintainers of Miri-compliant packages SHOULD publish vulnerabilities through the standard home-database path so they
flow to every consumer automatically:

1. File a **GitHub repository security advisory** (which can request a CVE via GitHub-as-CNA), or submit directly to the
   [PyPA Advisory Database](https://github.com/pypa/advisory-database).
2. The advisory propagates GHSA/PYSEC → OSV.dev → all scanners and agents.
3. Corrections go to the home database, never to downstream aggregators.

No Miri-specific publication step exists or is needed — this is deliberate (§2.2).

### 4.3 Deprecating a Package

When a package enters `deprecated` or `eol`, the final releases MUST carry the updated `support` block with
`replacement` set. Because agents read `lifecycle.json` from the *installed* wheel, this reaches every future install
even if the user never reads the README. The [migration-guide.json](agent-metadata-specification.md) file carries the
how; `support.replacement` carries the what.

## 5. Private and Internal Packages

For `distribution: "private"` packages published to internal indexes (Artifactory, Nexus, devpi, CodeArtifact, simple
private indexes):

### 5.1 Identity

- Internal packages MUST still carry a purl. The RECOMMENDED convention is the standard `pkg:pypi/` type with the
  organization's private index in a purl qualifier:
  `pkg:pypi/acme-billing@3.2.0?repository_url=https://pypi.internal.acme.example/simple/`.
- `identity.registry` MUST name the internal index. Public OSV lookups against private names return empty — which is
  indistinguishable from "not vulnerable" — so consumers MUST NOT query public OSV as authoritative for
  `distribution: "private"` packages unless it is explicitly listed in `advisory_sources`.

### 5.2 Internal Advisory Sources

Organizations have three interoperable options, all expressed through `advisory_sources`:

1. **Internal OSV endpoint** (`type: "osv-internal"`): a service serving OSV-schema records with organization-local IDs
   (e.g. `ACME-2026-0001`) and `database_specific` fields. This is the RECOMMENDED option: internal advisories become
   consumable by the same tooling as public ones, and osv-scanner-style offline databases can merge public and internal
   records.
2. **Offline OSV database** (`type: "osv-local"`): a maintained archive of OSV JSON records in the per-ecosystem
   `all.zip` layout, for air-gapped environments.
3. **Platform-managed** advisories (Dependency-Track internal vulnerabilities, commercial SCA custom advisories) —
   exposed to agents by fronting them with an OSV-compatible query endpoint.

Public dependencies of a private package are still covered by public OSV; `advisory_sources` MAY therefore list both the
internal endpoint (authoritative for the package itself) and the public one (for its dependency tree).

### 5.3 Update Checks Against Private Indexes

`update_check.type: "pep700-index"` with the internal index URL. Consumers use the standard PEP 691/700 JSON index API —
again, no new protocol.

### 5.4 VEX for Internal Consumers

Organizations that ship affected-but-not-exploitable components SHOULD publish an internal VEX document and reference it
in `vex`, so internal scanners can suppress false positives with an auditable statement rather than an ignore-list.

## 6. Deprecating Interfaces

Lifecycle state at package granularity (§3 `support`) is not enough: individual functions, classes, and parameters
deprecate independently. This section binds Miri to the existing Python deprecation standards — each requirement cites
the PEP it derives from — and adds the machine-readable inventory and coherence verification those standards lack.

### 6.1 Code-Level Marking (PEP 702)

- Deprecated interfaces MUST be marked with the `@deprecated` decorator standardized by
  [PEP 702](https://peps.python.org/pep-0702/) — `warnings.deprecated` on Python ≥3.13, `typing_extensions.deprecated`
  earlier. This makes deprecations visible to static type checkers and IDEs at call sites without executing code, and
  emits a runtime `DeprecationWarning`.
- Module-level attributes and constants cannot carry the `@deprecated` decorator (PEP 702 applies to functions,
  classes, and overloads only). Deprecate them instead through a module-level `__getattr__` that emits a
  `DeprecationWarning` on access (`warnings.warn(msg, DeprecationWarning, stacklevel=2)`), naming the replacement and
  removal version in the message. Such attributes still appear in `migration-guide.json` `deprecations` but are exempt
  from the decorator requirement above.
- Runtime warning behavior follows the standard `warnings` categories with the default-visibility semantics of [PEP 565](https://peps.python.org/pep-0565/).
- The decorator message SHOULD name the replacement interface and the planned removal version.
- The deprecation window SHOULD follow the policy shape of [PEP 387](https://peps.python.org/pep-0387/): the marked
  interface keeps working, warning, for at least two releases before removal.

### 6.2 The Machine-Readable Inventory

PEP 702 markers are discoverable only by importing or type-checking the code — invisible to an agent inspecting
metadata. The build MUST therefore extract them into the `deprecations` array of
[migration-guide.json](agent-metadata-specification.md) (fields: `deprecated`, `replacement`, `removal_version`,
`migration`). The decorators are the single source of truth; the JSON inventory is derived at build time, never
hand-written — the same schema-as-data rule as the [CLI specification §2.3](../cli/cli-lifecycle-specification.md).

### 6.3 Registry-Level State

Interface deprecation composes with, and does not replace, the registry mechanisms:

- Whole releases are withdrawn from dependency resolution by yanking, per [PEP 592](https://peps.python.org/pep-0592/).
- Whole projects signal `archived` / `quarantined` through the status markers of
  [PEP 792](https://peps.python.org/pep-0792/), served by the index APIs. PEP 792 defines no successor pointer —
  `support.replacement` in `lifecycle.json` (§3) carries what PEP 792 cannot.

### 6.4 Deprecation Coherence (Verification)

No existing ecosystem tool verifies that deprecation markers, the changelog, and actual removals agree — changelog bots
(towncrier-style CI) enforce only that *an entry exists per change*, and API-diff tools (griffe, cargo-semver-checks,
japicmp) detect surface changes without cross-checking them against declared deprecations. Miri validation tooling MUST
therefore check, per release:

1. Every interface carrying a PEP 702 marker appears in `migration-guide.json` `deprecations`.
2. Every public interface removed since the previous release appeared in `deprecations` of at least one earlier release
   — **no silent removals**.
3. Every `deprecations` entry names a `replacement` that exists in the new release's `sdk-manifest.json`, and a
   `removal_version` greater than the release's own version.
4. Package-level `support.status` of `deprecated`/`eol` carries `replacement` (schema-enforced, [lifecycle-v1.json](../../schemas/lifecycle-v1.json)).

## 7. Agent Consumption Workflow

```python
import json, importlib.resources

meta = json.loads(
    importlib.resources.files("example_package")
    .joinpath("agent-metadata/lifecycle.json").read_text()
)

# 1. Vulnerability check: one query per advisory source
for source in meta["advisory_sources"]:
    # POST {"package": {"purl": meta["identity"]["purl"]}} to source["url"]
    # OSV response includes affected ranges and the *fixed* version
    ...

# 2. Currency check
# GET meta["update_check"]["url"] -> compare latest vs installed version

# 3. Lifecycle check: no network needed
if meta["support"]["status"] in ("deprecated", "eol"):
    successor = meta["support"]["replacement"]  # purl of what to use instead
```

The agent-facing consequence: a package resolved from frozen model weights can be validated in two calls, converting
silent staleness into a call-time check.

**Defining "latest" for the currency check.** The latest version is the highest version offered by `update_check` that
is (a) not yanked, (b) not a pre-release — unless the installed version is itself a pre-release — and (c) compatible
with the environment's `Requires-Python`. Before trusting the local `support.status`, a consumer SHOULD consult the
index's PEP 792 status markers: a `quarantined` or `archived` project overrides an artifact's self-declared `active`.

## 8. Conformance Requirements

A package conforms to this specification if:

1. `agent-metadata/lifecycle.json` is present, valid against the published JSON Schema, and generated at build time.
2. `identity.purl` matches the wheel's `dist-info/METADATA` name and version exactly.
3. At least one `advisory_sources` entry is present and reachable-by-construction (a well-formed URL or path, not a placeholder).
4. `distribution: "private"` packages do not list public OSV as their sole authoritative source.
5. `support.status` of `deprecated` or `eol` is accompanied by `replacement` when a successor exists.
6. Wheels bundling non-Python components include PEP 770 SBOM data in `.dist-info/sboms/` covering those components.
7. The deprecation coherence checks of §6.4 pass: PEP 702 markers, the `migration-guide.json` inventory, and actual
   removals agree, with no silent removals.

Validation tooling (planned, see [Python README](README.md)) will check 1–7 and additionally verify that the declared
registry serves the declared version.

---

## 9. Security Considerations

### 9.1 Threat Model

The metadata this standard defines is generated and shipped by the artifact it describes. **Once an artifact is
compromised — a maintainer account taken over, a malicious release published, a name typosquatted — every field it
carries is attacker-controlled.** `advisory_sources`, `update_check`, `support.replacement`, `vex`, and every
natural-language file (`prompt-templates.md`, `usage-patterns.json`, migration text, suggested fixes) can all be made
to lie. The adversary this section addresses is a package that was trustworthy when adopted and became malicious
later; nothing an artifact declares about its own security can be trusted on the artifact's word alone.

### 9.2 Anchor Trust Outside the Artifact

Artifact-declared `advisory_sources` and `update_check` are **hints, not authorities**. A consumer MUST decide which
advisory sources are authoritative for a package from its own policy — typically an organization-level allowlist keyed
by purl namespace, with public OSV as the default for public packages — and treat the artifact's list as a suggestion
to reconcile against that policy. In particular:

- A consumer MUST NOT forward credentials (index tokens, session cookies) to any URL declared by the artifact.
- All signal URLs are HTTPS-only (enforced by `lifecycle-v1.json`); a consumer MUST reject other schemes.
- An agent fetching artifact-declared URLs from inside a private network MUST guard against SSRF: block RFC 1918,
  link-local, and cloud metadata addresses, and re-validate the target after every redirect.

### 9.3 The Replacement Redirect

`support.replacement` and `migration-guide.json` together can redirect a consumer onto a *different* package. A
compromised release can set `status: deprecated` with `replacement: pkg:pypi/attacker-successor` and ship migration
steps that move working code onto the attacker's package. Therefore:

- A consumer MUST verify a `replacement` before acting on it — that the successor shares the original's publisher
  identity (e.g. via PEP 740 attestation), or that an organization policy has approved the redirect.
- An agent MUST NOT automatically install, or migrate code onto, a declared `replacement`. Auto-migration requires
  out-of-band verification or human confirmation.

### 9.4 Metadata Is Data, Never Instructions

All natural-language metadata — `prompt-templates.md`, `usage-patterns.json` code and prose, migration narratives, and
the `remediation`/`suggested_fix` text of checks — is untrusted input authored by the artifact's publisher. A consumer
MUST treat it as **data, never as instructions**. An agent MUST NOT execute a command, apply a fix, or follow a step
that appears in metadata without the same out-of-band verification or human confirmation it would require for any
untrusted source. Structured, authoritative-looking metadata is *more* dangerous here than plain documentation,
precisely because it invites the consumer to lower its guard.

### 9.5 What the Standard Does and Does Not Bind

`generated_at` and RECORD hashes bind an artifact to itself, not to any external authority; they detect accidental
drift, not tampering. The only field that ties an artifact to an independent identity is a PEP 740 attestation
(MIRI-PY-005), verified by the index against a Trusted Publisher. Provenance verification is therefore the foundation
every other trust decision in this section builds on.

## References

- Background: [CLI Update and Vulnerability Signaling](../cli/update-and-vulnerability-signaling.md)
- purl spec — <https://github.com/package-url/purl-spec>
- OSV schema — <https://ossf.github.io/osv-schema/>
- OSV.dev API — <https://google.github.io/osv.dev/api/>
- PyPA Advisory Database — <https://github.com/pypa/advisory-database>
- GitHub Advisory Database — <https://github.com/github/advisory-database>
- PEP 691/700 — JSON-based simple index API
- PEP 387 — Backwards compatibility policy — <https://peps.python.org/pep-0387/>
- PEP 565 — DeprecationWarning visibility — <https://peps.python.org/pep-0565/>
- PEP 592 — Yanked releases — <https://peps.python.org/pep-0592/>
- PEP 702 — Marking deprecations using the type system — <https://peps.python.org/pep-0702/>
- PEP 770 — SBOMs in Python packages — <https://peps.python.org/pep-0770/>
- PEP 792 — Project status markers in the index APIs — <https://peps.python.org/pep-0792/>
- OpenVEX — <https://github.com/openvex/spec>
- OpenEoX TC (OASIS) — <https://www.oasis-open.org/tc-openeox/> · Core Schema 1.0 CSD01 — <http://www.oasis-open.org/2026/07/14/invitation-to-comment-on-openeox-core-schema-version-1-0-csd01/>
- OWASP CLE and OpenEoX — <https://owasp.org/blog/2026/04/15/end-of-life-cle-and-openeox>
- endoflife.date — <https://endoflife.date/>
