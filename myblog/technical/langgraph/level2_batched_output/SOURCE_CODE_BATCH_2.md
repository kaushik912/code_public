# Source Code Batch

This file contains 5 source files.

---

## File: 2_16_create_test_cases.md

```markdown
# Create Test Cases with Expected Outputs for AI Agents

## Overview

In this tutorial, you'll learn how to create robust test cases for AI agents and their tools. Testing AI agents is fundamentally different from testing traditional software because agent behavior involves stochastic (probabilistic) elements from the language models.

## What You'll Learn

- **What is a test case**: Understanding input → expected output patterns
- **Why AI agent testing is different**: Deterministic vs. stochastic behavior
- **Anatomy of a test case**: The Arrange-Act-Assert (AAA) pattern
- **Testing individual tools**: Verify tool functions work correctly
- **Testing agent actions**: Check tool usage, parameters, and outputs
- **Writing good test cases**: Clear, focused, independent, and repeatable

## Prerequisites

- **API Keys Required**: You'll need `OPENAI_API_KEY`
  - OpenAI: https://platform.openai.com/api-keys
- **Required Packages**: `langchain`, `langchain-openai`, `pytest`, `python-dotenv`

## Setup Instructions

1. Create a `.env` file in your project directory
2. Add your API key:
   ```
   OPENAI_API_KEY=your-openai-key-here
   ```
3. Install required packages:
   ```bash
   pip install langchain langchain-openai pytest python-dotenv
   ```

## Understanding Test Cases

### What is a Test Case?

A **test case** is a specification that describes:
1. **Input**: What you provide to the system
2. **Expected Output**: What you expect the system to produce
3. **Verification**: How you check that the output matches expectations

**Example**: For a function `add(a, b)`:
- Input: `add(2, 3)`
- Expected Output: `5`
- Verification: `assert add(2, 3) == 5`

### Why AI Agent Testing is Different

Traditional software is **deterministic** - the same input always produces the same output.

AI agents are **stochastic** (probabilistic) - the language model may produce different outputs for the same input because:
- Temperature settings introduce randomness
- Model responses vary naturally
- Wording differs while meaning stays consistent

**Therefore**, when testing AI agents we focus on:
1. **Tool usage**: Was the correct tool called?
2. **Parameters**: Were the right arguments passed?
3. **Output structure**: Does the response contain expected elements?
4. **Semantic correctness**: Is the answer reasonable, not exact word matching?

### The Arrange-Act-Assert Pattern

All good tests follow the **AAA pattern**:

1. **Arrange**: Set up test data and preconditions
2. **Act**: Execute the code being tested
3. **Assert**: Verify the results match expectations

This pattern makes tests clear, readable, and maintainable.

## Step 1: Import Libraries and Load Environment Variables

First, we'll import all necessary libraries and load our API keys from the `.env` file.


```python
import os
from dotenv import load_dotenv
from typing import Dict, Any, List
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

print("Environment and libraries loaded successfully!")
```

    Environment and libraries loaded successfully!


## Step 2: Create Simple Tools for Testing

We'll create two simple tools that our agent can use:
1. **Calculator**: Performs basic arithmetic operations
2. **Temperature Converter**: Converts between Celsius and Fahrenheit

These tools are deliberately simple so we can focus on testing concepts rather than complex logic.


```python
@tool
def calculator(operation: str, a: float, b: float) -> float:
    """
    Performs basic arithmetic operations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
    
    Returns:
        The result of the operation
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }
    
    if operation not in operations:
        return f"Error: Unknown operation '{operation}'"
    
    return operations[operation](a, b)


@tool
def temperature_converter(temperature: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """
    Converts temperature between Celsius and Fahrenheit.
    
    Args:
        temperature: The temperature value to convert
        from_unit: Source unit (C or F)
        to_unit: Target unit (C or F)
    
    Returns:
        A dictionary with the conversion result
    """
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()
    
    if from_unit == to_unit:
        return {
            "original": temperature,
            "converted": temperature,
            "from_unit": from_unit,
            "to_unit": to_unit
        }
    
    if from_unit == "C" and to_unit == "F":
        converted = (temperature * 9/5) + 32
    elif from_unit == "F" and to_unit == "C":
        converted = (temperature - 32) * 5/9
    else:
        return {"error": f"Invalid units: {from_unit} to {to_unit}"}
    
    return {
        "original": temperature,
        "converted": round(converted, 2),
        "from_unit": from_unit,
        "to_unit": to_unit
    }

print("Tools created successfully!")
print(f"Tool 1: {calculator.name} - {calculator.description}")
print(f"Tool 2: {temperature_converter.name} - {temperature_converter.description}")
```

    Tools created successfully!
    Tool 1: calculator - Performs basic arithmetic operations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
    
    Returns:
        The result of the operation
    Tool 2: temperature_converter - Converts temperature between Celsius and Fahrenheit.
    
    Args:
        temperature: The temperature value to convert
        from_unit: Source unit (C or F)
        to_unit: Target unit (C or F)
    
    Returns:
        A dictionary with the conversion result


## Part 1: Testing Individual Tools

### Why Test Tools Separately?

Before testing an agent's use of tools, we should verify that the tools themselves work correctly. This is called **unit testing** - testing individual components in isolation.

Benefits:
- **Faster**: No LLM calls required
- **Deterministic**: Same input always produces same output
- **Cheaper**: No API costs
- **Easier debugging**: Failures point directly to tool logic

### Test Case 1: Calculator Tool - Addition


```python
def test_calculator_addition():
    """
    Test that the calculator can correctly add two numbers.
    
    This test follows the Arrange-Act-Assert pattern.
    """
    # ARRANGE: Set up test inputs
    operation = "add"
    a = 15
    b = 27
    expected_result = 42
    
    # ACT: Execute the tool
    result = calculator.invoke({
        "operation": operation,
        "a": a,
        "b": b
    })
    
    # ASSERT: Verify the result
    assert result == expected_result, f"Expected {expected_result}, but got {result}"
    print(f"✓ Test passed: {a} + {b} = {result}")

# Run the test
test_calculator_addition()
```

    ✓ Test passed: 15 + 27 = 42.0


### Test Case 2: Calculator Tool - Division

Let's test another operation to ensure our calculator handles different operations correctly.


```python
def test_calculator_division():
    """
    Test that the calculator can correctly divide two numbers.
    """
    # ARRANGE
    operation = "divide"
    a = 100
    b = 4
    expected_result = 25.0
    
    # ACT
    result = calculator.invoke({
        "operation": operation,
        "a": a,
        "b": b
    })
    
    # ASSERT
    assert result == expected_result, f"Expected {expected_result}, but got {result}"
    print(f"✓ Test passed: {a} / {b} = {result}")

# Run the test
test_calculator_division()
```

    ✓ Test passed: 100 / 4 = 25.0


### Test Case 3: Example of a Failing Test

Let's see what happens when a test fails. This helps you understand how to read error messages and debug issues.

**Note**: This test is intentionally designed to fail to demonstrate the testing process.


```python
def test_calculator_division_failing_example():
    """
    INTENTIONALLY FAILING TEST - Demonstrates what a test failure looks like.
    
    This test expects an incorrect result to show how assertion errors appear.
    """
    # ARRANGE
    operation = "divide"
    a = 100
    b = 4
    expected_result = 20.0  # WRONG! We know 100 / 4 = 25, not 20
    
    # ACT
    result = calculator.invoke({
        "operation": operation,
        "a": a,
        "b": b
    })
    
    # ASSERT
    try:
        assert result == expected_result, f"Expected {expected_result}, but got {result}"
        print(f"✓ Test passed: {a} / {b} = {result}")
    except AssertionError as e:
        print("✗ Test FAILED (as expected for this demo)!")
        print(f"  AssertionError: {e}")
        print(f"\n  What went wrong:")
        print(f"    - We expected: {expected_result}")
        print(f"    - We actually got: {result}")
        print(f"    - The test correctly caught this mismatch!")
        print(f"\n  How to fix:")
        print(f"    - Either fix the expected value (expected_result = 25.0)")
        print(f"    - Or fix the implementation if the tool is wrong")

# Run the failing test
test_calculator_division_failing_example()
```

    ✗ Test FAILED (as expected for this demo)!
      AssertionError: Expected 20.0, but got 25.0
    
      What went wrong:
        - We expected: 20.0
        - We actually got: 25.0
        - The test correctly caught this mismatch!
    
      How to fix:
        - Either fix the expected value (expected_result = 25.0)
        - Or fix the implementation if the tool is wrong


### Key Takeaways: Tool Testing

1. **Test tools in isolation** before integrating them into agents
2. **Use specific, known values** with predictable outcomes
3. **Verify both output values and structure** (e.g., dictionary keys)
4. **Learn from failures** - when tests fail, they show you exactly what's wrong
5. **Read assertion errors carefully** - they tell you expected vs. actual values
6. **Test edge cases** (like division by zero, invalid units)
7. **Keep tests independent** - each test should run without depending on others

### Test Case 4: Temperature Converter Tool

Now let's test the temperature converter to ensure it correctly converts between units.


```python
def test_temperature_converter_c_to_f():
    """
    Test that the temperature converter correctly converts Celsius to Fahrenheit.
    
    We know that 0°C = 32°F and 100°C = 212°F
    """
    # ARRANGE
    temperature = 0
    from_unit = "C"
    to_unit = "F"
    expected_result = 32
    
    # ACT
    result = temperature_converter.invoke({
        "temperature": temperature,
        "from_unit": from_unit,
        "to_unit": to_unit
    })
    
    # ASSERT
    assert "converted" in result, "Result should contain 'converted' key"
    assert result["converted"] == expected_result, f"Expected {expected_result}, but got {result['converted']}"
    assert result["from_unit"] == "C", "Source unit should be 'C'"
    assert result["to_unit"] == "F", "Target unit should be 'F'"
    
    print(f"✓ Test passed: {temperature}°{from_unit} = {result['converted']}°{to_unit}")

# Run the test
test_temperature_converter_c_to_f()
```

    ✓ Test passed: 0°C = 32.0°F


## Part 2: Testing Agent Actions

### Why Agent Testing is Different

When testing agents, we care about:
1. **Tool selection**: Did the agent choose the right tool?
2. **Parameter extraction**: Did the agent pass the correct arguments?
3. **Output quality**: Is the final response reasonable?

We **cannot** expect:
- Exact word-for-word responses (stochastic behavior)
- Same tool calling order every time
- Identical phrasing across runs

### Step 3: Create an Agent

Let's create an agent that can use our tools to answer questions.


```python
# Configure the language model
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0  # Use 0 for more deterministic behavior in tests
)

# Create the agent with tools
tools = [calculator, temperature_converter]
agent = create_agent(
    model,
    tools=tools,
    system_prompt="You are a helpful assistant with access to tools. Use them when needed to answer questions accurately."
)

print("Agent created successfully!")
print(f"Agent has access to {len(tools)} tools: {[tool.name for tool in tools]}")
```

    Agent created successfully!
    Agent has access to 2 tools: ['calculator', 'temperature_converter']


### Test Case 5: Agent Tool Usage - Was the Correct Tool Called?

Our first agent test verifies that the agent selects the appropriate tool for a given query.


```python
def test_agent_uses_calculator():
    """
    Test that the agent correctly identifies when to use the calculator tool.
    
    We verify:
    1. The calculator tool was called
    2. The tool was called at least once
    """
    # ARRANGE
    query = "What is 456 multiplied by 789?"
    
    # ACT
    result = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    
    # ASSERT
    # The result contains messages including tool calls
    messages = result.get("messages", [])
    assert len(messages) > 0, "Agent should return messages"
    
    # Extract tool calls from messages
    tool_calls = []
    for message in messages:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append(tool_call.get("name"))
    
    # Verify calculator was used
    assert "calculator" in tool_calls, f"Expected calculator to be called, but got tools: {tool_calls}"
    
    print(f"✓ Test passed: Agent correctly used calculator tool")
    print(f"  Tools called: {tool_calls}")
    # Get the final message content
    final_message = messages[-1].content if messages else ""
    print(f"  Final answer: {final_message[:100]}...")

# Run the test
test_agent_uses_calculator()
```

    ✓ Test passed: Agent correctly used calculator tool
      Tools called: ['calculator']
      Final answer: 456 multiplied by 789 is 359,784....


### Test Case 6: Agent Output Validation - Reasonable Response?

We should also verify that the agent's final output is reasonable. Since we can't expect exact text matches, we check for key elements.


```python
def test_agent_output_contains_answer():
    """
    Test that the agent's output contains the expected answer.
    
    We verify:
    1. The output exists and is non-empty
    2. The output contains the correct numerical answer
    3. The output is reasonable (not an error message)
    """
    # ARRANGE
    query = "What is 100 divided by 4?"
    expected_answer = 25  # We know 100 / 4 = 25
    
    # ACT
    result = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    
    # ASSERT
    messages = result.get("messages", [])
    assert len(messages) > 0, "Agent should return messages"
    
    # Get the final message content
    output = messages[-1].content if messages else ""
    
    # Check output exists and is non-empty
    assert output, "Output should not be empty"
    assert len(output) > 0, "Output should contain text"
    
    # Check that the answer appears in the output
    # We convert to string because the agent might format it differently
    assert str(expected_answer) in output or str(float(expected_answer)) in output, \
        f"Expected answer '{expected_answer}' not found in output: {output}"
    
    # Check it's not an error message
    assert "error" not in output.lower(), f"Output contains error: {output}"
    
    print(f"✓ Test passed: Agent provided correct answer")
    print(f"  Query: {query}")
    print(f"  Expected answer: {expected_answer}")
    print(f"  Agent response: {output}")

# Run the test
test_agent_output_contains_answer()
```

    ✓ Test passed: Agent provided correct answer
      Query: What is 100 divided by 4?
      Expected answer: 25
      Agent response: 100 divided by 4 is 25.


### Test Case 7: Comprehensive Agent Test - All Three Aspects

Let's create a comprehensive test that checks tool usage, parameters, and output all together. This combines what we learned from Test Cases 5 and 6.


```python
def test_agent_temperature_conversion_comprehensive():
    """
    Comprehensive test of agent behavior with temperature conversion.
    
    This test verifies all three critical aspects:
    1. Tool Usage: Was temperature_converter called?
    2. Parameters: Were the correct arguments passed?
    3. Output: Does the response contain the expected answer?
    """
    # ARRANGE
    query = "Convert 25 degrees Celsius to Fahrenheit"
    expected_tool = "temperature_converter"
    expected_temp = 25
    expected_from_unit = "C"
    expected_to_unit = "F"
    expected_result = 77  # 25°C = 77°F
    
    # ACT
    result = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    
    # ASSERT - Part 1: Tool Usage
    messages = result.get("messages", [])
    assert len(messages) > 0, "Agent should return messages"
    
    tool_call_found = False
    tool_input = None
    
    for message in messages:
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.get("name") == expected_tool:
                    tool_call_found = True
                    tool_input = tool_call.get("args", {})
                    break
    
    assert tool_call_found, f"Expected tool '{expected_tool}' was not called"
    
    print("✓ Part 1 passed: Correct tool was used")
    
    # ASSERT - Part 2: Parameters
    assert tool_input is not None, "Tool input should not be None"
    assert tool_input.get("temperature") == expected_temp, \
        f"Expected temperature={expected_temp} but got {tool_input.get('temperature')}"
    
    # Note: Agent might use lowercase, so we normalize
    from_unit = tool_input.get("from_unit", "")
    to_unit = tool_input.get("to_unit", "")
    assert from_unit.upper() == expected_from_unit, \
        f"Expected from_unit='{expected_from_unit}' but got '{from_unit}'"
    
    assert to_unit.upper() == expected_to_unit, \
        f"Expected to_unit='{expected_to_unit}' but got '{to_unit}'"
    
    print("✓ Part 2 passed: Correct parameters were passed")
    print(f"  Parameters: {tool_input}")
    
    # ASSERT - Part 3: Output Quality
    output = messages[-1].content if messages else ""
    assert output, "Output should not be empty"
    
    # Check that the expected answer appears in the output
    assert str(expected_result) in output or str(float(expected_result)) in output, \
        f"Expected result '{expected_result}' not found in output: {output}"
    
    assert "error" not in output.lower(), f"Output contains error: {output}"
    
    print("✓ Part 3 passed: Output contains correct answer")
    print(f"  Agent response: {output}")
    print("\n✓✓✓ All tests passed: Agent performed complete task correctly!")

# Run the comprehensive test
test_agent_temperature_conversion_comprehensive()
```

    ✓ Part 1 passed: Correct tool was used
    ✓ Part 2 passed: Correct parameters were passed
      Parameters: {'temperature': 25, 'from_unit': 'C', 'to_unit': 'F'}
    ✓ Part 3 passed: Output contains correct answer
      Agent response: 25 degrees Celsius is equal to 77 degrees Fahrenheit.
    
    ✓✓✓ All tests passed: Agent performed complete task correctly!

```

---

## File: 2_17_performance_metrics.md

```markdown
# Performance Metrics Tracking for AI Agents

This notebook demonstrates how to track key performance metrics when making calls to OpenAI using LangChain:
- **Latency**: Response time
- **Token Usage**: Input/output tokens
- **Cost**: API expenses
- **Success Rate**: Request success/failure tracking

We'll compare the latest GPT model family:
- **GPT-5**: Best for coding and agentic tasks
- **GPT-5 mini**: Faster, cheaper version for well-defined tasks
- **GPT-5 nano**: Fastest, cheapest for summarization and classification
- **GPT-4o**: Previous generation flagship model

## Setup


```python
import os
import time
from datetime import datetime
from typing import Dict, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
```


```python
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
```




    True




```python
# Example: Initialize a single LLM
# We'll initialize all models in the comparison example below
llm = ChatOpenAI(
    model="gpt-5-nano",  # Start with the most cost-effective option
    temperature=0.7
)
```

## Metrics Tracking Class


```python
class PerformanceMetrics:
    """Track performance metrics for LLM calls"""
    
    # OpenAI pricing (as of 2025, in USD per 1K tokens)
    # Note: Cached input pricing is not tracked in this simple implementation
    PRICING = {
        "gpt-5": {"input": 0.00125, "output": 0.01},
        "gpt-5-mini": {"input": 0.00025, "output": 0.002},
        "gpt-5-nano": {"input": 0.00005, "output": 0.0004},
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
    }
    
    def __init__(self):
        self.metrics: List[Dict] = []
        
    def track_call(self, model: str, prompt: str, llm: ChatOpenAI) -> Dict:
        """Track a single LLM call and return metrics"""
        start_time = time.time()
        
        try:
            # Make the LLM call with callbacks to capture token usage
            response = llm.invoke([HumanMessage(content=prompt)])
            
            end_time = time.time()
            latency = end_time - start_time
            
            # Extract token usage from response metadata
            usage_metadata = response.response_metadata.get('token_usage', {})
            input_tokens = usage_metadata.get('prompt_tokens', 0)
            output_tokens = usage_metadata.get('completion_tokens', 0)
            total_tokens = usage_metadata.get('total_tokens', 0)
            
            # Calculate cost - use gpt-4o as fallback if model not found
            pricing = self.PRICING.get(model, self.PRICING["gpt-4o"])
            input_cost = (input_tokens / 1000) * pricing["input"]
            output_cost = (output_tokens / 1000) * pricing["output"]
            total_cost = input_cost + output_cost
            
            metric = {
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "latency_ms": round(latency * 1000, 2),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "input_cost_usd": round(input_cost, 6),
                "output_cost_usd": round(output_cost, 6),
                "total_cost_usd": round(total_cost, 6),
                "success": True,
                "response": response.content
            }
            
        except Exception as e:
            end_time = time.time()
            latency = end_time - start_time
            
            metric = {
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "latency_ms": round(latency * 1000, 2),
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "input_cost_usd": 0,
                "output_cost_usd": 0,
                "total_cost_usd": 0,
                "success": False,
                "error": str(e)
            }
        
        self.metrics.append(metric)
        return metric
    
    def get_summary(self) -> Dict:
        """Calculate summary statistics across all tracked calls"""
        if not self.metrics:
            return {}
        
        successful_calls = [m for m in self.metrics if m["success"]]
        total_calls = len(self.metrics)
        
        return {
            "total_calls": total_calls,
            "successful_calls": len(successful_calls),
            "failed_calls": total_calls - len(successful_calls),
            "success_rate": round(len(successful_calls) / total_calls * 100, 2) if total_calls > 0 else 0,
            "avg_latency_ms": round(sum(m["latency_ms"] for m in successful_calls) / len(successful_calls), 2) if successful_calls else 0,
            "total_tokens": sum(m["total_tokens"] for m in successful_calls),
            "total_cost_usd": round(sum(m["total_cost_usd"] for m in successful_calls), 6)
        }
    
    def print_metric(self, metric: Dict):
        """Pretty print a single metric"""
        print(f"\n{'='*60}")
        print(f"Timestamp: {metric['timestamp']}")
        print(f"Model: {metric['model']}")
        print(f"Success: {metric['success']}")
        print(f"Latency: {metric['latency_ms']} ms")
        
        if metric['success']:
            print(f"\nToken Usage:")
            print(f"  Input: {metric['input_tokens']}")
            print(f"  Output: {metric['output_tokens']}")
            print(f"  Total: {metric['total_tokens']}")
            print(f"\nCost:")
            print(f"  Input: ${metric['input_cost_usd']:.6f}")
            print(f"  Output: ${metric['output_cost_usd']:.6f}")
            print(f"  Total: ${metric['total_cost_usd']:.6f}")
            print(f"\nResponse: {metric['response'][:100]}..." if len(metric['response']) > 100 else f"\nResponse: {metric['response']}")
        else:
            print(f"Error: {metric.get('error', 'Unknown error')}")
        
        print(f"{'='*60}\n")
    
    def print_summary(self):
        """Pretty print summary statistics"""
        summary = self.get_summary()
        
        print(f"\n{'='*60}")
        print("PERFORMANCE METRICS SUMMARY")
        print(f"{'='*60}")
        print(f"Total Calls: {summary['total_calls']}")
        print(f"Successful: {summary['successful_calls']}")
        print(f"Failed: {summary['failed_calls']}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"\nAverage Latency: {summary['avg_latency_ms']} ms")
        print(f"Total Tokens Used: {summary['total_tokens']}")
        print(f"Total Cost: ${summary['total_cost_usd']:.6f}")
        print(f"{'='*60}\n")
```

## Example: Comparing Model Family

We'll test the same prompt across all models to compare their performance and cost characteristics.


```python
# Initialize metrics tracker
metrics = PerformanceMetrics()

# Dynamically initialize LLMs for each model
model_names = ["gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4o"]
models = {
    model_name: ChatOpenAI(model=model_name, temperature=0.7) 
    for model_name in model_names
}

# Test prompt - a coding task suitable for comparison
test_prompt = """Write a Python function that takes a list of numbers and returns 
a dictionary with the following statistics: mean, median, min, max, and standard deviation. 
Include proper error handling."""
```


```python
# Run the same prompt across all three models
results = {}

for model_name, llm in models.items():
    print(f"\n{'='*60}")
    print(f"Testing {model_name.upper()}")
    print(f"{'='*60}")
    
    metric = metrics.track_call(model_name, test_prompt, llm)
    results[model_name] = metric
    metrics.print_metric(metric)
```

    
    ============================================================
    Testing GPT-5
    ============================================================
    
    ============================================================
    Timestamp: 2025-11-07T15:59:36.752275
    Model: gpt-5
    Success: True
    Latency: 29432.39 ms
    
    Token Usage:
      Input: 44
      Output: 1966
      Total: 2010
    
    Cost:
      Input: $0.000055
      Output: $0.019660
      Total: $0.019715
    
    Response: Here’s a robust Python function with validation and clear errors. It computes mean, median, min, max...
    ============================================================
    
    
    ============================================================
    Testing GPT-5-MINI
    ============================================================
    
    ============================================================
    Timestamp: 2025-11-07T16:00:07.984484
    Model: gpt-5-mini
    Success: True
    Latency: 31231.56 ms
    
    Token Usage:
      Input: 44
      Output: 1872
      Total: 1916
    
    Cost:
      Input: $0.000011
      Output: $0.003744
      Total: $0.003755
    
    Response: Here's a concise, robust Python function that computes mean, median, min, max, and (population) stan...
    ============================================================
    
    
    ============================================================
    Testing GPT-5-NANO
    ============================================================
    
    ============================================================
    Timestamp: 2025-11-07T16:00:35.352503
    Model: gpt-5-nano
    Success: True
    Latency: 27366.72 ms
    
    Token Usage:
      Input: 44
      Output: 3447
      Total: 3491
    
    Cost:
      Input: $0.000002
      Output: $0.001379
      Total: $0.001381
    
    Response: Here's a robust Python function that computes mean, median, min, max, and standard deviation for a l...
    ============================================================
    
    
    ============================================================
    Testing GPT-4O
    ============================================================
    
    ============================================================
    Timestamp: 2025-11-07T16:00:44.671063
    Model: gpt-4o
    Success: True
    Latency: 9318.33 ms
    
    Token Usage:
      Input: 45
      Output: 524
      Total: 569
    
    Cost:
      Input: $0.000112
      Output: $0.005240
      Total: $0.005353
    
    Response: To achieve the task of calculating statistics from a list of numbers and returning them as a diction...
    ============================================================
    


## Model Comparison Table

Let's create a comprehensive comparison table to visualize the performance and cost differences across the model family.


```python
# Create comparison table
comparison_data = []
for model_name, metric in results.items():
    comparison_data.append({
        "Model": model_name,
        "Latency (ms)": metric["latency_ms"],
        "Input Tokens": metric["input_tokens"],
        "Output Tokens": metric["output_tokens"],
        "Total Tokens": metric["total_tokens"],
        "Total Cost ($)": f"${metric['total_cost_usd']:.6f}",
        "Cost per Token ($)": f"${metric['total_cost_usd']/metric['total_tokens']:.8f}" if metric['total_tokens'] > 0 else "$0"
    })

# Display comparison table
print("\n" + "="*100)
print("MODEL FAMILY COMPARISON")
print("="*100)

# Table header
header = f"{'Model':<15} {'Latency (ms)':<15} {'Input Tokens':<15} {'Output Tokens':<15} {'Total Tokens':<15} {'Total Cost ($)':<18} {'Cost per Token ($)':<20}"
print(header)
print("-" * 100)

# Table rows
for row in comparison_data:
    print(f"{row['Model']:<15} {str(row['Latency (ms)']):<15} {str(row['Input Tokens']):<15} {str(row['Output Tokens']):<15} {str(row['Total Tokens']):<15} {row['Total Cost ($)']:<18} {row['Cost per Token ($)']:<20}")

print("="*100)
```

    
    ====================================================================================================
    MODEL FAMILY COMPARISON
    ====================================================================================================
    Model           Latency (ms)    Input Tokens    Output Tokens   Total Tokens    Total Cost ($)     Cost per Token ($)  
    ----------------------------------------------------------------------------------------------------
    gpt-5           29432.39        44              1966            2010            $0.019715          $0.00000981         
    gpt-5-mini      31231.56        44              1872            1916            $0.003755          $0.00000196         
    gpt-5-nano      27366.72        44              3447            3491            $0.001381          $0.00000040         
    gpt-4o          9318.33         45              524             569             $0.005353          $0.00000941         
    ====================================================================================================

```

---

## File: 2_1_instantiate_prebuilt_agent.md

```markdown
# Instantiating Prebuilt Agents with LangChain

## Introduction

Prebuilt agents are ready-to-use agent implementations that handle tool selection and execution automatically. In this notebook, you'll learn the basic pattern for creating and using an agent with LangChain's `create_agent` function.

**Prerequisites**: An OpenAI API key stored in a `.env` file

**What You'll Learn**:
- How to create an agent with `create_agent`
- How to define a simple tool
- How to invoke the agent with a request

## Step 1: Environment Setup

Load environment variables to access your API key.


```python
from dotenv import load_dotenv

load_dotenv()
```




    True



## Step 2: Import Required Libraries


```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
```

## Step 3: Configure the Language Model

Configure the model with a low temperature for consistent tool selection.


```python
model = ChatOpenAI(
    model="gpt-5",
    temperature=0.1
)
```

## Step 4: Create a Simple Tool

Tools are functions decorated with `@tool` that have type hints and a docstring. The agent reads the docstring to understand what the tool does.


```python
@tool
def get_weather(location: str) -> str:
    """Get current weather information for a specific location.
    
    Args:
        location: The city or location to get weather for
    
    Returns:
        A string describing the current weather conditions, or a message if data is not available
    """
    # Mock implementation - in production, call a real weather API
    weather_data = {
        "new york": "Sunny, 72°F",
        "london": "Cloudy, 59°F",
        "tokyo": "Clear, 68°F",
    }
    
    location_key = location.lower().strip()
    
    if location_key in weather_data:
        return f"Weather in {location}: {weather_data[location_key]}"
    else:
        return f"Weather data not available for {location}"
```

## Step 5: Create the Agent

Use `create_agent` to create the agent with the model and tools.


```python
agent = create_agent(
    model=model,
    tools=[get_weather]
)

print("Agent created successfully!")
```

    Agent created successfully!


## Step 6: Create a Helper Function & Run the Agent

Let's create a simple helper function that makes it easy to ask the agent questions and get responses.


```python
def ask_agent(question: str):
    """Helper function to ask the agent a question and print the answer."""
    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    
    # Extract and print the final answer
    final_message = result["messages"][-1]
    print(final_message.content)
```


```python
# Test with London
ask_agent("What's the weather like in London?")
```

    It’s currently cloudy in London, around 59°F (15°C). Would you like a short forecast for the rest of the day?



```python
ask_agent("What's the weather like in Singapore?")
```

    I’m not able to retrieve live weather for Singapore right now. Typically in November it’s hot and very humid (around 25–31°C/77–88°F, often feeling warmer) with frequent afternoon/evening thunderstorms and showers on many days. For up-to-the-minute conditions, check the Meteorological Service Singapore (weather.gov.sg) or the myENV app.

```

---

## File: 2_2_structured_output_tutorial.md

```markdown
# Structured Output for AI Agents: A Comprehensive Tutorial

## Learning Objectives

By the end of this notebook, you will be able to:
- Understand why structured output is essential for AI agent systems
- Implement structured output using OpenAI's JSON Schema with strict mode
- Use Pydantic models with LangChain for type-safe structured output
- Compare different approaches and choose the right one for your use case
- Handle validation and error cases effectively

## Prerequisites

- Basic Python knowledge
- Familiarity with LLMs and API calls
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)

## Required Libraries

```bash
pip install openai langchain-openai pydantic python-dotenv
```

## 1. Introduction: Why Structured Output Matters

### The Problem

Large Language Models (LLMs) are trained to generate natural language text. While this is powerful for human interaction, it creates challenges when building AI agent systems:

- **Unpredictable Format**: LLMs might return data in different formats each time
- **Parsing Complexity**: Extracting specific information from free-form text is error-prone
- **Type Safety**: No guarantees about data types or required fields
- **Integration Issues**: Other components in your system need reliable, predictable data

### The Solution: Structured Output

Structured output ensures that LLM responses conform to a predefined schema, providing:

1. **Predictability**: Always receive data in the expected format
2. **Type Safety**: Guaranteed data types (strings, integers, booleans, etc.)
3. **Validation**: Automatic checking of required fields and constraints
4. **Seamless Integration**: Easy to pass data between agent components
5. **Tool Calling**: Enables reliable function/tool invocation in agent workflows

### Two Main Approaches

We'll explore two powerful methods:

1. **OpenAI API with JSON Schema**: Direct API control with strict schema enforcement
2. **LangChain with Pydantic Models**: Higher-level abstraction with Python type hints

## 2. Setup and Imports

Let's start by importing the necessary libraries and setting up our environment.


```python
import os
import json
from openai import OpenAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Verify OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY environment variable not set!")
    print("Please set it before running the examples.")
else:
    print("OpenAI API key found. Ready to proceed!")
```

    OpenAI API key found. Ready to proceed!


## 3. Approach 1: OpenAI API with JSON Schema

### Overview

OpenAI's API supports structured outputs through the `response_format` parameter with:
- `type: "json_schema"` to specify the desired structure
- `strict: True` to guarantee schema compliance

### Use Case: User Information Extraction

We'll extract structured user information (name, age, email) from natural language text.

### 3.1 Important: Optional Fields with Strict Mode

When using `strict: true` mode in OpenAI's structured outputs, there's a key constraint:

**All properties MUST be included in the `required` array.**

This means you cannot have truly "optional" fields in the traditional JSON Schema sense. However, you can emulate optional fields using **union types with null**:

```json
{
  "properties": {
    "age": {
      "type": ["integer", "null"],
      "description": "Age or null if not provided"
    }
  },
  "required": ["name", "age", "email"]
}
```

This approach:
- Satisfies the strict mode requirement (all fields in `required`)
- Allows the model to return `null` when data is not available
- Maintains schema compliance and type safety

Let's see this in action:

### 3.2 Define the JSON Schema

First, we define our desired output structure using JSON Schema format with the union type approach for optional fields:


```python
# Define JSON Schema for user information
# Note: age uses union type ["integer", "null"] to allow null values
user_info_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "user_info",
        "schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The user's full name"
                },
                "age": {
                    "type": ["integer", "null"],
                    "description": "The user's age in years, or null if not provided"
                },
                "email": {
                    "type": "string",
                    "description": "The user's email address"
                }
            },
            "required": ["name", "age", "email"],
            "additionalProperties": False
        },
        "strict": True
    }
}

print("JSON Schema defined successfully!")
print("\nSchema structure:")
print(json.dumps(user_info_schema["json_schema"]["schema"], indent=2))
```

    JSON Schema defined successfully!
    
    Schema structure:
    {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "The user's full name"
        },
        "age": {
          "type": [
            "integer",
            "null"
          ],
          "description": "The user's age in years, or null if not provided"
        },
        "email": {
          "type": "string",
          "description": "The user's email address"
        }
      },
      "required": [
        "name",
        "age",
        "email"
      ],
      "additionalProperties": false
    }


### 3.3 Create a Helper Function for Structured Output

Let's create a reusable helper function to make API calls with structured output cleaner and more maintainable:


```python
def extract_with_structured_output(
    text: str,
    schema: dict,
    model: str = "gpt-5",
    system_message: str = "You are a helpful assistant that extracts structured information from text."
) -> dict:
    """
    Helper function to extract structured output using OpenAI API.
    
    Args:
        text: The input text to extract information from
        schema: The JSON schema defining the structure
        model: The OpenAI model to use
        system_message: System message to guide the model
        
    Returns:
        Dictionary containing the structured output
        
    Raises:
        Exception: If API call fails or JSON parsing fails
    """
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": text}
            ],
            response_format=schema
        )
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response: {e}")
    except Exception as e:
        raise Exception(f"API call failed: {e}")

print("Helper function created successfully!")
print("This function makes structured output extraction reusable and cleaner.")
```

    Helper function created successfully!
    This function makes structured output extraction reusable and cleaner.


### 3.4 Use the Helper Function

Now let's use our helper function to extract user information:


```python
# Example user input text
user_text = "Extract user info: John Doe, 30 years old, john.doe@example.com"

# System message to guide extraction
system_msg = "You are a helpful assistant that extracts user information from text."

# Use helper function
structured_output = extract_with_structured_output(
    text=user_text,
    schema=user_info_schema,
    system_message=system_msg
)

print("Input text:")
print(f"  {user_text}")
print("\nStructured output:")
print(json.dumps(structured_output, indent=2))

```

    Input text:
      Extract user info: John Doe, 30 years old, john.doe@example.com
    
    Structured output:
    {
      "name": "John Doe",
      "age": 30,
      "email": "john.doe@example.com"
    }


### 3.5 Testing with Multiple Inputs

Let's test the robustness of our structured output with various input formats:


```python
# Test cases with different input formats
test_cases = [
    "My name is Alice Smith, I'm 25, and you can reach me at alice.smith@email.com",
    "Bob Johnson, bob.j@company.org, age 42",
    "Contact: sarah.williams@domain.com, Name: Sarah Williams (no age provided)"
]

system_msg = "You are a helpful assistant that extracts user information from text."

for i, test_input in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"Test Case {i}")
    print(f"{'='*60}")
    print(f"Input: {test_input}")
    
    result = extract_with_structured_output(
        text=test_input,
        schema=user_info_schema,
        system_message=system_msg
    )
    
    print(f"\nOutput:")
    print(json.dumps(result, indent=2))
```

    
    ============================================================
    Test Case 1
    ============================================================
    Input: My name is Alice Smith, I'm 25, and you can reach me at alice.smith@email.com
    
    Output:
    {
      "name": "Alice Smith",
      "age": 25,
      "email": "alice.smith@email.com"
    }
    
    ============================================================
    Test Case 2
    ============================================================
    Input: Bob Johnson, bob.j@company.org, age 42
    
    Output:
    {
      "name": "Bob Johnson",
      "age": 42,
      "email": "bob.j@company.org"
    }
    
    ============================================================
    Test Case 3
    ============================================================
    Input: Contact: sarah.williams@domain.com, Name: Sarah Williams (no age provided)
    
    Output:
    {
      "name": "Sarah Williams",
      "age": null,
      "email": "sarah.williams@domain.com"
    }


## 4. Approach 2: LangChain with Pydantic Models

### Overview

LangChain provides a higher-level abstraction using Pydantic models:
- Define schemas using Python classes with type hints
- Use `with_structured_output()` method on chat models
- Automatic validation and type conversion
- More Pythonic and developer-friendly

### Use Case: Same User Information Extraction

We'll implement the same use case to compare approaches directly.

### 4.1 Define the Pydantic Model

Instead of JSON Schema, we define a Python class with type annotations:


```python
# Define the Pydantic model for user information
class UserInfo(BaseModel):
    """Model for extracting user information from text."""
    
    name: str = Field(
        description="The user's full name"
    )
    age: Optional[int] = Field(
        default=None,
        description="The user's age in years"
    )
    email: str = Field(
        description="The user's email address"
    )
    

print("Pydantic model defined successfully!")
```

    Pydantic model defined successfully!


### 4.2 Create Structured Output Model

Now let's create a LangChain model configured for structured output:


```python
# Initialize the base chat model
base_model = ChatOpenAI(
    model="gpt-5",
    temperature=0
)

# Create structured output model
structured_model = base_model.with_structured_output(UserInfo)

print("Structured output model created successfully!")
print("The model will now return UserInfo objects instead of text.")
```

    Structured output model created successfully!
    The model will now return UserInfo objects instead of text.


### 4.3 Invoke with Natural Language

Let's extract structured information using our Pydantic-based model:


```python
# Example user input
user_text = "Extract user info: John Doe, 30 years old, john.doe@example.com"

# Invoke the structured model
result = structured_model.invoke(user_text)

print("Input text:")
print(f"  {user_text}")
print("\nStructured output:")
print(f"  Type: {type(result)}")
print(f"  Result: {result}")
print("\nAccessing fields (with type safety):")
print(f"  Name: {result.name} (type: {type(result.name).__name__})")
print(f"  Age: {result.age} (type: {type(result.age).__name__})")
print(f"  Email: {result.email} (type: {type(result.email).__name__})")
print("\nConvert to dictionary:")
print(json.dumps(result.model_dump(), indent=2))
```

    Input text:
      Extract user info: John Doe, 30 years old, john.doe@example.com
    
    Structured output:
      Type: <class '__main__.UserInfo'>
      Result: name='John Doe' age=30 email='john.doe@example.com'
    
    Accessing fields (with type safety):
      Name: John Doe (type: str)
      Age: 30 (type: int)
      Email: john.doe@example.com (type: str)
    
    Convert to dictionary:
    {
      "name": "John Doe",
      "age": 30,
      "email": "john.doe@example.com"
    }


### 4.4 Testing with Various Inputs

Let's test with the same diverse inputs we used earlier:


```python
# Same test cases as before
test_cases = [
    "My name is Alice Smith, I'm 25, and you can reach me at alice.smith@email.com",
    "Bob Johnson, bob.j@company.org, age 42",
    "Contact: sarah.williams@domain.com, Name: Sarah Williams (no age provided)"
]

for i, test_input in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"Test Case {i}")
    print(f"{'='*60}")
    print(f"Input: {test_input}")
    
    result = structured_model.invoke(test_input)

    print(json.dumps(result.model_dump(), indent=2))
```

    
    ============================================================
    Test Case 1
    ============================================================
    Input: My name is Alice Smith, I'm 25, and you can reach me at alice.smith@email.com
    {
      "name": "Alice Smith",
      "age": 25,
      "email": "alice.smith@email.com"
    }
    
    ============================================================
    Test Case 2
    ============================================================
    Input: Bob Johnson, bob.j@company.org, age 42
    {
      "name": "Bob Johnson",
      "age": 42,
      "email": "bob.j@company.org"
    }
    
    ============================================================
    Test Case 3
    ============================================================
    Input: Contact: sarah.williams@domain.com, Name: Sarah Williams (no age provided)
    {
      "name": "Sarah Williams",
      "age": null,
      "email": "sarah.williams@domain.com"
    }

```

---

## File: 2_3_integrate_tools.md

```markdown
# Integrating Tavily Search Tool into a LangChain Agent

## Overview

In this tutorial, you'll learn how to integrate the **Tavily Search Tool** into a LangChain prebuilt agent. By the end of this notebook, you'll have a working agent that can autonomously decide when to search the web for information to answer user queries.

## What You'll Learn

- How to set up and configure the Tavily search tool
- How to create a prebuilt agent that can use external tools
- How to observe the agent making decisions about when to use web search

## Prerequisites

- **API Keys Required**: You'll need both `OPENAI_API_KEY` and `TAVILY_API_KEY`
  - OpenAI: https://platform.openai.com/api-keys
  - Tavily: https://tavily.com (free account available)
- **Required Packages**: `langchain`, `langchain-openai`, `langchain-tavily`, `python-dotenv`

## Setup Instructions

1. Create a `.env` file in your project directory
2. Add your API keys:
   ```
   OPENAI_API_KEY=your-openai-key-here
   TAVILY_API_KEY=your-tavily-key-here
   ```
3. Install required packages:
   ```bash
   pip install langchain langchain-openai langchain-tavily python-dotenv
   ```

## Step 1: Import Libraries and Load Environment Variables

First, we'll import all necessary libraries and load our API keys from the `.env` file using `python-dotenv`.


```python
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

# Load environment variables from .env file
load_dotenv()

# Verify API keys are loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY not found in environment variables")

print("API keys loaded successfully!")
```

    API keys loaded successfully!


## Step 2: Configure the Language Model

We'll create an instance of ChatOpenAI that will power our agent's reasoning capabilities. The agent uses this model to understand queries and decide when to use tools.


```python
# Configure the model with a low temperature for more consistent reasoning
model = ChatOpenAI(
    model="gpt-5",  # Using GPT-5 for reliable tool usage
    temperature=0.1   # Low temperature for more deterministic responses
)

print(f"Model configured: {model.model_name}")
```

    Model configured: gpt-5


## Step 3: Create the Tavily Search Tool

The Tavily search tool provides real-time web search capabilities. We'll configure it with parameters that control how searches are performed:

- **max_results**: Number of search results to return (default: 5)
- **search_depth**: "basic" for faster searches or "advanced" for more comprehensive results
- **include_raw_content**: Whether to include full page content (we'll keep this False for cleaner results)
- **include_images**: Whether to include images in results


```python
# Instantiate the Tavily search tool
search_tool = TavilySearch(
    max_results=5,
    search_depth="basic",  # Use "advanced" for more comprehensive results
    include_raw_content=False,
    include_images=False
)

print("Tavily search tool created successfully!")
print(f"Tool name: {search_tool.name}")
print(f"Tool description: {search_tool.description}")
```

    Tavily search tool created successfully!
    Tool name: tavily_search
    Tool description: A search engine optimized for comprehensive, accurate, and trusted results. Useful for when you need to answer questions about current events. It not only retrieves URLs and snippets, but offers advanced search depths, domain management, time range filters, and image search, this tool delivers real-time, accurate, and citation-backed results.Input should be a search query.


## Step 4: Create the Agent with Tavily Tool

Now we'll create a prebuilt agent using LangChain's `create_agent` function. This agent will:

1. Receive a user query
2. Reason about whether it needs to use the search tool
3. If needed, invoke the Tavily search tool
4. Synthesize the search results into a coherent answer

The agent automatically decides when to use the search tool based on the query.


```python
# Create the agent with the search tool
agent = create_agent(
    model=model,
    tools=[search_tool]  # Pass our Tavily search tool in a list
)

print("Agent created successfully!")
print(f"Agent has access to {len([search_tool])} tool(s)")
```

    Agent created successfully!
    Agent has access to 1 tool(s)


## Step 5: Create a Helper Function for Agent Interactions

To make it easier to interact with our agent, we'll create a helper function that:

- Takes a query string
- Invokes the agent with properly formatted messages
- Extracts and prints the final response

This function simplifies our testing and makes the examples more readable.


```python
def generate_and_print_response(agent, query):
    """
    Invoke the agent with a query and print the response.
    
    Args:
        agent: The LangChain agent instance
        query: The user query string
    """
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")
    
    # Invoke the agent with the query
    result = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    
    # Extract and print the final response
    final_message = result["messages"][-1]
    print(f"Response: {final_message.content}\n")
    
    return result

print("Helper function defined successfully!")
```

    Helper function defined successfully!


## Step 6: Test the Agent - Current Events Query

Let's test our agent with a query about recent developments. The agent should recognize that it needs current information and automatically use the Tavily search tool.


```python
# Example 1: Current events query
result1 = generate_and_print_response(
    agent,
    "What are the latest developments in artificial intelligence in 2025?"
)
```

    
    ============================================================
    Query: What are the latest developments in artificial intelligence in 2025?
    ============================================================
    
    Response: Here’s a concise rundown of notable AI developments in 2025, with sources for each item:
    
    - Frontier models and multimodality
      - OpenAI: Released GPT-4.5 (Feb), new image-generation API model (Apr), published Sora 2 video model research (Sep), and updated the GPT-5 system card with safety addendum (Oct) (openai.com/news; GPT-4.5: https://openai.com/index/introducing-gpt-4-5/; Image API: https://openai.com/index/image-generation-api/; Sora 2: https://openai.com/index/sora-2/; GPT-5 addendum: https://openai.com/index/gpt-5-system-card-sensitive-conversations/).
      - Google: Upgraded Gemini 2.5 Pro and introduced “Deep Think” reasoning mode; Veo 3.1 and 3.1 Fast video models entered public preview via the Gemini API; rolled out “AI Mode” in Search to US users (Google blog: https://blog.google/technology/google-deepmind/google-gemini-updates-io-2025/; Gemini API changelog: https://ai.google.dev/gemini-api/docs/changelog; The Verge I/O wrap: https://www.theverge.com/news/669408/google-io-2025-biggest-announcements-ai-gemini).
      - Meta: Shipped Llama 4 Scout and Llama 4 Maverick (weights downloadable), with a larger “Behemoth” model still in training (Meta AI blog: https://ai.meta.com/blog/llama-4-multimodal-intelligence/; CNBC: https://www.cnbc.com/2025/04/05/meta-debuts-new-llama-4-models-but-most-powerful-ai-model-is-still-to-come.html).
      - Anthropic: Tightened usage policies for agentic use and expanded “Claude for Financial Services” with Excel add-ins, market data connectors, and prebuilt agent skills (Usage policy: https://www.anthropic.com/news/usage-policy-update; Finance: https://www.anthropic.com/news/advancing-claude-for-financial-services).
    
    - Agentic AI and automation
      - Analyst/industry take: Agent stacks and orchestration are moving from pilots to production, but many initiatives face complexity; Gartner projects >40% of agentic AI projects will be canceled by end of 2027 (Gartner press release: https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027).
    
    - Productivity copilots and platform features
      - Microsoft: Continued rapid updates to Microsoft 365 Copilot (new search “AI Views,” Teams summaries, admin controls) and introduced Copilot Mode in Edge; ongoing vertical copilots and service integrations (TechCommunity Oct update: https://techcommunity.microsoft.com/blog/microsoft365copilotblog/what%E2%80%99s-new-in-microsoft-365-copilot--october-2025/4464046; Copilot blog release notes: https://www.microsoft.com/en-us/microsoft-copilot/blog/2025/08/07/release-notes-august-7-2025/).
    
    - On‑device and consumer AI
      - Apple: “Apple Intelligence” added live translation and system-wide AI features at WWDC; later introduced the M5 chip with a Neural Accelerator per GPU core for faster on-device AI across MacBook Pro, iPad Pro, and Vision Pro (WWDC: https://www.apple.com/newsroom/2025/06/apple-intelligence-gets-even-more-powerful-with-new-capabilities-across-apple-devices/; M5: https://www.apple.com/newsroom/2025/10/apple-unleashes-m5-the-next-big-leap-in-ai-performance-for-apple-silicon/).
    
    - Creative AI and video generation
      - OpenAI Sora 2 (higher-fidelity text-to-video) and Google’s Veo 3.1 preview highlight rapid video model progress; Adobe launched new Firefly audio/video generation tools (Sora 2: https://openai.com/index/sora-2/; Veo 3.1: https://ai.google.dev/gemini-api/docs/changelog#video; Adobe MAX: https://news.adobe.com/news/2025/10/adobe-max-2025-firefly).
    
    - Chips and infrastructure
      - NVIDIA (GTC 2025): Announced Blackwell Ultra and next-gen “Vera Rubin” platforms targeting reasoning-heavy workloads; unveiled a Vera Rubin superchip pairing an 88‑core “Vera” CPU with two Rubin GPUs and SOCAMM memory modules (TechCrunch: https://techcrunch.com/2025/03/18/nvidia-announces-new-gpus-at-gtc-2025-including-rubin/; CRN wrap: https://www.crn.com/news/ai/2025/10-big-nvidia-gtc-2025-announcements-blackwell-ultra-rubin-ultra-dgx-spark-and-more; Tom’s Hardware: https://www.tomshardware.com/pc-components/gpus/nvidia-reveals-vera-rubin-superchip-for-the-first-time-incredibly-compact-board-features-88-core-vera-cpu-two-rubin-gpus-and-8-socamm-modules).
    
    - Regulation and policy
      - EU AI Act: Implementation milestones across 2025–2027, including early obligations for general‑purpose AI and high‑risk systems; European Parliament summary notes standards work and timeline (EPRS brief: https://www.europarl.europa.eu/RegData/etudes/ATAG/2025/772906/EPRS_ATA(2025)772906_EN.pdf; timeline explainer: https://artificialintelligenceact.eu/implementation-timeline/).
      - United States: Executive Order 14179 (Jan) directed an AI action plan to “remove barriers” and accelerate US AI leadership; the administration released an AI Action Plan in July outlining near‑term federal priorities (EO page: https://www.whitehouse.gov/presidential-actions/2025/01/removing-barriers-to-american-leadership-in-artificial-intelligence/; plan overview via Covington: https://www.insidegovernmentcontracts.com/2025/08/july-2025-ai-developments-under-the-trump-administration/).
    
    If you want, I can tailor a deeper dive to any area above (e.g., model benchmarks, enterprise agent architectures, or compliance timelines).
    


## Step 7: Test the Agent - Specific Topic Search

Now let's try a more specific query about a particular technology or company. The agent should use Tavily to find up-to-date information.


```python
# Example 2: Specific topic search
result2 = generate_and_print_response(
    agent,
    "What are the key features of LangChain's newest releases?"
)
```

    
    ============================================================
    Query: What are the key features of LangChain's newest releases?
    ============================================================
    
    Response: Here’s a concise roundup of the most recent LangChain/LangGraph releases and what they add:
    
    Core LangChain v1 (Python and JS)
    - New standard agent API: create_agent / createAgent replaces older patterns, making agent building simpler and more consistent across providers and platforms [Docs v1 (Python, JS), v1 migration guides].
    - Built-in middleware: first-class patterns for PII redaction, summarization/auto-condense, and human-in-the-loop approvals/intercepts; replaces pre/post model hooks [Docs v1].
    - Standard “content blocks”: a unified, multimodal message format used across models and tools for more reliable interactions [v1 announcement].
    - Updated semantics and migration tweaks: system_prompt naming, structured output now via Tool/Provider strategies (prompted structured output removed), updated return types, and streaming node rename [v1 migration guides].
    - New docs site and migration guides to v1 [v1 announcement, Docs v1].
    
    Agent runtime via LangGraph (shipped with v1 focus)
    - Durable execution + persistence: checkpointing, short-term memory, resumability, streaming, and human-in-the-loop patterns are native through LangGraph under the hood [v1 announcement].
    - Prebuilt agents: LangGraph 0.3 introduced prebuilt agents to speed up production agent creation [LangGraph 0.3 blog].
    - Checkpointers 3.0 and runtime improvements: checkpoint cloning, checkpoint_during, task result population, improved cache key hashing; better ergonomics across Python and JS [LangGraph releases, LangGraph.js releases, Release Week recap].
    
    Ecosystem and SDK updates (highlights)
    - Model profiles: new langchain-model-profiles with a profile property on BaseChatModel for standardized model capability descriptions/config [LangChain GitHub releases].
    - Tooling enhancements: better tool metadata, support for custom tools, and more robust streaming of tool-call chunks (especially in JS) [LangChain.js releases].
    - Provider adapters: continued updates across OpenAI/Anthropic/etc., including “reasoning” model support flags and prompt cache key support in JS packages [LangChain.js releases].
    
    Sources
    - LangChain & LangGraph v1 announcement: blog.langchain.com/langchain-langchain-1-0-alpha-releases/
    - What’s new in v1 (Python): docs.langchain.com/oss/python/releases/langchain-v1
    - What’s new in v1 (JS): docs.langchain.com/oss/javascript/releases/langchain-v1
    - v1 migration guides: docs.langchain.com/oss/python/migrate/langchain-v1 and docs.langchain.com/oss/javascript/migrate/langchain-v1
    - LangChain Python releases: github.com/langchain-ai/langchain/releases
    - LangGraph releases: github.com/langchain-ai/langgraph/releases and github.com/langchain-ai/langgraphjs/releases
    - LangGraph 0.3 prebuilt agents: blog.langchain.dev/langgraph-0-3-release-prebuilt-agents
    - LangGraph release week recap: blog.langchain.dev/langgraph-release-week-recap
    - LangChain.js releases: github.com/langchain-ai/langchainjs/releases
    
    If you tell me whether you’re on Python or JS (and which providers you use), I can map these changes to concrete upgrade steps and code snippets.
    

```

---

