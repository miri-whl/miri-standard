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
- **[test-patterns-v1.json](test-patterns-v1.json)** - Schema for `test-patterns.json` - unit and integration test
  patterns extracted from the package's own suite, plus the test doubles it ships
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

- **[check-v2.json](check-v2.json)** - Schema for the per-check check definitions in `standards/<target>/checks/`
  - **Current.** Requires each definition to declare `$schema` pointing at this file, which is what makes a
    semantics change loud: a v2 definition carries a key v1's closed `additionalProperties` rejects, and a v1
    definition omits a key v2 requires, so a mismatched corpus-and-schema pairing fails in both directions
- **[check-v1.json](check-v1.json)** - **Superseded at 0.5.0, retained frozen.** Describes pre-0.5.0 scoring
  semantics, under which `conditional: true` meant a check scored its full weight automatically when its condition
  did not apply. That reading was replaced by exclusion from both numerator and denominator — a change of *meaning*
  with no change of *shape*, which is precisely why it needed a new schema rather than an edited one. A consumer
  pinned here is old, not wrong, and stays internally consistent. Do not add fields
  - Canonical check metadata: level, weight, severity, violation unit, example, fix, references
  - The severity vocabulary (LOW/MINOR/MEDIUM/HIGH/CRITICAL, 1-5) is normative for health scoring

- **[lifecycle-v1.json](lifecycle-v1.json)** - Schema for `lifecycle.json`
  - Package identity (purl), advisory sources, update check, and support status
  - Required fields: `miri_lifecycle_version`, `generated_at`, `identity`, `advisory_sources`, `update_check`, `support`
  - Validates open source and private distribution declarations; see [Lifecycle and Security Metadata](../standards/python/lifecycle-security-metadata.md)

### CLI Schemas

- **[cli-describe-v1.json](cli-describe-v1.json)** - Schema for a CLI's `--describe` introspection document
  - Required fields: `schema_version`, `identity`, `support`, `advisory_sources`, `commands`
  - Closes `additionalProperties` at the root, and defines the per-surface `lifecycle` block that carries
    `deprecated_since` / `removed_in` / `replacement`
  - See [CLI Lifecycle Specification](../standards/cli/cli-lifecycle-specification.md) and the executable
    [`greetctl` fixtures](../examples/fixtures/cli/README.md)

### Consumption and Integration Schemas

- **[discovery-envelope-v1.json](discovery-envelope-v1.json)** - The surface-owned response envelope
  - Publisher bytes nest under a payload key, so `ok` and `present` cannot be forged
  - The root is deliberately **open**, so a new operation or channel may add a payload key without a schema
    change forbidding it
  - Round-tripped in both directions by `tools/validate_envelope_schema.py` (`make envelope`)

- **[agent-event-v1.json](agent-event-v1.json)** - The event a host sends a trigger
  - Required fields: `schema_version`, `kind`, `phase`, `subject`
  - Closes `additionalProperties` — the **opposite** of the envelope's open root — so a host cannot smuggle a
    file path or a diff into an event. `kind` is a closed set of six.
  - `subject.package_kind` distinguishes `import` from `distribution` names; an import-only shape rejects
    `python-dateutil`, `ruamel.yaml` and the project's own `greet-adversarial`

- **[agent-findings-v1.json](agent-findings-v1.json)** - The response a trigger returns
  - The envelope with one payload key, `findings`; not a new response format
  - Enforces the payload/absence coupling normatively: `present: true` requires `findings`, `present: false`
    forbids it and requires a `reason`, and an empty `findings` array is rejected because silence is the absent
    shape rather than an empty payload
  - `findings[].task` is closed to the six Consumption Map sections; `findings[].level` is closed to
    `must`/`should` — the conformance vocabulary, **not** the check-severity one — so a publisher's
    `priority: "critical"` cannot reach it even by accident
  - Exercised by the `E*` event-trace goldens in [`examples/fixtures/expected/`](../examples/fixtures/expected/)

### Reporting Schemas

- **[scoring-v1.json](scoring-v1.json)** - Conformance score reports
- **[lint-report-v1.json](lint-report-v1.json)** - Linter output. As of 0.5.0 a report MUST carry
  `scores.effective_denominator`, `scores.excluded`, `scores.forfeited` and `must_failures` beside a conformance
  score, because the number alone is not interpretable once checks leave the ratio
  - `must_failures` non-empty forces `grade: non-conforming` and caps `conformance` at 74. That coupling is what a
    `scoring: gate` check depends on entirely: a gate carries weight 0, so a failing one leaves no arithmetic trace
    and this field is its only representation
  - `checks_commit_sha` is a full 40-character sha, never a tag — a tag is movable and a published score must point
    at definitions that are not. The release name goes in `standard_version`
  - A `skipped` outcome MUST name its `skip_reason` from the closed set

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

### Recording Check-Definition Revisions

`added_in` records when a check was introduced and `withdrawn_in` when it was retired. Nothing records
**revision**: reading one of the 119 definitions does not tell you whether its meaning changed in the current
release. The governance decision is that this stays **editorial** — git history is the revision record, not a
field.

The reason is the failure mode of the alternative. A hand-maintained `changed_in` has to be updated on every
edit, so every missed update is a definition silently claiming it did not change in a release where it did.
0.5.0 rejected `semantics_version` on exactly these grounds: a single global fact copied into 119 files becomes
119 statements that can each be wrong, while the fact has one true value. A revision marker has the same shape.

Git holds the answer exactly, and `checks_commit_sha` makes it addressable — a lint report names the commit its
definitions were read from, so "what changed between these two reports" is a diff rather than a claim:

```bash
git diff --stat <old-sha>..<new-sha> -- 'standards/*/checks/*.yaml'
```

Should a future release need revision history carried *inside* the definitions — for a consumer that vendors the
YAML without the repository — the field to add is one that cannot go stale by omission, such as a content hash
computed and verified in CI, rather than a version marker a human has to remember.

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
