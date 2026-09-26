# Miri Standard: Agent-Friendly Python Wheel Extensions

*Specification Version: 0.2-draft*  
*Status: Draft*  
*Created: 2025*

## Abstract

This specification defines extensions to the Python wheel format (PEP 427) that enable enhanced communication
between Python packages and autonomous agents. The Miri Standard addresses the "thought-string gaps" in current Python
packaging by adding structured metadata, embedded examples, and discovery mechanisms that allow agents to immediately
understand and use packages without external documentation lookups.

## Table of Contents

1. [Overview & Problem Statement](#1-overview--problem-statement)
2. [Design Principles](#2-design-principles)
3. [Extension Strategy](#3-extension-strategy)
4. [Metadata File Specifications](#4-metadata-file-specifications)
5. [Package Structure Extensions](#5-package-structure-extensions)
6. [Discovery and Access APIs](#6-discovery-and-access-apis)
7. [Implementation Requirements](#7-implementation-requirements)
8. [Compatibility and Migration](#8-compatibility-and-migration)
9. [Validation and Conformance](#9-validation-and-conformance)

## 1. Overview & Problem Statement

### 1.1 Goal

Enable autonomous agents (code assistants, code generators, automated development tools) to immediately understand and
utilize Python packages after installation via standard package managers, without requiring external documentation
lookups or sequential text processing.

### 1.2 Current Limitations

Traditional Python packaging creates barriers for agent comprehension:

- **Scattered Information**: Examples in READMEs, documentation on websites, tutorials in blogs
- **Unstructured Content**: Free-form text descriptions lack semantic structure
- **Sequential Discovery**: Linear documentation reading prevents instant capability assessment
- **Missing Context**: No complexity indicators, learning paths, or relationship data
- **External Dependencies**: Agents must fetch information from multiple sources

### 1.3 Miri Solution

The Miri Standard fills these gaps by extending the wheel format with:

- **Structured Metadata**: JSON schemas for programmatic consumption
- **Embedded Examples**: Categorized, runnable code samples included in the package
- **Rich Templates**: Boilerplate code with clear placeholders
- **Discovery APIs**: Runtime access to all agent-relevant information
- **Learning Paths**: Structured progression through package capabilities

## 2. Design Principles

### 2.1 Backward Compatibility

All Miri extensions MUST maintain full compatibility with existing Python packaging tools:

- Standard `pip install` workflow unchanged
- Existing metadata formats preserved
- Non-Miri-aware tools continue to function normally

### 2.2 Additive Enhancement

Miri metadata supplements rather than replaces existing information:

- New files added to `.dist-info/` directory
- Optional package data directories
- Enhanced but compatible docstrings
- Graceful degradation when Miri tools unavailable

### 2.3 Immediate Discovery

All agent-relevant information MUST be accessible without external lookups:

- Complete examples bundled in the package
- Structured metadata agents can read without re-deriving it from prose
- Self-contained documentation
- Runtime discovery APIs

### 2.4 Multi-Dimensional Information

Information provided in multiple formats simultaneously:

- JSON metadata for programmatic access
- Markdown documentation for human readers
- Executable code examples for immediate use
- Template files for rapid prototyping

## 3. Extension Strategy

### 3.1 Extension Points

The Miri Standard leverages three extension points in the Python packaging ecosystem:

#### 3.1.1 Custom Metadata Files in `.dist-info/`

The wheel format allows custom files in the `.dist-info/` directory. Miri adds:

- `AGENT_EXAMPLES.json` - Example index and metadata
- `USAGE_PATTERNS.md` - Structured usage guide
- `API_REFERENCE.json` - Machine-readable API metadata
- `AGENT_GUIDE.md` - Agent-specific documentation
- `TEMPLATES.json` - Code template index

This extension point now has accepted upstream precedent: [PEP 770](https://peps.python.org/pep-0770/) (accepted 2025)
standardizes an `sboms/` directory inside `.dist-info/` for Software Bill-of-Materials documents. Miri does not redefine
SBOMs — packages bundling non-Python components MUST use PEP 770 as specified in
[Lifecycle and Security Metadata §3.2](lifecycle-security-metadata.md).

#### 3.1.2 Enhanced Package Data

Structured directories within the main package:

- `agent-metadata/` - Pre-parsed, structured data for agent consumption
- `examples/` - Categorized code samples
- `docs/` - Embedded documentation
- `templates/` - Boilerplate code files

#### 3.1.3 Pre-Parsed Agent Metadata

The `agent-metadata/` directory contains structured data that agents can read without re-deriving it from source:

- `sdk-manifest.json` - Core API index with structured signatures
- `usage-patterns.json` - Pre-extracted, categorized code patterns
- `migration-guide.json` - Structured version change documentation
- `api-graph.json` - *withdrawn at 0.7.3; see §5.5 and Agent Metadata §4.5*
- `lifecycle.json` - Identity (purl), advisory sources, update check, and support status ([full specification](lifecycle-security-metadata.md))

#### 3.1.4 Discovery APIs

Runtime functions for accessing Miri metadata:

- Package-level discovery functions
- Metadata extraction utilities
- Example enumeration and loading
- Template access methods
- Agent metadata loading and caching

### 3.2 Wheel Structure Extensions

```text
package-1.0.0-py3-none-any.whl
├── package/                          # Standard package code
│   ├── __init__.py                   # Enhanced with discovery APIs
│   ├── core.py                       # Main functionality
│   ├── agent-metadata/              # Miri: Pre-parsed agent data
│   │   ├── sdk-manifest.json        # Core API index (required)
│   │   ├── usage-patterns.json      # Common code patterns (required)
│   │   ├── migration-guide.json     # Version-specific changes
│   │   ├── prompt-templates.md      # Agent interaction guides
│   │   ├── api-graph.json          # withdrawn at 0.7.3 (§4.5); a wheel need not ship it
│   │   └── lifecycle.json          # Identity, advisory sources, support status (required)
│   ├── examples/                     # Miri: Embedded examples
│   │   ├── __init__.py              # Example discovery
│   │   ├── quickstart.py            # Basic usage
│   │   ├── authentication.py        # Auth patterns
│   │   ├── advanced.py              # Complex workflows
│   │   └── use_cases/               # Real-world scenarios
│   │       ├── __init__.py
│   │       ├── data_processing.py
│   │       └── api_integration.py
│   ├── docs/                        # Miri: Embedded docs
│   │   ├── __init__.py
│   │   ├── api_reference.md
│   │   └── troubleshooting.md
│   └── templates/                   # Miri: Code templates
│       ├── __init__.py
│       ├── basic_project.py
│       └── advanced_project.py
└── package-1.0.0.dist-info/         # Standard + Miri metadata
    ├── METADATA                      # Standard (enhanced)
    ├── WHEEL                         # Standard
    ├── RECORD                        # Standard
    ├── sboms/                        # Standard: PEP 770 SBOMs (when bundling non-Python components)
    ├── AGENT_EXAMPLES.json           # Miri: Example index
├── USAGE_PATTERNS.md             # Miri: Usage guide
├── API_REFERENCE.json            # Miri: API metadata
├── AGENT_GUIDE.md               # Miri: Agent documentation
└── TEMPLATES.json               # Miri: Template index
```

## 4. Metadata File Specifications

### 4.1 AGENT_EXAMPLES.json

**Purpose**: Structured index of all examples with metadata for agent consumption.

**Schema**:

```json
{
  "version": "1.0",
  "generated_at": "2025-08-30T12:00:00Z",
  "examples": {
    "example_id": {
      "description": "Human-readable description",
      "file": "examples/example_file.py",
      "complexity": "beginner|intermediate|advanced",
      "tags": ["tag1", "tag2"],
      "dependencies": ["package1", "package2"],
      "estimated_time": "5 minutes",
      "prerequisites": ["other_example_id"],
      "related": ["related_example_id"],
      "use_cases": ["use_case_1", "use_case_2"]
    }
  },
  "learning_paths": {
    "path_id": {
      "name": "Learning Path Name",
      "description": "Path description",
      "examples": ["example1", "example2", "example3"],
      "estimated_total_time": "30 minutes"
    }
  },
  "categories": {
    "category_id": {
      "name": "Category Name",
      "description": "Category description",
      "examples": ["example1", "example2"]
    }
  }
}
```

**Example**:

```json
{
  "version": "1.0",
  "generated_at": "2025-08-30T12:00:00Z",
  "examples": {
    "quickstart": {
      "description": "Basic SDK usage patterns for immediate getting started",
      "file": "examples/quickstart.py",
      "complexity": "beginner",
      "tags": ["basic", "getting-started", "authentication"],
      "dependencies": [],
      "estimated_time": "5 minutes",
      "prerequisites": [],
      "related": ["authentication", "error_handling"],
      "use_cases": ["first_time_setup", "basic_operations"]
    },
    "authentication": {
      "description": "Comprehensive authentication patterns and error handling",
      "file": "examples/authentication.py",
      "complexity": "intermediate",
      "tags": ["auth", "security", "api-keys", "oauth"],
      "dependencies": [],
      "estimated_time": "10 minutes",
      "prerequisites": ["quickstart"],
      "related": ["error_handling", "advanced_usage"],
      "use_cases": ["secure_access", "production_setup"]
    }
  },
  "learning_paths": {
    "complete_guide": {
      "name": "Complete SDK Guide",
      "description": "Full progression from basics to advanced usage",
      "examples": ["quickstart", "authentication", "error_handling", "advanced_usage"],
      "estimated_total_time": "45 minutes"
    }
  },
  "categories": {
    "getting_started": {
      "name": "Getting Started",
      "description": "Essential examples for new users",
      "examples": ["quickstart", "authentication"]
    }
  }
}
```

### 4.2 Metadata Location (no custom METADATA fields)

Earlier drafts proposed extending the wheel's core `METADATA` with Miri-specific fields (`Agent-Examples-Dir`,
`Miri-Version`, and similar). That approach is withdrawn: Python core metadata has no sanctioned extension mechanism,
no PEP 517 build backend can inject arbitrary fields, and strict parsers reject unknown ones. All Miri metadata
therefore lives in dedicated files — the `agent-metadata/` directory and the `.dist-info/AGENT_EXAMPLES.json` index
(§3, §4.1) — never in `METADATA`. This keeps the standard additive and compatible with every existing packaging tool.

### 4.3 API_REFERENCE.json

**Purpose**: Machine-readable API metadata for programmatic consumption.

**Schema**:

```json
{
  "version": "1.0",
  "classes": {
    "ClassName": {
      "description": "Class description",
      "methods": {
        "method_name": {
          "description": "Method description",
          "parameters": {
            "param_name": {
              "type": "str",
              "required": true,
              "description": "Parameter description"
            }
          },
          "returns": {
            "type": "dict",
            "description": "Return value description"
          },
          "examples": ["example_id"],
          "complexity": "beginner"
        }
      }
    }
  },
  "functions": {
    "function_name": {
      "description": "Function description",
      "parameters": {},
      "returns": {},
      "examples": [],
      "complexity": "beginner"
    }
  }
}
```

### 4.4 TEMPLATES.json

**Purpose**: Index of available code templates with metadata.

**Schema**:

```json
{
  "version": "1.0",
  "templates": {
    "template_id": {
      "name": "Template Name",
      "description": "Template description",
      "file": "templates/template_file.py",
      "category": "basic|advanced|integration",
      "placeholders": {
        "PLACEHOLDER_NAME": {
          "description": "What to replace this with",
          "example": "example_value",
          "required": true
        }
      },
      "dependencies": ["package1"],
      "use_cases": ["use_case_1"]
    }
  }
}
```

## 5. Package Structure Extensions

### 5.1 Examples Directory Structure

```text
examples/
├── __init__.py                    # Example discovery and loading
├── quickstart.py                  # Required: Basic usage
├── authentication.py              # Auth patterns
├── error_handling.py             # Error management
├── advanced.py                   # Complex workflows
├── use_cases/                    # Real-world scenarios
│   ├── __init__.py
│   ├── data_processing.py
│   ├── api_integration.py
│   └── batch_operations.py
└── async/                        # Async patterns (if applicable)
    ├── __init__.py
    ├── async_basic.py
    └── async_advanced.py
```

### 5.2 Example File Requirements

Each example file MUST include:

1. **Header Comment Block**:

   ```python
   #!/usr/bin/env python3
   """
   Example Title
   
   Brief description of what this example demonstrates.
   Perfect for AI agents to understand specific functionality.
   
   Complexity: beginner|intermediate|advanced
   Tags: tag1, tag2, tag3
   Estimated time: X minutes
   Prerequisites: other_example_names
   """
   ```

2. **Runnable Code**: Complete, executable examples
3. **Error Handling**: Proper exception management
4. **Documentation**: Inline comments explaining key concepts
5. **Main Function**: `if __name__ == "__main__":` entry point

### 5.3 Documentation Directory

```text
docs/
├── __init__.py                   # Doc discovery
├── api_reference.md             # Complete API documentation
├── troubleshooting.md           # Common issues and solutions
├── migration_guide.md           # Version migration info
└── advanced_topics/             # Deep-dive topics
    ├── __init__.py
    ├── performance.md
    └── security.md
```

### 5.4 Templates Directory

```text
templates/
├── __init__.py                  # Template discovery
├── basic_project.py            # Basic project structure
├── advanced_project.py         # Complex project template
├── integration_template.py     # Integration patterns
└── testing_template.py        # Testing setup template
```

### 5.5 Precomputed Code Index

*Status: SHOULD (MIRI-PY-045). Added 0.7.3, replacing the withdrawn `api-graph.json`.*

A wheel MAY carry a precomputed code index under `.dist-info/`, and SHOULD do so where a producer can generate
one. `sdk-manifest.json` `code_index` declares its path and format.

```text
greetlib-1.1.0.dist-info/
├── RECORD                       # lists the index with its sha256 and size, like every carried file
├── sboms/                       # PEP 770 SBOM documents
└── scip/index.scip              # the index, declared in sdk-manifest.json code_index
```

#### Why this helps a consumer, and what the evidence is

An agent writes against the API it was trained on, and the gap between that API and the installed one is
measured rather than assumed. A benchmark of 270 real API updates across eight Python libraries found that
**25.36%** of generations ignored the update entirely, **16.4%** used only the removed API, and **12.3%** mixed
old and new APIs *in the same file*. Supplying structured API documentation alongside the request raised the
share of generated code that **executes** from **42.55% to 66.36%** — the largest single intervention measured,
against 2.34 points for chain-of-thought prompting.

That study supplied the documentation by hand, in a prompt. The whole argument for carrying it in the wheel is
that nobody should have to: it ships versioned with the code, it is there offline, and it describes the release
that is actually installed rather than the one a model remembers.

**And 128 of those 270 updates were modifications** — symbols that kept their name and changed shape. That is
the class a name-keyed index cannot see at all, and the one that produces the mixed-API failure, because the
name still resolves and the call is wrong. It is also why `api-graph.json` was withdrawn rather than extended:
a graph of names and kinds cannot express the change a consumer most needs to be told about.

#### Why a published format, and not one of ours

Every code-intelligence format in production — LSIF, SCIP, Kythe, Stack Graphs — is produced by CI and ingested
by a central service. **None of them ships inside the distribution**, and an agent that has just run
`pip install` cannot query anybody's host. Carrying the index in the artifact is this standard's contribution;
the *format* does not need to be, and a format one implementation maintains is worse than one with a protobuf
schema, several indexers and existing consumers.

The standard therefore names **SCIP** as the format and says nothing about the indexer, exactly as it names the
wheel format and not the build backend. Producer maturity is a moving target: of the two Python indexers
measured, one is mature and requires npm, the other installs with pip and was two days old.

#### What a consumer should expect, stated honestly

- **The benefit is conditional on having a reader.** Measured on a 1.87 MB wheel: read end to end, an index
  costs *more* than reading the source; queried for one symbol, it is **22x cheaper** than opening the file
  and 889x cheaper than reading `sdk-manifest.json` whole. A consumer that cannot decode protobuf gains nothing
  and should fall back to `api_index` — which is why `code_index` declares the format, so that decision is made
  from the manifest rather than from a failed parse.
- **`api_index` remains the readable surface.** It is JSON, every consumer can parse it, and nothing here
  deprecates it. The index is an addition for consumers that can use it, not a replacement for the document
  that works everywhere.
- **Ship it reduced.** A full index measured **62%** of that wheel's size; the same index with reference
  occurrences removed measured **20%**. Occurrences record where a symbol is referenced *within the indexed
  source* — a navigation concern for a code host displaying the package's own repository, not something a
  consumer of a published API needs.
- **Which reduction is safe is unsettled.** If third-party readers locate definitions through definition
  occurrences rather than through `SymbolInformation`, stripping all occurrences breaks them and the correct
  reduction keeps definitions and drops references only. `code_index.reduction` declares which was applied so a
  consumer knows what it was handed, and so the question can be settled by measurement across implementations
  before this specification prescribes an answer.
- **Cross-release symbol stability is untested.** If two indexers, or two versions of one, emit different
  symbol IDs for the same code, a delta computed across releases breaks. `code_index.produced_by` records the
  producer for that reason.

#### What it makes decidable

`MIRI-PY-043` compares an `api_index` entry's signature-bearing fields across releases. With signature-level
identity available, a release delta stops being *declared* by the producer and becomes *computable* from two
artifacts the releases already ship — which is what makes 030, 043 and 044 verifiable rather than approximate.
This is why the index is worth its bytes even for a consumer that never opens it: the producer's own CI can
compute the delta the changelog must then declare.

## 6. Discovery and Access APIs

### 6.1 Package-Level Discovery Functions

Every Miri-compliant package MUST provide these functions in its main `__init__.py`:

```python
def get_examples_dir() -> Path:
    """Get path to installed examples directory."""

def get_docs_dir() -> Path:
    """Get path to installed documentation."""

def get_templates_dir() -> Path:
    """Get path to code templates."""

def get_agent_metadata() -> Dict:
    """Get agent-specific metadata from wheel distribution."""

def list_examples() -> List[str]:
    """List all available example files."""

def show_quickstart() -> str:
    """Display quickstart guide for immediate usage."""

def get_usage_guide() -> str:
    """Get comprehensive usage guide for AI agents."""
```

### 6.2 Example Access Patterns

```python
import package_name

# 1. Immediate overview
print(package_name.__doc__)

# 2. List examples
examples = package_name.list_examples()

# 3. Get quickstart
quickstart = package_name.show_quickstart()

# 4. Access metadata
metadata = package_name.get_agent_metadata()

# 5. Import examples
from package_name.examples import quickstart
from package_name.examples.use_cases import data_processing

# 6. Get templates
templates_dir = package_name.get_templates_dir()
```

## 7. Implementation Requirements

### 7.1 Build System Integration

#### 7.1.1 pyproject.toml Configuration

```toml
[project]
name = "example-package"
version = "1.0.0"
description = "Miri-compliant package"

[tool.setuptools.package-data]
example_package = [
    "examples/*.py",
    "examples/**/*.py",
    "docs/*.md",
    "docs/**/*.md", 
    "templates/*.py",
    "templates/**/*.py"
]

[tool.miri]
compliance_level = "full"
examples_dir = "examples"
docs_dir = "docs"
templates_dir = "templates"
quickstart_file = "examples/quickstart.py"
```

#### 7.1.2 Build-Time Metadata Generation

Build systems SHOULD generate AGENT_EXAMPLES.json automatically by scanning example files for metadata comments.

### 7.2 Validation Requirements

#### 7.2.1 Conformance

Conformance is defined by the [Linter Checklist](linter-checklist.md) — the single source of truth for what a wheel
MUST and SHOULD provide. A wheel is **conforming** when it passes every MUST (M) check; its Bronze/Silver/Gold tier is
the checklist score. Any file list once given here is superseded by the checklist.

#### 7.2.2 Content Requirements

- All examples MUST be runnable without modification (except API keys)
- All examples MUST include proper error handling
- All metadata MUST validate against JSON schemas
- All templates MUST include clear placeholder documentation

## 8. Compatibility and Migration

### 8.1 Backward Compatibility Guarantees

1. **Standard Tools**: All existing pip, setuptools, wheel tools continue to work
2. **Installation**: Standard `pip install` workflow unchanged
3. **Import**: Package imports work identically for non-Miri usage
4. **Metadata**: Standard metadata fields preserved and unchanged

### 8.2 Migration Path

#### 8.2.1 Existing Packages

1. **Phase 1**: Add basic examples directory and quickstart.py
2. **Phase 2**: Add AGENT_EXAMPLES.json metadata
3. **Phase 3**: Implement discovery APIs
4. **Phase 4**: Add full documentation and templates

#### 8.2.2 New Packages

New packages SHOULD implement full Miri compliance from the start using provided templates and build tools.

### 8.3 Graceful Degradation

Miri-enhanced packages MUST work normally when:

- Miri tools are not available
- Examples directory is missing
- Metadata files are absent
- Discovery APIs are not implemented

## 9. Validation and Conformance

### 9.1 Conformance Levels

Conformance levels — Bronze, Silver, Gold — are defined by the [Linter Checklist](linter-checklist.md): passing every
MUST (M) check is conformance, and the tier is the checklist score. The checklist is the authoritative definition; the
levels once listed here are superseded by it.

### 9.2 Validation Tools

#### 9.2.1 miri-validate Command

```bash
# Validate package conformance
miri-validate package-1.0.0-py3-none-any.whl

# Validate installed package
miri-validate --installed package-name

# Generate conformance report
miri-validate --report package-name
```

#### 9.2.2 JSON Schema Validation

The `agent-metadata/` files MUST validate against their published JSON Schemas in
[`schemas/`](../../schemas/) (`sdk-manifest-v1.json`, `usage-patterns-v1.json`, `migration-guide-v1.json`,
`api-graph-v1.json`, `lifecycle-v1.json`). The `.dist-info/` index files (`AGENT_EXAMPLES.json`, `API_REFERENCE.json`,
`TEMPLATES.json`) MUST follow the structures defined in §4.1, §4.3, and §4.4 respectively; dedicated JSON Schemas for
them are not yet published.

### 9.3 Testing Requirements

Miri-compliant packages SHOULD include tests that verify:

- All examples execute without errors
- All discovery APIs return valid data
- All metadata files are valid JSON
- All templates contain required placeholders

---

## References

- [PEP 427: The Wheel Binary Package Format 1.0](https://peps.python.org/pep-0427/)
- [Binary Distribution Format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/)
- [PEP 566: Metadata for Python Software Packages 2.1](https://peps.python.org/pep-0566/)
- [PEP 621: Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [PEP 770: Improving measurability of Python packages with SBOMs](https://peps.python.org/pep-0770/)
- [Miri Lifecycle and Security Metadata](lifecycle-security-metadata.md)
- [Miri Standard Origin Story](../../docs/origin-story.md)

---

*This specification is part of the Miri Standard project. For the latest version and additional resources, visit [https://github.com/miri-whl/miri-standard](https://github.com/miri-whl/miri-standard).*
