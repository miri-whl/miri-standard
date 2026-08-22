# miri-standard

<p align="center">
  <img src="assets/img/miri-grey.png" alt="MIRI Logo" width="200"/>
</p>

[![CI](https://github.com/miri-whl/miri-standard/workflows/CI/badge.svg)](https://github.com/miri-whl/miri-standard/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE-OF-CONDUCT.md)

> **Status**: 🚧 Incubation Phase - This project is in early development

**Packaging standards that make software artifacts legible to AI agents — and to the tools that vet them.**

*Named after Miranda Serena Sharifi from Nancy Kress's "Beggars in Spain".*

## Overview

The Miri Standard defines structured metadata that ships *inside* a software artifact — offline and version-locked to
the code — declaring its identity, where to check it for advisories, its support and deprecation status, and,
optionally, a machine-readable map of its API and examples. An agent or a security scanner reads that context straight
from the installed artifact instead of guessing the package's name, re-deriving its version, or hard-coding where to
look for vulnerabilities.

Its most defensible layer is small and hand-authorable: **Miri Core** — identity, security, and lifecycle signaling a
well-maintained package can adopt in a day. A `lifecycle.json` carried in the wheel looks like this:

```json
{
  "identity": {
    "purl": "pkg:pypi/weather-sdk@1.2.0",
    "registry": "https://pypi.org/simple/"
  },
  "advisory_sources": [
    { "type": "osv", "ecosystem": "PyPI", "url": "https://api.osv.dev/v1/query" }
  ],
  "support": { "status": "active", "supported_versions": [">=1.0,<2.0"] }
}
```

The guiding rule is *declare sources, not verdicts*: the artifact points at live sources; the consumer computes the
answer at call time. On top of Core, the **Full** profile adds the richer agent-facing surface — a structured API
index, usage examples, and deprecation-coherence machinery so a removal is never silent.

The standard starts with Python wheels and command-line tools; Go and Rust are early scope sketches (see
[Language Roadmap](#language-roadmap)). The name is a metaphor: just as Miranda Sharifi's "thought-strings" had "gaps
where information ought to go," packages carry code but not the machine-readable context around it, and Miri fills those
gaps.

> 📖 **Read the origin story**: [Where the name comes from](docs/origin-story.md)

## Who It's For

- **Security and supply-chain teams** — the natural home for Miri Core: purl identity plus authoritative advisory
  sources let a scanner resolve "is this artifact affected?" from the artifact itself, and deprecation/EOL signals with
  a named replacement drive migration.
- **Agent and tooling builders** — a stable, offline place to read a package's identity, API surface, and lifecycle
  state without scraping source or docs on every call.
- **Package maintainers** — a low-effort way (Core is hand-authorable) to make an artifact honest about what it is, how
  to reach its advisories, and what replaces it when it goes away.

## Core Principles

The standard is built on six design principles:

- **Declare sources, not verdicts.** Artifacts declare identity (purl) and advisory sources; consumers compute verdicts
  at call time. A package never claims "no vulnerabilities."
- **Reuse the existing stack.** Identity is purl; advisories are OSV records; SBOMs follow PEP 770 and CycloneDX/SPDX.
  Miri defines no parallel formats.
- **Same shape for open source and private.** Private artifacts differ only in values (private namespace, internal OSV
  endpoint), never in structure.
- **Schema as data, derived outputs.** One source generates both human docs and machine metadata.
- **Deprecation coherence.** Markers, changelog, and removals must agree; no silent removals.
- **Citation trail.** Every normative statement cites the standard it derives from (PEP, RFC, OSV, POSIX/GNU).

## How Miri Relates to Other Approaches

Miri deliberately builds on the existing ecosystem rather than replacing it, and it is not a competitor to the
following — it occupies the gap between them:

- **Docstrings, type stubs (`.pyi`)** ship in the wheel but describe *how to call* the code, not its identity, advisory
  sources, or lifecycle state. Miri is machine-checked and covers those.
- **`llms.txt`** is a repository-level, human-authored context file for LLMs; Miri is per-artifact, schema-validated,
  and version-locked to the installed code.
- **MCP** exposes *runtime* tools an agent calls; Miri is *static* metadata read at install time — the two compose.
- **Agent Skills** package instructions for an agent; Miri describes the software artifact itself.
- **SBOM / OSV / PEP 740** are the supply-chain primitives Miri *reuses*. Miri's addition is the in-artifact contract
  that binds them together and the coherence guarantee — notably "no silent removals" — that none of them checks on
  their own.

## Project Status

The Miri Standard is at **version 0.2-draft**, in its **Incubation** phase (see `MATURITY.md`). It is an early,
unratified draft: the shape of the standard is still moving, and its benefits to agents are design goals rather than
measured results.

### What exists today

- Normative specifications for Python wheels and command-line tools, under `standards/`.
- JSON Schemas for every metadata file and for the check-definition format, under `schemas/`.
- 83 machine-readable check definitions (40 Python, 43 CLI) with assigned severities and weights.
- Weighted linter checklists ([Python](standards/python/linter-checklist.md),
  [CLI](standards/cli/linter-checklist.md)), each summing to 100.
- The **Miri Core** and **Miri Full** conformance profiles — Core is a 15-check hand-authorable subset, the recommended
  adoption on-ramp.
- A **security-considerations / threat model** for the metadata agents consume (metadata is untrusted data, never
  instructions) in the [lifecycle and security spec](standards/python/lifecycle-security-metadata.md).
- A CLI `--describe` introspection schema ([`cli-describe-v1`](schemas/cli-describe-v1.json)) backing the CLI checks.
- A [published site](https://miri-whl.github.io/) generated from the check definitions.

### In progress and planned

- A reference linter (miri-py) implementing the checks — in development; not yet published to PyPI. A pointer will be
  added here once it is public.
- A published measurement study supporting the standard's agent-performance goals — planned.
- Go and Rust support — scope sketches only, not yet specified.

### Known limitations

- Some checks and their examples are still being reconciled with the reference implementation.
- Conformance tiers and scoring semantics are still stabilizing.
- No published measurement yet supports the standard's agent-performance goals.

## Quick Start

The Miri Standard is a specification, not a tool you install. To get oriented:

- **Read the standard** — start with the [Python standards overview](standards/python/README.md) and the
  [lifecycle and security metadata spec](standards/python/lifecycle-security-metadata.md).
- **Browse the checks** — the [Python linter checklist](standards/python/linter-checklist.md) lists all 40 numbered
  checks with their weights and severities; each check's machine-readable definition lives under
  `standards/python/checks/`, and every check has a page on the [published site](https://miri-whl.github.io/).
- **Validate an artifact** — the reference linter, miri-py, is in development; a pointer will be added here once it is
  published.

## Language Roadmap

Miri is developed one artifact type at a time. Each target gets a parallel spec suite under `standards/<type>/`.
The roadmap is deliberately narrow — new targets are added only when the existing ones are stable.

| Target | What it covers | Status |
| --- | --- | --- |
| **Python wheels** | `agent-metadata/` in the wheel, `lifecycle.json`, 40 checks | Developed (0.2-draft) |
| **Command-line tools** | `--describe`, `check-update`, `changelog --since`, per-flag lifecycle, 43 checks | Developed (0.2-draft) |
| **Go modules** | What `go.mod` / the module proxy already provide vs. what Miri adds | Scope sketch |
| **Rust crates** | What `Cargo.toml` / crates.io already provide vs. what Miri adds | Scope sketch |
| Other ecosystems (npm, Java, …) | — | Exploratory, not scheduled |

Because the metadata reuses ecosystem-neutral primitives (purl, OSV, SBOM), the same identity/advisory/lifecycle shape
is intended to carry across targets; only the values and the packaging surface change.

## Standards

Current specifications and standards:

- [Standards Directory](standards/) - Published and draft specifications
- [Proposals](proposals/) - Proposed new standards under development

## Community

### Getting Involved

- 📖 Read our [Contributing Guidelines](CONTRIBUTING.md)
- 💬 Join discussions in [GitHub Discussions](https://github.com/miri-whl/miri-standard/discussions)
- 🤝 Follow our [Code of Conduct](CODE-OF-CONDUCT.md)
- 📅 Attend community meetings (schedule TBD)

### Special Interest Groups (SIGs)

- **[SIG-Community](community/sig-community/)** - Community building and governance
- **[SIG-Spec](community/sig-spec/)** - Standards development and technical specifications

### Communication

- **GitHub Discussions**: General questions and community discussions
- **GitHub Issues**: Bug reports, feature requests, and technical discussions
- **Community Meetings**: [Schedule to be announced]

## Project Structure

```text
miri-standard/
├── community/          # Community organization and SIG information
├── standards/          # Published specifications and standards
├── proposals/          # Proposed new standards and changes
├── docs/              # Project documentation
├── images/            # Images and diagrams
├── .github/           # GitHub workflows and templates
├── CODE-OF-CONDUCT.md # Community code of conduct
├── CONTRIBUTING.md    # Contribution guidelines
├── GOVERNANCE.md      # Project governance model
├── MATURITY.md        # Project maturity framework
├── LICENSE            # MIT License
└── README.md          # This file
```

## Governance

This project follows an open governance model:

- **[Governance Document](GOVERNANCE.md)** - Detailed governance structure
- **[Maturity Model](MATURITY.md)** - Project maturity phases and criteria
- **[Code of Conduct](CODE-OF-CONDUCT.md)** - Community standards and enforcement

### Leadership

The project is in **Incubation** with a **single maintainer** — Emiliano Berenbaum (@y3bishop3y) — who authors the
specifications and makes technical and governance decisions, with all drafts public and open for review. A Steering
Committee and SIG leads will be established as a contributor community forms (see [GOVERNANCE.md](GOVERNANCE.md)).

## Contributing

We welcome contributions from everyone! Here's how to get started:

1. **Read** our [Code of Conduct](CODE-OF-CONDUCT.md)
2. **Review** the [Contributing Guidelines](CONTRIBUTING.md)
3. **Join** a [Special Interest Group](community/)
4. **Start** contributing to discussions, documentation, or code

### Areas of Contribution

- 📝 **Standards Development** - Help develop and refine specifications
- 📚 **Documentation** - Improve project documentation and guides
- 🏗️ **Implementation** - Create reference implementations and examples
- 🧪 **Testing** - Develop test suites and validation tools
- 🌍 **Community** - Help grow and support the community
- 🎤 **Outreach** - Present at conferences, write blog posts, create tutorials

## License

This project is licensed under the [MIT License](LICENSE).

## Security

For security concerns, please see our [Security Policy](SECURITY.md) (to be created).

## Acknowledgments

This project is inspired by successful open source standards projects, particularly the
[SPIFFE project](https://github.com/spiffe/spiffe), and follows best practices from the open source community.

---

**Project Status**: This project is currently in the Incubation phase. See [MATURITY.md](MATURITY.md) for details on our
maturity model and current progress.
