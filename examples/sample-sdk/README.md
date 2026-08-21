# Sample Weather SDK — Miri Standard Example

A small but **buildable, Miri-conforming** Python SDK. It ships pre-parsed agent metadata inside the wheel, declares
its identity and advisory sources, and exposes runtime discovery APIs — a worked example of the standard, not a
production package.

## Project Structure

```text
sample-sdk/
├── pyproject.toml               # Build configuration (setuptools, src layout)
├── README.md
└── src/weather_sdk/
    ├── __init__.py              # Main module with discovery APIs
    ├── client.py                # WeatherClient class
    ├── exceptions.py            # Custom exceptions
    ├── models.py                # Data models
    ├── agent-metadata/          # Pre-parsed agent data (packaged into the wheel)
    │   ├── sdk-manifest.json    # Core API index
    │   ├── usage-patterns.json  # Code patterns
    │   ├── migration-guide.json # Version changes (1.1.0 → 1.2.0)
    │   └── lifecycle.json       # Identity, advisory sources, support status
    └── examples/                # Embedded, runnable examples
        ├── __init__.py
        └── quickstart.py        # Basic usage
```

## Building and Conformance

```bash
python -m build --wheel        # produces weather_sdk-1.2.0-py3-none-any.whl
```

The build packages `agent-metadata/` and `examples/` into the wheel (declared under
`[tool.setuptools.package-data]`), so an agent finds them after `pip install`. All four `agent-metadata/` files validate
against the schemas in [`schemas/`](../../schemas/), and the version is coherent across the wheel, `sdk-manifest.json`,
`lifecycle.json`, and `migration-guide.json` (all `1.2.0`).

This example targets **Miri Core** conformance — the identity, lifecycle, and packaging layer defined in the
[Linter Checklist](../../standards/python/linter-checklist.md). Score it with the reference linter (`miri-py`, once
published); `make validate-sample` from the repo root checks its metadata against the schemas in the meantime.

## Quick Start

```python
from weather_sdk import WeatherClient

with WeatherClient(api_key="your-api-key") as client:
    weather = client.get_current_weather("New York, NY")
    print(f"Temperature: {weather.temperature}")
```

## For Autonomous Agents

The metadata travels with the installed wheel and is reachable through discovery functions:

```python
import weather_sdk

weather_sdk.get_agent_metadata()   # structured API metadata from sdk-manifest.json
weather_sdk.get_usage_patterns()   # categorized code patterns
weather_sdk.list_examples()        # ["quickstart"]
```

## What It Demonstrates

- ✅ **Buildable**: a real `pyproject.toml`; the wheel packages the metadata and examples
- ✅ **Pre-parsed metadata**: `agent-metadata/` JSON files an agent reads without re-deriving from source
- ✅ **Identity & lifecycle**: `lifecycle.json` with purl, advisory sources, and support status
- ✅ **Version coherence**: one version (`1.2.0`) across the wheel and every metadata file
- ✅ **Discovery APIs**: runtime access to the packaged metadata
- ✅ **Schema-valid**: every metadata file validates against its published JSON Schema
