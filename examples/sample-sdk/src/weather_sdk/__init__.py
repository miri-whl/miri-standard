"""
Weather SDK - Miri Standard Example

This SDK demonstrates the Miri Standard for agent-friendly Python packages.
It includes everything autonomous agents need:
- Pre-parsed metadata in agent-metadata/
- Working examples in weather_sdk.examples
- Documentation in weather_sdk.docs  
- Code templates in weather_sdk.templates
- Discovery helpers for runtime access

Quick Start:
    >>> from weather_sdk import WeatherClient
    >>> client = WeatherClient(api_key="your-key")
    >>> weather = client.get_current_weather("New York, NY")
    >>> print(f"Temperature: {weather.temperature}°F")
    
For Autonomous Agents:
    >>> import weather_sdk
    >>> weather_sdk.show_quickstart()  # Get immediate usage guide
    >>> weather_sdk.list_examples()    # List all examples
    >>> weather_sdk.get_agent_metadata()  # Get structured metadata
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import importlib.resources

# Main SDK exports
from .client import WeatherClient
from .exceptions import WeatherError, AuthenticationError, APIError
from .models import WeatherData, ForecastData, Location

__version__ = "1.2.0"
__all__ = ["WeatherClient", "WeatherError", "AuthenticationError", "APIError", 
           "WeatherData", "ForecastData", "Location"]

def get_examples_dir() -> Path:
    """Get path to installed examples directory."""
    return Path(__file__).parent / "examples"

def get_docs_dir() -> Path:
    """Get path to installed documentation."""
    return Path(__file__).parent / "docs"

def get_templates_dir() -> Path:
    """Get path to code templates."""
    return Path(__file__).parent / "templates"

def get_agent_metadata_dir() -> Path:
    """Get path to agent metadata directory."""
    return Path(__file__).parent / "agent-metadata"

def get_agent_metadata() -> Dict:
    """
    Get agent-specific metadata from package.
    
    Returns structured information about examples, usage patterns,
    and learning resources for autonomous agents.
    """
    try:
        # Try to load from agent-metadata directory
        metadata_dir = get_agent_metadata_dir()
        manifest_file = metadata_dir / "sdk-manifest.json"
        
        if manifest_file.exists():
            return json.loads(manifest_file.read_text())
    except Exception:
        pass
    
    # Fallback to basic structure
    return {
        "version": "1.0",
        "sdk_version": __version__,
        "quick_reference": {
            "primary_classes": ["WeatherClient"],
            "key_methods": ["get_current_weather", "get_forecast"],
            "common_imports": ["from weather_sdk import WeatherClient"]
        },
        "examples": {
            "quickstart": {
                "file": "examples/quickstart.py",
                "description": "Basic weather data retrieval"
            }
        }
    }

def get_usage_patterns() -> Dict:
    """Get pre-extracted usage patterns."""
    try:
        metadata_dir = get_agent_metadata_dir()
        patterns_file = metadata_dir / "usage-patterns.json"
        
        if patterns_file.exists():
            return json.loads(patterns_file.read_text())
    except Exception:
        pass
    
    return {"version": "1.0", "patterns": []}

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
from weather_sdk import WeatherClient

# Initialize client
client = WeatherClient(api_key="your-api-key")

# Get current weather
weather = client.get_current_weather("New York, NY")
print(f"Temperature: {weather.temperature}°F")
print(f"Conditions: {weather.description}")

# Get 5-day forecast
forecast = client.get_forecast("New York, NY", days=5)
for day in forecast.days:
    print(f"{day.date}: {day.high_temp}°F / {day.low_temp}°F - {day.description}")
'''

def get_migration_guide() -> Optional[Dict]:
    """Get migration guide for version changes."""
    try:
        metadata_dir = get_agent_metadata_dir()
        migration_file = metadata_dir / "migration-guide.json"
        
        if migration_file.exists():
            return json.loads(migration_file.read_text())
    except Exception:
        pass
    
    return None

def validate_agent_metadata() -> List[str]:
    """Validate agent metadata files against schemas."""
    errors = []
    metadata_dir = get_agent_metadata_dir()
    
    if not metadata_dir.exists():
        errors.append("Missing agent-metadata directory")
        return errors
    
    # Check required files
    required_files = ["sdk-manifest.json", "usage-patterns.json"]
    for filename in required_files:
        file_path = metadata_dir / filename
        if not file_path.exists():
            errors.append(f"Missing required file: {filename}")
        else:
            try:
                json.loads(file_path.read_text())
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in {filename}: {e}")
    
    return errors
