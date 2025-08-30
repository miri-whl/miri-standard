"""
Weather SDK Data Models

Data classes for weather information with clear structure for agent consumption.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Dict, Any


@dataclass
class Location:
    """
    Geographic location information.
    
    Attributes:
        name: Full location name (e.g., "New York, NY, USA")
        city: City name
        state: State/province (optional)
        country: Country name
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    """
    name: str
    city: str
    state: Optional[str]
    country: str
    latitude: float
    longitude: float
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Location':
        """Create Location from API response data."""
        return cls(
            name=data["name"],
            city=data["city"],
            state=data.get("state"),
            country=data["country"],
            latitude=float(data["lat"]),
            longitude=float(data["lon"])
        )


@dataclass
class WeatherData:
    """
    Current weather conditions for a location.
    
    Attributes:
        location: Location information
        temperature: Current temperature in Fahrenheit
        feels_like: "Feels like" temperature in Fahrenheit
        humidity: Humidity percentage (0-100)
        pressure: Atmospheric pressure in hPa
        visibility: Visibility in miles
        uv_index: UV index (0-11+)
        description: Weather description (e.g., "Partly cloudy")
        wind_speed: Wind speed in mph
        wind_direction: Wind direction in degrees (0-360)
        timestamp: When the data was recorded
    """
    location: Location
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    visibility: float
    uv_index: float
    description: str
    wind_speed: float
    wind_direction: int
    timestamp: datetime
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'WeatherData':
        """Create WeatherData from API response."""
        return cls(
            location=Location.from_api_response(data["location"]),
            temperature=float(data["temperature"]),
            feels_like=float(data["feels_like"]),
            humidity=int(data["humidity"]),
            pressure=float(data["pressure"]),
            visibility=float(data["visibility"]),
            uv_index=float(data["uv_index"]),
            description=data["description"],
            wind_speed=float(data["wind_speed"]),
            wind_direction=int(data["wind_direction"]),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


@dataclass
class DailyForecast:
    """
    Weather forecast for a single day.
    
    Attributes:
        date: Forecast date
        high_temp: High temperature in Fahrenheit
        low_temp: Low temperature in Fahrenheit
        description: Weather description
        precipitation_chance: Chance of precipitation (0-100)
        precipitation_amount: Expected precipitation in inches
        humidity: Average humidity percentage
        wind_speed: Average wind speed in mph
        wind_direction: Wind direction in degrees
        uv_index: UV index forecast
    """
    date: date
    high_temp: float
    low_temp: float
    description: str
    precipitation_chance: int
    precipitation_amount: float
    humidity: int
    wind_speed: float
    wind_direction: int
    uv_index: float
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'DailyForecast':
        """Create DailyForecast from API response."""
        return cls(
            date=datetime.fromisoformat(data["date"]).date(),
            high_temp=float(data["high_temp"]),
            low_temp=float(data["low_temp"]),
            description=data["description"],
            precipitation_chance=int(data["precipitation_chance"]),
            precipitation_amount=float(data["precipitation_amount"]),
            humidity=int(data["humidity"]),
            wind_speed=float(data["wind_speed"]),
            wind_direction=int(data["wind_direction"]),
            uv_index=float(data["uv_index"])
        )


@dataclass
class ForecastData:
    """
    Multi-day weather forecast for a location.
    
    Attributes:
        location: Location information
        days: List of daily forecasts
        generated_at: When the forecast was generated
    """
    location: Location
    days: List[DailyForecast]
    generated_at: datetime
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'ForecastData':
        """Create ForecastData from API response."""
        return cls(
            location=Location.from_api_response(data["location"]),
            days=[DailyForecast.from_api_response(day) for day in data["forecast"]],
            generated_at=datetime.fromisoformat(data["generated_at"])
        )
