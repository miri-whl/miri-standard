"""
Weather API Client

Main client class for interacting with weather services.
Demonstrates Miri Standard patterns for agent-friendly APIs.
"""

import requests
from typing import Optional, List
from .models import WeatherData, ForecastData, Location
from .exceptions import WeatherError, AuthenticationError, APIError


class WeatherClient:
    """
    Main weather API client for retrieving weather data and forecasts.
    
    This client handles authentication, request management, and response
    processing. It's designed to be intuitive for autonomous agents to 
    understand and use.
    
    Quick Start:
        >>> from weather_sdk import WeatherClient
        >>> client = WeatherClient(api_key="your-key")
        >>> weather = client.get_current_weather("New York, NY")
        >>> print(f"Temperature: {weather.temperature}°F")
        
    Authentication:
        The client supports API key authentication:
        
        >>> client = WeatherClient(api_key="your-api-key")
        
        Or using environment variables:
        >>> import os
        >>> client = WeatherClient(api_key=os.getenv("WEATHER_API_KEY"))
    
    Error Handling:
        >>> try:
        ...     weather = client.get_current_weather("Invalid Location")
        ... except WeatherError as e:
        ...     print(f"Weather API Error: {e}")
        ... except AuthenticationError as e:
        ...     print(f"Auth failed: {e}")
    
    Common Patterns:
        Multiple locations:
        >>> locations = ["New York, NY", "Los Angeles, CA", "Chicago, IL"]
        >>> for location in locations:
        ...     weather = client.get_current_weather(location)
        ...     print(f"{location}: {weather.temperature}°F")
        
        Forecast with error handling:
        >>> try:
        ...     forecast = client.get_forecast("Miami, FL", days=7)
        ...     for day in forecast.days:
        ...         print(f"{day.date}: {day.high_temp}°F")
        ... except WeatherError as e:
        ...     print(f"Forecast unavailable: {e}")
        
    See Also:
        - examples/quickstart.py: Basic usage patterns
        - examples/authentication.py: Authentication examples
        - examples/error_handling.py: Error management patterns
        - docs/api_reference.md: Complete API documentation
    """
    
    def __init__(self, api_key: str, base_url: str = None, timeout: int = 30):
        """
        Initialize the Weather API client.
        
        Args:
            api_key: Your weather API key for authentication
            base_url: Custom base URL for the weather service (optional)
            timeout: Request timeout in seconds (default: 30)
            
        Raises:
            AuthenticationError: If API key is invalid or missing
            
        Example:
            >>> client = WeatherClient(api_key="your-key")
            >>> client = WeatherClient(
            ...     api_key="your-key",
            ...     base_url="https://custom-weather-api.com",
            ...     timeout=60
            ... )
        """
        if not api_key:
            raise AuthenticationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url or "https://api.weather.example.com/v1"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "WeatherSDK/1.2.0"
        })
    
    def get_current_weather(self, location: str) -> WeatherData:
        """
        Get current weather conditions for a location.
        
        Args:
            location: Location name (e.g., "New York, NY" or "London, UK")
            
        Returns:
            WeatherData: Current weather information
            
        Raises:
            WeatherError: If weather data cannot be retrieved
            AuthenticationError: If API key is invalid
            APIError: If API request fails
            
        Examples:
            Basic usage:
            >>> client = WeatherClient(api_key="key")
            >>> weather = client.get_current_weather("San Francisco, CA")
            >>> print(f"Temperature: {weather.temperature}°F")
            >>> print(f"Humidity: {weather.humidity}%")
            
            With error handling:
            >>> try:
            ...     weather = client.get_current_weather("Invalid Location")
            ... except WeatherError as e:
            ...     print(f"Could not get weather: {e}")
            
            Multiple locations:
            >>> cities = ["New York", "London", "Tokyo"]
            >>> for city in cities:
            ...     try:
            ...         weather = client.get_current_weather(city)
            ...         print(f"{city}: {weather.temperature}°F")
            ...     except WeatherError:
            ...         print(f"{city}: Weather unavailable")
        """
        try:
            response = self.session.get(
                f"{self.base_url}/current",
                params={"location": location},
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 404:
                raise WeatherError(f"Location not found: {location}")
            elif response.status_code != 200:
                raise APIError(f"API request failed: {response.status_code}")
            
            data = response.json()
            return WeatherData.from_api_response(data)
            
        except requests.RequestException as e:
            raise APIError(f"Network error: {e}")
    
    def get_forecast(self, location: str, days: int = 5) -> ForecastData:
        """
        Get weather forecast for a location.
        
        Args:
            location: Location name (e.g., "New York, NY")
            days: Number of forecast days (1-10, default: 5)
            
        Returns:
            ForecastData: Weather forecast information
            
        Raises:
            WeatherError: If forecast data cannot be retrieved
            AuthenticationError: If API key is invalid
            APIError: If API request fails
            ValueError: If days parameter is out of range
            
        Examples:
            Basic forecast:
            >>> client = WeatherClient(api_key="key")
            >>> forecast = client.get_forecast("Chicago, IL")
            >>> for day in forecast.days:
            ...     print(f"{day.date}: {day.high_temp}°F / {day.low_temp}°F")
            
            Extended forecast:
            >>> forecast = client.get_forecast("Miami, FL", days=10)
            >>> print(f"10-day forecast for {forecast.location.name}")
            
            With validation:
            >>> try:
            ...     forecast = client.get_forecast("Boston, MA", days=15)
            ... except ValueError as e:
            ...     print(f"Invalid days parameter: {e}")
        """
        if not 1 <= days <= 10:
            raise ValueError("Days must be between 1 and 10")
        
        try:
            response = self.session.get(
                f"{self.base_url}/forecast",
                params={"location": location, "days": days},
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 404:
                raise WeatherError(f"Location not found: {location}")
            elif response.status_code != 200:
                raise APIError(f"API request failed: {response.status_code}")
            
            data = response.json()
            return ForecastData.from_api_response(data)
            
        except requests.RequestException as e:
            raise APIError(f"Network error: {e}")
    
    def search_locations(self, query: str, limit: int = 5) -> List[Location]:
        """
        Search for locations matching a query.
        
        Args:
            query: Search query (e.g., "New York" or "London")
            limit: Maximum number of results (1-20, default: 5)
            
        Returns:
            List[Location]: Matching locations
            
        Raises:
            WeatherError: If search fails
            AuthenticationError: If API key is invalid
            ValueError: If limit parameter is out of range
            
        Examples:
            Basic search:
            >>> client = WeatherClient(api_key="key")
            >>> locations = client.search_locations("New York")
            >>> for loc in locations:
            ...     print(f"{loc.name} - {loc.country}")
            
            Limited results:
            >>> locations = client.search_locations("London", limit=3)
            >>> print(f"Found {len(locations)} locations")
        """
        if not 1 <= limit <= 20:
            raise ValueError("Limit must be between 1 and 20")
        
        try:
            response = self.session.get(
                f"{self.base_url}/search",
                params={"q": query, "limit": limit},
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code != 200:
                raise APIError(f"API request failed: {response.status_code}")
            
            data = response.json()
            return [Location.from_api_response(item) for item in data.get("locations", [])]
            
        except requests.RequestException as e:
            raise APIError(f"Network error: {e}")
    
    def close(self):
        """
        Close the HTTP session and clean up resources.
        
        Example:
            >>> client = WeatherClient(api_key="key")
            >>> weather = client.get_current_weather("Boston, MA")
            >>> client.close()  # Clean up resources
        """
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.close()
