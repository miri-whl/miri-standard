# Miri Standard: Package Lifecycle and Security Metadata (Python)

*Specification Version: 0.1-draft*
*Status: Draft*
*Created: 2026*

## Abstract

This specification defines how a Miri-compliant Python package declares its identity, advisory sources, and lifecycle state so that agents and scanners can answer two questions at call time: **"is this package vulnerable?"** and **"is this package current?"**. It adds one file, `agent-metadata/lifecycle.json`, to the structure defined in the [Agent Metadata Specification](agent-metadata-specification.md).

The design reuses the existing open source security stack — [purl](https://github.com/package-url/purl-spec) for identity and the [OSV schema](https://ossf.github.io/osv-schema/) for advisories — rather than inventing a parallel one. The package never asserts its own security status; it declares **who it is** and **where authoritative answers live**, for both open source and private distribution. Background and rationale: [CLI Update and Vulnerability Signaling](../cli/update-and-vulnerability-signaling.md).

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Design Principles](#2-design-principles)
3. [The lifecycle.json File](#3-the-lifecyclejson-file)
4. [Open Source Packages](#4-open-source-packages)
5. [Private and Internal Packages](#5-private-and-internal-packages)
6. [Agent Consumption Workflow](#6-agent-consumption-workflow)
7. [Conformance Requirements](#7-conformance-requirements)

---

## 1. Problem Statement

"This package must be updated" is never knowledge the package holds. It is computed externally as a join:

> (installed identity + version) × (advisory database with affected ranges and a `fixed` version)

For public PyPI packages the join works today because both legs are standardized: `dist-info/METADATA` provides identity+version, and OSV.dev (aggregating PYSEC, GHSA, and CVE data) provides advisories. But three gaps remain that this specification closes:

1. **Agents don't know where to look.** A scanner has OSV hardcoded; an agent working with an arbitrary package does not know which advisory sources are authoritative for it — especially for packages from private indexes, where OSV.dev has no data and will silently return "no vulnerabilities."
2. **Private packages have no identity convention.** Internal packages lack a purl namespace agreement, so internal advisory records have nothing reliable to attach to.
3. **Lifecycle state beyond vulnerabilities is undeclared.** Deprecation, end-of-life, and successor packages live in READMEs and changelogs — invisible to an agent that resolves the package from frozen weights.

## 2. Design Principles

### 2.1 Declare Sources, Not Verdicts

A package MUST NOT embed claims like "no known vulnerabilities" — such a claim is stale the moment it is built. `lifecycle.json` declares *identity* and *pointers to live sources*; the verdict is always computed by the consumer at call time.

### 2.2 Reuse the Existing Stack

Identity is a purl. Advisories are OSV records. Update state comes from the package index the package was installed from. This specification defines no new advisory format and no new version-comparison rules.

### 2.3 Same Shape for Open Source and Private

A private package differs from a public one only in *values* (a private purl namespace, an internal OSV endpoint, an internal index URL) — never in *structure*. Tooling written against this spec works unchanged in both worlds.

### 2.4 Build-Time Generation

Like all Miri agent metadata, `lifecycle.json` SHOULD be generated at build time from `pyproject.toml` plus Miri-specific configuration, never hand-maintained per release.

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

### 3.2 Relationship to SBOMs (PEP 770)

`lifecycle.json` identifies the package itself; it does not describe what the package *bundles*. That is the job of an SBOM, and Python already has a standard for it: [PEP 770](https://peps.python.org/pep-0770/) (accepted 2025) places SBOM documents in `.dist-info/sboms/`, discoverable by scanners without any Miri-specific pointer.

- A pure-Python package MAY omit SBOMs — `Requires-Dist` plus installed dist-info already expose its dependency tree, and a Miri requirement here would duplicate PyPA machinery.
- A package bundling **non-Python components** (vendored C libraries, statically linked OpenSSL, Rust extensions — the "phantom dependency" problem) MUST ship PEP 770 SBOM data covering them. Build tooling makes this nearly free: auditwheel (≥6.5.0) generates it automatically when repairing wheels.

The two artifacts divide cleanly: advisories against the *package* join on `identity.purl` via `advisory_sources`; advisories against *bundled components* join on the purls inside the PEP 770 SBOM. Consumers performing a full vulnerability check evaluate both.

## 4. Open Source Packages

For `distribution: "open-source"` packages published to PyPI:

### 4.1 Defaults

- `advisory_sources` MUST include the public OSV endpoint with `ecosystem: "PyPI"`. Build tools SHOULD inject this entry automatically.
- `update_check` MUST point at the PyPI JSON API for the package.
- `identity.purl` MUST use the `pkg:pypi/` type with the normalized (PEP 503) project name.

### 4.2 Publishing Advisories

Maintainers of Miri-compliant packages SHOULD publish vulnerabilities through the standard home-database path so they flow to every consumer automatically:

1. File a **GitHub repository security advisory** (which can request a CVE via GitHub-as-CNA), or submit directly to the [PyPA Advisory Database](https://github.com/pypa/advisory-database).
2. The advisory propagates GHSA/PYSEC → OSV.dev → all scanners and agents.
3. Corrections go to the home database, never to downstream aggregators.

No Miri-specific publication step exists or is needed — this is deliberate (§2.2).

### 4.3 Deprecating a Package

When a package enters `deprecated` or `eol`, the final releases MUST carry the updated `support` block with `replacement` set. Because agents read `lifecycle.json` from the *installed* wheel, this reaches every future install even if the user never reads the README. The [migration-guide.json](agent-metadata-specification.md) file carries the how; `support.replacement` carries the what.

## 5. Private and Internal Packages

For `distribution: "private"` packages published to internal indexes (Artifactory, Nexus, devpi, CodeArtifact, simple private indexes):

### 5.1 Identity

- Internal packages MUST still carry a purl. The RECOMMENDED convention is the standard `pkg:pypi/` type with the organization's private index in a purl qualifier: `pkg:pypi/acme-billing@3.2.0?repository_url=https://pypi.internal.acme.example/simple/`.
- `identity.registry` MUST name the internal index. Public OSV lookups against private names return empty — which is indistinguishable from "not vulnerable" — so consumers MUST NOT query public OSV as authoritative for `distribution: "private"` packages unless it is explicitly listed in `advisory_sources`.

### 5.2 Internal Advisory Sources

Organizations have three interoperable options, all expressed through `advisory_sources`:

1. **Internal OSV endpoint** (`type: "osv-internal"`): a service serving OSV-schema records with organization-local IDs (e.g. `ACME-2026-0001`) and `database_specific` fields. This is the RECOMMENDED option: internal advisories become consumable by the same tooling as public ones, and osv-scanner-style offline databases can merge public and internal records.
2. **Offline OSV database** (`type: "osv-local"`): a maintained archive of OSV JSON records in the per-ecosystem `all.zip` layout, for air-gapped environments.
3. **Platform-managed** advisories (Dependency-Track internal vulnerabilities, commercial SCA custom advisories) — exposed to agents by fronting them with an OSV-compatible query endpoint.

Public dependencies of a private package are still covered by public OSV; `advisory_sources` MAY therefore list both the internal endpoint (authoritative for the package itself) and the public one (for its dependency tree).

### 5.3 Update Checks Against Private Indexes

`update_check.type: "pep700-index"` with the internal index URL. Consumers use the standard PEP 691/700 JSON index API — again, no new protocol.

### 5.4 VEX for Internal Consumers

Organizations that ship affected-but-not-exploitable components SHOULD publish an internal VEX document and reference it in `vex`, so internal scanners can suppress false positives with an auditable statement rather than an ignore-list.

## 6. Agent Consumption Workflow

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

The agent-facing consequence: a package resolved from frozen model weights can be validated in two calls, converting silent staleness into a call-time check.

## 7. Conformance Requirements

A package conforms to this specification if:

1. `agent-metadata/lifecycle.json` is present, valid against the published JSON Schema, and generated at build time.
2. `identity.purl` matches the wheel's `dist-info/METADATA` name and version exactly.
3. At least one `advisory_sources` entry is present and reachable-by-construction (a well-formed URL or path, not a placeholder).
4. `distribution: "private"` packages do not list public OSV as their sole authoritative source.
5. `support.status` of `deprecated` or `eol` is accompanied by `replacement` when a successor exists.
6. Wheels bundling non-Python components include PEP 770 SBOM data in `.dist-info/sboms/` covering those components.

Validation tooling (planned, see [Python README](README.md)) will check 1–6 and additionally verify that the declared registry serves the declared version.

---

## References

- Background: [CLI Update and Vulnerability Signaling](../cli/update-and-vulnerability-signaling.md)
- purl spec — https://github.com/package-url/purl-spec
- OSV schema — https://ossf.github.io/osv-schema/
- OSV.dev API — https://google.github.io/osv.dev/api/
- PyPA Advisory Database — https://github.com/pypa/advisory-database
- GitHub Advisory Database — https://github.com/github/advisory-database
- PEP 691/700 — JSON-based simple index API
- PEP 770 — SBOMs in Python packages — https://peps.python.org/pep-0770/
- OpenVEX — https://github.com/openvex/spec
