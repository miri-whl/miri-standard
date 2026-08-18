# Python Standards

This directory contains specifications and documentation for Python-specific implementations of the Miri Standard.

## Overview

Python serves as the foundation language for the Miri Standard. This section documents both the existing Python
packaging ecosystem and how the Miri Standard extends it to enable enhanced agent-package communication.

## Current Standards

### Python Wheel Format Documentation

- **[Wheel Format Specification](wheel-format.md)** - Complete documentation of the current .whl format
- **[Packaging Standards Overview](packaging-standards.md)** - Summary of existing Python packaging standards and PEPs
- **[Metadata Standards](metadata-standards.md)** - Current metadata formats and their limitations

## Miri Extensions

### Current Specifications

- **[Miri Wheel Extensions](miri-wheel-extensions.md)** - Complete specification for agent-friendly wheel format extensions
- **[Agent Metadata Specification](agent-metadata-specification.md)** - Pre-parsed metadata formats for eliminating
  agent re-parsing
- **[Implementation Guide](implementation-guide.md)** - Practical guide to implementing Miri Standard in Python packages
- **[Lifecycle and Security Metadata](lifecycle-security-metadata.md)** - Package identity (purl), advisory sources,
  update checks, and deprecation state for open source and private packages
- **[Linter Checklist](linter-checklist.md)** - The 40 numbered checks (MIRI-PY-001…040) with standards references and
  scoring weights summing to 100
- **[Artifact Lifecycle](artifact-lifecycle.md)** - Every stage from build to EOL, the nested interface lifecycle, and
  the three-clocks model (diagrammed PDF available)

### Planned Specifications

- **[Agent Metadata Schema](agent-metadata-schema.md)** *(Planned)* - JSON schemas for validation
- **[Example Structure Specification](example-structure.md)** *(Planned)* - Detailed example organization guidelines
- **[Build Tools Integration](build-tools-integration.md)** *(Planned)* - Integration with setuptools, poetry, hatch

## Implementation

### Reference Implementation

- **[Python Miri Library](reference-implementation/)** *(Planned)*
- **[Validation Tools](validation-tools/)** *(Planned)*
- **[Examples and Templates](examples/)** *(Planned)*

## Background

The Python ecosystem provides an excellent starting point for the Miri Standard because:

1. **Mature Packaging**: Well-established wheel format and metadata standards
2. **Agent Adoption**: High usage in AI/ML development and automation
3. **Extensible Format**: Wheel format allows for additional metadata files
4. **Rich Ecosystem**: Large number of packages that would benefit from agent-friendly metadata

## Resources

- [Python Packaging Authority (PyPA)](https://www.pypa.io/)
- [Python Enhancement Proposals (PEPs)](https://peps.python.org/)
- [Wheel Documentation](https://wheel.readthedocs.io/)
- [Python Packaging User Guide](https://packaging.python.org/)
