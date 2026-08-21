#!/usr/bin/env python3
"""
Quickstart

Basic usage of the Weather SDK: create a client and fetch the current weather.

Complexity: beginner
Tags: quickstart, client, weather
Estimated time: 2 minutes
"""
import os

from weather_sdk import WeatherClient


def main() -> None:
    # Documented placeholder credential; the example is skipped when it is absent
    # so it stays runnable in a sandbox without network access (MIRI-PY-015).
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        print("Set WEATHER_API_KEY to run this example against the live service.")
        return

    with WeatherClient(api_key=api_key) as client:
        weather = client.get_current_weather("San Francisco, CA")
        print(f"Current temperature: {weather.temperature}")


if __name__ == "__main__":
    main()
