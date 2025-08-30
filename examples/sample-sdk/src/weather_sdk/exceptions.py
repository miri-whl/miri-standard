"""
Weather SDK Exceptions

Custom exception classes for structured error handling.
"""


class WeatherError(Exception):
    """
    Base exception for all weather SDK errors.
    
    This is the parent class for all weather-related exceptions.
    Catch this to handle any weather SDK error generically.
    
    Example:
        >>> try:
        ...     weather = client.get_current_weather("Invalid Location")
        ... except WeatherError as e:
        ...     print(f"Weather error occurred: {e}")
    """
    pass


class AuthenticationError(WeatherError):
    """
    Raised when API authentication fails.
    
    This typically occurs when:
    - API key is missing or invalid
    - API key has expired
    - API key lacks required permissions
    
    Example:
        >>> try:
        ...     client = WeatherClient(api_key="invalid-key")
        ...     weather = client.get_current_weather("New York")
        ... except AuthenticationError as e:
        ...     print(f"Authentication failed: {e}")
        ...     print("Please check your API key")
    """
    pass


class APIError(WeatherError):
    """
    Raised when the weather API returns an error.
    
    This covers various API-related issues:
    - Network connectivity problems
    - API server errors (5xx status codes)
    - Rate limiting (429 status code)
    - Malformed API responses
    
    Example:
        >>> try:
        ...     weather = client.get_current_weather("London")
        ... except APIError as e:
        ...     print(f"API error: {e}")
        ...     print("Please try again later")
    """
    pass


class LocationNotFoundError(WeatherError):
    """
    Raised when a requested location cannot be found.
    
    This occurs when the weather service cannot identify
    or provide data for the specified location.
    
    Example:
        >>> try:
        ...     weather = client.get_current_weather("Nonexistent City")
        ... except LocationNotFoundError as e:
        ...     print(f"Location error: {e}")
        ...     print("Please check the location name and try again")
    """
    pass


class RateLimitError(APIError):
    """
    Raised when API rate limits are exceeded.
    
    This occurs when too many requests are made in a short time period.
    The client should implement backoff and retry logic.
    
    Example:
        >>> import time
        >>> try:
        ...     weather = client.get_current_weather("Boston")
        ... except RateLimitError as e:
        ...     print(f"Rate limited: {e}")
        ...     print("Waiting before retry...")
        ...     time.sleep(60)  # Wait 1 minute
        ...     weather = client.get_current_weather("Boston")  # Retry
    """
    pass
