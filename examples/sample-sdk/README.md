# Sample Weather SDK - Miri Standard Example

This is a complete example of a Python SDK that implements the Miri Standard for agent-friendly packaging. It demonstrates all the key features:

- **Agent Metadata**: Pre-parsed JSON files for instant agent consumption
- **Structured Examples**: Categorized code samples with complexity levels
- **Discovery APIs**: Runtime functions for accessing metadata
- **Rich Documentation**: Embedded docs and templates

## Project Structure

```
weather-sdk/
├── src/weather_sdk/
│   ├── __init__.py              # Main module with discovery APIs
│   ├── client.py                # WeatherClient class
│   ├── exceptions.py            # Custom exceptions
│   ├── models.py                # Data models
│   ├── agent-metadata/          # Pre-parsed agent data
│   │   ├── sdk-manifest.json    # Core API index
│   │   ├── usage-patterns.json  # Code patterns
│   │   ├── migration-guide.json # Version changes
│   │   └── api-graph.json      # API relationships
│   ├── examples/                # Code examples
│   │   ├── quickstart.py        # Basic usage
│   │   ├── authentication.py    # Auth patterns
│   │   └── use_cases/          # Real-world scenarios
│   ├── docs/                   # Embedded documentation
│   └── templates/              # Code templates
├── pyproject.toml              # Build configuration
├── tests/                      # Test suite
└── scripts/                    # Build and validation scripts
```

## Installation

```bash
pip install weather-sdk
```

## Quick Start

```python
from weather_sdk import WeatherClient

# Initialize client
client = WeatherClient(api_key="your-api-key")

# Get current weather
weather = client.get_current_weather("New York, NY")
print(f"Temperature: {weather.temperature}°F")

# Get forecast
forecast = client.get_forecast("New York, NY", days=5)
for day in forecast.days:
    print(f"{day.date}: {day.high_temp}°F / {day.low_temp}°F")
```

## For Autonomous Agents

This SDK is optimized for autonomous agents:

```python
import weather_sdk

# Get immediate API overview
metadata = weather_sdk.get_agent_metadata()
print("Available classes:", metadata["quick_reference"]["primary_classes"])

# Access usage patterns
patterns = weather_sdk.get_usage_patterns()
basic_pattern = patterns["patterns"][0]
print("Basic usage code:", basic_pattern["code"])

# List all examples
examples = weather_sdk.list_examples()
print("Available examples:", examples)
```

## Features Demonstrated

- ✅ **Pre-parsed Metadata**: JSON files eliminate agent re-parsing
- ✅ **Structured Examples**: Organized by complexity and use case
- ✅ **Discovery APIs**: Runtime access to all metadata
- ✅ **Rich Documentation**: Embedded guides and references
- ✅ **Code Templates**: Boilerplate for common patterns
- ✅ **Migration Guides**: Structured version change documentation
- ✅ **JSON Schema Validation**: All metadata files validated against schemas
