# miri-standard

<p align="center">
  <img src="assets/img/miri-grey.png" alt="MIRI Logo" width="200"/>
</p>

[![CI](https://github.com/[GITHUB_ORG]/miri-standard/workflows/CI/badge.svg)](https://github.com/[GITHUB_ORG]/miri-standard/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE-OF-CONDUCT.md)

> **Status**: 🚧 Incubation Phase - This project is in early development

**Multi-language packaging standards for enhanced human-agent collaboration.**

*Named after Miranda Serena Sharifi from Nancy Kress's "Beggars in Spain".*

## Overview

The Miri Standard addresses a fundamental gap in how software packages communicate with autonomous agents across all
programming languages. Just as Miranda Sharifi's "thought-strings" had structural flaws that prevented enhanced beings
from reaching their full potential, current packaging systems have gaps where agent-useful information should be—but
isn't.

**Starting with Python wheels, expanding to all languages.** While our initial implementation focuses on Python wheel
extensions, the Miri Standard's principles and specifications are designed to be language-agnostic. The same
"thought-string" approach that fills gaps in Python packaging will extend to npm packages, Ruby gems, Rust crates, Go
modules, and beyond.

The Miri Standard fills these gaps by defining rich, structured metadata that enables agents to instantly understand
package capabilities, discover examples, and access learning paths without external lookups or sequential documentation
reading.

### The Vision: From Linear Documentation to Thought-String Communication

Traditional package documentation follows a linear model that forces both humans and agents through sequential discovery
across all languages:

1. Read README → 2. Check docs → 3. Search examples → 4. Trial and error

The Miri Standard enables "thought-string" style information transfer that transcends language boundaries:

1. Install package → 2. Instantly discover all capabilities → 3. Access structured examples and templates → 4.
   Understand relationships and learning paths

This represents an evolution from language-specific, word-based documentation to universal, multi-dimensional metadata
structures that serve both human developers and autonomous agents regardless of the underlying programming language.

> 📖 **Read the full origin story**: [From Thought-Strings to Agent Communication](docs/origin-story.md)

## Core Principles

The Miri Standard is built on four foundational principles inspired by Miranda Sharifi's journey:

### 1. **Structural Completeness** 🧩

No gaps where information should be. Every Miri-compliant package includes complete metadata schemas with required
fields for agent comprehension.

### 2. **Multi-Dimensional Information** 🌐

Beyond linear documentation. Packages provide examples, templates, learning paths, and contextual relationships simultaneously.

### 3. **Immediate Discovery** ⚡

Instant capability assessment. Agents can understand package functionality without external lookups or sequential reading.

### 4. **Enhanced Collaboration** 🤝

Serving both humans and agents. Better structured information benefits all developers while enabling new forms of
AI-assisted development.

## Quick Start

[QUICK START GUIDE TO BE ADDED]

## Language Roadmap

The Miri Standard follows a strategic multi-language expansion plan:

### Phase 1: Python Foundation 🐍

- **Current Focus**: Python wheel extensions (.whl)
- **Status**: In development
- **Goal**: Establish core metadata schemas and validation frameworks

### Phase 2: JavaScript Ecosystem 📦

- **Target**: npm packages (package.json extensions)
- **Planned**: Q2 2025
- **Focus**: Node.js and browser-based package discovery

### Phase 3: Systems Languages 🦀

- **Rust**: Cargo.toml extensions for crates
- **Go**: go.mod metadata enhancements  
- **C/C++**: Package manager agnostic solutions

### Phase 4: Enterprise Languages ☕

- **Java**: Maven/Gradle integration
- **C#**: NuGet package extensions
- **Scala**: sbt compatibility

### Universal Principles Across All Languages

Regardless of the target language, every Miri implementation will provide:

- **Structured Examples**: Language-appropriate code samples with complexity levels
- **Rich Templates**: Boilerplate code with clear placeholders
- **Contextual Metadata**: Dependencies, relationships, and learning paths
- **Instant Discovery**: JSON schemas for immediate capability assessment

## Standards

Current specifications and standards:

- [Standards Directory](standards/) - Published and draft specifications
- [Proposals](proposals/) - Proposed new standards under development

## Community

### Getting Involved

- 📖 Read our [Contributing Guidelines](CONTRIBUTING.md)
- 💬 Join discussions in [GitHub Discussions](../../discussions)
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

- **Steering Committee**: [To be established]
- **Maintainers**: [To be assigned]
- **SIG Leads**: [To be assigned]

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
