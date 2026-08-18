# Miri Standard JSON Schemas

This directory contains JSON Schema definitions for validating Miri Standard metadata files. These schemas ensure
consistency and enable automated validation of agent metadata.

## Available Schemas

### Core Metadata Schemas

- **[sdk-manifest-v1.json](sdk-manifest-v1.json)** - Schema for `sdk-manifest.json`
  - Core API index with structured signatures and metadata
  - Required fields: `sdk_version`, `generated_at`, `miri_version`, `quick_reference`, `api_index`
  - Validates API components, methods, parameters, and error handling

- **[usage-patterns-v1.json](usage-patterns-v1.json)** - Schema for `usage-patterns.json`
  - Pre-extracted, categorized code patterns
  - Required fields: `version`, `generated_at`, `patterns`
  - Validates pattern structure, categories, and learning paths

- **[migration-guide-v1.json](migration-guide-v1.json)** - Schema for `migration-guide.json`
  - Structured version change documentation
  - Required fields: `from_version`, `to_version`, `migration_type`, `generated_at`, `summary`
  - Validates breaking changes, new features, and deprecations

- **[api-graph-v1.json](api-graph-v1.json)** - Schema for `api-graph.json`
  - API relationship mapping for advanced agent reasoning
  - Required fields: `version`, `nodes`, `edges`
  - Validates graph structure and workflow definitions

- **[lifecycle-v1.json](lifecycle-v1.json)** - Schema for `lifecycle.json`
  - Package identity (purl), advisory sources, update check, and support status
  - Required fields: `miri_lifecycle_version`, `generated_at`, `identity`, `advisory_sources`, `update_check`, `support`
  - Validates open source and private distribution declarations; see [Lifecycle and Security Metadata](../standards/python/lifecycle-security-metadata.md)

## Usage

### Validation with Python

```python
import json
import jsonschema
from pathlib import Path

def validate_agent_metadata(metadata_file: Path, schema_file: Path) -> List[str]:
    """Validate metadata file against JSON schema."""
    errors = []
    
    try:
        # Load schema and metadata
        schema = json.loads(schema_file.read_text())
        metadata = json.loads(metadata_file.read_text())
        
        # Validate
        jsonschema.validate(metadata, schema)
        return []  # No errors
        
    except jsonschema.ValidationError as e:
        errors.append(f"Validation error: {e.message}")
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
    
    return errors

# Example usage
schema_dir = Path("schemas")
metadata_dir = Path("src/my_package/agent-metadata")

# Validate SDK manifest
errors = validate_agent_metadata(
    metadata_dir / "sdk-manifest.json",
    schema_dir / "sdk-manifest-v1.json"
)

if errors:
    print("Validation errors:", errors)
else:
    print("✓ SDK manifest is valid")
```

### Validation with CLI Tools

Using `jsonschema` CLI:

```bash
# Install jsonschema
pip install jsonschema

# Validate files
jsonschema -i examples/sample-sdk/src/weather_sdk/agent-metadata/sdk-manifest.json schemas/sdk-manifest-v1.json
jsonschema -i examples/sample-sdk/src/weather_sdk/agent-metadata/usage-patterns.json schemas/usage-patterns-v1.json
```

### IDE Integration

Most modern IDEs support JSON Schema validation:

#### VS Code

Add to your workspace settings:

```json
{
  "json.schemas": [
    {
      "fileMatch": ["**/agent-metadata/sdk-manifest.json"],
      "url": "./schemas/sdk-manifest-v1.json"
    },
    {
      "fileMatch": ["**/agent-metadata/usage-patterns.json"], 
      "url": "./schemas/usage-patterns-v1.json"
    },
    {
      "fileMatch": ["**/agent-metadata/migration-guide.json"],
      "url": "./schemas/migration-guide-v1.json"
    },
    {
      "fileMatch": ["**/agent-metadata/api-graph.json"],
      "url": "./schemas/api-graph-v1.json"
    }
  ]
}
```

#### JetBrains IDEs (PyCharm, IntelliJ)

1. Go to Settings → Languages & Frameworks → Schemas and DTDs → JSON Schema Mappings
2. Add mappings for each schema file and corresponding file patterns

## Schema Validation in Build Process

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Validating Miri metadata schemas..."

# Find all agent-metadata directories
for metadata_dir in $(find . -name "agent-metadata" -type d); do
    echo "Validating $metadata_dir"
    
    # Validate each metadata file
    if [ -f "$metadata_dir/sdk-manifest.json" ]; then
        jsonschema -i "$metadata_dir/sdk-manifest.json" schemas/sdk-manifest-v1.json || exit 1
    fi
    
    if [ -f "$metadata_dir/usage-patterns.json" ]; then
        jsonschema -i "$metadata_dir/usage-patterns.json" schemas/usage-patterns-v1.json || exit 1
    fi
    
    if [ -f "$metadata_dir/migration-guide.json" ]; then
        jsonschema -i "$metadata_dir/migration-guide.json" schemas/migration-guide-v1.json || exit 1
    fi
    
    if [ -f "$metadata_dir/api-graph.json" ]; then
        jsonschema -i "$metadata_dir/api-graph.json" schemas/api-graph-v1.json || exit 1
    fi
done

echo "✓ All metadata files are valid"
```

### GitHub Actions

```yaml
name: Validate Miri Metadata

on: [push, pull_request]

jobs:
  validate-metadata:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install jsonschema
    
    - name: Validate metadata schemas
      run: |
        find . -name "agent-metadata" -type d | while read metadata_dir; do
          echo "Validating $metadata_dir"
          
          if [ -f "$metadata_dir/sdk-manifest.json" ]; then
            jsonschema -i "$metadata_dir/sdk-manifest.json" schemas/sdk-manifest-v1.json
          fi
          
          if [ -f "$metadata_dir/usage-patterns.json" ]; then
            jsonschema -i "$metadata_dir/usage-patterns.json" schemas/usage-patterns-v1.json
          fi
          
          if [ -f "$metadata_dir/migration-guide.json" ]; then
            jsonschema -i "$metadata_dir/migration-guide.json" schemas/migration-guide-v1.json
          fi
          
          if [ -f "$metadata_dir/api-graph.json" ]; then
            jsonschema -i "$metadata_dir/api-graph.json" schemas/api-graph-v1.json
          fi
        done
```

## Schema Evolution

### Versioning Strategy

- **Major version** (v2.0): Breaking changes to required fields or structure
- **Minor version** (v1.1): New optional fields or relaxed constraints  
- **Patch version** (v1.0.1): Bug fixes or clarifications

### Backward Compatibility

- New schemas maintain compatibility with previous versions when possible
- Deprecated fields are marked but not removed until next major version
- Migration guides provided for breaking changes

## Contributing

When updating schemas:

1. **Test thoroughly** with existing metadata files
2. **Update examples** to match schema changes
3. **Document changes** in schema descriptions
4. **Provide migration guidance** for breaking changes
5. **Validate against sample SDK** before committing

## Resources

- [JSON Schema Specification](https://json-schema.org/)
- [JSON Schema Validator](https://www.jsonschemavalidator.net/)
- [Sample Weather SDK](../examples/sample-sdk/) - Complete example with all metadata files
