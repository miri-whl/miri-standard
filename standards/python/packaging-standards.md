# Python Packaging Standards Overview

## Introduction

This document provides a comprehensive overview of the Python packaging ecosystem standards that form the foundation for
the Miri Standard extensions. Understanding these existing standards is crucial for implementing agent-friendly
enhancements while maintaining compatibility.

## Standards Hierarchy

### Core Standards (Must Implement)

#### 1. Package Distribution Format

- **PEP 427**: Wheel Binary Package Format 1.0
- **PEP 491**: Wheel Binary Package Format 1.9 (Deferred; superseded by the Binary Distribution Format spec)
- **Status**: Universal adoption
- **Purpose**: Defines the .whl file structure and naming

#### 2. Metadata Format

- **PEP 566**: Metadata for Python Software Packages 2.1
- **PEP 621**: Storing project metadata in pyproject.toml
- **Status**: Current standard
- **Purpose**: Defines package metadata structure and fields

#### 3. Dependency Specification

- **PEP 508**: Dependency specification for Python Software Packages
- **Status**: Universal adoption
- **Purpose**: Standardizes how dependencies are declared and resolved

### Build System Standards

#### 4. Build Interface

- **PEP 517**: A build-system independent format for source trees
- **PEP 518**: Specifying Minimum Build System Requirements
- **Status**: Modern standard
- **Purpose**: Defines how packages are built from source

#### 5. Source Distribution Format

- **PEP 643**: Metadata for Python Software Packages 2.2
- **Status**: Draft/Future
- **Purpose**: Next generation metadata format

## Metadata Evolution Timeline

### Historical Progression

```text
1998: distutils (basic setup.py)
     ↓
2004: setuptools (enhanced setup.py, eggs)
     ↓
2012: PEP 427 (wheel format)
     ↓
2015: PEP 491 (wheel 1.9, Deferred)
     ↓
2017: PEP 566 (metadata 2.1)
     ↓
2020: PEP 621 (pyproject.toml)
     ↓
2025: Miri Standard (agent-friendly extensions)
```

### Metadata Format Versions

| Version | PEP | Year | Key Features |
|---------|-----|------|--------------|
| 1.0 | PEP 241 | 2001 | Basic metadata fields |
| 1.1 | PEP 314 | 2003 | Added classifiers, download URL |
| 1.2 | PEP 345 | 2005 | Dependencies, obsoletes, provides |
| 2.0 | PEP 426 | 2013 | JSON format (withdrawn) |
| 2.1 | PEP 566 | 2017 | Description content type, dynamic fields |
| 2.2 | PEP 643 | Future | Enhanced dependency specification |

## Current Standard Components

### 1. Core Metadata (PEP 566)

**Required Fields:**

- `Metadata-Version`: Format version identifier
- `Name`: Package name
- `Version`: Package version

**Common Optional Fields:**

- `Summary`: One-line description
- `Description`: Long description
- `Author`: Package author
- `Author-email`: Author contact
- `License`: License information
- `Classifier`: Trove classifiers
- `Requires-Dist`: Runtime dependencies
- `Requires-Python`: Python version requirements

### 2. Wheel Metadata (PEP 427; Binary Distribution Format)

**WHEEL File Contents:**

```text
Wheel-Version: 1.0
Generator: bdist_wheel (0.37.1)
Root-Is-Purelib: true
Tag: py3-none-any
Build: 1
```

**Key Components:**

- **Wheel-Version**: Wheel format version
- **Generator**: Tool that created the wheel
- **Root-Is-Purelib**: Whether package is pure Python
- **Tag**: Compatibility tags
- **Build**: Optional build number

### 3. Installation Metadata

**RECORD File:**

- Lists all installed files
- Includes SHA256 hashes
- Tracks file sizes
- Enables clean uninstallation

**INSTALLER File:**

- Records installation tool
- Enables tool-specific behavior

## Trove Classifiers System

### Purpose

Trove classifiers provide standardized categorization of packages.

### Categories

#### Development Status

```text
Development Status :: 1 - Planning
Development Status :: 2 - Pre-Alpha
Development Status :: 3 - Alpha
Development Status :: 4 - Beta
Development Status :: 5 - Production/Stable
Development Status :: 6 - Mature
Development Status :: 7 - Inactive
```

#### Intended Audience

```text
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: Science/Research
Intended Audience :: System Administrators
```

#### License Categories

```text
License :: OSI Approved :: MIT License
License :: OSI Approved :: Apache Software License
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
```

#### Programming Language

```text
Programming Language :: Python :: 3
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
```

#### Topic Categories

```text
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Scientific/Engineering :: Artificial Intelligence
```

## Dependency Management Standards

### PEP 508 Specification Format

**Basic Dependency:**

```text
requests >= 2.25.0
```

**With Environment Markers:**

```text
pywin32 >= 1.0; sys_platform == "win32"
```

**With Extras:**

```text
requests[security] >= 2.25.0
```

**Complex Example:**

```text
numpy >= 1.19.0, < 2.0.0; python_version >= "3.8"
```

### Environment Markers

| Marker | Description | Example |
|--------|-------------|---------|
| `python_version` | Python version | `>= "3.8"` |
| `python_full_version` | Full Python version | `>= "3.8.5"` |
| `os_name` | Operating system | `== "posix"` |
| `sys_platform` | System platform | `== "linux"` |
| `platform_machine` | Machine type | `== "x86_64"` |
| `platform_python_implementation` | Python implementation | `== "CPython"` |

## Build Configuration Standards

### pyproject.toml Structure (PEP 621)

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "example-package"
version = "1.0.0"
description = "A sample Python package"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "Example Author", email = "author@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]
dependencies = [
    "requests >= 2.25.0",
    "click >= 7.0",
]
requires-python = ">=3.8"

[project.optional-dependencies]
dev = ["pytest", "black", "flake8"]
docs = ["sphinx", "sphinx-rtd-theme"]

[project.urls]
Homepage = "https://github.com/example/example-package"
Documentation = "https://example-package.readthedocs.io/"
Repository = "https://github.com/example/example-package.git"
"Bug Tracker" = "https://github.com/example/example-package/issues"

[project.scripts]
example-cli = "example_package.cli:main"

[project.entry-points."console_scripts"]
example-tool = "example_package.tools:run"
```

## Standards Compliance Tools

### Validation Tools

#### check-wheel-contents

```bash
check-wheel-contents dist/*.whl
```

- Validates wheel structure
- Checks for common issues
- Ensures standards compliance

#### twine check

```bash
twine check dist/*
```

- Validates metadata
- Checks description rendering
- Ensures PyPI compatibility

#### validate-pyproject

```bash
validate-pyproject pyproject.toml
```

- Validates pyproject.toml structure
- Checks PEP 621 compliance
- Ensures build system compatibility

### Metadata Extraction Tools

#### pkginfo

```python
from pkginfo import Wheel
wheel = Wheel('package-1.0-py3-none-any.whl')
print(wheel.name, wheel.version)
```

#### importlib.metadata

```python
from importlib import metadata
dist = metadata.distribution('package-name')
print(dist.metadata['Summary'])
```

## Standards Gaps for Agent Communication

### Current Limitations

#### 1. Unstructured Content

- **Problem**: Free-form text descriptions
- **Impact**: Agents cannot parse semantic meaning
- **Example**: "This library does many things..."

#### 2. Missing Context

- **Problem**: No complexity indicators
- **Impact**: Agents cannot assess difficulty
- **Example**: No distinction between beginner and advanced usage

#### 3. Scattered Examples

- **Problem**: Code samples in various locations
- **Impact**: Agents must search multiple sources
- **Example**: README, docs, Stack Overflow

#### 4. Limited Relationships

- **Problem**: Basic dependency information only
- **Impact**: Agents cannot understand usage patterns
- **Example**: No indication of common package combinations

#### 5. No Learning Paths

- **Problem**: No structured progression
- **Impact**: Agents cannot guide users through capabilities
- **Example**: No "start here, then try this" guidance

### Miri Standard Solutions

#### 1. Structured Metadata

```json
{
  "miri_version": "1.0",
  "complexity_level": "intermediate",
  "categories": ["web", "api", "async"],
  "learning_path": ["basic_usage", "advanced_features", "integration"]
}
```

#### 2. Organized Examples

```text
miri-examples/
├── basic/
│   ├── hello_world.py
│   └── simple_request.py
├── intermediate/
│   ├── async_requests.py
│   └── error_handling.py
└── advanced/
    ├── custom_auth.py
    └── streaming.py
```

#### 3. Rich Templates

```python
# Template: Basic API Client
import {package_name}

client = {package_name}.Client(
    api_key="{YOUR_API_KEY}",  # Replace with your API key
    base_url="{API_BASE_URL}"  # Optional: custom base URL
)

# {USAGE_EXAMPLE}
response = client.{method_name}({parameters})
print(response.{result_field})
```

## Compliance Strategy

### Backward Compatibility

The Miri Standard maintains full compatibility with existing standards:

1. **Existing Metadata**: All current fields remain unchanged
2. **Tool Compatibility**: Standard tools continue to work
3. **Installation Process**: No changes to pip install workflow
4. **Validation**: Existing validation tools still apply

### Extension Approach

Miri enhancements are additive:

1. **New Files**: Add `miri-examples/` and `MIRI` metadata
2. **Optional Fields**: Extend metadata with optional Miri fields
3. **Supplementary Data**: Enhance rather than replace existing information
4. **Graceful Degradation**: Packages work without Miri-aware tools

### Standards Evolution Path

```text
Current Standards (PEP 566, 621)
         ↓
Miri Extensions (additive)
         ↓
Community Adoption
         ↓
Potential PEP Proposal (future)
         ↓
Official Standard (long-term goal)
```

## References

### Official Documentation

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPA Specifications](https://packaging.python.org/specifications/)
- [PEP Index](https://peps.python.org/)

### Key PEPs

- [PEP 427: Wheel Binary Package Format 1.0](https://peps.python.org/pep-0427/)
- [Binary Distribution Format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/)
- [PEP 566: Metadata for Python Software Packages 2.1](https://peps.python.org/pep-0566/)
- [PEP 621: Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [PEP 508: Dependency specification](https://peps.python.org/pep-0508/)

### Tools and Resources

- [Python Packaging Authority](https://www.pypa.io/)
- [PyPI - Python Package Index](https://pypi.org/)
- [Warehouse (PyPI codebase)](https://github.com/pypa/warehouse)
- [Packaging Tools](https://packaging.python.org/key_projects/)
