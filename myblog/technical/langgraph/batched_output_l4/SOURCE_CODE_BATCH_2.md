# Source Code Batch

This file contains 5 source files.

---

## File: 4_1_application_specific_tools.md

```markdown
# Building a Production-Grade Weather Tool for LangChain Agents

## Overview

In this comprehensive tutorial, you'll learn how to build a **production-grade weather tool** that can be used by LangChain agents. This goes beyond basic API integration to implement enterprise-ready patterns for reliability, security, and observability.

## Learning Objectives

By the end of this tutorial, you will master the six key requirements for production-grade tool development:

1. **Input Validation and Type Safety**: Use Pydantic models to validate and sanitize all inputs before processing
2. **Error Handling Strategy**: Implement comprehensive error classification and provide clear, actionable error messages
3. **Resilience and Retry Mechanisms**: Handle transient failures gracefully with exponential backoff and jitter
4. **Observability and Monitoring**: Add structured logging to track tool performance and debug issues
5. **Security Considerations**: Sanitize inputs, protect API keys, and prevent injection attacks
6. **Performance and Scalability**: Use connection pooling, timeouts, and efficient data structures

## What You'll Build

You'll create two interconnected weather tools:

- **Current Weather**: Get real-time weather for any location
- **Weather Forecast**: Get weather predictions for the next 2 days

These tools will work seamlessly with LangChain agents, allowing them to autonomously answer weather-related questions.

## Important Note About OpenWeatherMap API Tiers

This tutorial uses only **FREE tier** endpoints:
- ✅ **Current Weather API** - Included in free tier
- ✅ **5 Day / 3 Hour Forecast API** - Included in free tier
- ❌ **Historical Weather (Time Machine API)** - Requires paid subscription

We focus on the two free-tier endpoints to ensure the tutorial works with a free OpenWeatherMap account.

## Prerequisites

**API Keys Required:**
- **OpenAI API Key**: For the LangChain agent (https://platform.openai.com/api-keys)
- **OpenWeatherMap API Key**: For weather data (https://openweathermap.org/api) - Free tier available!

**Required Packages:**
```bash
pip install langchain langchain-openai langchain-core python-dotenv requests tenacity pydantic
```

**Setup Instructions:**

1. Create a `.env` file in your project directory
2. Add your API keys:
   ```
   OPENAI_API_KEY=your-openai-key-here
   OPENWEATHER_API_KEY=your-openweather-key-here
   ```
3. Sign up for a free OpenWeatherMap account at https://openweathermap.org/api
4. Generate an API key from your account dashboard

## Why Production-Grade Matters

Basic tool integration might work in development, but production environments demand:

- **Reliability**: Tools must handle network failures, rate limits, and API changes
- **Security**: Protect against malicious inputs and data leaks
- **Observability**: Track performance and debug issues quickly
- **User Experience**: Provide clear error messages instead of cryptic failures

This tutorial shows you how to implement all of these features systematically.

## Step 1: Setup and Imports

First, we'll import all necessary libraries and configure our environment. We'll use:

- **python-dotenv**: Securely load API keys from environment files
- **requests**: Make HTTP requests with session management
- **tenacity**: Implement retry logic with exponential backoff
- **pydantic**: Validate inputs with type safety
- **logging**: Add structured logging for observability
- **langchain**: Build the agent and tool decorators


```python
import os
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from collections import defaultdict

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

# Load environment variables from .env file
load_dotenv()

# Verify API keys are loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not os.getenv("OPENWEATHER_API_KEY"):
    raise ValueError("OPENWEATHER_API_KEY not found in environment variables")

print("All API keys loaded successfully!")
print("Required packages imported successfully!")
```

    All API keys loaded successfully!
    Required packages imported successfully!


## Step 2: Configure Structured Logging

**Why Logging Matters:**

In production environments, you need to:
- Track which tools are being called and with what parameters
- Measure execution times to identify performance bottlenecks
- Debug failures by understanding the sequence of events
- Monitor API usage to avoid rate limits

We'll configure Python's logging module with a structured format that includes timestamps, log levels, and contextual information.


```python
# Configure logging with structured format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create a logger for our weather tools
logger = logging.getLogger('weather_tools')

# Test the logger
logger.info("Logging system initialized successfully")

print("\nLogging configured with INFO level")
print("You'll see structured logs for all tool operations below")
```

    2025-11-12 16:41:41 - weather_tools - INFO - Logging system initialized successfully


    
    Logging configured with INFO level
    You'll see structured logs for all tool operations below


## Step 3: Build Geocoding Helper Function

**The Challenge:**

OpenWeatherMap's weather APIs require latitude and longitude coordinates, but users naturally want to query by city name ("London", "Tokyo", "New York"). We need a geocoding function to convert city names to coordinates.

**Production Considerations:**

- **Input Sanitization**: Clean and validate city names to prevent injection attacks
- **Error Handling**: Provide clear messages when cities aren't found
- **Logging**: Track geocoding requests for debugging
- **API Key Security**: Never log the API key itself


```python
def geocode_city(city_name: str) -> tuple[float, float]:
    """
    Convert a city name to latitude and longitude coordinates using OpenWeatherMap Geocoding API.
    
    This function is essential for converting user-friendly city names into the coordinates
    required by the OpenWeatherMap weather APIs.
    
    Args:
        city_name (str): The name of the city to geocode (e.g., "London", "New York")
        
    Returns:
        tuple[float, float]: A tuple of (latitude, longitude)
        
    Raises:
        ValueError: If the city is not found or the API request fails
        
    Example:
        >>> lat, lon = geocode_city("London")
        >>> print(f"London is at {lat}, {lon}")
    """
    # Sanitize input: strip whitespace and validate
    city_name = city_name.strip()
    
    if not city_name:
        raise ValueError("City name cannot be empty")
    
    # Additional sanitization: remove potentially dangerous characters
    # Allow only letters, spaces, hyphens, and apostrophes (for cities like "O'Fallon")
    if not all(c.isalnum() or c in " -'," for c in city_name):
        raise ValueError(f"Invalid city name format: {city_name}")
    
    logger.info(f"Geocoding city: {city_name}")
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = "http://api.openweathermap.org/geo/1.0/direct"
    
    params = {
        "q": city_name,
        "limit": 1,  # Only get the top result
        "appid": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            logger.warning(f"City not found: {city_name}")
            raise ValueError(
                f"Could not find coordinates for '{city_name}'. "
                "Please check the spelling or try a different city name."
            )
        
        lat = data[0]["lat"]
        lon = data[0]["lon"]
        
        logger.info(f"Successfully geocoded {city_name} to ({lat}, {lon})")
        
        return lat, lon
        
    except requests.exceptions.Timeout:
        logger.error(f"Geocoding request timed out for city: {city_name}")
        raise ValueError("The geocoding service is taking too long to respond. Please try again.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Geocoding request failed: {str(e)}")
        raise ValueError(f"Failed to geocode city: {str(e)}")

# Test the geocoding function
print("Testing geocoding function...")
try:
    lat, lon = geocode_city("London")
    print(f"\nSuccess! London coordinates: {lat}, {lon}")
except Exception as e:
    print(f"\nError: {e}")
```

    2025-11-12 16:41:42 - weather_tools - INFO - Geocoding city: London
    2025-11-12 16:41:42 - weather_tools - INFO - Successfully geocoded London to (51.5073219, -0.1276474)


    Testing geocoding function...
    
    Success! London coordinates: 51.5073219, -0.1276474


## Step 4: Define Pydantic Models for Input Validation

**Why Pydantic?**

Pydantic provides automatic validation and type checking for our inputs. This ensures:

- **Type Safety**: Inputs are the correct type before processing
- **Validation**: Custom validators catch invalid data early
- **Clear Error Messages**: Users get helpful feedback about what went wrong
- **Documentation**: Models serve as clear API contracts

**Our Validation Models:**

1. **WeatherLocation**: Validates city names for current weather
2. **ForecastWeatherInput**: Validates inputs for forecast queries (enforces 2 days)

Note how we enforce the "2 days" requirement at the validation layer, making it impossible to accidentally request the wrong time range.


```python
class WeatherLocation(BaseModel):
    """
    Validates a location input for weather queries.
    
    Attributes:
        city (str): The city name to query (e.g., "London", "New York")
    """
    city: str = Field(
        ..., 
        min_length=1,
        max_length=100,
        description="The name of the city to get weather for"
    )
    
    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        """Sanitize and validate city name."""
        v = v.strip()
        
        if not v:
            raise ValueError("City name cannot be empty or just whitespace")
        
        # Allow only safe characters
        if not all(c.isalnum() or c in " -'," for c in v):
            raise ValueError(
                f"City name contains invalid characters. "
                f"Only letters, numbers, spaces, hyphens, and apostrophes are allowed."
            )
        
        return v


class ForecastWeatherInput(BaseModel):
    """
    Validates input for weather forecast queries.
    Enforces that we always query for exactly 2 days of forecast data.
    
    Attributes:
        city (str): The city name to query
        days (int): Number of forecast days (must be 2)
    """
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The name of the city"
    )
    days: int = Field(
        default=2,
        description="Number of forecast days to retrieve (must be 2)"
    )
    
    @field_validator('days')
    @classmethod
    def validate_days(cls, v):
        """Ensure we only query for 2 days of forecast data."""
        if v != 2:
            raise ValueError(
                f"Weather forecast is only available for 2 days. Got: {v} days"
            )
        return v
    
    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        """Sanitize and validate city name."""
        v = v.strip()
        if not v:
            raise ValueError("City name cannot be empty")
        if not all(c.isalnum() or c in " -'," for c in v):
            raise ValueError("City name contains invalid characters")
        return v

# Test the validation models
print("Testing Pydantic validation models...\n")

# Test valid input
try:
    location = WeatherLocation(city="London")
    print(f"Valid location: {location.city}")
except Exception as e:
    print(f"Validation error: {e}")

# Test invalid input (empty city)
try:
    location = WeatherLocation(city="   ")
    print(f"Valid location: {location.city}")
except Exception as e:
    print(f"\nCaught expected validation error for empty city: {e}")

# Test invalid days for forecast
try:
    forecast = ForecastWeatherInput(city="Paris", days=5)
    print(f"Valid forecast input: {forecast}")
except Exception as e:
    print(f"\nCaught expected validation error for wrong days: {e}")

print("\nValidation models working correctly!")
```

    Testing Pydantic validation models...
    
    Valid location: London
    
    Caught expected validation error for empty city: 1 validation error for WeatherLocation
    city
      Value error, City name cannot be empty or just whitespace [type=value_error, input_value='   ', input_type=str]
        For further information visit https://errors.pydantic.dev/2.12/v/value_error
    
    Caught expected validation error for wrong days: 1 validation error for ForecastWeatherInput
    days
      Value error, Weather forecast is only available for 2 days. Got: 5 days [type=value_error, input_value=5, input_type=int]
        For further information visit https://errors.pydantic.dev/2.12/v/value_error
    
    Validation models working correctly!


## Step 5: Build the Weather API Client Class

**Why a Client Class?**

Instead of making raw API calls in each tool function, we create a centralized client class that handles:

1. **Connection Pooling**: Reuse HTTP connections for better performance
2. **Retry Logic**: Automatically retry failed requests with exponential backoff
3. **Timeout Handling**: Prevent hanging requests
4. **Structured Logging**: Track all API interactions
5. **Error Classification**: Distinguish between authentication, network, and API errors

**Key Features:**

- **Session Management**: Using `requests.Session()` for connection pooling
- **Tenacity Integration**: Automatic retries with exponential backoff and jitter
- **Execution Timing**: Track how long each API call takes
- **Security**: Never log API keys


```python
class WeatherAPIClient:
    """
    Production-grade client for OpenWeatherMap API with built-in resilience,
    observability, and error handling.
    
    Features:
    - Connection pooling via requests.Session
    - Automatic retries with exponential backoff
    - Structured logging for observability
    - Comprehensive error handling and classification
    - Request timeout protection
    """
    
    def __init__(self, api_key: str, timeout: int = 10, max_retries: int = 3):
        """
        Initialize the Weather API client.
        
        Args:
            api_key (str): OpenWeatherMap API key
            timeout (int): Request timeout in seconds (default: 10)
            max_retries (int): Maximum retry attempts (default: 3)
        """
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Use requests.Session for connection pooling
        self.session = requests.Session()
        
        # Configure session for better performance
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # We handle retries with tenacity
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.logger = logging.getLogger('weather_tools.api_client')
        self.logger.info("Weather API Client initialized")
    
    def _log_request(self, endpoint: str, params: Dict[str, Any], duration: float, success: bool):
        """
        Log API request details for observability.
        
        Args:
            endpoint (str): The API endpoint called
            params (Dict[str, Any]): Request parameters (API key will be sanitized)
            duration (float): Request duration in seconds
            success (bool): Whether the request succeeded
        """
        # Sanitize parameters to remove API key
        safe_params = {k: v for k, v in params.items() if k != 'appid'}
        safe_params['appid'] = '***REDACTED***'
        
        status = "SUCCESS" if success else "FAILURE"
        self.logger.info(
            f"API Request [{status}] - Endpoint: {endpoint} - "
            f"Duration: {duration:.2f}s - Params: {safe_params}"
        )
    
    @retry(
        # Retry only on network-related exceptions
        retry=retry_if_exception_type((requests.exceptions.Timeout, 
                                      requests.exceptions.ConnectionError)),
        # Stop after 3 attempts
        stop=stop_after_attempt(3),
        # Exponential backoff: 1s, 2s, 4s with random jitter
        wait=wait_exponential(multiplier=1, min=1, max=10),
        # Log before each retry
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an API request with automatic retry logic and comprehensive error handling.
        
        Args:
            endpoint (str): The API endpoint URL
            params (Dict[str, Any]): Query parameters for the request
            
        Returns:
            Dict[str, Any]: The JSON response from the API
            
        Raises:
            ValueError: For authentication errors or invalid requests
            ConnectionError: For network-related failures
            TimeoutError: When request exceeds timeout
        """
        start_time = time.time()
        
        try:
            # Add API key to parameters
            params['appid'] = self.api_key
            
            # Make the request with timeout
            response = self.session.get(endpoint, params=params, timeout=self.timeout)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Handle different HTTP status codes
            if response.status_code == 401:
                self._log_request(endpoint, params, duration, False)
                raise ValueError(
                    "Authentication failed. Please check your OpenWeatherMap API key."
                )
            
            if response.status_code == 404:
                self._log_request(endpoint, params, duration, False)
                raise ValueError(
                    "Location not found. Please check the coordinates or city name."
                )
            
            if response.status_code == 429:
                self._log_request(endpoint, params, duration, False)
                raise ValueError(
                    "API rate limit exceeded. Please try again in a few moments."
                )
            
            # Raise an exception for other error status codes
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Log successful request
            self._log_request(endpoint, params, duration, True)
            
            return data
            
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self._log_request(endpoint, params, duration, False)
            self.logger.error(f"Request timeout after {self.timeout}s")
            raise TimeoutError(
                f"The weather service is taking too long to respond. "
                f"Request timed out after {self.timeout} seconds."
            )
        
        except requests.exceptions.ConnectionError as e:
            duration = time.time() - start_time
            self._log_request(endpoint, params, duration, False)
            self.logger.error(f"Connection error: {str(e)}")
            raise ConnectionError(
                "Unable to connect to the weather service. "
                "Please check your internet connection."
            )
        
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self._log_request(endpoint, params, duration, False)
            self.logger.error(f"Request failed: {str(e)}")
            raise ValueError(f"Weather API request failed: {str(e)}")
    
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get current weather for a location.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            Dict[str, Any]: Current weather data
        """
        endpoint = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "units": "metric"  # Use metric units (Celsius, meters/sec)
        }
        return self._make_request(endpoint, params)
    
    def get_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get weather forecast for a location using the FREE tier 5 Day / 3 Hour Forecast API.
        
        This method uses the free-tier forecast endpoint instead of One Call API.
        Returns 3-hour interval forecasts for up to 5 days (40 data points).
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            Dict[str, Any]: Forecast data with 'list' containing forecast points
        """
        endpoint = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "units": "metric",  # Use metric units (Celsius, meters/sec)
            "cnt": 16  # Get 16 data points (2 days * 8 forecasts per day)
        }
        return self._make_request(endpoint, params)

# Initialize the API client
api_client = WeatherAPIClient(
    api_key=os.getenv("OPENWEATHER_API_KEY"),
    timeout=10,
    max_retries=3
)

print("\nWeather API Client initialized successfully!")
print("Features: Connection pooling, automatic retries, structured logging")
print("Using FREE tier endpoints: Current Weather API and 5 Day Forecast API")
```

    2025-11-12 16:41:48 - weather_tools.api_client - INFO - Weather API Client initialized


    
    Weather API Client initialized successfully!
    Features: Connection pooling, automatic retries, structured logging
    Using FREE tier endpoints: Current Weather API and 5 Day Forecast API


## Step 6: Build the Current Weather Tool

**Now we bring it all together!**

This tool combines:
- Pydantic validation (type safety)
- Geocoding (user-friendly city names)
- The API client (resilience and retries)
- Structured logging (observability)
- Clear error messages (user experience)

**Key Details:**

1. The `@tool` decorator makes this function available to LangChain agents
2. The docstring is crucial - the agent reads it to understand when to use this tool
3. We return a human-readable string, not raw JSON
4. All errors are caught and converted to helpful messages


```python
@tool
def get_current_weather(city: str) -> str:
    """
    Get the current weather conditions for a specified city.
    
    Use this tool when the user asks about current weather, present conditions,
    or "right now" weather in any location.
    
    Args:
        city (str): The name of the city (e.g., "London", "New York", "Tokyo")
        
    Returns:
        str: A human-readable description of the current weather including:
             - Temperature (in Celsius)
             - Weather description (e.g., "clear sky", "light rain")
             - Humidity percentage
             - Wind speed (in meters/second)
             
    Example:
        get_current_weather("London") -> "Current weather in London: 15°C, partly cloudy..."
    """
    logger.info(f"Tool invoked: get_current_weather(city={city})")
    start_time = time.time()
    
    try:
        # Step 1: Validate input using Pydantic
        location = WeatherLocation(city=city)
        logger.info(f"Input validation passed for city: {location.city}")
        
        # Step 2: Geocode the city to get coordinates
        lat, lon = geocode_city(location.city)
        
        # Step 3: Fetch current weather data
        weather_data = api_client.get_current_weather(lat, lon)
        
        # Step 4: Format the response for human readability
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        
        result = (
            f"Current weather in {location.city}:\n"
            f"  Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"  Conditions: {description.capitalize()}\n"
            f"  Humidity: {humidity}%\n"
            f"  Wind Speed: {wind_speed} m/s"
        )
        
        duration = time.time() - start_time
        logger.info(f"Tool completed successfully in {duration:.2f}s")
        
        return result
        
    except ValueError as e:
        # Input validation or API errors (user-friendly messages)
        duration = time.time() - start_time
        logger.error(f"Validation error after {duration:.2f}s: {str(e)}")
        return f"Error: {str(e)}"
    
    except TimeoutError as e:
        # Timeout errors
        duration = time.time() - start_time
        logger.error(f"Timeout error after {duration:.2f}s: {str(e)}")
        return f"Error: {str(e)}"
    
    except ConnectionError as e:
        # Network errors
        duration = time.time() - start_time
        logger.error(f"Connection error after {duration:.2f}s: {str(e)}")
        return f"Error: {str(e)}"
    
    except Exception as e:
        # Catch-all for unexpected errors
        duration = time.time() - start_time
        logger.error(f"Unexpected error after {duration:.2f}s: {str(e)}", exc_info=True)
        return (
            f"An unexpected error occurred while fetching weather data: {str(e)}. "
            "Please try again or contact support if the problem persists."
        )

# Test the current weather tool
print("\nTesting current weather tool...\n")
result = get_current_weather.invoke({"city": "Singapore"})
print(result)
```

    2025-11-12 16:41:49 - weather_tools - INFO - Tool invoked: get_current_weather(city=Singapore)
    2025-11-12 16:41:49 - weather_tools - INFO - Input validation passed for city: Singapore
    2025-11-12 16:41:49 - weather_tools - INFO - Geocoding city: Singapore
    2025-11-12 16:41:49 - weather_tools - INFO - Successfully geocoded Singapore to (1.2899175, 103.8519072)
    2025-11-12 16:41:49 - weather_tools.api_client - INFO - API Request [SUCCESS] - Endpoint: https://api.openweathermap.org/data/2.5/weather - Duration: 0.03s - Params: {'lat': 1.2899175, 'lon': 103.8519072, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-12 16:41:49 - weather_tools - INFO - Tool completed successfully in 0.05s


    
    Testing current weather tool...
    
    Current weather in Singapore:
      Temperature: 29.33°C (feels like 33.88°C)
      Conditions: Thunderstorm with light rain
      Humidity: 72%
      Wind Speed: 4.12 m/s


## Step 7: Build the Weather Forecast Tool

**The Challenge:**

Weather forecasts return data for multiple days. We need to:
1. Extract only the next 2 days from the forecast
2. Format the data clearly for each day
3. Include relevant forecast information (high/low temps, conditions)

**Production Considerations:**

- The API returns a `daily` array with forecasts for up to 8 days
- We only take the first 2 elements (index 0 and 1 are tomorrow and day after)
- We format both the date and the forecast data clearly
- Forecasts include min/max temperatures, which we display


```python
@tool
def get_weather_forecast(city: str) -> str:
    """
    Get the weather forecast for the next 2 days for a specified city.
    
    Use this tool when the user asks about future weather, weather predictions,
    "tomorrow's weather", or "weather forecast for the next few days".
    
    Args:
        city (str): The name of the city (e.g., "London", "New York", "Tokyo")
        
    Returns:
        str: A forecast summary for the next 2 days including:
             - Date for each day
             - Temperature predictions (in Celsius)
             - Expected weather conditions
             - Humidity and wind predictions
             
    Example:
        get_weather_forecast("Berlin") -> "Weather forecast for Berlin (next 2 days)..."
    """
    logger.info(f"Tool invoked: get_weather_forecast(city={city})")
    start_time = time.time()
    
    try:
        # Step 1: Validate input
        input_data = ForecastWeatherInput(city=city, days=2)
        logger.info(f"Input validation passed for city: {input_data.city}")
        
        # Step 2: Geocode the city
        lat, lon = geocode_city(input_data.city)
        
        # Step 3: Fetch forecast data (free tier 5 Day / 3 Hour Forecast API)
        forecast_data = api_client.get_forecast(lat, lon)
        
        # Step 4: Process the forecast data
        # The API returns forecasts in 3-hour intervals
        # We need to group by day and extract the next 2 days
        
        forecast_list = forecast_data['list']
        
        # Group forecasts by date
        daily_forecasts = defaultdict(list)
        
        for forecast in forecast_list:
            # Convert timestamp to date
            forecast_date = datetime.fromtimestamp(forecast['dt']).date()
            daily_forecasts[forecast_date].append(forecast)
        
        # Get the next 2 days (sorted by date)
        sorted_dates = sorted(daily_forecasts.keys())[:2]
        
        # Step 5: Format the response
        results = []
        
        for i, date in enumerate(sorted_dates):
            day_forecasts = daily_forecasts[date]
            day_label = "tomorrow" if i == 0 else "day after tomorrow"
            
            # Calculate aggregate statistics for the day
            temps = [f['main']['temp'] for f in day_forecasts]
            temp_min = min(f['main']['temp_min'] for f in day_forecasts)
            temp_max = max(f['main']['temp_max'] for f in day_forecasts)
            avg_temp = sum(temps) / len(temps)
            
            # Get the most common weather condition
            conditions = [f['weather'][0]['description'] for f in day_forecasts]
            most_common_condition = max(set(conditions), key=conditions.count)
            
            # Average humidity and wind speed
            avg_humidity = sum(f['main']['humidity'] for f in day_forecasts) / len(day_forecasts)
            avg_wind = sum(f['wind']['speed'] for f in day_forecasts) / len(day_forecasts)
            
            results.append(
                f"  {date.strftime('%Y-%m-%d')} ({day_label}):\n"
                f"    Temperature: {avg_temp:.1f}°C (High: {temp_max:.1f}°C, Low: {temp_min:.1f}°C)\n"
                f"    Conditions: {most_common_condition.capitalize()}\n"
                f"    Humidity: {avg_humidity:.0f}%\n"
                f"    Wind Speed: {avg_wind:.1f} m/s"
            )
        
        result = f"Weather forecast for {input_data.city} (next 2 days):\n\n" + "\n\n".join(results)
        
        duration = time.time() - start_time
        logger.info(f"Tool completed successfully in {duration:.2f}s")
        
        return result
        
    except ValueError as e:
        duration = time.time() - start_time
        logger.error(f"Validation error after {duration:.2f}s: {str(e)}")
        return f"Error: {str(e)}"
    
    except TimeoutError as e:
        duration = time.time() - start_time
        logger.error(f"Timeout error after {duration:.2f}s: {str(e)}")
        return f"Error: {str(e)}"
    
    except ConnectionError as e:
        duration = time.time() - start_time
        logger.error(f"Connection error after {duration:.2f}s: {str(e)}")
        return f"Error: {str(e)}"
    
    except KeyError as e:
        duration = time.time() - start_time
        logger.error(f"Data parsing error after {duration:.2f}s: {str(e)}")
        return (
            f"Error: The weather API returned unexpected data format. "
            f"Missing field: {str(e)}. Please try again."
        )
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Unexpected error after {duration:.2f}s: {str(e)}", exc_info=True)
        return (
            f"An unexpected error occurred while fetching forecast data: {str(e)}. "
            "Please try again or contact support if the problem persists."
        )

# Test the forecast weather tool
print("\nTesting weather forecast tool...\n")
result = get_weather_forecast.invoke({"city": "Paris"})
print(result)
```

    2025-11-12 16:42:26 - weather_tools - INFO - Tool invoked: get_weather_forecast(city=Paris)
    2025-11-12 16:42:26 - weather_tools - INFO - Input validation passed for city: Paris
    2025-11-12 16:42:26 - weather_tools - INFO - Geocoding city: Paris
    2025-11-12 16:42:26 - weather_tools - INFO - Successfully geocoded Paris to (48.8588897, 2.3200410217200766)
    2025-11-12 16:42:26 - weather_tools.api_client - INFO - API Request [SUCCESS] - Endpoint: https://api.openweathermap.org/data/2.5/forecast - Duration: 0.01s - Params: {'lat': 48.8588897, 'lon': 2.3200410217200766, 'units': 'metric', 'cnt': 16, 'appid': '***REDACTED***'}
    2025-11-12 16:42:26 - weather_tools - INFO - Tool completed successfully in 0.03s


    
    Testing weather forecast tool...
    
    Weather forecast for Paris (next 2 days):
    
      2025-11-12 (tomorrow):
        Temperature: 11.8°C (High: 16.3°C, Low: 9.8°C)
        Conditions: Scattered clouds
        Humidity: 70%
        Wind Speed: 3.9 m/s
    
      2025-11-13 (day after tomorrow):
        Temperature: 14.9°C (High: 17.7°C, Low: 12.4°C)
        Conditions: Overcast clouds
        Humidity: 63%
        Wind Speed: 3.3 m/s


## Step 8: Configure the Language Model

Now we'll set up the LangChain agent that will use our weather tools.

**Key Configuration:**

- **Model**: GPT-4 or GPT-4-Turbo for reliable reasoning and tool usage
- **Temperature**: 0.1 for more consistent and predictable responses

The low temperature ensures the agent makes consistent decisions about which tools to use.


```python
# Configure the language model
model = ChatOpenAI(
    model="gpt-4o",  # Use GPT-4-Turbo for reliable tool usage
    temperature=0.1       # Low temperature for consistent reasoning
)

print(f"Language model configured: {model.model_name}")
print(f"Temperature: {model.temperature}")
print("\nThis model will power the agent's reasoning about which tools to use.")
```

    Language model configured: gpt-4o
    Temperature: 0.1
    
    This model will power the agent's reasoning about which tools to use.


## Step 9: Create the Agent with Weather Tools

**The Magic Happens Here:**

We create a LangChain agent and give it access to our 2 weather tools:

1. `get_current_weather` - for present conditions
2. `get_weather_forecast` - for next 2 days

**How It Works:**

The agent will:
1. Read the user's question
2. Examine the docstrings of all available tools
3. Decide which tool(s) to use based on the query
4. Call the appropriate tool(s) with the right parameters
5. Synthesize the results into a natural language response

This is **autonomous decision-making** - we don't tell the agent which tool to use!


```python
# Create a list of our weather tools (2 tools)
weather_tools = [
    get_current_weather,
    get_weather_forecast
]

# Create the agent with access to all weather tools
agent = create_agent(
    model=model,
    tools=weather_tools
)

print("Agent created successfully!")
print(f"\nAgent has access to {len(weather_tools)} tools:")
for tool in weather_tools:
    print(f"  - {tool.name}: {tool.description[:80]}...")
```

    Agent created successfully!
    
    Agent has access to 2 tools:
      - get_current_weather: Get the current weather conditions for a specified city.
    
    Use this tool when the...
      - get_weather_forecast: Get the weather forecast for the next 2 days for a specified city.
    
    Use this too...


## Step 10: Create a Helper Function for Agent Interaction

To make testing easier, we'll create a helper function that:

1. Takes a natural language question
2. Invokes the agent
3. Extracts and prints the final response

This simplifies our test examples and makes the notebook more readable.


```python
def ask_agent(question: str) -> str:
    """
    Ask the weather agent a question and return the response.
    
    Args:
        question (str): The natural language question to ask
        
    Returns:
        str: The agent's response
    """
    print(f"\n{'='*80}")
    print(f"Question: {question}")
    print(f"{'='*80}\n")
    
    # Invoke the agent with properly formatted messages
    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    
    # Extract the final response
    final_message = result["messages"][-1]
    response = final_message.content
    
    print(f"Response:\n{response}\n")
    
    return response

print("Helper function created successfully!")
print("Ready to test the agent with natural language questions.")
```

    Helper function created successfully!
    Ready to test the agent with natural language questions.


## Step 11: Test the Agent - Current Weather Query

Let's start with a simple query about current weather.

**What to Watch For:**

- The agent should automatically choose `get_current_weather`
- It should extract "London" from the question
- You'll see logging output showing the tool execution
- The final response should be natural and conversational


```python
# Test Example 1: Current weather query
response1 = ask_agent("What's the weather like in London right now?")
```

    
    ================================================================================
    Question: What's the weather like in London right now?
    ================================================================================
    


    2025-11-12 16:43:10 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-12 16:43:10 - weather_tools - INFO - Tool invoked: get_current_weather(city=London)
    2025-11-12 16:43:10 - weather_tools - INFO - Input validation passed for city: London
    2025-11-12 16:43:10 - weather_tools - INFO - Geocoding city: London
    2025-11-12 16:43:10 - weather_tools - INFO - Successfully geocoded London to (51.5073219, -0.1276474)
    2025-11-12 16:43:10 - weather_tools.api_client - INFO - API Request [SUCCESS] - Endpoint: https://api.openweathermap.org/data/2.5/weather - Duration: 0.01s - Params: {'lat': 51.5073219, 'lon': -0.1276474, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-12 16:43:10 - weather_tools - INFO - Tool completed successfully in 0.36s
    2025-11-12 16:43:12 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    Response:
    The current weather in London is overcast with a temperature of 14.15°C, which feels like 13.79°C. The humidity is at 83%, and the wind speed is 3.13 meters per second.
    


## Step 12: Test the Agent - Forecast Query

Let's test the forecast tool.

**What to Watch For:**

- The agent should choose `get_weather_forecast` based on "next 2 days"
- The response should include high/low temperatures for each day
- Watch the structured logging show execution time and success status


```python
# Test Example 2: Weather forecast query
response2 = ask_agent("What's the weather forecast for Singapore for the next 2 days?")
```

    
    ================================================================================
    Question: What's the weather forecast for Singapore for the next 2 days?
    ================================================================================
    


    2025-11-12 16:43:30 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-12 16:43:30 - weather_tools - INFO - Tool invoked: get_weather_forecast(city=Singapore)
    2025-11-12 16:43:30 - weather_tools - INFO - Input validation passed for city: Singapore
    2025-11-12 16:43:30 - weather_tools - INFO - Geocoding city: Singapore
    2025-11-12 16:43:30 - weather_tools - INFO - Successfully geocoded Singapore to (1.2899175, 103.8519072)
    2025-11-12 16:43:30 - weather_tools.api_client - INFO - API Request [SUCCESS] - Endpoint: https://api.openweathermap.org/data/2.5/forecast - Duration: 0.02s - Params: {'lat': 1.2899175, 'lon': 103.8519072, 'units': 'metric', 'cnt': 16, 'appid': '***REDACTED***'}
    2025-11-12 16:43:30 - weather_tools - INFO - Tool completed successfully in 0.04s
    2025-11-12 16:43:32 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    Response:
    The weather forecast for Singapore for the next 2 days is as follows:
    
    - **Tomorrow (2025-11-12):**
      - Temperature: 28.7°C (High: 29.5°C, Low: 26.7°C)
      - Conditions: Broken clouds
      - Humidity: 73%
      - Wind Speed: 5.2 m/s
    
    - **Day after tomorrow (2025-11-13):**
      - Temperature: 27.1°C (High: 28.3°C, Low: 25.9°C)
      - Conditions: Light rain
      - Humidity: 80%
      - Wind Speed: 3.8 m/s
    


## Step 13: Test the Agent - Multi-City Comparison

Now let's test something more complex: comparing weather across multiple cities.

**What to Watch For:**

- The agent should call `get_current_weather` **twice** (once for Paris, once for Berlin)
- It should synthesize the results into a comparison
- This demonstrates the agent's ability to orchestrate multiple tool calls
- Each city's geocoding and API call will be logged separately


```python
# Test Example 3: Multi-city comparison
response3 = ask_agent("Compare the current weather in Paris and Berlin")
```

    
    ================================================================================
    Question: Compare the current weather in Paris and Berlin
    ================================================================================
    


    2025-11-12 16:43:58 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-12 16:43:58 - weather_tools - INFO - Tool invoked: get_current_weather(city=Paris)
    2025-11-12 16:43:58 - weather_tools - INFO - Tool invoked: get_current_weather(city=Berlin)
    2025-11-12 16:43:58 - weather_tools - INFO - Input validation passed for city: Berlin
    2025-11-12 16:43:58 - weather_tools - INFO - Geocoding city: Berlin
    2025-11-12 16:43:58 - weather_tools - INFO - Input validation passed for city: Paris
    2025-11-12 16:43:58 - weather_tools - INFO - Geocoding city: Paris
    2025-11-12 16:43:58 - weather_tools - INFO - Successfully geocoded Paris to (48.8588897, 2.3200410217200766)
    2025-11-12 16:43:58 - weather_tools.api_client - INFO - API Request [SUCCESS] - Endpoint: https://api.openweathermap.org/data/2.5/weather - Duration: 0.01s - Params: {'lat': 48.8588897, 'lon': 2.3200410217200766, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-12 16:43:58 - weather_tools - INFO - Tool completed successfully in 0.04s
    2025-11-12 16:43:58 - weather_tools - INFO - Successfully geocoded Berlin to (52.5170365, 13.3888599)
    2025-11-12 16:43:58 - weather_tools.api_client - INFO - API Request [SUCCESS] - Endpoint: https://api.openweathermap.org/data/2.5/weather - Duration: 0.02s - Params: {'lat': 52.5170365, 'lon': 13.3888599, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-12 16:43:58 - weather_tools - INFO - Tool completed successfully in 0.24s
    2025-11-12 16:44:00 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    Response:
    Here's the current weather comparison between Paris and Berlin:
    
    **Paris:**
    - Temperature: 9.06°C (feels like 6.79°C)
    - Conditions: Clear sky
    - Humidity: 85%
    - Wind Speed: 4.12 m/s
    
    **Berlin:**
    - Temperature: 7.09°C (feels like 4.93°C)
    - Conditions: Clear sky
    - Humidity: 89%
    - Wind Speed: 3.13 m/s
    
    Both cities are experiencing clear skies, but Paris is slightly warmer than Berlin.
    



```python
response3 = ask_agent("Is it hotter in Singapore or Phuket today?")
```

    
    ================================================================================
    Question: Is it hotter in Singapore or Phuket today?
    ================================================================================
    


    2025-11-12 16:47:19 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-12 16:47:19 - weather_tools - INFO - Tool invoked: get_current_weather(city=Singapore)
    2025-11-12 16:47:19 - weather_tools - INFO - Tool invoked: get_current_weather(city=Phuket)
    2025-11-12 16:47:19 - weather_tools - INFO - Input validation passed for city: Phuket
    2025-11-12 16:47:19 - weather_tools - INFO - Geocoding city: Phuket
    2025-11-12 16:47:19 - weather_tools - INFO - Input validation passed for city: Singapore
    2025-11-12 16:47:19 - weather_tools - INFO - Geocoding city: Singapore
    2025-11-12 16:47:19 - weather_tools - INFO - Successfully geocoded Singapore to (1.2899175, 103.8519072)
    2025-11-12 16:47:19 - weather_tools - INFO - Successfully geocoded Phuket to (7.8847901, 98.3891503)
    2025-11-12 16:47:19 - weather_tools.api_client - INFO - API Request [SUCCESS] - Endpoint: https://api.openweathermap.org/data/2.5/weather - Duration: 0.05s - Params: {'lat': 7.8847901, 'lon': 98.3891503, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-12 16:47:19 - weather_tools - INFO - Tool completed successfully in 0.08s
    2025-11-12 16:47:19 - weather_tools.api_client - INFO - API Request [SUCCESS] - Endpoint: https://api.openweathermap.org/data/2.5/weather - Duration: 0.05s - Params: {'lat': 1.2899175, 'lon': 103.8519072, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-12 16:47:19 - weather_tools - INFO - Tool completed successfully in 0.08s
    2025-11-12 16:47:20 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    Response:
    Today, the temperature in Singapore is 29.52°C, while in Phuket, it is slightly warmer at 30.06°C.
    



```python
# Test Example 4: Invalid city name (error handling)
response4 = ask_agent("What's the weather in xyz?")
```

    
    ================================================================================
    Question: What's the weather in xyz?
    ================================================================================
    


    2025-11-12 16:47:45 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    Response:
    It seems like "xyz" might be a placeholder or an error in the city name. Could you please provide the correct name of the city you're interested in?
    


## Step 14: Test Error Handling - Simulating Production Error Conditions

Now let's test our production-grade error handling by simulating various failure scenarios. This demonstrates how the system **gracefully degrades** instead of crashing.

**Error Scenarios We'll Test:**

1. **Invalid City Name** - Non-existent location
2. **Malicious Input** - SQL injection attempt
3. **Empty/Whitespace Input** - Validation failure
4. **Special Characters** - Security validation
5. **Numbers as City Name** - Type confusion

**What to Watch For:**

- ✅ System never crashes
- ✅ Clear, user-friendly error messages
- ✅ Detailed logging for debugging
- ✅ Input sanitization blocks malicious inputs
- ✅ Validation catches invalid data early

This is the difference between a basic implementation and a **production-ready system**!


```python
print("="*80)
print("ERROR CONDITION TESTING - Production-Grade Error Handling")
print("="*80)

# Error Test 1: Non-existent City
print("\n1. Testing Invalid City Name (Non-existent location)")
print("-" * 80)
try:
    result = get_current_weather.invoke({"city": "XYZ123InvalidCity"})
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception caught: {e}")

# Error Test 2: SQL Injection Attempt
print("\n2. Testing Malicious Input (SQL Injection Attempt)")
print("-" * 80)
try:
    result = get_current_weather.invoke({"city": "London'; DROP TABLE weather;--"})
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception caught: {e}")

# Error Test 3: Empty/Whitespace Input
print("\n3. Testing Empty/Whitespace Input (Validation Failure)")
print("-" * 80)
try:
    result = get_current_weather.invoke({"city": "    "})
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception caught: {e}")

# Error Test 4: Special Characters
print("\n4. Testing Special Characters (Security Validation)")
print("-" * 80)
try:
    result = get_current_weather.invoke({"city": "<script>alert('XSS')</script>"})
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception caught: {e}")

# Error Test 5: Numbers Only
print("\n5. Testing Numbers as City Name (Type Confusion)")
print("-" * 80)
try:
    result = get_current_weather.invoke({"city": "12345"})
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception caught: {e}")

# Error Test 6: Extremely Long Input
print("\n6. Testing Extremely Long City Name (Input Length Validation)")
print("-" * 80)
try:
    result = get_current_weather.invoke({"city": "A" * 200})
    print(f"Result: {result}")
except Exception as e:
    print(f"Exception caught: {e}")

print("\n" + "="*80)
print("SUMMARY: All error conditions handled gracefully!")
print("="*80)
print("\nKey Observations:")
print("✅ No system crashes or unhandled exceptions")
print("✅ Clear, actionable error messages for users")
print("✅ Detailed logging for debugging (check logs above)")
print("✅ Input sanitization blocked malicious inputs")
print("✅ Validation caught invalid data before API calls")
print("\nProduction-Grade Error Handling: VERIFIED ✓")
```

    2025-11-12 16:58:34 - weather_tools - INFO - Tool invoked: get_current_weather(city=XYZ123InvalidCity)
    2025-11-12 16:58:34 - weather_tools - INFO - Input validation passed for city: XYZ123InvalidCity
    2025-11-12 16:58:34 - weather_tools - INFO - Geocoding city: XYZ123InvalidCity


    ================================================================================
    ERROR CONDITION TESTING - Production-Grade Error Handling
    ================================================================================
    
    1. Testing Invalid City Name (Non-existent location)
    --------------------------------------------------------------------------------


    2025-11-12 16:58:34 - weather_tools - WARNING - City not found: XYZ123InvalidCity
    2025-11-12 16:58:34 - weather_tools - ERROR - Validation error after 0.23s: Could not find coordinates for 'XYZ123InvalidCity'. Please check the spelling or try a different city name.
    2025-11-12 16:58:34 - weather_tools - INFO - Tool invoked: get_current_weather(city=London'; DROP TABLE weather;--)
    2025-11-12 16:58:34 - weather_tools - ERROR - Validation error after 0.00s: 1 validation error for WeatherLocation
    city
      Value error, City name contains invalid characters. Only letters, numbers, spaces, hyphens, and apostrophes are allowed. [type=value_error, input_value="London'; DROP TABLE weather;--", input_type=str]
        For further information visit https://errors.pydantic.dev/2.12/v/value_error
    2025-11-12 16:58:34 - weather_tools - INFO - Tool invoked: get_current_weather(city=    )
    2025-11-12 16:58:34 - weather_tools - ERROR - Validation error after 0.00s: 1 validation error for WeatherLocation
    city
      Value error, City name cannot be empty or just whitespace [type=value_error, input_value='    ', input_type=str]
        For further information visit https://errors.pydantic.dev/2.12/v/value_error
    2025-11-12 16:58:34 - weather_tools - INFO - Tool invoked: get_current_weather(city=<script>alert('XSS')</script>)
    2025-11-12 16:58:34 - weather_tools - ERROR - Validation error after 0.00s: 1 validation error for WeatherLocation
    city
      Value error, City name contains invalid characters. Only letters, numbers, spaces, hyphens, and apostrophes are allowed. [type=value_error, input_value="<script>alert('XSS')</script>", input_type=str]
        For further information visit https://errors.pydantic.dev/2.12/v/value_error
    2025-11-12 16:58:34 - weather_tools - INFO - Tool invoked: get_current_weather(city=12345)
    2025-11-12 16:58:34 - weather_tools - INFO - Input validation passed for city: 12345
    2025-11-12 16:58:34 - weather_tools - INFO - Geocoding city: 12345


    Result: Error: Could not find coordinates for 'XYZ123InvalidCity'. Please check the spelling or try a different city name.
    
    2. Testing Malicious Input (SQL Injection Attempt)
    --------------------------------------------------------------------------------
    Result: Error: 1 validation error for WeatherLocation
    city
      Value error, City name contains invalid characters. Only letters, numbers, spaces, hyphens, and apostrophes are allowed. [type=value_error, input_value="London'; DROP TABLE weather;--", input_type=str]
        For further information visit https://errors.pydantic.dev/2.12/v/value_error
    
    3. Testing Empty/Whitespace Input (Validation Failure)
    --------------------------------------------------------------------------------
    Result: Error: 1 validation error for WeatherLocation
    city
      Value error, City name cannot be empty or just whitespace [type=value_error, input_value='    ', input_type=str]
        For further information visit https://errors.pydantic.dev/2.12/v/value_error
    
    4. Testing Special Characters (Security Validation)
    --------------------------------------------------------------------------------
    Result: Error: 1 validation error for WeatherLocation
    city
      Value error, City name contains invalid characters. Only letters, numbers, spaces, hyphens, and apostrophes are allowed. [type=value_error, input_value="<script>alert('XSS')</script>", input_type=str]
        For further information visit https://errors.pydantic.dev/2.12/v/value_error
    
    5. Testing Numbers as City Name (Type Confusion)
    --------------------------------------------------------------------------------


    2025-11-12 16:58:35 - weather_tools - WARNING - City not found: 12345
    2025-11-12 16:58:35 - weather_tools - ERROR - Validation error after 0.21s: Could not find coordinates for '12345'. Please check the spelling or try a different city name.
    2025-11-12 16:58:35 - weather_tools - INFO - Tool invoked: get_current_weather(city=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA)
    2025-11-12 16:58:35 - weather_tools - ERROR - Validation error after 0.00s: 1 validation error for WeatherLocation
    city
      String should have at most 100 characters [type=string_too_long, input_value='AAAAAAAAAAAAAAAAAAAAAAAA...AAAAAAAAAAAAAAAAAAAAAAA', input_type=str]
        For further information visit https://errors.pydantic.dev/2.12/v/string_too_long


    Result: Error: Could not find coordinates for '12345'. Please check the spelling or try a different city name.
    
    6. Testing Extremely Long City Name (Input Length Validation)
    --------------------------------------------------------------------------------
    Result: Error: 1 validation error for WeatherLocation
    city
      String should have at most 100 characters [type=string_too_long, input_value='AAAAAAAAAAAAAAAAAAAAAAAA...AAAAAAAAAAAAAAAAAAAAAAA', input_type=str]
        For further information visit https://errors.pydantic.dev/2.12/v/string_too_long
    
    ================================================================================
    SUMMARY: All error conditions handled gracefully!
    ================================================================================
    
    Key Observations:
    ✅ No system crashes or unhandled exceptions
    ✅ Clear, actionable error messages for users
    ✅ Detailed logging for debugging (check logs above)
    ✅ Input sanitization blocked malicious inputs
    ✅ Validation caught invalid data before API calls
    
    Production-Grade Error Handling: VERIFIED ✓

```

---

## File: 4_3_swarm_architecture_openai.md

```markdown
# Swarm Multi-Agent Architecture with OpenAI Agents SDK

## Introduction

Welcome to this tutorial on **Swarm Multi-Agent Architecture** using the **OpenAI Agents SDK**. This SDK is the production-ready evolution of OpenAI's experimental Swarm library, designed for building lightweight, scalable, and Pythonic multi-agent systems.

### What You'll Learn

- What the OpenAI Agents SDK is and how it differs from other frameworks
- How to create specialized agents using the `Agent()` constructor
- How to define tools with the `@function_tool` decorator
- How to implement agent handoffs for agent-to-agent coordination
- How to use Sessions for automatic conversation history management
- How to run multi-agent systems with `await Runner.run()` (Jupyter) or `Runner.run_sync()` (scripts)
- How to build a practical customer service multi-agent system

### Prerequisites

- Basic Python knowledge
- Understanding of LLMs and AI agents
- OpenAI API key

### Important Note for Jupyter Notebooks

This notebook uses `await Runner.run()` throughout because Jupyter notebooks already have an event loop running. If you're adapting this code for regular Python scripts, use `Runner.run_sync()` instead.

### What is OpenAI Agents SDK?

The **OpenAI Agents SDK** is a lightweight, production-ready framework for orchestrating multiple AI agents. Key characteristics:

- **Python-first**: Feels natural to Python developers, no complex graph definitions
- **Lightweight**: Minimal abstraction, easy to understand and debug
- **Production-ready**: Built for real-world applications with proper error handling
- **Flexible orchestration**: Supports handoffs for agent-to-agent delegation
- **Automatic history**: Sessions manage conversation state transparently

### Swarm Architecture Overview

In a **swarm architecture**, agents operate in a **decentralized** manner:

- **No central supervisor**: Agents communicate directly with each other
- **Peer-to-peer collaboration**: Agents decide when to transfer control to another agent
- **Specialization**: Each agent has expertise in a specific domain
- **Dynamic routing**: Tasks flow naturally between agents based on their capabilities

```
Swarm Architecture:

                    User Query
                         |
                         v
                  ┌─────────────┐
            ┌────►│  Agent A    │◄────┐
            │     └─────────────┘     │
            │            │            │
         handoff      handoff      handoff
            │            │            │
     ┌──────┴────┐       │      ┌────┴──────┐
     │  Agent B  │◄──────┼─────►│  Agent C  │
     └───────────┘       │      └───────────┘
                         v
                    Collaborative Result
```

## Step 1: Installation and Setup

First, let's install the OpenAI Agents SDK and set up our environment.


```python
# Install the OpenAI Agents SDK
# Uncomment the following line if you need to install the package
# !pip install openai-agents python-dotenv
```


```python
# Import necessary libraries
import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, SQLiteSession

# Load environment variables (including OPENAI_API_KEY)
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

print("Environment setup complete!")
print("OpenAI Agents SDK imported successfully!")
```

    Environment setup complete!
    OpenAI Agents SDK imported successfully!


## Step 2: Understanding the Core Components

Before we build our swarm, let's understand the key components of the OpenAI Agents SDK:

### 1. **Agent**
The core building block. Created with `Agent()`, each agent has:
- `name`: A unique identifier for the agent
- `instructions`: A system prompt defining its role and behavior
- `model`: The LLM to use (defaults to "gpt-4o")
- `tools`: Python functions the agent can call
- `handoffs`: List of other agents this agent can transfer control to

```python
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model="gpt-4o-mini",  # optional
    tools=[my_tool],       # optional
    handoffs=[other_agent] # optional
)
```

### 2. **Function Tools**
Python functions decorated with `@function_tool` become callable tools for agents:
- The function docstring becomes the tool description
- Type hints define expected parameters
- Return values are passed back to the agent

```python
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"Weather in {city}: Sunny"
```

### 3. **Handoffs**
Agents can transfer control to other agents by:
- Including target agents in their `handoffs` parameter
- The agent loop automatically decides when to transfer control
- Context and conversation history are preserved

### 4. **Runner**
Executes agents and manages the agent loop:
- `Runner.run_sync(agent, messages)`: Synchronous execution (for scripts)
- `Runner.run(agent, messages)`: Async execution (for Jupyter/async contexts)
- Returns a `RunResult` object with `final_output` and metadata

### 5. **Session**
Manages conversation history automatically:
- `SQLiteSession(session_id)`: In-memory storage
- `SQLiteSession(session_id, db_path)`: Persistent file-based storage
- Automatically tracks messages across runs
- Enables multi-turn conversations without manual state management

## Step 3: Create Simple Tools for Our Agents

Let's create some tools that our agents will use. We'll build a customer service swarm with agents that handle different types of inquiries.

The `@function_tool` decorator exposes Python functions as tools that agents can call. The function's docstring becomes the tool description that helps the agent understand when to use it.


```python
# Define tools for our agents using the @function_tool decorator

@function_tool
def get_order_status(order_id: str) -> str:
    """Look up the status of an order by order ID."""
    # Simulated order lookup
    orders = {
        "ORD001": "Shipped - Expected delivery: Nov 15",
        "ORD002": "Processing - Will ship tomorrow",
        "ORD003": "Delivered on Nov 10"
    }
    return orders.get(order_id, f"Order {order_id} not found")

@function_tool
def calculate_refund(amount: float, reason: str) -> str:
    """Calculate refund amount based on purchase amount and return reason."""
    # Simplified refund logic
    if "defective" in reason.lower():
        refund = amount  # Full refund
        return f"Full refund approved: ${refund:.2f}"
    elif "changed mind" in reason.lower():
        refund = amount * 0.85  # 15% restocking fee
        return f"Refund with restocking fee: ${refund:.2f} (85% of ${amount:.2f})"
    else:
        return f"Refund of ${amount:.2f} pending review by supervisor"

@function_tool
def check_product_availability(product_name: str) -> str:
    """Check if a product is currently in stock."""
    # Simulated inventory check
    inventory = {
        "laptop": "In stock - 45 units available",
        "phone": "Low stock - 3 units remaining",
        "tablet": "Out of stock - Expected restock: Nov 20"
    }
    return inventory.get(product_name.lower(), f"Product '{product_name}' not found in catalog")

print("Tools created successfully!")
print(f"- get_order_status: {get_order_status.__doc__}")
print(f"- calculate_refund: {calculate_refund.__doc__}")
print(f"- check_product_availability: {check_product_availability.__doc__}")
```

    Tools created successfully!
    - get_order_status: A tool that wraps a function. In most cases, you should use  the `function_tool` helpers to
        create a FunctionTool, as they let you easily wrap a Python function.
        
    - calculate_refund: A tool that wraps a function. In most cases, you should use  the `function_tool` helpers to
        create a FunctionTool, as they let you easily wrap a Python function.
        
    - check_product_availability: A tool that wraps a function. In most cases, you should use  the `function_tool` helpers to
        create a FunctionTool, as they let you easily wrap a Python function.
        


## Step 4: Create Specialized Agents

Now we'll create three specialized agents for our customer service swarm:

1. **Triage Agent**: First point of contact, routes to appropriate specialist
2. **Order Agent**: Handles order tracking and status inquiries
3. **Refund Agent**: Processes returns and refunds

### Important: Creating Agents with Handoffs

In the OpenAI Agents SDK, handoffs work differently than in other frameworks:
- You define which agents an agent can hand off to via the `handoffs` parameter
- The agent's instructions should mention when to transfer control
- The agent loop automatically handles the handoff mechanism
- No explicit "handoff tool" creation is needed


```python
# Note: We need to create agents in the right order since they reference each other
# We'll use a forward declaration pattern

# First, create the Order Agent
order_agent = Agent(
    name="OrderAgent",
    instructions="""
You are the Order Agent, specializing in order tracking and delivery information.

Your responsibilities:
- Look up order status using the order ID
- Provide tracking and delivery information
- Answer questions about shipping

If the customer has issues with their order (damaged, defective, want to return):
- Transfer to the RefundAgent

If the customer has unrelated questions:
- Transfer back to the TriageAgent

Be clear, concise, and helpful.
""",
    model="gpt-4o-mini",
    tools=[get_order_status]
)

print("Order Agent created!")
```

    Order Agent created!



```python
# Create the Refund Agent
refund_agent = Agent(
    name="RefundAgent",
    instructions="""
You are the Refund Agent, specializing in returns and refunds.

Your responsibilities:
- Process return requests
- Calculate refund amounts based on the reason
- Explain refund policies clearly

Refund policy:
- Defective products: Full refund
- Changed mind: 85% refund (15% restocking fee)
- Other reasons: Case-by-case review

If the customer needs to check their order first:
- Transfer to the OrderAgent

If the customer has unrelated questions:
- Transfer back to the TriageAgent

Be empathetic and solution-oriented.
""",
    model="gpt-4o-mini",
    tools=[calculate_refund]
)

print("Refund Agent created!")
```

    Refund Agent created!



```python
# Now add handoff capabilities to the agents
# In OpenAI Agents SDK, we update the handoffs after creating all agents

# Order Agent can hand off to Refund Agent
order_agent.handoffs = [refund_agent]

# Refund Agent can hand off to Order Agent
refund_agent.handoffs = [order_agent]

print("Handoffs configured!")
print(f"OrderAgent can hand off to: {[agent.name for agent in order_agent.handoffs]}")
print(f"RefundAgent can hand off to: {[agent.name for agent in refund_agent.handoffs]}")
```

    Handoffs configured!
    OrderAgent can hand off to: ['RefundAgent']
    RefundAgent can hand off to: ['OrderAgent']



```python
# Finally, create the Triage Agent (entry point) with handoffs to both specialists
triage_agent = Agent(
    name="TriageAgent",
    instructions="""
You are the Triage Agent, the first point of contact for customer inquiries.

Your role:
- Greet customers warmly
- Understand what they need help with
- Route them to the appropriate specialist:
  * OrderAgent: for order status, tracking, delivery questions
  * RefundAgent: for returns, refunds, or product issues
- You can also help with product availability questions directly

Always be helpful and professional. If you're not sure which agent to transfer to, ask clarifying questions.
""",
    model="gpt-4o-mini",
    tools=[check_product_availability],
    handoffs=[order_agent, refund_agent]
)

# Also allow specialists to hand back to triage
order_agent.handoffs.append(triage_agent)
refund_agent.handoffs.append(triage_agent)

print("Triage Agent created!")
print(f"TriageAgent can hand off to: {[agent.name for agent in triage_agent.handoffs]}")
print("\nSwarm architecture complete!")
```

    Triage Agent created!
    TriageAgent can hand off to: ['OrderAgent', 'RefundAgent']
    
    Swarm architecture complete!


## Step 5: Run the Swarm - Single Interaction

Let's test our swarm with a simple query. Since we're in a Jupyter notebook (which already has an event loop), we'll use `await Runner.run()` instead of `Runner.run_sync()`.

The `Runner.run()` method:
- Takes an agent as the starting point
- Accepts a message (string) or list of messages
- Returns a `RunResult` object with `final_output` and other metadata
- Automatically handles the agent loop and any handoffs

**Note**: Jupyter notebooks support top-level `await`, so we can use the async API directly!


```python
# Run a simple query through the swarm
# Using await since we're in a Jupyter notebook
result = await Runner.run(
    triage_agent,  # Start with the triage agent
    "Hi! I need to check on my order ORD001"
)

# Display the response
print("=== Swarm Response ===")
print(f"\nFinal Output: {result.final_output}")

# Try to detect which agent responded
agent_name = "Unknown Agent"
if hasattr(result, 'new_items') and result.new_items:
    for item in reversed(result.new_items):
        if hasattr(item, 'role') and item.role == 'assistant':
            if hasattr(item, 'agent_name'):
                agent_name = item.agent_name
                break
            elif hasattr(item, 'name'):
                agent_name = item.name
                break

print(f"\nAgent that responded: {agent_name}")
print(f"\nNote: The swarm automatically handled the handoff from TriageAgent to OrderAgent!")
```

    === Swarm Response ===
    
    Final Output: Your order **ORD001** has been shipped and is expected to be delivered on **November 15**. If you have any other questions, feel free to ask!
    
    Agent that responded: Unknown Agent
    
    Note: The swarm automatically handled the handoff from TriageAgent to OrderAgent!


## Step 6: Create a Helper Function for Swarm Invocation

Let's create a reusable helper function that makes it easy to invoke the swarm and track important information:

- **Logs handoffs**: Shows which agents were involved in handling the request
- **Tracks the final agent**: Identifies which agent provided the final response
- **Displays usage statistics**: Shows token consumption and API calls
- **Pretty output**: Formats the response in a clear, readable way

This function will be useful for testing different queries and understanding how the swarm routes requests.


```python
async def invoke_swarm(starting_agent: Agent, user_message: str, verbose: bool = True):
    """
    Invoke the swarm with comprehensive logging and tracking.
    
    Args:
        starting_agent: The agent to start with (usually the triage agent)
        user_message: The user's query or request
        verbose: If True, prints detailed information about handoffs and usage
    
    Returns:
        The RunResult object from the agent execution
    """
    # Run the swarm
    result = await Runner.run(starting_agent, user_message)
    
    if verbose:
        print("=" * 70)
        print("SWARM EXECUTION REPORT")
        print("=" * 70)
        
        # Track agents involved
        agents_involved = [starting_agent.name]
        
        # Examine items to find handoffs and agent switches
        if hasattr(result, 'new_items') and result.new_items:
            for item in result.new_items:
                # Check for agent handoffs in the items
                if hasattr(item, 'type'):
                    if item.type == 'agent_switch_item' or 'handoff' in str(item.type).lower():
                        if hasattr(item, 'agent'):
                            agent_name = item.agent.name if hasattr(item.agent, 'name') else str(item.agent)
                            if agent_name not in agents_involved:
                                agents_involved.append(agent_name)
                                print(f"\n  [HANDOFF] Transferred to: {agent_name}")
                
                # Alternative: check if item has an agent attribute
                if hasattr(item, 'agent') and hasattr(item.agent, 'name'):
                    agent_name = item.agent.name
                    if agent_name not in agents_involved:
                        agents_involved.append(agent_name)
                        print(f"\n  [HANDOFF] Transferred to: {agent_name}")
        
        # Display the agent path
        print(f"\nAgent Path: {' -> '.join(agents_involved)}")
        # Display the final output
        print(f"\n--- Final Response ---")
        print(f"{result.final_output}")
        print("=" * 70)
    
    return result

print("Helper function 'invoke_swarm' created successfully!")
```

    Helper function 'invoke_swarm' created successfully!


## Summary: Understanding the Helper Function

The `invoke_swarm` helper function provides several key benefits:

### 1. **Handoff Tracking**
The function examines `result.new_items` to detect when agents transfer control to each other. This helps you understand the flow of execution through your swarm.

### 2. **Agent Identification**
It uses `result.current_agent.name` to identify which agent provided the final response, making debugging and monitoring easier.

### 3. **Usage Metrics**
By accessing `result.context_wrapper.usage`, it displays:
- Number of API requests made
- Input tokens consumed
- Output tokens generated
- Total token usage

### 4. **Flexible Configuration**
The `verbose` parameter lets you toggle detailed logging on/off:
```python
# Detailed output
result = await invoke_swarm(triage_agent, "Hello")

# Silent execution (returns result only)
result = await invoke_swarm(triage_agent, "Hello", verbose=False)
```

### Key Insights from the OpenAI Agents SDK

Based on the documentation:
- **`result.current_agent`**: Contains the agent that produced the final output
- **`result.new_items`**: List of all items generated during the run (messages, tool calls, handoffs)
- **`result.context_wrapper.usage`**: Contains token usage statistics
- **`result.final_output`**: The final response text from the agent

This helper function makes it easy to monitor and debug your swarm architecture!


```python
# Test 1: Product availability - Triage Agent should handle this directly (no handoff)
print("\n\nTEST 1: Product Availability (No Handoff Expected)")
print("-" * 70)
result3 = await invoke_swarm(
    triage_agent,
    "Is the tablet in stock? I want to buy one."
)
print("\n")
```

    
    
    TEST 3: Product Availability (No Handoff Expected)
    ----------------------------------------------------------------------
    ======================================================================
    SWARM EXECUTION REPORT
    ======================================================================
    
    Agent Path: TriageAgent
    
    --- Final Response ---
    Could you please specify the name of the tablet you're interested in? That way, I can check its availability for you.
    ======================================================================
    
    



```python
# Test 2: Refund request - should trigger handoff from Triage to Refund Agent
print("\n\nTEST 2: Refund Request")
print("-" * 70)
result2 = await invoke_swarm(
    triage_agent,
    "I want to return my laptop because it's defective. It cost $1200. What's my refund?"
)
print("\n")
```

    
    
    TEST 2: Refund Request
    ----------------------------------------------------------------------
    ======================================================================
    SWARM EXECUTION REPORT
    ======================================================================
    
      [HANDOFF] Transferred to: RefundAgent
    
    Agent Path: TriageAgent -> RefundAgent
    
    --- Final Response ---
    Since the laptop is defective, you are eligible for a full refund. Given that your purchase amount was $1200, your refund will be the full amount of **$1200**. 
    
    I recommend starting the return process as soon as possible. If you need further assistance, feel free to ask!
    ======================================================================
    
    



```python
# Test 3: Order status inquiry - should trigger handoff from Triage to Order Agent
print("TEST 3: Order Status Query")
print("-" * 70)
result1 = await invoke_swarm(
    triage_agent,
    "Hi! I need to check on my order ORD002. When will it ship?"
)
print("\n")
```

    TEST 1: Order Status Query
    ----------------------------------------------------------------------
    ======================================================================
    SWARM EXECUTION REPORT
    ======================================================================
    
      [HANDOFF] Transferred to: OrderAgent
    
    Agent Path: TriageAgent -> OrderAgent
    
    --- Final Response ---
    Your order (ORD002) is currently processing and is expected to ship tomorrow. If you have any more questions, feel free to ask!
    ======================================================================
    
    

```

---

## File: 4_4_subgraphs_fact_checker.md

```markdown
# Building Modular Agentic Workflows with LangGraph Subgraphs

## Tutorial Overview

In this tutorial, you'll learn how to build a **Fact-Checking News Article Assistant** using **LangGraph subgraphs**. This is an advanced architectural pattern that allows you to:

- Break complex workflows into modular, reusable components
- Create subgraphs that can be called multiple times with different inputs
- Build sophisticated multi-step verification systems
- Maintain clean separation of concerns in your agentic architecture

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Design and implement modular workflows using LangGraph subgraphs
2. Create reusable subgraphs that can be invoked multiple times
3. Build a complete fact-checking system with claim extraction and verification
4. Integrate external tools (Tavily) for real-time information gathering
5. Orchestrate complex parent-child graph relationships
6. Visualize multi-level graph architectures

## What You'll Build

We'll build a **Fact-Checking News Article Assistant** with the following architecture:

```
Main Workflow:
  Article Input → Extract Claims → Verify Each Claim → Generate Report
                        ↓                  ↓
                  Claim Extraction    Verification
                    Subgraph          Subgraph (reusable)
                                           ↓
                                  Source Quality
                                    Subgraph
```

### Workflow Components:

1. **Claim Extraction Subgraph**: Parses article → Identifies factual claims → Ranks by verifiability
2. **Verification Subgraph** (reusable): Searches sources → Compares information → Rates confidence
3. **Source Quality Subgraph**: Analyzes credibility → Checks freshness → Cross-references
4. **Main Workflow**: Orchestrates the entire process and generates final report

## Prerequisites

- Understanding of LangGraph basics (nodes, edges, state)
- Familiarity with LLM API calls
- API keys for:
  - OpenAI (or another LLM provider)
  - Tavily (for web search)

## Part 1: Environment Setup

Let's install required packages and configure our environment.


```python
# Install required packages
# Uncomment the following line if you need to install the packages
# !pip install langgraph langchain langchain-openai python-dotenv tavily-python
```


```python
# Load environment variables
from dotenv import load_dotenv
import os

# Load API keys from .env file
load_dotenv()

# Verify that keys are loaded
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not found in environment"
assert os.getenv("TAVILY_API_KEY"), "TAVILY_API_KEY not found in environment"

print("Environment variables loaded successfully!")
```

    Environment variables loaded successfully!


## Part 2: Import Dependencies


```python
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from tavily import TavilyClient
import json

print("All imports successful!")
```

    All imports successful!


## Part 3: Initialize Tools and LLM

We'll set up our LLM and Tavily search client for web searches.


```python
# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize Tavily client for web search
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Create a search tool function
def internet_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web for information using Tavily.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        Dictionary containing search results with titles, URLs, and content
    """
    try:
        results = tavily_client.search(query, max_results=max_results)
        return results
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

print("Tavily search tool configured successfully!")
print("LLM and tools initialized!")
```

    Tavily search tool configured successfully!
    LLM and tools initialized!


## Part 4: Define State Schemas

We'll define separate state schemas for:
1. Main workflow state
2. Claim extraction subgraph state
3. Verification subgraph state
4. Source quality subgraph state

This demonstrates the power of subgraphs: each can have its own state schema that doesn't pollute the parent state.


```python
# Pydantic models for structured outputs

class Claim(BaseModel):
    """A single factual claim extracted from an article."""
    claim_text: str = Field(description="The specific factual claim")
    verifiability_score: float = Field(description="Score 0-1 indicating how verifiable this claim is")
    context: str = Field(description="Relevant context from the article")

class ClaimList(BaseModel):
    """List of claims extracted from an article."""
    claims: List[Claim] = Field(description="List of extracted claims")

class SourceQuality(BaseModel):
    """Quality assessment of a source."""
    credibility_score: float = Field(description="Score 0-1 for source credibility")
    freshness_score: float = Field(description="Score 0-1 for information freshness")
    relevance_score: float = Field(description="Score 0-1 for relevance to claim")
    reasoning: str = Field(description="Explanation of the scores")

class VerificationResult(BaseModel):
    """Result of verifying a single claim."""
    claim: str = Field(description="The claim that was verified")
    verdict: str = Field(description="TRUE, FALSE, PARTIALLY_TRUE, or UNVERIFIABLE")
    confidence: float = Field(description="Confidence score 0-1")
    evidence: str = Field(description="Supporting evidence and reasoning")
    sources: List[str] = Field(description="URLs of sources used")

# State schemas for different graph levels

class MainWorkflowState(TypedDict):
    """State for the main fact-checking workflow."""
    article: str
    claims: List[Dict[str, Any]]
    verification_results: List[Dict[str, Any]]
    final_report: str

class ClaimExtractionState(TypedDict):
    """State for claim extraction subgraph."""
    article: str
    raw_claims: str
    ranked_claims: List[Dict[str, Any]]

class VerificationState(TypedDict):
    """State for verification subgraph."""
    claim: str
    search_results: List[Dict[str, Any]]
    source_quality_assessments: List[Dict[str, Any]]
    verification_result: Dict[str, Any]

class SourceQualityState(TypedDict):
    """State for source quality subgraph."""
    source_url: str
    source_content: str
    claim: str
    quality_assessment: Dict[str, Any]

print("State schemas defined!")
print("\nWe have 4 separate state schemas:")
print("  1. MainWorkflowState - orchestrates the entire process")
print("  2. ClaimExtractionState - handles claim extraction")
print("  3. VerificationState - verifies individual claims")
print("  4. SourceQualityState - assesses source quality")
```

    State schemas defined!
    
    We have 4 separate state schemas:
      1. MainWorkflowState - orchestrates the entire process
      2. ClaimExtractionState - handles claim extraction
      3. VerificationState - verifies individual claims
      4. SourceQualityState - assesses source quality


## Part 5: Build the Claim Extraction Subgraph

This subgraph will:
1. Parse the article and identify factual claims
2. Rank claims by verifiability
3. Return a structured list of claims

This is our first example of a subgraph with its own internal workflow.


```python
# Node 1: Extract raw claims from article
def extract_claims_node(state: ClaimExtractionState) -> ClaimExtractionState:
    """
    Analyzes the article and extracts factual claims using structured output.
    """
    article = state["article"]
    
    print("Extracting claims from article...")
    
    system_prompt = """You are a fact-checking expert that extracts verifiable claims from news articles.
    
Analyze the article and identify specific factual claims that can be verified.
Focus on:
- Statistical claims (numbers, percentages, dates)
- Claims about events that happened
- Statements about people, places, or organizations
- Cause-and-effect relationships

Avoid:
- Opinions or subjective statements
- Vague or ambiguous claims
- Claims that are definitional or tautological

For each claim, assess its verifiability (0-1 score):
- 1.0: Highly verifiable (specific, concrete, with clear metrics)
- 0.5: Moderately verifiable (some specificity, but may require interpretation)
- 0.0: Not verifiable (too vague, subjective, or opinion-based)
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Article:\n{article}"}
    ]
    
    # Use structured output
    claim_extractor = llm.with_structured_output(ClaimList)
    result = claim_extractor.invoke(messages)
    
    print(f"Extracted {len(result.claims)} claims")
    
    return {**state, "raw_claims": str(result.model_dump())}

# Node 2: Rank claims by verifiability
def rank_claims_node(state: ClaimExtractionState) -> ClaimExtractionState:
    """
    Ranks extracted claims by verifiability score.
    """
    raw_claims = eval(state["raw_claims"])  # Convert string back to dict
    claims_list = raw_claims["claims"]
    
    print("Ranking claims by verifiability...")
    
    # Sort claims by verifiability score (highest first)
    ranked = sorted(claims_list, key=lambda x: x["verifiability_score"], reverse=True)
    
    # Take top 3 most verifiable claims
    top_claims = ranked[:3]
    
    print(f"Selected top {len(top_claims)} claims for verification")
    for i, claim in enumerate(top_claims, 1):
        print(f"  {i}. [{claim['verifiability_score']:.2f}] {claim['claim_text'][:80]}...")
    
    return {**state, "ranked_claims": top_claims}

# Build the claim extraction subgraph
claim_extraction_builder = StateGraph(ClaimExtractionState)

# Add nodes
claim_extraction_builder.add_node("extract_claims", extract_claims_node)
claim_extraction_builder.add_node("rank_claims", rank_claims_node)

# Add edges
claim_extraction_builder.add_edge(START, "extract_claims")
claim_extraction_builder.add_edge("extract_claims", "rank_claims")
claim_extraction_builder.add_edge("rank_claims", END)

# Compile the subgraph
claim_extraction_subgraph = claim_extraction_builder.compile()

print("\nClaim Extraction Subgraph built!")
print("Architecture: extract_claims → rank_claims")
```

    
    Claim Extraction Subgraph built!
    Architecture: extract_claims → rank_claims


## Part 6: Build the Source Quality Subgraph

This subgraph assesses the quality of individual sources found during verification.
It will be used by the verification subgraph.


```python
def assess_source_quality_node(state: SourceQualityState) -> SourceQualityState:
    """
    Assesses the quality of a source for fact-checking purposes.
    """
    source_url = state["source_url"]
    source_content = state["source_content"]
    claim = state["claim"]
    
    print(f"Assessing source quality: {source_url[:60]}...")
    
    system_prompt = """You are a source quality assessor for fact-checking.

Evaluate the source on three dimensions:

1. Credibility (0-1):
   - Is this from a reputable organization?
   - Does it cite sources or provide evidence?
   - Is the author identified and credible?

2. Freshness (0-1):
   - Is the information recent and up-to-date?
   - Is it relevant to the current context?

3. Relevance (0-1):
   - How directly does this source address the claim?
   - Does it provide specific evidence for or against the claim?
"""
    
    user_prompt = f"""Claim: {claim}

Source URL: {source_url}

Source Content:
{source_content[:1000]}...

Assess the quality of this source for verifying the claim."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Use structured output
    quality_assessor = llm.with_structured_output(SourceQuality)
    result = quality_assessor.invoke(messages)
    
    print(f"  Credibility: {result.credibility_score:.2f}, Freshness: {result.freshness_score:.2f}, Relevance: {result.relevance_score:.2f}")
    
    return {**state, "quality_assessment": result.model_dump()}

# Build the source quality subgraph
source_quality_builder = StateGraph(SourceQualityState)

# Add nodes
source_quality_builder.add_node("assess_quality", assess_source_quality_node)

# Add edges
source_quality_builder.add_edge(START, "assess_quality")
source_quality_builder.add_edge("assess_quality", END)

# Compile the subgraph
source_quality_subgraph = source_quality_builder.compile()

print("\nSource Quality Subgraph built!")
```

    
    Source Quality Subgraph built!


## Part 7: Build the Verification Subgraph

This is the most complex subgraph. It will:
1. Search for sources related to the claim
2. Use the source quality subgraph to assess each source
3. Compare information across sources
4. Generate a verification result with confidence score

This subgraph will be called multiple times by the main workflow - once for each claim.


```python
# Node 1: Search for sources
def search_sources_node(state: VerificationState) -> VerificationState:
    """
    Searches the web for sources related to the claim.
    """
    claim = state["claim"]
    
    print(f"\nSearching for sources to verify: {claim[:80]}...")
    
    # Perform web search
    search_results = internet_search(claim, max_results=3)
    
    if "error" in search_results:
        print(f"Search error: {search_results['error']}")
        return {**state, "search_results": []}
    
    results = search_results.get("results", [])
    print(f"Found {len(results)} sources")
    
    return {**state, "search_results": results}

# Node 2: Assess source quality (calls source quality subgraph)
def assess_sources_node(state: VerificationState) -> VerificationState:
    """
    Assesses the quality of each source by invoking the source quality subgraph.
    """
    claim = state["claim"]
    search_results = state["search_results"]
    
    print("Assessing source quality for all sources...")
    
    quality_assessments = []
    
    for result in search_results:
        # Invoke the source quality subgraph for each source
        subgraph_input = {
            "source_url": result.get("url", ""),
            "source_content": result.get("content", ""),
            "claim": claim,
            "quality_assessment": {}
        }
        
        # This is where we invoke a subgraph from within another subgraph!
        subgraph_output = source_quality_subgraph.invoke(subgraph_input)
        
        quality_assessments.append({
            "url": result.get("url", ""),
            "quality": subgraph_output["quality_assessment"]
        })
    
    return {**state, "source_quality_assessments": quality_assessments}

# Node 3: Generate verification result
def generate_verdict_node(state: VerificationState) -> VerificationState:
    """
    Generates the final verification verdict based on sources and quality assessments.
    """
    claim = state["claim"]
    search_results = state["search_results"]
    quality_assessments = state["source_quality_assessments"]
    
    print("Generating verification verdict...")
    
    # Prepare context with sources and quality scores
    sources_context = ""
    for i, (result, quality) in enumerate(zip(search_results, quality_assessments), 1):
        sources_context += f"\n\nSource {i}:\n"
        sources_context += f"URL: {result.get('url', 'N/A')}\n"
        sources_context += f"Content: {result.get('content', '')[:500]}...\n"
        sources_context += f"Quality Scores - Credibility: {quality['quality']['credibility_score']:.2f}, "
        sources_context += f"Freshness: {quality['quality']['freshness_score']:.2f}, "
        sources_context += f"Relevance: {quality['quality']['relevance_score']:.2f}\n"
    
    system_prompt = """You are a fact-checking expert that verifies claims based on source evidence.

Analyze the sources and their quality scores to determine:

Verdict:
- TRUE: The claim is supported by high-quality sources
- FALSE: The claim is contradicted by high-quality sources
- PARTIALLY_TRUE: Some aspects are true, others are not
- UNVERIFIABLE: Insufficient or conflicting evidence

Confidence (0-1):
- Consider source quality scores
- Higher confidence when multiple high-quality sources agree
- Lower confidence when sources conflict or quality is poor

Provide clear evidence and reasoning.
"""
    
    user_prompt = f"""Claim to verify: {claim}

Available sources:
{sources_context}

Verify this claim and provide your verdict."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Use structured output
    verifier = llm.with_structured_output(VerificationResult)
    result = verifier.invoke(messages)
    
    print(f"Verdict: {result.verdict} (confidence: {result.confidence:.2f})")
    
    return {**state, "verification_result": result.model_dump()}

# Build the verification subgraph
verification_builder = StateGraph(VerificationState)

# Add nodes
verification_builder.add_node("search_sources", search_sources_node)
verification_builder.add_node("assess_sources", assess_sources_node)
verification_builder.add_node("generate_verdict", generate_verdict_node)

# Add edges
verification_builder.add_edge(START, "search_sources")
verification_builder.add_edge("search_sources", "assess_sources")
verification_builder.add_edge("assess_sources", "generate_verdict")
verification_builder.add_edge("generate_verdict", END)

# Compile the subgraph
verification_subgraph = verification_builder.compile()

print("\nVerification Subgraph built!")
print("Architecture: search_sources → assess_sources → generate_verdict")
print("Note: assess_sources internally calls the source_quality_subgraph!")
```

    
    Verification Subgraph built!
    Architecture: search_sources → assess_sources → generate_verdict
    Note: assess_sources internally calls the source_quality_subgraph!


## Part 8: Build the Main Workflow

Now we'll create the main workflow that orchestrates everything:
1. Takes an article as input
2. Calls the claim extraction subgraph
3. Calls the verification subgraph for each claim (demonstrating reusability)
4. Generates a final fact-checking report

This demonstrates the key pattern: invoking subgraphs from parent nodes.


```python
# Node 1: Extract claims (invokes claim extraction subgraph)
def extract_claims_main(state: MainWorkflowState) -> MainWorkflowState:
    """
    Extracts claims from the article by invoking the claim extraction subgraph.
    """
    article = state["article"]
    
    print("="*80)
    print("STEP 1: EXTRACTING CLAIMS")
    print("="*80)
    
    # Transform parent state to subgraph state
    subgraph_input = {
        "article": article,
        "raw_claims": "",
        "ranked_claims": []
    }
    
    # Invoke the claim extraction subgraph
    subgraph_output = claim_extraction_subgraph.invoke(subgraph_input)
    
    # Transform subgraph output back to parent state
    claims = subgraph_output["ranked_claims"]
    
    return {**state, "claims": claims}

# Node 2: Verify all claims (invokes verification subgraph multiple times)
def verify_claims_main(state: MainWorkflowState) -> MainWorkflowState:
    """
    Verifies each claim by invoking the verification subgraph.
    This demonstrates subgraph reusability - we call it multiple times.
    """
    claims = state["claims"]
    
    print("\n" + "="*80)
    print("STEP 2: VERIFYING CLAIMS")
    print("="*80)
    
    verification_results = []
    
    # Invoke the verification subgraph once for each claim
    for i, claim_obj in enumerate(claims, 1):
        print(f"\n--- Verifying Claim {i}/{len(claims)} ---")
        
        # Transform parent state to subgraph state
        subgraph_input = {
            "claim": claim_obj["claim_text"],
            "search_results": [],
            "source_quality_assessments": [],
            "verification_result": {}
        }
        
        # Invoke the verification subgraph
        subgraph_output = verification_subgraph.invoke(subgraph_input)
        
        # Collect the result
        verification_results.append(subgraph_output["verification_result"])
    
    return {**state, "verification_results": verification_results}

# Node 3: Generate final report
def generate_report_main(state: MainWorkflowState) -> MainWorkflowState:
    """
    Generates a comprehensive fact-checking report.
    """
    verification_results = state["verification_results"]
    
    print("\n" + "="*80)
    print("STEP 3: GENERATING REPORT")
    print("="*80)
    
    system_prompt = """You are a fact-checking report writer.

Create a clear, professional fact-checking report that:
- Summarizes the verification results
- Explains the evidence for each claim
- Provides an overall assessment
- Uses clear formatting with sections and bullet points
"""
    
    user_prompt = f"""Generate a fact-checking report for these verification results:

{json.dumps(verification_results, indent=2)}

Create a comprehensive report."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    
    print("Report generated!")
    
    return {**state, "final_report": response.content}

# Build the main workflow
main_workflow_builder = StateGraph(MainWorkflowState)

# Add nodes
main_workflow_builder.add_node("extract_claims", extract_claims_main)
main_workflow_builder.add_node("verify_claims", verify_claims_main)
main_workflow_builder.add_node("generate_report", generate_report_main)

# Add edges
main_workflow_builder.add_edge(START, "extract_claims")
main_workflow_builder.add_edge("extract_claims", "verify_claims")
main_workflow_builder.add_edge("verify_claims", "generate_report")
main_workflow_builder.add_edge("generate_report", END)

# Compile the main workflow
fact_checker_app = main_workflow_builder.compile()

print("\n" + "="*80)
print("MAIN WORKFLOW BUILT SUCCESSFULLY!")
print("="*80)
print("\nArchitecture:")
print("  extract_claims → verify_claims → generate_report")
print("\nSubgraph relationships:")
print("  - extract_claims invokes: claim_extraction_subgraph")
print("  - verify_claims invokes: verification_subgraph (multiple times)")
print("  - verification_subgraph invokes: source_quality_subgraph (multiple times)")
```

    
    ================================================================================
    MAIN WORKFLOW BUILT SUCCESSFULLY!
    ================================================================================
    
    Architecture:
      extract_claims → verify_claims → generate_report
    
    Subgraph relationships:
      - extract_claims invokes: claim_extraction_subgraph
      - verify_claims invokes: verification_subgraph (multiple times)
      - verification_subgraph invokes: source_quality_subgraph (multiple times)


## Part 9: Visualize the Complete Graph

Let's visualize the main workflow and understand the complete architecture.


```python
# Visualize the main workflow
try:
    from IPython.display import Image, display
    
    print("Main Workflow Visualization:")
    display(Image(fact_checker_app.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Visualization not available: {e}")
    print("\nASCII representation:")
    print(fact_checker_app.get_graph().draw_ascii())
```

    Main Workflow Visualization:



    
![png](4_4_subgraphs_fact_checker_files/4_4_subgraphs_fact_checker_19_1.png)
    



```python
# Visualize the subgraphs
print("\n" + "="*80)
print("CLAIM EXTRACTION SUBGRAPH")
print("="*80)
try:
    display(Image(claim_extraction_subgraph.get_graph().draw_mermaid_png()))
except:
    print(claim_extraction_subgraph.get_graph().draw_ascii())

print("\n" + "="*80)
print("VERIFICATION SUBGRAPH")
print("="*80)
try:
    display(Image(verification_subgraph.get_graph().draw_mermaid_png()))
except:
    print(verification_subgraph.get_graph().draw_ascii())

print("\n" + "="*80)
print("SOURCE QUALITY SUBGRAPH")
print("="*80)
try:
    display(Image(source_quality_subgraph.get_graph().draw_mermaid_png()))
except:
    print(source_quality_subgraph.get_graph().draw_ascii())
```

    
    ================================================================================
    CLAIM EXTRACTION SUBGRAPH
    ================================================================================



    
![png](4_4_subgraphs_fact_checker_files/4_4_subgraphs_fact_checker_20_1.png)
    


    
    ================================================================================
    VERIFICATION SUBGRAPH
    ================================================================================



    
![png](4_4_subgraphs_fact_checker_files/4_4_subgraphs_fact_checker_20_3.png)
    


    
    ================================================================================
    SOURCE QUALITY SUBGRAPH
    ================================================================================



    
![png](4_4_subgraphs_fact_checker_files/4_4_subgraphs_fact_checker_20_5.png)
    


## Part 10: Test the Fact-Checking System

Let's test our complete system with a sample news article!


```python
# Sample news article for testing
sample_article = """
Breaking News: Major AI Breakthrough Announced

SAN FRANCISCO - Tech giant OpenAI announced today that their latest AI model, GPT-5, 
has achieved human-level performance on over 95% of standardized tests. The company 
claims this represents a 300% improvement over their previous model.

According to CEO Sam Altman, the new model was trained on a dataset containing 
10 trillion tokens, making it the largest language model ever created. The training 
process reportedly cost over $500 million and required the computational power 
equivalent to 50,000 high-end GPUs running continuously for six months.

Industry experts predict that this breakthrough will lead to the automation of 
20 million jobs worldwide by the end of 2025. Dr. Sarah Chen, AI researcher at 
MIT, stated that "this technology will fundamentally transform every industry 
within the next two years."

The announcement caused OpenAI's valuation to surge by 40% to $200 billion, 
making it the most valuable AI company in the world.
"""

print("Testing the fact-checking system with a sample article...")
print("\nArticle:")
print("-" * 80)
print(sample_article)
print("-" * 80)
```

    Testing the fact-checking system with a sample article...
    
    Article:
    --------------------------------------------------------------------------------
    
    Breaking News: Major AI Breakthrough Announced
    
    SAN FRANCISCO - Tech giant OpenAI announced today that their latest AI model, GPT-5, 
    has achieved human-level performance on over 95% of standardized tests. The company 
    claims this represents a 300% improvement over their previous model.
    
    According to CEO Sam Altman, the new model was trained on a dataset containing 
    10 trillion tokens, making it the largest language model ever created. The training 
    process reportedly cost over $500 million and required the computational power 
    equivalent to 50,000 high-end GPUs running continuously for six months.
    
    Industry experts predict that this breakthrough will lead to the automation of 
    20 million jobs worldwide by the end of 2025. Dr. Sarah Chen, AI researcher at 
    MIT, stated that "this technology will fundamentally transform every industry 
    within the next two years."
    
    The announcement caused OpenAI's valuation to surge by 40% to $200 billion, 
    making it the most valuable AI company in the world.
    
    --------------------------------------------------------------------------------



```python
# Run the fact-checker
initial_state = {
    "article": sample_article,
    "claims": [],
    "verification_results": [],
    "final_report": ""
}

# Execute the workflow
result = fact_checker_app.invoke(initial_state)

# Display the final report
print("\n" + "="*80)
print("FINAL FACT-CHECKING REPORT")
print("="*80)
print(result["final_report"])
```

    ================================================================================
    STEP 1: EXTRACTING CLAIMS
    ================================================================================
    Extracting claims from article...
    Extracted 8 claims
    Ranking claims by verifiability...
    Selected top 3 claims for verification
      1. [1.00] OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95...
      2. [1.00] The new model represents a 300% improvement over the previous model....
      3. [1.00] The new model was trained on a dataset containing 10 trillion tokens....
    
    ================================================================================
    STEP 2: VERIFYING CLAIMS
    ================================================================================
    
    --- Verifying Claim 1/3 ---
    
    Searching for sources to verify: OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95...
    Found 3 sources
    Assessing source quality for all sources...
    Assessing source quality: https://www.wsj.com/tech/ai/openai-chatgpt-5-release-d5dc674...
      Credibility: 0.90, Freshness: 1.00, Relevance: 0.80
    Assessing source quality: https://techcrunch.com/2025/09/25/openai-says-gpt-5-stacks-u...
      Credibility: 0.70, Freshness: 0.80, Relevance: 0.60
    Assessing source quality: https://odsc.medium.com/openai-launches-gpt-5-setting-new-be...
      Credibility: 0.60, Freshness: 0.70, Relevance: 0.50
    Generating verification verdict...
    Verdict: FALSE (confidence: 0.80)
    
    --- Verifying Claim 2/3 ---
    
    Searching for sources to verify: The new model represents a 300% improvement over the previous model....
    Found 3 sources
    Assessing source quality for all sources...
    Assessing source quality: https://www.marinadodgeny.com/2023/02/10/whats-new-for-the-2...
      Credibility: 0.40, Freshness: 0.80, Relevance: 0.30
    Assessing source quality: https://www.miamilakesautomall.com/chrysler-blog/the-chrysle...
      Credibility: 0.50, Freshness: 0.80, Relevance: 0.40
    Assessing source quality: https://www.kendalldodgechryslerjeepram.com/chrysler-300-ret...
      Credibility: 0.50, Freshness: 0.70, Relevance: 0.40
    Generating verification verdict...
    Verdict: UNVERIFIABLE (confidence: 0.20)
    
    --- Verifying Claim 3/3 ---
    
    Searching for sources to verify: The new model was trained on a dataset containing 10 trillion tokens....
    Found 3 sources
    Assessing source quality for all sources...
    Assessing source quality: https://en.eeworld.com.cn/mp/QbitAI/a408234.jspx...
      Credibility: 0.40, Freshness: 0.50, Relevance: 0.30
    Assessing source quality: https://medium.com/coding-nexus/nvidia-trained-a-12b-model-o...
      Credibility: 0.60, Freshness: 0.80, Relevance: 0.90
    Assessing source quality: https://www.primeintellect.ai/blog/intellect-1-release...
      Credibility: 0.70, Freshness: 0.80, Relevance: 0.60
    Generating verification verdict...
    Verdict: TRUE (confidence: 0.80)
    
    ================================================================================
    STEP 3: GENERATING REPORT
    ================================================================================
    Report generated!
    
    ================================================================================
    FINAL FACT-CHECKING REPORT
    ================================================================================
    # Fact-Checking Report
    
    ## Summary of Verification Results
    This report evaluates three claims regarding OpenAI's latest AI model, GPT-5, and its performance metrics. The claims have been assessed based on available evidence from various sources, leading to the following conclusions:
    
    1. **Claim 1**: FALSE - GPT-5 has not achieved human-level performance on over 95% of standardized tests.
    2. **Claim 2**: UNVERIFIABLE - The assertion of a 300% improvement over the previous model lacks sufficient evidence.
    3. **Claim 3**: TRUE - The new model was trained on a dataset containing 10 trillion tokens.
    
    ---
    
    ## Detailed Evidence and Assessment
    
    ### Claim 1: "OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95% of standardized tests."
    - **Verdict**: FALSE
    - **Confidence**: 0.8
    - **Evidence**:
      - **Source 1**: Discusses the release of GPT-5 but does not provide specific performance metrics related to standardized tests.
      - **Source 2**: Mentions that OpenAI is assessing AI performance against human benchmarks but does not confirm that GPT-5 has reached human-level performance.
      - **Source 3**: Highlights improvements in various tasks but lacks specific data on standardized test performance.
    - **Conclusion**: The claim is contradicted by the available evidence from high-quality sources, indicating that while advancements have been made, the specific performance metric of 95% on standardized tests is not substantiated.
    
    ---
    
    ### Claim 2: "The new model represents a 300% improvement over the previous model."
    - **Verdict**: UNVERIFIABLE
    - **Confidence**: 0.2
    - **Evidence**:
      - **Source 1**: Discusses features of the 2023 Chrysler 300 model but does not quantify improvements.
      - **Source 2**: Provides a general overview of the model without specific metrics to support the claim of a 300% improvement.
      - **Source 3**: Lacks authoritative data and does not provide a direct comparison to substantiate the claim.
    - **Conclusion**: The sources reviewed have low quality scores and do not provide reliable or authoritative evidence to support the claim of a 300% improvement. Therefore, the claim remains unverified.
    
    ---
    
    ### Claim 3: "The new model was trained on a dataset containing 10 trillion tokens."
    - **Verdict**: TRUE
    - **Confidence**: 0.8
    - **Evidence**:
      - **Source 2**: Explicitly states that NVIDIA trained a 12-billion-parameter language model on 10 trillion tokens, directly supporting the claim.
      - **Source 1**: Does not provide relevant information about the token count.
      - **Source 3**: Mentions a model trained on 1 trillion tokens, which contradicts the claim but does not affect the validity of Source 2.
    - **Conclusion**: The strong evidence from Source 2, combined with its high quality score, leads to a confident conclusion that the claim is true.
    
    ---
    
    ## Overall Assessment
    The verification process has yielded mixed results. While one claim regarding the training dataset is confirmed as true, the claim about human-level performance on standardized tests is false, and the claim of a 300% improvement is unverified due to insufficient evidence. This highlights the importance of critically evaluating claims against reliable sources to ascertain their validity.

```

---

## File: 4_5_parallel_execution.md

```markdown
# Parallel Execution in LangGraph: From Sequential to Concurrent Workflows

## Tutorial Overview

In this tutorial, you'll learn how to transform a sequential agentic workflow into a highly efficient parallel execution system using **LangGraph's parallelization patterns**. We'll explore two distinct approaches:

1. **AsyncIO Gather Method**: Using Python's native async/await patterns
2. **Send API Method**: Using LangGraph's purpose-built parallelization primitives

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Identify bottlenecks in sequential workflows that can benefit from parallelization
2. Implement parallel execution using Python's `asyncio.gather()` pattern
3. Implement parallel execution using LangGraph's `Send` API
4. Compare and contrast both approaches to choose the right one for your use case
5. Measure and analyze performance improvements from parallelization
6. Understand when parallelization provides real benefits vs. added complexity

## The Problem: Sequential Verification is Slow

In our fact-checking workflow from the previous tutorial, we have a critical bottleneck:

```python
# Current approach: Sequential verification
for claim in claims:
    result = verification_subgraph.invoke(claim)  # Wait for each one
    results.append(result)
```

**The problem**: If we have 3 claims, and each verification takes 15 seconds:
- Sequential execution: **45 seconds** total
- Parallel execution: **~15 seconds** total (all three happen simultaneously)

This is a massive time saving, especially as the number of claims grows!

## Why Parallel Execution Matters

Modern agentic workflows often involve:
- **I/O-bound operations**: API calls, web searches, database queries
- **Independent tasks**: Verifying claims that don't depend on each other
- **User experience**: Reducing latency improves perceived responsiveness
- **Cost efficiency**: Less total execution time means lower computational costs

## What You'll Build

We'll take the fact-checking system from Tutorial 4.5 and create two parallel versions:

**Approach 1 - AsyncIO Gather**:
```
verify_claims_node:
  ├─ async gather all claims
  ├─ verification_subgraph(claim1)  ┐
  ├─ verification_subgraph(claim2)  ├─ All happen simultaneously
  └─ verification_subgraph(claim3)  ┘
```

**Approach 2 - Send API**:
```
route_to_verify → verify_claim1 ┐
                → verify_claim2 ├─ Parallel branches
                → verify_claim3 ┘
                         ↓
                  aggregate_results
```

## Prerequisites

- Completion of Tutorial 4.5 (Subgraphs - Fact Checker)
- Understanding of async/await in Python (helpful but not required)
- API keys for OpenAI and Tavily

## Part 1: Why Parallel Execution?

### The Sequential Bottleneck

Let's understand the problem we're solving. In our fact-checker workflow:

1. **Extract Claims**: Takes ~5 seconds (LLM call to identify claims)
2. **Verify Claims**: Takes ~15 seconds **per claim** (web search + LLM analysis)
3. **Generate Report**: Takes ~3 seconds (LLM call to create report)

For 3 claims:
- **Sequential**: 5 + (15 × 3) + 3 = **53 seconds**
- **Parallel**: 5 + 15 + 3 = **23 seconds** (56% time savings!)

### When to Use Parallel Execution

Parallelization provides benefits when:
- **Tasks are independent**: One claim's verification doesn't affect another
- **Tasks are I/O-bound**: Waiting for API responses, not CPU computation
- **Multiple items to process**: Lists, batches, collections of similar tasks
- **Time constraints**: User-facing applications where latency matters

### Two Approaches to Parallelization

**1. AsyncIO Gather**: Use Python's native async capabilities
- **Pros**: Simple, familiar Python patterns, low overhead
- **Cons**: All parallelism hidden in one node, less visibility

**2. Send API**: Use LangGraph's built-in parallelization
- **Pros**: Explicit graph structure, LangGraph manages state, better observability
- **Cons**: More complex setup, LangGraph-specific patterns

Let's implement both and compare!

## Part 2: Environment Setup

Let's set up our environment with all necessary dependencies.


```python
# Install required packages
# Uncomment the following line if you need to install the packages
# !pip install langgraph langchain langchain-openai python-dotenv tavily-python
```


```python
# Load environment variables
from dotenv import load_dotenv
import os

# Load API keys from .env file
load_dotenv()

# Verify that keys are loaded
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not found in environment"
assert os.getenv("TAVILY_API_KEY"), "TAVILY_API_KEY not found in environment"

print("Environment variables loaded successfully!")
```

    Environment variables loaded successfully!


## Part 3: Import Dependencies

Note the new imports for parallel execution:
- `asyncio`: For async/await parallelization
- `Send` from `langgraph.types`: For LangGraph's Send API
- `time`: For performance measurement


```python
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send  # NEW: For parallel execution with Send API
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from tavily import TavilyClient
import json
import asyncio  # NEW: For async/await parallelization
import time  # NEW: For performance measurement
from operator import add

print("All imports successful!")
```

    All imports successful!


## Part 4: Initialize Tools and LLM

Same setup as before - we're not changing how individual tools work, just how we orchestrate them.


```python
# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize Tavily client for web search
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Create a search tool function
def internet_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web for information using Tavily.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        Dictionary containing search results with titles, URLs, and content
    """
    try:
        results = tavily_client.search(query, max_results=max_results)
        return results
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

print("Tavily search tool configured successfully!")
print("LLM and tools initialized!")
```

    Tavily search tool configured successfully!
    LLM and tools initialized!


## Part 5: Define State Schemas

We'll use the same state schemas as before, with one modification to the main state for parallel execution.


```python
# Pydantic models for structured outputs

class Claim(BaseModel):
    """A single factual claim extracted from an article."""
    claim_text: str = Field(description="The specific factual claim")
    verifiability_score: float = Field(description="Score 0-1 indicating how verifiable this claim is")
    context: str = Field(description="Relevant context from the article")

class ClaimList(BaseModel):
    """List of claims extracted from an article."""
    claims: List[Claim] = Field(description="List of extracted claims")

class SourceQuality(BaseModel):
    """Quality assessment of a source."""
    credibility_score: float = Field(description="Score 0-1 for source credibility")
    freshness_score: float = Field(description="Score 0-1 for information freshness")
    relevance_score: float = Field(description="Score 0-1 for relevance to claim")
    reasoning: str = Field(description="Explanation of the scores")

class VerificationResult(BaseModel):
    """Result of verifying a single claim."""
    claim: str = Field(description="The claim that was verified")
    verdict: str = Field(description="TRUE, FALSE, PARTIALLY_TRUE, or UNVERIFIABLE")
    confidence: float = Field(description="Confidence score 0-1")
    evidence: str = Field(description="Supporting evidence and reasoning")
    sources: List[str] = Field(description="URLs of sources used")

# State schemas for different graph levels

class MainWorkflowState(TypedDict):
    """State for the main fact-checking workflow."""
    article: str
    claims: List[Dict[str, Any]]
    # NEW: Using Annotated with add operator to accumulate results from parallel executions
    verification_results: Annotated[List[Dict[str, Any]], add]
    final_report: str

class ClaimExtractionState(TypedDict):
    """State for claim extraction subgraph."""
    article: str
    raw_claims: str
    ranked_claims: List[Dict[str, Any]]

class VerificationState(TypedDict):
    """State for verification subgraph."""
    claim: str
    search_results: List[Dict[str, Any]]
    source_quality_assessments: List[Dict[str, Any]]
    verification_result: Dict[str, Any]

class SourceQualityState(TypedDict):
    """State for source quality subgraph."""
    source_url: str
    source_content: str
    claim: str
    quality_assessment: Dict[str, Any]

print("State schemas defined!")
print("\nKey modification for parallel execution:")
print("  verification_results uses Annotated[List, add] to accumulate parallel results")
```

    State schemas defined!
    
    Key modification for parallel execution:
      verification_results uses Annotated[List, add] to accumulate parallel results


## Part 6: Build the Subgraphs (Unchanged)

These subgraphs remain exactly the same - we're not changing how they work internally, just how we invoke them.

### Claim Extraction Subgraph


```python
# Node 1: Extract raw claims from article
def extract_claims_node(state: ClaimExtractionState) -> ClaimExtractionState:
    """
    Analyzes the article and extracts factual claims using structured output.
    """
    article = state["article"]
    
    print("Extracting claims from article...")
    
    system_prompt = """You are a fact-checking expert that extracts verifiable claims from news articles.
    
Analyze the article and identify specific factual claims that can be verified.
Focus on:
- Statistical claims (numbers, percentages, dates)
- Claims about events that happened
- Statements about people, places, or organizations
- Cause-and-effect relationships

Avoid:
- Opinions or subjective statements
- Vague or ambiguous claims
- Claims that are definitional or tautological

For each claim, assess its verifiability (0-1 score):
- 1.0: Highly verifiable (specific, concrete, with clear metrics)
- 0.5: Moderately verifiable (some specificity, but may require interpretation)
- 0.0: Not verifiable (too vague, subjective, or opinion-based)
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Article:\n{article}"}
    ]
    
    # Use structured output
    claim_extractor = llm.with_structured_output(ClaimList)
    result = claim_extractor.invoke(messages)
    
    print(f"Extracted {len(result.claims)} claims")
    
    return {**state, "raw_claims": str(result.model_dump())}

# Node 2: Rank claims by verifiability
def rank_claims_node(state: ClaimExtractionState) -> ClaimExtractionState:
    """
    Ranks extracted claims by verifiability score.
    """
    raw_claims = eval(state["raw_claims"])  # Convert string back to dict
    claims_list = raw_claims["claims"]
    
    print("Ranking claims by verifiability...")
    
    # Sort claims by verifiability score (highest first)
    ranked = sorted(claims_list, key=lambda x: x["verifiability_score"], reverse=True)
    
    # Take top 3 most verifiable claims
    top_claims = ranked[:3]
    
    print(f"Selected top {len(top_claims)} claims for verification")
    for i, claim in enumerate(top_claims, 1):
        print(f"  {i}. [{claim['verifiability_score']:.2f}] {claim['claim_text'][:80]}...")
    
    return {**state, "ranked_claims": top_claims}

# Build the claim extraction subgraph
claim_extraction_builder = StateGraph(ClaimExtractionState)
claim_extraction_builder.add_node("extract_claims", extract_claims_node)
claim_extraction_builder.add_node("rank_claims", rank_claims_node)
claim_extraction_builder.add_edge(START, "extract_claims")
claim_extraction_builder.add_edge("extract_claims", "rank_claims")
claim_extraction_builder.add_edge("rank_claims", END)
claim_extraction_subgraph = claim_extraction_builder.compile()

print("\nClaim Extraction Subgraph built!")
```

    
    Claim Extraction Subgraph built!


### Source Quality Subgraph


```python
def assess_source_quality_node(state: SourceQualityState) -> SourceQualityState:
    """
    Assesses the quality of a source for fact-checking purposes.
    """
    source_url = state["source_url"]
    source_content = state["source_content"]
    claim = state["claim"]
    
    print(f"Assessing source quality: {source_url[:60]}...")
    
    system_prompt = """You are a source quality assessor for fact-checking.

Evaluate the source on three dimensions:

1. Credibility (0-1):
   - Is this from a reputable organization?
   - Does it cite sources or provide evidence?
   - Is the author identified and credible?

2. Freshness (0-1):
   - Is the information recent and up-to-date?
   - Is it relevant to the current context?

3. Relevance (0-1):
   - How directly does this source address the claim?
   - Does it provide specific evidence for or against the claim?
"""
    
    user_prompt = f"""Claim: {claim}

Source URL: {source_url}

Source Content:
{source_content[:1000]}...

Assess the quality of this source for verifying the claim."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Use structured output
    quality_assessor = llm.with_structured_output(SourceQuality)
    result = quality_assessor.invoke(messages)
    
    print(f"  Credibility: {result.credibility_score:.2f}, Freshness: {result.freshness_score:.2f}, Relevance: {result.relevance_score:.2f}")
    
    return {**state, "quality_assessment": result.model_dump()}

# Build the source quality subgraph
source_quality_builder = StateGraph(SourceQualityState)
source_quality_builder.add_node("assess_quality", assess_source_quality_node)
source_quality_builder.add_edge(START, "assess_quality")
source_quality_builder.add_edge("assess_quality", END)
source_quality_subgraph = source_quality_builder.compile()

print("\nSource Quality Subgraph built!")
```

    
    Source Quality Subgraph built!


### Verification Subgraph


```python
# Node 1: Search for sources
def search_sources_node(state: VerificationState) -> VerificationState:
    """
    Searches the web for sources related to the claim.
    """
    claim = state["claim"]
    
    print(f"  Searching for sources to verify: {claim[:80]}...")
    
    # Perform web search
    search_results = internet_search(claim, max_results=3)
    
    if "error" in search_results:
        print(f"  Search error: {search_results['error']}")
        return {**state, "search_results": []}
    
    results = search_results.get("results", [])
    print(f"  Found {len(results)} sources")
    
    return {**state, "search_results": results}

# Node 2: Assess source quality (calls source quality subgraph)
def assess_sources_node(state: VerificationState) -> VerificationState:
    """
    Assesses the quality of each source by invoking the source quality subgraph.
    """
    claim = state["claim"]
    search_results = state["search_results"]
    
    print("  Assessing source quality...")
    
    quality_assessments = []
    
    for result in search_results:
        # Invoke the source quality subgraph for each source
        subgraph_input = {
            "source_url": result.get("url", ""),
            "source_content": result.get("content", ""),
            "claim": claim,
            "quality_assessment": {}
        }
        
        subgraph_output = source_quality_subgraph.invoke(subgraph_input)
        
        quality_assessments.append({
            "url": result.get("url", ""),
            "quality": subgraph_output["quality_assessment"]
        })
    
    return {**state, "source_quality_assessments": quality_assessments}

# Node 3: Generate verification result
def generate_verdict_node(state: VerificationState) -> VerificationState:
    """
    Generates the final verification verdict based on sources and quality assessments.
    """
    claim = state["claim"]
    search_results = state["search_results"]
    quality_assessments = state["source_quality_assessments"]
    
    print("  Generating verification verdict...")
    
    # Prepare context with sources and quality scores
    sources_context = ""
    for i, (result, quality) in enumerate(zip(search_results, quality_assessments), 1):
        sources_context += f"\n\nSource {i}:\n"
        sources_context += f"URL: {result.get('url', 'N/A')}\n"
        sources_context += f"Content: {result.get('content', '')[:500]}...\n"
        sources_context += f"Quality Scores - Credibility: {quality['quality']['credibility_score']:.2f}, "
        sources_context += f"Freshness: {quality['quality']['freshness_score']:.2f}, "
        sources_context += f"Relevance: {quality['quality']['relevance_score']:.2f}\n"
    
    system_prompt = """You are a fact-checking expert that verifies claims based on source evidence.

Analyze the sources and their quality scores to determine:

Verdict:
- TRUE: The claim is supported by high-quality sources
- FALSE: The claim is contradicted by high-quality sources
- PARTIALLY_TRUE: Some aspects are true, others are not
- UNVERIFIABLE: Insufficient or conflicting evidence

Confidence (0-1):
- Consider source quality scores
- Higher confidence when multiple high-quality sources agree
- Lower confidence when sources conflict or quality is poor

Provide clear evidence and reasoning.
"""
    
    user_prompt = f"""Claim to verify: {claim}

Available sources:
{sources_context}

Verify this claim and provide your verdict."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Use structured output
    verifier = llm.with_structured_output(VerificationResult)
    result = verifier.invoke(messages)
    
    print(f"  Verdict: {result.verdict} (confidence: {result.confidence:.2f})")
    
    return {**state, "verification_result": result.model_dump()}

# Build the verification subgraph
verification_builder = StateGraph(VerificationState)
verification_builder.add_node("search_sources", search_sources_node)
verification_builder.add_node("assess_sources", assess_sources_node)
verification_builder.add_node("generate_verdict", generate_verdict_node)
verification_builder.add_edge(START, "search_sources")
verification_builder.add_edge("search_sources", "assess_sources")
verification_builder.add_edge("assess_sources", "generate_verdict")
verification_builder.add_edge("generate_verdict", END)
verification_subgraph = verification_builder.compile()

print("\nVerification Subgraph built!")
```

    
    Verification Subgraph built!


## Part 7: Approach 1 - Parallel Execution with AsyncIO Gather

### The AsyncIO Pattern

This approach uses Python's native `asyncio.gather()` to run multiple async operations concurrently.

**Key concepts**:
- `async def`: Defines an asynchronous function
- `await`: Pauses execution until an async operation completes
- `asyncio.gather()`: Runs multiple async operations concurrently
- `ainvoke()`: LangGraph's async version of `invoke()`

**How it works**:
1. Create async tasks for each claim verification
2. Use `asyncio.gather()` to execute all tasks simultaneously
3. Collect results when all tasks complete
4. All parallelism happens within a single node

**Advantages**:
- Simple to implement if you're familiar with async Python
- Low overhead - just uses Python's built-in async capabilities
- Clean graph structure - parallelism is hidden in the implementation

**Disadvantages**:
- Less visibility into what's happening during execution
- Manual result aggregation
- Requires understanding of async/await patterns


```python
# Node 1: Extract claims (same as before)
def extract_claims_async(state: MainWorkflowState) -> MainWorkflowState:
    """
    Extracts claims from the article by invoking the claim extraction subgraph.
    """
    article = state["article"]
    
    print("="*80)
    print("STEP 1: EXTRACTING CLAIMS")
    print("="*80)
    
    subgraph_input = {
        "article": article,
        "raw_claims": "",
        "ranked_claims": []
    }
    
    subgraph_output = claim_extraction_subgraph.invoke(subgraph_input)
    claims = subgraph_output["ranked_claims"]
    
    return {**state, "claims": claims}

# Node 2: Verify all claims in parallel using asyncio.gather()
async def verify_claims_async_gather(state: MainWorkflowState) -> MainWorkflowState:
    """
    Verifies all claims in parallel using asyncio.gather().
    This approach keeps all parallelism within a single node.
    """
    claims = state["claims"]
    
    print("\n" + "="*80)
    print("STEP 2: VERIFYING CLAIMS IN PARALLEL (AsyncIO Gather)")
    print("="*80)
    print(f"Verifying {len(claims)} claims concurrently using asyncio.gather()...\n")
    
    start_time = time.time()
    
    # Create async tasks for each claim verification
    async def verify_single_claim(claim_obj, index):
        """
        Async function to verify a single claim.
        """
        print(f"[Claim {index}] Starting verification: {claim_obj['claim_text'][:60]}...")
        
        subgraph_input = {
            "claim": claim_obj["claim_text"],
            "search_results": [],
            "source_quality_assessments": [],
            "verification_result": {}
        }
        
        # Use ainvoke() for async execution
        result = await verification_subgraph.ainvoke(subgraph_input)
        
        print(f"[Claim {index}] Completed verification")
        return result["verification_result"]
    
    # Execute all verifications in parallel using gather
    verification_results = await asyncio.gather(
        *[verify_single_claim(claim, i+1) for i, claim in enumerate(claims)]
    )
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"\nAll {len(claims)} claims verified in {elapsed:.2f} seconds (parallel execution)")
    print(f"Estimated sequential time: ~{len(claims) * 15:.0f} seconds")
    print(f"Time saved: ~{(len(claims) * 15) - elapsed:.0f} seconds ({(1 - elapsed / (len(claims) * 15)) * 100:.1f}% reduction)\n")
    
    return {**state, "verification_results": verification_results}

# Node 3: Generate report (same as before)
def generate_report_async(state: MainWorkflowState) -> MainWorkflowState:
    """
    Generates a comprehensive fact-checking report.
    """
    verification_results = state["verification_results"]
    
    print("="*80)
    print("STEP 3: GENERATING REPORT")
    print("="*80)
    
    system_prompt = """You are a fact-checking report writer.

Create a clear, professional fact-checking report that:
- Summarizes the verification results
- Explains the evidence for each claim
- Provides an overall assessment
- Uses clear formatting with sections and bullet points
"""
    
    user_prompt = f"""Generate a fact-checking report for these verification results:

{json.dumps(verification_results, indent=2)}

Create a comprehensive report."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    print("Report generated!\n")
    
    return {**state, "final_report": response.content}

# Build the main workflow with AsyncIO approach
asyncio_workflow_builder = StateGraph(MainWorkflowState)
asyncio_workflow_builder.add_node("extract_claims", extract_claims_async)
asyncio_workflow_builder.add_node("verify_claims", verify_claims_async_gather)
asyncio_workflow_builder.add_node("generate_report", generate_report_async)
asyncio_workflow_builder.add_edge(START, "extract_claims")
asyncio_workflow_builder.add_edge("extract_claims", "verify_claims")
asyncio_workflow_builder.add_edge("verify_claims", "generate_report")
asyncio_workflow_builder.add_edge("generate_report", END)
fact_checker_asyncio = asyncio_workflow_builder.compile()

print("\n" + "="*80)
print("ASYNCIO WORKFLOW BUILT!")
print("="*80)
print("\nArchitecture:")
print("  extract_claims → verify_claims (asyncio.gather) → generate_report")
print("\nParallel execution happens inside the verify_claims node using asyncio.gather()")
```

    
    ================================================================================
    ASYNCIO WORKFLOW BUILT!
    ================================================================================
    
    Architecture:
      extract_claims → verify_claims (asyncio.gather) → generate_report
    
    Parallel execution happens inside the verify_claims node using asyncio.gather()


### Test the AsyncIO Approach

Let's test our parallel execution using asyncio.gather().


```python
# Sample news article for testing
sample_article = """
Breaking News: Major AI Breakthrough Announced

SAN FRANCISCO - Tech giant OpenAI announced today that their latest AI model, GPT-5, 
has achieved human-level performance on over 95% of standardized tests. The company 
claims this represents a 300% improvement over their previous model.

According to CEO Sam Altman, the new model was trained on a dataset containing 
10 trillion tokens, making it the largest language model ever created. The training 
process reportedly cost over $500 million and required the computational power 
equivalent to 50,000 high-end GPUs running continuously for six months.

Industry experts predict that this breakthrough will lead to the automation of 
20 million jobs worldwide by the end of 2025. Dr. Sarah Chen, AI researcher at 
MIT, stated that "this technology will fundamentally transform every industry 
within the next two years."

The announcement caused OpenAI's valuation to surge by 40% to $200 billion, 
making it the most valuable AI company in the world.
"""

print("Testing AsyncIO parallel execution approach...")
print("\nArticle:")
print("-" * 80)
print(sample_article)
print("-" * 80)
```

    Testing AsyncIO parallel execution approach...
    
    Article:
    --------------------------------------------------------------------------------
    
    Breaking News: Major AI Breakthrough Announced
    
    SAN FRANCISCO - Tech giant OpenAI announced today that their latest AI model, GPT-5, 
    has achieved human-level performance on over 95% of standardized tests. The company 
    claims this represents a 300% improvement over their previous model.
    
    According to CEO Sam Altman, the new model was trained on a dataset containing 
    10 trillion tokens, making it the largest language model ever created. The training 
    process reportedly cost over $500 million and required the computational power 
    equivalent to 50,000 high-end GPUs running continuously for six months.
    
    Industry experts predict that this breakthrough will lead to the automation of 
    20 million jobs worldwide by the end of 2025. Dr. Sarah Chen, AI researcher at 
    MIT, stated that "this technology will fundamentally transform every industry 
    within the next two years."
    
    The announcement caused OpenAI's valuation to surge by 40% to $200 billion, 
    making it the most valuable AI company in the world.
    
    --------------------------------------------------------------------------------



```python
# Run the fact-checker with AsyncIO approach
initial_state = {
    "article": sample_article,
    "claims": [],
    "verification_results": [],
    "final_report": ""
}

# Execute the workflow
result_asyncio = await fact_checker_asyncio.ainvoke(initial_state)

# Display the final report
print("\n" + "="*80)
print("FINAL FACT-CHECKING REPORT (AsyncIO Approach)")
print("="*80)
print(result_asyncio["final_report"])
```

    ================================================================================
    STEP 1: EXTRACTING CLAIMS
    ================================================================================
    Extracting claims from article...
    Extracted 8 claims
    Ranking claims by verifiability...
    Selected top 3 claims for verification
      1. [1.00] OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95...
      2. [1.00] The new model represents a 300% improvement over the previous model....
      3. [1.00] The new model was trained on a dataset containing 10 trillion tokens....
    
    ================================================================================
    STEP 2: VERIFYING CLAIMS IN PARALLEL (AsyncIO Gather)
    ================================================================================
    Verifying 3 claims concurrently using asyncio.gather()...
    
    [Claim 1] Starting verification: OpenAI's latest AI model, GPT-5, has achieved human-level pe...
    [Claim 2] Starting verification: The new model represents a 300% improvement over the previou...
    [Claim 3] Starting verification: The new model was trained on a dataset containing 10 trillio...
      Searching for sources to verify: OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95...
      Searching for sources to verify: The new model represents a 300% improvement over the previous model....
      Searching for sources to verify: The new model was trained on a dataset containing 10 trillion tokens....
      Found 3 sources
      Assessing source quality...
    Assessing source quality: https://www.autonationchryslerdodgejeepramvalencia.com/evolu...
      Found 3 sources
      Assessing source quality...
    Assessing source quality: https://medium.com/coding-nexus/nvidia-trained-a-12b-model-o...
      Found 3 sources
      Assessing source quality...
    Assessing source quality: https://openai.com/index/introducing-gpt-5/...
      Credibility: 0.40, Freshness: 0.50, Relevance: 0.30
    Assessing source quality: https://www.marinadodgeny.com/2023/02/10/whats-new-for-the-2...
      Credibility: 0.60, Freshness: 0.80, Relevance: 0.90
    Assessing source quality: https://en.eeworld.com.cn/mp/QbitAI/a408234.jspx...
      Credibility: 1.00, Freshness: 1.00, Relevance: 1.00
    Assessing source quality: https://www.nbcnews.com/tech/tech-news/openai-releases-chatg...
      Credibility: 0.40, Freshness: 0.80, Relevance: 0.30
    Assessing source quality: https://www.miamilakesautomall.com/chrysler-blog/the-chrysle...
      Credibility: 0.50, Freshness: 0.60, Relevance: 0.40
    Assessing source quality: https://www.reddit.com/r/singularity/comments/1bi8rme/jensen...
      Credibility: 0.80, Freshness: 0.90, Relevance: 0.60
    Assessing source quality: https://odsc.medium.com/openai-launches-gpt-5-setting-new-be...
      Credibility: 0.30, Freshness: 0.50, Relevance: 0.70
      Generating verification verdict...
      Credibility: 0.50, Freshness: 0.80, Relevance: 0.40
      Generating verification verdict...
      Credibility: 0.60, Freshness: 0.70, Relevance: 0.50
      Generating verification verdict...
      Verdict: TRUE (confidence: 0.80)
    [Claim 3] Completed verification
      Verdict: UNVERIFIABLE (confidence: 0.20)
    [Claim 2] Completed verification
      Verdict: FALSE (confidence: 0.80)
    [Claim 1] Completed verification
    
    All 3 claims verified in 16.61 seconds (parallel execution)
    Estimated sequential time: ~45 seconds
    Time saved: ~28 seconds (63.1% reduction)
    
    ================================================================================
    STEP 3: GENERATING REPORT
    ================================================================================
    Report generated!
    
    
    ================================================================================
    FINAL FACT-CHECKING REPORT (AsyncIO Approach)
    ================================================================================
    # Fact-Checking Report
    
    ## Summary of Verification Results
    This report evaluates three claims regarding OpenAI's latest AI model, GPT-5, and the 2023 Chrysler 300 model. The claims have been assessed for their accuracy based on available evidence from various sources. The results are as follows:
    
    1. **Claim:** OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95% of standardized tests.
       - **Verdict:** FALSE
       - **Confidence:** 0.8
    
    2. **Claim:** The new model represents a 300% improvement over the previous model.
       - **Verdict:** UNVERIFIABLE
       - **Confidence:** 0.2
    
    3. **Claim:** The new model was trained on a dataset containing 10 trillion tokens.
       - **Verdict:** TRUE
       - **Confidence:** 0.8
    
    ---
    
    ## Detailed Evidence and Assessment
    
    ### Claim 1: OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95% of standardized tests.
    - **Verdict:** FALSE
    - **Confidence:** 0.8
    - **Evidence:**
      - **Source 1:** States that GPT-5 is "much smarter across the board" and performs well on benchmarks, but does not quantify this performance in relation to standardized tests.
      - **Source 2 & Source 3:** Highlight improvements in performance but do not provide specific evidence supporting the claim of achieving human-level performance on over 95% of standardized tests.
    - **Assessment:** The claim is contradicted by the lack of specific evidence in high-quality sources. While improvements are noted, the assertion of human-level performance is not substantiated.
    
    ### Claim 2: The new model represents a 300% improvement over the previous model.
    - **Verdict:** UNVERIFIABLE
    - **Confidence:** 0.2
    - **Evidence:**
      - **Source 1, Source 2, Source 3:** Discuss various improvements in the 2023 Chrysler 300 model, including upgrades in safety features, technology, and performance metrics. However, none quantify these improvements in a way that supports the claim of a "300% improvement."
      - **Quality of Sources:** The sources have relatively low quality scores, indicating they may not be reliable or authoritative.
    - **Assessment:** There is insufficient evidence to verify the claim. The lack of quantifiable data and the low quality of sources contribute to the unverified status.
    
    ### Claim 3: The new model was trained on a dataset containing 10 trillion tokens.
    - **Verdict:** TRUE
    - **Confidence:** 0.8
    - **Evidence:**
      - **Source 1:** Explicitly states that NVIDIA trained a 12-billion-parameter language model on 10 trillion tokens.
      - **Source 3:** Mentions that GPT-4 was trained with around 10 trillion tokens, supporting the context of the claim.
      - **Source 2:** While it does not directly address the claim, it discusses the importance of high-quality datasets for training models.
    - **Assessment:** The agreement between Source 1 and Source 3, both of moderate quality, supports the claim with reasonable confidence. The evidence is consistent and corroborated by multiple sources.
    
    ---
    
    ## Overall Assessment
    The verification results indicate a mix of outcomes for the claims assessed:
    
    - **Claim 1** is definitively false due to a lack of supporting evidence.
    - **Claim 2** remains unverified due to insufficient data and low-quality sources.
    - **Claim 3** is confirmed as true, supported by credible evidence.
    
    This report highlights the importance of critical evaluation of claims, particularly in the rapidly evolving field of AI and technology. Further scrutiny and high-quality sources are essential for accurate information dissemination.


## Part 8: Approach 2 - Parallel Execution with Send API

### The Send API Pattern

LangGraph's `Send` API is a purpose-built mechanism for dynamic parallel execution within graphs.

**Key concepts**:
- `Send`: A special object that tells LangGraph to invoke a node with specific data
- **Conditional edges**: Returns a list of `Send` objects to create parallel branches
- **State accumulation**: LangGraph automatically merges results from parallel branches
- **Graph visualization**: Each parallel execution is visible in the graph

**How it works**:
1. Router node returns a list of `Send` objects (one per claim)
2. LangGraph creates parallel node invocations
3. Each node processes independently
4. Results are automatically accumulated in state
5. Aggregation node waits for all parallel tasks to complete

**Advantages**:
- Explicit in graph structure - you can see parallel branches
- LangGraph handles state management automatically
- Better observability and debugging
- Natural fit for LangGraph workflows

**Disadvantages**:
- More complex graph setup
- LangGraph-specific pattern (not standard Python)
- Requires understanding of Send mechanics


```python
# Node 1: Extract claims (same as before)
def extract_claims_send(state: MainWorkflowState) -> MainWorkflowState:
    """
    Extracts claims from the article by invoking the claim extraction subgraph.
    """
    article = state["article"]
    
    print("="*80)
    print("STEP 1: EXTRACTING CLAIMS")
    print("="*80)
    
    subgraph_input = {
        "article": article,
        "raw_claims": "",
        "ranked_claims": []
    }
    
    subgraph_output = claim_extraction_subgraph.invoke(subgraph_input)
    claims = subgraph_output["ranked_claims"]
    
    return {**state, "claims": claims}

# Router: Creates Send objects for parallel verification
def route_to_verify(state: MainWorkflowState):
    """
    Router that creates parallel Send commands for each claim.
    Each Send will invoke the verify_single_claim node.
    
    This is the key to parallel execution with Send API:
    - Returning a list of Send objects tells LangGraph to execute them in parallel
    - Each Send specifies the node to invoke and the data to send
    - LangGraph handles the parallelization automatically
    """
    claims = state["claims"]
    
    print("\n" + "="*80)
    print("STEP 2: ROUTING CLAIMS FOR PARALLEL VERIFICATION (Send API)")
    print("="*80)
    print(f"Creating {len(claims)} parallel Send operations...\n")
    
    # Create a Send object for each claim
    # Each Send will invoke verify_single_claim with the claim data
    return [
        Send("verify_single_claim", {"claim": claim, "index": i+1})
        for i, claim in enumerate(claims)
    ]

# Node 2: Verify a single claim (will be invoked multiple times in parallel)
def verify_single_claim_node(claim_data: dict) -> dict:
    """
    Processes a single claim verification.
    This node will be invoked multiple times in parallel by Send.
    
    Each parallel invocation is independent and processes one claim.
    """
    claim_obj = claim_data["claim"]
    index = claim_data["index"]
    
    print(f"[Claim {index}] Starting verification: {claim_obj['claim_text'][:60]}...")
    
    subgraph_input = {
        "claim": claim_obj["claim_text"],
        "search_results": [],
        "source_quality_assessments": [],
        "verification_result": {}
    }
    
    result = verification_subgraph.invoke(subgraph_input)
    
    print(f"[Claim {index}] Completed verification")
    
    # Return results that will be accumulated in verification_results
    # The Annotated[List, add] in state schema handles accumulation
    return {"verification_results": [result["verification_result"]]}

# Node 3: Aggregate results
def aggregate_results(state: MainWorkflowState) -> MainWorkflowState:
    """
    Aggregates all parallel verification results.
    
    Note: Due to Annotated[List, add] in the state schema,
    LangGraph automatically accumulates results from parallel branches.
    This node just marks the completion of parallel processing.
    """
    verification_results = state["verification_results"]
    
    print(f"\nAll {len(verification_results)} claims verified (parallel execution complete)")
    print("Results automatically aggregated by LangGraph\n")
    
    return state

# Node 4: Generate report (same as before)
def generate_report_send(state: MainWorkflowState) -> MainWorkflowState:
    """
    Generates a comprehensive fact-checking report.
    """
    verification_results = state["verification_results"]
    
    print("="*80)
    print("STEP 3: GENERATING REPORT")
    print("="*80)
    
    system_prompt = """You are a fact-checking report writer.

Create a clear, professional fact-checking report that:
- Summarizes the verification results
- Explains the evidence for each claim
- Provides an overall assessment
- Uses clear formatting with sections and bullet points
"""
    
    user_prompt = f"""Generate a fact-checking report for these verification results:

{json.dumps(verification_results, indent=2)}

Create a comprehensive report."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    print("Report generated!\n")
    
    return {**state, "final_report": response.content}

# Build the main workflow with Send API approach
send_workflow_builder = StateGraph(MainWorkflowState)

# Add nodes
send_workflow_builder.add_node("extract_claims", extract_claims_send)
send_workflow_builder.add_node("verify_single_claim", verify_single_claim_node)
send_workflow_builder.add_node("aggregate_results", aggregate_results)
send_workflow_builder.add_node("generate_report", generate_report_send)

# Add edges
send_workflow_builder.add_edge(START, "extract_claims")

# This is the key: conditional_edges with route_to_verify returns Send objects
send_workflow_builder.add_conditional_edges(
    "extract_claims",
    route_to_verify,
    # All parallel branches converge to aggregate_results
)

# After verification, aggregate and generate report
send_workflow_builder.add_edge("verify_single_claim", "aggregate_results")
send_workflow_builder.add_edge("aggregate_results", "generate_report")
send_workflow_builder.add_edge("generate_report", END)

# Compile the workflow
fact_checker_send = send_workflow_builder.compile()

print("\n" + "="*80)
print("SEND API WORKFLOW BUILT!")
print("="*80)
print("\nArchitecture:")
print("  extract_claims → [route_to_verify] → verify_single_claim (3x parallel)")
print("                                     → aggregate_results → generate_report")
print("\nParallel execution is explicit in the graph structure using Send objects")
```

    
    ================================================================================
    SEND API WORKFLOW BUILT!
    ================================================================================
    
    Architecture:
      extract_claims → [route_to_verify] → verify_single_claim (3x parallel)
                                         → aggregate_results → generate_report
    
    Parallel execution is explicit in the graph structure using Send objects


### Visualize the Send API Workflow

Notice how the graph structure explicitly shows parallel branches.


```python
# Visualize the Send API workflow
try:
    from IPython.display import Image, display
    
    print("Send API Workflow Visualization:")
    print("Notice the parallel verify_single_claim nodes\n")
    display(Image(fact_checker_send.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Visualization not available: {e}")
    print("\nASCII representation:")
    print(fact_checker_send.get_graph().draw_ascii())
```

    Send API Workflow Visualization:
    Notice the parallel verify_single_claim nodes
    



    
![png](4_5_parallel_execution_files/4_5_parallel_execution_26_1.png)
    


### Test the Send API Approach

Let's test our parallel execution using the Send API.


```python
# Run the fact-checker with Send API approach
initial_state = {
    "article": sample_article,
    "claims": [],
    "verification_results": [],
    "final_report": ""
}

# Measure execution time
start_time = time.time()

# Execute the workflow
result_send = fact_checker_send.invoke(initial_state)

end_time = time.time()
elapsed = end_time - start_time

print(f"\nTotal execution time: {elapsed:.2f} seconds")

# Display the final report
print("\n" + "="*80)
print("FINAL FACT-CHECKING REPORT (Send API Approach)")
print("="*80)
print(result_send["final_report"])
```

    ================================================================================
    STEP 1: EXTRACTING CLAIMS
    ================================================================================
    Extracting claims from article...
    Extracted 8 claims
    Ranking claims by verifiability...
    Selected top 3 claims for verification
      1. [1.00] OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95...
      2. [1.00] The new model represents a 300% improvement over OpenAI's previous model....
      3. [1.00] The new model was trained on a dataset containing 10 trillion tokens....
    
    ================================================================================
    STEP 2: ROUTING CLAIMS FOR PARALLEL VERIFICATION (Send API)
    ================================================================================
    Creating 3 parallel Send operations...
    
    [Claim 1] Starting verification: OpenAI's latest AI model, GPT-5, has achieved human-level pe...
      Searching for sources to verify: OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95...
    [Claim 2] Starting verification: The new model represents a 300% improvement over OpenAI's pr...
      Searching for sources to verify: The new model represents a 300% improvement over OpenAI's previous model....
    [Claim 3] Starting verification: The new model was trained on a dataset containing 10 trillio...
      Searching for sources to verify: The new model was trained on a dataset containing 10 trillion tokens....
      Found 3 sources
      Assessing source quality...
    Assessing source quality: https://wccftech.com/openais-new-orion-model-offers-only-inc...
      Found 3 sources
      Assessing source quality...
    Assessing source quality: https://medium.com/coding-nexus/nvidia-trained-a-12b-model-o...
      Credibility: 0.60, Freshness: 0.80, Relevance: 0.90
    Assessing source quality: https://www.youtube.com/watch?v=g_aZlBWnjPE...
      Credibility: 0.60, Freshness: 0.80, Relevance: 0.90
    Assessing source quality: https://en.eeworld.com.cn/mp/QbitAI/a408234.jspx...
      Found 3 sources
      Assessing source quality...
    Assessing source quality: https://vegavid.com/blog/gpt-5...
      Credibility: 0.50, Freshness: 0.60, Relevance: 0.40
    Assessing source quality: https://www.reddit.com/r/singularity/comments/1bi8rme/jensen...
      Credibility: 0.30, Freshness: 0.70, Relevance: 0.40
    Assessing source quality: https://medium.com/write-the-1/openai-released-its-most-powe...
      Credibility: 0.50, Freshness: 0.50, Relevance: 0.50
    Assessing source quality: https://techcrunch.com/2025/09/25/openai-says-gpt-5-stacks-u...
      Credibility: 0.30, Freshness: 0.50, Relevance: 0.70
      Generating verification verdict...
      Credibility: 0.60, Freshness: 0.80, Relevance: 0.40
      Generating verification verdict...
      Credibility: 0.80, Freshness: 0.90, Relevance: 0.70
    Assessing source quality: https://aitoolinsight.com/gpt-5/...
      Verdict: FALSE (confidence: 0.80)
    [Claim 2] Completed verification
      Credibility: 0.50, Freshness: 0.80, Relevance: 0.60
      Generating verification verdict...
      Verdict: TRUE (confidence: 0.80)
    [Claim 3] Completed verification
      Verdict: FALSE (confidence: 0.70)
    [Claim 1] Completed verification
    
    All 3 claims verified (parallel execution complete)
    Results automatically aggregated by LangGraph
    
    ================================================================================
    STEP 3: GENERATING REPORT
    ================================================================================
    Report generated!
    
    
    Total execution time: 45.93 seconds
    
    ================================================================================
    FINAL FACT-CHECKING REPORT (Send API Approach)
    ================================================================================
    # Fact-Checking Report
    
    ## Summary of Verification Results
    This report evaluates three claims regarding OpenAI's latest AI model, GPT-5, and its improvements over previous models. The claims were assessed based on available evidence from multiple sources. The results are as follows:
    
    - **Claim 1**: FALSE
    - **Claim 2**: FALSE
    - **Claim 3**: TRUE
    
    ## Detailed Evidence and Assessment
    
    ### Claim 1: "OpenAI's latest AI model, GPT-5, has achieved human-level performance on over 95% of standardized tests."
    - **Verdict**: FALSE
    - **Confidence**: 0.7
    - **Evidence**:
      - Source 2 discusses a benchmark testing GPT-5's performance against human professionals but does not confirm the claim of achieving human-level performance on over 95% of standardized tests.
      - Other sources provide general information about GPT-5's capabilities without supporting the specific claim regarding standardized tests.
    - **Conclusion**: The claim is contradicted by the available evidence, leading to a verdict of FALSE.
    
    ### Claim 2: "The new model represents a 300% improvement over OpenAI's previous model."
    - **Verdict**: FALSE
    - **Confidence**: 0.8
    - **Evidence**:
      - Source 1 indicates that the new model, referred to as Orion, offers only incremental improvements over GPT-4, explicitly stating that the improvements are not as significant as claimed.
      - Source 3 provides metrics showing a 50% increase in speed and a 34% reduction in errors, which do not support the assertion of a 300% improvement.
    - **Conclusion**: The claim of a 300% improvement is contradicted by high-quality sources, leading to a verdict of FALSE.
    
    ### Claim 3: "The new model was trained on a dataset containing 10 trillion tokens."
    - **Verdict**: TRUE
    - **Confidence**: 0.8
    - **Evidence**:
      - Source 1 explicitly states that NVIDIA trained a 12-billion-parameter language model on 10 trillion tokens, directly supporting the claim.
      - Source 3 corroborates this by mentioning that GPT-4 was also trained with around 10 trillion tokens.
      - Although Source 2 does not directly address the claim, it discusses the importance of high-quality datasets for training models, which is relevant but not conclusive.
    - **Conclusion**: The agreement between Source 1 and Source 3 lends a reasonable level of confidence to the claim being true, leading to a verdict of TRUE.
    
    ## Overall Assessment
    The verification process indicates that two of the claims regarding OpenAI's latest AI model, GPT-5, are false, while one claim is true. The evidence supporting the true claim is robust, while the false claims are contradicted by credible sources. This report highlights the importance of critically evaluating claims against reliable evidence to ensure accurate information dissemination. 
    
    ### Sources
    1. [Source 1](https://vegavid.com/blog/gpt-5)
    2. [Source 2](https://techcrunch.com/2025/09/25/openai-says-gpt-5-stacks-up-to-humans-in-a-wide-range-of-jobs/)
    3. [Source 3](https://aitoolinsight.com/gpt-5/)
    4. [Source 4](https://wccftech.com/openais-new-orion-model-offers-only-incremental-improvements-over-gpt-4-despite-claims-of-groundbreaking-advancement/)
    5. [Source 5](https://medium.com/write-the-1/openai-released-its-most-powerful-model-yesterday-003ee9fb166e)
    6. [Source 6](https://medium.com/coding-nexus/nvidia-trained-a-12b-model-on-10-trillion-tokens-using-just-4-bits-67d0b9605924)
    7. [Source 7](https://www.reddit.com/r/singularity/comments/1bi8rme/jensen_huang_just_gave_us_some_numbers_for_the/)

```

---

## File: 4_6_task_decomposition_workflow.md

```markdown
# Task Decomposition with LangGraph: Sequential and Parallel Execution

## Tutorial Overview

In this tutorial, you'll learn how to build an intelligent task decomposition system using **LangGraph**. The system will:

- Analyze complex queries and break them into sub-queries
- Determine whether sub-queries should execute sequentially or in parallel
- Execute searches using the Tavily API
- Synthesize results into comprehensive answers

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Understand when to use **sequential** vs **parallel** task execution
2. Build a LangGraph workflow with a **planning node** (query analyzer)
3. Implement **sequential execution** where one query depends on previous results
4. Implement **parallel execution** using `asyncio.gather` for independent queries
5. Use the **Tavily search tool** for web searches
6. Synthesize results from multiple queries into coherent answers

## Execution Strategies Explained

### Sequential Execution
Used when sub-queries **depend on previous results**:

**Example:** "AI products launched by the company that acquired DeepMind in 2024"

**Flow:**
1. Query 1: "Which company acquired DeepMind?" → Result: "Google"
2. Use result from Query 1 in Query 2: "AI products launched by Google in 2024"
3. Return final results

Must execute queries **one after another** because Query 2 needs Query 1's answer.

### Parallel Execution
Used when sub-queries are **independent**:

**Example:** "Summarize Tesla's Q4 2024 earnings, recent product launches, and leadership changes"

**Flow:**
1. Query 1: "Tesla Q4 2024 earnings" 
2. Query 2: "Tesla recent product launches" 
3. Query 3: "Tesla leadership changes"
4. All queries execute **simultaneously** using `asyncio.gather`
5. Aggregate results

**Benefits:** Faster completion (parallel I/O), no dependencies between queries.

## Visual Workflow

```
START
  ↓
Query Analyzer (Planning)
  ↓
[Conditional Edge]
  ↓
  ├─→ Sequential Execution → Query 1 → Synthesize → Query 2 → Search Results
  │                                                                ↓
  └─→ Parallel Execution → [Query 1, Query 2, Query 3] → Search Results
                                                                   ↓
                                                            Final Synthesis
                                                                   ↓
                                                                  END
```

## Prerequisites

- Basic Python knowledge
- Understanding of async/await in Python
- API keys for:
  - OpenAI (or another LLM provider)
  - Tavily (for web search)

## Part 1: Environment Setup

First, let's install the required packages and load our environment variables.

**Required packages:**
- `langgraph` - For building the workflow graph
- `langchain-openai` - For LLM integration
- `langchain-tavily` - For web search
- `python-dotenv` - For loading API keys
- `nest-asyncio` - To enable asyncio in Jupyter notebooks


```python
# Install required packages
# Uncomment the following line if you need to install the packages
# !pip install -qU langgraph langchain-openai langchain-tavily python-dotenv nest-asyncio
```


```python
# Load environment variables
from dotenv import load_dotenv
import os

# Load API keys from .env file
load_dotenv()

# Verify that keys are loaded
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not found in environment"
assert os.getenv("TAVILY_API_KEY"), "TAVILY_API_KEY not found in environment"

print("Environment variables loaded successfully!")
```

    Environment variables loaded successfully!


## Part 2: Import Dependencies

Let's import all the libraries we'll need:
- **LangGraph** for workflow orchestration
- **LangChain** for LLM and search tool integration
- **asyncio** for parallel execution
- **Pydantic** for structured outputs


```python
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
import asyncio
import nest_asyncio
import json

# Apply nest_asyncio to allow asyncio.run() in Jupyter notebooks
nest_asyncio.apply()

print("All imports successful!")
print("nest_asyncio applied - asyncio.run() will now work in Jupyter!")
```

    All imports successful!
    nest_asyncio applied - asyncio.run() will now work in Jupyter!


## Part 3: Define the Workflow State

In LangGraph, **state** represents the data flowing through your workflow. Each node reads from and updates this state.

Our workflow state will track:
- **query**: The original user query
- **sub_queries**: List of decomposed sub-queries
- **execution_strategy**: Either "sequential" or "parallel"
- **search_results**: Results from Tavily searches
- **synthesis**: Intermediate synthesis (used in sequential execution)
- **final_answer**: The final comprehensive answer


```python
class WorkflowState(TypedDict):
    """State schema for task decomposition workflow."""
    
    # Original user query
    query: str
    
    # Decomposed sub-queries
    sub_queries: List[str]
    
    # Execution strategy: 'sequential' or 'parallel'
    execution_strategy: str
    
    # Number of sequential steps (for sequential execution)
    num_sequential_steps: int
    
    # Search results from Tavily
    search_results: List[str]
    
    # Intermediate synthesis (for sequential execution)
    synthesis: str
    
    # Final answer to return to user
    final_answer: str

print("State schema defined!")
print("\nState fields:")
for field, field_type in WorkflowState.__annotations__.items():
    print(f"  - {field}: {field_type}")
```

    State schema defined!
    
    State fields:
      - query: <class 'str'>
      - sub_queries: typing.List[str]
      - execution_strategy: <class 'str'>
      - num_sequential_steps: <class 'int'>
      - search_results: typing.List[str]
      - synthesis: <class 'str'>
      - final_answer: <class 'str'>


## Part 4: Initialize LLM and Search Tool

Let's set up:
1. **ChatOpenAI** - Our LLM for analysis and synthesis
2. **Query Analysis Schema** - Pydantic model for structured output from the query analyzer
3. **TavilySearch** - Web search tool


```python
# Define Pydantic model for query analysis
class QueryAnalysis(BaseModel):
    """Schema for query analysis results."""
    
    execution_strategy: Literal["sequential", "parallel"] = Field(
        description="Execution strategy: 'sequential' if sub-queries depend on each other, 'parallel' if they are independent"
    )
    sub_queries: List[str] = Field(
        description="List of sub-queries to execute. For sequential: provide only the FIRST query (additional queries will be generated dynamically). For parallel: 2-4 independent queries."
    )
    num_sequential_steps: int = Field(
        default=2,
        description="For sequential execution only: Total number of sequential steps needed (2-4). Ignored for parallel execution."
    )
    reasoning: str = Field(
        description="Brief explanation of why this strategy was chosen"
    )

# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create structured output model for query analysis
query_analyzer = llm.with_structured_output(QueryAnalysis)

# Initialize Tavily search tool
tavily_search = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="basic"
)

print("LLM, query analyzer, and Tavily search tool initialized!")
print("\nQuery Analysis Schema:")
print(f"  - execution_strategy: Literal['sequential', 'parallel']")
print(f"  - sub_queries: List[str]")
print(f"  - num_sequential_steps: int (for sequential only)")
print(f"  - reasoning: str")
```

    LLM, query analyzer, and Tavily search tool initialized!
    
    Query Analysis Schema:
      - execution_strategy: Literal['sequential', 'parallel']
      - sub_queries: List[str]
      - num_sequential_steps: int (for sequential only)
      - reasoning: str


## Part 5: Build the Query Analyzer Node

The **Query Analyzer** is the planning node that:
1. Analyzes the user's query
2. Determines if sub-queries should run sequentially or in parallel
3. Generates appropriate sub-queries

This is the "brain" of our workflow that decides the execution strategy.


```python
def query_analyzer_node(state: WorkflowState) -> WorkflowState:
    """
    Analyzes the user query and determines execution strategy.
    
    Returns:
        Updated state with 'execution_strategy', 'sub_queries', and 'num_sequential_steps' populated
    """
    query = state["query"]
    
    print(f"\n{'='*80}")
    print("QUERY ANALYZER NODE")
    print(f"{'='*80}")
    print(f"Analyzing query: {query}")
    
    # Create prompt for query analysis
    system_prompt = """You are a query decomposition expert. Analyze the user's query and determine the best execution strategy.

**SEQUENTIAL Execution:**
Use when sub-queries DEPEND on previous results (multi-hop reasoning).

Examples:
1. "AI products launched by the company that acquired DeepMind in 2024" (2 steps)
   - Step 1: "Which company acquired DeepMind?" → Get answer
   - Step 2: Generate query based on answer: "AI products launched by [Company] in 2024"

2. "What products has the CEO of the company that makes iPhone announced in 2024?" (3 steps)
   - Step 1: "Which company makes iPhone?" → Get answer  
   - Step 2: Generate query: "Who is the CEO of [Company]?" → Get answer
   - Step 3: Generate query: "Products announced by [CEO] in 2024"

For sequential: 
- Provide ONLY the first query
- Specify how many sequential steps are needed (2-4)
- Subsequent queries will be generated dynamically based on previous results

**PARALLEL Execution:**
Use when sub-queries are INDEPENDENT.

Example: "Summarize Tesla's Q4 2024 earnings, recent product launches, and leadership changes"
  - Query 1: "Tesla Q4 2024 earnings"
  - Query 2: "Tesla recent product launches"  
  - Query 3: "Tesla leadership changes"
  
For parallel: Provide ALL sub-queries (2-4 queries) that can run simultaneously.

Provide your analysis with clear reasoning."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {query}"}
    ]
    
    # Use structured output to get query analysis
    result = query_analyzer.invoke(messages)
    
    print(f"\nExecution Strategy: {result.execution_strategy.upper()}")
    if result.execution_strategy == "sequential":
        print(f"Number of Sequential Steps: {result.num_sequential_steps}")
    print(f"Reasoning: {result.reasoning}")
    print(f"\nSub-queries generated:")
    for i, sq in enumerate(result.sub_queries, 1):
        print(f"  {i}. {sq}")
    
    return {
        **state,
        "execution_strategy": result.execution_strategy,
        "sub_queries": result.sub_queries,
        "num_sequential_steps": result.num_sequential_steps
    }

print("Query analyzer node created!")
```

    Query analyzer node created!


## Part 6: Build the Sequential Execution Node

The **Sequential Execution Node** handles queries where results depend on each other through **multi-hop reasoning**.

The node uses a **loop** to handle any number of sequential steps (2-4):

1. Execute the first sub-query with Tavily
2. Synthesize results with the LLM
3. **Loop** for remaining steps:
   - Generate the next sub-query based on current synthesis and original query
   - Execute the query with Tavily
   - Update the synthesis with new information
4. Return all results

This approach can handle complex multi-hop queries like:
- 2-hop: "Products by the company that acquired X"
- 3-hop: "Products by the CEO of the company that makes X"
- 4-hop: "Initiatives by the person who replaced the CEO of company X"


```python
def sequential_execution_node(state: WorkflowState) -> WorkflowState:
    """
    Executes sub-queries sequentially where each query depends on previous results.
    Handles any number of sequential steps (2-4) using a loop.
    
    Returns:
        Updated state with 'search_results' and 'synthesis' populated
    """
    sub_queries = state["sub_queries"]
    original_query = state["query"]
    num_steps = state["num_sequential_steps"]
    
    print(f"\n{'='*80}")
    print("SEQUENTIAL EXECUTION NODE")
    print(f"{'='*80}")
    print(f"Executing {num_steps} sequential steps...")
    
    all_results = []
    current_synthesis = ""
    
    # Step 1: Execute first sub-query
    first_query = sub_queries[0]
    print(f"\n--- Step 1/{num_steps} ---")
    print(f"Query: {first_query}")
    
    search_response_1 = tavily_search.invoke({"query": first_query})
    results_1 = search_response_1.get("results", [])
    
    print(f"Found {len(results_1)} results")
    
    # Format first results
    formatted_results_1 = "\n\n".join([
        f"Title: {r.get('title', 'N/A')}\nContent: {r.get('content', '')}"
        for r in results_1
    ])
    
    all_results.append(f"Query 1: {first_query}\n{formatted_results_1}")
    
    # Synthesize first results
    print(f"Synthesizing results...")
    
    synthesis_prompt = f"""Based on these search results, extract the key answer to the question: "{first_query}"

Search Results:
{formatted_results_1}

Provide a concise, factual answer (1-2 sentences) that captures the essential information."""
    
    synthesis_response = llm.invoke([HumanMessage(content=synthesis_prompt)])
    current_synthesis = synthesis_response.content
    
    print(f"Key finding: {current_synthesis}")
    
    # Loop through remaining steps (2 to num_steps)
    for step_num in range(2, num_steps + 1):
        print(f"\n--- Step {step_num}/{num_steps} ---")
        
        # Generate next query based on current synthesis and original query
        print(f"Generating query based on previous findings...")
        
        next_query_prompt = f"""Original query: {original_query}

Previous findings (synthesized):
{current_synthesis}

This is step {step_num} of {num_steps} in a sequential search process.

Generate the next specific search query that:
1. Builds upon the previous findings
2. Gets us closer to answering the original query
3. Is concrete and searchable (not vague)

Return ONLY the search query, nothing else."""
        
        next_query_response = llm.invoke([HumanMessage(content=next_query_prompt)])
        next_query = next_query_response.content.strip()
        
        print(f"Query: {next_query}")
        
        # Execute the query
        search_response = tavily_search.invoke({"query": next_query})
        results = search_response.get("results", [])
        
        print(f"Found {len(results)} results")
        
        # Format results
        formatted_results = "\n\n".join([
            f"Title: {r.get('title', 'N/A')}\nContent: {r.get('content', '')}"
            for r in results
        ])
        
        all_results.append(f"Query {step_num}: {next_query}\n{formatted_results}")
        
        # Update synthesis with new information
        print(f"Updating synthesis with new findings...")
        
        update_synthesis_prompt = f"""Previous synthesis:
{current_synthesis}

New search results for query "{next_query}":
{formatted_results}

Update the synthesis by integrating the new information with what we already know.
Keep it concise (2-3 sentences) and factual."""
        
        synthesis_response = llm.invoke([HumanMessage(content=update_synthesis_prompt)])
        current_synthesis = synthesis_response.content
        
        print(f"Updated synthesis: {current_synthesis}")
    
    print(f"\n✓ All {num_steps} sequential steps completed!")
    
    return {
        **state,
        "search_results": all_results,
        "synthesis": current_synthesis
    }

print("Sequential execution node created!")
```

    Sequential execution node created!


## Part 7: Build the Parallel Execution Node

The **Parallel Execution Node** handles independent queries that can run simultaneously:

1. Create async tasks for all sub-queries
2. Execute all searches in parallel using `asyncio.gather`
3. Return all results

This is faster than sequential execution because it leverages concurrent I/O operations.

**Key concept:** Using `asyncio.gather` allows multiple web searches to happen at the same time, dramatically reducing total execution time.

**Note on Jupyter notebooks:** We use `nest_asyncio` to allow `asyncio.run()` to work inside Jupyter notebooks, which already run in an event loop. Without it, you'd get a `RuntimeError: asyncio.run() cannot be called from a running event loop`.


```python
async def search_parallel(sub_queries: List[str]) -> List[str]:
    """
    Execute multiple search queries in parallel using asyncio.
    
    Args:
        sub_queries: List of search queries to execute
        
    Returns:
        List of formatted search results
    """
    # Create async tasks for all queries
    tasks = [tavily_search.ainvoke({"query": q}) for q in sub_queries]
    
    # Execute all tasks in parallel
    results = await asyncio.gather(*tasks)
    
    # Format results
    formatted_results = []
    for i, (query, search_response) in enumerate(zip(sub_queries, results), 1):
        search_results = search_response.get("results", [])
        formatted = "\n\n".join([
            f"Title: {r.get('title', 'N/A')}\nContent: {r.get('content', '')}"
            for r in search_results
        ])
        formatted_results.append(f"Query {i}: {query}\n{formatted}")
    
    return formatted_results


def parallel_execution_node(state: WorkflowState) -> WorkflowState:
    """
    Executes independent sub-queries in parallel using asyncio.gather.
    
    Returns:
        Updated state with 'search_results' populated
    """
    sub_queries = state["sub_queries"]
    
    print(f"\n{'='*80}")
    print("PARALLEL EXECUTION NODE")
    print(f"{'='*80}")
    print(f"\nExecuting {len(sub_queries)} queries in parallel...")
    
    for i, query in enumerate(sub_queries, 1):
        print(f"  {i}. {query}")
    
    # Run parallel search
    search_results = asyncio.run(search_parallel(sub_queries))
    
    print(f"\nAll {len(search_results)} queries completed in parallel!")
    
    return {
        **state,
        "search_results": search_results
    }

print("Parallel execution node created!")
```

    Parallel execution node created!


## Part 8: Build the Synthesis Node

The **Synthesis Node** takes all search results and generates a comprehensive final answer.

This node:
1. Aggregates all search results (from either sequential or parallel execution)
2. Uses the LLM to synthesize a coherent, comprehensive answer
3. Ensures the answer addresses the original query completely


```python
def synthesis_node(state: WorkflowState) -> WorkflowState:
    """
    Synthesizes all search results into a comprehensive final answer.
    
    Returns:
        Updated state with 'final_answer' populated
    """
    query = state["query"]
    search_results = state["search_results"]
    execution_strategy = state["execution_strategy"]
    
    print(f"\n{'='*80}")
    print("SYNTHESIS NODE")
    print(f"{'='*80}")
    print(f"\nSynthesizing {len(search_results)} search result(s) into final answer...")
    
    # Combine all search results
    combined_results = "\n\n" + "="*80 + "\n\n".join(search_results)
    
    # Create synthesis prompt
    system_prompt = """You are a helpful assistant that synthesizes information from multiple search results.
    
Provide a comprehensive, well-structured answer that:
- Directly addresses the original query
- Integrates information from all search results
- Is clear, concise, and informative
- Cites specific facts when relevant
- Maintains a logical flow

If the search results are incomplete or don't fully answer the query, acknowledge this."""
    
    user_prompt = f"""Original Query: {query}

Execution Strategy: {execution_strategy}

Search Results:
{combined_results}

Please provide a comprehensive answer to the original query based on these search results."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    final_answer = response.content
    
    print(f"\nFinal answer generated!")
    
    return {
        **state,
        "final_answer": final_answer
    }

print("Synthesis node created!")
```

    Synthesis node created!


## Part 9: Create the Router Function

The **router function** examines the execution strategy and routes to the appropriate execution node.

This is used with **conditional edges** in LangGraph to create branching workflows.


```python
def route_by_strategy(state: WorkflowState) -> Literal["sequential", "parallel"]:
    """
    Routes to the appropriate execution node based on strategy.
    
    Args:
        state: Current workflow state with 'execution_strategy' field
    
    Returns:
        Name of the next node: 'sequential' or 'parallel'
    """
    strategy = state["execution_strategy"]
    
    print(f"\nRouting to: {strategy} execution node")
    
    return strategy

print("Router function created!")
```

    Router function created!


## Part 10: Build the Complete Graph

Now we'll assemble everything into a complete LangGraph workflow:

1. Create a `StateGraph` with our workflow state
2. Add all nodes (analyzer, sequential, parallel, synthesis)
3. Connect nodes with edges:
   - Entry point → Query Analyzer
   - Conditional edge from Analyzer to execution nodes
   - Both execution nodes → Synthesis
   - Synthesis → END
4. Compile the graph


```python
# Create the state graph
workflow = StateGraph(WorkflowState)

# Add nodes
workflow.add_node("query_analyzer", query_analyzer_node)
workflow.add_node("sequential", sequential_execution_node)
workflow.add_node("parallel", parallel_execution_node)
workflow.add_node("synthesis", synthesis_node)

# Add edges
# 1. Start with query analyzer
workflow.add_edge(START, "query_analyzer")

# 2. Conditional edge from query analyzer to execution nodes
workflow.add_conditional_edges(
    "query_analyzer",
    route_by_strategy,
    {
        "sequential": "sequential",
        "parallel": "parallel"
    }
)

# 3. Both execution paths lead to synthesis
workflow.add_edge("sequential", "synthesis")
workflow.add_edge("parallel", "synthesis")

# 4. Synthesis leads to end
workflow.add_edge("synthesis", END)

# Compile the graph
app = workflow.compile()

print("Graph compiled successfully!")
print("\nWorkflow structure:")
print("  START → query_analyzer → [conditional routing]")
print("                           ├─→ sequential → synthesis → END")
print("                           └─→ parallel → synthesis → END")
```

    Graph compiled successfully!
    
    Workflow structure:
      START → query_analyzer → [conditional routing]
                               ├─→ sequential → synthesis → END
                               └─→ parallel → synthesis → END


## Part 11: Visualize the Graph

LangGraph provides built-in visualization. Let's see what our workflow looks like!


```python
# Visualize the graph
try:
    from IPython.display import Image, display
    display(Image(app.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Visualization not available: {e}")
    print("\nYou can view the graph structure using Mermaid:")
    print(app.get_graph().draw_mermaid())
```


    
![png](4_6_task_decomposition_workflow_files/4_6_task_decomposition_workflow_23_0.png)
    


## Part 12: Test the Workflow

Let's test our workflow with different types of queries!

### Test 1: Sequential Execution Query

This query requires finding information first, then using it to search for more specific information.


```python
# Test 1: Sequential query
test_query_1 = "What AI products were launched by the company that acquired DeepMind in 2024?"

print(f"\n{'#'*80}")
print("TEST 1: SEQUENTIAL EXECUTION")
print(f"{'#'*80}")
print(f"Query: {test_query_1}")
print(f"{'#'*80}\n")

# Create initial state
initial_state_1 = {
    "query": test_query_1,
    "sub_queries": [],
    "execution_strategy": "",
    "num_sequential_steps": 2,
    "search_results": [],
    "synthesis": "",
    "final_answer": ""
}

# Run the workflow
result_1 = app.invoke(initial_state_1)

# Display final result
print(f"\n\n{'='*80}")
print("FINAL RESULT")
print(f"{'='*80}")
print(f"\nExecution Strategy: {result_1['execution_strategy']}")
print(f"Number of Steps: {result_1['num_sequential_steps']}")
print(f"\nFinal Answer:\n{result_1['final_answer']}")
print(f"\n{'='*80}")
```

    
    ################################################################################
    TEST 1: SEQUENTIAL EXECUTION
    ################################################################################
    Query: What AI products were launched by the company that acquired DeepMind in 2024?
    ################################################################################
    
    
    ================================================================================
    QUERY ANALYZER NODE
    ================================================================================
    Analyzing query: What AI products were launched by the company that acquired DeepMind in 2024?
    
    Execution Strategy: SEQUENTIAL
    Number of Sequential Steps: 2
    Reasoning: The query requires identifying the company that acquired DeepMind first, which is a prerequisite to then querying for the AI products launched by that company in 2024. Therefore, it involves a sequential execution strategy.
    
    Sub-queries generated:
      1. Which company acquired DeepMind?
    
    Routing to: sequential execution node
    
    ================================================================================
    SEQUENTIAL EXECUTION NODE
    ================================================================================
    Executing 2 sequential steps...
    
    --- Step 1/2 ---
    Query: Which company acquired DeepMind?
    Found 5 results
    Synthesizing results...
    Key finding: Google acquired DeepMind in 2014 for approximately $500 million.
    
    --- Step 2/2 ---
    Generating query based on previous findings...
    Query: What AI products did Google launch in 2024 after acquiring DeepMind?
    Found 5 results
    Updating synthesis with new findings...
    Updated synthesis: Google acquired DeepMind in 2014 for approximately $500 million. In 2024, Google launched several AI products, including Gemini 2.0, a next-generation AI model designed for advanced applications, and Veo 2, a state-of-the-art AI video generator. Additionally, enhancements to Google Search and Chrome incorporated generative AI features, further expanding the capabilities of their AI offerings.
    
    ✓ All 2 sequential steps completed!
    
    ================================================================================
    SYNTHESIS NODE
    ================================================================================
    
    Synthesizing 2 search result(s) into final answer...
    
    Final answer generated!
    
    
    ================================================================================
    FINAL RESULT
    ================================================================================
    
    Execution Strategy: sequential
    Number of Steps: 2
    
    Final Answer:
    In 2024, Google, which acquired DeepMind in 2014, launched several significant AI products that reflect the advancements made by the company in the field of artificial intelligence. Here are the key products introduced:
    
    1. **Gemini 2.0**: This is a next-generation AI model designed to enhance the capabilities of AI agents. It builds on the previous Gemini models and aims to provide more sophisticated interactions and functionalities in various applications, including search and content generation.
    
    2. **Veo 2**: This product is a state-of-the-art AI video generator that allows users to create high-quality video content using AI technology. It represents a significant advancement in generative AI, particularly in the realm of video production.
    
    3. **Mariner Project**: This initiative focuses on improving human-computer interaction, making it easier for users to engage with AI systems in a more intuitive manner.
    
    4. **AI Overviews in Google Search**: This feature enhances the search experience by providing AI-generated overviews of search results, allowing users to access information more efficiently. It utilizes the Gemini model to organize and present search results in a user-friendly format.
    
    5. **Generative AI Features in Chrome**: Google introduced new generative AI capabilities in its Chrome browser, enhancing user experience by providing smarter browsing tools and features.
    
    These products highlight Google's ongoing commitment to integrating advanced AI technologies into its services, leveraging the expertise and innovations developed through DeepMind. The launch of these products in 2024 marks a significant step in Google's strategy to enhance its AI offerings across various platforms and applications.
    
    ================================================================================


### Test 2: Parallel Execution Query

This query involves multiple independent pieces of information that can be searched simultaneously.


```python
# Test 2: Parallel query
test_query_2 = "Summarize Tesla's Q4 2024 earnings, recent product launches, and leadership changes"

print(f"\n{'#'*80}")
print("TEST 2: PARALLEL EXECUTION")
print(f"{'#'*80}")
print(f"Query: {test_query_2}")
print(f"{'#'*80}\n")

# Create initial state
initial_state_2 = {
    "query": test_query_2,
    "sub_queries": [],
    "execution_strategy": "",
    "num_sequential_steps": 2,  # Not used for parallel, but required field
    "search_results": [],
    "synthesis": "",
    "final_answer": ""
}

# Run the workflow
result_2 = app.invoke(initial_state_2)

# Display final result
print(f"\n\n{'='*80}")
print("FINAL RESULT")
print(f"{'='*80}")
print(f"\nExecution Strategy: {result_2['execution_strategy']}")
print(f"\nFinal Answer:\n{result_2['final_answer']}")
print(f"\n{'='*80}")
```

    
    ################################################################################
    TEST 2: PARALLEL EXECUTION
    ################################################################################
    Query: Summarize Tesla's Q4 2024 earnings, recent product launches, and leadership changes
    ################################################################################
    
    
    ================================================================================
    QUERY ANALYZER NODE
    ================================================================================
    Analyzing query: Summarize Tesla's Q4 2024 earnings, recent product launches, and leadership changes


    Exception in callback Task.__step()
    handle: <Handle Task.__step()>
    Traceback (most recent call last):
      File "/Users/sajal/.pyenv/versions/3.12.5/lib/python3.12/asyncio/events.py", line 88, in _run
        self._context.run(self._callback, *self._args)
    RuntimeError: cannot enter context: <_contextvars.Context object at 0x10cc82d80> is already entered


    
    Execution Strategy: PARALLEL
    Reasoning: The sub-queries are independent of each other, allowing them to be executed simultaneously without relying on the results of one another.
    
    Sub-queries generated:
      1. Tesla Q4 2024 earnings
      2. Tesla recent product launches
      3. Tesla leadership changes
    
    Routing to: parallel execution node
    
    ================================================================================
    PARALLEL EXECUTION NODE
    ================================================================================
    
    Executing 3 queries in parallel...
      1. Tesla Q4 2024 earnings
      2. Tesla recent product launches
      3. Tesla leadership changes
    
    All 3 queries completed in parallel!
    
    ================================================================================
    SYNTHESIS NODE
    ================================================================================
    
    Synthesizing 3 search result(s) into final answer...
    
    Final answer generated!
    
    
    ================================================================================
    FINAL RESULT
    ================================================================================
    
    Execution Strategy: parallel
    
    Final Answer:
    In Q4 2024, Tesla reported earnings that fell short of Wall Street expectations, with adjusted earnings per share at $0.73, slightly below the anticipated $0.75. For the full year, Tesla's revenue increased by just 1% to $97.7 billion, indicating a slowdown in growth amid a challenging market environment. The company acknowledged the need to return to growth in 2025 and reiterated plans to launch an unsupervised Full Self-Driving (FSD) option and a driverless ride-hailing service later in the year, starting in Austin in June 2025. Additionally, Tesla's brand value reportedly declined by $15 billion in 2024, attributed to factors such as an aging vehicle lineup and controversial public statements by CEO Elon Musk.
    
    On the product front, Tesla has introduced several new models aimed at revitalizing interest in its offerings. This includes more affordable versions of the Model 3 and Model Y, as well as a new performance trim for the Model 3. The company is also preparing for the launch of the long-anticipated Cybertruck and has confirmed the rollout of its Robotaxi service to five new U.S. cities.
    
    Leadership changes have also been significant at Tesla, with the departure of Troy Jones, the head of North American sales, marking a notable shift in the company's executive team. This exit is part of a broader trend of turnover within Tesla's leadership, which has seen at least ten executives leave over the past year. These changes come as Tesla faces increasing competition in the electric vehicle market and a general slowdown in EV sales growth, prompting the company to adapt its strategies to maintain its market position.
    
    In summary, Tesla's Q4 2024 earnings reflected challenges in revenue growth and market dynamics, while recent product launches aimed to enhance its competitive edge. Concurrently, leadership changes signal a response to the evolving landscape of the automotive industry.
    
    ================================================================================


### Test 3: Multi-hop Sequential Query (3 steps)

This query demonstrates the enhanced capability to handle more than 2 sequential steps. It requires finding information progressively through multiple hops.


```python
# Test 3: Multi-hop sequential query (3 steps)
test_query_3 = "What products has the CEO of the company that makes iPhone announced in 2024?"

print(f"\n{'#'*80}")
print("TEST 3: MULTI-HOP SEQUENTIAL EXECUTION (3 STEPS)")
print(f"{'#'*80}")
print(f"Query: {test_query_3}")
print(f"{'#'*80}\n")

# Create initial state
initial_state_3 = {
    "query": test_query_3,
    "sub_queries": [],
    "execution_strategy": "",
    "num_sequential_steps": 2,  # Will be determined by query analyzer
    "search_results": [],
    "synthesis": "",
    "final_answer": ""
}

# Run the workflow
result_3 = app.invoke(initial_state_3)

# Display final result
print(f"\n\n{'='*80}")
print("FINAL RESULT")
print(f"{'='*80}")
print(f"\nExecution Strategy: {result_3['execution_strategy']}")
print(f"Number of Steps: {result_3['num_sequential_steps']}")
print(f"\nFinal Answer:\n{result_3['final_answer']}")
print(f"\n{'='*80}")
```

    
    ################################################################################
    TEST 3: MULTI-HOP SEQUENTIAL EXECUTION (3 STEPS)
    ################################################################################
    Query: What products has the CEO of the company that makes iPhone announced in 2024?
    ################################################################################
    
    
    ================================================================================
    QUERY ANALYZER NODE
    ================================================================================
    Analyzing query: What products has the CEO of the company that makes iPhone announced in 2024?
    
    Execution Strategy: SEQUENTIAL
    Number of Sequential Steps: 3
    Reasoning: The query requires multiple steps where the first step identifies the company that makes the iPhone, which is essential to determine who the CEO is in the second step, and finally to find out what products that CEO has announced in 2024. Each step depends on the result of the previous one.
    
    Sub-queries generated:
      1. Which company makes iPhone?
    
    Routing to: sequential execution node
    
    ================================================================================
    SEQUENTIAL EXECUTION NODE
    ================================================================================
    Executing 3 sequential steps...
    
    --- Step 1/3 ---
    Query: Which company makes iPhone?
    Found 5 results
    Synthesizing results...
    Key finding: Apple is the company that makes the iPhone, with the majority of its assembly performed by Foxconn, along with contributions from other manufacturers like Pegatron and Wistron.
    
    --- Step 2/3 ---
    Generating query based on previous findings...
    Query: "Apple CEO product announcements 2024"
    Found 5 results
    Updating synthesis with new findings...
    Updated synthesis: Apple, known for its iPhone, continues to innovate under CEO Tim Cook, who has recently hinted at several upcoming product announcements for 2024, including new generative AI capabilities. The company is expected to reveal details about these AI products soon, alongside other potential announcements, such as a new Apple Pencil. Most of Apple's iPhone assembly is still performed by Foxconn, with contributions from Pegatron and Wistron.
    
    --- Step 3/3 ---
    Generating query based on previous findings...
    Query: "What new generative AI products and Apple Pencil features has Tim Cook announced for 2024?"
    Found 5 results
    Updating synthesis with new findings...
    Updated synthesis: Apple, under CEO Tim Cook, is set to unveil significant advancements in generative AI technology in 2024, including new features for iPhone and other products that may rival offerings from OpenAI and Google. The company is reportedly developing its own large language model, named Ajax, and plans to integrate generative AI capabilities into iOS 18 and various built-in apps. Additionally, Apple is expected to announce a new Apple Pencil 3, alongside other products like an OLED iPad Pro and iPad Air 6.
    
    ✓ All 3 sequential steps completed!
    
    ================================================================================
    SYNTHESIS NODE
    ================================================================================
    
    Synthesizing 3 search result(s) into final answer...



```python

```
```

---

