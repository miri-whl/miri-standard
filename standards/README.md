# Miri Standard Specifications

This directory contains the official specifications and standards for agent-friendly package extensions across all
programming languages.

## Overview

The Miri Standard develops specifications that enable rich, structured communication between software packages and
autonomous agents, transcending language boundaries. Named after Miranda Serena Sharifi from "Beggars in Spain," these
standards address the "thought-string gaps" in current packaging systems—missing information that prevents agents from
reaching their full potential in understanding and using software libraries.

**Multi-Language Vision**: While we begin with Python wheel extensions, the Miri Standard's core principles apply
universally. The same metadata structures that enhance Python packages will extend to npm packages, Ruby gems, Rust
crates, Go modules, and all major packaging ecosystems.

### The Problem: Structural Flaws in Package Communication

Just as Miri's thought-strings had gaps where information should be, current Python packages have structural flaws:

- **Missing Context**: Agents can't determine complexity levels or learning paths
- **Scattered Examples**: Code samples are dispersed across READMEs, docs, and external sites  
- **No Relationships**: Dependencies and related packages lack structured connections
- **Linear Discovery**: Sequential documentation reading prevents instant capability assessment

### The Solution: Complete Metadata Structures

Miri Standard specifications define complete, multi-dimensional metadata that fills these gaps:

- **Structured Examples**: Organized by complexity, category, and learning progression
- **Rich Templates**: With clear placeholders and usage instructions
- **Contextual Metadata**: Relationships, prerequisites, and capability descriptions
- **Instant Discovery**: JSON schemas enabling immediate package comprehension

## Language-Specific Standards

### Python Standards

- **[Python Overview](python/)** - Complete Python packaging documentation and Miri extensions
- **[Wheel Format Specification](python/wheel-format.md)** - Comprehensive documentation of current .whl format
- **[Packaging Standards Overview](python/packaging-standards.md)** - Summary of existing Python packaging standards and
  PEPs
- **Metadata Standards** *(Planned)*

### CLI Standards

- **[CLI Overview](cli/)** - CLI standards, background research, and planned specifications
- **[CLI Lifecycle and Vulnerability Signaling](cli/cli-lifecycle-specification.md)** - Self-identification, advisory
  sources, update checks, and deprecation metadata for open source and private CLIs
- **[CLI Linter Checklist](cli/linter-checklist.md)** - 43 numbered, weighted conformance checks for scoring CLIs 0–100
- **[CLI Artifact Lifecycle](cli/artifact-lifecycle.md)** - Stages from release to withdrawal with the nested surface lifecycle
- **[Agent CLI Landscape and Prior Art](cli/landscape-and-prior-art.md)** - Survey of existing CLI standards, 2026
  agent-CLI efforts, and the open gaps (lifecycle, versioning, introspection) that scope Miri's CLI work
- **[Update and Vulnerability Signaling](cli/update-and-vulnerability-signaling.md)** - How the library world computes
  "must be updated" (purl + OSV + installed inventory), why standalone CLIs are illegible to that machinery, and what
  Miri should require (self-identification, update-check primitive)

### Go Standards

- **[Go Overview](go/)** - Scope sketch: agent metadata for modules, lifecycle metadata, structured examples, and the Go
  CLI conformance profile — building on embedded buildinfo, govulncheck, and testable examples

### Rust Standards

- **[Rust Overview](rust/)** - Scope sketch: agent metadata for crates, lifecycle metadata, structured examples, and the
  Rust CLI conformance profile — building on `#[deprecated]`, RustSec, cargo-semver-checks, and cargo auditable

### Future Language Standards

- **JavaScript/npm** *(Planned)*

## Specification Status

### Published Standards

*(No published standards yet).*

### Draft Standards

- **[Python Wheel Format Documentation](python/wheel-format.md)** - Complete reference for current wheel format
- **[Python Packaging Standards](python/packaging-standards.md)** - Overview of existing Python packaging ecosystem
- **[Miri Wheel Extensions](python/miri-wheel-extensions.md)** - Agent-friendly Python wheel format extensions specification
- **[Agent Metadata Specification](python/agent-metadata-specification.md)** - Pre-parsed metadata formats for
  performance optimization
- **[Python Implementation Guide](python/implementation-guide.md)** - Practical guide to implementing Miri Standard in
  Python packages
- **[Python Lifecycle and Security Metadata](python/lifecycle-security-metadata.md)** - Package identity, advisory
  sources, and lifecycle state for open source and private packages
- **[Python Linter Checklist](python/linter-checklist.md)** - 40 numbered, weighted conformance checks for scoring
  wheels 0–100
- **[Python Artifact Lifecycle](python/artifact-lifecycle.md)** - Stages from build to archival with the nested
  interface lifecycle
- **[CLI Lifecycle and Vulnerability Signaling](cli/cli-lifecycle-specification.md)** - CLI self-identification,
  advisory sources, update checks, and deprecation metadata

### Proposed Standards

*(Proposed standards will be listed here).*

## Specification Structure

Each specification includes:

- **Abstract**: Brief overview of the specification's purpose
- **Introduction**: Background and motivation
- **Terminology**: Definitions of key terms
- **Requirements**: Normative requirements and specifications
- **Examples**: Non-normative examples and use cases
- **Security Considerations**: Security implications and guidelines
- **References**: Related standards and documents

## Versioning

Specifications use semantic versioning:

- **Major Version**: Breaking changes or significant new features
- **Minor Version**: Backward-compatible additions
- **Patch Version**: Bug fixes and clarifications

## Development Process

1. **Proposal**: New specifications start as proposals in the [proposals/](../proposals/) directory
2. **Draft**: Approved proposals become draft specifications
3. **Review**: Community review and feedback period
4. **Revision**: Specifications updated based on feedback
5. **Approval**: Final approval by SIG-Spec and project maintainers
6. **Publication**: Specifications published with stable version numbers

## Implementation

### Reference Implementations

Reference implementations are provided to demonstrate specification compliance and serve as examples for implementers.

### Conformance Testing

Test suites are developed to validate specification compliance. Implementations can use these tests to verify conformance.

### Certification

*(Certification process to be defined as project matures).*

## Contributing

To contribute to specification development:

1. Review the [Contributing Guidelines](../CONTRIBUTING.md)
2. Join [SIG-Spec](../community/sig-spec/)
3. Participate in specification discussions
4. Submit proposals for new specifications
5. Review and provide feedback on draft specifications

## Resources

- [SIG-Spec](../community/sig-spec/): Specification development group
- [Proposals](../proposals/): Proposed new specifications
- [Community](../community/): Community organization and communication
- [Contributing](../CONTRIBUTING.md): How to contribute to the project

## Contact

- **Specification Questions**: Use GitHub Discussions with the `specification` label
- **Technical Issues**: Create GitHub issues with the `specification` label
- **SIG-Spec**: Join SIG-Spec meetings and discussions
