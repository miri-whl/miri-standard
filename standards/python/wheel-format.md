# Python Wheel Format Specification

## Overview

This document provides comprehensive documentation of the current Python wheel (.whl) format, serving as the foundation for understanding how the Miri Standard extends Python packaging for enhanced agent communication.

## What is a Python Wheel?

A Python wheel is a built-package format for Python that provides faster installation compared to building from source. Wheels are ZIP archives with a specially formatted filename and contain all the files needed to install a Python package.

## Historical Context

### Evolution of Python Packaging

1. **Early Days**: Manual installation and distutils (1998)
2. **setuptools Era**: Easy installation and egg format (2004)
3. **Modern Packaging**: pip, wheels, and standardized metadata (2012-present)

### Key Milestones

- **PEP 427** (2012): The Wheel Binary Package Format 1.0
- **PEP 491** (2015): The Wheel Binary Package Format 1.9
- **PEP 566** (2017): Metadata for Python Software Packages 2.1
- **PEP 621** (2020): Storing project metadata in pyproject.toml

## Wheel Format Structure

### Filename Convention

Wheels follow a strict naming convention:
```
{distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl
```

**Example**: `numpy-1.21.0-cp39-cp39-win_amd64.whl`

- **distribution**: `numpy`
- **version**: `1.21.0`
- **python tag**: `cp39` (CPython 3.9)
- **abi tag**: `cp39` (CPython 3.9 ABI)
- **platform tag**: `win_amd64` (Windows 64-bit)

### Internal Structure

A wheel is a ZIP archive containing:

```
package_name/
    __init__.py
    module.py
    ...
package_name-version.dist-info/
    METADATA
    WHEEL
    RECORD
    top_level.txt
    INSTALLER (optional)
    REQUESTED (optional)
    entry_points.txt (optional)
    LICENCE (optional)
    ...
```

## Core Metadata Files

### METADATA File

Contains package metadata in RFC 5322 format (email header style):

```
Metadata-Version: 2.1
Name: example-package
Version: 1.0.0
Summary: A sample Python package
Home-page: https://github.com/example/example-package
Author: Example Author
Author-email: author@example.com
License: MIT
Description-Content-Type: text/markdown
Classifier: Development Status :: 4 - Beta
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.8
Classifier: Programming Language :: Python :: 3.9
Requires-Dist: requests (>=2.25.0)
Requires-Dist: click (>=7.0)

Long description content here...
```

### WHEEL File

Contains wheel-specific metadata:

```
Wheel-Version: 1.0
Generator: bdist_wheel (0.37.1)
Root-Is-Purelib: true
Tag: py3-none-any
```

### RECORD File

Contains a list of all files in the wheel with their hash and size:

```
package_name/__init__.py,sha256=hash_value,file_size
package_name/module.py,sha256=hash_value,file_size
package_name-version.dist-info/METADATA,sha256=hash_value,file_size
package_name-version.dist-info/WHEEL,sha256=hash_value,file_size
package_name-version.dist-info/RECORD,,
```

## Governing Standards and PEPs

### Primary Standards

#### PEP 427: The Wheel Binary Package Format 1.0
- **Status**: Final
- **Created**: 2012
- **Summary**: Defines the basic wheel format structure
- **URL**: https://peps.python.org/pep-0427/

#### PEP 491: The Wheel Binary Package Format 1.9  
- **Status**: Final
- **Created**: 2015
- **Summary**: Updates to wheel format, adds build numbers
- **URL**: https://peps.python.org/pep-0491/

#### PEP 566: Metadata for Python Software Packages 2.1
- **Status**: Final
- **Created**: 2017
- **Summary**: Defines metadata format used in METADATA file
- **URL**: https://peps.python.org/pep-0566/

#### PEP 621: Storing project metadata in pyproject.toml
- **Status**: Final
- **Created**: 2020
- **Summary**: Standardizes metadata in pyproject.toml files
- **URL**: https://peps.python.org/pep-0621/

### Supporting Standards

#### PEP 314: Metadata for Python Software Packages 1.1
- **Status**: Final
- **Summary**: Earlier metadata format
- **URL**: https://peps.python.org/pep-0314/

#### PEP 345: Metadata for Python Software Packages 1.2
- **Status**: Final
- **Summary**: Intermediate metadata format
- **URL**: https://peps.python.org/pep-0345/

#### PEP 508: Dependency specification for Python Software Packages
- **Status**: Final
- **Summary**: Defines how to specify dependencies
- **URL**: https://peps.python.org/pep-0508/

#### PEP 517: A build-system independent format for source trees
- **Status**: Final
- **Summary**: Defines build system interface
- **URL**: https://peps.python.org/pep-0517/

#### PEP 518: Specifying Minimum Build System Requirements
- **Status**: Final
- **Summary**: Defines build requirements in pyproject.toml
- **URL**: https://peps.python.org/pep-0518/

## Metadata Fields Reference

### Core Fields

| Field | Required | Description |
|-------|----------|-------------|
| `Metadata-Version` | Yes | Version of metadata format |
| `Name` | Yes | Package name |
| `Version` | Yes | Package version |
| `Summary` | No | One-line description |
| `Description` | No | Longer description |
| `Keywords` | No | Comma-separated keywords |
| `Home-page` | No | Project homepage URL |
| `Download-URL` | No | Download URL |
| `Author` | No | Author name |
| `Author-email` | No | Author email |
| `Maintainer` | No | Maintainer name |
| `Maintainer-email` | No | Maintainer email |
| `License` | No | License information |
| `Classifier` | No | Trove classifiers (multiple) |
| `Requires-Dist` | No | Runtime dependencies (multiple) |
| `Requires-Python` | No | Python version requirement |
| `Requires-External` | No | External dependencies (multiple) |
| `Project-URL` | No | Additional project URLs (multiple) |
| `Provides-Extra` | No | Optional feature names (multiple) |
| `Provides-Dist` | No | Provided distributions (multiple) |
| `Obsoletes-Dist` | No | Obsoleted distributions (multiple) |

### Extended Fields (PEP 566)

| Field | Description |
|-------|-------------|
| `Description-Content-Type` | MIME type of description |
| `Dynamic` | Fields that are determined dynamically |

## Current Limitations for Agent Communication

### Information Gaps

The current wheel format has several gaps that limit agent comprehension:

1. **No Structured Examples**: Examples are embedded in descriptions or external docs
2. **Limited Complexity Indicators**: No way to indicate beginner vs advanced usage
3. **No Learning Paths**: No structured progression through package capabilities
4. **Scattered Documentation**: Links to external resources without structure
5. **No Agent Metadata**: No fields specifically designed for programmatic consumption
6. **Limited Relationship Data**: Basic dependency info without contextual relationships

### Discovery Challenges

Agents face challenges with current wheels:

- **Sequential Processing**: Must read description text linearly
- **External Lookups**: Need to fetch documentation from external URLs
- **Unstructured Content**: Free-form text descriptions lack semantic structure
- **Missing Context**: No indication of use cases, complexity, or prerequisites
- **No Templates**: No structured starting points for common usage patterns

## Tools and Ecosystem

### Core Tools

- **wheel**: Reference implementation for building and installing wheels
- **pip**: Package installer that handles wheels
- **setuptools**: Build system that can create wheels
- **twine**: Tool for uploading packages to PyPI

### Validation Tools

- **check-wheel-contents**: Validates wheel structure
- **wheel-inspect**: Inspects wheel metadata
- **pkginfo**: Extracts metadata from packages

### Build Tools

- **build**: PEP 517 compatible build frontend
- **flit**: Simple packaging tool
- **poetry**: Dependency management and packaging
- **hatch**: Modern Python project manager

## Standards Bodies and Governance

### Python Packaging Authority (PyPA)

The PyPA maintains the core packaging tools and standards:
- **Website**: https://www.pypa.io/
- **GitHub**: https://github.com/pypa
- **Specifications**: https://packaging.python.org/specifications/

### Python Enhancement Proposal Process

New packaging standards go through the PEP process:
1. **Draft**: Initial proposal
2. **Discussion**: Community feedback
3. **Acceptance**: BDFL/Steering Council approval
4. **Implementation**: Reference implementation
5. **Final**: Standard adoption

## Relationship to Miri Standard

### Foundation for Extension

The wheel format provides an excellent foundation for Miri extensions because:

1. **Extensible Structure**: Can add new files to `.dist-info/` directory
2. **Metadata Framework**: Existing metadata system can be enhanced
3. **Tool Compatibility**: Extensions can coexist with existing tools
4. **Validation Support**: Existing validation can be extended

### Miri Enhancement Areas

The Miri Standard will enhance wheels by adding:

1. **Structured Examples**: `miri-examples/` directory with categorized code samples
2. **Agent Metadata**: `MIRI` file with JSON schema for programmatic access
3. **Learning Paths**: Structured progression through package capabilities
4. **Rich Templates**: Boilerplate code with clear placeholders
5. **Contextual Relationships**: Enhanced dependency and usage information

### Backward Compatibility

Miri-enhanced wheels maintain full compatibility:
- Standard tools can still install and use the packages
- Additional Miri metadata is optional and non-breaking
- Existing metadata formats remain unchanged
- New metadata supplements rather than replaces existing information

## References

- [PEP Index](https://peps.python.org/): Complete list of Python Enhancement Proposals
- [Python Packaging User Guide](https://packaging.python.org/): Official packaging documentation
- [Wheel Documentation](https://wheel.readthedocs.io/): Reference implementation docs
- [PyPA Specifications](https://packaging.python.org/specifications/): Formal specifications
- [Python Package Index](https://pypi.org/): Central repository for Python packages
