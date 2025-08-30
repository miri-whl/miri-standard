# Miri Standard: Agent-Friendly Python Wheel Extensions

*Specification Version: 1.0-draft*  
*Status: Draft*  
*Created: 2025*

## Abstract

This specification defines extensions to the Python wheel format (PEP 427/491) that enable enhanced communication between Python packages and autonomous agents. The Miri Standard addresses the "thought-string gaps" in current Python packaging by adding structured metadata, embedded examples, and discovery mechanisms that allow agents to immediately understand and use packages without external documentation lookups.

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

Enable autonomous agents (code assistants, code generators, automated development tools) to immediately understand and utilize Python packages after installation via standard package managers, without requiring external documentation lookups or sequential text processing.

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
- Structured metadata for instant parsing
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

#### 3.1.2 Enhanced Package Data

Structured directories within the main package:
- `agent-metadata/` - Pre-parsed, structured data for agent consumption
- `examples/` - Categorized code samples
- `docs/` - Embedded documentation
- `templates/` - Boilerplate code files

#### 3.1.3 Pre-Parsed Agent Metadata

The `agent-metadata/` directory contains optimized data structures that eliminate agent re-parsing:
- `sdk-manifest.json` - Core API index with structured signatures
- `usage-patterns.json` - Pre-extracted, categorized code patterns
- `migration-guide.json` - Structured version change documentation
- `api-graph.json` - Relationship mapping between API components

#### 3.1.4 Discovery APIs

Runtime functions for accessing Miri metadata:
- Package-level discovery functions
- Metadata extraction utilities
- Example enumeration and loading
- Template access methods
- Agent metadata loading and caching

### 3.2 Wheel Structure Extensions

```
package-1.0.0-py3-none-any.whl
├── package/                          # Standard package code
│   ├── __init__.py                   # Enhanced with discovery APIs
│   ├── core.py                       # Main functionality
│   ├── agent-metadata/              # Miri: Pre-parsed agent data
│   │   ├── sdk-manifest.json        # Core API index (required)
│   │   ├── usage-patterns.json      # Common code patterns (required)
│   │   ├── migration-guide.json     # Version-specific changes
│   │   ├── prompt-templates.md      # Agent interaction guides
│   │   ├── api-graph.json          # API relationship graph
│   │   └── performance-hints.json  # Optimization suggestions
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
  "$schema": "https://miri-standard.org/schemas/agent-examples-v1.json",
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

### 4.2 Enhanced METADATA File

**Purpose**: Extend standard PEP 566 metadata with Miri-specific fields.

**Additional Fields**:
```
# Miri Standard Extensions
Agent-Examples-Dir: examples
Agent-Docs-Dir: docs
Agent-Templates-Dir: templates
Agent-Quickstart-File: examples/quickstart.py
Agent-Friendly: true
Agent-Complexity-Level: beginner|intermediate|advanced
Agent-Learning-Time: 15-minutes
Miri-Version: 1.0
Miri-Compliance: full|partial|none
```

**Example**:
```
Metadata-Version: 2.1
Name: example-sdk
Version: 1.0.0
Summary: AI-friendly SDK with embedded examples and documentation
Author: Example Author
Author-email: author@example.com
License: MIT
Requires-Dist: requests>=2.25.0
Requires-Dist: pydantic>=1.8.0

# Miri Standard Extensions
Agent-Examples-Dir: examples
Agent-Docs-Dir: docs
Agent-Templates-Dir: templates
Agent-Quickstart-File: examples/quickstart.py
Agent-Friendly: true
Agent-Complexity-Level: intermediate
Agent-Learning-Time: 15-minutes
Miri-Version: 1.0
Miri-Compliance: full

This SDK demonstrates the Miri Standard for agent-friendly Python packages.
It includes embedded examples, structured documentation, and discovery APIs
that enable autonomous agents to immediately understand and use the package.
```

### 4.3 API_REFERENCE.json

**Purpose**: Machine-readable API metadata for programmatic consumption.

**Schema**:
```json
{
  "$schema": "https://miri-standard.org/schemas/api-reference-v1.json",
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
  "$schema": "https://miri-standard.org/schemas/templates-v1.json",
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

```
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

```
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

```
templates/
├── __init__.py                  # Template discovery
├── basic_project.py            # Basic project structure
├── advanced_project.py         # Complex project template
├── integration_template.py     # Integration patterns
└── testing_template.py        # Testing setup template
```

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
metadata = package_name.get_ai_metadata()

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

Build systems SHOULD generate AI_EXAMPLES.json automatically by scanning example files for metadata comments.

### 7.2 Validation Requirements

#### 7.2.1 Required Files

**Minimum Compliance**:
- `examples/quickstart.py` - Basic usage example
- `AI_EXAMPLES.json` - Example metadata
- Enhanced METADATA with Miri fields

**Full Compliance**:
- Complete examples directory structure
- All metadata files (AI_EXAMPLES.json, API_REFERENCE.json, TEMPLATES.json)
- Documentation directory
- Templates directory
- All discovery APIs implemented

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
2. **Phase 2**: Add AI_EXAMPLES.json metadata
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

#### 9.1.1 Basic Conformance

- `examples/quickstart.py` exists and is runnable
- `AI_EXAMPLES.json` includes quickstart metadata
- Enhanced METADATA includes minimum Miri fields
- Package `__init__.py` includes `show_quickstart()` function

#### 9.1.2 Full Conformance

- Complete examples directory structure
- All metadata files present and valid
- All discovery APIs implemented
- Documentation and templates directories
- JSON schema validation passes

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

All JSON metadata files MUST validate against published schemas:
- `https://miri-standard.org/schemas/ai-examples-v1.json`
- `https://miri-standard.org/schemas/api-reference-v1.json`
- `https://miri-standard.org/schemas/templates-v1.json`

### 9.3 Testing Requirements

Miri-compliant packages SHOULD include tests that verify:
- All examples execute without errors
- All discovery APIs return valid data
- All metadata files are valid JSON
- All templates contain required placeholders

---

## References

- [PEP 427: The Wheel Binary Package Format 1.0](https://peps.python.org/pep-0427/)
- [PEP 491: The Wheel Binary Package Format 1.9](https://peps.python.org/pep-0491/)
- [PEP 566: Metadata for Python Software Packages 2.1](https://peps.python.org/pep-0566/)
- [PEP 621: Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [Miri Standard Origin Story](../../docs/origin-story.md)

---

*This specification is part of the Miri Standard project. For the latest version and additional resources, visit [https://github.com/miri-whl/miri-standard](https://github.com/miri-whl/miri-standard).*
