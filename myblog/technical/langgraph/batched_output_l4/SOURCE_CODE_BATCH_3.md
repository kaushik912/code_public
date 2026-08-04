# Source Code Batch

This file contains 3 source files.

---

## File: 4_7_graceful_degradation_tutorial.md

```markdown
# Graceful Degradation in Weather Agent Workflows

## Overview

In production AI agent systems, external dependencies will fail. APIs go down, rate limits hit, networks timeout. **Graceful degradation** is a workflow-level error handling pattern that keeps your agent functional by automatically falling back to alternative data sources when primary services fail.

Think of it like a restaurant: if the kitchen runs out of salmon, they offer you chicken instead. If chicken runs out too, they offer a vegetarian option. The key is **you still get a meal** - it just might not be your first choice.

## Learning Objectives

By the end of this tutorial, you will:

1. Understand graceful degradation as a workflow-level error handling pattern
2. Implement multi-level fallback pathways using LangGraph conditional edges
3. Build a weather agent with three degradation levels (API → Search → LLM)
4. Compare quality/cost/latency tradeoffs across different data sources
5. Route workflow execution dynamically based on service availability

## Prerequisites

**API Keys Required:**
- **OpenAI API Key**: For the LLM reasoning
- **OpenWeatherMap API Key**: Primary weather data source (https://openweathermap.org/api - free tier)
- **Tavily API Key**: Web search fallback (https://tavily.com - free tier)

**Required Packages:**
```bash
pip install langgraph langchain-openai langchain-core python-dotenv requests tavily-python pydantic
```

**Setup Instructions:**

1. Create a `.env` file in your project directory
2. Add your API keys:
   ```
   OPENAI_API_KEY=your-openai-key-here
   OPENWEATHER_API_KEY=your-openweather-key-here
   TAVILY_API_KEY=your-tavily-key-here
   ```

## What is Graceful Degradation?

Graceful degradation is a design philosophy where systems maintain functionality at reduced capacity when components fail, rather than failing completely.

**Traditional Error Handling:**
```
Try API → If fails, return error message ❌
```

**Graceful Degradation:**
```
Try API → If fails, try Search → If fails, use LLM knowledge ✓
```

### Quality Hierarchy

Our weather agent will have three levels:

| Level | Source | Quality | Latency | Cost | Reliability |
|-------|--------|---------|---------|------|-------------|
| 0 | OpenWeather API | Real-time, precise | ~200ms | Free | 99%+ |
| 1 | Tavily Web Search | Recent, approximate | ~1-2s | Free (limited) | 99.9%+ |
| 2 | LLM General Knowledge | Seasonal patterns | ~500ms | Tokens | 100% |

The workflow **automatically downgrades** when higher-quality sources fail.

### When to Use Graceful Degradation

**Good Use Cases:**
- Weather information (approximate is better than nothing)
- News/content aggregation (stale is better than missing)
- Recommendations (general is better than none)
- Informational queries (best-effort is acceptable)

**Bad Use Cases:**
- Financial transactions (accuracy critical)
- Medical diagnoses (precision required)
- Legal documents (exactness mandatory)
- Authentication/authorization (security critical)

**Rule of Thumb:** Use graceful degradation when **approximate/stale data is better than no data**, and the consequences of lower-quality information are acceptable.

## Part 1: Setup and Imports

Let's import all necessary libraries and load our environment variables.


```python
import os
import logging
import requests
from datetime import datetime
from typing import TypedDict, Optional, List, Literal
from enum import Enum

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from tavily import TavilyClient

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# Load environment variables
load_dotenv()

# Verify all API keys are present
required_keys = ["OPENAI_API_KEY", "OPENWEATHER_API_KEY", "TAVILY_API_KEY"]
missing_keys = [key for key in required_keys if not os.getenv(key)]

if missing_keys:
    raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")

print("All required API keys loaded successfully!")
print("Libraries imported successfully!")
```

    All required API keys loaded successfully!
    Libraries imported successfully!


## Part 2: Configure Structured Logging

Logging is crucial for understanding degradation behavior in production. We'll log:
- Which data source is being attempted
- Why sources failed
- Which degradation level was ultimately used
- Execution time at each level


```python
# Configure logging with clear format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Create logger for our workflow
logger = logging.getLogger('weather_workflow')

# Test the logger
logger.info("Logging system initialized")

print("Logging configured - watch for structured logs during execution")
```

    12:54:42 - weather_workflow - INFO - Logging system initialized


    Logging configured - watch for structured logs during execution


## Part 3: Build Three Weather Data Sources

We'll create three functions, each representing a different quality level. Each function returns a tuple:
- `success` (bool): Whether the data source worked
- `result` (str): The weather information or error message

This consistent interface makes it easy to chain fallbacks in our workflow.

### Level 0: OpenWeather API (Primary Source)

**Advantages:**
- Real-time data updated every 10 minutes
- Precise temperature, humidity, wind speed
- Reliable (99%+ uptime)

**Disadvantages:**
- Can fail during maintenance
- Rate limits on free tier
- Requires valid API key


```python
# Reuse geocoding helper from the application-specific tools notebook
def geocode_city(city_name: str) -> tuple[float, float]:
    """
    Convert city name to latitude/longitude using OpenWeatherMap Geocoding API.
    
    Args:
        city_name: Name of the city to geocode
    
    Returns:
        Tuple of (latitude, longitude)
    
    Raises:
        ValueError: If city not found or API request fails
    """
    city_name = city_name.strip()
    
    if not city_name:
        raise ValueError("City name cannot be empty")
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = "http://api.openweathermap.org/geo/1.0/direct"
    
    params = {
        "q": city_name,
        "limit": 1,
        "appid": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            raise ValueError(f"City '{city_name}' not found")
        
        return data[0]["lat"], data[0]["lon"]
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Geocoding failed: {str(e)}")


def get_weather_from_api(city: str) -> tuple[bool, str]:
    """
    Get real-time weather from OpenWeatherMap API.
    
    This is Level 0 - the highest quality data source.
    
    Args:
        city: City name to query
    
    Returns:
        Tuple of (success, result_string)
    """
    logger.info(f"[Level 0] Attempting OpenWeather API for {city}")
    
    try:
        # Geocode the city
        lat, lon = geocode_city(city)
        
        # Get current weather
        api_key = os.getenv("OPENWEATHER_API_KEY")
        url = "https://api.openweathermap.org/data/2.5/weather"
        
        params = {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "appid": api_key
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        # Format detailed weather information
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        result = (
            f"Real-time weather in {city}:\n"
            f"  Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"  Conditions: {description.capitalize()}\n"
            f"  Humidity: {humidity}%\n"
            f"  Wind Speed: {wind_speed} m/s\n"
            f"  Data Quality: Real-time API data (most accurate)"
        )
        
        logger.info(f"[Level 0] SUCCESS - API returned real-time data")
        return True, result
        
    except Exception as e:
        error_msg = f"API failed: {str(e)}"
        logger.warning(f"[Level 0] FAILED - {error_msg}")
        return False, error_msg


# Test the API function
print("Testing OpenWeather API...")
success, result = get_weather_from_api("London")
if success:
    print(f"\n{result}")
else:
    print(f"\nFailed: {result}")
```

    12:54:42 - weather_workflow - INFO - [Level 0] Attempting OpenWeather API for London
    12:54:42 - weather_workflow - INFO - [Level 0] SUCCESS - API returned real-time data


    Testing OpenWeather API...
    
    Real-time weather in London:
      Temperature: 13.21°C (feels like 13.07°C)
      Conditions: Light rain
      Humidity: 95%
      Wind Speed: 5.14 m/s
      Data Quality: Real-time API data (most accurate)


### Level 1: Web Search Fallback (Tavily)

**Advantages:**
- Works when API is down
- Still provides recent weather information
- More reliable than direct API (99.9%+ uptime)

**Disadvantages:**
- Less precise (scraped from web sources)
- Slower (1-2 second latency)
- May include outdated information


```python
def get_weather_from_search(city: str) -> tuple[bool, str]:
    """
    Get weather information from web search results.
    
    This is Level 1 - fallback when API fails.
    
    Args:
        city: City name to query
    
    Returns:
        Tuple of (success, result_string)
    """
    logger.info(f"[Level 1] Attempting Tavily web search for {city}")
    
    try:
        # Initialize Tavily client
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        # Search for current weather
        query = f"current weather in {city} today temperature"
        search_results = tavily_client.search(
            query=query,
            max_results=3,
            search_depth="basic"
        )
        
        if not search_results or 'results' not in search_results:
            raise ValueError("No search results found")
        
        # Extract weather information from search results
        # Combine snippets from top results
        weather_info = []
        for result in search_results['results'][:2]:
            if 'content' in result:
                weather_info.append(result['content'][:200])
        
        if not weather_info:
            raise ValueError("No weather content extracted from search")
        
        combined_info = " ".join(weather_info)
        
        result = (
            f"Web-sourced weather for {city}:\n"
            f"  {combined_info[:300]}...\n\n"
            f"  Data Quality: Recent web information (approximate)"
        )
        
        logger.info(f"[Level 1] SUCCESS - Search returned weather information")
        return True, result
        
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        logger.warning(f"[Level 1] FAILED - {error_msg}")
        return False, error_msg


# Test the search function
print("Testing Tavily web search...")
success, result = get_weather_from_search("Paris")
if success:
    print(f"\n{result}")
else:
    print(f"\nFailed: {result}")
```

    12:54:42 - weather_workflow - INFO - [Level 1] Attempting Tavily web search for Paris


    Testing Tavily web search...


    12:54:44 - weather_workflow - INFO - [Level 1] SUCCESS - Search returned weather information


    
    Web-sourced weather for Paris:
      {'location': {'name': 'Paris', 'region': 'Ile-de-France', 'country': 'France', 'lat': 48.8667, 'lon': 2.3333, 'tz_id': 'Europe/Paris', 'localtime_epoch': 1763096086, 'localtime': '2025-11-14 05:54'},  During November, expect a variety of temperatures with highs around 11° and lows near 6°, suitable ...
    
      Data Quality: Recent web information (approximate)


### Level 2: LLM General Knowledge (Last Resort)

**Advantages:**
- Always works (100% availability)
- No external dependencies
- Provides seasonal/typical patterns

**Disadvantages:**
- Not real-time (knowledge cutoff)
- Generic information only
- Cannot provide actual current conditions


```python
# Initialize LLM for fallback
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def get_weather_from_llm(city: str) -> tuple[bool, str]:
    """
    Get general weather information from LLM's knowledge.
    
    This is Level 2 - last resort when both API and search fail.
    
    Args:
        city: City name to query
    
    Returns:
        Tuple of (success, result_string)
    """
    logger.info(f"[Level 2] Using LLM general knowledge for {city}")
    
    try:
        # Determine current season
        month = datetime.now().month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "autumn"
        
        # Ask LLM for typical weather patterns
        prompt = (
            f"What is the typical weather in {city} during {season}? "
            f"Provide a brief description including typical temperature range, "
            f"common conditions, and what to expect. Keep it under 100 words. "
            f"Be clear that this is general seasonal information, not current conditions."
        )
        
        response = llm.invoke(prompt)
        llm_content = response.content
        
        result = (
            f"General weather patterns for {city} ({season}):\n"
            f"  {llm_content}\n\n"
            f"  Data Quality: Seasonal patterns from LLM knowledge (not real-time)"
        )
        
        logger.info(f"[Level 2] SUCCESS - LLM provided general weather information")
        return True, result
        
    except Exception as e:
        # LLM should rarely fail, but handle it gracefully
        error_msg = f"LLM failed: {str(e)}"
        logger.error(f"[Level 2] FAILED - {error_msg}")
        return False, error_msg


# Test the LLM function
print("Testing LLM general knowledge...")
success, result = get_weather_from_llm("Tokyo")
if success:
    print(f"\n{result}")
else:
    print(f"\nFailed: {result}")
```

    12:54:44 - weather_workflow - INFO - [Level 2] Using LLM general knowledge for Tokyo


    Testing LLM general knowledge...


    12:54:48 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    12:54:48 - weather_workflow - INFO - [Level 2] SUCCESS - LLM provided general weather information


    
    General weather patterns for Tokyo (autumn):
      During autumn in Tokyo, typically from September to November, temperatures range from 15°C to 25°C (59°F to 77°F). September can still be warm and humid, while October and November bring cooler, crisp air. Expect mostly clear skies with occasional rain, especially in September. The vibrant fall foliage, particularly in parks and gardens, adds to the beauty of the season. Overall, autumn is a pleasant time to visit, with comfortable weather and stunning natural scenery.
    
      Data Quality: Seasonal patterns from LLM knowledge (not real-time)


## Part 4: Define LangGraph State Schema

Our state needs to track:
1. **User's query** (city name)
2. **Current degradation level** (0, 1, or 2)
3. **Final result** (weather information)
4. **Error log** (what went wrong at each level)
5. **Data quality indicator** (for user transparency)

This rich state allows us to:
- Make routing decisions based on failures
- Track which fallbacks were used
- Provide transparency to users about data quality


```python
class WeatherWorkflowState(TypedDict):
    """State for weather workflow with graceful degradation."""
    city: str                          # User's city query
    degradation_level: int             # 0=API, 1=Search, 2=LLM
    result: Optional[str]              # Final weather information
    error_log: List[str]               # Track what failed at each level
    data_quality: str                  # "high", "medium", "low"


print("State schema defined!")
print("\nState fields:")
print("  - city: The city to get weather for")
print("  - degradation_level: Which data source we're currently trying (0-2)")
print("  - result: The weather information (set when successful)")
print("  - error_log: List of errors encountered during fallbacks")
print("  - data_quality: Quality indicator (high/medium/low)")
```

    State schema defined!
    
    State fields:
      - city: The city to get weather for
      - degradation_level: Which data source we're currently trying (0-2)
      - result: The weather information (set when successful)
      - error_log: List of errors encountered during fallbacks
      - data_quality: Quality indicator (high/medium/low)


## Part 5: Build Workflow Nodes

Each node attempts one data source and updates the state accordingly.

**Node Responsibilities:**
1. Log what it's attempting
2. Try its designated data source
3. If successful: populate `result` and `data_quality`
4. If failed: add error to `error_log`
5. Return updated state for routing decision

**Special Note on `format_response_node`:**
This node uses an LLM to generate a natural, conversational response that:
- Synthesizes the weather data in a user-friendly way
- Explains the data quality level transparently
- Acknowledges any degradation that occurred (with context)
- Maintains a positive, helpful tone

This creates a much better user experience compared to raw data dumps!


```python
def parse_request_node(state: WeatherWorkflowState) -> WeatherWorkflowState:
    """
    Entry node: Validate input and initialize state.
    """
    logger.info(f"=== Starting weather query for: {state['city']} ===")
    
    return {
        "city": state["city"],
        "degradation_level": 0,  # Start at highest quality level
        "result": None,
        "error_log": [],
        "data_quality": "high"
    }


def try_api_node(state: WeatherWorkflowState) -> WeatherWorkflowState:
    """
    Level 0: Attempt to get weather from OpenWeather API.
    """
    success, result = get_weather_from_api(state["city"])
    
    if success:
        return {
            "city": state["city"],
            "degradation_level": 0,
            "result": result,
            "error_log": state["error_log"],
            "data_quality": "high"
        }
    else:
        # Failed - prepare for fallback
        error_log = state["error_log"] + [f"Level 0 (API): {result}"]
        return {
            "city": state["city"],
            "degradation_level": 1,  # Move to next level
            "result": None,
            "error_log": error_log,
            "data_quality": state["data_quality"]
        }


def try_search_node(state: WeatherWorkflowState) -> WeatherWorkflowState:
    """
    Level 1: Attempt to get weather from web search.
    """
    success, result = get_weather_from_search(state["city"])
    
    if success:
        return {
            "city": state["city"],
            "degradation_level": 1,
            "result": result,
            "error_log": state["error_log"],
            "data_quality": "medium"
        }
    else:
        # Failed - prepare for final fallback
        error_log = state["error_log"] + [f"Level 1 (Search): {result}"]
        return {
            "city": state["city"],
            "degradation_level": 2,  # Move to final level
            "result": None,
            "error_log": error_log,
            "data_quality": state["data_quality"]
        }


def try_llm_node(state: WeatherWorkflowState) -> WeatherWorkflowState:
    """
    Level 2: Get weather from LLM general knowledge (last resort).
    """
    success, result = get_weather_from_llm(state["city"])
    
    if success:
        return {
            "city": state["city"],
            "degradation_level": 2,
            "result": result,
            "error_log": state["error_log"],
            "data_quality": "low"
        }
    else:
        # Complete failure (rare)
        error_log = state["error_log"] + [f"Level 2 (LLM): {result}"]
        return {
            "city": state["city"],
            "degradation_level": 2,
            "result": f"Unable to retrieve weather for {state['city']}. All data sources failed.",
            "error_log": error_log,
            "data_quality": "none"
        }


def format_response_node(state: WeatherWorkflowState) -> WeatherWorkflowState:
    """
    Final node: Use LLM to generate a natural, conversational response that
    synthesizes weather data with degradation context.
    """
    logger.info("[Formatter] Generating natural language response with LLM")

    raw_weather_data = state["result"]
    degradation_level = state["degradation_level"]
    error_log = state["error_log"]
    data_quality = state["data_quality"]
    city = state["city"]

    # Map quality levels to user-friendly descriptions
    quality_descriptions = {
        "high": "real-time API data (most accurate and current)",
        "medium": "recent web search results (approximate but recent)",
        "low": "general seasonal patterns from knowledge base (not real-time)",
        "none": "no data available"
    }

    quality_desc = quality_descriptions.get(data_quality, "unknown quality")

    # Build context for LLM
    if error_log:
        # Degradation occurred - explain what happened
        error_context = f"\n\nImportant context: We encountered {len(error_log)} errors while trying to get weather data:\n"
        for i, error in enumerate(error_log, 1):
            error_context += f"{i}. {error}\n"
        error_context += f"\nWe successfully fell back to degradation level {degradation_level} to provide you with information."
    else:
        error_context = "\n\nWe successfully retrieved data from our primary source (no fallbacks needed)."

    # Create prompt for LLM
    prompt = f"""You are a helpful weather assistant. Generate a natural, conversational response for the user about the weather in {city}.

Here's the weather information we gathered:
{raw_weather_data}

Data quality level: {quality_desc}
{error_context}

Your task:
1. Present the weather information in a clear, friendly way
2. Be transparent about the data quality (mention it's {quality_desc})
3. If degradation occurred (errors exist), briefly acknowledge it but stay positive
4. Keep the response concise (2-3 paragraphs max)
5. Don't use emojis in the main text, but include a quality badge at the end

Quality badges to use:
- High quality: 🟢 Real-time Data
- Medium quality: 🟡 Web Search Data  
- Low quality: 🔴 General Patterns

Format your response naturally, as if talking to a user. End with the appropriate quality badge."""

    try:
        # Generate response with LLM
        llm_response = llm.invoke(prompt)
        formatted_result = llm_response.content

        logger.info("[Formatter] Successfully generated natural language response")

    except Exception as e:
        # Fallback if LLM fails (shouldn't happen, but be safe)
        logger.error(f"[Formatter] LLM formatting failed: {e}")

        # Fallback to simple formatting
        quality_badge = {
            "high": "🟢 High Quality",
            "medium": "🟡 Medium Quality",
            "low": "🔴 Low Quality",
            "none": "❌ No Data"
        }.get(data_quality, "Unknown")

        formatted_result = f"{raw_weather_data}\n\nData Quality: {quality_badge}"
        if error_log:
            formatted_result += f"\n\n⚠️  Note: Fell back to level {degradation_level} after {len(error_log)} errors."

    logger.info(f"=== Query completed at degradation level {degradation_level} ===")

    return {
        "city": state["city"],
        "degradation_level": state["degradation_level"],
        "result": formatted_result,
        "error_log": state["error_log"],
        "data_quality": state["data_quality"]
    }


print("All workflow nodes defined!")
print("\nNode summary:")
print("  1. parse_request: Validate input and initialize state")
print("  2. try_api: Attempt Level 0 (OpenWeather API)")
print("  3. try_search: Attempt Level 1 (Tavily search)")
print("  4. try_llm: Attempt Level 2 (LLM knowledge)")
print("  5. format_response: Use LLM to generate natural conversational response")
```

    All workflow nodes defined!
    
    Node summary:
      1. parse_request: Validate input and initialize state
      2. try_api: Attempt Level 0 (OpenWeather API)
      3. try_search: Attempt Level 1 (Tavily search)
      4. try_llm: Attempt Level 2 (LLM knowledge)
      5. format_response: Use LLM to generate natural conversational response


## Part 6: Build Routing Functions

These functions examine the state and decide where to route next:

- If data source succeeded (`result` is not None) → Go to format_response
- If data source failed (`result` is None) → Try next fallback level

This is the **heart of graceful degradation** - the conditional routing that automatically moves down the quality hierarchy when failures occur.


```python
def route_after_api(state: WeatherWorkflowState) -> Literal["format_response", "try_search"]:
    """
    Route after API attempt:
    - If API succeeded → format_response
    - If API failed → try_search
    """
    if state["result"] is not None:
        logger.info("[Router] API succeeded, routing to format_response")
        return "format_response"
    else:
        logger.info("[Router] API failed, routing to try_search")
        return "try_search"


def route_after_search(state: WeatherWorkflowState) -> Literal["format_response", "try_llm"]:
    """
    Route after search attempt:
    - If search succeeded → format_response
    - If search failed → try_llm
    """
    if state["result"] is not None:
        logger.info("[Router] Search succeeded, routing to format_response")
        return "format_response"
    else:
        logger.info("[Router] Search failed, routing to try_llm")
        return "try_llm"


print("Routing functions defined!")
print("\nRouting logic:")
print("  - After API: Success → format | Failure → search")
print("  - After Search: Success → format | Failure → LLM")
print("  - After LLM: Always → format (last resort)")
```

    Routing functions defined!
    
    Routing logic:
      - After API: Success → format | Failure → search
      - After Search: Success → format | Failure → LLM
      - After LLM: Always → format (last resort)


## Part 7: Construct LangGraph Workflow

Now we assemble all the pieces into a complete workflow graph.

**Key Features:**
1. Linear entry: START → parse_request → try_api
2. Conditional branching after each attempt (success vs. failure)
3. Three degradation levels with automatic fallback
4. All paths converge at format_response → END

This structure ensures that **no matter what fails**, we always return something to the user.


```python
# Create the state graph
workflow = StateGraph(WeatherWorkflowState)

# Add all nodes
workflow.add_node("parse_request", parse_request_node)
workflow.add_node("try_api", try_api_node)
workflow.add_node("try_search", try_search_node)
workflow.add_node("try_llm", try_llm_node)
workflow.add_node("format_response", format_response_node)

# Add edges
workflow.add_edge(START, "parse_request")
workflow.add_edge("parse_request", "try_api")

# Conditional edges for graceful degradation
workflow.add_conditional_edges(
    "try_api",
    route_after_api,
    {
        "format_response": "format_response",
        "try_search": "try_search"
    }
)

workflow.add_conditional_edges(
    "try_search",
    route_after_search,
    {
        "format_response": "format_response",
        "try_llm": "try_llm"
    }
)

# LLM always goes to format (last resort)
workflow.add_edge("try_llm", "format_response")
workflow.add_edge("format_response", END)

# Compile the workflow
weather_app = workflow.compile()

print("Workflow compiled successfully!")
print("\nWorkflow structure:")
print("  START → parse_request → try_api")
print("                            ├─ [success] → format_response → END")
print("                            └─ [failure] → try_search")
print("                                            ├─ [success] → format_response → END")
print("                                            └─ [failure] → try_llm → format_response → END")
```

    Workflow compiled successfully!
    
    Workflow structure:
      START → parse_request → try_api
                                ├─ [success] → format_response → END
                                └─ [failure] → try_search
                                                ├─ [success] → format_response → END
                                                └─ [failure] → try_llm → format_response → END


### Visualize the Workflow

Let's create a visual representation of our graceful degradation workflow.


```python
from IPython.display import Image, display

try:
    display(Image(weather_app.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Could not generate graph visualization: {e}")
    print("\nWorkflow structure (text):")
    print("""
    START
      ↓
    parse_request
      ↓
    try_api (Level 0: OpenWeather API)
      ├─→ [SUCCESS] → format_response → END
      └─→ [FAILURE] → try_search (Level 1: Tavily Search)
                        ├─→ [SUCCESS] → format_response → END
                        └─→ [FAILURE] → try_llm (Level 2: LLM Knowledge)
                                          ↓
                                      format_response
                                          ↓
                                        END
    """)
```


    
![png](4_7_graceful_degradation_tutorial_files/4_7_graceful_degradation_tutorial_20_0.png)
    


## Part 8: Test Scenario 1 - Normal Operation (Level 0)

**Expected Behavior:**
- API should work normally
- Should return detailed real-time data
- Data quality: High (green badge)
- No fallbacks triggered

This is the **happy path** - what happens when everything works correctly.


```python
print("=" * 80)
print("TEST SCENARIO 1: Normal Operation - API Success")
print("=" * 80)
print("\nExpected: Level 0 (API) should succeed with high-quality real-time data\n")

initial_state = {
    "city": "London",
    "degradation_level": 0,
    "result": None,
    "error_log": [],
    "data_quality": "high"
}

result = weather_app.invoke(initial_state)

print("\n" + "=" * 80)
print("FINAL RESULT:")
print("=" * 80)
print(f"\n{result['result']}")
print(f"\nDegradation level used: {result['degradation_level']}")
print(f"Errors encountered: {len(result['error_log'])}")
```

    12:54:48 - weather_workflow - INFO - === Starting weather query for: London ===
    12:54:48 - weather_workflow - INFO - [Level 0] Attempting OpenWeather API for London
    12:54:48 - weather_workflow - INFO - [Level 0] SUCCESS - API returned real-time data
    12:54:48 - weather_workflow - INFO - [Router] API succeeded, routing to format_response
    12:54:48 - weather_workflow - INFO - [Formatter] Generating natural language response with LLM


    ================================================================================
    TEST SCENARIO 1: Normal Operation - API Success
    ================================================================================
    
    Expected: Level 0 (API) should succeed with high-quality real-time data
    


    12:54:53 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    12:54:53 - weather_workflow - INFO - [Formatter] Successfully generated natural language response
    12:54:53 - weather_workflow - INFO - === Query completed at degradation level 0 ===


    
    ================================================================================
    FINAL RESULT:
    ================================================================================
    
    Currently, the weather in London is a bit damp, with light rain falling and a temperature of around 13.2°C, which feels slightly cooler at 13.1°C. The humidity is quite high at 95%, so it might feel a bit muggy out there. There's a gentle breeze blowing at about 5.1 m/s, which could provide a little relief from the rain.
    
    This information is pulled from real-time API data, ensuring it's the most accurate and current available. So, if you're heading out, it might be a good idea to grab an umbrella! 
    
    🟢 Real-time Data
    
    Degradation level used: 0
    Errors encountered: 0


## Part 9: Test Scenario 2 - API Failure (Level 1 Degradation)

**Simulating API Failure:**
We'll temporarily break the API by using an invalid API key, forcing the workflow to fall back to web search.

**Expected Behavior:**
- API should fail (invalid credentials)
- Workflow automatically routes to search
- Search should succeed with web-scraped data
- Data quality: Medium (yellow badge)
- User sees degradation warning

This demonstrates **automatic fallback in action**.


```python
print("=" * 80)
print("TEST SCENARIO 2: API Failure - Search Fallback")
print("=" * 80)
print("\nSimulating API failure by temporarily using invalid credentials...\n")

# Save original API key
original_api_key = os.getenv("OPENWEATHER_API_KEY")

# Temporarily set invalid API key
os.environ["OPENWEATHER_API_KEY"] = "invalid_key_for_testing"

try:
    initial_state = {
        "city": "London",
        "degradation_level": 0,
        "result": None,
        "error_log": [],
        "data_quality": "high"
    }
    
    result = weather_app.invoke(initial_state)
    
    print("\n" + "=" * 80)
    print("FINAL RESULT:")
    print("=" * 80)
    print(f"\n{result['result']}")
    print(f"\nDegradation level used: {result['degradation_level']}")
    print(f"Errors encountered: {len(result['error_log'])}")
    
    if result['error_log']:
        print("\nError details:")
        for i, error in enumerate(result['error_log'], 1):
            print(f"  {i}. {error}")
    
finally:
    # Restore original API key
    os.environ["OPENWEATHER_API_KEY"] = original_api_key
    print("\n[API key restored]")
```

    12:54:53 - weather_workflow - INFO - === Starting weather query for: London ===
    12:54:53 - weather_workflow - INFO - [Level 0] Attempting OpenWeather API for London
    12:54:53 - weather_workflow - WARNING - [Level 0] FAILED - API failed: Geocoding failed: 401 Client Error: Unauthorized for url: http://api.openweathermap.org/geo/1.0/direct?q=London&limit=1&appid=invalid_key_for_testing
    12:54:53 - weather_workflow - INFO - [Router] API failed, routing to try_search
    12:54:53 - weather_workflow - INFO - [Level 1] Attempting Tavily web search for London


    ================================================================================
    TEST SCENARIO 2: API Failure - Search Fallback
    ================================================================================
    
    Simulating API failure by temporarily using invalid credentials...
    


    12:54:56 - weather_workflow - INFO - [Level 1] SUCCESS - Search returned weather information
    12:54:56 - weather_workflow - INFO - [Router] Search succeeded, routing to format_response
    12:54:56 - weather_workflow - INFO - [Formatter] Generating natural language response with LLM
    12:55:01 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    12:55:01 - weather_workflow - INFO - [Formatter] Successfully generated natural language response
    12:55:01 - weather_workflow - INFO - === Query completed at degradation level 1 ===


    
    ================================================================================
    FINAL RESULT:
    ================================================================================
    
    Hey there! The weather in London right now is quite chilly, typical for November. You can expect temperatures to range between 42°F and 51°F, so it’s a good idea to bundle up if you’re heading out. It might feel a bit brisk, especially with the potential for some wind.
    
    I gathered this information from recent web sources, so while it's approximate, it should give you a decent idea of what to expect. We did encounter a minor issue retrieving the most precise data, but overall, it looks like a typical London autumn day. Stay warm out there! 🟡 Web Search Data
    
    Degradation level used: 1
    Errors encountered: 1
    
    Error details:
      1. Level 0 (API): API failed: Geocoding failed: 401 Client Error: Unauthorized for url: http://api.openweathermap.org/geo/1.0/direct?q=London&limit=1&appid=invalid_key_for_testing
    
    [API key restored]


## Part 10: Test Scenario 3 - API + Search Failure (Level 2 Degradation)

**Simulating Double Failure:**
We'll break both the API and search to force the workflow down to LLM general knowledge.

**Expected Behavior:**
- API fails (invalid credentials)
- Search fails (invalid API key)
- Workflow falls back to LLM
- LLM provides seasonal/typical weather patterns
- Data quality: Low (red badge)
- User sees multiple degradation warnings

This demonstrates the **full degradation chain** - all the way to the last resort.


```python
print("=" * 80)
print("TEST SCENARIO 3: Double Failure - LLM Fallback")
print("=" * 80)
print("\nSimulating both API and Search failures...\n")

# Save original API keys
original_weather_key = os.getenv("OPENWEATHER_API_KEY")
original_tavily_key = os.getenv("TAVILY_API_KEY")

# Temporarily set invalid API keys
os.environ["OPENWEATHER_API_KEY"] = "invalid_weather_key"
os.environ["TAVILY_API_KEY"] = "invalid_tavily_key"

try:
    initial_state = {
        "city": "London",
        "degradation_level": 0,
        "result": None,
        "error_log": [],
        "data_quality": "high"
    }
    
    result = weather_app.invoke(initial_state)
    
    print("\n" + "=" * 80)
    print("FINAL RESULT:")
    print("=" * 80)
    print(f"\n{result['result']}")
    print(f"\nDegradation level used: {result['degradation_level']}")
    print(f"Errors encountered: {len(result['error_log'])}")
    
    if result['error_log']:
        print("\nError details:")
        for i, error in enumerate(result['error_log'], 1):
            print(f"  {i}. {error}")
    
finally:
    # Restore original API keys
    os.environ["OPENWEATHER_API_KEY"] = original_weather_key
    os.environ["TAVILY_API_KEY"] = original_tavily_key
    print("\n[API keys restored]")
```

    12:55:01 - weather_workflow - INFO - === Starting weather query for: London ===
    12:55:01 - weather_workflow - INFO - [Level 0] Attempting OpenWeather API for London
    12:55:01 - weather_workflow - WARNING - [Level 0] FAILED - API failed: Geocoding failed: 401 Client Error: Unauthorized for url: http://api.openweathermap.org/geo/1.0/direct?q=London&limit=1&appid=invalid_weather_key
    12:55:01 - weather_workflow - INFO - [Router] API failed, routing to try_search
    12:55:01 - weather_workflow - INFO - [Level 1] Attempting Tavily web search for London


    ================================================================================
    TEST SCENARIO 3: Double Failure - LLM Fallback
    ================================================================================
    
    Simulating both API and Search failures...
    


    12:55:02 - weather_workflow - WARNING - [Level 1] FAILED - Search failed: Invalid API key: Unauthorized: missing or invalid API key.
    12:55:02 - weather_workflow - INFO - [Router] Search failed, routing to try_llm
    12:55:02 - weather_workflow - INFO - [Level 2] Using LLM general knowledge for London
    12:55:05 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    12:55:05 - weather_workflow - INFO - [Level 2] SUCCESS - LLM provided general weather information
    12:55:05 - weather_workflow - INFO - [Formatter] Generating natural language response with LLM
    12:55:11 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    12:55:11 - weather_workflow - INFO - [Formatter] Successfully generated natural language response
    12:55:11 - weather_workflow - INFO - === Query completed at degradation level 2 ===


    
    ================================================================================
    FINAL RESULT:
    ================================================================================
    
    The weather in London during autumn, which runs from September to November, typically sees temperatures ranging from 10°C to 18°C (50°F to 64°F). Early in the season, you might still enjoy some mild days, but as autumn progresses, it does get cooler. You'll experience a mix of sunny spells and overcast skies, with November bringing more frequent rainfall. The beautiful fall foliage adds a lovely touch to the city's parks and streets, making it a charming time to explore.
    
    Just a heads up, the information I provided is based on general seasonal patterns rather than real-time data, as we encountered some issues retrieving the latest weather updates. So, it's always a good idea to dress in layers and keep an umbrella handy, as the weather can be quite unpredictable. Enjoy your time in London!
    
    🔴 General Patterns
    
    Degradation level used: 2
    Errors encountered: 2
    
    Error details:
      1. Level 0 (API): API failed: Geocoding failed: 401 Client Error: Unauthorized for url: http://api.openweathermap.org/geo/1.0/direct?q=London&limit=1&appid=invalid_weather_key
      2. Level 1 (Search): Search failed: Invalid API key: Unauthorized: missing or invalid API key.
    
    [API keys restored]

```

---

## File: 4_8_time_travel.md

```markdown
# LangGraph Time Travel: Research Assistant with Query Refinement

## Overview

**Time travel** in LangGraph is a powerful feature that lets you go back to any point in an agent's execution history, modify the state, and create alternative timelines. This isn't just debugging - it's a fundamental capability for building interactive agents that can:

- Accept mid-execution guidance from users
- Explore multiple solution paths from a single starting point
- Recover from mistakes by branching from earlier states
- Create "what-if" scenarios without re-running expensive operations

Think of it like Git for agent execution: every step creates a checkpoint, and you can branch from any checkpoint to explore alternatives.

## Use Case: Research Assistant with Interactive Direction

We'll build a research assistant that:

1. **parse_request**: Takes a research question
2. **generate_queries**: LLM generates 2-3 search queries (influenced by optional `direction`)
3. **search_and_summarize**: Uses Tavily API to find information
4. **generate_report**: Synthesizes findings into a final report

After the initial run, we'll:
- Go back to before query generation
- Add a `direction` field (technical, business, historical)
- Resume execution and observe how the workflow adapts

## Learning Objectives

By the end of this tutorial, you will:

1. Understand LangGraph's checkpoint-based execution model
2. Navigate execution history using `get_state_history()`
3. Identify strategic checkpoints for time travel
4. Update state at specific checkpoints using `update_state()`
5. Resume execution from modified checkpoints
6. Create multiple alternative timelines from a single checkpoint
7. Build interactive agents that accept mid-execution guidance

## Prerequisites

**API Keys Required:**
- **OpenAI API Key**: For LLM reasoning (query generation and report synthesis)
- **Tavily API Key**: For web search functionality (https://tavily.com - free tier available)

**Required Packages:**
```bash
pip install langgraph langchain-openai langchain-core python-dotenv tavily-python
```

**Setup Instructions:**

1. Create a `.env` file in your project directory
2. Add your API keys:
   ```
   OPENAI_API_KEY=your-openai-key-here
   TAVILY_API_KEY=your-tavily-key-here
   ```

## When to Use Time Travel

**Good Use Cases:**
- Interactive agents that accept user guidance mid-execution
- Exploring multiple solution approaches without re-running setup
- A/B testing different prompts or parameters
- Debugging by replaying with modified state
- Recovery from errors by branching before the failure

**Not Ideal For:**
- Real-time applications where latency is critical
- Simple linear workflows with no branching needs
- Stateless operations that don't benefit from checkpoints

**Rule of Thumb:** Use time travel when you need to explore alternative paths or accept guidance without re-running expensive or non-deterministic operations.

## Part 1: Setup and Imports

Let's import all necessary libraries and verify our environment is correctly configured.


```python
import os
import logging
from typing import TypedDict, List, Dict, Optional
from datetime import datetime

from dotenv import load_dotenv
from tavily import TavilyClient

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

# Verify API keys are present
required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
missing_keys = [key for key in required_keys if not os.getenv(key)]

if missing_keys:
    raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")

print("All required API keys loaded successfully!")
print("Libraries imported successfully!")
```

    All required API keys loaded successfully!
    Libraries imported successfully!


## Part 2: Configure Structured Logging

Logging is essential for understanding how time travel affects execution flow. We'll log:
- When each node executes
- What the current state contains
- Which checkpoint we're resuming from
- How direction influences query generation


```python
# Configure logging with clear format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Create logger for our workflow
logger = logging.getLogger('research_workflow')

# Test the logger
logger.info("Logging system initialized")

print("Logging configured - watch for structured logs during execution")
```

    13:54:44 - research_workflow - INFO - Logging system initialized


    Logging configured - watch for structured logs during execution


## Part 3: Define State Schema

Our state needs to track the research process from question to final report.

**Key Field: `direction`**

The `direction` field is optional and acts as guidance for the LLM during query generation:
- If `None`: LLM generates general queries
- If present: LLM focuses queries on that direction (technical, business, historical, etc.)

This is the field we'll add via time travel to influence the workflow.


```python
class ResearchState(TypedDict):
    """State for research assistant workflow."""
    research_question: str              # User's research question
    direction: Optional[str]            # Direction to guide query generation
    generated_queries: List[str]        # Search queries generated by LLM
    search_results: Dict[str, str]      # Query -> summary mappings
    final_report: str                   # Synthesized research report


print("State schema defined!")
print("\nState fields:")
print("  - research_question: The question to research")
print("  - direction: Optional guidance for query generation")
print("  - generated_queries: List of search queries")
print("  - search_results: Dictionary mapping queries to summaries")
print("  - final_report: Final synthesized report")
```

    State schema defined!
    
    State fields:
      - research_question: The question to research
      - direction: Optional guidance for query generation
      - generated_queries: List of search queries
      - search_results: Dictionary mapping queries to summaries
      - final_report: Final synthesized report


## Part 4: Initialize LLM and Tavily Client

We'll use:
- **GPT-4o**: For query generation and report synthesis (better reasoning)
- **Tavily**: For web search to find relevant information

Temperature is set low (0.1) to ensure consistent, focused outputs.


```python
# Initialize LLM for query generation and report synthesis
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

# Initialize Tavily client for web search
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

print("LLM and Tavily client initialized successfully!")
print(f"  - LLM: {llm.model_name}")
print(f"  - Temperature: {llm.temperature}")
print("  - Search: Tavily API")
```

    LLM and Tavily client initialized successfully!
      - LLM: gpt-4o
      - Temperature: 0.1
      - Search: Tavily API


## Part 5: Build Workflow Nodes

Each node performs one step of the research process.

### Node 1: parse_request_node

**Responsibility:**
- Validate the research question
- Initialize state
- Preserve `direction` if it exists

When we resume from a checkpoint after adding `direction`, this node must keep it in the state for the next node to use.


```python
def parse_request_node(state: ResearchState) -> ResearchState:
    """
    Entry node: Validate research question and initialize state.
    
    Preserves 'direction' if present for time travel scenarios.
    """
    question = state.get("research_question", "").strip()
    
    if not question:
        raise ValueError("Research question cannot be empty")
    
    logger.info(f"=== Starting research for: {question} ===")
    
    direction = state.get("direction")
    if direction:
        logger.info(f"Direction guidance detected: '{direction}'")
    else:
        logger.info("No direction guidance - will generate general queries")
    
    return {
        "research_question": question,
        "direction": direction,
        "generated_queries": [],
        "search_results": {},
        "final_report": ""
    }


print("parse_request_node defined!")
print("  - Validates input")
print("  - Initializes state")
print("  - Preserves direction field for time travel")
```

    parse_request_node defined!
      - Validates input
      - Initializes state
      - Preserves direction field for time travel


### Node 2: generate_queries_node

**Behavior:**
1. Check if `direction` exists in state
2. If present: Adjust prompt to focus queries on that direction
3. If absent: Generate general queries
4. Use LLM to generate 2-3 search queries

When we time travel back and add `direction`, this node will naturally generate different queries aligned with that direction.


```python
def generate_queries_node(state: ResearchState) -> ResearchState:
    """
    Generate search queries using LLM.
    
    Adapts query generation based on 'direction' field:
    - If direction exists: Focus queries on that direction
    - If direction is None: Generate general queries
    """
    question = state["research_question"]
    direction = state.get("direction")
    
    logger.info(f"[generate_queries] Processing question: {question}")
    
    # Build prompt based on whether direction is provided
    if direction:
        logger.info(f"[generate_queries] Using direction: '{direction}'")
        prompt = f"""You are a research assistant. Generate 2-3 focused search queries to research this question.

Research Question: {question}

IMPORTANT: Focus your queries specifically on the {direction} aspects of this topic.
Your queries should help find information about {direction} related to the question.

Generate 2-3 search queries, one per line. Make them specific and focused on {direction}.

Example format:
query 1
query 2
query 3
"""
    else:
        logger.info("[generate_queries] No direction - generating general queries")
        prompt = f"""You are a research assistant. Generate 2-3 search queries to comprehensively research this question.

Research Question: {question}

Generate 2-3 diverse search queries that cover different aspects of this topic.
Make them specific and actionable, one per line.

Example format:
query 1
query 2
query 3
"""
    
    # Generate queries with LLM
    response = llm.invoke(prompt)
    queries_text = response.content.strip()
    
    # Parse queries (one per line)
    queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
    
    # Keep only first 3 queries
    queries = queries[:3]
    
    logger.info(f"[generate_queries] Generated {len(queries)} queries")
    for i, q in enumerate(queries, 1):
        logger.info(f"  Query {i}: {q}")
    
    return {
        "research_question": state["research_question"],
        "direction": state.get("direction"),
        "generated_queries": queries,
        "search_results": {},
        "final_report": ""
    }


print("generate_queries_node defined!")
print("  - Checks for direction guidance")
print("  - Adapts prompt based on direction")
print("  - Generates 2-3 focused queries")
```

    generate_queries_node defined!
      - Checks for direction guidance
      - Adapts prompt based on direction
      - Generates 2-3 focused queries


### Node 3: search_and_summarize_node

**Responsibility:**
- Execute each query using Tavily API
- Extract relevant content from search results
- Create concise summaries for each query
- Handle search failures gracefully


```python
def search_and_summarize_node(state: ResearchState) -> ResearchState:
    """
    Execute searches and create summaries for each query.
    """
    queries = state["generated_queries"]
    
    logger.info(f"[search] Executing {len(queries)} searches...")
    
    search_results = {}
    
    for i, query in enumerate(queries, 1):
        logger.info(f"[search] Query {i}/{len(queries)}: {query}")
        
        try:
            # Execute search
            results = tavily_client.search(
                query=query,
                max_results=3,
                search_depth="basic"
            )
            
            if not results or 'results' not in results:
                logger.warning(f"[search] No results for query: {query}")
                search_results[query] = "No results found"
                continue
            
            # Extract and combine content from top results
            content_pieces = []
            for result in results['results'][:3]:
                if 'content' in result:
                    content_pieces.append(result['content'][:300])
            
            if content_pieces:
                combined_content = " ".join(content_pieces)
                # Truncate to reasonable length
                summary = combined_content[:500] + "..." if len(combined_content) > 500 else combined_content
                search_results[query] = summary
                logger.info(f"[search] Found {len(content_pieces)} results")
            else:
                search_results[query] = "No content extracted"
                logger.warning(f"[search] No content extracted for query: {query}")
        
        except Exception as e:
            logger.error(f"[search] Error searching '{query}': {e}")
            search_results[query] = f"Search failed: {str(e)}"
    
    logger.info(f"[search] Completed {len(search_results)} searches")
    
    return {
        "research_question": state["research_question"],
        "direction": state.get("direction"),
        "generated_queries": state["generated_queries"],
        "search_results": search_results,
        "final_report": ""
    }


print("search_and_summarize_node defined!")
print("  - Executes Tavily searches")
print("  - Extracts and summarizes content")
print("  - Handles errors gracefully")
```

    search_and_summarize_node defined!
      - Executes Tavily searches
      - Extracts and summarizes content
      - Handles errors gracefully


### Node 4: generate_report_node

**Responsibility:**
- Synthesize all search results into a coherent report
- Mention the direction if one was provided
- Cite which queries contributed to findings
- Create a well-structured, informative report


```python
def generate_report_node(state: ResearchState) -> ResearchState:
    """
    Synthesize search results into a final research report.
    """
    question = state["research_question"]
    direction = state.get("direction")
    queries = state["generated_queries"]
    search_results = state["search_results"]
    
    logger.info("[report] Synthesizing findings into final report...")
    
    # Build context from search results
    search_context = ""
    for i, (query, summary) in enumerate(search_results.items(), 1):
        search_context += f"\nQuery {i}: {query}\nFindings: {summary}\n"
    
    # Build prompt
    if direction:
        direction_note = f"\n\nIMPORTANT: This research was focused on {direction}. Make sure your report emphasizes these aspects."
    else:
        direction_note = ""
    
    prompt = f"""You are a research analyst. Synthesize the following search results into a clear, informative report.

Research Question: {question}
{direction_note}

Search Results:
{search_context}

Create a well-structured report that:
1. Directly answers the research question
2. Synthesizes information from multiple sources
3. Is clear and easy to understand
4. Is 2-3 paragraphs long
{"5. Emphasizes " + direction + " aspects" if direction else ""}

Write the report now:
"""
    
    # Generate report
    response = llm.invoke(prompt)
    report = response.content.strip()
    
    logger.info("[report] Report generated successfully")
    logger.info(f"=== Research completed for: {question} ===")
    
    return {
        "research_question": state["research_question"],
        "direction": state.get("direction"),
        "generated_queries": state["generated_queries"],
        "search_results": state["search_results"],
        "final_report": report
    }


print("generate_report_node defined!")
print("  - Synthesizes all findings")
print("  - Creates structured report")
print("  - Mentions direction if provided")
```

    generate_report_node defined!
      - Synthesizes all findings
      - Creates structured report
      - Mentions direction if provided


## Part 6: Build Workflow Graph

Now we assemble all nodes into a linear workflow.

**Critical Component: MemorySaver**

The `MemorySaver` checkpointer is what enables time travel:
- Saves state after every node execution
- Creates a checkpoint at each step
- Allows retrieval of execution history
- Enables resuming from any checkpoint

Without a checkpointer, time travel is not possible.


```python
# Create the state graph
workflow = StateGraph(ResearchState)

# Add all nodes
workflow.add_node("parse_request", parse_request_node)
workflow.add_node("generate_queries", generate_queries_node)
workflow.add_node("search_and_summarize", search_and_summarize_node)
workflow.add_node("generate_report", generate_report_node)

# Add edges (linear workflow)
workflow.add_edge(START, "parse_request")
workflow.add_edge("parse_request", "generate_queries")
workflow.add_edge("generate_queries", "search_and_summarize")
workflow.add_edge("search_and_summarize", "generate_report")
workflow.add_edge("generate_report", END)

# Use MemorySaver checkpointer to enable time travel
checkpointer = MemorySaver()
research_app = workflow.compile(checkpointer=checkpointer)

print("Workflow compiled successfully!")
print("\nWorkflow structure:")
print("  START → parse_request → generate_queries → search_and_summarize → generate_report → END")
print("\nCheckpointer: MemorySaver (enables time travel)")
```

    Workflow compiled successfully!
    
    Workflow structure:
      START → parse_request → generate_queries → search_and_summarize → generate_report → END
    
    Checkpointer: MemorySaver (enables time travel)


## Part 7: Visualize Workflow

Let's create a visual representation of our research workflow.


```python
from IPython.display import Image, display

try:
    display(Image(research_app.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Could not generate graph visualization: {e}")
    print("\nWorkflow structure (text):")
    print("""
    START
      ↓
    parse_request
      ↓
    generate_queries
      ↓
    search_and_summarize
      ↓
    generate_report
      ↓
    END
    """)
```


    
![png](4_8_time_travel_files/4_8_time_travel_20_0.png)
    


## Part 8: Initial Run (No Direction)

Let's run the workflow with a research question but no direction guidance.

**What to observe:**
- The LLM generates general, broad queries
- Search finds information across various aspects
- Report covers the topic comprehensively but without specific focus

We need to use a `thread_id` in the config to track this execution and retrieve its history later.


```python
print("=" * 80)
print("INITIAL RUN: Research without Direction")
print("=" * 80)
print("\nResearch Question: What are AI agents and how do they work?")
print("Direction: None (will generate general queries)\n")

# Create initial state
initial_state = {
    "research_question": "What are AI agents and how do they work?",
    "direction": None,  # No direction initially
    "generated_queries": [],
    "search_results": {},
    "final_report": ""
}

# Create config with thread_id for tracking
config = {"configurable": {"thread_id": "research_001"}}

# Run the workflow
initial_result = research_app.invoke(initial_state, config)

print("\n" + "=" * 80)
print("INITIAL RESULTS")
print("=" * 80)

print("\nGenerated Queries:")
for i, query in enumerate(initial_result["generated_queries"], 1):
    print(f"  {i}. {query}")

print("\nFinal Report:")
print(initial_result["final_report"])

print("\n" + "=" * 80)
```

    13:54:58 - research_workflow - INFO - === Starting research for: What are AI agents and how do they work? ===
    13:54:58 - research_workflow - INFO - No direction guidance - will generate general queries
    13:54:58 - research_workflow - INFO - [generate_queries] Processing question: What are AI agents and how do they work?
    13:54:58 - research_workflow - INFO - [generate_queries] No direction - generating general queries


    ================================================================================
    INITIAL RUN: Research without Direction
    ================================================================================
    
    Research Question: What are AI agents and how do they work?
    Direction: None (will generate general queries)
    


    13:55:01 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    13:55:01 - research_workflow - INFO - [generate_queries] Generated 3 queries
    13:55:01 - research_workflow - INFO -   Query 1: 1. "Overview of AI agents: definitions and types in artificial intelligence"
    13:55:01 - research_workflow - INFO -   Query 2: 2. "Mechanisms and algorithms behind the functioning of AI agents"
    13:55:01 - research_workflow - INFO -   Query 3: 3. "Applications and real-world examples of AI agents in various industries"
    13:55:01 - research_workflow - INFO - [search] Executing 3 searches...
    13:55:01 - research_workflow - INFO - [search] Query 1/3: 1. "Overview of AI agents: definitions and types in artificial intelligence"
    13:55:04 - research_workflow - INFO - [search] Found 3 results
    13:55:04 - research_workflow - INFO - [search] Query 2/3: 2. "Mechanisms and algorithms behind the functioning of AI agents"
    13:55:05 - research_workflow - INFO - [search] Found 3 results
    13:55:05 - research_workflow - INFO - [search] Query 3/3: 3. "Applications and real-world examples of AI agents in various industries"
    13:55:05 - research_workflow - INFO - [search] Found 3 results
    13:55:05 - research_workflow - INFO - [search] Completed 3 searches
    13:55:06 - research_workflow - INFO - [report] Synthesizing findings into final report...
    13:55:17 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    13:55:17 - research_workflow - INFO - [report] Report generated successfully
    13:55:17 - research_workflow - INFO - === Research completed for: What are AI agents and how do they work? ===


    
    ================================================================================
    INITIAL RESULTS
    ================================================================================
    
    Generated Queries:
      1. 1. "Overview of AI agents: definitions and types in artificial intelligence"
      2. 2. "Mechanisms and algorithms behind the functioning of AI agents"
      3. 3. "Applications and real-world examples of AI agents in various industries"
    
    Final Report:
    **Report on AI Agents and Their Functioning**
    
    AI agents are autonomous entities in artificial intelligence that perceive their environment through sensors and act upon that environment using actuators to achieve specific goals. These agents can range from simple rule-based systems to complex, learning-based models. They are designed to operate independently, making decisions based on the data they receive and the objectives they are programmed to fulfill. AI agents can be categorized into several types, including reactive agents, which respond to stimuli without internal states, and cognitive agents, which possess memory and learning capabilities to adapt over time.
    
    The functioning of AI agents relies on a combination of algorithms and mechanisms that enable them to process information and make decisions. These algorithms can include decision trees, neural networks, and reinforcement learning models, among others. The choice of algorithm depends on the complexity of the task and the environment in which the agent operates. For instance, in dynamic environments where learning from experience is crucial, reinforcement learning is often employed. This allows the agent to improve its performance by receiving feedback from its actions. In contrast, simpler environments might only require rule-based algorithms that follow predefined instructions.
    
    AI agents are widely used across various industries, demonstrating their versatility and effectiveness. In healthcare, AI agents assist in diagnosing diseases by analyzing medical data and suggesting treatment plans. In finance, they are employed for algorithmic trading and fraud detection. In customer service, AI agents, such as chatbots, handle inquiries and provide support, enhancing user experience. These applications highlight the transformative impact of AI agents, as they streamline processes, improve decision-making, and offer innovative solutions to complex problems.
    
    ================================================================================


## Part 9: Explore Execution History

Now let's retrieve the execution history to see all the checkpoints that were created.

**What is a checkpoint?**
A checkpoint is a snapshot of the state at a specific point in execution. Each checkpoint has:
- `values`: The state at that point
- `next`: Which node(s) will execute next
- `config`: Configuration including a unique checkpoint ID
- `metadata`: Additional info (timestamp, source, etc.)

Checkpoints are returned in **reverse chronological order** (newest first).


```python
print("=" * 80)
print("EXPLORING EXECUTION HISTORY")
print("=" * 80)
print("\nRetrieving all checkpoints from the initial run...\n")

# Get state history (returns a generator)
history = list(research_app.get_state_history(config))

print(f"Found {len(history)} checkpoints (in reverse chronological order)\n")

# Display each checkpoint
for i, checkpoint in enumerate(history):
    print(f"Checkpoint {i}:")
    print(f"  Next node(s): {checkpoint.next}")
    print(f"  Direction in state: {checkpoint.values.get('direction')}")
    print(f"  Has queries: {bool(checkpoint.values.get('generated_queries'))}")
    print(f"  Has search results: {bool(checkpoint.values.get('search_results'))}")
    print(f"  Has report: {bool(checkpoint.values.get('final_report'))}")
    print(f"  Checkpoint ID: {checkpoint.config['configurable']['checkpoint_id'][:8]}...")
    print()

print("=" * 80)
```

    ================================================================================
    EXPLORING EXECUTION HISTORY
    ================================================================================
    
    Retrieving all checkpoints from the initial run...
    
    Found 6 checkpoints (in reverse chronological order)
    
    Checkpoint 0:
      Next node(s): ()
      Direction in state: None
      Has queries: True
      Has search results: True
      Has report: True
      Checkpoint ID: 1f0c11e7...
    
    Checkpoint 1:
      Next node(s): ('generate_report',)
      Direction in state: None
      Has queries: True
      Has search results: True
      Has report: False
      Checkpoint ID: 1f0c11e7...
    
    Checkpoint 2:
      Next node(s): ('search_and_summarize',)
      Direction in state: None
      Has queries: True
      Has search results: False
      Has report: False
      Checkpoint ID: 1f0c11e7...
    
    Checkpoint 3:
      Next node(s): ('generate_queries',)
      Direction in state: None
      Has queries: False
      Has search results: False
      Has report: False
      Checkpoint ID: 1f0c11e7...
    
    Checkpoint 4:
      Next node(s): ('parse_request',)
      Direction in state: None
      Has queries: False
      Has search results: False
      Has report: False
      Checkpoint ID: 1f0c11e7...
    
    Checkpoint 5:
      Next node(s): ('__start__',)
      Direction in state: None
      Has queries: False
      Has search results: False
      Has report: False
      Checkpoint ID: 1f0c11e7...
    
    ================================================================================


## Part 10: Understanding Checkpoint Structure

Let's understand what each checkpoint represents:

| Index | Next Node(s) | Description | State |
|-------|-------------|-------------|-------|
| 0 | `()` | Workflow completed | Full state with final report |
| 1 | `('generate_report',)` | After search, before report | Has queries and search results |
| 2 | `('search_and_summarize',)` | After queries, before search | Has queries, no search results |
| 3 | `('generate_queries',)` | After parse, before query generation | No queries yet ← **Time Travel Target** |
| 4 | `('parse_request',)` | Before parse | Initial state |
| 5 | `(START,)` | Start of execution | Empty |

Checkpoint 3 is our target because:
1. The question has been validated
2. The state is initialized
3. But queries haven't been generated yet
4. We can add `direction` to influence query generation

Time traveling to checkpoint 3 lets us influence query generation without re-running parsing or re-initializing state.

## Part 11: Identify the Key Checkpoint

Let's programmatically find checkpoint 3 - the one right before query generation.

We identify it by looking for a checkpoint where:
- `next` contains only `('generate_queries',)`
- This means `parse_request` has completed
- And `generate_queries` is about to execute


```python
print("=" * 80)
print("IDENTIFYING TIME TRAVEL TARGET")
print("=" * 80)
print("\nSearching for checkpoint after parse_request, before generate_queries...\n")

# Find the checkpoint where generate_queries is next
target_checkpoint = None
for i, checkpoint in enumerate(history):
    if checkpoint.next == ('generate_queries',):
        target_checkpoint = checkpoint
        print(f"Found target checkpoint at index {i}!")
        print(f"\nCheckpoint details:")
        print(f"  Next node: {checkpoint.next}")
        print(f"  Current state:")
        print(f"    - research_question: {checkpoint.values['research_question']}")
        print(f"    - direction: {checkpoint.values.get('direction')}")
        print(f"    - generated_queries: {checkpoint.values['generated_queries']}")
        print(f"    - search_results: {checkpoint.values['search_results']}")
        print(f"    - final_report: {checkpoint.values['final_report']}")
        print(f"  Checkpoint ID: {checkpoint.config['configurable']['checkpoint_id']}")
        break

if not target_checkpoint:
    raise ValueError("Could not find target checkpoint!")

print("\n" + "=" * 80)
```

    ================================================================================
    IDENTIFYING TIME TRAVEL TARGET
    ================================================================================
    
    Searching for checkpoint after parse_request, before generate_queries...
    
    Found target checkpoint at index 3!
    
    Checkpoint details:
      Next node: ('generate_queries',)
      Current state:
        - research_question: What are AI agents and how do they work?
        - direction: None
        - generated_queries: []
        - search_results: {}
        - final_report: 
      Checkpoint ID: 1f0c11e7-4116-6e4e-8001-ba238e187243
    
    ================================================================================


## Part 12: Interactive Direction Choice

Now let's ask the user what direction they want to explore.

**Common directions:**
- **Technical implementation details**: Focus on how AI agents work internally
- **Business applications and ROI**: Focus on practical use cases and value
- **Historical context and evolution**: Focus on how AI agents developed over time
- **Ethical considerations**: Focus on risks, bias, and responsible use
- **Comparison with alternatives**: Focus on how AI agents differ from other approaches

The direction can be any phrase that guides the LLM's focus.


```python
print("=" * 80)
print("INTERACTIVE DIRECTION SELECTION")
print("=" * 80)
print("\nWe're about to time travel back and add a 'direction' to guide query generation.")
print("\nCommon direction examples:")
print("  - 'technical implementation details'")
print("  - 'business applications and ROI'")
print("  - 'historical context and evolution'")
print("  - 'ethical considerations'")
print("  - 'comparison with traditional systems'")
print("\nThe direction can be any phrase that describes the focus you want.\n")

# Get direction from user
user_direction = input("Enter your desired research direction (or press Enter for 'technical implementation details'): ").strip()

# Use default if empty
if not user_direction:
    user_direction = "technical implementation details"
    print(f"\nUsing default direction: '{user_direction}'")
else:
    print(f"\nUsing your direction: '{user_direction}'")

print("\n" + "=" * 80)
```

    ================================================================================
    INTERACTIVE DIRECTION SELECTION
    ================================================================================
    
    We're about to time travel back and add a 'direction' to guide query generation.
    
    Common direction examples:
      - 'technical implementation details'
      - 'business applications and ROI'
      - 'historical context and evolution'
      - 'ethical considerations'
      - 'comparison with traditional systems'
    
    The direction can be any phrase that describes the focus you want.
    


    Enter your desired research direction (or press Enter for 'technical implementation details'):  business applications and roi


    
    Using your direction: 'business applications and roi'
    
    ================================================================================


## Part 13: Update State with Direction (Time Travel!)

Now we'll update the state at our target checkpoint.

**What we're doing:**
1. Take the target checkpoint (before query generation)
2. Add the `direction` field to its state
3. Use `as_node="parse_request"` to specify where execution should resume from
4. Create a new checkpoint with the modified state
5. Get back a new config pointing to this checkpoint

**Understanding `as_node`:**

The `as_node` parameter tells the workflow which node "produced" this updated state:

```python
research_app.update_state(
    checkpoint.config,
    values={"direction": "..."},
    as_node="parse_request"
)
```

This ensures:
- The workflow knows to continue from after `parse_request`
- The next node (`generate_queries`) will execute with the updated state
- New queries will be generated (not reused from cache)

**Important notes:**
- This doesn't modify the original timeline
- It creates a new branch from that checkpoint
- The original execution is preserved
- You can create multiple branches from the same checkpoint


```python
print("=" * 80)
print("TIME TRAVEL: Updating State at Target Checkpoint")
print("=" * 80)
print(f"\nAdding direction: '{user_direction}'")
print("\nThis will:")
print("  1. Create a NEW checkpoint with direction added")
print("  2. Branch from the original timeline")
print("  3. Keep the original execution intact")
print("  4. Tell the workflow to continue from after parse_request")
print("\nUpdating state...\n")

# Update the state at the target checkpoint
new_config = research_app.update_state(
    target_checkpoint.config,
    values={"direction": user_direction},
    as_node="parse_request"
)

print("State updated successfully!")
print(f"\nNew checkpoint created with ID: {new_config['configurable']['checkpoint_id']}")
print(f"Original checkpoint ID: {target_checkpoint.config['configurable']['checkpoint_id']}")
print("\nThese are different checkpoints - we've created a branch!")
print("\n" + "=" * 80)
```

    ================================================================================
    TIME TRAVEL: Updating State at Target Checkpoint
    ================================================================================
    
    Adding direction: 'business applications and roi'
    
    This will:
      1. Create a NEW checkpoint with direction added
      2. Branch from the original timeline
      3. Keep the original execution intact
      4. Tell the workflow to continue from after parse_request
    
    Updating state...
    
    State updated successfully!
    
    New checkpoint created with ID: 1f0c11e9-77d8-67fa-8002-23c78e66e86f
    Original checkpoint ID: 1f0c11e7-4116-6e4e-8001-ba238e187243
    
    These are different checkpoints - we've created a branch!
    
    ================================================================================


## Part 14: Resume Execution from Modified Checkpoint

Now we resume execution from the modified checkpoint.

**What happens:**
1. The workflow picks up from the checkpoint (after parse_request)
2. `generate_queries_node` sees the `direction` field
3. It adapts its prompt to focus on that direction
4. LLM generates queries aligned with the direction
5. Rest of workflow executes normally with these new queries

We pass `None` as the input state because we're resuming from a checkpoint, not starting fresh. The workflow loads state from the checkpoint automatically.


```python
print("=" * 80)
print("RESUMING EXECUTION FROM MODIFIED CHECKPOINT")
print("=" * 80)
print(f"\nDirection: '{user_direction}'")
print("\nResuming workflow...\n")

# Resume execution from the modified checkpoint
# Pass None because we're resuming, not starting fresh
alternative_result = research_app.invoke(None, new_config)

print("\n" + "=" * 80)
print("ALTERNATIVE TIMELINE RESULTS")
print("=" * 80)

print(f"\nDirection: {alternative_result['direction']}")

print("\nGenerated Queries:")
for i, query in enumerate(alternative_result["generated_queries"], 1):
    print(f"  {i}. {query}")

print("\nFinal Report:")
print(alternative_result["final_report"])

print("\n" + "=" * 80)
```

    13:56:00 - research_workflow - INFO - [generate_queries] Processing question: What are AI agents and how do they work?
    13:56:00 - research_workflow - INFO - [generate_queries] Using direction: 'business applications and roi'


    ================================================================================
    RESUMING EXECUTION FROM MODIFIED CHECKPOINT
    ================================================================================
    
    Direction: 'business applications and roi'
    
    Resuming workflow...
    


    13:56:01 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    13:56:01 - research_workflow - INFO - [generate_queries] Generated 3 queries
    13:56:01 - research_workflow - INFO -   Query 1: AI agents business applications ROI
    13:56:01 - research_workflow - INFO -   Query 2: AI agents impact on business efficiency and ROI
    13:56:01 - research_workflow - INFO -   Query 3: Case studies on AI agents improving business ROI
    13:56:01 - research_workflow - INFO - [search] Executing 3 searches...
    13:56:01 - research_workflow - INFO - [search] Query 1/3: AI agents business applications ROI
    13:56:03 - research_workflow - INFO - [search] Found 3 results
    13:56:03 - research_workflow - INFO - [search] Query 2/3: AI agents impact on business efficiency and ROI
    13:56:05 - research_workflow - INFO - [search] Found 3 results
    13:56:05 - research_workflow - INFO - [search] Query 3/3: Case studies on AI agents improving business ROI
    13:56:06 - research_workflow - INFO - [search] Found 3 results
    13:56:06 - research_workflow - INFO - [search] Completed 3 searches
    13:56:06 - research_workflow - INFO - [report] Synthesizing findings into final report...
    13:56:10 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    13:56:10 - research_workflow - INFO - [report] Report generated successfully
    13:56:10 - research_workflow - INFO - === Research completed for: What are AI agents and how do they work? ===


    
    ================================================================================
    ALTERNATIVE TIMELINE RESULTS
    ================================================================================
    
    Direction: business applications and roi
    
    Generated Queries:
      1. AI agents business applications ROI
      2. AI agents impact on business efficiency and ROI
      3. Case studies on AI agents improving business ROI
    
    Final Report:
    **Report on AI Agents: Business Applications and ROI**
    
    AI agents are sophisticated software programs designed to perform tasks autonomously, often simulating human interaction and decision-making processes. In the business context, these agents are increasingly being deployed to enhance operational efficiency and drive significant returns on investment (ROI). AI agents can be integrated into various business functions, such as customer service, HR management, and supply chain optimization. For instance, they can provide real-time support to customers in banking, assist employees in navigating complex HR policies, and streamline supply chain operations. By automating routine tasks and providing intelligent insights, AI agents help businesses reduce costs, improve service speed, and increase revenue, thereby delivering measurable ROI.
    
    The deployment of AI agents in business settings has shown promising results in terms of ROI. According to multiple case studies, businesses that have effectively implemented AI agents have experienced substantial cost savings and operational improvements. These agents outperform traditional methods by offering consistent and scalable solutions that can adapt to various business needs. However, it is important to note that only a fraction of AI initiatives have successfully delivered the expected ROI, as highlighted by the 2025 IBM Institute for Business Values C-suite Study. This underscores the importance of strategic planning and execution in the design, deployment, and scaling of AI agents to realize their full potential and achieve enterprise-level ROI. By focusing on practical tactics and clear use cases, businesses can harness the power of AI agents to transform operations and achieve high-impact results.
    
    ================================================================================


## Part 15: Compare Results Across Timelines

Now let's do a side-by-side comparison of the two timelines:
1. **Original timeline**: No direction, general queries
2. **Alternative timeline**: With direction, focused queries

**What to observe:**
- How queries changed based on direction
- How the final report's focus shifted


```python
print("=" * 80)
print("TIMELINE COMPARISON")
print("=" * 80)
print("\n")

# Compare research questions (should be the same)
print("Research Question:")
print(f"  {initial_result['research_question']}")
print("\n")

# Compare directions
print("Direction:")
print(f"  Original:    {initial_result.get('direction') or 'None'}")
print(f"  Alternative: {alternative_result.get('direction')}")
print("\n")

print("=" * 80)
```

    ================================================================================
    TIMELINE COMPARISON
    ================================================================================
    
    
    Research Question:
      What are AI agents and how do they work?
    
    
    Direction:
      Original:    None
      Alternative: business applications and roi
    
    
    ================================================================================


### Query Comparison

Let's compare the queries generated in each timeline:


```python
print("GENERATED QUERIES COMPARISON")
print("=" * 80)
print("\n")

# Get the queries from both timelines
original_queries = initial_result['generated_queries']
alternative_queries = alternative_result['generated_queries']

# Display side by side
max_queries = max(len(original_queries), len(alternative_queries))

for i in range(max_queries):
    print(f"Query {i + 1}:")
    print("-" * 80)
    
    if i < len(original_queries):
        print(f"  Original (no direction):")
        print(f"    {original_queries[i]}")
    else:
        print(f"  Original (no direction): -")
    
    print()
    
    if i < len(alternative_queries):
        print(f"  Alternative (with '{user_direction}'):")
        print(f"    {alternative_queries[i]}")
    else:
        print(f"  Alternative: -")
    
    print("\n")

print("=" * 80)
```

    GENERATED QUERIES COMPARISON
    ================================================================================
    
    
    Query 1:
    --------------------------------------------------------------------------------
      Original (no direction):
        1. "Overview of AI agents: definitions and types in artificial intelligence"
    
      Alternative (with 'business applications and roi'):
        AI agents business applications ROI
    
    
    Query 2:
    --------------------------------------------------------------------------------
      Original (no direction):
        2. "Mechanisms and algorithms behind the functioning of AI agents"
    
      Alternative (with 'business applications and roi'):
        AI agents impact on business efficiency and ROI
    
    
    Query 3:
    --------------------------------------------------------------------------------
      Original (no direction):
        3. "Applications and real-world examples of AI agents in various industries"
    
      Alternative (with 'business applications and roi'):
        Case studies on AI agents improving business ROI
    
    
    ================================================================================


### Report Comparison

Now let's compare the final reports generated from each timeline:


```python
print("FINAL REPORTS COMPARISON")
print("=" * 80)
print("\n")

print("ORIGINAL TIMELINE (No Direction):")
print("-" * 80)
print(initial_result['final_report'])
print("\n" * 2)

print("ALTERNATIVE TIMELINE (With Direction: '{}'):".format(user_direction))
print("-" * 80)
print(alternative_result['final_report'])
print("\n")

print("=" * 80)
```

    FINAL REPORTS COMPARISON
    ================================================================================
    
    
    ORIGINAL TIMELINE (No Direction):
    --------------------------------------------------------------------------------
    **Report on AI Agents and Their Functioning**
    
    AI agents are autonomous entities in artificial intelligence that perceive their environment through sensors and act upon that environment using actuators to achieve specific goals. These agents can range from simple rule-based systems to complex, learning-based models. They are designed to operate independently, making decisions based on the data they receive and the objectives they are programmed to fulfill. AI agents can be categorized into several types, including reactive agents, which respond to stimuli without internal states, and cognitive agents, which possess memory and learning capabilities to adapt over time.
    
    The functioning of AI agents relies on a combination of algorithms and mechanisms that enable them to process information and make decisions. These algorithms can include decision trees, neural networks, and reinforcement learning models, among others. The choice of algorithm depends on the complexity of the task and the environment in which the agent operates. For instance, in dynamic environments where learning from experience is crucial, reinforcement learning is often employed. This allows the agent to improve its performance by receiving feedback from its actions. In contrast, simpler environments might only require rule-based algorithms that follow predefined instructions.
    
    AI agents are widely used across various industries, demonstrating their versatility and effectiveness. In healthcare, AI agents assist in diagnosing diseases by analyzing medical data and suggesting treatment plans. In finance, they are employed for algorithmic trading and fraud detection. In customer service, AI agents, such as chatbots, handle inquiries and provide support, enhancing user experience. These applications highlight the transformative impact of AI agents, as they streamline processes, improve decision-making, and offer innovative solutions to complex problems.
    
    
    
    ALTERNATIVE TIMELINE (With Direction: 'business applications and roi'):
    --------------------------------------------------------------------------------
    **Report on AI Agents: Business Applications and ROI**
    
    AI agents are sophisticated software programs designed to perform tasks autonomously, often simulating human interaction and decision-making processes. In the business context, these agents are increasingly being deployed to enhance operational efficiency and drive significant returns on investment (ROI). AI agents can be integrated into various business functions, such as customer service, HR management, and supply chain optimization. For instance, they can provide real-time support to customers in banking, assist employees in navigating complex HR policies, and streamline supply chain operations. By automating routine tasks and providing intelligent insights, AI agents help businesses reduce costs, improve service speed, and increase revenue, thereby delivering measurable ROI.
    
    The deployment of AI agents in business settings has shown promising results in terms of ROI. According to multiple case studies, businesses that have effectively implemented AI agents have experienced substantial cost savings and operational improvements. These agents outperform traditional methods by offering consistent and scalable solutions that can adapt to various business needs. However, it is important to note that only a fraction of AI initiatives have successfully delivered the expected ROI, as highlighted by the 2025 IBM Institute for Business Values C-suite Study. This underscores the importance of strategic planning and execution in the design, deployment, and scaling of AI agents to realize their full potential and achieve enterprise-level ROI. By focusing on practical tactics and clear use cases, businesses can harness the power of AI agents to transform operations and achieve high-impact results.
    
    
    ================================================================================

```

---

## File: 4_9_prompt_optimization.md

```markdown
# Prompt Optimization Techniques for AI Agents

## Introduction

Prompt optimization is the art of crafting instructions that guide AI agents toward better reasoning and more reliable behavior. While modern LLMs like GPT-4o and Claude Sonnet 4.5 are highly capable and less prone to hallucination than earlier models, **strategic prompt optimization still significantly improves agent performance**.

**Why Prompt Optimization Matters:**
- Improves reasoning accuracy and tool selection
- Reduces hallucinations and made-up information
- Ensures consistent agent behavior across varied inputs
- Prevents premature stopping in multi-step workflows

**What You'll Learn:**

In this notebook, you'll learn the **Plan and Reflect** prompt optimization technique - a research-backed approach that encourages agents to think through tool selection before acting, then verify results.

We'll use streaming to make the agent's reasoning process visible, so you can see exactly how this optimization technique affects behavior.

**Prerequisites:**
- OpenAI API key stored in a `.env` file
- Familiarity with LangChain agents (from Level 2)
- Basic understanding of tool calling

## Setup: Load Dependencies

First, let's load our environment variables and import the necessary libraries.


```python
from dotenv import load_dotenv

load_dotenv()
```




    True




```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

print("Dependencies loaded successfully!")
```

    Dependencies loaded successfully!


## Create Weather Tools

Let's create two weather-related tools to give our agent more interesting capabilities:
1. **get_weather**: Returns current weather for a location
2. **get_forecast**: Returns a 3-day forecast for a location

These tools will help us demonstrate how prompt optimization affects tool selection and information handling.


```python
@tool
def get_weather(location: str) -> str:
    """Get current weather information for a specific location.
    
    Args:
        location: The city or location to get weather for
    
    Returns:
        A string describing the current weather conditions, or a message if data is not available
    """
    # Mock implementation with limited data
    weather_data = {
        "new york": "Sunny, 72°F",
        "london": "Cloudy, 59°F",
        "tokyo": "Clear, 68°F",
        "paris": "Rainy, 55°F",
    }
    
    location_key = location.lower().strip()
    
    if location_key in weather_data:
        return f"Weather in {location}: {weather_data[location_key]}"
    else:
        return f"Location not found"


@tool
def get_forecast(location: str) -> str:
    """Get 3-day weather forecast for a specific location.
    
    Args:
        location: The city or location to get forecast for
    
    Returns:
        A string with the 3-day forecast, or a message if data is not available
    """
    # Mock implementation with limited data
    forecast_data = {
        "new york": "Day 1: Sunny, 72°F | Day 2: Partly cloudy, 68°F | Day 3: Rainy, 65°F",
        "london": "Day 1: Cloudy, 59°F | Day 2: Rainy, 57°F | Day 3: Foggy, 56°F",
        "tokyo": "Day 1: Clear, 68°F | Day 2: Sunny, 70°F | Day 3: Partly cloudy, 67°F",
        "paris": "Day 1: Rainy, 55°F | Day 2: Cloudy, 58°F | Day 3: Sunny, 62°F",
    }
    
    location_key = location.lower().strip()
    
    if location_key in forecast_data:
        return f"3-day forecast for {location}: {forecast_data[location_key]}"
    else:
        return f"Forecast data not available for {location}"


tools = [get_weather, get_forecast]
print(f"Tools created: {[tool.name for tool in tools]}")
```

    Tools created: ['get_weather', 'get_forecast']


## Create Streaming Helper Function

To understand how prompt optimization affects agent behavior, we need to **see the agent's reasoning process**. We'll create a helper function that uses streaming to display:

- Which tools the agent decides to call
- What results the tools return
- The agent's final response

This visibility is crucial for understanding how different prompt optimizations change agent behavior.


```python
def ask_agent_with_streaming(agent, question: str):
    """Ask the agent a question and stream the response to show reasoning.
    
    Args:
        agent: The LangChain agent to query
        question: The question to ask
    """
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}\n")
    
    # Stream with 'updates' mode to see what changes at each step
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="updates"
    ):
        # Check if this is a model update (includes tool calls or final response)
        if "model" in chunk:
            messages = chunk["model"].get("messages", [])
            for msg in messages:
                # Check for tool calls
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        print(f"🔧 Tool Call: {tool_call['name']}")
                        print(f"   Input: {tool_call['args']}")
                # Check for final content
                elif hasattr(msg, 'content') and msg.content:
                    print(f"\n💬 Agent Response:\n{msg.content}")
        
        # Check if this is a tool result
        if "tools" in chunk:
            messages = chunk["tools"].get("messages", [])
            for msg in messages:
                if hasattr(msg, 'content'):
                    print(f"   Result: {msg.content}\n")
    
    print(f"\n{'='*60}\n")


print("Streaming helper function created!")
```

    Streaming helper function created!


---

# Technique: Plan and Reflect

## What is Plan and Reflect?

**Plan and Reflect** is a prompt optimization technique that encourages agents to:
1. **Plan**: Think through which tool to use and why before taking action
2. **Reflect**: Check if tool outputs make sense before proceeding

**Research shows** this technique provides a ~4% performance improvement by reducing impulsive tool selection and catching errors early.

## Creating an Agent with Plan and Reflect

Let's create an agent with a system prompt that includes Plan and Reflect instructions.


```python
# Configure the language model
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1
)

# System prompt with Plan and Reflect optimization
plan_and_reflect_prompt = """You are a helpful weather assistant.

Before using any tool:
1. Think through which tool is most appropriate for the user's question
2. Consider whether you need current weather or forecast data

After receiving tool results:
1. Check if the output makes sense and answers the user's question
2. If the tool returns "not available", acknowledge this to the user
3. Only provide information that you received from tools
"""

# Create agent with custom system prompt
agent_with_planning = create_agent(
    model=model.with_config(configurable={"system_prompt": plan_and_reflect_prompt}),
    tools=tools
)

print("Agent with Plan and Reflect created!")
```

    Agent with Plan and Reflect created!


## Example 1: Current Weather Query

Let's test with a simple current weather question. Watch how the agent:
- Selects the appropriate tool
- Uses the tool result to answer


```python
ask_agent_with_streaming(
    agent_with_planning,
    "What's the weather like in Tokyo right now?"
)
```

    
    ============================================================
    Question: What's the weather like in Tokyo right now?
    ============================================================
    
    🔧 Tool Call: get_weather
       Input: {'location': 'Tokyo'}
       Result: Weather in Tokyo: Clear, 68°F
    
    
    💬 Agent Response:
    The current weather in Tokyo is clear with a temperature of 68°F.
    
    ============================================================
    


## Example 2: Forecast Query

Now let's ask for a forecast. Notice how the agent should select the forecast tool instead of the current weather tool.


```python
ask_agent_with_streaming(
    agent_with_planning,
    "What will the weather be like in London over the next few days?"
)
```

    
    ============================================================
    Question: What will the weather be like in London over the next few days?
    ============================================================
    
    🔧 Tool Call: get_forecast
       Input: {'location': 'London'}
       Result: 3-day forecast for London: Day 1: Cloudy, 59°F | Day 2: Rainy, 57°F | Day 3: Foggy, 56°F
    
    
    💬 Agent Response:
    The 3-day weather forecast for London is as follows:
    
    - **Day 1:** Cloudy, 59°F
    - **Day 2:** Rainy, 57°F
    - **Day 3:** Foggy, 56°F
    
    ============================================================
    


## Example 3: Complex Query

Let's try a more complex question that requires understanding which tool is appropriate.


```python
ask_agent_with_streaming(
    agent_with_planning,
    "Should I bring an umbrella to Paris this week?"
)
```

    
    ============================================================
    Question: Should I bring an umbrella to Paris this week?
    ============================================================
    
    🔧 Tool Call: get_weather
       Input: {'location': 'Paris'}
    🔧 Tool Call: get_forecast
       Input: {'location': 'Paris'}
       Result: Weather in Paris: Rainy, 55°F
    
       Result: 3-day forecast for Paris: Day 1: Rainy, 55°F | Day 2: Cloudy, 58°F | Day 3: Sunny, 62°F
    
    
    💬 Agent Response:
    Yes, you should bring an umbrella to Paris this week. The current weather is rainy, and the forecast for the next few days includes rain on the first day, followed by cloudy and then sunny weather.
    
    ============================================================
    


## What Does Plan and Reflect Improve?

The Plan and Reflect optimization helps agents:

- **Better tool selection**: Think through which tool is appropriate before acting
- **Error detection**: Catch when tool outputs don't make sense
- **Appropriate responses**: Acknowledge when data isn't available
- **Multi-step reasoning**: Plan sequences of tool calls more effectively

**Research shows** this technique provides a ~4% performance improvement by reducing impulsive tool selection and catching errors early.

---

## Summary

In this notebook, you learned the **Plan and Reflect** prompt optimization technique:

1. **Planning Phase**: Instruct the agent to think through which tool to use before acting
2. **Reflection Phase**: Have the agent verify tool outputs make sense before responding

This technique improves tool selection accuracy and helps agents handle edge cases like unavailable data more gracefully.

**Next Steps:**
- In the "Try It Yourself" exercise, you'll implement another powerful technique: **Tool Usage Over Guessing**
- This technique prevents agents from making up information when tool data is unavailable
```

---

