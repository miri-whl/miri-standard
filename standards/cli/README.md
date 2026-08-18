# CLI Standards

This directory contains specifications and background research for making command-line tools legible to autonomous agents — the CLI counterpart to the [Python packaging standards](../python/).

## Overview

Where the Python standards extend the wheel format so agents can understand a *library*, the CLI standards define what a *command-line tool* must expose so agents can discover its capabilities, trust its identity, and track its lifecycle: introspection, versioning, deprecation, update checks, and vulnerability signaling — for both open source and private/internal CLIs.

## Current Specifications

- **[CLI Lifecycle and Vulnerability Signaling](cli-lifecycle-specification.md)** *(Draft)* - Self-identification (purl), advisory sources, `check-update`, machine-readable changelog, and deprecation metadata; covers open source and private CLIs
- **[Linter Checklist](linter-checklist.md)** *(Draft)* - The 43 numbered checks (MIRI-CLI-001…043) with standards references and scoring weights summing to 100
- **[Artifact Lifecycle](artifact-lifecycle.md)** *(Draft)* - Every stage from release to withdrawal, the nested surface lifecycle, and the three-clocks model (diagrammed PDF available)

### Planned Specifications

- **Introspection Schema** *(Planned)* - Normative JSON Schema for `--describe` output with conformance tests (landscape doc §4.1)
- **Stability Contract** *(Planned)* - Required artifact defining what SemVer covers for a CLI (landscape doc §3.4)
- **Skill-File Regeneration** *(Planned)* - Specified command for regenerating `SKILL.md` from the installed binary (landscape doc §4.5)

## Background Research

- **[Agent CLI Landscape and Prior Art](landscape-and-prior-art.md)** - Survey of existing CLI standards (POSIX, GNU, clig.dev), the 2026 agent-CLI efforts, and the open gaps that scope Miri's CLI work
- **[Update and Vulnerability Signaling](update-and-vulnerability-signaling.md)** - How the library world computes "must be updated" (purl + OSV + installed inventory), why standalone CLIs are illegible to that machinery, and the options for private libraries and CLIs
