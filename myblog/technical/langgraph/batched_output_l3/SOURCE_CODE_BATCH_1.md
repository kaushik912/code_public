# Source Code Batch

This file contains 5 source files.

---

## File: 3_10_conversation_threading.md

```markdown
# Tutorial: Conversation Threading and Memory Persistence in LangGraph

## Learning Objectives

By the end of this tutorial, you will be able to:
- Understand what conversation threading means and why it's important
- Use checkpointers to persist conversation state across invocations
- Implement thread_id to maintain separate conversation histories
- Build a chatbot with memory using SQLite persistence
- Manage multiple user conversations with proper isolation

## Prerequisites

- Basic understanding of LangGraph workflows
- Python programming fundamentals
- Familiarity with LangChain message types
- OpenAI API key

## What is Conversation Threading?

**Conversation threading** enables a chatbot to remember previous interactions within a conversation. Without threading, each message to the bot starts fresh with no memory of what was said before.

### Why Threading Matters:

**Without Threading:**
```
User: My name is Sarah
Bot: Nice to meet you, Sarah!

User: What's my name?
Bot: I don't know your name.
```

**With Threading:**
```
User: My name is Sarah
Bot: Nice to meet you, Sarah!

User: What's my name?
Bot: Your name is Sarah!
```

### Key Concepts:

| Concept | Description |
|---------|-------------|
| **Checkpointer** | A component that saves and loads conversation state |
| **thread_id** | A unique identifier for a conversation thread |
| **State Persistence** | Saving conversation history between invocations |
| **Thread Isolation** | Keeping different conversations separate |

### Use Cases:
- **Customer support bots** that remember context throughout a support session
- **Personal assistants** that maintain conversation history
- **Multi-user applications** where each user has their own conversation thread
- **Long-running conversations** that span multiple sessions

## Setup

Let's start by importing the necessary libraries and loading environment variables.


```python
# Install required packages if needed
# !pip install langgraph langchain-openai python-dotenv
```


```python
import os
import sqlite3
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

# Load environment variables
load_dotenv()

# Verify OpenAI API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

print("Environment loaded successfully!")
print("All required libraries imported!")
```

    Environment loaded successfully!
    All required libraries imported!


## Understanding Checkpointers and Persistence

A **checkpointer** is responsible for:
1. Saving the state after each step in the graph
2. Loading the state when you invoke the graph again
3. Managing multiple conversation threads

### SQLite for Learning and Production

In this tutorial, we'll use **SqliteSaver** which stores conversation state in a SQLite database file.

**Why SQLite?**
- **Persistent storage**: Conversations survive program restarts
- **No setup required**: File-based database with zero configuration
- **Perfect for learning**: Simple to understand and use
- **Production-ready**: Suitable for many real-world applications

### Production Database Options

While we use SQLite in this tutorial for simplicity, LangGraph supports several database backends for production scenarios:

| Database | Use Case | LangGraph Class |
|----------|----------|-----------------|
| **SQLite** | Single-server apps, development, learning | `SqliteSaver` |
| **PostgreSQL** | High-traffic production apps, distributed systems | `PostgresSaver` |
| **MongoDB** | Document-based storage, flexible schemas | `MongoDBSaver` |
| **Redis** | Ultra-fast access, caching, real-time apps | `RedisSaver` |

**For this tutorial, we'll focus on SQLite**, but the concepts and patterns you learn here apply to all checkpoint implementations.

## Building a Basic Chatbot (Without Memory)

Let's first build a simple chatbot without any persistence to see the problem we're solving.

### Step 1: Define the State

Our state will contain a list of messages. We use the special `add_messages` reducer to append new messages to the list rather than replacing them.


```python
class ChatState(TypedDict):
    """
    State structure for our chatbot.
    
    The Annotated type with add_messages tells LangGraph to append new messages
    to the messages list rather than replacing the entire list.
    """
    messages: Annotated[list[BaseMessage], add_messages]

print("State defined successfully!")
```

    State defined successfully!


### Step 2: Create the Chatbot Node

This node will call the LLM with the current messages and return the response.


```python
def chatbot_node(state: ChatState) -> ChatState:
    """
    The main chatbot node that processes messages using OpenAI.
    """
    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # Get the response from the LLM
    response = llm.invoke(state["messages"])
    
    # Return the updated state with the new message
    # The add_messages reducer will append this to the existing messages
    return {"messages": [response]}

print("Chatbot node created successfully!")
```

    Chatbot node created successfully!


### Step 3: Build the Graph (Without Checkpointer)

Notice we compile the graph WITHOUT a checkpointer. This means it has no memory.


```python
# Create the workflow
workflow_no_memory = StateGraph(ChatState)

# Add the chatbot node
workflow_no_memory.add_node("chatbot", chatbot_node)

# Add edges
workflow_no_memory.add_edge(START, "chatbot")
workflow_no_memory.add_edge("chatbot", END)

# Compile WITHOUT a checkpointer - no memory!
app_no_memory = workflow_no_memory.compile()

print("Chatbot without memory compiled successfully!")
```

    Chatbot without memory compiled successfully!


### Step 4: Test Without Memory

Let's see what happens when we try to have a conversation without memory.


```python
print("=" * 60)
print("DEMONSTRATION: Chatbot WITHOUT Memory")
print("=" * 60)

# First message
print("\nUser: My name is Alice")
result1 = app_no_memory.invoke({
    "messages": [HumanMessage(content="My name is Alice")]
})
print(f"Bot: {result1['messages'][-1].content}")

# Second message - trying to reference the first
print("\nUser: What's my name?")
result2 = app_no_memory.invoke({
    "messages": [HumanMessage(content="What's my name?")]
})
print(f"Bot: {result2['messages'][-1].content}")

print("\n" + "=" * 60)
print("Notice: The bot doesn't remember the previous conversation!")
print("=" * 60)
```

    ============================================================
    DEMONSTRATION: Chatbot WITHOUT Memory
    ============================================================
    
    User: My name is Alice
    Bot: Nice to meet you, Alice! How can I assist you today?
    
    User: What's my name?
    Bot: I'm sorry, but I don't have access to personal information about you unless you've shared it with me in this conversation. How can I assist you today?
    
    ============================================================
    Notice: The bot doesn't remember the previous conversation!
    ============================================================


## Adding Memory with SqliteSaver

Now let's add persistent memory to our chatbot using the `SqliteSaver` checkpointer. This will allow the bot to remember conversations even after restarting the program.

### Understanding thread_id

The `thread_id` is a unique identifier for a conversation thread. Think of it as a "conversation ID":

- **Same thread_id** = Same conversation (bot remembers previous messages)
- **Different thread_id** = Different conversation (fresh start)

The thread_id is passed in the config parameter:
```python
config = {"configurable": {"thread_id": "user_123"}}
```

### Setting Up SQLite Persistence

To add persistence, we need to:
1. Create a SqliteSaver checkpointer with a database file path
2. Compile the graph with the checkpointer
3. Pass the thread_id in the config when invoking the graph


```python
# Create the same workflow structure
workflow_with_memory = StateGraph(ChatState)
workflow_with_memory.add_node("chatbot", chatbot_node)
workflow_with_memory.add_edge(START, "chatbot")
workflow_with_memory.add_edge("chatbot", END)

# The KEY difference: compile WITH a checkpointer
# SqliteSaver stores conversation state in a database file
# For Jupyter notebooks, we create the connection directly

# Create database connection
conn = sqlite3.connect("chatbot_memory.db", check_same_thread=False)
sqlite_checkpointer = SqliteSaver(conn)

# Compile with the checkpointer
app_with_memory = workflow_with_memory.compile(checkpointer=sqlite_checkpointer)

print("Chatbot with SQLite persistence compiled successfully!")
print("Database file: chatbot_memory.db")
```

    Chatbot with SQLite persistence compiled successfully!
    Database file: chatbot_memory.db


### Testing with Memory

Now let's test the same conversation with memory enabled. Notice how we:
1. Use the same `thread_id` for related messages
2. Only send the NEW message each time (not the entire history)
3. The checkpointer automatically loads and saves the full conversation history


```python
print("=" * 60)
print("DEMONSTRATION: Chatbot WITH SQLite Persistence")
print("=" * 60)

# Define our thread configuration
config = {"configurable": {"thread_id": "conversation_1"}}

# First message
print("\nUser: My name is Alice")
result1 = app_with_memory.invoke(
    {"messages": [HumanMessage(content="My name is Alice")]},
    config=config  # Pass the thread_id config
)
print(f"Bot: {result1['messages'][-1].content}")

# Second message - using the SAME thread_id
print("\nUser: What's my name?")
result2 = app_with_memory.invoke(
    {"messages": [HumanMessage(content="What's my name?")]},
    config=config  # Same thread_id = same conversation
)
print(f"Bot: {result2['messages'][-1].content}")

# Third message - continuing the conversation
print("\nUser: What was the first thing I told you?")
result3 = app_with_memory.invoke(
    {"messages": [HumanMessage(content="What was the first thing I told you?")]},
    config=config
)
print(f"Bot: {result3['messages'][-1].content}")

print("\n" + "=" * 60)
print("Success! The bot remembers the entire conversation!")
print("This is now stored persistently in chatbot_memory.db")
print("=" * 60)
```

    ============================================================
    DEMONSTRATION: Chatbot WITH SQLite Persistence
    ============================================================
    
    User: My name is Alice
    Bot: Hello again, Alice! How can I assist you today?
    
    User: What's my name?
    Bot: Your name is Alice.
    
    User: What was the first thing I told you?
    Bot: The first thing you told me was, "My name is Alice."
    
    ============================================================
    Success! The bot remembers the entire conversation!
    This is now stored persistently in chatbot_memory.db
    ============================================================


### Viewing the Conversation History

We can retrieve the full conversation history from the checkpointer using the `get_state()` method.


```python
print("=" * 60)
print("Full Conversation History for thread_id='conversation_1'")
print("=" * 60)

# Get the current state for our thread
state = app_with_memory.get_state(config)

# Display all messages
for i, message in enumerate(state.values["messages"], 1):
    role = "User" if isinstance(message, HumanMessage) else "Bot"
    print(f"\n{i}. {role}: {message.content}")
```

    ============================================================
    Full Conversation History for thread_id='conversation_1'
    ============================================================
    
    1. User: My name is Alice
    
    2. Bot: Nice to meet you, Alice! How can I assist you today?
    
    3. User: What's my name?
    
    4. Bot: Your name is Alice. How can I help you today?
    
    5. User: What was the first thing I told you?
    
    6. Bot: The first thing you told me was, "My name is Alice."
    
    7. User: My name is Alice
    
    8. Bot: Hello again, Alice! How can I assist you today?
    
    9. User: What's my name?
    
    10. Bot: Your name is Alice.
    
    11. User: What was the first thing I told you?
    
    12. Bot: The first thing you told me was, "My name is Alice."


## Example : Single User Persistent Conversation

Let's demonstrate a realistic scenario where a user has a conversation, then comes back later (simulated by using the same thread_id in a new invocation).


```python
print("=" * 70)
print("EXAMPLE 1: Single User - Conversation Continuity")
print("=" * 70)

# User's thread
user_config = {"configurable": {"thread_id": "user_alice_thread"}}

print("\n--- Session 1: Initial Conversation ---")
print("\nUser: I'm planning a trip to Paris next month.")
result = app_with_memory.invoke(
    {"messages": [HumanMessage(content="I'm planning a trip to Paris next month.")]},
    config=user_config
)
print(f"Bot: {result['messages'][-1].content}")

print("\nUser: What are the must-see attractions?")
result = app_with_memory.invoke(
    {"messages": [HumanMessage(content="What are the must-see attractions?")]},
    config=user_config
)
print(f"Bot: {result['messages'][-1].content}")

print("\n--- User logs off, comes back later ---")
print("--- Session 2: Continuing the Conversation ---")
print("\nUser: Thanks for those suggestions! How about restaurants?")
result = app_with_memory.invoke(
    {"messages": [HumanMessage(content="Thanks for those suggestions! How about restaurants?")]},
    config=user_config  # Same thread_id = continues the conversation
)
print(f"Bot: {result['messages'][-1].content}")

print("\nUser: Which one is closest to the Eiffel Tower?")
result = app_with_memory.invoke(
    {"messages": [HumanMessage(content="Which one is closest to the Eiffel Tower?")]},
    config=user_config
)
print(f"Bot: {result['messages'][-1].content}")

print("\n" + "=" * 70)
print("Key Takeaway: Same thread_id maintains conversation context")
print("across multiple sessions!")
print("=" * 70)
```

    ======================================================================
    EXAMPLE 1: Single User - Conversation Continuity
    ======================================================================
    
    --- Session 1: Initial Conversation ---
    
    User: I'm planning a trip to Paris next month.
    Bot: That sounds wonderful! Paris is a fantastic destination with so much to explore. If you have any specific questions or need help with planning your itinerary, feel free to ask! Whether you need recommendations on attractions, restaurants, accommodations, or tips for getting around, I'm here to help. What are you most excited to do in Paris?
    
    User: What are the must-see attractions?
    Bot: When visiting Paris, there are several iconic attractions that you won't want to miss. Here’s a list of must-see spots:
    
    1. **Eiffel Tower**: The symbol of Paris, you can take an elevator ride to the top for spectacular views of the city. Visiting at night when it’s illuminated is particularly magical.
    
    2. **Louvre Museum**: One of the world’s largest and most famous art museums, home to masterpieces like the Mona Lisa and the Venus de Milo. Allocate a few hours to explore its vast collection.
    
    3. **Notre-Dame Cathedral**: Although it is currently under restoration due to the 2019 fire, the exterior remains stunning. The area around Notre-Dame is also worth exploring.
    
    4. **Sacré-Cœur Basilica**: Located in Montmartre, this basilica offers breathtaking views of the city from its dome. The surrounding neighborhood is charming, with artists and cafés.
    
    5. **Champs-Élysées and Arc de Triomphe**: Stroll down this famous avenue, lined with shops and cafés, and visit the Arc de Triomphe for a panoramic view of Paris.
    
    6. **Palace of Versailles**: A short trip from Paris, this opulent palace and its gardens are a must-see for anyone interested in French history and royalty.
    
    7. **Musée d'Orsay**: Housed in a former train station, this museum is known for its collection of Impressionist and Post-Impressionist masterpieces, including works by Monet, Van Gogh, and Degas.
    
    8. **Seine River Cruise**: A cruise on the Seine, especially at sunset or in the evening, offers beautiful views of many iconic landmarks along the river.
    
    9. **Latin Quarter**: This historic area is known for its narrow streets, lively atmosphere, and rich literary history. It's a great place to wander, shop, and enjoy a meal.
    
    10. **Sainte-Chapelle**: Famous for its stunning stained glass windows, this Gothic chapel is located near Notre-Dame and is a hidden gem worth visiting.
    
    11. **Montmartre**: Explore this bohemian neighborhood where artists like Picasso and Van Gogh lived. It’s filled with quaint streets, cafés, and the beautiful Place du Tertre.
    
    12. **The Pompidou Center**: Known for its modern architecture and contemporary art collections, it's an interesting contrast to the historical sites in the city.
    
    Be sure to check the opening hours and book tickets in advance for popular attractions to save time. Enjoy your trip to Paris!
    
    --- User logs off, comes back later ---
    --- Session 2: Continuing the Conversation ---
    
    User: Thanks for those suggestions! How about restaurants?
    Bot: Paris is a culinary delight with a wide range of dining options, from traditional French bistros to modern eateries. Here are some recommendations across different styles and budgets:
    
    ### Classic French Bistros:
    1. **Le Comptoir de la Gastronomie**: A classic bistro known for its traditional French dishes, including duck confit and a variety of charcuterie.
    2. **Chez Janou**: Located in the Marais, this charming spot serves Provençal cuisine and offers a lovely courtyard. Their chocolate mousse is a must-try!
    
    ### Michelin-Starred Restaurants:
    3. **Le Meurice**: A luxurious dining experience with a menu inspired by French cuisine. The elegant setting and exceptional service make it a special occasion spot.
    4. **L'Arpège**: Famous for its vegetable-focused dishes, this three-Michelin-star restaurant emphasizes fresh, seasonal ingredients.
    
    ### Casual Dining:
    5. **L’As du Fallafel**: Renowned for its delicious falafel sandwiches, this casual eatery in the Marais is a favorite for a quick and tasty meal.
    6. **Le Relais de l’Entrecôte**: Known for its steak-frites and secret sauce, this restaurant serves a simple yet satisfying menu.
    
    ### Bakeries and Cafés:
    7. **Du Pain et des Idées**: An artisanal bakery famous for its pain au chocolat and other pastries. Perfect for breakfast or a snack.
    8. **Café de Flore**: One of Paris's oldest cafés, it’s a great spot for people-watching while enjoying a coffee or a light meal.
    
    ### Modern and Trendy Spots:
    9. **Frenchie**: Located in the 2nd arrondissement, this trendy restaurant offers a modern twist on French cuisine. Reservations are highly recommended!
    10. **Le Mary Celeste**: A hip bar and restaurant in the Marais known for its creative cocktails and small plates, perfect for sharing.
    
    ### Dessert:
    11. **Pierre Hermé**: Famous for his macarons, a visit to one of his shops is a must for anyone with a sweet tooth.
    12. **Angelina**: Known for its rich hot chocolate and pastries, this historic tearoom offers a delightful break during your sightseeing.
    
    ### Tips:
    - **Reservations**: For popular restaurants, especially those with Michelin stars, making a reservation is highly recommended.
    - **Explore Local Neighborhoods**: Some of the best meals can be found in smaller, less touristy spots, so don’t hesitate to wander and discover hidden gems.
    - **Enjoy the Experience**: Dining in Paris is often a leisurely affair, so take your time and savor the experience.
    
    Enjoy your culinary adventures in Paris!
    
    User: Which one is closest to the Eiffel Tower?
    Bot: If you're looking for restaurants close to the Eiffel Tower, here are a few excellent options:
    
    1. **Le Café de l'Homme**: Located in the Trocadéro area, this restaurant offers stunning views of the Eiffel Tower. It's a great place to enjoy French cuisine in a stylish setting.
    
    2. **Les Ombres**: Situated on the rooftop of the Musée du quai Branly, this restaurant provides beautiful views of the Eiffel Tower, especially at sunset. The menu features modern French cuisine.
    
    3. **58 Tour Eiffel**: Located on the first floor of the Eiffel Tower, this restaurant offers a unique dining experience with incredible views. Reservations are highly recommended, as it can be quite popular.
    
    4. **Le Relais de l'Entrecôte**: While not directly next to the Eiffel Tower, it’s located in the 6th arrondissement and is a short distance away. This casual eatery is famous for its steak-frites.
    
    5. **Bistro Parisien**: Located right by the Seine River, this bistro offers a lovely view of the Eiffel Tower and serves a variety of French dishes in a relaxed atmosphere.
    
    These options allow you to enjoy a meal while taking in the beauty of the Eiffel Tower! Make sure to check for reservations, especially for those with great views!
    
    ======================================================================
    Key Takeaway: Same thread_id maintains conversation context
    across multiple sessions!
    ======================================================================

```

---

## File: 3_11_semantic_memory.md

```markdown
# Semantic Memory with LangMem

## Introduction

Semantic memory enables agents to remember and retrieve information by meaning across multiple conversation sessions. Unlike simple chat history which stores all messages sequentially, semantic memory uses vector embeddings to find and retrieve the most relevant memories based on the current context.

**Why is semantic memory useful?**
- **Personalization**: Remember user preferences, interests, and past interactions
- **Context persistence**: Recall relevant information from previous sessions
- **Efficient retrieval**: Use similarity search to find the most relevant memories instead of loading entire conversation history
- **Scalability**: Handle long-term interactions without overwhelming the context window

**What you'll learn:**
- How to set up a semantic memory store with embeddings
- How to create memory management tools that the agent can use
- How to build an agent that actively saves and retrieves memories
- How to inspect stored memories

**Prerequisites**: An OpenAI API key stored in a `.env` file

## Step 1: Environment Setup

Load environment variables to access your API key.


```python
from dotenv import load_dotenv

load_dotenv()
```




    True



## Step 2: Import Required Libraries

We'll need:
- **LangGraph**: For agent creation with `create_react_agent`
- **LangChain**: For model interaction
- **LangMem**: For memory management tools
- **InMemoryStore**: A simple in-memory vector store for this demo


```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.store.memory import InMemoryStore
```

## Step 3: Set Up the Memory Store with Embeddings

The `InMemoryStore` will store our memories with vector embeddings enabled. This allows semantic search - finding memories based on meaning similarity rather than exact keyword matches.

**Key configuration:**
- `index`: Enables semantic search with the specified embedding model
- We use OpenAI's `text-embedding-3-small` model for efficient, high-quality embeddings


```python
# Create the memory store with semantic search capabilities
memory_store = InMemoryStore(
    index={
        "embed": OpenAIEmbeddings(model="text-embedding-3-small")
    }
)

print("Memory store initialized with semantic search enabled!")
```

    Memory store initialized with semantic search enabled!


## Step 4: Create Memory Management Tools

LangMem provides two essential tools that our agent can use:

1. **manage_memory_tool**: Allows the agent to save new memories
2. **search_memory_tool**: Allows the agent to search for relevant memories

These tools give the agent control over its own memory system - this is called the "hot path" approach where the agent actively decides what to remember.

**Key configuration:**
- We use a namespace `("memories",)` to organize where memories are stored
- The namespace helps isolate different types of memories


```python
# Create the memory management tool - allows agent to save memories
manage_memory_tool = create_manage_memory_tool(namespace=("memories",))

# Create the memory search tool - allows agent to search for memories
search_memory_tool = create_search_memory_tool(namespace=("memories",))

print("Memory tools created:")
print(f"- {manage_memory_tool.name}: {manage_memory_tool.description}")
print(f"- {search_memory_tool.name}: {search_memory_tool.description}")
```

    Memory tools created:
    - manage_memory: Create, update, or delete a memory to persist across conversations.
    Include the MEMORY ID when updating or deleting a MEMORY. Omit when creating a new MEMORY - it will be created for you.
    Proactively call this tool when you:
    
    1. Identify a new USER preference.
    2. Receive an explicit USER request to remember something or otherwise alter your behavior.
    3. Are working and want to record important context.
    4. Identify that an existing MEMORY is incorrect or outdated.
    - search_memory: Search your long-term memories for information relevant to your current context.


## Step 5: Create a Simple Weather Tool

Let's add a basic tool so our agent can demonstrate memory usage in context. The agent might remember user location preferences.


```python
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
        "new york": "Sunny, 72°F with light breeze",
        "london": "Cloudy, 59°F with occasional drizzle",
        "tokyo": "Clear, 68°F and pleasant",
        "san francisco": "Foggy, 63°F typical for this time of year",
        "paris": "Partly cloudy, 65°F and comfortable",
    }
    
    location_key = location.lower().strip()
    
    if location_key in weather_data:
        return f"Weather in {location}: {weather_data[location_key]}"
    else:
        return f"Weather data not available for {location}"
```

## Step 6: Configure the Language Model



```python
model = ChatOpenAI(
    model="gpt-5",
    temperature=0.1
)
```

## Step 7: Create the Agent with Memory Tools

Now we create the agent with all our tools: the weather tool and the two memory tools. The agent will have access to:
- `get_weather`: Check weather for locations
- `manage_memory`: Save important information to memory
- `search_memory`: Retrieve relevant memories

The agent can now actively decide when to save memories and when to search for them!


```python
# Combine all tools
tools = [get_weather, manage_memory_tool, search_memory_tool]

# Create the agent with LangGraph's create_react_agent
# Pass the store so the memory tools can access it
agent = create_react_agent(
    model=model,
    tools=tools,
    store=memory_store
)

print("Agent created successfully with memory capabilities!")
print(f"Available tools: {[tool.name for tool in tools]}")
```

    Agent created successfully with memory capabilities!
    Available tools: ['get_weather', 'manage_memory', 'search_memory']


    /var/folders/_1/tfp0k5355jxb501q_ckbc6m80000gn/T/ipykernel_87136/7600960.py:6: LangGraphDeprecatedSinceV10: create_react_agent has been moved to `langchain.agents`. Please update your import to `from langchain.agents import create_agent`. Deprecated in LangGraph V1.0 to be removed in V2.0.
      agent = create_react_agent(


## Step 8: Create a Helper Function for Interactions

This helper function will make it easy to interact with the agent. The agent will automatically handle memory storage and retrieval.


```python
def chat_with_agent(message: str, user_id: str = "user_123"):
    """Chat with the agent and see its response.
    
    Args:
        message: The user's message
        user_id: Identifier to namespace this user's memories (optional)
    """
    print(f"\n{'='*60}")
    print(f"USER: {message}")
    print(f"{'='*60}")
    
    # Invoke the agent with the message
    result = agent.invoke({
        "messages": [{"role": "user", "content": message}]
    })
    
    # Extract the final response
    final_message = result["messages"][-1]
    print(f"\nAGENT: {final_message.content}\n")
    
    return result
```

## Step 9: Example Interactions - Building Memory

Let's have a conversation where the agent learns about our preferences. The agent should use the `manage_memory` tool to save important information.


```python
# First interaction - tell the agent our preferences
chat_with_agent(
    "Hi! My name is Sarah and I live in San Francisco. I love checking the weather in the morning for SF so if I ask for the weather without mentioning a city, return the weather for SF."
)
```

    
    ============================================================
    USER: Hi! My name is Sarah and I live in San Francisco. I love checking the weather in the morning for SF so if I ask for the weather without mentioning a city, return the weather for SF.
    ============================================================
    
    AGENT: Got it, Sarah! I’ll use San Francisco as your default location for weather requests. If you ever want to change it, just let me know.
    





    {'messages': [HumanMessage(content='Hi! My name is Sarah and I live in San Francisco. I love checking the weather in the morning for SF so if I ask for the weather without mentioning a city, return the weather for SF.', additional_kwargs={}, response_metadata={}, id='3575ed48-3b98-46df-b409-7ceb0769b076'),
      AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 1039, 'prompt_tokens': 407, 'total_tokens': 1446, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 960, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-CadtxMtJsxdT0C1VN5D4iYT35t4HD', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--fb4bbc8d-6500-4a3b-b252-5ef87fe534d1-0', tool_calls=[{'name': 'manage_memory', 'args': {'action': 'create', 'content': 'User prefers default weather location to be San Francisco when not specified.'}, 'id': 'call_HcUBVkSbveD7KizCQ8y3yusj', 'type': 'tool_call'}, {'name': 'manage_memory', 'args': {'action': 'create', 'content': "User's preferred name is Sarah."}, 'id': 'call_qaCRMXXWrZh73h0d4dwE5SWA', 'type': 'tool_call'}], usage_metadata={'input_tokens': 407, 'output_tokens': 1039, 'total_tokens': 1446, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 960}}),
      ToolMessage(content='created memory 6ea3f543-cd95-41f7-aae1-c1f154e9f220', name='manage_memory', id='ecba121d-5792-49b4-a957-dd4417bdf965', tool_call_id='call_HcUBVkSbveD7KizCQ8y3yusj'),
      ToolMessage(content='created memory 185f3485-8c15-4551-9b79-b6f9ed0972a7', name='manage_memory', id='27c796a7-3eaf-4e40-a146-f93786763117', tool_call_id='call_qaCRMXXWrZh73h0d4dwE5SWA'),
      AIMessage(content='Got it, Sarah! I’ll use San Francisco as your default location for weather requests. If you ever want to change it, just let me know.', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 34, 'prompt_tokens': 550, 'total_tokens': 584, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-CaduKYLKls7frOg5QIcH49r0qQGRO', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--bf9052da-35e9-4d46-afb5-7aaa77bc93b4-0', usage_metadata={'input_tokens': 550, 'output_tokens': 34, 'total_tokens': 584, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})]}




```python
# Tell the agent about preferences
chat_with_agent(
    "By the way, I prefer temperature in Celsis, not Fahrenheit."
)
```

    
    ============================================================
    USER: By the way, I prefer temperature in Celsis, not Fahrenheit.
    ============================================================
    
    AGENT: Got it—I'll use Celsius for temperatures going forward.
    





    {'messages': [HumanMessage(content='By the way, I prefer temperature in Celsis, not Fahrenheit.', additional_kwargs={}, response_metadata={}, id='5e66c371-e829-495e-970a-35c0ccb8d998'),
      AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 224, 'prompt_tokens': 381, 'total_tokens': 605, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 192, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-CaduMPqKAwEPr5NHDkQTcAKLOuizg', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--990d7c30-4028-45d6-a370-4a0791f2204a-0', tool_calls=[{'name': 'manage_memory', 'args': {'action': 'create', 'content': 'User prefers temperature in Celsius.'}, 'id': 'call_Z3rWobjaTiAWxT00SSqYFnJs', 'type': 'tool_call'}], usage_metadata={'input_tokens': 381, 'output_tokens': 224, 'total_tokens': 605, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 192}}),
      ToolMessage(content='created memory 8383c6e6-0873-4aff-8711-06b6d10191e9', name='manage_memory', id='1df679dd-bdeb-47d7-9e1d-f0e6c9269a5f', tool_call_id='call_Z3rWobjaTiAWxT00SSqYFnJs'),
      AIMessage(content="Got it—I'll use Celsius for temperatures going forward.", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 14, 'prompt_tokens': 445, 'total_tokens': 459, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-CaduRyHpl5MxNEnGUZOccCNhFwSdb', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--ef451611-ad91-4296-8920-8c63a9144446-0', usage_metadata={'input_tokens': 445, 'output_tokens': 14, 'total_tokens': 459, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})]}



## Step 10: Testing Memory Retrieval

Now let's start a "new session" where the agent doesn't have the conversation history. It should use the `search_memory` tool to recall what it learned about us.


```python
# Ask about something specific that should be remembered
chat_with_agent(
    "What's my name and where do I live?"
)
```

    
    ============================================================
    USER: What's my name and where do I live?
    ============================================================
    
    AGENT: Your name is Sarah. I don’t know where you live. I do have San Francisco as your default weather location—do you live there, or would you like me to remember a different city?
    





    {'messages': [HumanMessage(content="What's my name and where do I live?", additional_kwargs={}, response_metadata={}, id='51a6e65b-3161-4163-9b38-56f55f7527ff'),
      AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 103, 'prompt_tokens': 375, 'total_tokens': 478, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 64, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-CaduSm60Hx8f36QWV7oziK6pz0iPt', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--07b00b3f-8ca5-4e85-a9d6-6973991f31a0-0', tool_calls=[{'name': 'search_memory', 'args': {'query': 'user name OR my name OR called name OR I am', 'limit': 10}, 'id': 'call_ws6Yu4rPP0PTHWUS8P4qahYL', 'type': 'tool_call'}], usage_metadata={'input_tokens': 375, 'output_tokens': 103, 'total_tokens': 478, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 64}}),
      ToolMessage(content='[{"namespace":["memories"],"key":"185f3485-8c15-4551-9b79-b6f9ed0972a7","value":{"content":"User\'s preferred name is Sarah."},"created_at":"2025-11-11T08:20:35.308980+00:00","updated_at":"2025-11-11T08:20:35.308982+00:00","score":0.40283246798597305},{"namespace":["memories"],"key":"6ea3f543-cd95-41f7-aae1-c1f154e9f220","value":{"content":"User prefers default weather location to be San Francisco when not specified."},"created_at":"2025-11-11T08:20:35.308771+00:00","updated_at":"2025-11-11T08:20:35.308775+00:00","score":0.20766277515472673},{"namespace":["memories"],"key":"8383c6e6-0873-4aff-8711-06b6d10191e9","value":{"content":"User prefers temperature in Celsius."},"created_at":"2025-11-11T08:20:41.597545+00:00","updated_at":"2025-11-11T08:20:41.597558+00:00","score":0.20220983866321657}]', name='search_memory', id='dd7004d1-22c5-451f-885b-3122f791e504', tool_call_id='call_ws6Yu4rPP0PTHWUS8P4qahYL'),
      AIMessage(content='Your name is Sarah. I don’t know where you live. I do have San Francisco as your default weather location—do you live there, or would you like me to remember a different city?', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 369, 'prompt_tokens': 729, 'total_tokens': 1098, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 320, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-CadubnvMyDYxrIPsrssexobOJuYET', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--e2008b9d-255a-4bc9-9937-7c161f79ffa1-0', usage_metadata={'input_tokens': 729, 'output_tokens': 369, 'total_tokens': 1098, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 320}})]}




```python
chat_with_agent(
    "Hey, can you check the weather for me in the city where I live?"
)
```

    
    ============================================================
    USER: Hey, can you check the weather for me in the city where I live?
    ============================================================
    
    AGENT: Here’s the weather in your default city, San Francisco: Foggy, around 17°C (63°F), typical for this time of year.
    
    If you meant a different city, tell me which one and I’ll check it.
    





    {'messages': [HumanMessage(content='Hey, can you check the weather for me in the city where I live?', additional_kwargs={}, response_metadata={}, id='a0313f1f-30fe-43d3-93a4-59b5d0ce8d23'),
      AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 100, 'prompt_tokens': 382, 'total_tokens': 482, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 64, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-Cadujh2W8vcVDj8wZMzLWoQF4W3q3', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--c5feac09-9198-4582-955e-0b0263fa9b75-0', tool_calls=[{'name': 'search_memory', 'args': {'query': 'user home city OR location OR lives in', 'limit': 5}, 'id': 'call_SEO5gS1RtxFpXq6FTISjuS7i', 'type': 'tool_call'}], usage_metadata={'input_tokens': 382, 'output_tokens': 100, 'total_tokens': 482, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 64}}),
      ToolMessage(content='[{"namespace":["memories"],"key":"6ea3f543-cd95-41f7-aae1-c1f154e9f220","value":{"content":"User prefers default weather location to be San Francisco when not specified."},"created_at":"2025-11-11T08:20:35.308771+00:00","updated_at":"2025-11-11T08:20:35.308775+00:00","score":0.44269580673763054},{"namespace":["memories"],"key":"185f3485-8c15-4551-9b79-b6f9ed0972a7","value":{"content":"User\'s preferred name is Sarah."},"created_at":"2025-11-11T08:20:35.308980+00:00","updated_at":"2025-11-11T08:20:35.308982+00:00","score":0.27294081225113337},{"namespace":["memories"],"key":"8383c6e6-0873-4aff-8711-06b6d10191e9","value":{"content":"User prefers temperature in Celsius."},"created_at":"2025-11-11T08:20:41.597545+00:00","updated_at":"2025-11-11T08:20:41.597558+00:00","score":0.23902420730407603}]', name='search_memory', id='43035020-eebd-494c-ac46-47e4e28460b1', tool_call_id='call_SEO5gS1RtxFpXq6FTISjuS7i'),
      AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 280, 'prompt_tokens': 733, 'total_tokens': 1013, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 256, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-CaduwkwcvJ1346FOCLqcUEi9noEzO', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--a0f3f256-e3bf-43cf-9a56-3792154adaba-0', tool_calls=[{'name': 'get_weather', 'args': {'location': 'San Francisco'}, 'id': 'call_YlX1axwHxc6Z0Xc7Ejdog1yA', 'type': 'tool_call'}], usage_metadata={'input_tokens': 733, 'output_tokens': 280, 'total_tokens': 1013, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 256}}),
      ToolMessage(content='Weather in San Francisco: Foggy, 63°F typical for this time of year', name='get_weather', id='363941c0-bf96-415d-9870-bf04b0bd32ec', tool_call_id='call_YlX1axwHxc6Z0Xc7Ejdog1yA'),
      AIMessage(content='Here’s the weather in your default city, San Francisco: Foggy, around 17°C (63°F), typical for this time of year.\n\nIf you meant a different city, tell me which one and I’ll check it.', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 504, 'prompt_tokens': 779, 'total_tokens': 1283, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 448, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-Cadv2NDAEUcuc9jjoBK8qz4a9XdFQ', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--c91d9b24-4b25-4a6f-9659-c0de99a7e20a-0', usage_metadata={'input_tokens': 779, 'output_tokens': 504, 'total_tokens': 1283, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 448}})]}



## Step 11: Testing Semantic Search

Let's directly test the semantic search capability by searching for memories using similarity.


```python
def search_memories_by_query(query: str, limit: int = 3):
    """Search for memories using semantic similarity."""
    namespace = ("memories",)
    
    print(f"\nSearching for: '{query}'")
    print(f"{'='*60}\n")
    
    try:
        # Perform semantic search
        results = memory_store.search(namespace, query=query, limit=limit)
        
        if not results:
            print("No relevant memories found.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Content: {result.value.get('content', 'N/A')}")
            if hasattr(result, 'score'):
                print(f"  Similarity Score: {result.score:.4f}")
            print()
    except Exception as e:
        print(f"Search error: {e}")

# Test semantic search
search_memories_by_query("Where does the user live?")
search_memories_by_query("temperature preferences")
```

    
    Searching for: 'Where does the user live?'
    ============================================================
    
    Result 1:
      Content: User prefers default weather location to be San Francisco when not specified.
      Similarity Score: 0.4492
    
    Result 2:
      Content: User's preferred name is Sarah.
      Similarity Score: 0.3864
    
    Result 3:
      Content: User prefers temperature in Celsius.
      Similarity Score: 0.3443
    
    
    Searching for: 'temperature preferences'
    ============================================================
    
    Result 1:
      Content: User prefers temperature in Celsius.
      Similarity Score: 0.5130
    
    Result 2:
      Content: User prefers default weather location to be San Francisco when not specified.
      Similarity Score: 0.3685
    
    Result 3:
      Content: User's preferred name is Sarah.
      Similarity Score: 0.2751
    

```

---

## File: 3_1_conditional_edges_tutorial.md

```markdown
# Tutorial: Conditional Edges in LangGraph

## Learning Objectives

By the end of this tutorial, you will be able to:
- Understand what conditional edges are and how they differ from normal edges
- Create routing functions that evaluate state to determine the next node
- Implement conditional edges to build dynamic, adaptive workflows
- Apply conditional routing patterns to real-world agent scenarios

## Prerequisites

- Basic understanding of LangGraph workflows
- Python programming fundamentals
- Familiarity with state graphs and nodes

## What are Conditional Edges?

**Conditional edges** enable dynamic routing in LangGraph workflows by choosing the next node based on runtime conditions. Unlike normal edges that always route to the same destination, conditional edges evaluate the current state and make decisions about where to go next.

### Key Differences:

| Normal Edge | Conditional Edge |
|-------------|------------------|
| Always goes to the same next node | Chooses next node based on logic |
| Static workflow path | Dynamic workflow path |
| Simple linear flow | Branching flow with decision points |

### Use Cases:
- **Tool selection** based on query type (math vs. search vs. calculation)
- **Quality checks** that determine if revision is needed
- **Error handling** with retry logic
- **Different processing paths** for different data types

## Setup

Let's start by importing the necessary libraries and loading environment variables.


```python
# Install required packages if needed
# !pip install langgraph python-dotenv
```


```python
import os
from dotenv import load_dotenv
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# Load environment variables
load_dotenv()

print("Environment loaded successfully!")
```

    Environment loaded successfully!


## Anatomy of a Conditional Edge

A conditional edge consists of three core components:

1. **Source Node**: The node where the edge originates
2. **Routing Function**: A function that evaluates the state and returns the name of the next node
3. **Path Map** (optional): A dictionary that maps routing function return values to node names

### Basic Structure:

```python
workflow.add_conditional_edges(
    "source_node",          # Source node name
    routing_function,       # Function that determines next node
    {                       # Path map (optional)
        "option_a": "node_a",
        "option_b": "node_b"
    }
)
```

### Execution Flow:
1. Source node executes and updates state
2. Routing function evaluates the current state
3. Function returns a value indicating the next node
4. Graph routes to the determined node

## Example: Simple Query Routing System

Let's build a simple workflow that demonstrates conditional edges. Our system will:
1. Accept user input
2. Classify the input type
3. Route to different processing nodes based on the classification

### Scenario:
We'll create a query router that:
- Routes **math questions** to a math processor
- Routes **general questions** to a general processor
- Routes **greeting messages** to a greeting processor

### Step 1: Define the State

First, we define our state structure. The state will hold the user input and any processing results.


```python
class QueryState(TypedDict):
    """State structure for our query routing workflow."""
    user_input: str          # The original user query
    query_type: str          # Classified type: 'math', 'general', or 'greeting'
    result: str              # Final processing result

print("State defined successfully!")
```

    State defined successfully!


### Step 2: Create Node Functions

Now we'll create the node functions. Each node performs a specific task and updates the state.


```python
def classifier_node(state: QueryState) -> QueryState:
    """
    Classifies the user input into one of three categories.
    This is our first node that analyzes the input.
    """
    user_input = state["user_input"].lower()
    
    # Simple classification logic
    if any(word in user_input for word in ["hello", "hi", "hey", "greetings"]):
        query_type = "greeting"
    elif any(char in user_input for char in "0123456789+-*/") or any(
        word in user_input for word in ["calculate", "sum", "multiply", "divide"]
    ):
        query_type = "math"
    else:
        query_type = "general"
    
    print(f"Classifier: Input classified as '{query_type}'")
    
    return {
        "user_input": state["user_input"],
        "query_type": query_type,
        "result": state.get("result", "")
    }


def math_processor_node(state: QueryState) -> QueryState:
    """
    Processes math-related queries.
    """
    print("Math Processor: Processing mathematical query...")
    result = f"Math processing result for: '{state['user_input']}' - This would involve mathematical computation."
    
    return {
        "user_input": state["user_input"],
        "query_type": state["query_type"],
        "result": result
    }


def general_processor_node(state: QueryState) -> QueryState:
    """
    Processes general queries.
    """
    print("General Processor: Processing general query...")
    result = f"General processing result for: '{state['user_input']}' - This would involve general knowledge retrieval."
    
    return {
        "user_input": state["user_input"],
        "query_type": state["query_type"],
        "result": result
    }


def greeting_processor_node(state: QueryState) -> QueryState:
    """
    Processes greeting messages.
    """
    print("Greeting Processor: Processing greeting...")
    result = f"Hello! Thank you for your greeting: '{state['user_input']}'. How can I help you today?"
    
    return {
        "user_input": state["user_input"],
        "query_type": state["query_type"],
        "result": result
    }

print("Node functions created successfully!")
```

    Node functions created successfully!


### Step 3: Create the Routing Function

The **routing function** is the heart of conditional edges. It examines the state and returns a string that will be mapped to the next node.

**Key Requirements:**
- Must accept state as a parameter
- Must return a string that can be mapped to a node name via the path map
- Should contain clear, simple logic

**Why use path maps?** Path maps separate routing logic from node naming, making your code more maintainable and easier to understand.


```python
def route_query(state: QueryState) -> Literal["math", "general", "greeting"]:
    """
    Routing function that determines which processor to use based on query_type.
    
    This function evaluates the state and returns a category string.
    The path map will translate this to the actual node name.
    """
    query_type = state["query_type"]
    
    print(f"Router: Routing to '{query_type}' category")
    
    # Return simple category names that will be mapped to actual nodes
    if query_type == "math":
        return "math"
    elif query_type == "greeting":
        return "greeting"
    else:
        return "general"

print("Routing function created successfully!")
```

    Routing function created successfully!


### Step 4: Build the Workflow

Now we'll construct the complete workflow by:
1. Creating a StateGraph
2. Adding all nodes
3. Adding edges (normal and conditional)
4. Compiling the graph


```python
# Create the workflow
workflow = StateGraph(QueryState)

# Add all nodes to the workflow
workflow.add_node("classifier", classifier_node)
workflow.add_node("math_processor", math_processor_node)
workflow.add_node("general_processor", general_processor_node)
workflow.add_node("greeting_processor", greeting_processor_node)

# Add normal edge from START to classifier
# This edge always goes to the classifier node
workflow.add_edge(START, "classifier")

# Add CONDITIONAL EDGE from classifier to processors
# This is where the magic happens!
# The route_query function determines the category,
# and the path map translates it to the actual node name
workflow.add_conditional_edges(
    "classifier",      # Source node
    route_query,       # Routing function
    {                  # Path map: routing output → node name
        "math": "math_processor",
        "general": "general_processor",
        "greeting": "greeting_processor"
    }
)

# Add normal edges from all processors to END
workflow.add_edge("math_processor", END)
workflow.add_edge("general_processor", END)
workflow.add_edge("greeting_processor", END)

# Compile the workflow
app = workflow.compile()

print("Workflow built and compiled successfully!")
```

    Workflow built and compiled successfully!


## Demonstration: Testing the Conditional Routing

Let's test our workflow with different types of inputs to see how conditional edges route to different nodes.

### Test Case 1: Math Query

This should route to the math processor.


```python
print("=" * 60)
print("TEST CASE 1: Math Query")
print("=" * 60)

initial_state = {
    "user_input": "What is 25 + 37?",
    "query_type": "",
    "result": ""
}

result = app.invoke(initial_state)

print("\nFinal State:")
print(f"Input: {result['user_input']}")
print(f"Type: {result['query_type']}")
print(f"Result: {result['result']}")
```

    ============================================================
    TEST CASE 1: Math Query
    ============================================================
    Classifier: Input classified as 'math'
    Router: Routing to 'math' category
    Math Processor: Processing mathematical query...
    
    Final State:
    Input: What is 25 + 37?
    Type: math
    Result: Math processing result for: 'What is 25 + 37?' - This would involve mathematical computation.


### Test Case 2: General Query

This should route to the general processor.


```python
print("=" * 60)
print("TEST CASE 2: General Query")
print("=" * 60)

initial_state = {
    "user_input": "What is the capital of France?",
    "query_type": "",
    "result": ""
}

result = app.invoke(initial_state)

print("\nFinal State:")
print(f"Input: {result['user_input']}")
print(f"Type: {result['query_type']}")
print(f"Result: {result['result']}")
```

    ============================================================
    TEST CASE 2: General Query
    ============================================================
    Classifier: Input classified as 'general'
    Router: Routing to 'general' category
    General Processor: Processing general query...
    
    Final State:
    Input: What is the capital of France?
    Type: general
    Result: General processing result for: 'What is the capital of France?' - This would involve general knowledge retrieval.


### Test Case 3: Greeting

This should route to the greeting processor.


```python
print("=" * 60)
print("TEST CASE 3: Greeting")
print("=" * 60)

initial_state = {
    "user_input": "Hello there!",
    "query_type": "",
    "result": ""
}

result = app.invoke(initial_state)

print("\nFinal State:")
print(f"Input: {result['user_input']}")
print(f"Type: {result['query_type']}")
print(f"Result: {result['result']}")
```

    ============================================================
    TEST CASE 3: Greeting
    ============================================================
    Classifier: Input classified as 'greeting'
    Router: Routing to 'greeting' category
    Greeting Processor: Processing greeting...
    
    Final State:
    Input: Hello there!
    Type: greeting
    Result: Hello! Thank you for your greeting: 'Hello there!'. How can I help you today?

```

---

## File: 3_2_custom_agentic_workflows_tutorial.md

```markdown
# Building Custom Agentic Workflows with LangGraph: Routing Pattern

## Tutorial Overview

In this tutorial, you'll learn how to build a custom agentic workflow using **LangGraph** with intelligent routing capabilities. We'll create a system that:

- Analyzes user queries to detect intent
- Routes to appropriate processing paths based on the intent
- Executes either a web search (using Tavily) or direct LLM response
- Returns contextually appropriate results

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Design and implement branching workflow patterns using LangGraph
2. Create conditional edges for intelligent routing
3. Implement intent detection for query classification
4. Integrate external tools (Tavily web search) into your workflow
5. Build modular, testable agentic systems

## Prerequisites

- Basic Python knowledge
- Understanding of LLMs and API calls
- API keys for:
  - OpenAI (or another LLM provider)
  - Tavily (for web search)

## What You'll Build

We'll build a **Smart Query Router** that:
- Receives a user question
- Detects if the question requires current/real-time information (web search) or can be answered directly
- Routes to the appropriate node
- Returns an augmented response

**Workflow Architecture:**

```
START → Intent Detection → [Conditional Edge] → Web Search Path OR Direct LLM Path → END
```

## Part 1: Environment Setup

First, let's install the required packages and load our environment variables.


```python
# Install required packages
# Uncomment the following line if you need to install the packages
# !pip install langgraph langchain langchain-openai langchain-tavily python-dotenv
```


```python
# Load environment variables
from dotenv import load_dotenv
import os

# Load API keys from .env file
load_dotenv()

# Verify that keys are loaded (don't print the actual keys!)
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not found in environment"
assert os.getenv("TAVILY_API_KEY"), "TAVILY_API_KEY not found in environment"

print("Environment variables loaded successfully!")
```

    Environment variables loaded successfully!


## Part 2: Import Dependencies

Let's import all the libraries we'll need for building our workflow.


```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
import json

print("All imports successful!")
```

    All imports successful!


## Part 3: Define the State

In LangGraph, **state** is the data structure that flows through your workflow. Each node reads from and writes to this state.

For our routing workflow, we need to track:
- The user's query
- The detected intent
- Search results (if web search is used)
- The final response


```python
class AgentState(TypedDict):
    """State schema for our agentic workflow."""
    
    # User's original query
    query: str
    
    # Detected intent: 'search' or 'direct'
    intent: str
    
    # Search results from Tavily (if applicable)
    search_results: str
    
    # Final response to return to user
    response: str

print("State schema defined!")
print("\nState fields:")
for field, field_type in AgentState.__annotations__.items():
    print(f"  - {field}: {field_type}")
```

    State schema defined!
    
    State fields:
      - query: <class 'str'>
      - intent: <class 'str'>
      - search_results: <class 'str'>
      - response: <class 'str'>


## Part 4: Initialize LLM and Tools

Let's set up our LLM (OpenAI), create a structured output model for intent detection, and initialize the Tavily search tool using the LangChain integration.


```python
# Define Pydantic model for intent detection
class IntentClassification(BaseModel):
    """Schema for intent classification results."""
    
    intent: Literal["search", "direct"] = Field(
        description="The detected intent: 'search' for queries requiring current/real-time information, 'direct' for general knowledge questions"
    )
    reasoning: str = Field(
        description="Brief explanation of why this intent was chosen"
    )

# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create structured output model for intent classification
intent_classifier = llm.with_structured_output(IntentClassification)

# Initialize Tavily search tool (using LangChain integration)
tavily_search = TavilySearch(max_results=3, topic="general")

print("LLM, intent classifier, and Tavily search tool initialized!")
print("\nIntent Classification Schema:")
print(f"  - intent: Literal['search', 'direct']")
print(f"  - reasoning: str")
```

    LLM, intent classifier, and Tavily search tool initialized!
    
    Intent Classification Schema:
      - intent: Literal['search', 'direct']
      - reasoning: str


## Part 5: Build the Nodes

Nodes are the processing units in your workflow. Each node is a function that:
1. Receives the current state
2. Performs some processing
3. Returns updates to the state

We'll create three nodes:
1. **Intent Detection Node**: Analyzes the query to determine if web search is needed
2. **Web Search Node**: Performs web search and augments response with current information
3. **Direct Response Node**: Generates response directly from LLM knowledge

### Node 1: Intent Detection

This node analyzes the user's query and classifies it as either:
- **search**: Requires current/real-time information (weather, news, stock prices, etc.)
- **direct**: Can be answered from LLM's training knowledge (definitions, general facts, coding help, etc.)

We use **structured output with Pydantic** to ensure reliable, type-safe intent classification.


```python
def intent_detection_node(state: AgentState) -> AgentState:
    """
    Analyzes the user query and determines the appropriate processing path using structured output.
    
    Returns:
        Updated state with 'intent' field set to either 'search' or 'direct'
    """
    query = state["query"]
    
    # Create a prompt for intent classification
    system_prompt = """You are an intent classifier for a query routing system.

Analyze the user's query and determine if it requires:
- SEARCH: Current/real-time information (news, weather, stock prices, recent events, current facts)
- DIRECT: General knowledge, definitions, explanations, coding help, historical facts

Provide your classification with reasoning.

Examples:
- "What's the weather in Paris today?" -> search (requires current data)
- "Explain how neural networks work" -> direct (general knowledge)
- "Latest news about AI" -> search (requires current information)
- "How do I write a for loop in Python?" -> direct (coding help from training)
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {query}"}
    ]
    
    # Use structured output to get intent classification
    result = intent_classifier.invoke(messages)
    
    print(f"Intent detected: {result.intent}")
    print(f"Reasoning: {result.reasoning}")
    
    return {**state, "intent": result.intent}

print("Intent detection node created with structured output!")
```

    Intent detection node created with structured output!


### Node 2: Web Search Path

This node:
1. Uses Tavily (via LangChain integration) to search the web for current information
2. Extracts relevant results
3. Uses the LLM to generate a response augmented with search results


```python
def web_search_node(state: AgentState) -> AgentState:
    """
    Performs web search using Tavily (LangChain integration) and generates an augmented response.
    
    Returns:
        Updated state with 'search_results' and 'response' fields populated
    """
    query = state["query"]
    
    print(f"Performing web search for: {query}")
    
    # Perform the web search using LangChain Tavily tool
    # The tool returns a dictionary with 'results', 'answer', 'query', etc.
    search_response = tavily_search.invoke({"query": query})
    
    # Extract the results list from the response
    search_results = search_response.get("results", [])
    
    print(f"Found {len(search_results)} search results")
    
    # Format search results for the LLM
    formatted_results = "\n\n".join([
        f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nContent: {r.get('content', '')}"
        for r in search_results
    ])
    
    # Generate response using search results
    system_prompt = """You are a helpful assistant that answers questions using web search results.
    
Use the provided search results to give an accurate, informative answer.
Always cite your sources by mentioning the titles and URLs.
If the search results don't contain relevant information, say so.
"""
    
    user_prompt = f"""Question: {query}

Search Results:
{formatted_results}

Please provide a clear, concise answer based on these search results."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    
    return {
        **state,
        "search_results": formatted_results,
        "response": response.content
    }

print("Web search node created!")
```

    Web search node created!


### Node 3: Direct Response Path

This node generates a response directly from the LLM's training knowledge, without web search.


```python
def direct_response_node(state: AgentState) -> AgentState:
    """
    Generates a direct response using the LLM's knowledge.
    
    Returns:
        Updated state with 'response' field populated
    """
    query = state["query"]
    
    print(f"Generating direct response for: {query}")
    
    system_prompt = """You are a helpful assistant that provides clear, accurate answers.
    
Answer questions using your knowledge and training.
Be concise but thorough.
If you're not certain about something, acknowledge the uncertainty.
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    
    response = llm.invoke(messages)
    
    return {**state, "response": response.content}

print("Direct response node created!")
```

    Direct response node created!


## Part 6: Create the Router Function

The router function is used with **conditional edges** in LangGraph. It examines the state and returns the name of the next node to execute.

This is the key to branching workflows!


```python
def route_by_intent(state: AgentState) -> Literal["web_search", "direct_response"]:
    """
    Routes to the appropriate processing node based on detected intent.
    
    Args:
        state: Current agent state containing the 'intent' field
    
    Returns:
        Name of the next node to execute: 'web_search' or 'direct_response'
    """
    intent = state["intent"]
    
    if intent == "search":
        print("Routing to: web_search node")
        return "web_search"
    else:
        print("Routing to: direct_response node")
        return "direct_response"

print("Router function created!")
```

    Router function created!


## Part 7: Build the Graph

Now we'll assemble everything into a LangGraph workflow:

1. Create a `StateGraph` with our state schema
2. Add all nodes
3. Connect nodes with edges:
   - Regular edges for fixed transitions
   - Conditional edges for dynamic routing
4. Compile the graph into an executable app


```python
# Create the state graph
workflow = StateGraph(AgentState)

# Add nodes to the graph
workflow.add_node("intent_detection", intent_detection_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("direct_response", direct_response_node)

# Add edges
# 1. Start with intent detection
workflow.add_edge(START, "intent_detection")

# 2. Use conditional edge to route based on intent
workflow.add_conditional_edges(
    "intent_detection",  # Source node
    route_by_intent,     # Router function
    {
        "web_search": "web_search",           # If router returns 'web_search'
        "direct_response": "direct_response"  # If router returns 'direct_response'
    }
)

# 3. Both paths end after execution
workflow.add_edge("web_search", END)
workflow.add_edge("direct_response", END)

# Compile the graph into an executable app
app = workflow.compile()

print("Graph compiled successfully!")
print("\nWorkflow structure:")
print("  START → intent_detection → [conditional routing]")
print("                              ├─→ web_search → END")
print("                              └─→ direct_response → END")
```

    Graph compiled successfully!
    
    Workflow structure:
      START → intent_detection → [conditional routing]
                                  ├─→ web_search → END
                                  └─→ direct_response → END


## Part 8: Visualize the Graph (Optional)

LangGraph provides built-in visualization capabilities. Let's visualize our workflow!


```python
# Try to visualize the graph
try:
    from IPython.display import Image, display
    
    # Generate and display the graph visualization
    display(Image(app.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Visualization not available: {e}")
    print("\nGraph structure (text representation):")
    print(app.get_graph().to_json())
```


    
![png](3_2_custom_agentic_workflows_tutorial_files/3_2_custom_agentic_workflows_tutorial_22_0.png)
    


## Part 9: Test the Workflow

Let's test our workflow with different types of queries to see the routing in action!

### Test 1: Query Requiring Web Search

This query asks about current information, so it should route to the web search node.


```python
# Test with a query that requires web search
test_query_1 = "What are the latest developments in AI safety research?"

print(f"Testing Query 1: {test_query_1}")
print("=" * 80)

# Create initial state
initial_state = {
    "query": test_query_1,
    "intent": "",
    "search_results": "",
    "response": ""
}

# Run the workflow
result = app.invoke(initial_state)

# Display results
print("\n" + "=" * 80)
print("FINAL RESULT")
print("=" * 80)
print(f"\nIntent: {result['intent']}")
print(f"\nResponse:\n{result['response']}")
```

    Testing Query 1: What are the latest developments in AI safety research?
    ================================================================================
    Intent detected: search
    Reasoning: The query asks for the latest developments, which implies a need for current and real-time information about AI safety research.
    Routing to: web_search node
    Performing web search for: What are the latest developments in AI safety research?
    Found 3 search results
    
    ================================================================================
    FINAL RESULT
    ================================================================================
    
    Intent: search
    
    Response:
    Recent developments in AI safety research indicate a significant increase in activity and focus in this field. Notably, AI safety research has grown by 312% from 2018 to 2023, reflecting a substantial uptick in interest and investment compared to previous years. This growth suggests a heightened awareness of the potential risks associated with AI technologies and the need for effective safety measures.
    
    For ongoing updates and analysis, resources like the AI Safety Newsletter provide insights into the latest research, policy changes, and industry news related to AI safety. Additionally, the International AI Safety Report offers comprehensive updates on major breakthroughs in AI capabilities and their implications for safety, with the latest report published in January 2025.
    
    For more detailed information, you can explore the following sources:
    - "Still a drop in the bucket: new data on global AI safety research" [Eto Tech](https://eto.tech/blog/still-drop-bucket-ai-safety-research/)
    - "The AI Safety Newsletter" [AI Safety](https://safe.ai/newsletter)
    - "International AI Safety Report" [International AI Safety Report](https://internationalaisafetyreport.org/)


### Test 2: Query for Direct Response

This query asks about general knowledge, so it should route to the direct response node.


```python
# Test with a query that can be answered directly
test_query_2 = "Explain the difference between supervised and unsupervised learning"

print(f"Testing Query 2: {test_query_2}")
print("=" * 80)

# Create initial state
initial_state = {
    "query": test_query_2,
    "intent": "",
    "search_results": "",
    "response": ""
}

# Run the workflow
result = app.invoke(initial_state)

# Display results
print("\n" + "=" * 80)
print("FINAL RESULT")
print("=" * 80)
print(f"\nIntent: {result['intent']}")
print(f"\nResponse:\n{result['response']}")
```

    Testing Query 2: Explain the difference between supervised and unsupervised learning
    ================================================================================
    Intent detected: direct
    Reasoning: The query asks for a general explanation of concepts in machine learning, which falls under general knowledge.
    Routing to: direct_response node
    Generating direct response for: Explain the difference between supervised and unsupervised learning
    
    ================================================================================
    FINAL RESULT
    ================================================================================
    
    Intent: direct
    
    Response:
    Supervised and unsupervised learning are two main types of machine learning techniques, each with distinct characteristics and applications.
    
    ### Supervised Learning:
    - **Definition**: In supervised learning, the model is trained on a labeled dataset, which means that each training example is paired with an output label or target value.
    - **Goal**: The goal is to learn a mapping from inputs to outputs so that the model can predict the output for new, unseen data.
    - **Examples**: Common tasks include classification (e.g., spam detection, image recognition) and regression (e.g., predicting house prices).
    - **Data Requirement**: Requires a large amount of labeled data for training.
    
    ### Unsupervised Learning:
    - **Definition**: In unsupervised learning, the model is trained on data without labeled responses. The algorithm tries to learn the underlying structure or distribution of the data.
    - **Goal**: The goal is to identify patterns, groupings, or features in the data without prior knowledge of the outcomes.
    - **Examples**: Common tasks include clustering (e.g., customer segmentation, grouping similar items) and dimensionality reduction (e.g., PCA).
    - **Data Requirement**: Does not require labeled data, making it useful for exploring data and finding hidden patterns.
    
    ### Summary:
    - **Supervised Learning**: Uses labeled data to predict outcomes.
    - **Unsupervised Learning**: Uses unlabeled data to find patterns or groupings. 
    
    Both methods have their own strengths and are used in different scenarios depending on the availability of labeled data and the specific problem being addressed.

```

---

## File: 3_3_debug_execution_flow.md

```markdown
# Debugging Agentic Workflows in LangGraph

## Tutorial Overview

Debugging agentic workflows presents unique challenges compared to traditional software. With LLM-based agents:
- Behavior emerges from state transformations, not deterministic code paths
- You need to observe what's happening at each step in real-time
- Traditional debugging techniques (breakpoints, print statements) aren't sufficient
- You must validate LLM decisions, routing logic, and tool invocations

In this tutorial, you'll learn professional debugging techniques for LangGraph workflows:

1. **Streaming for observation**: Watch state evolve in real-time as your agent executes
2. **Interrupts for inspection**: Pause execution at critical points to validate behavior
3. **Practical debugging scenarios**: Apply these techniques to real problems

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Use LangGraph's streaming modes (`values`, `updates`, `debug`) to observe execution
2. Trace execution through state history to understand agent behavior
3. Use interrupts to pause and inspect state at critical decision points
4. Debug failed agent runs by identifying where things went wrong
5. Monitor and log agent behavior for analysis

## Prerequisites

- Completion of `3_2_custom_agentic_workflows_tutorial.ipynb`
- Understanding of the Smart Query Router workflow
- API keys for:
  - OpenAI (or another LLM provider)
  - Tavily (for web search)

## What We'll Debug

We'll use the **Smart Query Router** from the previous tutorial as our debugging target. This workflow has several decision points that benefit from debugging:
- Intent detection (is it working correctly?)
- Routing logic (are queries routed to the right node?)
- Tool invocations (is web search returning relevant results?)
- Response generation (is the final answer appropriate?)

## Part 1: Setup - Recreate the Smart Query Router

We'll reuse the Smart Query Router from the previous tutorial. This gives us a working workflow to debug.

The workflow:
1. Detects intent (search vs. direct response)
2. Routes based on intent
3. Either searches the web or generates a direct response
4. Returns the final result


```python
# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not found in environment"
assert os.getenv("TAVILY_API_KEY"), "TAVILY_API_KEY not found in environment"

print("Environment variables loaded successfully!")
```

    Environment variables loaded successfully!



```python
# Import dependencies
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
import json

print("All imports successful!")
```

    All imports successful!



```python
# Define state schema
class AgentState(TypedDict):
    """State schema for our agentic workflow."""
    query: str
    intent: str
    search_results: str
    response: str

print("State schema defined!")
```

    State schema defined!



```python
# Initialize LLM and tools
class IntentClassification(BaseModel):
    """Schema for intent classification results."""
    intent: Literal["search", "direct"] = Field(
        description="The detected intent: 'search' for queries requiring current/real-time information, 'direct' for general knowledge questions"
    )
    reasoning: str = Field(
        description="Brief explanation of why this intent was chosen"
    )

llm = ChatOpenAI(model="gpt-4o", temperature=0)
intent_classifier = llm.with_structured_output(IntentClassification)
tavily_search = TavilySearch(max_results=3, topic="general")

print("LLM and tools initialized!")
```

    LLM and tools initialized!



```python
# Node 1: Intent Detection
def intent_detection_node(state: AgentState) -> AgentState:
    """Analyzes the user query and determines the appropriate processing path."""
    query = state["query"]
    
    system_prompt = """You are an intent classifier for a query routing system.

Analyze the user's query and determine if it requires:
- SEARCH: Current/real-time information (news, weather, stock prices, recent events, current facts)
- DIRECT: General knowledge, definitions, explanations, coding help, historical facts

Provide your classification with reasoning.

Examples:
- "What's the weather in Paris today?" -> search (requires current data)
- "Explain how neural networks work" -> direct (general knowledge)
- "Latest news about AI" -> search (requires current information)
- "How do I write a for loop in Python?" -> direct (coding help from training)
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {query}"}
    ]
    
    result = intent_classifier.invoke(messages)
    
    print(f"Intent detected: {result.intent}")
    print(f"Reasoning: {result.reasoning}")
    
    # Return ONLY the field we're updating (not the entire state)
    # This makes "updates" stream mode show only what changed
    return {"intent": result.intent}

print("Intent detection node created!")
```

    Intent detection node created!



```python
# Node 2: Web Search
def web_search_node(state: AgentState) -> AgentState:
    """Performs web search using Tavily and generates an augmented response."""
    query = state["query"]
    
    print(f"Performing web search for: {query}")
    
    search_response = tavily_search.invoke({"query": query})
    search_results = search_response.get("results", [])
    
    print(f"Found {len(search_results)} search results")
    
    formatted_results = "\n\n".join([
        f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nContent: {r.get('content', '')}"
        for r in search_results
    ])
    
    system_prompt = """You are a helpful assistant that answers questions using web search results.
    
Use the provided search results to give an accurate, informative answer.
Always cite your sources by mentioning the titles and URLs.
If the search results don't contain relevant information, say so.
"""
    
    user_prompt = f"""Question: {query}

Search Results:
{formatted_results}

Please provide a clear, concise answer based on these search results."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    
    # Return ONLY the fields we're updating
    return {
        "search_results": formatted_results,
        "response": response.content
    }

print("Web search node created!")
```

    Web search node created!



```python
# Node 3: Direct Response
def direct_response_node(state: AgentState) -> AgentState:
    """Generates a direct response using the LLM's knowledge."""
    query = state["query"]
    
    print(f"Generating direct response for: {query}")
    
    system_prompt = """You are a helpful assistant that provides clear, accurate answers.
    
Answer questions using your knowledge and training.
Be concise but thorough.
If you're not certain about something, acknowledge the uncertainty.
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    
    response = llm.invoke(messages)
    
    # Return ONLY the field we're updating
    return {"response": response.content}

print("Direct response node created!")
```

    Direct response node created!



```python
# Router function
def route_by_intent(state: AgentState) -> Literal["web_search", "direct_response"]:
    """Routes to the appropriate processing node based on detected intent."""
    intent = state["intent"]
    
    if intent == "search":
        print("Routing to: web_search node")
        return "web_search"
    else:
        print("Routing to: direct_response node")
        return "direct_response"

print("Router function created!")
```

    Router function created!



```python
# Build and compile the graph
workflow = StateGraph(AgentState)

workflow.add_node("intent_detection", intent_detection_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("direct_response", direct_response_node)

workflow.add_edge(START, "intent_detection")
workflow.add_conditional_edges(
    "intent_detection",
    route_by_intent,
    {
        "web_search": "web_search",
        "direct_response": "direct_response"
    }
)
workflow.add_edge("web_search", END)
workflow.add_edge("direct_response", END)

app = workflow.compile()

print("Graph compiled successfully!")
print("\nReady for debugging!")
```

    Graph compiled successfully!
    
    Ready for debugging!


## Part 2: Debugging with Streaming - State Inspection

### Why Streaming for Debugging?

Traditional debugging (breakpoints, print statements) works well for deterministic code, but agentic workflows are different:

- **Emergent behavior**: Agent behavior emerges from state transformations and LLM decisions
- **Non-deterministic**: LLM outputs can vary, making reproduction challenging
- **Multiple decision points**: Intent detection, routing, tool calls - each can fail silently
- **State evolution**: You need to see how state changes through the workflow

**Streaming** gives you real-time visibility into what's happening at each step without modifying your code.

### LangGraph Streaming Modes

LangGraph provides three streaming modes, each offering different insights:

1. **`values`**: Complete state snapshot after each node
2. **`updates`**: Only what changed in each node (deltas)
3. **`debug`**: Execution metadata and framework internals

Let's explore each mode to understand when to use them.

### Stream Mode: `values`

The `values` mode returns the complete state after each node executes. This is useful for:
- Understanding overall state evolution
- Seeing accumulated data across nodes
- Verifying that state is building up correctly

Let's stream a query that requires web search and observe the full state at each step.


```python
# Test query that should trigger web search
test_query = "What are the current stock prices for Apple?"

print(f"Query: {test_query}")
print("=" * 80)
print("\nSTREAMING MODE: values (complete state snapshots)")
print("=" * 80)

initial_state = {
    "query": test_query,
    "intent": "",
    "search_results": "",
    "response": ""
}

# Stream with 'values' mode
for i, chunk in enumerate(app.stream(initial_state, stream_mode="values")):
    print(f"\n--- Chunk {i+1} ---")
    print(f"Query: {chunk.get('query', 'N/A')}")
    print(f"Intent: {chunk.get('intent', 'N/A')}")
    print(f"Search Results: {chunk.get('search_results', 'N/A')[:100]}...") if chunk.get('search_results') else print(f"Search Results: N/A")
    print(f"Response: {chunk.get('response', 'N/A')[:150]}...") if chunk.get('response') else print(f"Response: N/A")
    print()
```

    Query: What are the current stock prices for Apple?
    ================================================================================
    
    STREAMING MODE: values (complete state snapshots)
    ================================================================================
    
    --- Chunk 1 ---
    Query: What are the current stock prices for Apple?
    Intent: 
    Search Results: N/A
    Response: N/A
    
    Intent detected: search
    Reasoning: The query asks for the current stock prices of Apple, which requires real-time financial data that can change frequently throughout the trading day.
    Routing to: web_search node
    
    --- Chunk 2 ---
    Query: What are the current stock prices for Apple?
    Intent: search
    Search Results: N/A
    Response: N/A
    
    Performing web search for: What are the current stock prices for Apple?
    Found 3 search results
    
    --- Chunk 3 ---
    Query: What are the current stock prices for Apple?
    Intent: search
    Search Results: Title: Buy or Sell Apple Stock - AAPL Stock Price Quote & News | Robinhood
    URL: https://robinhood.co...
    Response: The current stock price for Apple Inc. (AAPL) is approximately $269.43 according to Seeking Alpha [source](https://seekingalpha.com/symbol/AAPL). Mark...
    


### Observations from `values` Mode

Notice how:
1. **Initial state** appears in the first chunk
2. **After intent detection**: `intent` field is populated
3. **After web search**: Both `search_results` and `response` are populated
4. **Each chunk shows the complete state**, not just what changed

This mode is great for:
- Getting the full picture at each step
- Debugging state accumulation issues
- Understanding the complete flow from start to finish

**Limitation**: Can be verbose for complex states with many fields.

### Stream Mode: `updates`

The `updates` mode returns only what changed in each node (the delta). This is useful for:
- Focusing on individual node outputs
- Reducing noise in complex workflows
- Identifying which nodes are modifying which fields

Let's run the same query with `updates` mode and compare.


```python
print(f"Query: {test_query}")
print("=" * 80)
print("\nSTREAMING MODE: updates (only changes from each node)")
print("=" * 80)

# Stream with 'updates' mode
for i, chunk in enumerate(app.stream(initial_state, stream_mode="updates")):
    print(f"\n--- Update {i+1} ---")
    print(f"Node: {list(chunk.keys())[0] if chunk else 'N/A'}")
    print(f"Updates: {json.dumps(chunk, indent=2, default=str)[:500]}...")
    print()
```

    Query: What are the current stock prices for Apple?
    ================================================================================
    
    STREAMING MODE: updates (only changes from each node)
    ================================================================================
    Intent detected: search
    Reasoning: The query asks for the current stock prices of Apple, which requires real-time financial data.
    Routing to: web_search node
    
    --- Update 1 ---
    Node: intent_detection
    Updates: {
      "intent_detection": {
        "intent": "search"
      }
    }...
    
    Performing web search for: What are the current stock prices for Apple?
    Found 3 search results
    
    --- Update 2 ---
    Node: web_search
    Updates: {
      "web_search": {
        "search_results": "Title: Buy or Sell Apple Stock - AAPL Stock Price Quote & News | Robinhood\nURL: https://robinhood.com/us/en/stocks/AAPL/\nContent: Shares are currently priced at $268.69, which is +0.1% above the low and -2.6% below the high. Apple(AAPL) shares are trading with a volume of 46.21M, against a\n\nTitle: Apple Inc. (AAPL) Stock Price, Quote, News & Analysis\nURL: https://seekingalpha.com/symbol/AAPL\nContent: Apple Inc.'s stock symbol is AAPL and currently...
    


### Comparing `values` vs `updates`

**`values` mode:**
- Shows complete state after each node
- Includes all fields, even unchanged ones
- Best for understanding overall state evolution

**`updates` mode:**
- Shows only what changed in each node
- Highlights node-specific transformations
- Best for identifying which node does what

**Important**: The `updates` mode shows what the node **returns**. For this to be truly useful, nodes should return only the fields they're modifying:

```python
# ✅ Good: Returns only what changed
def intent_detection_node(state):
    # ... classification logic ...
    return {"intent": result.intent}  # Only the modified field

# ❌ Less useful for "updates" mode: Returns entire state
def intent_detection_node(state):
    # ... classification logic ...
    return {**state, "intent": result.intent}  # All fields
```

Our nodes follow the first pattern, which is why `updates` mode shows clean, focused output.

Use `updates` when:
- You want to isolate node behavior
- Your state has many fields and you want to reduce noise
- You're debugging a specific node's output

### Stream Mode: `debug`

The `debug` mode returns execution metadata and framework internals. This includes:
- Which nodes executed
- Routing decisions
- Timing information
- Framework-level events

This is useful for:
- Understanding the execution path
- Debugging routing logic
- Performance analysis
- Identifying framework-level issues


```python
print(f"Query: {test_query}")
print("=" * 80)
print("\nSTREAMING MODE: debug (execution metadata)")
print("=" * 80)

# Stream with 'debug' mode
for i, chunk in enumerate(app.stream(initial_state, stream_mode="debug")):
    print(f"\n--- Debug Event {i+1} ---")
    print(f"Type: {chunk.get('type', 'N/A')}")
    print(f"Timestamp: {chunk.get('timestamp', 'N/A')}")
    
    # Print relevant details based on event type
    if 'payload' in chunk:
        payload = chunk['payload']
        if 'name' in payload:
            print(f"Node: {payload['name']}")
        if 'input' in payload:
            print(f"Input keys: {list(payload['input'].keys()) if isinstance(payload['input'], dict) else 'N/A'}")
        if 'output' in payload:
            print(f"Output keys: {list(payload['output'].keys()) if isinstance(payload['output'], dict) else 'N/A'}")
    print()
```

    Query: What are the current stock prices for Apple?
    ================================================================================
    
    STREAMING MODE: debug (execution metadata)
    ================================================================================
    
    --- Debug Event 1 ---
    Type: task
    Timestamp: 2025-11-12T05:20:49.631886+00:00
    Node: intent_detection
    Input keys: ['query', 'intent', 'search_results', 'response']
    
    Intent detected: search
    Reasoning: The query asks for the current stock prices of Apple, which requires real-time financial data.
    Routing to: web_search node
    
    --- Debug Event 2 ---
    Type: task_result
    Timestamp: 2025-11-12T05:20:51.080943+00:00
    Node: intent_detection
    
    
    --- Debug Event 3 ---
    Type: task
    Timestamp: 2025-11-12T05:20:51.081346+00:00
    Node: web_search
    Input keys: ['query', 'intent', 'search_results', 'response']
    
    Performing web search for: What are the current stock prices for Apple?
    Found 3 search results
    
    --- Debug Event 4 ---
    Type: task_result
    Timestamp: 2025-11-12T05:20:54.287124+00:00
    Node: web_search
    


## Part 3: Debugging with Interrupts - Interactive Inspection

### Why Interrupts for Debugging?

Streaming lets you observe, but sometimes you need to:
- **Pause at critical decision points**
- **Inspect state before it changes**
- **Validate assumptions about agent behavior**
- **Interactively explore different paths**

**Interrupts** give you "debug mode" - the ability to pause execution, inspect state, and then resume.


### Key Concept: Checkpointing

Interrupts require **checkpointing** to save state. We'll use `MemorySaver` for this tutorial:
- Keeps state in memory (good for development)
- Use `SqliteSaver` or `PostgresSaver` for production
- Each execution has a `thread_id` to track state

### Adding an Interrupt for Debugging

Let's modify the `intent_detection_node` to add an interrupt AFTER intent classification. This lets us:
- See what intent was detected
- Validate the reasoning
- Decide whether to continue or investigate further

We'll create a new version of the node with an interrupt.


```python
# Modified intent detection node with interrupt
def intent_detection_node_with_interrupt(state: AgentState) -> AgentState:
    """Analyzes the user query and determines the appropriate processing path.
    
    Includes an interrupt for debugging: pauses after intent detection to allow inspection.
    """
    query = state["query"]
    
    system_prompt = """You are an intent classifier for a query routing system.

Analyze the user's query and determine if it requires:
- SEARCH: Current/real-time information (news, weather, stock prices, recent events, current facts)
- DIRECT: General knowledge, definitions, explanations, coding help, historical facts

Provide your classification with reasoning.

Examples:
- "What's the weather in Paris today?" -> search (requires current data)
- "Explain how neural networks work" -> direct (general knowledge)
- "Latest news about AI" -> search (requires current information)
- "How do I write a for loop in Python?" -> direct (coding help from training)
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {query}"}
    ]
    
    result = intent_classifier.invoke(messages)
    
    print(f"Intent detected: {result.intent}")
    print(f"Reasoning: {result.reasoning}")
    
    # INTERRUPT: Pause here for inspection
    # This allows us to validate the intent detection before routing
    interrupt({
        "message": "Intent detection complete. Review and resume to continue.",
        "detected_intent": result.intent,
        "reasoning": result.reasoning,
        "query": query
    })
    
    # Return ONLY the field we're updating
    return {"intent": result.intent}

print("Intent detection node with interrupt created!")
```

    Intent detection node with interrupt created!


### Recompile Graph with Checkpointer

Now we need to:
1. Create a new graph with the modified node
2. Add a checkpointer (MemorySaver)
3. Compile the graph

The checkpointer will save state at each step, allowing us to pause and resume.


```python
# Create a new workflow with the interrupt-enabled node
workflow_with_interrupt = StateGraph(AgentState)

# Add nodes (using the modified intent detection node)
workflow_with_interrupt.add_node("intent_detection", intent_detection_node_with_interrupt)
workflow_with_interrupt.add_node("web_search", web_search_node)
workflow_with_interrupt.add_node("direct_response", direct_response_node)

# Add edges (same as before)
workflow_with_interrupt.add_edge(START, "intent_detection")
workflow_with_interrupt.add_conditional_edges(
    "intent_detection",
    route_by_intent,
    {
        "web_search": "web_search",
        "direct_response": "direct_response"
    }
)
workflow_with_interrupt.add_edge("web_search", END)
workflow_with_interrupt.add_edge("direct_response", END)

# Compile with checkpointer
# NOTE: Always run this cell after modifying node functions to recompile the graph
checkpointer = MemorySaver()
app_with_interrupt = workflow_with_interrupt.compile(checkpointer=checkpointer)

print("Graph with interrupts compiled successfully!")
print("Checkpointer: MemorySaver (in-memory state persistence)")
print("\nIMPORTANT: Re-run this cell if you modify any node functions above!")
```

    Graph with interrupts compiled successfully!
    Checkpointer: MemorySaver (in-memory state persistence)
    
    IMPORTANT: Re-run this cell if you modify any node functions above!


### Testing the Interrupt: Pause and Inspect

Let's test the interrupt by:
1. Starting execution with a test query
2. Observing when the interrupt triggers
3. Inspecting the state at the pause point
4. Examining the interrupt payload
5. Resuming execution to see the final result

**Important**: We need to provide a `thread_id` in the config to track this execution.


```python
# Test query
test_query_interrupt = "What's the weather like in Tokyo right now?"

print(f"Query: {test_query_interrupt}")
print("=" * 80)
print("\nPhase 1: Initial execution (will hit interrupt)")
print("=" * 80)

# Configuration with thread_id for state tracking
config = {"configurable": {"thread_id": "debug-session-1"}}

# Initial state
initial_state = {
    "query": test_query_interrupt,
    "intent": "",
    "search_results": "",
    "response": ""
}

# Invoke the graph - it will pause at the interrupt
result = app_with_interrupt.invoke(initial_state, config)

print("\n" + "=" * 80)
print("Execution paused at interrupt!")
print("=" * 80)
```

    Query: What's the weather like in Tokyo right now?
    ================================================================================
    
    Phase 1: Initial execution (will hit interrupt)
    ================================================================================
    Intent detected: search
    Reasoning: The query asks for the current weather in Tokyo, which requires real-time information.
    
    ================================================================================
    Execution paused at interrupt!
    ================================================================================


### Inspecting State at the Interrupt

Now that execution is paused, let's inspect:
1. The current state
2. The interrupt payload (what information was passed)
3. What we can learn before deciding to resume


```python
print("INSPECTING STATE AT INTERRUPT")
print("=" * 80)

# Check current state
print("\nCurrent State:")
print(f"  Query: {result['query']}")
print(f"  Intent: {result['intent']}")
print(f"  Search Results: {result['search_results'] or 'Not yet executed'}")
print(f"  Response: {result['response'] or 'Not yet executed'}")

# Check interrupt information
if '__interrupt__' in result:
    print("\nInterrupt Payload:")
    interrupts = result['__interrupt__']
    for interrupt_info in interrupts:
        interrupt_value = interrupt_info.value
        print(f"  Message: {interrupt_value.get('message')}")
        print(f"  Detected Intent: {interrupt_value.get('detected_intent')}")
        print(f"  Reasoning: {interrupt_value.get('reasoning')}")

print("\n" + "=" * 80)
print("Analysis: Intent detection shows 'search' - this is correct for a weather query.")
print("Decision: Resume execution to see the web search results.")
print("=" * 80)
```

    INSPECTING STATE AT INTERRUPT
    ================================================================================
    
    Current State:
      Query: What's the weather like in Tokyo right now?
      Intent: 
      Search Results: Not yet executed
      Response: Not yet executed
    
    Interrupt Payload:
      Message: Intent detection complete. Review and resume to continue.
      Detected Intent: search
      Reasoning: The query asks for the current weather in Tokyo, which requires real-time information.
    
    ================================================================================
    Analysis: Intent detection shows 'search' - this is correct for a weather query.
    Decision: Resume execution to see the web search results.
    ================================================================================


### Resuming Execution

After inspecting the state and validating the intent, we can resume execution using `Command(resume=True)`.

The graph will:
1. Continue from where it paused
2. Route based on the detected intent
3. Execute the appropriate node (web search in this case)
4. Return the final result


```python
print("Phase 2: Resuming execution")
print("=" * 80)

# Resume execution with the same config (same thread_id)
final_result = app_with_interrupt.invoke(Command(resume=True), config)

print("\n" + "=" * 80)
print("FINAL RESULT")
print("=" * 80)
print(f"\nIntent: {final_result['intent']}")
print(f"\nResponse Preview:")
print(final_result['response'][:300] + "..." if len(final_result['response']) > 300 else final_result['response'])
```

    Phase 2: Resuming execution
    ================================================================================
    Intent detected: search
    Reasoning: The query asks for the current weather in Tokyo, which requires real-time information that can change frequently.
    Routing to: web_search node
    Performing web search for: What's the weather like in Tokyo right now?
    Found 3 search results
    
    ================================================================================
    FINAL RESULT
    ================================================================================
    
    Intent: search
    
    Response Preview:
    The current weather in Tokyo is partly cloudy with a temperature of 15.1°C (59.2°F). The wind is blowing from the south-southeast at 8.3 kph (5.1 mph), and the humidity is at 39%. There is no precipitation, and the visibility is 10 km (6 miles) [source](https://www.weatherapi.com/).

```

---

