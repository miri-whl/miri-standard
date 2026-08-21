# Miri Standard: Pre-Parsed Agent Metadata Specification

*Specification Version: 1.0-draft*  
*Status: Draft*  
*Created: 2025*

## Abstract

This specification defines pre-parsed, structured metadata formats that travel inside Python wheel packages, so the
information an agent needs about a package is available offline and version-locked to the exact code it describes,
without re-deriving it from source on every use. The intended benefit — faster, more reliable agent integration with
SDKs and libraries — is a design goal of the standard, not yet a measured result.

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Solution Overview](#2-solution-overview)
3. [Agent Metadata Directory Structure](#3-agent-metadata-directory-structure)
4. [Core Metadata Files](#4-core-metadata-files)
5. [Automated Generation](#5-automated-generation)
6. [Integration Patterns](#6-integration-patterns)
7. [Performance Optimization](#7-performance-optimization)
8. [Implementation Requirements](#8-implementation-requirements)

## 1. Problem Statement

### 1.1 Current Inefficiencies

Autonomous agents face significant performance bottlenecks when working with Python packages:

- **Continuous Re-parsing**: Agents repeatedly parse the same documentation and examples
- **Unstructured Data**: Free-form text requires complex NLP processing
- **Version Inconsistency**: Documentation often lags behind code changes
- **Context Loss**: Agents lose learned patterns between sessions
- **Slow Discovery**: Sequential reading of documentation prevents instant API comprehension

### 1.2 Performance Impact

These inefficiencies result in:

- **Slow Integration**: understanding an unfamiliar SDK from unstructured sources is slow and repeated each session
- **Repeated Work**: Same parsing operations across multiple projects
- **Inconsistent Results**: Varying interpretation of unstructured documentation
- **Resource Waste**: Unnecessary compute cycles on repetitive tasks

## 2. Solution Overview

### 2.1 Pre-Parsed Metadata Approach

The Miri Standard addresses these issues by providing:

- **Structured API Index**: Machine-readable API signatures and metadata
- **Usage Pattern Library**: Pre-extracted, categorized code patterns
- **Migration Guides**: Structured version change documentation
- **Agent Prompt Templates**: Optimized interaction guides for different agent types

### 2.2 Key Benefits

- **Instant Consumption**: Agents access structured data immediately
- **Consistent Interpretation**: Standardized formats eliminate ambiguity
- **Version Synchronization**: Automated generation ensures accuracy
- **Performance Optimization**: Eliminate redundant parsing operations
- **Context Preservation**: Structured patterns enable better code suggestions

## 3. Agent Metadata Directory Structure

### 3.1 Enhanced Wheel Structure

```text
package-1.0.0-py3-none-any.whl
├── package/                          # Standard package code
│   ├── __init__.py
│   └── core.py
├── package/agent-metadata/           # Miri: Pre-parsed agent data
│   ├── sdk-manifest.json            # Core API index (required)
│   ├── usage-patterns.json          # Common code patterns (required)
│   ├── migration-guide.json         # Version-specific changes
│   ├── prompt-templates.md          # Agent interaction guides
│   ├── api-graph.json              # API relationship graph
│   ├── performance-hints.json      # Optimization suggestions
│   └── lifecycle.json              # Identity, advisory sources (required)
├── package/examples/                # Miri: Example code
└── package-1.0.0.dist-info/        # Standard + Miri metadata
    ├── METADATA
    ├── AGENT_EXAMPLES.json
    └── ...
```

### 3.2 Directory Organization

The `agent-metadata/` directory contains pre-processed data optimized for agent consumption:

- **Immediate Access**: No parsing required, direct JSON consumption
- **Structured Relationships**: API connections and dependencies mapped
- **Context-Rich**: Includes usage patterns, examples, and migration paths
- **Version-Aware**: Synchronized with package version automatically

## 4. Core Metadata Files

### 4.1 sdk-manifest.json (Required)

**Purpose**: Core API index with structured signatures and metadata.

**Schema**:

```json
{
  "$schema": "https://miri-standard.org/schemas/sdk-manifest-v1.json",
  "sdk_version": "1.2.0",
  "generated_at": "2025-08-30T12:00:00Z",
  "miri_version": "1.0",
  "quick_reference": {
    "primary_classes": ["DatabaseClient", "QueryBuilder", "Transaction"],
    "key_methods": ["connect", "query", "execute", "migrate"],
    "common_imports": [
      "from your_sdk import DatabaseClient",
      "from your_sdk.query import QueryBuilder"
    ],
    "typical_workflow": [
      "client = DatabaseClient(connection_string)",
      "client.connect()",
      "result = client.query('SELECT * FROM users')",
      "client.close()"
    ]
  },
  "api_index": {
    "DatabaseClient": {
      "type": "class",
      "purpose": "Main database interface for connection and query management",
      "complexity": "intermediate",
      "init_params": {
        "connection_string": {
          "type": "str",
          "required": true,
          "description": "Database connection string",
          "example": "postgresql://user:pass@localhost/db"
        },
        "timeout": {
          "type": "int",
          "required": false,
          "default": 30,
          "description": "Connection timeout in seconds"
        }
      },
      "key_methods": {
        "connect": {
          "purpose": "Establish database connection",
          "returns": "bool",
          "raises": ["ConnectionError", "AuthenticationError"],
          "example": "success = client.connect()"
        },
        "query": {
          "purpose": "Execute SQL query and return results",
          "params": {
            "sql": {"type": "str", "description": "SQL query string"},
            "params": {"type": "dict", "required": false, "description": "Query parameters"}
          },
          "returns": "QueryResult",
          "example": "result = client.query('SELECT * FROM users WHERE id = %(id)s', {'id': 123})"
        }
      },
      "usage_patterns": ["basic_connection", "parameterized_query", "transaction_handling"],
      "related_classes": ["QueryBuilder", "Transaction"],
      "common_errors": ["ConnectionError", "QuerySyntaxError", "AuthenticationError"]
    },
    "QueryBuilder": {
      "type": "class",
      "purpose": "Fluent interface for building SQL queries programmatically",
      "complexity": "advanced",
      "usage_patterns": ["fluent_query", "dynamic_filtering"],
      "example": "query = QueryBuilder().select('*').from_table('users').where('active', True)"
    }
  },
  "error_handling": {
    "ConnectionError": {
      "when": "Database connection fails",
      "common_causes": ["Invalid connection string", "Network issues", "Database unavailable"],
      "solutions": ["Check connection string", "Verify network connectivity", "Ensure database is running"]
    }
  },
  "configuration": {
    "environment_variables": {
      "DATABASE_URL": "Primary database connection string",
      "DB_TIMEOUT": "Connection timeout override"
    },
    "config_files": {
      "database.yaml": "YAML configuration for multiple environments"
    }
  }
}
```

### 4.2 usage-patterns.json (Required)

**Purpose**: Pre-extracted, categorized code patterns for common use cases.

**Schema**:

```json
{
  "$schema": "https://miri-standard.org/schemas/usage-patterns-v1.json",
  "version": "1.0",
  "generated_at": "2025-08-30T12:00:00Z",
  "patterns": [
    {
      "id": "basic_connection",
      "name": "Basic Database Connection",
      "description": "Standard pattern for connecting to database and executing queries",
      "complexity": "beginner",
      "category": "connection",
      "tags": ["connection", "query", "basic"],
      "code": "from your_sdk import DatabaseClient\n\n# Initialize client\nclient = DatabaseClient('postgresql://user:pass@localhost/db')\n\n# Connect and query\nclient.connect()\nresult = client.query('SELECT * FROM users')\nprint(f'Found {len(result)} users')\n\n# Always close connection\nclient.close()",
      "explanation": {
        "steps": [
          "Import the DatabaseClient class",
          "Create client instance with connection string", 
          "Establish connection to database",
          "Execute SQL query",
          "Process results",
          "Close connection to free resources"
        ],
        "key_points": [
          "Always close connections to prevent resource leaks",
          "Use connection strings for configuration",
          "Handle connection errors appropriately"
        ]
      },
      "variations": [
        {
          "name": "With context manager",
          "code": "with DatabaseClient('postgresql://...') as client:\n    result = client.query('SELECT * FROM users')\n    # Connection automatically closed"
        }
      ],
      "related_patterns": ["parameterized_query", "error_handling"],
      "prerequisites": [],
      "estimated_time": "2 minutes"
    },
    {
      "id": "parameterized_query",
      "name": "Parameterized Query Execution",
      "description": "Safe query execution with parameters to prevent SQL injection",
      "complexity": "intermediate",
      "category": "security",
      "tags": ["query", "security", "parameters"],
      "code": "# Safe parameterized query\nuser_id = 123\nresult = client.query(\n    'SELECT * FROM users WHERE id = %(user_id)s AND active = %(active)s',\n    {'user_id': user_id, 'active': True}\n)\n\n# Multiple parameter styles supported\nresult = client.query(\n    'SELECT * FROM orders WHERE user_id = ? AND status = ?',\n    [user_id, 'completed']\n)",
      "explanation": {
        "security_note": "Always use parameterized queries to prevent SQL injection attacks",
        "parameter_styles": ["named (%(name)s)", "positional (?)", "numeric (:1, :2)"]
      },
      "prerequisites": ["basic_connection"],
      "estimated_time": "3 minutes"
    }
  ],
  "categories": {
    "connection": {
      "name": "Database Connection",
      "description": "Patterns for establishing and managing database connections",
      "patterns": ["basic_connection", "connection_pooling"]
    },
    "security": {
      "name": "Security Best Practices", 
      "description": "Secure coding patterns and practices",
      "patterns": ["parameterized_query", "authentication"]
    }
  },
  "learning_paths": {
    "beginner": {
      "name": "Getting Started Path",
      "description": "Essential patterns for new users",
      "patterns": ["basic_connection", "simple_query", "error_handling"],
      "estimated_total_time": "15 minutes"
    },
    "production": {
      "name": "Production Ready Path",
      "description": "Patterns for production deployment",
      "patterns": ["connection_pooling", "parameterized_query", "transaction_handling", "monitoring"],
      "estimated_total_time": "45 minutes"
    }
  }
}
```

### 4.3 migration-guide.json (Version-Dependent)

**Purpose**: Structured documentation of version changes and migration paths.

**Schema**:

```json
{
  "$schema": "https://miri-standard.org/schemas/migration-guide-v1.json",
  "from_version": "1.1.x",
  "to_version": "1.2.0",
  "migration_type": "minor",
  "generated_at": "2025-08-30T12:00:00Z",
  "summary": {
    "breaking_changes": 2,
    "new_features": 5,
    "deprecations": 3,
    "estimated_migration_time": "30 minutes"
  },
  "breaking_changes": [
    {
      "id": "method_rename_execute_to_query",
      "severity": "high",
      "component": "DatabaseClient",
      "change": "Method DatabaseClient.execute() renamed to query()",
      "reason": "Improved API consistency and clarity",
      "old_code": "result = client.execute('SELECT * FROM users')",
      "new_code": "result = client.query('SELECT * FROM users')",
      "migration_steps": [
        "Find all calls to client.execute()",
        "Replace with client.query()",
        "Update any error handling for new exception types"
      ],
      "automated_fix": {
        "find_pattern": r"\.execute\(",
        "replace_pattern": ".query(",
        "confidence": "high"
      },
      "affected_patterns": ["basic_connection", "parameterized_query"]
    }
  ],
  "new_features": [
    {
      "id": "async_support",
      "name": "Async/Await Support",
      "description": "Added async versions of all database operations",
      "example": "async with AsyncDatabaseClient(conn_str) as client:\n    result = await client.query('SELECT * FROM users')",
      "new_classes": ["AsyncDatabaseClient"],
      "new_methods": ["async_query", "async_connect"],
      "usage_patterns": ["async_connection", "async_transaction"]
    }
  ],
  "deprecations": [
    {
      "id": "legacy_connection_method",
      "deprecated": "DatabaseClient.legacy_connect()",
      "replacement": "DatabaseClient.connect()",
      "removal_version": "2.0.0",
      "migration": "Replace legacy_connect() calls with connect()"
    }
  ],
  "compatibility": {
    "python_versions": ["3.8+"],
    "dependencies": {
      "added": ["asyncpg>=0.25.0"],
      "updated": ["sqlalchemy>=1.4.0"],
      "removed": []
    }
  }
}
```

**Generation source for `deprecations`**: entries MUST be derived from the code's
[PEP 702](https://peps.python.org/pep-0702/) `@deprecated` markers at build time (see
[Lifecycle and Security Metadata §6](lifecycle-security-metadata.md)) — the decorators are the source of truth, the JSON
is the derived inventory.

### 4.4 prompt-templates.md (Optional)

**Purpose**: Agent-specific interaction guides and prompt templates.

```markdown
# Agent Prompt Templates

## Quick Start Prompts

### For Code Generation
```

Generate code using {package_name} to {task_description}.
Use the patterns from usage-patterns.json, specifically the "{pattern_id}" pattern.
Follow the API signatures from sdk-manifest.json.

```text

### For Debugging
```

Help debug this {package_name} code: {code_snippet}
Check against common errors in sdk-manifest.json error_handling section.
Suggest fixes based on usage patterns.

```text

### For Migration
```

Migrate this code from {package_name} v{old_version} to v{new_version}:
{code_snippet}

Use migration-guide.json for breaking changes and new features.

```text

## Agent-Specific Optimizations

### Cursor IDE Integration
- Prioritize usage-patterns.json for autocomplete suggestions
- Use sdk-manifest.json for parameter hints
- Reference migration-guide.json for version warnings

### Claude/ChatGPT Integration  
- Load full sdk-manifest.json as context
- Reference specific patterns by ID
- Use structured error handling guides

### GitHub Copilot Integration
- Embed usage patterns as comments
- Use API signatures for function completion
- Reference common imports for suggestions
```

### 4.5 api-graph.json (Optional)

**Purpose**: Relationship graph between API components for advanced agent reasoning.

**Schema**:

```json
{
  "$schema": "https://miri-standard.org/schemas/api-graph-v1.json",
  "version": "1.0",
  "nodes": {
    "DatabaseClient": {
      "type": "class",
      "centrality": 0.95,
      "dependencies": ["Connection", "QueryResult"],
      "dependents": ["QueryBuilder", "Transaction"]
    },
    "QueryBuilder": {
      "type": "class", 
      "centrality": 0.7,
      "dependencies": ["DatabaseClient"],
      "common_with": ["Transaction"]
    }
  },
  "edges": [
    {
      "from": "DatabaseClient",
      "to": "QueryResult", 
      "relationship": "returns",
      "methods": ["query", "execute"]
    },
    {
      "from": "QueryBuilder",
      "to": "DatabaseClient",
      "relationship": "uses",
      "pattern": "builder_with_client"
    }
  ],
  "workflows": [
    {
      "id": "standard_query_workflow",
      "steps": ["DatabaseClient", "connect", "query", "QueryResult"],
      "frequency": 0.85
    }
  ]
}
```

### 4.6 lifecycle.json (Required)

**Purpose**: Package identity (purl), authoritative advisory sources, update-check endpoint, and support status — so
agents and scanners can answer "is this package vulnerable?" and "is this package current?" at call time, for both open
source and private packages.

This file is fully specified in [Lifecycle and Security Metadata](lifecycle-security-metadata.md), including the open
source defaults (PyPI + public OSV), the private/internal package requirements (private purl namespaces, internal
OSV-schema advisory sources), and the relationship to PEP 770 SBOMs. Like all files in this directory, it MUST be
generated at build time.

## 5. Automated Generation

### 5.1 Build-Time Generation

**Integration with setup.py/pyproject.toml**:

```python
# build_metadata.py
import inspect
import json
import ast
from datetime import datetime
from pathlib import Path

class AgentMetadataGenerator:
    """Generate pre-parsed agent metadata from source code."""
    
    def __init__(self, package_name, version):
        self.package_name = package_name
        self.version = version
        self.metadata_dir = Path(f"src/{package_name}/agent-metadata")
        
    def generate_all(self):
        """Generate all agent metadata files."""
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Generate core files
        self.generate_sdk_manifest()
        self.generate_usage_patterns()
        self.generate_migration_guide()
        
        print(f"Generated agent metadata in {self.metadata_dir}")
    
    def generate_sdk_manifest(self):
        """Generate sdk-manifest.json from source code inspection."""
        manifest = {
            "sdk_version": self.version,
            "generated_at": datetime.now().isoformat(),
            "miri_version": "1.0",
            "quick_reference": self._extract_quick_reference(),
            "api_index": self._extract_api_index(),
            "error_handling": self._extract_error_handling(),
            "configuration": self._extract_configuration()
        }
        
        with open(self.metadata_dir / "sdk-manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
    
    def _extract_api_index(self):
        """Extract API signatures using AST parsing."""
        api_index = {}
        
        # Scan all Python files in package
        package_path = Path(f"src/{self.package_name}")
        for py_file in package_path.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
                
            tree = ast.parse(py_file.read_text())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node, py_file)
                    if class_info:
                        api_index[node.name] = class_info
        
        return api_index
    
    def _analyze_class(self, class_node, file_path):
        """Analyze a class AST node to extract metadata."""
        docstring = ast.get_docstring(class_node)
        
        methods = {}
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                method_info = self._analyze_method(node)
                if method_info:
                    methods[node.name] = method_info
        
        return {
            "type": "class",
            "purpose": self._extract_purpose_from_docstring(docstring),
            "complexity": self._infer_complexity(class_node, methods),
            "key_methods": methods,
            "file": str(file_path.relative_to(Path("src")))
        }
    
    def generate_usage_patterns(self):
        """Extract usage patterns from tests and examples."""
        patterns = []
        
        # Scan test files for patterns
        test_patterns = self._extract_patterns_from_tests()
        patterns.extend(test_patterns)
        
        # Scan example files for patterns  
        example_patterns = self._extract_patterns_from_examples()
        patterns.extend(example_patterns)
        
        usage_data = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "patterns": patterns,
            "categories": self._categorize_patterns(patterns),
            "learning_paths": self._generate_learning_paths(patterns)
        }
        
        with open(self.metadata_dir / "usage-patterns.json", "w") as f:
            json.dump(usage_data, f, indent=2)
```

### 5.2 Pre-commit Hook Integration

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Generating agent metadata..."
python scripts/generate_agent_metadata.py

# Add generated files to commit
git add src/*/agent-metadata/

echo "Agent metadata updated and staged"
```

### 5.3 CI/CD Integration

```yaml
# .github/workflows/build.yml
name: Build with Agent Metadata

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Generate Agent Metadata
      run: |
        python scripts/generate_agent_metadata.py
        
    - name: Validate Metadata
      run: |
        python scripts/validate_agent_metadata.py
        
    - name: Build Package
      run: |
        python -m build
        
    - name: Verify Metadata in Wheel
      run: |
        python scripts/verify_wheel_metadata.py dist/*.whl
```

## 6. Integration Patterns

### 6.1 Agent Detection and Loading

```python
# Agent integration utility
import json
import importlib.resources
from pathlib import Path
from typing import Dict, Optional

class AgentMetadataLoader:
    """Load and cache pre-parsed agent metadata."""
    
    def __init__(self, package_name: str):
        self.package_name = package_name
        self._cache = {}
    
    def load_sdk_manifest(self) -> Optional[Dict]:
        """Load SDK manifest with caching."""
        if "manifest" not in self._cache:
            try:
                # Try to load from installed package
                with importlib.resources.files(f"{self.package_name}.agent-metadata") as metadata_dir:
                    manifest_file = metadata_dir / "sdk-manifest.json"
                    if manifest_file.exists():
                        self._cache["manifest"] = json.loads(manifest_file.read_text())
                    else:
                        return None
            except (ImportError, FileNotFoundError):
                return None
        
        return self._cache.get("manifest")
    
    def load_usage_patterns(self) -> Optional[Dict]:
        """Load usage patterns with caching."""
        if "patterns" not in self._cache:
            try:
                with importlib.resources.files(f"{self.package_name}.agent-metadata") as metadata_dir:
                    patterns_file = metadata_dir / "usage-patterns.json"
                    if patterns_file.exists():
                        self._cache["patterns"] = json.loads(patterns_file.read_text())
                    else:
                        return None
            except (ImportError, FileNotFoundError):
                return None
        
        return self._cache.get("patterns")
    
    def get_quick_reference(self) -> Optional[Dict]:
        """Get quick reference for immediate agent consumption."""
        manifest = self.load_sdk_manifest()
        if manifest:
            return manifest.get("quick_reference")
        return None
    
    def get_pattern_by_id(self, pattern_id: str) -> Optional[Dict]:
        """Get specific usage pattern by ID."""
        patterns = self.load_usage_patterns()
        if patterns:
            for pattern in patterns.get("patterns", []):
                if pattern.get("id") == pattern_id:
                    return pattern
        return None
    
    def get_api_signature(self, class_name: str, method_name: str = None) -> Optional[Dict]:
        """Get API signature for class or method."""
        manifest = self.load_sdk_manifest()
        if manifest and "api_index" in manifest:
            class_info = manifest["api_index"].get(class_name)
            if class_info and method_name:
                return class_info.get("key_methods", {}).get(method_name)
            return class_info
        return None

# Usage in agent integration
def integrate_with_cursor():
    """Example Cursor IDE integration."""
    loader = AgentMetadataLoader("your_sdk")
    
    # Get quick reference for autocomplete
    quick_ref = loader.get_quick_reference()
    if quick_ref:
        print("Available classes:", quick_ref.get("primary_classes"))
        print("Common imports:", quick_ref.get("common_imports"))
    
    # Get specific pattern for code generation
    pattern = loader.get_pattern_by_id("basic_connection")
    if pattern:
        print("Pattern code:", pattern.get("code"))
        print("Explanation:", pattern.get("explanation"))
```

### 6.2 .cursorrules Integration

```text
# .cursorrules for projects using Miri-compliant packages

## Agent Metadata Integration
- Always check for agent-metadata/ directory in installed packages
- Prioritize sdk-manifest.json for API signatures and quick reference
- Use usage-patterns.json for code suggestions and examples
- Reference migration-guide.json when updating package versions
- Prefer structured metadata over parsing raw documentation

## Code Generation Rules
- Use quick_reference.common_imports for import statements
- Reference api_index for parameter types and method signatures
- Apply usage patterns based on complexity level and tags
- Include error handling based on common_errors in manifest

## Performance Optimization
- Cache loaded metadata for session duration
- Use pattern IDs for consistent code suggestions
- Leverage API graph for relationship-aware completions
```

## 7. Performance Optimization

### 7.1 Lazy Loading Strategy

```python
class LazyAgentMetadata:
    """Lazy-loading agent metadata with performance optimization."""
    
    def __init__(self, package_name: str):
        self.package_name = package_name
        self._manifest = None
        self._patterns = None
        self._migration_guide = None
    
    @property
    def manifest(self) -> Dict:
        """Lazy load SDK manifest."""
        if self._manifest is None:
            self._manifest = self._load_file("sdk-manifest.json")
        return self._manifest
    
    @property  
    def patterns(self) -> Dict:
        """Lazy load usage patterns."""
        if self._patterns is None:
            self._patterns = self._load_file("usage-patterns.json")
        return self._patterns
    
    def _load_file(self, filename: str) -> Dict:
        """Load and cache metadata file."""
        try:
            with importlib.resources.files(f"{self.package_name}.agent-metadata") as metadata_dir:
                file_path = metadata_dir / filename
                if file_path.exists():
                    return json.loads(file_path.read_text())
        except Exception:
            pass
        return {}
```

### 7.2 Memory Optimization

- **Selective Loading**: Load only required metadata sections
- **Compression**: Use compressed JSON for large metadata files
- **Indexing**: Create indexes for fast pattern and API lookup
- **Caching**: Implement LRU cache for frequently accessed data

### 7.3 Performance Metrics

Track agent performance improvements:

```python
class AgentPerformanceTracker:
    """Track performance improvements from pre-parsed metadata."""
    
    def __init__(self):
        self.metrics = {
            "metadata_load_time": [],
            "pattern_lookup_time": [],
            "api_discovery_time": [],
            "cache_hit_rate": 0.0
        }
    
    def measure_load_time(self, operation: str):
        """Decorator to measure operation time."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                self.metrics[f"{operation}_time"].append(end_time - start_time)
                return result
            return wrapper
        return decorator
```

## 8. Implementation Requirements

### 8.1 Required Files

**Minimum Compliance**:

- `agent-metadata/sdk-manifest.json` - Core API index
- `agent-metadata/usage-patterns.json` - Basic usage patterns
- `agent-metadata/lifecycle.json` - Identity and advisory sources ([specification](lifecycle-security-metadata.md))

**Full Compliance**:

- All metadata files present and valid
- Automated generation integrated into build process
- Performance optimization implemented
- Agent integration utilities provided

### 8.2 Validation Requirements

```python
def validate_agent_metadata(package_path: Path) -> List[str]:
    """Validate agent metadata structure and content."""
    errors = []
    
    metadata_dir = package_path / "agent-metadata"
    if not metadata_dir.exists():
        errors.append("Missing agent-metadata directory")
        return errors
    
    # Validate required files
    required_files = ["sdk-manifest.json", "usage-patterns.json", "lifecycle.json"]
    for filename in required_files:
        file_path = metadata_dir / filename
        if not file_path.exists():
            errors.append(f"Missing required file: {filename}")
        else:
            # Validate JSON structure
            try:
                data = json.loads(file_path.read_text())
                errors.extend(validate_file_schema(filename, data))
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in {filename}: {e}")
    
    return errors

def validate_file_schema(filename: str, data: Dict) -> List[str]:
    """Validate specific file schema."""
    errors = []
    
    if filename == "sdk-manifest.json":
        required_fields = ["sdk_version", "generated_at", "api_index"]
        for field in required_fields:
            if field not in data:
                errors.append(f"sdk-manifest.json missing required field: {field}")
    
    elif filename == "lifecycle.json":
        required_fields = ["identity", "advisory_sources", "update_check", "support"]
        for field in required_fields:
            if field not in data:
                errors.append(f"lifecycle.json missing required field: {field}")

    elif filename == "usage-patterns.json":
        if "patterns" not in data:
            errors.append("usage-patterns.json missing 'patterns' field")
        else:
            for i, pattern in enumerate(data["patterns"]):
                if "id" not in pattern:
                    errors.append(f"Pattern {i} missing required 'id' field")
                if "code" not in pattern:
                    errors.append(f"Pattern {i} missing required 'code' field")
    
    return errors
```

### 8.3 Build Integration

```toml
# pyproject.toml
[tool.miri.agent-metadata]
enabled = true
auto_generate = true
include_patterns = ["tests/", "examples/"]
exclude_patterns = ["tests/conftest.py"]
performance_optimization = true

[build-system]
requires = ["setuptools>=61.0", "wheel", "miri-build-tools"]
build-backend = "miri_build_tools.build_meta"
```

---

This specification provides a foundation for reducing agent re-parsing while maintaining full compatibility with the
existing Miri Standard. Whether the pre-parsed metadata approach improves agent performance in practice is a
hypothesis to be validated by measurement; its concrete, testable advantages are that the metadata is bundled
(available offline) and version-locked to the code it describes.
