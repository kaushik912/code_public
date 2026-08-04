# Source Code Batch

This file contains 5 source files.

---

## File: 4_10_context_window_management.md

```markdown
# Managing Context Window Limits in AI Agents

## Introduction

When building AI agents that engage in extended conversations, one of the most critical challenges is managing **context window limits**. Every language model has a maximum number of tokens it can process in a single request, which includes both the input (conversation history, system prompts, tool definitions) and the output.

### What are Context Windows?

A context window is the maximum amount of text (measured in tokens) that a language model can process at once. For example:

- GPT-3.5-turbo: 16,385 tokens
- GPT-4o-mini: 128,000 tokens
- GPT-4: 8,192 tokens (standard) or 128,000 tokens (turbo)

### Why Context Window Management Matters

1. **Performance**: Larger contexts take longer to process and increase latency
2. **Cost**: You pay per token, so unnecessary context directly increases costs
3. **Overflow**: Exceeding the limit causes errors and conversation failures
4. **Quality**: Too much irrelevant context can confuse the model and degrade response quality

### Two Core Strategies

In this notebook, we'll explore two fundamental approaches to managing context:

1. **Trimming**: Remove older messages to keep only recent conversation history
   - Fast and simple
   - No additional API calls
   - Loses information from removed messages

2. **Summarization**: Compress older messages into summaries while preserving key information
   - Retains important context
   - Requires additional API calls
   - More sophisticated but higher cost

### Learning Objectives

By the end of this notebook, you'll be able to:
- Understand when context window limits become a problem
- Implement message trimming using the `@before_model` decorator
- Implement conversation summarization using `SummarizationMiddleware`
- Choose the right strategy for your specific use case
- Combine both approaches for optimal results

## Setup

First, let's import the necessary libraries and configure our environment. We'll be using LangChain's `create_agent` function with middleware to manage context.

Key imports:
- `create_agent`: The main function for creating agents with middleware support
- `@before_model`: Decorator for running functions before model invocation
- `SummarizationMiddleware`: Pre-built middleware for automatic summarization
- `InMemorySaver`: Checkpoint storage for conversation persistence


```python
import os
from dotenv import load_dotenv
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig

# Load environment variables
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

print("Setup complete! All required libraries imported successfully.")
```

    Setup complete! All required libraries imported successfully.


## Understanding Middleware in LangChain Agents

Before diving into context management strategies, let's understand **middleware** - a powerful pattern for modifying agent behavior.

### What is Middleware?

Middleware are functions that intercept and potentially modify the agent's execution at specific points. They allow you to:
- Transform state before it reaches the model
- Process outputs after the model responds
- Implement cross-cutting concerns like logging, monitoring, or context management

### Key Middleware Decorators

LangChain provides two main decorators:

1. **`@before_model`**: Runs before the model is invoked
   - Receives current `AgentState` and `Runtime`
   - Can modify messages, add/remove context, etc.
   - Return `dict` with changes or `None` to keep state unchanged

2. **`@after_model`**: Runs after the model responds
   - Receives the model's response
   - Can modify or process the output
   - Useful for logging, validation, post-processing

### The Return Pattern

Middleware functions follow a simple pattern:

```python
@before_model
def my_middleware(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    # Check if modifications are needed
    if no_changes_needed:
        return None  # Keep state as-is
    
    # Make modifications
    modified_state = {...}
    return modified_state  # Apply changes
```

### Passing Middleware to Agents

Middleware is passed as a list to the `middleware` parameter:

```python
agent = create_agent(
    model=model,
    tools=[],
    middleware=[middleware_func1, middleware_func2],  # Applied in order
    checkpointer=InMemorySaver(),
)
```

## Strategy 1: Message Trimming

### When to Use Trimming

Message trimming is ideal when:
- You need a simple, fast solution with no additional API calls
- Recent conversation context is most important
- Older messages become irrelevant over time
- You want minimal computational overhead and cost
- Your use case is transactional (e.g., single-issue support)

### How Trimming Works

The trimming strategy:
1. Keeps the first message (often contains important context or instructions)
2. Removes middle messages when the count exceeds a threshold
3. Always keeps the most recent messages
4. Uses `RemoveMessage` with `REMOVE_ALL_MESSAGES` to efficiently clear old messages

### The Trade-off

**Advantage**: Fast, free (no extra API calls), simple to implement

**Disadvantage**: You permanently lose information from trimmed messages - the agent cannot recall anything from removed context

### Implementing Trimming with `@before_model`

Let's create middleware that automatically trims messages before each model call.


```python
@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """
    Keep only the last few messages to fit within context window.
    
    Strategy:
    - Keep last 4 messages (most recent conversation)
    - Remove everything older
    
    Args:
        state: Current agent state containing messages
        runtime: Runtime object (not used in this example)
    
    Returns:
        Dict with modified messages, or None if no changes needed
    """
    messages = state["messages"]
    
    # If we have 4 or fewer messages, no trimming needed
    if len(messages) <= 4:
        return None  # Keep state unchanged
    
    # Keep only the last 4 messages (most recent context)
    recent_messages = messages[-4:]
    
    # Return the trimmed message list
    # Use RemoveMessage with REMOVE_ALL_MESSAGES to clear, then add back what we want
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *recent_messages
        ]
    }

# Create model instance
model = ChatOpenAI(model="gpt-4o")

# Create agent with trimming middleware
agent_trimming = create_agent(
    model=model,
    tools=[],  # No tools for this demonstration
    middleware=[trim_messages],  # Apply our trimming middleware
    checkpointer=InMemorySaver(),  # Enable conversation persistence
)

print("Agent with trimming middleware created successfully!")
print(f"This agent will keep at most 4 messages (last 4 turns) in memory.")
```

    Agent with trimming middleware created successfully!
    This agent will keep at most 4 messages (last 4 turns) in memory.


### Testing the Trimming Strategy

Let's simulate a long conversation about travel planning and observe how trimming affects the agent's memory.


```python
# Configuration with thread ID for conversation persistence
config: RunnableConfig = {"configurable": {"thread_id": "trimming_demo"}}

# Simulate a multi-turn conversation
conversation = [
    "Hi! My name is Sajal and I'm planning a trip to Japan.",
    "I'm interested in visiting Tokyo first.",
    "What are the must-see places in Tokyo?",
    "How about food recommendations?",
    "What's the best way to get around Tokyo?",
    "Should I get a JR Pass?",
]

print("Starting conversation with trimming agent...")
print("=" * 80)

for i, msg in enumerate(conversation, 1):
    result = agent_trimming.invoke(
        {"messages": [HumanMessage(content=msg)]}, 
        config
    )
    
    # Get the last AI message
    ai_response = result['messages'][-1].content
    
    print(f"\nTurn {i}:")
    print(f"User: {msg}")
    print(f"Agent: {ai_response[:100]}...")
    print("-" * 80)

print("\nConversation complete!")
```

    Starting conversation with trimming agent...
    ================================================================================
    
    Turn 1:
    User: Hi! My name is Sajal and I'm planning a trip to Japan.
    Agent: Hi Sajal! That sounds like an exciting trip. Japan is a fantastic destination with a rich culture, i...
    --------------------------------------------------------------------------------
    
    Turn 2:
    User: I'm interested in visiting Tokyo first.
    Agent: Great choice! Tokyo is a vibrant city with endless things to see and do. Here are some suggestions t...
    --------------------------------------------------------------------------------
    
    Turn 3:
    User: What are the must-see places in Tokyo?
    Agent: Tokyo is full of fascinating places to explore, and while each visitor may have different interests,...
    --------------------------------------------------------------------------------
    
    Turn 4:
    User: How about food recommendations?
    Agent: Tokyo is a culinary paradise with a diverse range of food options, from traditional Japanese cuisine...
    --------------------------------------------------------------------------------
    
    Turn 5:
    User: What's the best way to get around Tokyo?
    Agent: Tokyo boasts one of the world's most efficient and comprehensive public transportation systems, maki...
    --------------------------------------------------------------------------------
    
    Turn 6:
    User: Should I get a JR Pass?
    Agent: Whether or not you should get a Japan Rail (JR) Pass depends on your travel plans within Japan. The ...
    --------------------------------------------------------------------------------
    
    Conversation complete!


### Verifying Trimming Behavior

Now let's examine what messages are actually stored in memory after trimming has been applied.


```python
# Get the current state to inspect memory
state = agent_trimming.get_state(config)
messages = state.values["messages"]

print(f"Total messages in memory: {len(messages)}")
print(f"\nMessage breakdown:")

for i, msg in enumerate(messages, 1):
    msg_type = msg.__class__.__name__
    content_preview = msg.content[:70] if len(msg.content) > 70 else msg.content
    print(f"  {i}. {msg_type}: {content_preview}...")

print(f"\nAs expected, we should see 5 messages in the state, the 4 messages after trimming BEFORE we invoked the agent one more time, and the latest agent response.")
```

    Total messages in memory: 5
    
    Message breakdown:
      1. AIMessage: Tokyo is a culinary paradise with a diverse range of food options, fro...
      2. HumanMessage: What's the best way to get around Tokyo?...
      3. AIMessage: Tokyo boasts one of the world's most efficient and comprehensive publi...
      4. HumanMessage: Should I get a JR Pass?...
      5. AIMessage: Whether or not you should get a Japan Rail (JR) Pass depends on your t...
    
    As expected, we should see 5 messages in the state, the 4 messages after trimming BEFORE we invoked the agent one more time, and the latest agent response.


### Testing Information Loss

The key limitation of trimming: information from removed messages is permanently lost. Let's test this by asking about something mentioned early in the conversation.


```python
# Ask about the first message (likely trimmed if conversation was long enough)
result = agent_trimming.invoke(
    {"messages": [HumanMessage(content="What's my name?")]},
    config
)

print("Testing recall of early conversation...")
print(f"\nUser: What's my name?")
print(f"\nAgent: {result['messages'][-1].content}")

print("\n" + "=" * 80)
print("OBSERVATION:")
print("If the early messages were trimmed, the agent may not the name was mentioned.")
print("This demonstrates the information loss inherent in the trimming strategy.")
print("=" * 80)
```

    Testing recall of early conversation...
    
    User: What's my name?
    
    Agent: I'm sorry, but I don't have access to personal data about users unless it's shared with me in the course of our conversation. That includes your name or any other personal details. If there's anything else you'd like to know or discuss, feel free to ask!
    
    ================================================================================
    OBSERVATION:
    If the early messages were trimmed, the agent may not the name was mentioned.
    This demonstrates the information loss inherent in the trimming strategy.
    ================================================================================


## Strategy 2: Conversation Summarization

### When to Use Summarization

Summarization is better when:
- You need to preserve information from earlier in the conversation
- The conversation contains important context that spans many turns
- You're willing to trade additional API costs for better memory
- The agent needs to reference details from throughout the entire conversation
- Your use case involves complex, long-running interactions (planning, tutoring, analysis)

### How Summarization Works

The summarization strategy:
1. Monitors the total token count of conversation history
2. When tokens exceed a threshold, triggers summarization
3. Uses the LLM to create a concise summary of older messages
4. Replaces old messages with the summary
5. Keeps recent messages in full detail for immediate context

### The Trade-off

**Advantage**: Preserves key information from the entire conversation history

**Disadvantage**: Each summarization requires an additional LLM API call, increasing cost and latency

### Implementing Summarization with `SummarizationMiddleware`

LangChain provides a pre-built `SummarizationMiddleware` class that handles all the complexity for us. Let's use it to create an agent with automatic summarization.


```python
from langchain.agents.middleware import SummarizationMiddleware

# Create agent with built-in summarization middleware
agent_summary = create_agent(
    model="gpt-4o-mini",  # Can pass model name directly
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model="gpt-4o-mini",  # Model used for generating summaries
            max_tokens_before_summary=500,  # Trigger summary after 500 tokens
            messages_to_keep=4,  # Keep last 4 messages in full
        )
    ],
    checkpointer=InMemorySaver(),
)

print("Agent with summarization middleware created successfully!")
print(f"\nConfiguration:")
print(f"  - Summarization triggers after: 500 tokens")
print(f"  - Recent messages kept in full: 4")
print(f"  - Older messages will be: Summarized (not deleted)")
```

    Agent with summarization middleware created successfully!
    
    Configuration:
      - Summarization triggers after: 500 tokens
      - Recent messages kept in full: 4
      - Older messages will be: Summarized (not deleted)


### Testing the Summarization Strategy

Let's run the same conversation with the summarization agent and compare the results.


```python
# Use a different thread ID for this test
config_summary: RunnableConfig = {"configurable": {"thread_id": "summary_demo"}}

print("Starting conversation with summarization agent...")
print("=" * 80)

# Run the same conversation
for i, msg in enumerate(conversation, 1):
    result = agent_summary.invoke(
        {"messages": [HumanMessage(content=msg)]},
        config_summary
    )
    
    ai_response = result['messages'][-1].content
    
    print(f"\nTurn {i}:")
    print(f"User: {msg}")
    print(f"Agent: {ai_response[:100]}...")
    print("-" * 80)

print("\nConversation complete!")
```

    Starting conversation with summarization agent...
    ================================================================================
    
    Turn 1:
    User: Hi! My name is Sajal and I'm planning a trip to Japan.
    Agent: Hi Sajal! That sounds exciting! Japan is a beautiful country with a rich culture, stunning landscape...
    --------------------------------------------------------------------------------
    
    Turn 2:
    User: I'm interested in visiting Tokyo first.
    Agent: Great choice! Tokyo is a vibrant city with a mix of traditional and modern attractions. Here are som...
    --------------------------------------------------------------------------------
    
    Turn 3:
    User: What are the must-see places in Tokyo?
    Agent: Tokyo is full of incredible sights and experiences! Here’s a list of must-see places you should cons...
    --------------------------------------------------------------------------------
    
    Turn 4:
    User: How about food recommendations?
    Agent: Tokyo is a food lover's paradise, offering a wide variety of delicious cuisines and dining experienc...
    --------------------------------------------------------------------------------
    
    Turn 5:
    User: What's the best way to get around Tokyo?
    Agent: Getting around Tokyo is convenient and efficient, thanks to its extensive public transportation syst...
    --------------------------------------------------------------------------------
    
    Turn 6:
    User: Should I get a JR Pass?
    Agent: Deciding whether to get a Japan Rail (JR) Pass depends on your travel plans in Japan, including how ...
    --------------------------------------------------------------------------------
    
    Conversation complete!


### Verifying Summarization Behavior

Let's examine what's stored in memory with the summarization strategy. We should see a summary message plus recent messages.


```python
# Get the current state
state = agent_summary.get_state(config_summary)
messages = state.values["messages"]
print(f"Total messages in memory: {len(messages)}")
print(f"\nMessage structure:")
for i, msg in enumerate(messages, 1):
    msg_type = msg.__class__.__name__
    
    # Check if this is a summary message
    is_summary = "summary" in msg.content.lower()[:100] or msg_type == "SystemMessage"
    
    if is_summary:
        # Print summary in full
        print(f"\n  {i}. {msg_type} [SUMMARY]:")
        print(f"     {msg.content}\n\n")
    else:
        # Print preview for other messages
        content_preview = msg.content[:80] if len(msg.content) > 200 else msg.content
        print(f"  {i}. {msg_type}: {content_preview}{'...' if len(msg.content) > 200 else ''}")

print(f"\nNote: Look for a summary message that condenses older conversation turns.")
```

    Total messages in memory: 6
    
    Message structure:
    
      1. HumanMessage [SUMMARY]:
         Here is a summary of the conversation to date:
    
    Sajal is planning a trip to Japan, starting with a visit to Tokyo. Key attractions in Tokyo include Senso-ji Temple, Tokyo Skytree, Shibuya Crossing, Meiji Shrine, Harajuku, Akihabara, Ginza, Shinjuku Gyoen National Garden, Tokyo National Museum (Ueno Park), Odaiba, Tsukiji Outer Market, Imperial Palace, Roppongi Hills, and Yanaka District. Sajal is also interested in food recommendations.
    
    
      2. AIMessage: Tokyo is a food lover's paradise, offering a wide variety of delicious cuisines ...
      3. HumanMessage: What's the best way to get around Tokyo?
      4. AIMessage: Getting around Tokyo is convenient and efficient, thanks to its extensive public...
      5. HumanMessage: Should I get a JR Pass?
      6. AIMessage: Deciding whether to get a Japan Rail (JR) Pass depends on your travel plans in J...
    
    Note: Look for a summary message that condenses older conversation turns.


### Testing Information Retention

Now let's test whether the summarization approach successfully preserves information from early in the conversation.


```python
# Ask the same recall question
result = agent_summary.invoke(
    {"messages": [HumanMessage(content="What's my name?")]},
    config_summary
)

print("Testing recall of early conversation...")
print(f"\nUser: What's my name?")
print(f"\nAgent: {result['messages'][-1].content}")

print("\n" + "=" * 80)
print("OBSERVATION:")
print("With summarization, the agent should be able to recall our name.")
print("This demonstrates how summarization retains important context over time.")
print("=" * 80)
```

    Testing recall of early conversation...
    
    User: What's my name?
    
    Agent: Your name is Sajal. If you have any other questions or need further assistance with your trip to Japan, feel free to ask!
    
    ================================================================================
    OBSERVATION:
    With summarization, the agent should be able to recall our name.
    This demonstrates how summarization retains important context over time.
    ================================================================================



```python

```
```

---

## File: 4_11_evaluating_agent_trajectories.md

```markdown
# Evaluating Agent Trajectories with AgentEvals

## Introduction

When building AI agents, it's not enough to just evaluate the final output. We need to understand **how** the agent arrived at its answer - the intermediate steps it took, the tools it called, and the reasoning path it followed. This is called **agent trajectory evaluation**.

### What is an Agent Trajectory?

An agent trajectory is the complete sequence of actions an agent takes to solve a task:
- The user's initial request
- The agent's decision to call specific tools
- The arguments passed to those tools
- The responses from tools
- The agent's final answer

### Why Evaluate Trajectories?

Evaluating trajectories helps you:
- **Catch reasoning errors**: An agent might get the right answer for the wrong reason
- **Verify tool usage**: Ensure the agent calls appropriate tools with correct parameters
- **Improve reliability**: Identify when agents take inefficient or incorrect paths
- **Enable Evaluation-Driven Development**: Write tests for agent behavior before implementation

### What You'll Learn

In this notebook, you'll learn to:
1. Capture agent trajectories from LangChain agents
2. Use LLM-as-judge evaluation (no reference trajectory needed)
3. Compare trajectories against reference trajectories
4. Use strict matching for precise tool call verification

**Prerequisites**: 
- OpenAI API key in `.env` file
- Basic understanding of LangChain agents
- Familiarity with tool calling

## Section 1: Setup

First, we'll install the agentevals library and import all required dependencies.


```python
# Install agentevals (run this once)
!pip install agentevals -q
```

    
    [1m[[0m[34;49mnotice[0m[1;39;49m][0m[39;49m A new release of pip is available: [0m[31;49m24.2[0m[39;49m -> [0m[32;49m25.3[0m
    [1m[[0m[34;49mnotice[0m[1;39;49m][0m[39;49m To update, run: [0m[32;49mpip install --upgrade pip[0m



```python
# Load environment variables
from dotenv import load_dotenv

load_dotenv()
```




    True




```python
# Import required libraries
import json
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

# Import agentevals components
from agentevals.trajectory.llm import (
    create_trajectory_llm_as_judge,
    TRAJECTORY_ACCURACY_PROMPT,
    TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE
)
from agentevals.trajectory.match import create_trajectory_match_evaluator

print("All libraries imported successfully!")
```

    All libraries imported successfully!


## Section 2: Create the Agent

We'll create a simple weather agent that uses a `get_weather` tool. This is the same agent from our earlier tutorial on instantiating prebuilt agents.


```python
# Configure the language model for the AGENT
# Using gpt-4o (standard model, no reasoning effort needed for the agent)
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1
)

print("Model configured for agent")
```

    Model configured for agent



```python
# Create a simple weather tool
@tool
def get_weather(location: str) -> str:
    """Get current weather information for a specific location.
    
    Args:
        location: The city or location to get weather for
    
    Returns:
        A string describing the current weather conditions
    """
    # Mock implementation - in production, call a real weather API
    weather_data = {
        "san francisco": "Sunny, 72°F with light winds",
        "new york": "Partly cloudy, 65°F",
        "london": "Rainy, 55°F",
        "tokyo": "Clear, 68°F",
    }
    
    location_key = location.lower().strip()
    
    if location_key in weather_data:
        return f"Weather in {location}: {weather_data[location_key]}"
    else:
        return f"Weather data not available for {location}"

print("Weather tool created")
```

    Weather tool created



```python
# Create the agent
agent = create_agent(
    model=model,
    tools=[get_weather]
)

print("Agent created successfully!")
```

    Agent created successfully!


## Section 3: Capturing Agent Trajectories

An agent trajectory captures the complete sequence of messages during an agent's execution. Let's run the agent and examine what a trajectory looks like.


```python
# Run the agent and capture the trajectory
user_question = "What's the weather like in San Francisco?"

result = agent.invoke({
    "messages": [{"role": "user", "content": user_question}]
})

# Extract all messages from the agent's execution
trajectory_messages = result["messages"]

print(f"Agent executed {len(trajectory_messages)} steps")
print(f"\nFinal answer: {trajectory_messages[-1].content}")
```

    Agent executed 4 steps
    
    Final answer: The weather in San Francisco is currently sunny with a temperature of 72°F and light winds.



```python
# Let's examine the trajectory in detail
print("=== AGENT TRAJECTORY ===")
print()

for i, msg in enumerate(trajectory_messages):
    print(f"Step {i+1}: {type(msg).__name__}")
    
    if isinstance(msg, HumanMessage):
        print(f"  User: {msg.content}")
    elif isinstance(msg, AIMessage):
        if msg.tool_calls:
            print(f"  Agent decided to call tools:")
            for tc in msg.tool_calls:
                print(f"    - {tc['name']}({tc['args']})")
        if msg.content:
            print(f"  Agent response: {msg.content}")
    elif isinstance(msg, ToolMessage):
        print(f"  Tool result: {msg.content}")
    print()
```

    === AGENT TRAJECTORY ===
    
    Step 1: HumanMessage
      User: What's the weather like in San Francisco?
    
    Step 2: AIMessage
      Agent decided to call tools:
        - get_weather({'location': 'San Francisco'})
    
    Step 3: ToolMessage
      Tool result: Weather in San Francisco: Sunny, 72°F with light winds
    
    Step 4: AIMessage
      Agent response: The weather in San Francisco is currently sunny with a temperature of 72°F and light winds.
    


### Converting to AgentEvals Format

The agentevals library expects trajectories in OpenAI message format. Let's create a helper function to convert LangChain messages to this format.


```python
def convert_to_openai_format(messages):
    """Convert LangChain messages to OpenAI format for agentevals."""
    openai_messages = []
    
    for msg in messages:
        if isinstance(msg, HumanMessage):
            openai_messages.append({
                "role": "user",
                "content": msg.content
            })
        elif isinstance(msg, AIMessage):
            msg_dict = {"role": "assistant", "content": msg.content or ""}
            
            # Add tool calls if present
            if msg.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["args"])
                        }
                    }
                    for tc in msg.tool_calls
                ]
            
            openai_messages.append(msg_dict)
        elif isinstance(msg, ToolMessage):
            openai_messages.append({
                "role": "tool",
                "content": msg.content
            })
    
    return openai_messages

# Convert the trajectory
trajectory = convert_to_openai_format(trajectory_messages)

print("Trajectory converted to OpenAI format:")
print(json.dumps(trajectory, indent=2))
```

    Trajectory converted to OpenAI format:
    [
      {
        "role": "user",
        "content": "What's the weather like in San Francisco?"
      },
      {
        "role": "assistant",
        "content": "",
        "tool_calls": [
          {
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"San Francisco\"}"
            }
          }
        ]
      },
      {
        "role": "tool",
        "content": "Weather in San Francisco: Sunny, 72\u00b0F with light winds"
      },
      {
        "role": "assistant",
        "content": "The weather in San Francisco is currently sunny with a temperature of 72\u00b0F and light winds."
      }
    ]


## Section 4: Trajectory LLM-as-Judge Evaluation

The most flexible evaluation method is to use an LLM as a judge. The judge evaluates whether the agent:
- Called appropriate tools
- Used correct arguments
- Provided an accurate final answer

**Key advantage**: You don't need a reference trajectory - the judge evaluates based on the user's question and the agent's behavior.


```python
# Create an LLM-as-judge evaluator
# Using gpt-5-mini with reasoning effort for the EVALUATOR
# Pass the ChatOpenAI instance to the 'judge' parameter
judge_model = ChatOpenAI(
    model='gpt-5-mini',
    reasoning_effort='medium'  # Options: "low", "medium", "high"
)

trajectory_evaluator = create_trajectory_llm_as_judge(
    prompt=TRAJECTORY_ACCURACY_PROMPT,
    judge=judge_model  # Pass ChatOpenAI instance here!
)

print("Evaluator created successfully with gpt-5-mini + reasoning_effort!")
```

    Evaluator created successfully with gpt-5-mini + reasoning_effort!


### Understanding the Model Architecture

Notice that we're using **different models** for different purposes:

- **Agent Model** (`gpt-4o`): Handles the actual task - answering user questions
- **Judge Model** (`gpt-5-mini` with `reasoning_effort`): Evaluates the agent's trajectory

This separation allows you to:
1. Use faster/cheaper models for the agent during development
2. Use more powerful reasoning models for thorough evaluation
3. Optimize each component independently

The `judge` parameter in `create_trajectory_llm_as_judge` accepts a `ChatOpenAI` instance, which lets us configure reasoning effort and other parameters specifically for evaluation.


```python
# Evaluate the trajectory
evaluation_result = trajectory_evaluator(outputs=trajectory)

print("=== EVALUATION RESULT ===")
print(f"Score: {evaluation_result['score']}")
print(f"\nReasoning:")
print(evaluation_result['comment'])
```

    === EVALUATION RESULT ===
    Score: True
    
    Reasoning:
    The goal is to answer the user's question about the weather in San Francisco. The trajectory shows the assistant calling a weather tool with the correct location, receiving a clear tool response (Sunny, 72°F with light winds), and then communicating that information back to the user. The steps are logically connected (question → tool call → tool result → user-facing reply), show clear progression, and are efficient (no unnecessary steps). The assistant's final message accurately restates the tool output. Thus, the score should be: true.

```

---

## File: 4_12_fine_tuning_with_feedback.md

```markdown
# Fine-Tuning Agent Behavior with Feedback Using Meta-Prompting

## Introduction

In this tutorial, you'll learn how to use **meta-prompting** to automatically improve your agent's behavior based on user feedback. Meta-prompting is a powerful technique where one LLM analyzes the performance of another LLM and generates improved instructions for it.

### What is Meta-Prompting?

Meta-prompting is an instruction-tuning approach that creates a feedback-driven improvement loop:

```
┌─────────────────────────────────────────────────────────┐
│                   Improvement Cycle                      │
└─────────────────────────────────────────────────────────┘

    1. Run Agent                2. Collect Feedback
    ┌──────────┐                ┌──────────────┐
    │  Agent   │                │ User rates   │
    │ v1.0     │───────────────▶│ response &   │
    │ (prompt) │                │ provides     │
    └──────────┘                │ comments     │
         ▲                      └──────────────┘
         │                             │
         │                             ▼
    5. Deploy                  3. Analyze & Generate
    Improved Agent             ┌──────────────────┐
    ┌──────────┐               │  Meta-Prompt LLM │
    │  Agent   │               │  analyzes issues │
    │ v2.0     │◀──────────────│  & writes better │
    │ (better) │               │  system prompt   │
    └──────────┘               └──────────────────┘
                                      │
                                      ▼
                              4. Test & Validate
                              ┌──────────────────┐
                              │ Compare old vs   │
                              │ new performance  │
                              └──────────────────┘
```

### Key Concepts Covered

- **Automated Improvement**: Using an LLM to generate better prompts
- **Version Tracking**: Maintaining a history of prompt iterations
- **Feedback-Driven Refinement**: Systematic improvement based on user input
- **Iterative Development**: Multiple cycles leading to progressively better agents

### Prerequisites

- OpenAI API key stored in a `.env` file
- Basic understanding of LangChain agents
- Familiarity with the weather agent from Level 2

### Learning Objectives

By the end of this tutorial, you will:
1. Understand how meta-prompting enables automated prompt improvement
2. Implement a complete feedback collection and analysis system
3. Create a version management system for tracking prompt evolution
4. Build a feedback loop that continuously improves agent behavior
5. Compare and validate improvements across prompt versions

## 1. Setup and Configuration

First, let's import all necessary libraries and load our environment variables.


```python
import os
import json
from datetime import datetime
from typing import Dict, List, Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

print("✓ Environment configured successfully")
```

    ✓ Environment configured successfully


## 2. Create Base Weather Tool

We'll use the same weather tool from Level 2 as our example agent. This tool provides mock weather data for demonstration purposes.


```python
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.
    
    Args:
        location: The city name to get weather for
        
    Returns:
        A string describing the current weather conditions
    """
    # Mock weather data
    weather_data = {
        "new york": "Sunny, 72°F (22°C), humidity 45%",
        "london": "Cloudy, 59°F (15°C), light rain expected",
        "tokyo": "Clear, 68°F (20°C), humidity 60%",
        "paris": "Partly cloudy, 65°F (18°C), gentle breeze",
        "sydney": "Sunny, 75°F (24°C), perfect beach weather"
    }
    
    # Normalize location
    normalized_location = location.lower().strip()
    
    # Return weather or helpful message
    if normalized_location in weather_data:
        return weather_data[normalized_location]
    else:
        return f"Weather data not available for {location}. Try: New York, London, Tokyo, Paris, or Sydney."

print("✓ Weather tool created")
```

    ✓ Weather tool created


## 3. Initialize Prompt Version Management System

Before creating our agent, let's set up a system to track different versions of our system prompts. This is crucial for:
- Understanding how prompts evolve over time
- Rolling back to previous versions if needed
- Analyzing which changes led to improvements

💡 **Key Concept**: Version tracking isn't just about storing text - it's about maintaining context around *why* each change was made and *how* it performed.


```python
# File to store prompt versions
VERSIONS_FILE = "prompt_versions.json"

def initialize_version_system(initial_prompt: str) -> Dict[str, Any]:
    """Initialize the prompt version tracking system.
    
    Args:
        initial_prompt: The starting system prompt
        
    Returns:
        Dictionary containing version 1.0 of the prompt
    """
    versions = {
        "v1.0": {
            "prompt": initial_prompt,
            "timestamp": datetime.now().isoformat(),
            "feedback_summary": "Initial version - baseline prompt",
            "avg_rating": None,
            "num_interactions": 0,
            "feedback_items": []
        }
    }
    return versions

def save_versions(versions: Dict[str, Any]):
    """Save prompt versions to JSON file."""
    with open(VERSIONS_FILE, 'w') as f:
        json.dump(versions, f, indent=2)
    print(f"✓ Versions saved to {VERSIONS_FILE}")

def load_versions() -> Dict[str, Any]:
    """Load prompt versions from JSON file."""
    if os.path.exists(VERSIONS_FILE):
        with open(VERSIONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_latest_version(versions: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Get the most recent prompt version.
    
    Returns:
        Tuple of (version_key, version_data)
    """
    latest_key = sorted(versions.keys())[-1]
    return latest_key, versions[latest_key]

print("✓ Version management system ready")
```

    ✓ Version management system ready


## 4. Create Base Weather Agent (Version 1.0)

Let's start with a simple, basic system prompt. This will be our baseline - intentionally minimal so we can see clear improvements through the meta-prompting process.

⚠️ **Important**: Starting with a simple prompt helps demonstrate the improvement process. In production, you'd start with a more thoughtful initial prompt.


```python
# Initial system prompt (intentionally basic)
INITIAL_SYSTEM_PROMPT = "You are a helpful weather assistant."

# Initialize version tracking
prompt_versions = initialize_version_system(INITIAL_SYSTEM_PROMPT)
save_versions(prompt_versions)

print("Initial System Prompt (v1.0):")
print("="*60)
print(INITIAL_SYSTEM_PROMPT)
print("="*60)
```

    ✓ Versions saved to prompt_versions.json
    Initial System Prompt (v1.0):
    ============================================================
    You are a helpful weather assistant.
    ============================================================



```python
def create_weather_agent(system_prompt: str):
    """Create a weather agent with a specific system prompt.
    
    Args:
        system_prompt: The system instructions for the agent
        
    Returns:
        Configured LangChain agent
    """
    # Create LLM with system prompt
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1
    )
    
    # Note: We'll add the system prompt via messages in invoke
    # Create agent with tools
    agent = create_agent(
        model=model,
        tools=[get_weather]
    )
    
    return agent, system_prompt

# Create initial agent
agent_v1, system_prompt_v1 = create_weather_agent(INITIAL_SYSTEM_PROMPT)
print("✓ Weather agent v1.0 created")
```

    ✓ Weather agent v1.0 created



```python
def ask_agent(agent, system_prompt: str, question: str) -> str:
    """Ask the agent a question and return its response.
    
    Args:
        agent: The LangChain agent
        system_prompt: System instructions for the agent
        question: User's question
        
    Returns:
        Agent's response text
    """
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    })
    
    # Extract final message
    final_message = result['messages'][-1]
    return final_message.content

print("✓ Helper function ready")
```

    ✓ Helper function ready


### Test the Initial Agent

Let's see how our basic agent performs with a simple weather query.


```python
test_query = "What's the weather in London?"

print(f"User: {test_query}\n")
response_v1 = ask_agent(agent_v1, system_prompt_v1, test_query)
print(f"Agent v1.0: {response_v1}")
```

    User: What's the weather in London?
    
    Agent v1.0: The current weather in London is cloudy with a temperature of 59°F (15°C). Light rain is expected.


## 5. Collect User Feedback

Feedback is the foundation of improvement. We'll collect both quantitative (rating) and qualitative (comments) feedback.

💡 **Key Concept**: Structured feedback (rating + specific comments) is more actionable than vague feedback like "it's okay". The meta-prompt LLM needs concrete information about what went wrong and why.


```python
def collect_feedback(query: str, response: str) -> Dict[str, Any]:
    """Collect user feedback on an agent response.
    
    Args:
        query: The user's original question
        response: The agent's response
        
    Returns:
        Dictionary containing feedback data
    """
    print("\n" + "="*60)
    print("FEEDBACK COLLECTION")
    print("="*60)
    print(f"\nQuery: {query}")
    print(f"Response: {response}\n")
    
    # For tutorial purposes, we'll use hardcoded feedback
    # In a real application, you would use input() or a UI form
    
    # Simulated user feedback for the basic agent
    rating = 2  # Out of 5
    comments = (
        "The response is too brief and doesn't provide context. "
        "I'd like to know what to wear or if I need an umbrella. "
        "Also, it would be nice if the agent was more conversational and friendly."
    )
    
    print(f"Rating: {rating}/5")
    print(f"Comments: {comments}")
    
    feedback = {
        "query": query,
        "response": response,
        "rating": rating,
        "comments": comments,
        "timestamp": datetime.now().isoformat()
    }
    
    return feedback

# Collect feedback on our test interaction
feedback_v1 = collect_feedback(test_query, response_v1)

print("\n✓ Feedback collected")
```

    
    ============================================================
    FEEDBACK COLLECTION
    ============================================================
    
    Query: What's the weather in London?
    Response: The current weather in London is cloudy with a temperature of 59°F (15°C). Light rain is expected.
    
    Rating: 2/5
    Comments: The response is too brief and doesn't provide context. I'd like to know what to wear or if I need an umbrella. Also, it would be nice if the agent was more conversational and friendly.
    
    ✓ Feedback collected


## 6. Meta-Prompting: Generate Improved System Prompt

Now for the magic! We'll use a separate LLM instance (the "meta-prompt LLM") to analyze the feedback and generate an improved system prompt.

### How Meta-Prompting Works

The meta-prompt LLM receives:
1. **Current system prompt** - What instructions the agent currently follows
2. **User query** - What the user asked
3. **Agent response** - What the agent said
4. **User feedback** - Rating and specific complaints/suggestions

Based on this analysis, it generates a **new system prompt** that addresses the issues.

💡 **Key Concept**: The meta-prompt LLM is a prompt engineer. It understands what makes good prompts and can write better instructions based on observed failures.


```python
def create_meta_prompt(current_prompt: str, feedback: Dict[str, Any]) -> str:
    """Create a meta-prompt for analyzing and improving the system prompt.
    
    Args:
        current_prompt: The current system prompt being used
        feedback: Dictionary containing query, response, rating, and comments
        
    Returns:
        Meta-prompt string for the optimization LLM
    """
    meta_prompt = f"""You are an expert prompt engineer specializing in optimizing AI agent behavior.

Your task is to analyze a user interaction with an AI agent and generate an improved system prompt that addresses the user's concerns.

CURRENT SYSTEM PROMPT:
{current_prompt}

INTERACTION DETAILS:
User Query: {feedback['query']}
Agent Response: {feedback['response']}
User Rating: {feedback['rating']}/5
User Feedback: {feedback['comments']}

ANALYSIS INSTRUCTIONS:
1. Identify specific issues mentioned in the user feedback
2. Determine what the current prompt is missing or doing wrong
3. Consider what instructions would lead to better responses
4. Generate a new system prompt that:
   - Addresses all user concerns
   - Maintains the agent's core purpose
   - Provides clear, actionable instructions
   - Specifies desired tone, style, and behavior

IMPORTANT: Output ONLY the new system prompt, nothing else. Do not include explanations, markdown formatting, or meta-commentary. Just the raw prompt text that will be used as the new system instruction.
"""
    return meta_prompt

print("✓ Meta-prompt template ready")
```

    ✓ Meta-prompt template ready



```python
def generate_improved_prompt(current_prompt: str, feedback: Dict[str, Any]) -> str:
    """Use meta-prompting to generate an improved system prompt.
    
    Args:
        current_prompt: The current system prompt
        feedback: User feedback dictionary
        
    Returns:
        New improved system prompt
    """
    # Create meta-prompt
    meta_prompt = create_meta_prompt(current_prompt, feedback)
    
    # Use a separate LLM instance for meta-prompting
    # We use higher temperature for creative prompt engineering
    meta_llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7
    )
    
    # Generate improved prompt
    response = meta_llm.invoke(meta_prompt)
    improved_prompt = response.content.strip()
    
    return improved_prompt

print("✓ Prompt improvement function ready")
```

    ✓ Prompt improvement function ready


### Generate Version 2.0 of the System Prompt

Let's run the meta-prompting process to create an improved prompt based on our user feedback.


```python
print("Analyzing feedback and generating improved prompt...\n")

improved_prompt = generate_improved_prompt(system_prompt_v1, feedback_v1)

print("\n" + "="*60)
print("PROMPT COMPARISON")
print("="*60)

print("\n📋 VERSION 1.0 (Original):")
print("-" * 60)
print(system_prompt_v1)

print("\n\n📋 VERSION 2.0 (Improved):")
print("-" * 60)
print(improved_prompt)
print("="*60)

print("\n✓ Improved prompt generated successfully")
```

    Analyzing feedback and generating improved prompt...
    
    
    ============================================================
    PROMPT COMPARISON
    ============================================================
    
    📋 VERSION 1.0 (Original):
    ------------------------------------------------------------
    You are a helpful weather assistant.
    
    
    📋 VERSION 2.0 (Improved):
    ------------------------------------------------------------
    You are a friendly and conversational weather assistant. Provide detailed weather updates that include current conditions, temperature, and precipitation expectations. Offer practical advice on what to wear and whether an umbrella is needed. Ensure your responses are engaging and relatable, adding context to help users plan their day.
    ============================================================
    
    ✓ Improved prompt generated successfully


## 7. Save New Version and Update Tracking

Now that we have an improved prompt, let's save it to our version management system.


```python
def add_new_version(versions: Dict[str, Any], 
                   new_prompt: str, 
                   feedback: Dict[str, Any]) -> str:
    """Add a new prompt version to the tracking system.
    
    Args:
        versions: Current versions dictionary
        new_prompt: The improved system prompt
        feedback: Feedback that led to this improvement
        
    Returns:
        Version key for the new version
    """
    # Generate new version number
    version_numbers = [float(v.replace('v', '')) for v in versions.keys()]
    new_version_num = max(version_numbers) + 1.0
    new_version_key = f"v{new_version_num}"
    
    # Create summary of why this version was created
    feedback_summary = (
        f"Improved based on rating {feedback['rating']}/5. "
        f"User requested: {feedback['comments'][:100]}..."
    )
    
    # Add new version
    versions[new_version_key] = {
        "prompt": new_prompt,
        "timestamp": datetime.now().isoformat(),
        "feedback_summary": feedback_summary,
        "avg_rating": None,
        "num_interactions": 0,
        "feedback_items": [],
        "previous_version": sorted(versions.keys())[-1]  # Link to previous
    }
    
    return new_version_key

# Add v2.0 to our version tracking
new_version = add_new_version(prompt_versions, improved_prompt, feedback_v1)
save_versions(prompt_versions)

print(f"✓ Version {new_version} saved to tracking system")
print(f"✓ Total versions: {len(prompt_versions)}")
```

    ✓ Versions saved to prompt_versions.json
    ✓ Version v2.0 saved to tracking system
    ✓ Total versions: 2


## 8. Test Improved Agent (Version 2.0)

Let's create a new agent with the improved prompt and test it with the same query to see the difference.


```python
# Create agent with improved prompt
agent_v2, system_prompt_v2 = create_weather_agent(improved_prompt)

print("✓ Weather agent v2.0 created with improved prompt\n")

# Test with same query
print(f"User: {test_query}\n")
response_v2 = ask_agent(agent_v2, system_prompt_v2, test_query)
print(f"Agent v2.0: {response_v2}")
```

    ✓ Weather agent v2.0 created with improved prompt
    
    User: What's the weather in London?
    
    Agent v2.0: In London, it's currently cloudy with a temperature of 59°F (15°C). There's light rain expected, so it might be a good idea to have an umbrella handy if you're heading out. With the cool and damp conditions, wearing a light jacket or a sweater would be comfortable. Enjoy your day, and don't forget to stay dry!

```

---

## File: 4_16_cost_optimization_semantic_caching.md

```markdown
# Semantic Caching for LLM Cost Optimization

## Introduction

Welcome to this tutorial on **semantic caching** - one of the most effective strategies for optimizing AI agent costs while maintaining response quality!

### What You'll Learn

In this notebook, you will:
- Understand what semantic caching is and why it's crucial for cost optimization
- Learn the difference between traditional and semantic caching
- Build a semantic cache using embeddings and vector similarity
- Implement a cache-aware agent wrapper
- Measure and calculate real cost savings
- Learn best practices for production deployment

### Prerequisites

- Basic Python knowledge
- Understanding of LLMs and agents
- Familiarity with embeddings (helpful but not required)
- An OpenAI API key

### The Cost Problem

AI agents that use LLMs can be expensive to run at scale:
- GPT-4o mini call: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- High-volume applications: Thousands of requests per day
- Many queries are similar or repetitive

**Example scenario:**
```
User 1: "What's the weather in New York?"
User 2: "Can you tell me the weather in New York?"
User 3: "How's the weather in New York City?"
```

These three queries ask the same thing but have different wording. Traditional caching (exact string match) would miss these opportunities. **Semantic caching solves this!**

### Traditional vs Semantic Caching

| Aspect | Traditional Cache | Semantic Cache |
|--------|------------------|----------------|
| Match Type | Exact string match | Meaning-based match |
| Query: "weather in NYC" | ❌ Miss | ✅ Hit |
| Query: "NYC weather" | ❌ Miss | ✅ Hit |
| Technology | Hash tables | Vector embeddings |
| Hit Rate | 5-10% | 30-50% |

### How Semantic Caching Works

```
┌─────────────────────────────────────────────────────────┐
│  User Query: "What's the weather in NYC?"               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  1. Convert to Embedding Vector                         │
│     [0.23, -0.45, 0.12, ...]                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  2. Search Vector Store for Similar Queries            │
│     Cosine Similarity Threshold: 0.90                  │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   ┌─────────────┐      ┌─────────────┐
   │ Similarity  │      │ Similarity  │
   │   ≥ 0.90    │      │   < 0.90    │
   │ (CACHE HIT) │      │ (CACHE MISS)│
   └──────┬──────┘      └──────┬──────┘
          │                     │
          ▼                     ▼
   ┌─────────────┐      ┌─────────────┐
   │ Return      │      │ Call LLM    │
   │ Cached      │      │ Get New     │
   │ Response    │      │ Response    │
   │             │      │ Cache It    │
   └─────────────┘      └─────────────┘
```

### Cost Savings Breakdown

**Per Query Costs:**
- Embedding generation: ~$0.0001 (very cheap!)
- LLM call: ~$0.01-0.03 (100-300x more expensive)
- Cache hit saves: 99%+ of the cost

**Example Calculation:**
- 1000 queries per day
- 40% cache hit rate (400 hits)
- Savings: 400 × $0.02 = $8 per day = $240 per month
- Break-even: After just 2-3 cache hits per unique query

Let's build it!

## 1. Setup and Installation

First, let's install the required packages and set up our environment.


```python
# Install required packages
# Uncomment the line below if you need to install packages
# !pip install langchain langchain-openai langchain-chroma langgraph python-dotenv
```

### Import Libraries and Load Environment

We'll need:
- **LangChain Core**: For tools and base abstractions
- **LangChain OpenAI**: For embeddings and LLM
- **LangChain Chroma**: For vector-based cache storage
- **LangChain Agents**: For creating our weather agent
- **Python standard library**: For time tracking and hashing


```python
import os
import time
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain.agents import create_agent

# Load environment variables
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")

print("All libraries imported successfully!")
print("OpenAI API key loaded")
```

    All libraries imported successfully!
    OpenAI API key loaded


## 2. Build a Simple Weather Agent (Without Cache)

Before implementing caching, let's create a simple agent that uses a weather tool. This will be our baseline for comparison.

### Create the Weather Tool

This is a mock tool that returns simulated weather data. In production, you'd call a real weather API.


```python
@tool
def get_weather(location: str) -> str:
    """Get current weather information for a specific location.
    
    Args:
        location: The city or location to get weather for
    
    Returns:
        A string describing the current weather conditions
    """
    # Mock implementation - simulates API call delay
    time.sleep(0.5)  # Simulate API latency
    
    weather_data = {
        "new york": "Sunny, 72°F with light breeze",
        "new york city": "Sunny, 72°F with light breeze",
        "nyc": "Sunny, 72°F with light breeze",
        "london": "Cloudy, 59°F with occasional drizzle",
        "tokyo": "Clear, 68°F with low humidity",
        "san francisco": "Foggy, 62°F with coastal breeze",
        "paris": "Partly cloudy, 65°F",
    }
    
    location_key = location.lower().strip()
    
    if location_key in weather_data:
        return f"Weather in {location}: {weather_data[location_key]}"
    else:
        return f"Weather data not available for {location}"

print("Weather tool created")
print("Available locations: New York, London, Tokyo, San Francisco, Paris")
```

    Weather tool created
    Available locations: New York, London, Tokyo, San Francisco, Paris


### Create the Agent

We'll use LangChain's `create_agent` function to create a simple agent with the weather tool.


```python
# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create the agent
agent = create_agent(
    model=llm,
    tools=[get_weather]
)

print("Agent created successfully!")
print("The agent can answer weather-related questions using the get_weather tool")
```

    Agent created successfully!
    The agent can answer weather-related questions using the get_weather tool


### Test the Agent (Without Cache)

Let's test our agent with a few queries and time how long they take.


```python
def ask_agent(question: str) -> str:
    """Helper function to ask the agent a question."""
    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    return result["messages"][-1].content

# Test with timing
print("Testing agent WITHOUT cache...\n")
print("="*70)

test_queries = [
    "What's the weather in New York?",
    "Can you tell me the weather in New York?",
    "How's the weather in NYC?"
]

for i, query in enumerate(test_queries, 1):
    start = time.time()
    response = ask_agent(query)
    duration = time.time() - start
    
    print(f"\nQuery {i}: {query}")
    print(f"Response: {response}")
    print(f"Time: {duration:.2f}s")
    print("="*70)

print("\nNotice: All three similar queries took similar time and cost!")
print("This is where semantic caching can help.")
```

    Testing agent WITHOUT cache...
    
    ======================================================================
    
    Query 1: What's the weather in New York?
    Response: The weather in New York is sunny, with a temperature of 72°F and a light breeze.
    Time: 3.90s
    ======================================================================
    
    Query 2: Can you tell me the weather in New York?
    Response: The weather in New York is currently sunny, with a temperature of 72°F and a light breeze.
    Time: 2.67s
    ======================================================================
    
    Query 3: How's the weather in NYC?
    Response: The weather in New York City is sunny, with a temperature of 72°F and a light breeze.
    Time: 2.83s
    ======================================================================
    
    Notice: All three similar queries took similar time and cost!
    This is where semantic caching can help.


## 3. Implement Semantic Cache

Now let's build the semantic cache using embeddings and ChromaDB. The cache will store user queries and their corresponding agent responses.

### Initialize Embeddings and Vector Store

We'll use:
- **OpenAI's text-embedding-3-small**: Cost-effective and fast
- **ChromaDB**: In-memory vector store for similarity search


```python
# Initialize embeddings model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

print("Embeddings model initialized: text-embedding-3-small")
print("Cost per 1M tokens: ~$0.02 (very cheap!)")

# Test embeddings
sample_query = "What's the weather in New York?"
sample_embedding = embeddings.embed_query(sample_query)
print(f"\nSample embedding dimensions: {len(sample_embedding)}")
print(f"First 5 values: {sample_embedding[:5]}")
```

    Embeddings model initialized: text-embedding-3-small
    Cost per 1M tokens: ~$0.02 (very cheap!)
    
    Sample embedding dimensions: 1536
    First 5 values: [-0.03764260932803154, -0.020033851265907288, -0.05704335868358612, 0.0393165685236454, 0.0066153560765087605]



```python
# Create vector store for semantic cache
semantic_cache = Chroma(
    collection_name="semantic_cache",
    embedding_function=embeddings,
    # Using in-memory for this tutorial
    # In production, add: persist_directory="./semantic_cache_db"
)

print("Semantic cache initialized!")
print("Vector store: ChromaDB (in-memory)")
print("\nCache structure:")
print("  - Document content: User query text")
print("  - Metadata: {response: agent_response, timestamp: datetime}")
print("  - Automatic embedding: Handled by ChromaDB")
```

    Semantic cache initialized!
    Vector store: ChromaDB (in-memory)
    
    Cache structure:
      - Document content: User query text
      - Metadata: {response: agent_response, timestamp: datetime}
      - Automatic embedding: Handled by ChromaDB


### Understanding the Cache Structure

Our cache stores three pieces of information for each query:

1. **User Query** (as Document content): The actual question asked
2. **Agent Response** (in metadata): The answer the agent provided
3. **Timestamp** (in metadata): When this was cached

**Important:** We only cache the user's input query, NOT system prompts or tool descriptions. This ensures we're matching on what the user actually asked.

When a new query comes in:
1. We embed the query → convert to vector
2. Search for similar cached queries → cosine similarity
3. If similarity ≥ threshold (0.90) → return cached response
4. If similarity < threshold → call agent and cache the new response

## 4. Create Cache-Aware Agent Wrapper

Now let's create a wrapper function that checks the cache before calling the agent.

### Define the Similarity Threshold

The threshold determines how similar queries must be to count as a cache hit:
- **0.95+**: Very strict, fewer false positives, lower hit rate
- **0.90-0.95**: Balanced (recommended for most use cases)
- **0.80-0.90**: Looser, higher hit rate, some risk of false positives


```python
# Configuration
SIMILARITY_THRESHOLD = 0.90
CACHE_TTL_HOURS = 24  # Time-to-live for cache entries

print(f"Cache Configuration:")
print(f"  Similarity Threshold: {SIMILARITY_THRESHOLD}")
print(f"  Cache TTL: {CACHE_TTL_HOURS} hours")
print(f"\nThreshold guide:")
print(f"  0.95+ : Very precise, fewer cache hits")
print(f"  0.90-0.95: Balanced (recommended)")
print(f"  0.80-0.90: More cache hits, some false positives")
```

    Cache Configuration:
      Similarity Threshold: 0.9
      Cache TTL: 24 hours
    
    Threshold guide:
      0.95+ : Very precise, fewer cache hits
      0.90-0.95: Balanced (recommended)
      0.80-0.90: More cache hits, some false positives


### Implement the Cached Agent Function

This function:
1. Takes a user query
2. Searches the cache for similar queries
3. Returns cached response if similarity ≥ threshold
4. Otherwise calls the agent and caches the new response


```python
def ask_agent_with_cache(question: str, verbose: bool = True) -> tuple[str, bool, float, float]:
    """
    Ask the agent a question with semantic caching.
    
    Args:
        question: The user's question
        verbose: If True, print cache hit/miss information
    
    Returns:
        tuple: (response, cache_hit, similarity_score, duration)
    """
    start_time = time.time()
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"Query: {question}")
        print(f"{'='*70}")
    
    # Step 1: Search cache for similar queries
    # similarity_search_with_score returns (Document, similarity_score) tuples
    results = semantic_cache.similarity_search_with_score(
        query=question,
        k=1  # Get the most similar cached query
    )
    
    cache_hit = False
    similarity_score = 0.0
    
    # Step 2: Check if we have a cache hit
    if results:
        cached_doc, distance = results[0]
        # ChromaDB returns L2 distance, convert to cosine similarity
        # For normalized vectors: cosine_similarity = 1 - (distance^2 / 2)
        similarity_score = 1 - (distance ** 2 / 2)
        
        if verbose:
            print(f"\nCache Search:")
            print(f"  Most similar cached query: '{cached_doc.page_content}'")
            print(f"  Similarity score: {similarity_score:.4f}")
            print(f"  Threshold: {SIMILARITY_THRESHOLD}")
        
        # Step 3: Cache hit - return cached response
        if similarity_score >= SIMILARITY_THRESHOLD:
            cache_hit = True
            response = cached_doc.metadata["response"]
            cached_time = cached_doc.metadata.get("timestamp", "unknown")
            
            duration = time.time() - start_time
            
            if verbose:
                print(f"\n  ✅ CACHE HIT!")
                print(f"  Cached at: {cached_time}")
                print(f"  Cost savings: ~99% (embedding vs LLM call)")
                print(f"  Response time: {duration:.2f}s")
                print(f"\nResponse: {response}")
            
            return response, cache_hit, similarity_score, duration
    
    # Step 4: Cache miss - call agent and cache the response
    if verbose:
        print(f"\n  ❌ CACHE MISS (similarity: {similarity_score:.4f} < {SIMILARITY_THRESHOLD})")
        print(f"  Calling agent...")
    
    # Call the agent
    response = ask_agent(question)
    
    # Cache the new query-response pair
    cache_doc = Document(
        page_content=question,  # Store the user query
        metadata={
            "response": response,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
    semantic_cache.add_documents([cache_doc])
    
    duration = time.time() - start_time
    
    if verbose:
        print(f"  Cached new response for future queries")
        print(f"  Response time: {duration:.2f}s")
        print(f"\nResponse: {response}")
    
    return response, cache_hit, similarity_score, duration

print("Cache-aware agent wrapper created!")
print("Ready to demonstrate semantic caching.")
```

    Cache-aware agent wrapper created!
    Ready to demonstrate semantic caching.


## 5. Demonstrate Semantic Caching

Now let's test our semantic cache with similar queries and see the cost savings!

### Test 1: Similar Queries About New York Weather

We'll ask three different ways of asking about New York weather. The first query will be a cache miss, but the subsequent similar queries should be cache hits.


```python
print("TEST 1: Similar queries about New York weather\n")

test_queries = [
    "What's the weather in New York?",
    "Can you tell me the weather in New York?",
    "How's the weather in NYC?",
    "What's the weather like in New York City?"
]

results = []

for query in test_queries:
    response, cache_hit, similarity, duration = ask_agent_with_cache(query)
    results.append({
        "query": query,
        "cache_hit": cache_hit,
        "similarity": similarity,
        "duration": duration
    })
    time.sleep(0.5)  # Small delay between queries

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
```

    TEST 1: Similar queries about New York weather
    
    
    ======================================================================
    Query: What's the weather in New York?
    ======================================================================
    
      ❌ CACHE MISS (similarity: 0.0000 < 0.9)
      Calling agent...
      Cached new response for future queries
      Response time: 6.87s
    
    Response: The weather in New York is sunny, with a temperature of 72°F and a light breeze.
    
    ======================================================================
    Query: Can you tell me the weather in New York?
    ======================================================================
    
    Cache Search:
      Most similar cached query: 'What's the weather in New York?'
      Similarity score: 0.9821
      Threshold: 0.9
    
      ✅ CACHE HIT!
      Cached at: 2025-11-15 17:45:25
      Cost savings: ~99% (embedding vs LLM call)
      Response time: 0.51s
    
    Response: The weather in New York is sunny, with a temperature of 72°F and a light breeze.
    
    ======================================================================
    Query: How's the weather in NYC?
    ======================================================================
    
    Cache Search:
      Most similar cached query: 'What's the weather in New York?'
      Similarity score: 0.9675
      Threshold: 0.9
    
      ✅ CACHE HIT!
      Cached at: 2025-11-15 17:45:25
      Cost savings: ~99% (embedding vs LLM call)
      Response time: 0.42s
    
    Response: The weather in New York is sunny, with a temperature of 72°F and a light breeze.
    
    ======================================================================
    Query: What's the weather like in New York City?
    ======================================================================
    
    Cache Search:
      Most similar cached query: 'What's the weather in New York?'
      Similarity score: 0.9917
      Threshold: 0.9
    
      ✅ CACHE HIT!
      Cached at: 2025-11-15 17:45:25
      Cost savings: ~99% (embedding vs LLM call)
      Response time: 0.52s
    
    Response: The weather in New York is sunny, with a temperature of 72°F and a light breeze.
    
    ======================================================================
    SUMMARY
    ======================================================================



```python
# Display summary table
print(f"\n{'Query':<50} {'Hit?':<8} {'Similarity':<12} {'Time':<8}")
print("="*80)

for result in results:
    hit_symbol = "✅" if result["cache_hit"] else "❌"
    print(f"{result['query']:<50} {hit_symbol:<8} {result['similarity']:<12.4f} {result['duration']:<8.2f}s")

# Calculate statistics
total_queries = len(results)
cache_hits = sum(1 for r in results if r["cache_hit"])
cache_hit_rate = (cache_hits / total_queries) * 100
avg_hit_time = sum(r["duration"] for r in results if r["cache_hit"]) / max(cache_hits, 1)
avg_miss_time = sum(r["duration"] for r in results if not r["cache_hit"]) / (total_queries - cache_hits)

print(f"\nStatistics:")
print(f"  Total queries: {total_queries}")
print(f"  Cache hits: {cache_hits}")
print(f"  Cache hit rate: {cache_hit_rate:.1f}%")
print(f"  Avg time (cache hit): {avg_hit_time:.2f}s")
print(f"  Avg time (cache miss): {avg_miss_time:.2f}s")
print(f"  Speedup: {avg_miss_time/avg_hit_time:.1f}x faster with cache")
```

    
    Query                                              Hit?     Similarity   Time    
    ================================================================================
    What's the weather in New York?                    ❌        0.0000       6.87    s
    Can you tell me the weather in New York?           ✅        0.9821       0.51    s
    How's the weather in NYC?                          ✅        0.9675       0.42    s
    What's the weather like in New York City?          ✅        0.9917       0.52    s
    
    Statistics:
      Total queries: 4
      Cache hits: 3
      Cache hit rate: 75.0%
      Avg time (cache hit): 0.48s
      Avg time (cache miss): 6.87s
      Speedup: 14.2x faster with cache


### Test 2: Different Location (Cache Miss Expected)

Now let's ask about a different location. This should be a cache miss because it's semantically different from the New York queries.


```python
print("\n\nTEST 2: Different location (Tokyo)\n")

# This should be a cache miss
response, cache_hit, similarity, duration = ask_agent_with_cache(
    "What's the weather in Tokyo?"
)

print("\nThis query is semantically different from the New York queries,")
print("so it correctly results in a cache miss.")
```

    
    
    TEST 2: Different location (Tokyo)
    
    
    ======================================================================
    Query: What's the weather in Tokyo?
    ======================================================================
    
    Cache Search:
      Most similar cached query: 'What's the weather in New York?'
      Similarity score: 0.6172
      Threshold: 0.9
    
      ❌ CACHE MISS (similarity: 0.6172 < 0.9)
      Calling agent...
      Cached new response for future queries
      Response time: 4.57s
    
    Response: The weather in Tokyo is clear, with a temperature of 68°F and low humidity.
    
    This query is semantically different from the New York queries,
    so it correctly results in a cache miss.



```python
# Now ask about Tokyo again with different wording
print("\n\nAsking about Tokyo again with different wording...\n")

response, cache_hit, similarity, duration = ask_agent_with_cache(
    "Can you tell me the weather in Tokyo?"
)

print("\nThis time we got a cache hit because it's similar to the previous Tokyo query!")
```

    
    
    Asking about Tokyo again with different wording...
    
    
    ======================================================================
    Query: Can you tell me the weather in Tokyo?
    ======================================================================
    
    Cache Search:
      Most similar cached query: 'What's the weather in Tokyo?'
      Similarity score: 0.9854
      Threshold: 0.9
    
      ✅ CACHE HIT!
      Cached at: 2025-11-15 17:45:49
      Cost savings: ~99% (embedding vs LLM call)
      Response time: 1.23s
    
    Response: The weather in Tokyo is clear, with a temperature of 68°F and low humidity.
    
    This time we got a cache hit because it's similar to the previous Tokyo query!


## 6. Calculate Cost Savings

Let's calculate the actual cost savings from semantic caching with real numbers.

### Cost Model

Based on OpenAI pricing (as of January 2025):
- **GPT-4o mini**: $0.150 per 1M input tokens, $0.600 per 1M output tokens
- **text-embedding-3-small**: $0.020 per 1M tokens
- **Average LLM call**: ~500 input tokens + ~100 output tokens
- **Average embedding**: ~50 tokens

Let's calculate the savings:


```python
# Cost parameters (in dollars)
GPT4O_MINI_INPUT_COST_PER_1M = 0.150
GPT4O_MINI_OUTPUT_COST_PER_1M = 0.600
EMBEDDING_COST_PER_1M = 0.020

# Average token counts
AVG_INPUT_TOKENS_PER_QUERY = 500
AVG_OUTPUT_TOKENS_PER_QUERY = 100
AVG_EMBEDDING_TOKENS_PER_QUERY = 50

# Calculate cost per query
cost_per_llm_call = (
    (AVG_INPUT_TOKENS_PER_QUERY / 1_000_000) * GPT4O_MINI_INPUT_COST_PER_1M +
    (AVG_OUTPUT_TOKENS_PER_QUERY / 1_000_000) * GPT4O_MINI_OUTPUT_COST_PER_1M
)

cost_per_embedding = (
    (AVG_EMBEDDING_TOKENS_PER_QUERY / 1_000_000) * EMBEDDING_COST_PER_1M
)

savings_per_cache_hit = cost_per_llm_call - cost_per_embedding

print("COST ANALYSIS")
print("="*70)
print(f"\nPer Query Costs:")
print(f"  LLM call (GPT-4o mini): ${cost_per_llm_call:.6f}")
print(f"  Embedding lookup: ${cost_per_embedding:.6f}")
print(f"  Savings per cache hit: ${savings_per_cache_hit:.6f} ({(savings_per_cache_hit/cost_per_llm_call)*100:.1f}%)")
print(f"\nCost breakdown:")
print(f"  Cache hit is {cost_per_llm_call/cost_per_embedding:.0f}x cheaper than LLM call!")
```

    COST ANALYSIS
    ======================================================================
    
    Per Query Costs:
      LLM call (GPT-4o mini): $0.000135
      Embedding lookup: $0.000001
      Savings per cache hit: $0.000134 (99.3%)
    
    Cost breakdown:
      Cache hit is 135x cheaper than LLM call!


### Projected Savings for Different Scenarios

Let's calculate savings for different usage patterns:


```python
def calculate_monthly_savings(queries_per_day: int, cache_hit_rate: float) -> dict:
    """
    Calculate monthly cost savings from semantic caching.
    
    Args:
        queries_per_day: Number of queries per day
        cache_hit_rate: Cache hit rate (0.0 to 1.0)
    
    Returns:
        Dictionary with cost breakdown
    """
    queries_per_month = queries_per_day * 30
    cache_hits = queries_per_month * cache_hit_rate
    cache_misses = queries_per_month * (1 - cache_hit_rate)
    
    # Cost without caching
    cost_without_cache = queries_per_month * cost_per_llm_call
    
    # Cost with caching
    cost_with_cache = (
        cache_hits * cost_per_embedding +  # Cache hits: only embedding cost
        cache_misses * (cost_per_llm_call + cost_per_embedding)  # Misses: LLM + embedding
    )
    
    monthly_savings = cost_without_cache - cost_with_cache
    savings_percentage = (monthly_savings / cost_without_cache) * 100
    
    return {
        "queries_per_month": queries_per_month,
        "cache_hits": int(cache_hits),
        "cache_misses": int(cache_misses),
        "cost_without_cache": cost_without_cache,
        "cost_with_cache": cost_with_cache,
        "monthly_savings": monthly_savings,
        "savings_percentage": savings_percentage,
        "annual_savings": monthly_savings * 12
    }

# Calculate for different scenarios
scenarios = [
    {"name": "Small App", "queries": 1000, "hit_rate": 0.30},
    {"name": "Medium App", "queries": 10000, "hit_rate": 0.40},
    {"name": "Large App", "queries": 100000, "hit_rate": 0.50},
]

print("\nMONTHLY SAVINGS PROJECTIONS")
print("="*70)

for scenario in scenarios:
    result = calculate_monthly_savings(scenario["queries"], scenario["hit_rate"])
    
    print(f"\n{scenario['name']} ({scenario['queries']:,} queries/day, {scenario['hit_rate']*100:.0f}% hit rate):")
    print(f"  Monthly queries: {result['queries_per_month']:,}")
    print(f"  Cache hits: {result['cache_hits']:,}")
    print(f"  Cost without cache: ${result['cost_without_cache']:.2f}/month")
    print(f"  Cost with cache: ${result['cost_with_cache']:.2f}/month")
    print(f"  Monthly savings: ${result['monthly_savings']:.2f} ({result['savings_percentage']:.1f}%)")
    print(f"  Annual savings: ${result['annual_savings']:.2f}")

print("\n" + "="*70)
print("Note: These calculations use average token counts and may vary in practice.")
```

    
    MONTHLY SAVINGS PROJECTIONS
    ======================================================================
    
    Small App (1,000 queries/day, 30% hit rate):
      Monthly queries: 30,000
      Cache hits: 9,000
      Cost without cache: $4.05/month
      Cost with cache: $2.86/month
      Monthly savings: $1.19 (29.3%)
      Annual savings: $14.22
    
    Medium App (10,000 queries/day, 40% hit rate):
      Monthly queries: 300,000
      Cache hits: 120,000
      Cost without cache: $40.50/month
      Cost with cache: $24.60/month
      Monthly savings: $15.90 (39.3%)
      Annual savings: $190.80
    
    Large App (100,000 queries/day, 50% hit rate):
      Monthly queries: 3,000,000
      Cache hits: 1,500,000
      Cost without cache: $405.00/month
      Cost with cache: $205.50/month
      Monthly savings: $199.50 (49.3%)
      Annual savings: $2394.00
    
    ======================================================================
    Note: These calculations use average token counts and may vary in practice.

```

---

## File: 4_17_deepagents_package.md

```markdown
# Building Deep Agents with Sub-Agent Architectures

## Introduction

In this advanced tutorial, you'll learn how to build **multi-agent systems** using the **orchestrator pattern** - the architecture used by production systems like Claude Code, LangGraph Deep Agents, and enterprise AI applications.

### What You'll Learn

- Why monolithic agents struggle with complex tasks
- How to design sub-agent architectures with clear responsibility boundaries
- The orchestrator pattern: coordinator + specialized workers
- Building production-grade specialized agents (Research + Weather)
- Practical travel planning system with parallel sub-agent execution

### The Problem: Monolithic Agents Hit Limits

**Single Agent with All Tools:**
- Context window fills with 20+ tool descriptions
- System prompt becomes unfocused and conflicting
- Agent gets confused about which tool to use when
- Difficult to debug and maintain

**Sub-Agent Solution:**
- **Cognitive specialization**: Each agent has focused expertise
- **Context efficiency**: Only relevant tools per agent
- **Parallel processing**: Multiple sub-agents work concurrently
- **Maintainability**: Test and update individual agents

### The Orchestrator Pattern

The orchestrator pattern divides responsibilities into two types of agents:

| **Orchestrator (Coordinator)** | **Worker Agents (Specialists)** |
|--------------------------------|----------------------------------|
| Analyze overall task | Execute specific sub-tasks |
| Decompose into sub-tasks | Use specialized tools |
| Route to workers (parallel) | Return structured results |
| Synthesize final response | Remain stateless |
| **Tools:** Planning, file I/O | **Tools:** Domain-specific |
| **Focus:** Breadth, delegation | **Focus:** Depth, completion |

**Communication Flow:**
```
User: "I'm traveling to Tokyo next week. Research the city and give me the weather."
          ↓
    Orchestrator
    (decomposes into 2 sub-tasks)
          ↓
    ┌─────┴─────┐
    ↓           ↓
 Research    Weather
 Agent       Agent
(Tavily)    (Weather API)
    ↓           ↓
    └─────┬─────┘
          ↓
    Orchestrator
    (synthesizes)
          ↓
   Travel Brief
```

### Prerequisites

**Required API Keys:**
- OpenAI API key (for GPT-4)
- Tavily API key (for web research)
- OpenWeatherMap API key (for weather data)

**Setup:**
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_key_here
TAVILY_API_KEY=your_tavily_key_here
OPENWEATHER_API_KEY=your_openweather_key_here
```

### Learning Objectives

By the end of this tutorial, you'll be able to:
1. Design responsibility boundaries for multi-agent systems
2. Build specialized sub-agents with focused toolsets
3. Implement an orchestrator that coordinates parallel execution
4. Use shared filesystem for artifact-based communication
5. Deploy production-grade multi-agent systems

## Part 1: Setup and Installation

First, let's install all required packages and verify our environment.


```python
# Install required packages
# !pip install -q deepagents langchain-openai tavily-python requests tenacity pydantic python-dotenv
```

### Import Libraries and Load Environment Variables


```python
import os
import logging
import time
from datetime import datetime
from pathlib import Path
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

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

# Load environment variables
load_dotenv()

# Verify all API keys are loaded
required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY", "OPENWEATHER_API_KEY"]
for key in required_keys:
    if not os.getenv(key):
        raise ValueError(f"{key} not found in environment variables")

print("All API keys loaded successfully!")
print("Required packages imported successfully!")
```

    All API keys loaded successfully!
    Required packages imported successfully!


### Configure Structured Logging

Logging is critical in multi-agent systems to understand:
- Which sub-agent is executing which task
- How long each sub-task takes
- The sequence of orchestration decisions


```python
# Configure logging with structured format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create loggers for different components
logger = logging.getLogger('multi_agent_system')
weather_logger = logging.getLogger('weather_agent')
research_logger = logging.getLogger('research_agent')
orchestrator_logger = logging.getLogger('orchestrator')

logger.info("Multi-agent logging system initialized")
print("Logging configured - you'll see detailed execution traces below")
```

    2025-11-17 15:31:39 - multi_agent_system - INFO - Multi-agent logging system initialized


    Logging configured - you'll see detailed execution traces below


## Part 2: Building Production-Grade Weather Tools

Our Weather Agent needs robust, production-ready tools. We'll implement:
- Geocoding helper (convert city names to coordinates)
- Pydantic validation models
- Weather API client with retry logic
- Two weather tools: current conditions and 2-day forecast

### Step 1: Geocoding Helper Function

Convert user-friendly city names to the lat/lon coordinates required by the weather API.


```python
def geocode_city(city_name: str) -> tuple[float, float]:
    """
    Convert a city name to latitude and longitude coordinates.
    
    Args:
        city_name: The name of the city (e.g., "Tokyo", "London")
        
    Returns:
        tuple[float, float]: (latitude, longitude)
        
    Raises:
        ValueError: If city not found or invalid
    """
    city_name = city_name.strip()
    
    if not city_name:
        raise ValueError("City name cannot be empty")
    
    # Sanitize input: allow only safe characters
    if not all(c.isalnum() or c in " -'," for c in city_name):
        raise ValueError(f"Invalid city name format: {city_name}")
    
    weather_logger.info(f"Geocoding city: {city_name}")
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = "http://api.openweathermap.org/geo/1.0/direct"
    
    params = {
        "q": city_name,
        "limit": 1,
        "appid": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            raise ValueError(
                f"Could not find coordinates for '{city_name}'. "
                "Please check the spelling."
            )
        
        lat = data[0]["lat"]
        lon = data[0]["lon"]
        
        weather_logger.info(f"Geocoded {city_name} to ({lat}, {lon})")
        return lat, lon
        
    except requests.exceptions.RequestException as e:
        weather_logger.error(f"Geocoding failed: {str(e)}")
        raise ValueError(f"Failed to geocode city: {str(e)}")

# Test geocoding
lat, lon = geocode_city("Tokyo")
print(f"Tokyo coordinates: {lat}, {lon}")
```

    2025-11-17 15:31:39 - weather_agent - INFO - Geocoding city: Tokyo
    2025-11-17 15:31:40 - weather_agent - INFO - Geocoded Tokyo to (35.6828387, 139.7594549)


    Tokyo coordinates: 35.6828387, 139.7594549


### Step 2: Pydantic Validation Models

Type-safe input validation prevents errors before they reach the API.


```python
class WeatherLocation(BaseModel):
    """Validates location input for weather queries."""
    city: str = Field(
        ..., 
        min_length=1,
        max_length=100,
        description="City name"
    )
    
    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("City name cannot be empty")
        if not all(c.isalnum() or c in " -'," for c in v):
            raise ValueError("City name contains invalid characters")
        return v


class ForecastWeatherInput(BaseModel):
    """Validates forecast input (always 2 days)."""
    city: str = Field(..., min_length=1, max_length=100)
    days: int = Field(default=2, description="Forecast days (must be 2)")
    
    @field_validator('days')
    @classmethod
    def validate_days(cls, v):
        if v != 2:
            raise ValueError(f"Forecast only available for 2 days. Got: {v}")
        return v
    
    @field_validator('city')
    @classmethod
    def validate_city(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("City name cannot be empty")
        if not all(c.isalnum() or c in " -'," for c in v):
            raise ValueError("City name contains invalid characters")
        return v

# Test validation
location = WeatherLocation(city="Tokyo")
forecast_input = ForecastWeatherInput(city="Tokyo", days=2)
print(f"Validation models working: {location.city}, {forecast_input.days} days")
```

    Validation models working: Tokyo, 2 days


### Step 3: Weather API Client with Retry Logic

Production-grade client with:
- Connection pooling for performance
- Automatic retries with exponential backoff
- Comprehensive error handling
- Request timing and logging


```python
class WeatherAPIClient:
    """
    Production-grade Weather API client with resilience and observability.
    
    Features:
    - Connection pooling via requests.Session
    - Automatic retries with exponential backoff
    - Structured logging
    - Comprehensive error handling
    """
    
    def __init__(self, api_key: str, timeout: int = 10, max_retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Connection pooling
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        weather_logger.info("Weather API Client initialized")
    
    def _log_request(self, endpoint: str, params: Dict[str, Any], 
                     duration: float, success: bool):
        """Log API request with sanitized parameters."""
        safe_params = {k: v for k, v in params.items() if k != 'appid'}
        safe_params['appid'] = '***REDACTED***'
        status = "SUCCESS" if success else "FAILURE"
        weather_logger.info(
            f"API [{status}] - {endpoint} - {duration:.2f}s - {safe_params}"
        )
    
    @retry(
        retry=retry_if_exception_type((requests.exceptions.Timeout, 
                                      requests.exceptions.ConnectionError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=before_sleep_log(weather_logger, logging.WARNING)
    )
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        start_time = time.time()
        
        try:
            params['appid'] = self.api_key
            response = self.session.get(endpoint, params=params, timeout=self.timeout)
            duration = time.time() - start_time
            
            if response.status_code == 401:
                self._log_request(endpoint, params, duration, False)
                raise ValueError("Authentication failed. Check API key.")
            
            if response.status_code == 404:
                self._log_request(endpoint, params, duration, False)
                raise ValueError("Location not found.")
            
            if response.status_code == 429:
                self._log_request(endpoint, params, duration, False)
                raise ValueError("Rate limit exceeded.")
            
            response.raise_for_status()
            data = response.json()
            self._log_request(endpoint, params, duration, True)
            return data
            
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self._log_request(endpoint, params, duration, False)
            raise TimeoutError(f"Request timed out after {self.timeout}s")
        
        except requests.exceptions.ConnectionError as e:
            duration = time.time() - start_time
            self._log_request(endpoint, params, duration, False)
            raise ConnectionError("Unable to connect to weather service")
    
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather for coordinates."""
        endpoint = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "units": "metric"}
        return self._make_request(endpoint, params)
    
    def get_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get 2-day forecast using free tier 5 Day / 3 Hour Forecast API."""
        endpoint = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat, 
            "lon": lon, 
            "units": "metric",
            "cnt": 16  # 2 days * 8 forecasts per day
        }
        return self._make_request(endpoint, params)

# Initialize the API client
weather_api_client = WeatherAPIClient(
    api_key=os.getenv("OPENWEATHER_API_KEY"),
    timeout=10,
    max_retries=3
)

print("Weather API Client initialized with connection pooling and retries")
```

    2025-11-17 15:31:40 - weather_agent - INFO - Weather API Client initialized


    Weather API Client initialized with connection pooling and retries


### Step 4: Current Weather Tool

This tool will be used by our Weather Agent to get current conditions.


```python
def get_current_weather(city: str) -> str:
    """
    Get current weather conditions for a city.
    
    Use this when asked about current weather, present conditions,
    or "right now" weather.
    
    Args:
        city: City name (e.g., "Tokyo", "London")
        
    Returns:
        str: Human-readable current weather description
    """
    weather_logger.info(f"get_current_weather called for: {city}")
    start_time = time.time()
    
    try:
        # Validate input
        location = WeatherLocation(city=city)
        
        # Geocode
        lat, lon = geocode_city(location.city)
        
        # Fetch weather
        weather_data = weather_api_client.get_current_weather(lat, lon)
        
        # Format response
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
        weather_logger.info(f"Tool completed in {duration:.2f}s")
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        weather_logger.error(f"Error after {duration:.2f}s: {str(e)}")
        return f"Error: {str(e)}"

# Test the tool
result = get_current_weather("Tokyo")
print(result)
```

    2025-11-17 15:31:40 - weather_agent - INFO - get_current_weather called for: Tokyo
    2025-11-17 15:31:40 - weather_agent - INFO - Geocoding city: Tokyo
    2025-11-17 15:31:40 - weather_agent - INFO - Geocoded Tokyo to (35.6828387, 139.7594549)
    2025-11-17 15:31:41 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/weather - 0.93s - {'lat': 35.6828387, 'lon': 139.7594549, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-17 15:31:41 - weather_agent - INFO - Tool completed in 1.05s


    Current weather in Tokyo:
      Temperature: 19.41°C (feels like 18.61°C)
      Conditions: Clear sky
      Humidity: 46%
      Wind Speed: 5.14 m/s


### Step 5: Weather Forecast Tool

This tool provides 2-day weather forecasts.


```python
def get_weather_forecast(city: str) -> str:
    """
    Get weather forecast for the next 2 days.
    
    Use this when asked about future weather, tomorrow's weather,
    or weather predictions.
    
    Args:
        city: City name (e.g., "Tokyo", "London")
        
    Returns:
        str: 2-day forecast with temperatures and conditions
    """
    weather_logger.info(f"get_weather_forecast called for: {city}")
    start_time = time.time()
    
    try:
        # Validate
        input_data = ForecastWeatherInput(city=city, days=2)
        
        # Geocode
        lat, lon = geocode_city(input_data.city)
        
        # Fetch forecast
        forecast_data = weather_api_client.get_forecast(lat, lon)
        
        # Process forecast data (group by day)
        forecast_list = forecast_data['list']
        daily_forecasts = defaultdict(list)
        
        for forecast in forecast_list:
            forecast_date = datetime.fromtimestamp(forecast['dt']).date()
            daily_forecasts[forecast_date].append(forecast)
        
        # Get next 2 days
        sorted_dates = sorted(daily_forecasts.keys())[:2]
        results = []
        
        for i, date in enumerate(sorted_dates):
            day_forecasts = daily_forecasts[date]
            day_label = "tomorrow" if i == 0 else "day after tomorrow"
            
            # Calculate daily statistics
            temps = [f['main']['temp'] for f in day_forecasts]
            temp_min = min(f['main']['temp_min'] for f in day_forecasts)
            temp_max = max(f['main']['temp_max'] for f in day_forecasts)
            avg_temp = sum(temps) / len(temps)
            
            # Most common condition
            conditions = [f['weather'][0]['description'] for f in day_forecasts]
            most_common = max(set(conditions), key=conditions.count)
            
            # Averages
            avg_humidity = sum(f['main']['humidity'] for f in day_forecasts) / len(day_forecasts)
            avg_wind = sum(f['wind']['speed'] for f in day_forecasts) / len(day_forecasts)
            
            results.append(
                f"  {date.strftime('%Y-%m-%d')} ({day_label}):\n"
                f"    Temp: {avg_temp:.1f}°C (High: {temp_max:.1f}°C, Low: {temp_min:.1f}°C)\n"
                f"    Conditions: {most_common.capitalize()}\n"
                f"    Humidity: {avg_humidity:.0f}%\n"
                f"    Wind: {avg_wind:.1f} m/s"
            )
        
        result = f"Weather forecast for {input_data.city} (next 2 days):\n\n" + "\n\n".join(results)
        
        duration = time.time() - start_time
        weather_logger.info(f"Tool completed in {duration:.2f}s")
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        weather_logger.error(f"Error after {duration:.2f}s: {str(e)}")
        return f"Error: {str(e)}"

# Test the tool
result = get_weather_forecast("Tokyo")
print(result)
```

    2025-11-17 15:31:41 - weather_agent - INFO - get_weather_forecast called for: Tokyo
    2025-11-17 15:31:41 - weather_agent - INFO - Geocoding city: Tokyo
    2025-11-17 15:31:41 - weather_agent - INFO - Geocoded Tokyo to (35.6828387, 139.7594549)
    2025-11-17 15:31:42 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/forecast - 0.28s - {'lat': 35.6828387, 'lon': 139.7594549, 'units': 'metric', 'cnt': 16, 'appid': '***REDACTED***'}
    2025-11-17 15:31:42 - weather_agent - INFO - Tool completed in 0.77s


    Weather forecast for Tokyo (next 2 days):
    
      2025-11-17 (tomorrow):
        Temp: 16.1°C (High: 18.8°C, Low: 13.5°C)
        Conditions: Clear sky
        Humidity: 46%
        Wind: 5.9 m/s
    
      2025-11-18 (day after tomorrow):
        Temp: 11.4°C (High: 12.3°C, Low: 9.5°C)
        Conditions: Light rain
        Humidity: 60%
        Wind: 3.3 m/s


## Part 3: Building the Research Agent

The Research Agent specializes in web search using Tavily. It has a focused system prompt and only one tool.

### Step 1: Create the Tavily Search Tool


```python
# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def internet_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web for information using Tavily.
    
    Args:
        query: Search query string
        max_results: Maximum results to return (default: 5)
    
    Returns:
        dict: Search results with titles, URLs, and content
    """
    research_logger.info(f"Searching: {query}")
    try:
        results = tavily_client.search(query, max_results=max_results)
        research_logger.info(f"Found {len(results.get('results', []))} results")
        return results
    except Exception as e:
        research_logger.error(f"Search failed: {str(e)}")
        return {"error": f"Search failed: {str(e)}"}

print("Tavily search tool configured")
```

    Tavily search tool configured


### Step 2: Create the Research Agent

Notice the specialized system prompt - it only knows about research, not weather.


```python
# Create workspace for shared files
workspace_dir = Path("./multi_agent_workspace")
workspace_dir.mkdir(exist_ok=True)

# Research Agent system prompt - focused on research only
research_system_prompt = """You are an expert research assistant specializing in web search and information gathering.

YOUR EXPERTISE:
- Conduct thorough web research using internet search
- Synthesize information from multiple sources
- Provide well-organized research summaries
- Cite sources when presenting findings

RESEARCH WORKFLOW:
1. Break down complex research questions into specific search queries
2. Search for information systematically
3. Analyze and synthesize findings
4. Save comprehensive research reports to files

TOOL USAGE:
- Use internet_search for all web research needs
- Start with broad searches, then narrow based on results
- Always verify facts from multiple sources
- Save detailed findings to files for later reference

You do NOT handle weather queries - focus only on research tasks.
"""

# Create Research Agent
research_model = ChatOpenAI(model="gpt-4o", temperature=0.1)

research_agent = create_deep_agent(
    model=research_model,
    tools=[internet_search],
    system_prompt=research_system_prompt,
    backend=FilesystemBackend(root_dir=str(workspace_dir), virtual_mode=True)
)

research_logger.info("Research Agent created")
print("Research Agent created successfully!")
print("Capabilities: Web search, file I/O, planning")
print(f"Shared workspace: {workspace_dir.absolute()}")
```

    2025-11-17 15:31:42 - research_agent - INFO - Research Agent created


    Research Agent created successfully!
    Capabilities: Web search, file I/O, planning
    Shared workspace: /Users/sajal/code/active/projects/oreilly_ai_agent_skill/level_4/multi_agent_workspace


## Part 4: Building the Weather Agent

The Weather Agent specializes in weather data. It only knows about weather tools.


```python
# Weather Agent system prompt - focused on weather only
weather_system_prompt = """You are an expert weather information specialist.

YOUR EXPERTISE:
- Provide current weather conditions for any city
- Provide 2-day weather forecasts
- Interpret weather data clearly for users

AVAILABLE TOOLS:
- get_current_weather: Use for current/present conditions
- get_weather_forecast: Use for future weather (next 2 days)

TOOL SELECTION:
- "What's the weather now?" → get_current_weather
- "What's the forecast?" → get_weather_forecast
- "Weather this week?" → get_weather_forecast (only have 2 days)

RESPONSE FORMAT:
- Present temperature in Celsius
- Include all relevant conditions (humidity, wind, etc.)
- Be concise but complete
- Save weather reports to files when requested

You do NOT handle research queries - focus only on weather tasks.
"""

# Create Weather Agent
weather_model = ChatOpenAI(model="gpt-4o", temperature=0.1)

weather_agent = create_deep_agent(
    model=weather_model,
    tools=[get_current_weather, get_weather_forecast],
    system_prompt=weather_system_prompt,
    backend=FilesystemBackend(root_dir=str(workspace_dir), virtual_mode=True)
)

weather_logger.info("Weather Agent created")
print("Weather Agent created successfully!")
print("Capabilities: Current weather, 2-day forecast, file I/O")
print(f"Shared workspace: {workspace_dir.absolute()}")
```

    2025-11-17 15:31:42 - weather_agent - INFO - Weather Agent created


    Weather Agent created successfully!
    Capabilities: Current weather, 2-day forecast, file I/O
    Shared workspace: /Users/sajal/code/active/projects/oreilly_ai_agent_skill/level_4/multi_agent_workspace


## Part 5: Building the Orchestrator Agent

The Orchestrator coordinates sub-agents. It doesn't have domain tools - it has the `task` tool to spawn sub-agents.


```python
# Orchestrator system prompt - coordination and delegation
orchestrator_system_prompt = """You are an orchestrator agent that coordinates specialized sub-agents.

YOUR ROLE:
- Analyze user requests and break them into sub-tasks
- Delegate sub-tasks to specialized agents
- Synthesize results from multiple agents into comprehensive responses

AVAILABLE SUB-AGENTS:
1. **Research Agent** (subagent_type='research')
   - Use for: Web research, information gathering, learning about cities/topics
   - Capabilities: Internet search, synthesis, citation

2. **Weather Agent** (subagent_type='weather')
   - Use for: Current weather, weather forecasts
   - Capabilities: Current conditions, 2-day forecasts

ORCHESTRATION PATTERN:
1. Analyze the user's request
2. Identify which sub-agents are needed
3. Use the 'task' tool to spawn sub-agents (can run in parallel)
4. Collect results from sub-agents
5. Synthesize into a coherent, comprehensive response

TASK TOOL USAGE:
- description: Clear description of what the sub-agent should do
- subagent_type: 'research' or 'weather'

Example:
User: "I'm traveling to Tokyo. Research the city and tell me the weather."
→ Spawn research agent: "Research Tokyo: culture, attractions, travel tips"
→ Spawn weather agent: "Get current weather and 2-day forecast for Tokyo"
→ Synthesize both results into travel brief

RESPONSE QUALITY:
- Combine all sub-agent results into a cohesive response
- Organize information logically
- Ensure completeness - answer all parts of the user's query
"""

# Create Orchestrator Agent with access to sub-agents
orchestrator_model = ChatOpenAI(model="gpt-4o", temperature=0.1)

# Define subagents in the correct format: list of dictionaries
subagent_list = [
    {
        'name': 'research',
        'description': 'Expert research assistant for web search and information gathering',
        'runnable': research_agent
    },
    {
        'name': 'weather',
        'description': 'Weather specialist for current conditions and forecasts',
        'runnable': weather_agent
    }
]

orchestrator = create_deep_agent(
    model=orchestrator_model,
    tools=[],  # No domain tools - only uses task tool for sub-agents
    system_prompt=orchestrator_system_prompt,
    backend=FilesystemBackend(root_dir=str(workspace_dir), virtual_mode=True),
    subagents=subagent_list  # Pass as list of dicts with name, description, runnable
)

orchestrator_logger.info("Orchestrator Agent created")
print("Orchestrator Agent created successfully!")
print("Capabilities: Task decomposition, sub-agent coordination, synthesis")
print(f"Sub-agents: research, weather")
print(f"Shared workspace: {workspace_dir.absolute()}")
```

    2025-11-17 15:31:42 - orchestrator - INFO - Orchestrator Agent created


    Orchestrator Agent created successfully!
    Capabilities: Task decomposition, sub-agent coordination, synthesis
    Sub-agents: research, weather
    Shared workspace: /Users/sajal/code/active/projects/oreilly_ai_agent_skill/level_4/multi_agent_workspace


## Part 6: Testing the Multi-Agent System

Now let's test our orchestrator with a complex query that requires both research and weather.

### Helper Function: Stream Orchestrator Responses

This helper shows the orchestration process including sub-agent spawning.


```python
def stream_orchestrator(query: str, show_details: bool = True):
    """
    Stream orchestrator execution with detailed logging.
    
    Args:
        query: User query
        show_details: Show detailed tool calls and sub-agent spawning
    """
    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)
    print()
    
    seen_message_ids = set()
    
    for chunk in orchestrator.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values"
    ):
        if "messages" in chunk:
            for message in chunk["messages"]:
                msg_id = message.id
                if msg_id in seen_message_ids:
                    continue
                seen_message_ids.add(msg_id)
                
                msg_type = getattr(message, 'type', 'unknown')
                
                if msg_type == 'human':
                    print(f"[USER] {message.content}")
                    print("-" * 80)
                
                elif msg_type == 'ai':
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        print(f"[ORCHESTRATOR] Calling {len(message.tool_calls)} tool(s):")
                        for tc in message.tool_calls:
                            tool_name = tc.get('name', 'unknown')
                            tool_args = tc.get('args', {})
                            
                            if tool_name == 'task' and show_details:
                                subagent_type = tool_args.get('subagent_type', 'unknown')
                                description = tool_args.get('description', '')[:80]
                                print(f"  - Spawning {subagent_type} agent: {description}...")
                            elif tool_name == 'write_todos' and show_details:
                                todos = tool_args.get('todos', [])
                                print(f"  - Planning {len(todos)} tasks")
                            else:
                                print(f"  - {tool_name}()")
                    elif message.content:
                        print(f"[ORCHESTRATOR] {message.content}")
                    print("-" * 80)
                
                elif msg_type == 'tool':
                    tool_name = getattr(message, 'name', 'unknown')
                    if show_details:
                        print(f"[TOOL: {tool_name}] Completed")
                        print("-" * 80)
    
    print()
    print("=" * 80)
    print("ORCHESTRATION COMPLETED")
    print("=" * 80)

print("Helper function created!")
```

    Helper function created!


### Example 1: Travel Planning Query

This complex query requires both research and weather information.

**Expected Behavior:**
1. Orchestrator analyzes the query
2. Spawns research agent: "Research Tokyo travel information"
3. Spawns weather agent: "Get weather forecast for Tokyo"
4. Both agents run (potentially in parallel)
5. Orchestrator synthesizes results into comprehensive travel brief

**Watch For:**
- Task decomposition (planning todos)
- Sub-agent spawning (task tool calls)
- Parallel execution (both agents working simultaneously)
- Result synthesis (combining research + weather)


```python
# Example 1: Complex travel planning query
travel_query = """
I'm planning a trip to Tokyo next week. I need:
1. Research about Tokyo - culture, top attractions, and travel tips
2. Weather forecast for the next 2 days so I know what to pack

Please provide a comprehensive travel brief.
"""

stream_orchestrator(travel_query, show_details=True)
```

    ================================================================================
    QUERY: 
    I'm planning a trip to Tokyo next week. I need:
    1. Research about Tokyo - culture, top attractions, and travel tips
    2. Weather forecast for the next 2 days so I know what to pack
    
    Please provide a comprehensive travel brief.
    
    ================================================================================
    
    [USER] 
    I'm planning a trip to Tokyo next week. I need:
    1. Research about Tokyo - culture, top attractions, and travel tips
    2. Weather forecast for the next 2 days so I know what to pack
    
    Please provide a comprehensive travel brief.
    
    --------------------------------------------------------------------------------


    2025-11-17 15:31:45 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [ORCHESTRATOR] Calling 2 tool(s):
      - Spawning research agent: Research Tokyo: culture, top attractions, and travel tips...
      - Spawning weather agent: Get current weather and 2-day forecast for Tokyo...
    --------------------------------------------------------------------------------


    2025-11-17 15:31:47 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:31:47 - weather_agent - INFO - get_current_weather called for: Tokyo
    2025-11-17 15:31:47 - weather_agent - INFO - Geocoding city: Tokyo
    2025-11-17 15:31:47 - weather_agent - INFO - get_weather_forecast called for: Tokyo
    2025-11-17 15:31:47 - weather_agent - INFO - Geocoding city: Tokyo
    2025-11-17 15:31:47 - weather_agent - INFO - Geocoded Tokyo to (35.6828387, 139.7594549)
    2025-11-17 15:31:47 - weather_agent - INFO - Geocoded Tokyo to (35.6828387, 139.7594549)
    2025-11-17 15:31:47 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/weather - 0.06s - {'lat': 35.6828387, 'lon': 139.7594549, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-17 15:31:47 - weather_agent - INFO - Tool completed in 0.19s
    2025-11-17 15:31:47 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/forecast - 0.19s - {'lat': 35.6828387, 'lon': 139.7594549, 'units': 'metric', 'cnt': 16, 'appid': '***REDACTED***'}
    2025-11-17 15:31:47 - weather_agent - INFO - Tool completed in 0.32s
    2025-11-17 15:31:50 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:31:50 - research_agent - INFO - Searching: Tokyo culture overview
    2025-11-17 15:31:50 - research_agent - INFO - Searching: Top attractions in Tokyo
    2025-11-17 15:31:50 - research_agent - INFO - Searching: Travel tips for visiting Tokyo
    2025-11-17 15:31:50 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:31:52 - research_agent - INFO - Found 5 results
    2025-11-17 15:31:52 - research_agent - INFO - Found 5 results
    2025-11-17 15:31:53 - research_agent - INFO - Found 5 results
    2025-11-17 15:32:10 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [TOOL: task] Completed
    --------------------------------------------------------------------------------
    [TOOL: task] Completed
    --------------------------------------------------------------------------------


    2025-11-17 15:32:16 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [ORCHESTRATOR] Here's a comprehensive travel brief for your upcoming trip to Tokyo:
    
    ### Culture of Tokyo
    Tokyo is a city where tradition and modernity coexist harmoniously. The cultural landscape is a dynamic fusion of historical practices and contemporary innovations. Key cultural elements include:
    - **Traditional Arts**: Kabuki and Noh are prominent traditional performing arts in Tokyo.
    - **Modern Influences**: The city is a hub for pop culture phenomena, including anime and manga.
    - **Cultural Sites**: Tokyo offers a rich history with ancient temples and modern architectural marvels.
    - **Diverse Neighborhoods**: Each area in Tokyo has its unique cultural flavor, from the historic Asakusa to the bustling Shibuya.
    
    ### Top Attractions in Tokyo
    Tokyo is filled with must-see attractions that cater to a variety of interests:
    - **Shinjuku Gyoen National Garden**: A beautiful garden perfect for a relaxing stroll.
    - **Senso-ji Temple**: Tokyo's oldest temple, located in Asakusa.
    - **Tokyo Skytree and Tokyo Tower**: Iconic landmarks offering panoramic views of the city.
    - **Meiji Shrine**: A serene Shinto shrine surrounded by a forested area.
    - **TeamLab Planets**: An immersive digital art museum in Toyosu.
    - **Imperial Palace**: The primary residence of the Emperor of Japan.
    
    ### Travel Tips for Visiting Tokyo
    - **Best Time to Visit**: Spring and fall are ideal due to pleasant weather.
    - **Transportation**: Consider getting an IC card (like Suica) for convenient travel on public transport.
    - **Footwear**: Bring comfortable, waterproof shoes as you'll likely do a lot of walking.
    - **Connectivity**: While there are many Wi-Fi spots, they can be unreliable, so plan accordingly.
    - **Local Etiquette**: Familiarize yourself with basic Japanese phrases and customs to enhance your experience.
    
    ### Weather Forecast for Tokyo
    **Current Weather:**
    - Temperature: 19.41°C (feels like 18.61°C)
    - Conditions: Clear sky
    - Humidity: 46%
    - Wind Speed: 5.14 m/s
    
    **2-Day Forecast:**
    - **Tomorrow (2025-11-17):**
      - Temperature: 16.1°C (High: 18.8°C, Low: 13.5°C)
      - Conditions: Clear sky
      - Humidity: 46%
      - Wind: 5.9 m/s
    
    - **Day After Tomorrow (2025-11-18):**
      - Temperature: 11.4°C (High: 12.3°C, Low: 9.5°C)
      - Conditions: Light rain
      - Humidity: 60%
      - Wind: 3.3 m/s
    
    This information should help you plan your trip effectively, ensuring you experience the best of Tokyo's culture, attractions, and weather. Enjoy your trip!
    --------------------------------------------------------------------------------
    
    ================================================================================
    ORCHESTRATION COMPLETED
    ================================================================================


### Example 2: Multi-City Comparison

Test the orchestrator's ability to handle multiple locations.


```python
# Example 2: Multi-city comparison
comparison_query = """
I'm deciding between visiting Paris or London next month.
Research both cities and compare their weather forecasts.
Help me decide which would be better for a week-long trip.
"""

stream_orchestrator(comparison_query, show_details=True)
```

    ================================================================================
    QUERY: 
    I'm deciding between visiting Paris or London next month.
    Research both cities and compare their weather forecasts.
    Help me decide which would be better for a week-long trip.
    
    ================================================================================
    
    [USER] 
    I'm deciding between visiting Paris or London next month.
    Research both cities and compare their weather forecasts.
    Help me decide which would be better for a week-long trip.
    
    --------------------------------------------------------------------------------


    2025-11-17 15:32:18 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [ORCHESTRATOR] Calling 4 tool(s):
      - Spawning research agent: Research Paris: culture, attractions, travel tips...
      - Spawning research agent: Research London: culture, attractions, travel tips...
      - Spawning weather agent: Get current weather and 2-day forecast for Paris...
      - Spawning weather agent: Get current weather and 2-day forecast for London...
    --------------------------------------------------------------------------------


    2025-11-17 15:32:20 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:20 - weather_agent - INFO - get_current_weather called for: London
    2025-11-17 15:32:20 - weather_agent - INFO - get_weather_forecast called for: London
    2025-11-17 15:32:20 - weather_agent - INFO - Geocoding city: London
    2025-11-17 15:32:20 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:20 - weather_agent - INFO - Geocoding city: London
    2025-11-17 15:32:20 - weather_agent - INFO - get_current_weather called for: Paris
    2025-11-17 15:32:20 - weather_agent - INFO - get_weather_forecast called for: Paris
    2025-11-17 15:32:20 - weather_agent - INFO - Geocoding city: Paris
    2025-11-17 15:32:20 - weather_agent - INFO - Geocoding city: Paris
    2025-11-17 15:32:20 - weather_agent - INFO - Geocoded London to (51.5073219, -0.1276474)
    2025-11-17 15:32:20 - weather_agent - INFO - Geocoded Paris to (48.8588897, 2.3200410217200766)
    2025-11-17 15:32:20 - weather_agent - INFO - Geocoded London to (51.5073219, -0.1276474)
    2025-11-17 15:32:20 - weather_agent - INFO - Geocoded Paris to (48.8588897, 2.3200410217200766)
    2025-11-17 15:32:21 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/weather - 0.06s - {'lat': 51.5073219, 'lon': -0.1276474, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-17 15:32:21 - weather_agent - INFO - Tool completed in 0.46s
    2025-11-17 15:32:21 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/forecast - 0.07s - {'lat': 48.8588897, 'lon': 2.3200410217200766, 'units': 'metric', 'cnt': 16, 'appid': '***REDACTED***'}
    2025-11-17 15:32:21 - weather_agent - INFO - Tool completed in 0.47s
    2025-11-17 15:32:21 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/weather - 0.19s - {'lat': 48.8588897, 'lon': 2.3200410217200766, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-17 15:32:21 - weather_agent - INFO - Tool completed in 0.61s
    2025-11-17 15:32:21 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/forecast - 0.20s - {'lat': 51.5073219, 'lon': -0.1276474, 'units': 'metric', 'cnt': 16, 'appid': '***REDACTED***'}
    2025-11-17 15:32:21 - weather_agent - INFO - Tool completed in 0.63s
    2025-11-17 15:32:21 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:21 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:23 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:23 - research_agent - INFO - Searching: London culture historical influences arts local customs
    2025-11-17 15:32:23 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:23 - research_agent - INFO - Searching: Paris culture history art lifestyle
    2025-11-17 15:32:23 - research_agent - INFO - Searching: Paris popular attractions landmarks museums parks
    2025-11-17 15:32:23 - research_agent - INFO - Searching: Paris travel tips best times to visit transportation local customs
    2025-11-17 15:32:24 - research_agent - INFO - Found 5 results
    2025-11-17 15:32:25 - research_agent - INFO - Found 5 results
    2025-11-17 15:32:25 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:25 - research_agent - INFO - Found 5 results
    2025-11-17 15:32:25 - research_agent - INFO - Found 5 results
    2025-11-17 15:32:25 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:30 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:31 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:31 - research_agent - INFO - Searching: major attractions in London landmarks museums parks
    2025-11-17 15:32:32 - research_agent - INFO - Found 5 results
    2025-11-17 15:32:34 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:36 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:36 - research_agent - INFO - Searching: travel tips for visiting London transportation accommodation dining
    2025-11-17 15:32:36 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:38 - research_agent - INFO - Found 5 results
    2025-11-17 15:32:38 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:45 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:46 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [TOOL: task] Completed
    --------------------------------------------------------------------------------
    [TOOL: task] Completed
    --------------------------------------------------------------------------------
    [TOOL: task] Completed
    --------------------------------------------------------------------------------
    [TOOL: task] Completed
    --------------------------------------------------------------------------------


    2025-11-17 15:32:54 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [ORCHESTRATOR] I've gathered detailed information on both Paris and London, including their cultural highlights, attractions, and travel tips, as well as their current weather conditions and forecasts. Here's a summary to help you decide which city might be better for your week-long trip:
    
    ### Paris
    - **Culture & Attractions**: Paris is renowned for its rich history, art, and architecture. Key attractions include the Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, and charming neighborhoods like Montmartre.
    - **Travel Tips**: Paris offers a vibrant café culture, excellent public transport, and numerous parks and gardens.
    - **Weather**:
      - **Current**: 7.36°C, feels like 4.23°C, broken clouds, 88% humidity.
      - **Forecast**:
        - **Tomorrow**: 7.5°C, scattered clouds, 63% humidity.
        - **Day After Tomorrow**: 6.6°C, clear sky, 55% humidity.
    
    For more detailed insights, you can review the [Paris Research Report](sandbox:/Paris_Research_Report.txt).
    
    ### London
    - **Culture & Attractions**: London is a bustling metropolis with a mix of modern and historical sites. Highlights include the British Museum, Tower of London, Buckingham Palace, and vibrant areas like Camden and Shoreditch.
    - **Travel Tips**: London is known for its diverse food scene, extensive public transport, and numerous parks.
    - **Weather**:
      - **Current**: 5.84°C, feels like 2.32°C, broken clouds, 80% humidity.
      - **Forecast**:
        - **Tomorrow**: 6.7°C, few clouds, 67% humidity.
        - **Day After Tomorrow**: 4.5°C, scattered clouds, 73% humidity.
    
    For a comprehensive guide, you can check the [London Travel Guide](sandbox:/research/London_Travel_Guide.txt).
    
    ### Decision Factors
    - **Weather**: Both cities have similar weather conditions, with Paris being slightly warmer and clearer in the coming days.
    - **Cultural Experience**: Both cities offer rich cultural experiences, but your preference for art, history, or modern attractions might sway your decision.
    
    Consider what type of experiences you value most and the weather conditions that suit your preferences. Both cities have a lot to offer, so you can't go wrong with either choice!
    --------------------------------------------------------------------------------
    
    ================================================================================
    ORCHESTRATION COMPLETED
    ================================================================================


### Example 3: Single Sub-Agent Query

Test that the orchestrator correctly handles queries requiring only one sub-agent.


```python
# Example 3: Weather-only query
weather_only_query = "What's the weather forecast for Singapore for the next 2 days?"

stream_orchestrator(weather_only_query, show_details=True)
```

    ================================================================================
    QUERY: What's the weather forecast for Singapore for the next 2 days?
    ================================================================================
    
    [USER] What's the weather forecast for Singapore for the next 2 days?
    --------------------------------------------------------------------------------


    2025-11-17 15:32:55 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [ORCHESTRATOR] Calling 1 tool(s):
      - Spawning weather agent: Get current weather and 2-day forecast for Singapore...
    --------------------------------------------------------------------------------


    2025-11-17 15:32:56 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:32:56 - weather_agent - INFO - get_weather_forecast called for: Singapore
    2025-11-17 15:32:56 - weather_agent - INFO - get_current_weather called for: Singapore
    2025-11-17 15:32:56 - weather_agent - INFO - Geocoding city: Singapore
    2025-11-17 15:32:56 - weather_agent - INFO - Geocoding city: Singapore
    2025-11-17 15:32:56 - weather_agent - INFO - Geocoded Singapore to (1.2899175, 103.8519072)
    2025-11-17 15:32:56 - weather_agent - INFO - Geocoded Singapore to (1.2899175, 103.8519072)
    2025-11-17 15:32:56 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/weather - 0.07s - {'lat': 1.2899175, 'lon': 103.8519072, 'units': 'metric', 'appid': '***REDACTED***'}
    2025-11-17 15:32:56 - weather_agent - INFO - Tool completed in 0.45s
    2025-11-17 15:32:56 - weather_agent - INFO - API [SUCCESS] - https://api.openweathermap.org/data/2.5/forecast - 0.08s - {'lat': 1.2899175, 'lon': 103.8519072, 'units': 'metric', 'cnt': 16, 'appid': '***REDACTED***'}
    2025-11-17 15:32:56 - weather_agent - INFO - Tool completed in 0.46s
    2025-11-17 15:32:59 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [TOOL: task] Completed
    --------------------------------------------------------------------------------


    2025-11-17 15:33:03 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [ORCHESTRATOR] Here's the current weather and 2-day forecast for Singapore:
    
    **Current Weather in Singapore:**
    - Temperature: 27.81°C (feels like 31.77°C)
    - Conditions: Scattered clouds
    - Humidity: 81%
    - Wind Speed: 2.06 m/s
    
    **Weather Forecast for the Next 2 Days:**
    
    **November 17, 2025 (Tomorrow):**
    - Temperature: 28.5°C (High: 29.3°C, Low: 28.3°C)
    - Conditions: Light rain
    - Humidity: 80%
    - Wind Speed: 2.8 m/s
    
    **November 18, 2025 (Day After Tomorrow):**
    - Temperature: 27.7°C (High: 28.9°C, Low: 26.8°C)
    - Conditions: Light rain
    - Humidity: 78%
    - Wind Speed: 4.3 m/s
    
    Stay prepared for some light rain over the next couple of days!
    --------------------------------------------------------------------------------
    
    ================================================================================
    ORCHESTRATION COMPLETED
    ================================================================================



```python
# Example 4: Research-only query
research_only_query = "Research the best time to visit Iceland and what activities are popular there."

stream_orchestrator(research_only_query, show_details=True)
```

    ================================================================================
    QUERY: Research the best time to visit Iceland and what activities are popular there.
    ================================================================================
    
    [USER] Research the best time to visit Iceland and what activities are popular there.
    --------------------------------------------------------------------------------


    2025-11-17 15:33:04 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [ORCHESTRATOR] Calling 1 tool(s):
      - Spawning research agent: Research the best time to visit Iceland, considering weather, tourist seasons, a...
    --------------------------------------------------------------------------------


    2025-11-17 15:33:06 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-11-17 15:33:06 - research_agent - INFO - Searching: best time to visit Iceland weather tourist seasons special events
    2025-11-17 15:33:06 - research_agent - INFO - Searching: popular activities attractions Iceland natural wonders cultural experiences adventure activities
    2025-11-17 15:33:07 - research_agent - INFO - Found 5 results
    2025-11-17 15:33:08 - research_agent - INFO - Found 5 results
    2025-11-17 15:33:14 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [TOOL: task] Completed
    --------------------------------------------------------------------------------


    2025-11-17 15:33:20 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"


    [ORCHESTRATOR] Here's a comprehensive overview of the best time to visit Iceland and popular activities you can enjoy there:
    
    ### Best Time to Visit Iceland
    
    1. **Summer (June-August):**
       - **Weather:** Warmest months with temperatures reaching the low 20°Cs. Enjoy long daylight hours.
       - **Tourist Season:** Peak tourist season due to favorable weather and extended daylight.
       - **Events:** Summer festivals and dry weather inland make it a prime time for travel.
    
    2. **Autumn (September-November):**
       - **Weather:** Cooler temperatures with vibrant autumn colors.
       - **Tourist Season:** Fewer crowds, ideal for budget travel.
       - **Events:** Northern Lights begin to appear.
    
    3. **Winter (November-December):**
       - **Weather:** Cold, with Iceland transforming into a winter wonderland.
       - **Tourist Season:** Popular for festive season activities.
       - **Events:** Christmas and New Year celebrations.
    
    4. **Spring (May):**
       - **Weather:** Nature comes back to life, and temperatures start to rise.
       - **Tourist Season:** Considered off-season, offering a quieter experience.
       - **Events:** Puffin watching and blooming landscapes.
    
    ### Popular Activities and Attractions in Iceland
    
    1. **Natural Wonders:**
       - **Waterfalls:** Visit iconic sites like Skógafoss and Seljalandsfoss.
       - **Northern Lights:** Best viewed in autumn and winter.
       - **Glaciers:** Explore Vatnajökull Glacier for hiking opportunities.
    
    2. **Cultural Experiences:**
       - **Festivals:** Enjoy summer festivals and Christmas celebrations.
       - **Architecture:** Don't miss Hallgrimskirkja in Reykjavik.
    
    3. **Adventure Activities:**
       - **Whale Watching:** Popular in Dalvik.
       - **Snorkeling:** Experience the clear waters at Silfra.
       - **Ice Caving and Snowmobiling:** Available in various locations.
       - **Hiking:** Explore remote destinations and black sand beaches like Reynisfjara.
    
    4. **Relaxation:**
       - **Blue Lagoon:** A famous geothermal spa for relaxation.
    
    These insights should help you plan a trip to Iceland that aligns with your interests and preferences. Enjoy your adventure!
    --------------------------------------------------------------------------------
    
    ================================================================================
    ORCHESTRATION COMPLETED
    ================================================================================


## Part 7: Understanding Sub-Agent Architecture Benefits

Let's examine what we've built and why it's powerful.

### Architecture Analysis

**What We Built:**

```
Orchestrator Agent
├── System Prompt: Coordination and delegation
├── Tools: task (for spawning sub-agents), planning, file I/O
└── Sub-agents:
    ├── Research Agent
    │   ├── System Prompt: Web research expertise
    │   └── Tools: internet_search, file I/O, planning
    └── Weather Agent
        ├── System Prompt: Weather data expertise
        └── Tools: get_current_weather, get_weather_forecast, file I/O
```

**Key Architectural Patterns:**

1. **Cognitive Specialization**
   - Each agent has a focused domain
   - Specialized system prompts
   - Minimal tool sets per agent

2. **Clear Responsibility Boundaries**
   - Orchestrator: Planning and coordination
   - Research Agent: Web search and synthesis
   - Weather Agent: Weather data retrieval

3. **Artifact-Based Communication**
   - Shared filesystem for results
   - Lightweight references passed between agents
   - No heavy data in messages

4. **Parallel Execution Capability**
   - Orchestrator can spawn multiple sub-agents
   - Independent tasks run simultaneously
   - Results collected and synthesized

**Benefits Over Monolithic Design:**

| Aspect | Monolithic Agent | Sub-Agent Architecture |
|--------|------------------|------------------------|
| Context Window | Filled with all tools | Only relevant tools per agent |
| System Prompt | Conflicting instructions | Focused expertise |
| Tool Selection | Confused with 20+ tools | Clear with 1-3 tools |
| Debugging | Hard to trace | Clear agent boundaries |
| Testing | Test everything together | Test each agent separately |
| Maintenance | Update affects everything | Update individual agents |
| Parallelization | Sequential execution | Parallel sub-agents |

**Production Readiness:**

This architecture includes:
- Structured logging for observability
- Error handling at each layer
- Input validation (Pydantic models)
- Retry logic with exponential backoff
- Connection pooling for performance
- Shared filesystem for state management

## Part 8: Design Patterns for Sub-Agent Boundaries

When designing your own multi-agent systems, use these patterns:

### Pattern 1: Functional Specialization
Divide by **task type**:
- Research Agent: Information gathering
- Analysis Agent: Data processing
- Writing Agent: Report generation

### Pattern 2: Domain Specialization
Divide by **knowledge domain**:
- Financial Agent: Stock data, analysis
- Medical Agent: Health information
- Legal Agent: Regulatory compliance

### Pattern 3: Process Stage Specialization
Divide by **pipeline stage**:
- Ingestion Agent: Data collection
- Cleaning Agent: Data validation
- Analysis Agent: Processing
- Output Agent: Report generation

### Pattern 4: Capability-Based Specialization
Divide by **technical capability**:
- Web Scraper Agent: HTTP requests
- Database Agent: SQL queries
- File Agent: File operations
- API Agent: External API calls

### Good Boundary Indicators

✅ **Good boundaries:**
- Distinct toolsets with minimal overlap
- Natural handoff points between agents
- Clear expertise separation
- Agents can be tested independently
- Reduces prompt complexity

❌ **Poor boundaries:**
- Many overlapping tools
- Frequent back-and-forth communication
- Tight coupling between agents
- Unclear ownership of tasks
- Shared context dependencies

## Part 9: Exercises and Extensions

Try these exercises to deepen your understanding:

### Exercise 1: Add a New Sub-Agent
Create a **Translation Agent** that:
- Uses a translation API or LLM
- Translates research findings into different languages
- Integrates with the orchestrator

### Exercise 2: Implement Error Recovery
Enhance the orchestrator to:
- Detect when a sub-agent fails
- Retry with modified parameters
- Fall back to alternative sub-agents
- Log failure patterns

### Exercise 3: Add Caching
Implement semantic caching:
- Cache research results for similar queries
- Cache weather data with TTL (time-to-live)
- Reduce API calls and improve response time

### Exercise 4: Metrics and Monitoring
Add observability:
- Track execution time per sub-agent
- Monitor tool call frequency
- Measure parallel vs sequential execution gains
- Log orchestration decisions

### Exercise 5: Build a Different System
Apply the patterns to a new domain:
- E-commerce: Product Agent + Inventory Agent + Recommendation Agent
- Healthcare: Symptom Agent + Research Agent + Appointment Agent
- Finance: Market Agent + Portfolio Agent + News Agent

## Summary

Congratulations! You've built a production-grade multi-agent system using the orchestrator pattern.

### What You Learned

1. **The Problem**: Monolithic agents with too many tools get confused and inefficient

2. **The Solution**: Sub-agent architectures with:
   - Cognitive specialization (focused expertise)
   - Clear responsibility boundaries
   - Parallel execution capability
   - Maintainable, testable components

3. **The Orchestrator Pattern**:
   - Coordinator agent handles planning and delegation
   - Worker agents execute specialized tasks
   - Artifact-based communication via shared filesystem
   - Results synthesized into cohesive responses

4. **Production-Grade Implementation**:
   - Input validation with Pydantic
   - Retry logic with exponential backoff
   - Structured logging for observability
   - Error handling at every layer
   - Connection pooling for performance

5. **Design Patterns**:
   - Functional specialization (by task type)
   - Domain specialization (by knowledge area)
   - Process stage specialization (by pipeline stage)
   - Capability-based specialization (by technical ability)

### Key Takeaways

- **Divide and conquer**: Break complex systems into specialized components
- **Clear boundaries**: Each agent should have focused expertise and minimal tools
- **Parallel execution**: Orchestrator pattern enables concurrent sub-agent work
- **Production patterns**: Validation, retry logic, logging, and error handling are essential
- **Real-world usage**: This pattern powers Claude Code, LangGraph, and enterprise systems

### Next Steps

- Apply these patterns to your own domain
- Experiment with different sub-agent configurations
- Add monitoring and metrics to track performance
- Consider implementing caching and optimization strategies
- Explore advanced coordination patterns (hierarchical orchestrators, bidding systems)

You now have the knowledge to build sophisticated, scalable multi-agent systems!
```

---

