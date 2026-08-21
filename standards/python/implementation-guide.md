# Miri Standard Implementation Guide

*A practical guide to implementing agent-friendly Python wheel extensions.*

## Quick Start

This guide walks you through implementing the Miri Standard in your Python package, from basic compliance to full
AI-friendly features.

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Basic Implementation](#2-basic-implementation)
3. [Enhanced Package Structure](#3-enhanced-package-structure)
4. [Metadata Generation](#4-metadata-generation)
5. [Build System Integration](#5-build-system-integration)
6. [Testing and Validation](#6-testing-and-validation)
7. [Complete Build Process](#7-complete-build-process)
8. [Complete Examples](#8-complete-examples)

## 1. Prerequisites

### 1.1 Requirements

- Python 3.8+
- Modern build system (setuptools 61.0+, or poetry, hatch, etc.)
- Understanding of Python packaging basics

### 1.2 Project Structure

Starting with a typical Python package:

```text
my_package/
├── pyproject.toml
├── README.md
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── client.py
│       └── exceptions.py
└── tests/
    └── test_basic.py
```

## 2. Basic Implementation

### 2.1 Step 1: Create Examples Directory

Create the examples structure:

```bash
mkdir -p src/my_package/examples
mkdir -p src/my_package/examples/use_cases
```

### 2.2 Step 2: Create Quickstart Example

Create `src/my_package/examples/quickstart.py`:

```python
#!/usr/bin/env python3
"""
Quick Start Guide for My Package

This example demonstrates the most common usage patterns.
Perfect for AI agents to understand basic package operations.

Complexity: beginner
Tags: basic, getting-started, authentication
Estimated time: 5 minutes
Prerequisites: none
"""

import os
from my_package import MyClient, MyError

def main():
    """Main quickstart demonstration."""
    
    # 1. Initialize client
    print("=== Basic Usage ===")
    try:
        # Replace with your actual initialization
        client = MyClient(api_key="demo-key")
        
        # Basic operation
        result = client.process({"message": "Hello, World!"})
        print(f"✓ Success: {result}")
        
    except MyError as e:
        print(f"✗ Error: {e}")
        return
    
    # 2. Common operations
    print("\n=== Common Operations ===")
    
    operations = [
        {"action": "create", "data": {"name": "test"}},
        {"action": "update", "data": {"id": 1, "name": "updated"}},
        {"action": "list", "data": {}}
    ]
    
    for op in operations:
        try:
            result = client.process(op)
            print(f"✓ {op['action']}: Success")
        except MyError as e:
            print(f"✗ {op['action']}: {e}")
    
    print("\n=== Next Steps ===")
    print("1. Check examples/authentication.py for auth patterns")
    print("2. See examples/use_cases/ for real-world scenarios")
    print("3. Read docs/api_reference.md for complete API")

if __name__ == "__main__":
    main()
```

### 2.3 Step 3: Create Examples Index

Create `src/my_package/examples/__init__.py`:

```python
"""
Package Examples

This module contains working examples that AI agents can immediately
understand and adapt for their specific use cases.

Available examples:
- quickstart: Basic usage patterns
- authentication: Auth handling patterns
- use_cases: Real-world scenarios

Usage:
    from my_package.examples import quickstart
    # or
    import my_package
    examples_dir = my_package.get_examples_dir()
"""

from pathlib import Path
from typing import List

EXAMPLES_DIR = Path(__file__).parent

def list_examples() -> List[str]:
    """Return all available example files."""
    examples = []
    for py_file in EXAMPLES_DIR.rglob("*.py"):
        if py_file.name != "__init__.py":
            rel_path = py_file.relative_to(EXAMPLES_DIR)
            examples.append(str(rel_path.with_suffix('')))
    return examples

def get_example_content(name: str) -> str:
    """Get content of specific example file."""
    # Try direct file
    example_file = EXAMPLES_DIR / f"{name}.py"
    if example_file.exists():
        return example_file.read_text()
    
    # Try in subdirectories
    for py_file in EXAMPLES_DIR.rglob(f"{name}.py"):
        return py_file.read_text()
    
    raise FileNotFoundError(f"Example '{name}' not found")
```

### 2.4 Step 4: Add Discovery APIs to Main Module

Update `src/my_package/__init__.py`:

```python
"""
My Package - AI-Friendly SDK

This package includes everything autonomous agents need:
- Working examples in my_package.examples
- Documentation in my_package.docs  
- Code templates in my_package.templates
- Discovery helpers for runtime access

Quick Start:
    >>> from my_package import MyClient
    >>> client = MyClient(api_key="your-key")
    >>> result = client.process({"message": "hello"})
    
For Autonomous Agents:
    >>> import my_package
    >>> my_package.show_quickstart()  # Get immediate usage guide
    >>> my_package.list_examples()    # List all examples
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import importlib.metadata

# Main exports
from .client import MyClient
from .exceptions import MyError

__version__ = "1.0.0"
__all__ = ["MyClient", "MyError"]

def get_examples_dir() -> Path:
    """Get path to installed examples directory."""
    return Path(__file__).parent / "examples"

def get_docs_dir() -> Path:
    """Get path to installed documentation."""
    return Path(__file__).parent / "docs"

def get_templates_dir() -> Path:
    """Get path to code templates."""
    return Path(__file__).parent / "templates"

def get_agent_metadata() -> Dict:
    """
    Get agent-specific metadata from wheel distribution.
    
    Returns structured information about examples, usage patterns,
    and learning resources for autonomous agents.
    """
    try:
        dist = importlib.metadata.distribution("my-package")
        # Try to find AGENT_EXAMPLES.json in distribution
        if hasattr(dist, 'files') and dist.files:
            for file in dist.files:
                if file.name == "AGENT_EXAMPLES.json":
                    return json.loads(file.read_text())
    except Exception:
        pass
    
    # Fallback to scanning examples directory
    examples_dir = get_examples_dir()
    if not examples_dir.exists():
        return {"version": "1.0", "examples": {}}
    
    examples = {}
    for py_file in examples_dir.rglob("*.py"):
        if py_file.name != "__init__.py":
            rel_path = py_file.relative_to(examples_dir)
            name = str(rel_path.with_suffix(''))
            examples[name] = {
                "file": f"examples/{rel_path}",
                "description": _extract_description(py_file)
            }
    
    return {
        "version": "1.0",
        "examples": examples
    }

def list_examples() -> List[str]:
    """List all available example files."""
    examples_dir = get_examples_dir()
    if not examples_dir.exists():
        return []
    
    examples = []
    for py_file in examples_dir.rglob("*.py"):
        if py_file.name != "__init__.py":
            rel_path = py_file.relative_to(examples_dir)
            examples.append(str(rel_path.with_suffix('')))
    
    return examples

def show_quickstart() -> str:
    """Display quickstart guide for immediate usage."""
    quickstart = get_examples_dir() / "quickstart.py"
    if quickstart.exists():
        return quickstart.read_text()
    
    return '''
# Quick Start Example
from my_package import MyClient

# Initialize client
client = MyClient(api_key="your-api-key")

# Basic operation
result = client.process({"message": "Hello, World!"})
print(result)
'''

def _extract_description(file_path: Path) -> str:
    """Extract description from example file docstring."""
    try:
        content = file_path.read_text()
        lines = content.strip().split('\n')
        
        # Look for docstring
        in_docstring = False
        description_lines = []
        
        for line in lines:
            if '"""' in line and not in_docstring:
                in_docstring = True
                # Check if docstring starts and ends on same line
                if line.count('"""') == 2:
                    return line.split('"""')[1].strip()
                continue
            elif '"""' in line and in_docstring:
                break
            elif in_docstring and line.strip():
                # Skip title line, get description
                if not description_lines and line.strip():
                    continue  # Skip title
                description_lines.append(line.strip())
        
        return ' '.join(description_lines[:2])  # First two description lines
    except Exception:
        return "No description available"
```

## 3. Enhanced Package Structure

### 3.1 Complete Directory Structure

Expand your package to include all Miri components:

```text
src/my_package/
├── __init__.py                   # Enhanced with discovery APIs
├── client.py                     # Main functionality
├── exceptions.py                 # Custom exceptions
├── examples/                     # Miri: Example code
│   ├── __init__.py              # Example discovery
│   ├── quickstart.py            # Basic usage (required)
│   ├── authentication.py        # Auth patterns
│   ├── error_handling.py        # Error management
│   ├── advanced.py              # Complex workflows
│   └── use_cases/               # Real-world scenarios
│       ├── __init__.py
│       ├── data_processing.py
│       ├── api_integration.py
│       └── batch_operations.py
├── docs/                        # Miri: Embedded docs
│   ├── __init__.py
│   ├── api_reference.md
│   ├── troubleshooting.md
│   └── migration_guide.md
└── templates/                   # Miri: Code templates
    ├── __init__.py
    ├── basic_project.py
    ├── advanced_project.py
    └── integration_template.py
```

### 3.2 Create Additional Examples

Create `src/my_package/examples/authentication.py`:

```python
#!/usr/bin/env python3
"""
Authentication Patterns

Comprehensive guide to all authentication methods supported by the package.
Includes error handling and best practices.

Complexity: intermediate
Tags: authentication, security, api-keys
Estimated time: 10 minutes
Prerequisites: quickstart
"""

import os
from my_package import MyClient, MyError

def api_key_auth():
    """Demonstrate API key authentication."""
    print("=== API Key Authentication ===")
    
    # Method 1: Direct API key
    try:
        client = MyClient(api_key="your-api-key")
        result = client.process({"test": "data"})
        print("✓ Direct API key: Success")
    except MyError as e:
        print(f"✗ Direct API key failed: {e}")
    
    # Method 2: Environment variable (recommended)
    try:
        api_key = os.getenv("MY_PACKAGE_API_KEY")
        if not api_key:
            print("⚠ MY_PACKAGE_API_KEY environment variable not set")
            return
            
        client = MyClient(api_key=api_key)
        result = client.process({"test": "data"})
        print("✓ Environment API key: Success")
    except MyError as e:
        print(f"✗ Environment API key failed: {e}")

def main():
    """Run authentication examples."""
    api_key_auth()
    
    print("\n=== Best Practices ===")
    print("1. Store API keys in environment variables")
    print("2. Never hardcode API keys in source code")
    print("3. Always handle authentication errors")
    print("4. Use the most secure method available")

if __name__ == "__main__":
    main()
```

### 3.3 Create Documentation Files

Create `src/my_package/docs/__init__.py`:

```python
"""
Package Documentation

Embedded documentation accessible without external lookups.
"""

from pathlib import Path

DOCS_DIR = Path(__file__).parent

def get_api_reference() -> str:
    """Get API reference documentation."""
    api_ref = DOCS_DIR / "api_reference.md"
    if api_ref.exists():
        return api_ref.read_text()
    return "API reference not available"

def get_troubleshooting() -> str:
    """Get troubleshooting guide."""
    troubleshooting = DOCS_DIR / "troubleshooting.md"
    if troubleshooting.exists():
        return troubleshooting.read_text()
    return "Troubleshooting guide not available"
```

Create `src/my_package/docs/api_reference.md`:

```markdown
# API Reference

## MyClient

Main client class for interacting with the service.

### Constructor

```python
MyClient(api_key: str, base_url: str = None, timeout: int = 30)
```text

**Parameters:**

- `api_key` (str): Your API key for authentication
- `base_url` (str, optional): Custom base URL for the service
- `timeout` (int, optional): Request timeout in seconds (default: 30)

### Methods

#### process(data: dict) -> dict

Process data through the service.

**Parameters:**

- `data` (dict): Data to process

**Returns:**

- `dict`: Processed result

**Raises:**

- `MyError`: If processing fails
- `AuthenticationError`: If API key is invalid

**Example:**

```python
client = MyClient(api_key="your-key")
result = client.process({"message": "hello"})
```text

## Exceptions

### MyError

Base exception for all package errors.

### AuthenticationError

Raised when authentication fails.

```

## 4. Metadata Generation

### 4.1 Create AGENT_EXAMPLES.json

Create a build script `scripts/generate_metadata.py`:

```python
#!/usr/bin/env python3
"""
Generate Miri metadata files during build process.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any

def extract_example_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract metadata from example file docstring."""
    content = file_path.read_text()
    
    # Extract docstring
    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if not docstring_match:
        return {}
    
    docstring = docstring_match.group(1).strip()
    lines = docstring.split('\n')
    
    # Parse metadata
    metadata = {
        "description": "",
        "complexity": "unknown",
        "tags": [],
        "estimated_time": "",
        "prerequisites": []
    }
    
    # Extract title and description
    title_line = lines[0].strip() if lines else ""
    desc_lines = []
    metadata_started = False
    
    for line in lines[1:]:
        line = line.strip()
        if line.startswith("Complexity:"):
            metadata["complexity"] = line.split(":", 1)[1].strip().lower()
            metadata_started = True
        elif line.startswith("Tags:"):
            tags_str = line.split(":", 1)[1].strip()
            metadata["tags"] = [t.strip() for t in tags_str.split(",")]
            metadata_started = True
        elif line.startswith("Estimated time:"):
            metadata["estimated_time"] = line.split(":", 1)[1].strip()
            metadata_started = True
        elif line.startswith("Prerequisites:"):
            prereq_str = line.split(":", 1)[1].strip()
            if prereq_str.lower() != "none":
                metadata["prerequisites"] = [p.strip() for p in prereq_str.split(",")]
            metadata_started = True
        elif not metadata_started and line:
            desc_lines.append(line)
    
    metadata["description"] = " ".join(desc_lines).strip()
    if not metadata["description"]:
        metadata["description"] = title_line
    
    return metadata

def generate_agent_examples_json(package_dir: Path) -> Dict[str, Any]:
    """Generate AGENT_EXAMPLES.json content."""
    examples_dir = package_dir / "examples"
    
    if not examples_dir.exists():
        return {"version": "1.0", "examples": {}}
    
    examples = {}
    categories = {
        "getting_started": {
            "name": "Getting Started",
            "description": "Essential examples for new users",
            "examples": []
        },
        "authentication": {
            "name": "Authentication",
            "description": "Authentication and security patterns",
            "examples": []
        },
        "advanced": {
            "name": "Advanced Usage",
            "description": "Complex workflows and patterns",
            "examples": []
        }
    }
    
    learning_paths = {
        "complete_guide": {
            "name": "Complete Package Guide",
            "description": "Full progression from basics to advanced usage",
            "examples": [],
            "estimated_total_time": "30 minutes"
        }
    }
    
    for py_file in examples_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        rel_path = py_file.relative_to(examples_dir)
        example_id = str(rel_path.with_suffix(''))
        
        metadata = extract_example_metadata(py_file)
        
        examples[example_id] = {
            "description": metadata.get("description", "No description"),
            "file": f"examples/{rel_path}",
            "complexity": metadata.get("complexity", "unknown"),
            "tags": metadata.get("tags", []),
            "dependencies": [],  # Could be extracted from imports
            "estimated_time": metadata.get("estimated_time", "unknown"),
            "prerequisites": metadata.get("prerequisites", []),
            "related": [],  # Could be inferred from tags
            "use_cases": []  # Could be extracted from content
        }
        
        # Categorize examples
        if "auth" in metadata.get("tags", []) or "authentication" in example_id:
            categories["authentication"]["examples"].append(example_id)
        elif metadata.get("complexity") == "advanced" or "advanced" in example_id:
            categories["advanced"]["examples"].append(example_id)
        else:
            categories["getting_started"]["examples"].append(example_id)
        
        # Add to learning path based on complexity
        if metadata.get("complexity") in ["beginner", "intermediate", "advanced"]:
            learning_paths["complete_guide"]["examples"].append(example_id)
    
    return {
        "version": "1.0",
        "generated_at": "build-time",
        "examples": examples,
        "categories": categories,
        "learning_paths": learning_paths
    }

def main():
    """Generate all metadata files."""
    # Find package directory
    src_dir = Path("src")
    package_dirs = [d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    
    if not package_dirs:
        print("No package directory found in src/")
        return
    
    package_dir = package_dirs[0]  # Use first package found
    print(f"Generating metadata for {package_dir.name}")
    
    # Generate AGENT_EXAMPLES.json
    agent_examples = generate_agent_examples_json(package_dir)
    
    # Create build metadata directory
    build_dir = Path("build/metadata")
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Write AGENT_EXAMPLES.json
    with open(build_dir / "AGENT_EXAMPLES.json", "w") as f:
        json.dump(agent_examples, f, indent=2)
    
    print(f"Generated AGENT_EXAMPLES.json with {len(agent_examples['examples'])} examples")

if __name__ == "__main__":
    main()
```

## 5. Build System Integration

### 5.1 Update pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "1.0.0"
description = "AI-friendly package with embedded examples"
authors = [{name = "Your Name", email = "you@example.com"}]
license = {text = "MIT"}
requires-python = ">=3.8"
dependencies = [
    "requests>=2.25.0"
]

[project.optional-dependencies]
dev = ["pytest>=6.0", "black", "mypy"]

[tool.setuptools.packages.find]
where = ["src"]
include = ["my_package*"]

[tool.setuptools.package-data]
my_package = [
    "examples/*.py",
    "examples/**/*.py",
    "docs/*.md",
    "docs/**/*.md",
    "templates/*.py",
    "templates/**/*.py"
]

# Miri-specific configuration
[tool.miri]
compliance_level = "full"
examples_dir = "examples"
docs_dir = "docs"
templates_dir = "templates"
quickstart_file = "examples/quickstart.py"
```

### 5.2 Custom Build Hook

Create `build_hooks.py`:

```python
"""
Custom build hooks for Miri metadata generation.
"""

import json
from pathlib import Path
from setuptools import build_meta as _default
from scripts.generate_metadata import generate_agent_examples_json

# Pass through the setuptools hooks we do not customize.
prepare_metadata_for_build_wheel = _default.prepare_metadata_for_build_wheel
get_requires_for_build_wheel = _default.get_requires_for_build_wheel
get_requires_for_build_sdist = _default.get_requires_for_build_sdist
build_sdist = _default.build_sdist


def _write_agent_examples():
    """Generate AGENT_EXAMPLES.json into each package; return the files written."""
    written = []
    for package_dir in (d for d in Path("src").iterdir() if d.is_dir()):
        agent_examples = generate_agent_examples_json(package_dir)
        target = package_dir / "AGENT_EXAMPLES.json"
        target.write_text(json.dumps(agent_examples, indent=2))
        written.append(target)
    return written


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Generate Miri metadata, build the wheel with setuptools, then clean up."""
    written = _write_agent_examples()
    try:
        return _default.build_wheel(wheel_directory, config_settings, metadata_directory)
    finally:
        for target in written:
            target.unlink(missing_ok=True)
```

Update pyproject.toml to use custom backend:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "build_hooks"
backend-path = ["."]
```

## 6. Testing and Validation

### 6.1 Create Miri Tests

Create `tests/test_miri.py`:

```python
"""
Tests for Miri Standard compliance.
"""

import json
import pytest
from pathlib import Path
import my_package

def test_discovery_apis():
    """Test that all discovery APIs are available."""
    # Test required functions exist
    assert hasattr(my_package, 'get_examples_dir')
    assert hasattr(my_package, 'list_examples')
    assert hasattr(my_package, 'show_quickstart')
    assert hasattr(my_package, 'get_agent_metadata')
    
    # Test functions return expected types
    examples_dir = my_package.get_examples_dir()
    assert isinstance(examples_dir, Path)
    
    examples = my_package.list_examples()
    assert isinstance(examples, list)
    
    quickstart = my_package.show_quickstart()
    assert isinstance(quickstart, str)
    assert len(quickstart) > 0
    
    metadata = my_package.get_agent_metadata()
    assert isinstance(metadata, dict)
    assert "version" in metadata

def test_examples_directory():
    """Test examples directory structure."""
    examples_dir = my_package.get_examples_dir()
    assert examples_dir.exists()
    
    # Test quickstart exists
    quickstart_file = examples_dir / "quickstart.py"
    assert quickstart_file.exists()
    
    # Test quickstart is executable Python
    quickstart_content = quickstart_file.read_text()
    assert "def main(" in quickstart_content
    assert 'if __name__ == "__main__"' in quickstart_content

def test_examples_execution():
    """Test that examples can be imported without errors."""
    try:
        from my_package.examples import quickstart
        assert hasattr(quickstart, 'main')
    except ImportError as e:
        pytest.fail(f"Could not import quickstart example: {e}")

def test_ai_metadata_structure():
    """Test AI metadata has required structure."""
    metadata = my_package.get_agent_metadata()
    
    # Test required fields
    assert "version" in metadata
    assert "examples" in metadata
    
    # Test examples structure
    examples = metadata["examples"]
    if examples:
        for example_id, example_data in examples.items():
            assert "description" in example_data
            assert "file" in example_data
            assert "complexity" in example_data

def test_package_data_inclusion():
    """Test that package data is properly included."""
    import importlib.resources
    
    # Test examples are included
    try:
        files = importlib.resources.files("my_package.examples")
        example_files = [f.name for f in files.iterdir() if f.name.endswith('.py')]
        assert "quickstart.py" in example_files
    except Exception as e:
        pytest.fail(f"Examples not properly included in package: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
```

### 6.2 Validation Script

Create `scripts/validate_miri.py`:

```python
#!/usr/bin/env python3
"""
Validate Miri Standard compliance.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

def validate_examples_directory(package_dir: Path) -> List[str]:
    """Validate examples directory structure."""
    errors = []
    
    examples_dir = package_dir / "examples"
    if not examples_dir.exists():
        errors.append("Missing examples/ directory")
        return errors
    
    # Check for quickstart.py
    quickstart = examples_dir / "quickstart.py"
    if not quickstart.exists():
        errors.append("Missing examples/quickstart.py (required)")
    else:
        # Validate quickstart content
        content = quickstart.read_text()
        if "def main(" not in content:
            errors.append("quickstart.py missing main() function")
        if 'if __name__ == "__main__"' not in content:
            errors.append("quickstart.py missing main execution block")
    
    # Check __init__.py
    init_file = examples_dir / "__init__.py"
    if not init_file.exists():
        errors.append("Missing examples/__init__.py")
    
    return errors

def validate_discovery_apis(package_dir: Path) -> List[str]:
    """Validate discovery APIs in __init__.py."""
    errors = []
    
    init_file = package_dir / "__init__.py"
    if not init_file.exists():
        errors.append("Missing package __init__.py")
        return errors
    
    content = init_file.read_text()
    
    required_functions = [
        "get_examples_dir",
        "list_examples", 
        "show_quickstart",
        "get_agent_metadata"
    ]
    
    for func in required_functions:
        if f"def {func}(" not in content:
            errors.append(f"Missing discovery function: {func}")
    
    return errors

def validate_agent_metadata(metadata: Dict[str, Any]) -> List[str]:
    """Validate AGENT_EXAMPLES.json structure."""
    errors = []
    
    # Check required top-level fields
    required_fields = ["version", "examples"]
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
    
    # Validate examples structure
    if "examples" in metadata:
        examples = metadata["examples"]
        if not isinstance(examples, dict):
            errors.append("'examples' must be a dictionary")
        else:
            for example_id, example_data in examples.items():
                if not isinstance(example_data, dict):
                    errors.append(f"Example '{example_id}' must be a dictionary")
                    continue
                
                # Check required example fields
                required_example_fields = ["description", "file", "complexity"]
                for field in required_example_fields:
                    if field not in example_data:
                        errors.append(f"Example '{example_id}' missing field: {field}")
                
                # Validate complexity values
                if "complexity" in example_data:
                    valid_complexity = ["beginner", "intermediate", "advanced", "unknown"]
                    if example_data["complexity"] not in valid_complexity:
                        errors.append(f"Example '{example_id}' has invalid complexity: {example_data['complexity']}")
    
    return errors

def validate_package(package_path: Path) -> Dict[str, List[str]]:
    """Validate complete package for Miri compliance."""
    results = {
        "examples": [],
        "discovery_apis": [],
        "metadata": [],
        "overall": []
    }
    
    if not package_path.exists():
        results["overall"].append(f"Package path does not exist: {package_path}")
        return results
    
    # Validate examples
    results["examples"] = validate_examples_directory(package_path)
    
    # Validate discovery APIs
    results["discovery_apis"] = validate_discovery_apis(package_path)
    
    # Try to load and validate AI metadata
    try:
        # This would need to import the actual package
        # For now, just check if we can generate metadata
        from scripts.generate_metadata import generate_agent_examples_json
        metadata = generate_agent_examples_json(package_path)
        results["metadata"] = validate_agent_metadata(metadata)
    except Exception as e:
        results["metadata"].append(f"Could not generate/validate metadata: {e}")
    
    # Overall compliance check
    total_errors = sum(len(errors) for errors in results.values())
    if total_errors == 0:
        results["overall"].append("✓ Full Miri compliance")
    elif len(results["examples"]) == 0 and len(results["discovery_apis"]) == 0:
        results["overall"].append("✓ Basic Miri compliance")
    else:
        results["overall"].append(f"✗ {total_errors} compliance issues found")
    
    return results

def main():
    """Main validation function."""
    if len(sys.argv) != 2:
        print("Usage: python validate_miri.py <package_directory>")
        sys.exit(1)
    
    package_path = Path(sys.argv[1])
    results = validate_package(package_path)
    
    print(f"Miri Standard Validation Report for {package_path.name}")
    print("=" * 50)
    
    for category, errors in results.items():
        print(f"\n{category.title()}:")
        if not errors:
            print("  ✓ No issues found")
        else:
            for error in errors:
                print(f"  ✗ {error}")
    
    # Exit with error code if issues found
    total_errors = sum(len(errors) for errors in results.values() if errors)
    sys.exit(1 if total_errors > 0 else 0)

if __name__ == "__main__":
    main()
```

## 7. Complete Build Process

### 7.1 Build Script

Create `scripts/build.py`:

```python
#!/usr/bin/env python3
"""
Complete build script for Miri-compliant packages.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd: str, description: str):
    """Run a command and handle errors."""
    print(f"\n=== {description} ===")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"✗ Failed: {description}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    else:
        print(f"✓ Success: {description}")
        if result.stdout:
            print(result.stdout)

def main():
    """Main build process."""
    print("Building Miri-compliant Python package")
    
    # 1. Generate metadata
    run_command(
        "python scripts/generate_metadata.py",
        "Generating Miri metadata"
    )
    
    # 2. Validate compliance
    src_dir = Path("src")
    package_dirs = [d for d in src_dir.iterdir() if d.is_dir()]
    if package_dirs:
        package_dir = package_dirs[0]
        run_command(
            f"python scripts/validate_miri.py {package_dir}",
            "Validating Miri compliance"
        )
    
    # 3. Run tests
    run_command(
        "python -m pytest tests/ -v",
        "Running tests"
    )
    
    # 4. Build wheel
    run_command(
        "python -m build",
        "Building wheel"
    )
    
    print("\n🎉 Build completed successfully!")
    print("Your Miri-compliant package is ready in dist/")

if __name__ == "__main__":
    main()
```

### 7.2 Usage Instructions

1. **Install build dependencies**:

   ```bash
   pip install build pytest
   ```

2. **Run the build**:

   ```bash
   python scripts/build.py
   ```

3. **Install and test**:

   ```bash
   pip install dist/my_package-1.0.0-py3-none-any.whl
   python -c "import my_package; print(my_package.show_quickstart())"
   ```

## 8. Complete Examples

### 8.1 Minimal Miri Package

For a minimal implementation, you need:

1. `examples/quickstart.py` - Basic usage example
2. Enhanced `__init__.py` with discovery functions
3. `pyproject.toml` with package data inclusion

### 8.2 Full Miri Package

For full compliance, add:

1. Complete examples directory structure
2. Documentation directory
3. Templates directory  
4. Metadata generation scripts
5. Validation and testing

This implementation guide provides everything needed to create AI-friendly Python packages that follow the Miri
Standard, enabling autonomous agents to immediately understand and use your code.
