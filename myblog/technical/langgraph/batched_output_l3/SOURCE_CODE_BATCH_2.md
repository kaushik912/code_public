# Source Code Batch

This file contains 4 source files.

---

## File: 3_4_mcp_tools_with_langchain_agent.md

```markdown
# Tutorial: Using MCP Tools with LangChain Agents

## Learning Objectives

By the end of this tutorial, you will be able to:
- Connect a LangGraph agent to an MCP server
- Use MCP tools within an agent workflow
- Understand the `MultiServerMCPClient` pattern

## Prerequisites

- Understanding of MCP concepts from the slides
- Familiarity with LangGraph agents and tool calling
- Basic async/await knowledge

## Setup


```python
# !pip install langchain-mcp-adapters fastmcp langchain langchain-openai python-dotenv
```


```python
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "Please set OPENAI_API_KEY in your .env file"

print("Environment loaded!")
```

    Environment loaded!


## The MCP Server

This directory contains `knowledge_base_server.py` - a FastMCP server with these tools:

| Tool | Description |
|------|-------------|
| `create_note` | Create a note with title, content, tags |
| `search_notes` | Search notes by keyword |
| `get_note` | Get a note by ID |
| `list_notes` | List all notes |
| `update_note` | Update a note |
| `delete_note` | Delete a note |
| `get_statistics` | Get KB statistics |

## Connecting to the MCP Server

Use `MultiServerMCPClient` to connect to MCP servers. For local servers, use `stdio` transport.


```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# Path to our MCP server
SERVER_PATH = Path(".").resolve() / "knowledge_base_server.py"

# MCP client configuration
mcp_config = {
    "knowledge_base": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(SERVER_PATH)],
    }
}

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

## Running the Agent with MCP Tools

The pattern:
1. Create `MultiServerMCPClient` with server config
2. Get tools with `await client.get_tools()`
3. Pass tools to `create_agent()`


```python
async def run_agent(user_message: str):
    """Run a LangChain agent with MCP tools."""
    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()
    
    print(f"Available tools: {[t.name for t in tools]}\n")
    
    agent = create_agent(model=llm, tools=tools)
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": user_message}]
    })
    
    return result["messages"][-1].content
```

## Test: Creating Notes


```python
response = await run_agent(
    "Create a note titled 'Python Decorators' about how decorators work. "
    "Tag it with 'python' and 'tutorial'."
)
print(response)
```

    Available tools: ['create_note', 'search_notes', 'get_note', 'list_notes', 'update_note', 'delete_note', 'get_statistics']
    
    The note titled **"Python Decorators"** has been created successfully. Here are the details:
    
    ### Python Decorators
    **Content:**
    Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way. A decorator is essentially a function that takes another function as an argument and extends its behavior without explicitly modifying it.
    
    #### How Decorators Work:
    1. **Function as First-Class Objects**: In Python, functions are first-class objects, meaning they can be passed around as arguments, returned from other functions, and assigned to variables.
    
    2. **Defining a Decorator**: A decorator is defined as a function that returns another function. The inner function usually contains the code that extends or modifies the behavior of the original function.
    
    3. **Using a Decorator**: You can apply a decorator to a function using the `@decorator_name` syntax above the function definition. This is syntactic sugar for calling the decorator function and passing the original function as an argument.
    
    #### Example:
    ```python
    def my_decorator(func):
        def wrapper():
            print("Something is happening before the function is called.")
            func()
            print("Something is happening after the function is called.")
        return wrapper
    
    @my_decorator
    def say_hello():
        print("Hello!")
    
    say_hello()
    ```
    
    #### Output:
    ```
    Something is happening before the function is called.
    Hello!
    Something is happening after the function is called.
    ```
    
    #### Use Cases:
    - Logging
    - Access control
    - Caching
    - Validation
    
    Decorators can also take arguments, allowing for even more flexibility. They are widely used in frameworks like Flask and Django for routing and middleware functionality.
    
    **Tags:** python, tutorial
    
    If you need any further modifications or additional notes, feel free to ask!



```python
response = await run_agent(
    "Create a note about LangGraph basics covering nodes, edges, and state. "
    "Tag it with 'langgraph' and 'agents'."
)
print(response)
```

    Available tools: ['create_note', 'search_notes', 'get_note', 'list_notes', 'update_note', 'delete_note', 'get_statistics']
    
    The note titled **"LangGraph Basics"** has been successfully created. Here are the details:
    
    ### LangGraph Basics
    LangGraph is a framework that allows for the representation and manipulation of knowledge in a graph structure. The fundamental components of LangGraph include:
    
    1. **Nodes**: These are the individual entities or concepts within the graph. Each node can represent a specific piece of information, such as a word, phrase, or even a more complex idea. Nodes can have attributes that provide additional context or metadata.
    
    2. **Edges**: Edges are the connections between nodes. They define the relationships between different entities in the graph. Edges can be directed or undirected, indicating the nature of the relationship (e.g., a parent-child relationship or a mutual connection).
    
    3. **State**: The state in LangGraph refers to the current configuration or condition of the graph at any given time. This includes the active nodes, the relationships that are currently being utilized, and any changes that have been made to the graph structure. Managing state is crucial for dynamic interactions and updates within the graph.
    
    Understanding these basic components is essential for effectively using LangGraph in various applications, including natural language processing, knowledge representation, and agent-based systems.
    
    **Tags**: langgraph, agents
    
    If you need any further modifications or additional notes, feel free to ask!


## Test: Searching and Listing


```python
response = await run_agent("Search for notes about Python.")
print(response)
```

    Available tools: ['create_note', 'search_notes', 'get_note', 'list_notes', 'update_note', 'delete_note', 'get_statistics']
    
    I found two notes related to Python:
    
    1. **Title:** Python Decorators
       - **Content:** 
         Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way. A decorator is essentially a function that takes another function as an argument and extends its behavior without explicitly modifying it.
         
         ### How Decorators Work:
         1. **Function as First-Class Objects**: In Python, functions are first-class objects, meaning they can be passed around as arguments, returned from other functions, and assigned to variables.
         
         2. **Defining a Decorator**: A decorator is defined as a function that returns another function. The inner function usually contains the code that extends the behavior of the original function.
         
         3. **Using a Decorator**: You can apply a decorator to a function using the `@decorator_name` syntax just above the function definition. This is syntactic sugar for calling the decorator function and passing the original function as an argument.
         
         ### Example:
         ```python
         def my_decorator(func):
             def wrapper():
                 print("Something is happening before the function is called.")
                 func()
                 print("Something is happening after the function is called.")
             return wrapper
         
         @my_decorator
         def say_hello():
             print("Hello!")
         
         say_hello()
         ```
         
         ### Output:
         ```
         Something is happening before the function is called.
         Hello!
         Something is happening after the function is called.
         ```
         
         ### Use Cases:
         - Logging
         - Access control
         - Caching
         - Validation
         
         Decorators are a key feature in Python that can help you write cleaner and more maintainable code by separating concerns and enhancing functionality without modifying the original code directly.
       - **Tags:** python, tutorial
       - **Created At:** December 10, 2025
    
    2. **Title:** Python Decorators
       - **Content:** 
         Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way. A decorator is essentially a function that takes another function as an argument and extends its behavior without explicitly modifying it.
         
         ### How Decorators Work:
         1. **Function as First-Class Objects**: In Python, functions are first-class objects, meaning they can be passed around as arguments, returned from other functions, and assigned to variables.
         
         2. **Defining a Decorator**: A decorator is defined as a function that returns another function. The inner function usually contains the code that extends or modifies the behavior of the original function.
         
         3. **Using a Decorator**: You can apply a decorator to a function using the `@decorator_name` syntax above the function definition. This is syntactic sugar for calling the decorator function and passing the original function as an argument.
         
         ### Example:
         ```python
         def my_decorator(func):
             def wrapper():
                 print("Something is happening before the function is called.")
                 func()
                 print("Something is happening after the function is called.")
             return wrapper
         
         @my_decorator
         def say_hello():
             print("Hello!")
         
         say_hello()
         ```
         
         ### Output:
         ```
         Something is happening before the function is called.
         Hello!
         Something is happening after the function is called.
         ```
         
         ### Use Cases:
         - Logging
         - Access control
         - Caching
         - Validation
         
         Decorators can also take arguments, allowing for even more flexibility. They are widely used in frameworks like Flask and Django for routing and middleware functionality.
       - **Tags:** python, tutorial
       - **Created At:** December 10, 2025
    
    If you need more information or want to explore a specific note, let me know!



```python
response = await run_agent("List all my notes and show me the knowledge base statistics.")
print(response)
```

    Available tools: ['create_note', 'search_notes', 'get_note', 'list_notes', 'update_note', 'delete_note', 'get_statistics']
    
    ### Your Notes
    
    1. **Title**: LangGraph Basics
       - **Content**: LangGraph is a framework that allows for the representation and manipulation of knowledge in a graph structure. The fundamental components of LangGraph include:
         - **Nodes**: Individual entities or concepts within the graph.
         - **Edges**: Connections between nodes that define relationships.
         - **State**: The current configuration of the graph.
       - **Tags**: langgraph, agents
       - **Created At**: December 10, 2025
       - **Updated At**: December 10, 2025
    
    2. **Title**: Python Decorators
       - **Content**: Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way. A decorator is essentially a function that takes another function as an argument and extends its behavior without explicitly modifying it.
         - **How Decorators Work**: Functions as first-class objects, defining a decorator, and using a decorator.
         - **Example**: Code snippet demonstrating a simple decorator.
         - **Use Cases**: Logging, access control, caching, validation.
       - **Tags**: python, tutorial
       - **Created At**: December 10, 2025
       - **Updated At**: December 10, 2025
    
    3. **Title**: Python Decorators
       - **Content**: (Same as above)
       - **Tags**: python, tutorial
       - **Created At**: December 10, 2025
       - **Updated At**: December 10, 2025
    
    ---
    
    ### Knowledge Base Statistics
    
    - **Total Notes**: 3
    - **Unique Tags**: 4
    - **Top Tags**:
      - python: 2
      - tutorial: 2
      - langgraph: 1
      - agents: 1
    - **Recent Notes**:
      - LangGraph Basics
      - Python Decorators
      - Python Decorators
    
    If you need any further information or actions regarding your notes, feel free to ask!


## Test: Multi-Tool Task


```python
response = await run_agent(
    "Check what notes I have, then create a 'Learning Roadmap' note "
    "that references the topics from my existing notes. Tag it with 'meta'."
)
print(response)
```

    Available tools: ['create_note', 'search_notes', 'get_note', 'list_notes', 'update_note', 'delete_note', 'get_statistics']
    
    I have checked your existing notes and created a new note titled **"Learning Roadmap"**. This note references the topics from your existing notes and is tagged with **"meta"**. 
    
    ### Learning Roadmap
    This roadmap outlines the key topics to explore based on existing notes:
    
    1. **LangGraph Basics**
       - Understanding nodes, edges, and state in graph structures.
       - Applications in natural language processing and knowledge representation.
    
    2. **Python Decorators**
       - How decorators work and their use cases.
       - Examples of defining and using decorators in Python.
    
    This roadmap serves as a guide for further learning and exploration in these areas. 
    
    If you need any further assistance or modifications, feel free to ask!


## Inspecting Tool Calls

Let's see the full trace of what the agent does.


```python
async def run_agent_verbose(user_message: str):
    """Run agent and show detailed tool call trace."""
    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()
    agent = create_agent(model=llm, tools=tools)
    
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": user_message}]
    })
    
    print("TRACE:")
    print("=" * 50)
    for i, msg in enumerate(result["messages"]):
        msg_type = type(msg).__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"[{i}] Tool: {tc['name']}({tc['args']})")
        elif msg_type == "ToolMessage":
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            print(f"[{i}] Result: {content}")
    print("=" * 50)
    
    return result["messages"][-1].content
```


```python
response = await run_agent_verbose(
    "Find notes tagged 'python' and add 'programming' to their tags."
)
print(f"\nFinal response:\n{response}")
```

    TRACE:
    ==================================================
    [1] Tool: list_notes({'tag_filter': 'python'})
    [2] Result: [{'type': 'text', 'text': '{"status":"success","total_count":4,"returned_count":2,"filter_applied":"python","notes":[{"id":"309f851d","title":"Python Decorators","content":"Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way. A decorator is essentially a function that takes another function as an argument and extends its behavior without explicitly modifying it.\\n\\n### How Decorators Work:\\n1. **Function as First-Class Objects**: In Python, functions are first-class objects, meaning they can be passed around as arguments, returned from other functions, and assigned to variables.\\n\\n2. **Defining a Decorator**: A decorator is defined as a function that returns another function. The inner function usually contains the code that extends or modifies the behavior of the original function.\\n\\n3. **Using a Decorator**: You can apply a decorator to a function using the `@decorator_name` syntax above the function definition. This is syntactic sugar for calling the decorator function and passing the original function as an argument.\\n\\n### Example:\\n```python\\ndef my_decorator(func):\\n    def wrapper():\\n        print(\\"Something is happening before the function is called.\\")\\n        func()\\n        print(\\"Something is happening after the function is called.\\")\\n    return wrapper\\n\\n@my_decorator\\ndef say_hello():\\n    print(\\"Hello!\\")\\n\\nsay_hello()\\n```\\n\\n### Output:\\n```\\nSomething is happening before the function is called.\\nHello!\\nSomething is happening after the function is called.\\n```\\n\\n### Use Cases:\\n- Logging\\n- Access control\\n- Caching\\n- Validation\\n\\nDecorators can also take arguments, allowing for even more flexibility. They are widely used in frameworks like Flask and Django for routing and middleware functionality.","tags":["python","tutorial"],"created_at":"2025-12-10T12:44:02.867233","updated_at":"2025-12-10T12:44:02.867233"},{"id":"beb35560","title":"Python Decorators","content":"Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way. A decorator is essentially a function that takes another function as an argument and extends its behavior without explicitly modifying it.\\n\\n### How Decorators Work:\\n1. **Function as First-Class Objects**: In Python, functions are first-class objects, meaning they can be passed around as arguments, returned from other functions, and assigned to variables.\\n\\n2. **Defining a Decorator**: A decorator is defined as a function that returns another function. The inner function usually contains the code that extends the behavior of the original function.\\n\\n3. **Using a Decorator**: You can apply a decorator to a function using the `@decorator_name` syntax just above the function definition. This is syntactic sugar for calling the decorator function and passing the original function as an argument.\\n\\n### Example:\\n```python\\ndef my_decorator(func):\\n    def wrapper():\\n        print(\\"Something is happening before the function is called.\\")\\n        func()\\n        print(\\"Something is happening after the function is called.\\")\\n    return wrapper\\n\\n@my_decorator\\ndef say_hello():\\n    print(\\"Hello!\\")\\n\\nsay_hello()\\n```\\n\\n### Output:\\n```\\nSomething is happening before the function is called.\\nHello!\\nSomething is happening after the function is called.\\n```\\n\\n### Use Cases:\\n- Logging\\n- Access control\\n- Caching\\n- Validation\\n\\nDecorators are a key feature in Python that can help you write cleaner and more maintainable code by separating concerns and enhancing functionality without modifying the original code directly.","tags":["python","tutorial"],"created_at":"2025-12-10T12:40:04.469786","updated_at":"2025-12-10T12:40:04.469786"}]}', 'id': 'lc_f725296e-e078-4208-8604-f5ad365926c1'}]
    [3] Tool: update_note({'note_id': '309f851d', 'tags': ['python', 'tutorial', 'programming']})
    [3] Tool: update_note({'note_id': 'beb35560', 'tags': ['python', 'tutorial', 'programming']})
    [4] Result: [{'type': 'text', 'text': '{"status":"success","message":"Note \'Python Decorators\' updated successfully","note":{"id":"309f851d","title":"Python Decorators","content":"Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way. A decorator is essentially a function that takes another function as an argument and extends its behavior without explicitly modifying it.\\n\\n### How Decorators Work:\\n1. **Function as First-Class Objects**: In Python, functions are first-class objects, meaning they can be passed around as arguments, returned from other functions, and assigned to variables.\\n\\n2. **Defining a Decorator**: A decorator is defined as a function that returns another function. The inner function usually contains the code that extends or modifies the behavior of the original function.\\n\\n3. **Using a Decorator**: You can apply a decorator to a function using the `@decorator_name` syntax above the function definition. This is syntactic sugar for calling the decorator function and passing the original function as an argument.\\n\\n### Example:\\n```python\\ndef my_decorator(func):\\n    def wrapper():\\n        print(\\"Something is happening before the function is called.\\")\\n        func()\\n        print(\\"Something is happening after the function is called.\\")\\n    return wrapper\\n\\n@my_decorator\\ndef say_hello():\\n    print(\\"Hello!\\")\\n\\nsay_hello()\\n```\\n\\n### Output:\\n```\\nSomething is happening before the function is called.\\nHello!\\nSomething is happening after the function is called.\\n```\\n\\n### Use Cases:\\n- Logging\\n- Access control\\n- Caching\\n- Validation\\n\\nDecorators can also take arguments, allowing for even more flexibility. They are widely used in frameworks like Flask and Django for routing and middleware functionality.","tags":["python","tutorial","programming"],"created_at":"2025-12-10T12:44:02.867233","updated_at":"2025-12-10T12:45:32.211737"}}', 'id': 'lc_da6a3bbf-eccb-43c2-a7ea-9702485eabb3'}]
    [5] Result: [{'type': 'text', 'text': '{"status":"success","message":"Note \'Python Decorators\' updated successfully","note":{"id":"beb35560","title":"Python Decorators","content":"Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way. A decorator is essentially a function that takes another function as an argument and extends its behavior without explicitly modifying it.\\n\\n### How Decorators Work:\\n1. **Function as First-Class Objects**: In Python, functions are first-class objects, meaning they can be passed around as arguments, returned from other functions, and assigned to variables.\\n\\n2. **Defining a Decorator**: A decorator is defined as a function that returns another function. The inner function usually contains the code that extends the behavior of the original function.\\n\\n3. **Using a Decorator**: You can apply a decorator to a function using the `@decorator_name` syntax just above the function definition. This is syntactic sugar for calling the decorator function and passing the original function as an argument.\\n\\n### Example:\\n```python\\ndef my_decorator(func):\\n    def wrapper():\\n        print(\\"Something is happening before the function is called.\\")\\n        func()\\n        print(\\"Something is happening after the function is called.\\")\\n    return wrapper\\n\\n@my_decorator\\ndef say_hello():\\n    print(\\"Hello!\\")\\n\\nsay_hello()\\n```\\n\\n### Output:\\n```\\nSomething is happening before the function is called.\\nHello!\\nSomething is happening after the function is called.\\n```\\n\\n### Use Cases:\\n- Logging\\n- Access control\\n- Caching\\n- Validation\\n\\nDecorators are a key feature in Python that can help you write cleaner and more maintainable code by separating concerns and enhancing functionality without modifying the original code directly.","tags":["python","tutorial","programming"],"created_at":"2025-12-10T12:40:04.469786","updated_at":"2025-12-10T12:45:32.211860"}}', 'id': 'lc_f7d7601b-bcc2-47da-a145-15a1640380a1'}]
    ==================================================
    
    Final response:
    I found two notes tagged with 'python' and successfully added 'programming' to their tags. Here are the updated details:
    
    1. **Note Title**: Python Decorators
       - **Tags**: python, tutorial, programming
       - **Content**: Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way...
    
    2. **Note Title**: Python Decorators
       - **Tags**: python, tutorial, programming
       - **Content**: Decorators in Python are a powerful tool that allows you to modify the behavior of a function or class. They are often used to add functionality to existing code in a clean and readable way...
    
    If you need any further assistance, feel free to ask!


## Cleanup


```python
import json

storage_file = Path(".").resolve() / "data" / "notes.json"
if storage_file.exists():
    storage_file.write_text(json.dumps({"notes": {}}, indent=2))
    print("Knowledge base cleared.")
```

    Knowledge base cleared.


## Summary

- Create `MultiServerMCPClient(config)` with `stdio` transport for local MCP servers
- Call `await client.get_tools()` to get LangChain-compatible tools
- Pass tools to `create_agent()` just like any other LangChain tools
- The same MCP server works with Claude Desktop, Cursor, and custom agents
```

---

## File: 3_5_retrieval_system_embeddings_tutorial.md

```markdown
# Building a Basic RAG Pipeline with LangGraph and ChromaDB

## Introduction

Welcome to this tutorial on building a **Retrieval-Augmented Generation (RAG)** system! RAG is a powerful technique that combines information retrieval with large language models (LLMs) to create more accurate, grounded responses based on your own knowledge base.

### What You'll Learn

In this notebook, you will learn to:
- Understand the two-phase RAG architecture (indexing and querying)
- Work with embeddings and vector stores for semantic search
- Use ChromaDB as an in-memory vector database
- Build a simple LangGraph workflow with retrieve and generate nodes
- Create a working RAG pipeline from start to finish

### Prerequisites

- Basic Python knowledge
- Understanding of LLMs and prompts
- Familiarity with LangGraph basics (states and nodes)
- An OpenAI API key (for embeddings and LLM)

### What is RAG?

RAG (Retrieval-Augmented Generation) is a technique that enhances LLM responses by:
1. **Retrieving** relevant information from a knowledge base
2. **Augmenting** the LLM prompt with that retrieved context
3. **Generating** responses grounded in factual information

This approach helps prevent hallucinations and allows LLMs to answer questions about information they weren't trained on.

### The RAG Pipeline

```
INDEXING PHASE (Offline):
Documents → Split into Chunks → Generate Embeddings → Store in Vector DB

QUERY PHASE (Runtime):
User Query → Embed Query → Similarity Search → Retrieve Top-K → Augment Prompt → Generate Response
```

Let's build this step by step!

## 1. Setup and Installation

First, let's install the required packages and set up our environment.


```python
# Install required packages
# Uncomment the line below if you need to install packages
# !pip install langchain langchain-openai langchain-chroma langchain-text-splitters langchain-core langgraph python-dotenv
```

### Import Required Libraries

We'll need:
- **LangChain Core**: For document processing and base abstractions
- **LangChain OpenAI**: For embeddings and language model
- **LangChain Chroma**: For our vector database integration
- **LangChain Text Splitters**: For chunking documents
- **LangGraph**: For building our RAG workflow
- **CSV**: For loading our data (built-in Python module)


```python
import os
import csv
from dotenv import load_dotenv
from typing import TypedDict, List

# LangChain imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

# LangGraph imports
from langgraph.graph import StateGraph, START, END

# Load environment variables
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")

print("All libraries imported successfully!")
print("OpenAI API key loaded")
```

## 2. Load and Explore the Data

We'll use a collection of Paul Graham's essays as our knowledge base. These essays cover topics like startups, programming, and technology.

The CSV file contains:
- `id`: Unique identifier for each essay
- `title`: Essay title
- `date`: Publication date
- `text`: Full essay content


```python
# Load the Paul Graham essays using Python's csv module
data_path = "pual_graham_essays.csv"

essays = []
with open(data_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        essays.append(row)

# Display basic information
print(f"Loaded {len(essays)} essays")
print(f"\nColumns: {list(essays[0].keys())}")
print(f"\nFirst few rows:")
for i, essay in enumerate(essays[:3]):
    print(f"\n{i+1}. {essay['title']} ({essay['date']})")
```

    Loaded 215 essays
    
    Columns: ['id', 'title', 'date', 'text']
    
    First few rows:
    
    1. The Age of the Essay (September 2004)
    
    2. A Plan for Spam (August 2002)
    
    3. The Trouble with the Segway (July 2009)



```python
# Let's look at one essay to understand the content
sample_essay = essays[0]
print(f"Title: {sample_essay['title']}")
print(f"Date: {sample_essay['date']}")
print(f"\nFirst 500 characters of text:")
print(sample_essay['text'][:500] + "...")
```

    Title: The Age of the Essay
    Date: September 2004
    
    First 500 characters of text:
    Remember the essays you had to write in high school? Topic sentence, introductory paragraph, supporting paragraphs, conclusion. The conclusion being, say, that Ahab in _Moby Dick_ was a Christ-like figure.
    
    Oy. So I'm going to try to give the other side of the story: what an essay really is, and how you write one. Or at least, how I write one.
    
    **Mods**
    
    The most obvious difference between real essays and the things one has to write in school is that real essays are not exclusively about English...


## 3. Indexing Phase: Building the Knowledge Base

The indexing phase is where we prepare our documents for retrieval. This happens **offline** (before any user queries) and consists of three main steps:

1. **Document Loading & Chunking**: Split large texts into smaller, manageable pieces
2. **Generate Embeddings**: Convert text chunks into numerical vectors that capture semantic meaning
3. **Store in Vector Database**: Save embeddings for efficient similarity search

### Why Chunking?

- LLMs have context limits
- Smaller chunks improve retrieval precision
- Each chunk can be independently searched and ranked
- Typical chunk size: 500-1500 characters with 10-20% overlap

### Step 3.1: Convert Data to LangChain Documents

LangChain's `Document` object holds:
- `page_content`: The actual text
- `metadata`: Additional information (title, date, source, etc.)


```python
# Convert essays to LangChain Document objects
documents = []

for essay in essays:
    doc = Document(
        page_content=essay['text'],
        metadata={
            'title': essay['title'],
            'date': essay['date'],
            'essay_id': essay['id']
        }
    )
    documents.append(doc)

print(f"Created {len(documents)} documents")
print(f"\nExample document:")
print(f"Content length: {len(documents[0].page_content)} characters")
print(f"Metadata: {documents[0].metadata}")
```

    Created 215 documents
    
    Example document:
    Content length: 26200 characters
    Metadata: {'title': 'The Age of the Essay', 'date': 'September 2004', 'essay_id': '0'}


### Step 3.2: Split Documents into Chunks

We'll use `RecursiveCharacterTextSplitter` which:
- Splits text at natural boundaries (paragraphs, sentences)
- Maintains a target chunk size
- Creates overlap between chunks to preserve context

**Parameters:**
- `chunk_size=1000`: Target size for each chunk (in characters)
- `chunk_overlap=200`: Overlap between chunks (20% overlap helps maintain context)


```python
# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]  # Try to split at paragraph, then line, then word
)

# Split all documents into chunks
chunks = text_splitter.split_documents(documents)

print(f"Original documents: {len(documents)}")
print(f"Total chunks after splitting: {len(chunks)}")
print(f"Average chunks per document: {len(chunks) / len(documents):.1f}")
print(f"\nExample chunk:")
print(f"Content: {chunks[0].page_content[:300]}...")
print(f"Metadata: {chunks[0].metadata}")
```

    Original documents: 215
    Total chunks after splitting: 3924
    Average chunks per document: 18.3
    
    Example chunk:
    Content: Remember the essays you had to write in high school? Topic sentence, introductory paragraph, supporting paragraphs, conclusion. The conclusion being, say, that Ahab in _Moby Dick_ was a Christ-like figure.
    
    Oy. So I'm going to try to give the other side of the story: what an essay really is, and how...
    Metadata: {'title': 'The Age of the Essay', 'date': 'September 2004', 'essay_id': '0'}


### Step 3.3: Initialize Embeddings Model

**What are embeddings?**
Embeddings are numerical vectors that capture the semantic meaning of text. Similar concepts have similar vectors.

Examples:
- "dog" and "puppy" → close vectors
- "dog" and "car" → distant vectors

We'll use OpenAI's `text-embedding-3-small` model:
- Fast and cost-effective
- 1536 dimensions
- Good for most RAG applications


```python
# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

print("Embeddings model initialized")
print("Model: text-embedding-3-small")

# Optional: Test the embeddings with a sample text
sample_text = "What is a startup?"
sample_embedding = embeddings.embed_query(sample_text)
print(f"\nSample embedding dimensions: {len(sample_embedding)}")
print(f"First 5 values: {sample_embedding[:5]}")
```

### Step 3.4: Create Vector Store with ChromaDB via LangChain

Now we'll create our vector database using LangChain's Chroma integration. This will:
1. Initialize a Chroma vector store with our embeddings model
2. Store document chunks with their embeddings
3. Enable fast similarity search

**LangChain's Chroma integration** automatically handles:
- Generating embeddings for all chunks
- Storing embeddings along with text and metadata
- Managing the ChromaDB collection

**Note:** We're using in-memory mode by not specifying `persist_directory`. In production, you'd add `persist_directory="./chroma_db"` to persist the data to disk.

**This step takes a few moments** as it generates embeddings for all chunks.


```python
# Create vector store using LangChain's Chroma
print("Creating Chroma vector store... (this may take a minute)")

vectorstore = Chroma(
    collection_name="paul_graham_essays",
    embedding_function=embeddings,
    # persist_directory="./chroma_db"  # Uncomment to persist to disk
)

# Add all document chunks to the vector store
# This will automatically generate embeddings and store them
print("Adding documents and generating embeddings...")
vectorstore.add_documents(documents=chunks)

print(f"\nVector store created successfully!")
print(f"Total chunks indexed: {len(chunks)}")
print("\nThe indexing phase is complete. Your knowledge base is ready for queries!")
```

### Test the Vector Store

Let's test our vector store by performing a simple similarity search. This will show us that retrieval is working correctly.


```python


# Test similarity search
test_query = "What makes a good startup idea?"

# Perform similarity search (returns Document objects)
results = vectorstore.similarity_search(test_query, k=3)

print(f"Query: '{test_query}'\n")
print(f"Found {len(results)} relevant chunks:\n")

for i, doc in enumerate(results, 1):
    print(f"--- Result {i} ---")
    print(f"Title: {doc.metadata.get('title', 'Unknown')}")
    print(f"Content preview: {doc.page_content[:200]}...")
    print()
```

    Query: 'What makes a good startup idea?'
    
    Found 3 relevant chunks:
    
    --- Result 1 ---
    Title: How to Get Startup Ideas
    Content preview: The way to get startup ideas is not to try to think of startup ideas. It's to look for problems, preferably problems you have yourself.
    
    The very best startup ideas tend to have three things in common...
    
    --- Result 2 ---
    Title: How to Get Startup Ideas
    Content preview: Made-up startup ideas are usually of the first type. Lots of people are mildly interested in a social network for pet owners.
    
    Nearly all good startup ideas are of the second type. Microsoft was a wel...
    
    --- Result 3 ---
    Title: How to Get Startup Ideas
    Content preview: Finding startup ideas is a subtle business, and that's why most people who try fail so miserably. It doesn't work well simply to try to think of startup ideas. If you do that, you get bad ones that so...
    


## 4. Query Phase: Building the RAG Workflow

Now we'll build the **query phase** using LangGraph. This phase runs at runtime for each user question and consists of:

1. **Retrieve Node**: Find relevant document chunks
2. **Generate Node**: Create a response using retrieved context

### RAG State Definition

First, let's define our state. The state holds all the information that flows through our workflow nodes.


```python
# Define the state that will be passed between nodes
class RAGState(TypedDict):
    """State for our RAG workflow."""
    query: str                    # User's question
    context: List[Document]       # Retrieved document chunks
    answer: str                   # Final generated answer

print("RAG state defined")
print("\nState fields:")
print("  - query: The user's question")
print("  - context: Retrieved relevant document chunks")
print("  - answer: The final LLM-generated response")
```

    RAG state defined
    
    State fields:
      - query: The user's question
      - context: Retrieved relevant document chunks
      - answer: The final LLM-generated response


### Node 1: Retrieve Documents

The retrieve node:
1. Takes the user query from the state
2. Embeds the query (converts to vector)
3. Performs similarity search in the vector store
4. Returns the top-k most relevant chunks

**Key Point:** We use the same embedding model for queries as we used for indexing. This ensures queries and documents exist in the same vector space.


```python
def retrieve_node(state: RAGState) -> RAGState:
    """
    Retrieve relevant documents based on the query.
    
    This node:
    1. Takes the query from state
    2. Performs similarity search in the vector store
    3. Returns top 5 most relevant chunks as Document objects
    """
    query = state["query"]
    
    print(f"Retrieving documents for query: '{query}'")
    
    # Perform similarity search using LangChain's Chroma
    # k=5 means we retrieve the top 5 most relevant chunks
    retrieved_docs = vectorstore.similarity_search(query, k=5)
    
    print(f"Retrieved {len(retrieved_docs)} relevant documents")
    
    # Update state with retrieved context
    return {
        "query": query,
        "context": retrieved_docs,
        "answer": ""  # Will be filled by generate node
    }

print("Retrieve node defined")
```

    Retrieve node defined


### Node 2: Generate Answer

The generate node:
1. Takes the query and retrieved context from state
2. Formats the context into a readable string
3. Creates a prompt that instructs the LLM to use the context
4. Calls the LLM to generate a grounded response

**The RAG Magic:** By providing retrieved context in the prompt, we ground the LLM's response in factual information from our knowledge base.


```python
# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create a prompt template for RAG
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant answering questions about Paul Graham's essays.
    
Use the following context to answer the user's question. If you cannot answer the question based 
on the context, say so clearly. Always ground your answer in the provided context.

Context:
{context}
"""),
    ("human", "{query}")
])

def generate_node(state: RAGState) -> RAGState:
    """
    Generate an answer using retrieved context.
    
    This node:
    1. Formats retrieved documents as context
    2. Creates a prompt with context + query
    3. Calls LLM to generate grounded response
    """
    query = state["query"]
    context_docs = state["context"]
    
    print(f"Generating answer using {len(context_docs)} context chunks")
    
    # Format context: combine all retrieved documents
    context_text = "\n\n".join([
        f"[From '{doc.metadata.get('title', 'Unknown')}']\\n{doc.page_content}"
        for doc in context_docs
    ])
    
    # Create the prompt with context
    prompt = rag_prompt.invoke({
        "context": context_text,
        "query": query
    })
    
    # Generate response
    response = llm.invoke(prompt)
    answer = response.content
    
    print("Answer generated")
    
    # Update state with final answer
    return {
        "query": query,
        "context": context_docs,
        "answer": answer
    }

print("Generate node defined")
```

    Generate node defined


### Build the LangGraph Workflow

Now we'll assemble our nodes into a workflow using LangGraph's `StateGraph`.

Our workflow is simple and linear:
```
START → retrieve → generate → END
```

This means:
1. Start with a query
2. Always retrieve context first
3. Then generate an answer
4. Return the final result


```python
# Create the workflow
workflow = StateGraph(RAGState)

# Add nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

# Define the flow
workflow.add_edge(START, "retrieve")        # Start by retrieving
workflow.add_edge("retrieve", "generate")   # Then generate answer
workflow.add_edge("generate", END)          # End after generating

# Compile the workflow
rag_app = workflow.compile()

print("RAG workflow compiled successfully!")
print("\nWorkflow structure:")
print("  START -> retrieve -> generate -> END")
```

    RAG workflow compiled successfully!
    
    Workflow structure:
      START -> retrieve -> generate -> END


### Visualize the Workflow (Optional)

LangGraph can generate a visual representation of your workflow. This helps you understand the flow of data through your nodes.


```python
# Display the workflow graph
try:
    from IPython.display import Image, display
    display(Image(rag_app.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Could not display graph: {e}")
    print("Graph visualization requires graphviz. The workflow will still work fine!")
```


    
![png](3_5_retrieval_system_embeddings_tutorial_files/3_5_retrieval_system_embeddings_tutorial_28_0.png)
    


## 5. Using the RAG Pipeline

Now our RAG pipeline is complete! Let's test it with some questions about Paul Graham's essays.

### Helper Function for Queries


```python
def ask_question(query: str, verbose: bool = True):
    """
    Ask a question using the RAG pipeline.
    
    Args:
        query: The question to ask
        verbose: If True, print retrieval details
    
    Returns:
        The answer and retrieved context
    """
    print("=" * 80)
    print(f"Question: {query}")
    print("=" * 80)
    print()
    
    # Run the workflow
    result = rag_app.invoke({
        "query": query,
        "context": [],
        "answer": ""
    })
    
    # Display results
    if verbose:
        print("\nRetrieved Context:")
        print("-" * 80)
        for i, doc in enumerate(result["context"], 1):
            print(f"\n[{i}] {doc.metadata.get('title', 'Unknown')} ({doc.metadata.get('date', 'Unknown')})")
            print(f"    {doc.page_content[:150]}...")
    
    print("\nAnswer:")
    print("=" * 80)
    print(result["answer"])
    print("\n")
    
    return result

print("Helper function ready")
```

    Helper function ready


### Example Query 1: Startup Ideas

Let's ask about what makes a good startup idea, a common topic in Paul Graham's essays.


```python
result1 = ask_question("What makes a good startup idea according to Paul Graham?")
```

    ================================================================================
    Question: What makes a good startup idea according to Paul Graham?
    ================================================================================
    
    Retrieving documents for query: 'What makes a good startup idea according to Paul Graham?'
    Retrieved 5 relevant documents
    Generating answer using 5 context chunks
    Answer generated
    
    Retrieved Context:
    --------------------------------------------------------------------------------
    
    [1] How to Get Startup Ideas (November 2012)
        The way to get startup ideas is not to try to think of startup ideas. It's to look for problems, preferably problems you have yourself.
    
    The very best...
    
    [2] How to Start a Startup (March 2005)
        _(This essay is derived from a talk at the Harvard Computer Society.)_
    
    You need three things to create a successful startup: to start with good peopl...
    
    [3] How to Get Startup Ideas (November 2012)
        Made-up startup ideas are usually of the first type. Lots of people are mildly interested in a social network for pet owners.
    
    Nearly all good startup...
    
    [4] How to Get Startup Ideas (November 2012)
        Finding startup ideas is a subtle business, and that's why most people who try fail so miserably. It doesn't work well simply to try to think of start...
    
    [5] How to Get Startup Ideas (November 2012)
        **Well**
    
    When a startup launches, there have to be at least some users who really need what they're making — not just people who could see themselves...
    
    Answer:
    ================================================================================
    According to Paul Graham, a good startup idea typically has three key characteristics:
    
    1. **It is something the founders themselves want**: This ensures that the problem is real and that the founders are personally invested in solving it.
    
    2. **The founders can build it**: The technical capability to create the product or service is crucial.
    
    3. **Few others realize it is worth doing**: This means that the idea is not widely recognized or pursued by others, giving the startup a unique position in the market.
    
    Additionally, Graham emphasizes the importance of focusing on problems that genuinely exist and that the initial group of users should urgently need what the startup is offering. He suggests that good startup ideas often come from identifying gaps or needs that may not seem like obvious business opportunities at first.
    
    


### Example Query 2: Programming Languages

Paul Graham has written extensively about programming languages, particularly Lisp.


```python
result2 = ask_question("What does Paul Graham think about programming languages?")
```

    ================================================================================
    Question: What does Paul Graham think about programming languages?
    ================================================================================
    
    Retrieving documents for query: 'What does Paul Graham think about programming languages?'
    Retrieved 5 relevant documents
    Generating answer using 5 context chunks
    Answer generated
    
    Retrieved Context:
    --------------------------------------------------------------------------------
    
    [1] Beating the Averages (April 2003)
        Ordinarily technology changes fast. But programming languages are different: programming languages are not just technology, but what programmers think...
    
    [2] Succinctness is Power (May 2002)
        Brooks' hypothesis, if it's true, seems to be at the very heart of hacking. In the years since, I've paid close attention to any evidence I could get ...
    
    [3] What Languages Fix ()
        Kevin Kelleher suggested an interesting way to compare programming languages: to describe each in terms of the problem it fixes. The surprising thing ...
    
    [4] Beating the Averages (April 2003)
        I'll begin with a shockingly controversial statement: programming languages vary in power.
    
    Few would dispute, at least, that high level languages are...
    
    [5] Revenge of the Nerds (May 2002)
        Presumably, if you create a new language, it's because you think it's better in some way than what people already had. And in fact, Gosling makes it c...
    
    Answer:
    ================================================================================
    Paul Graham believes that programming languages vary significantly in power and that they are not just tools but also shape the way programmers think. He argues that high-level languages are generally more powerful than low-level languages, such as machine language, and that it is a mistake to use anything but the most powerful language available when given a choice. He also notes that programming languages have a slow evolution due to their deep integration into the thinking processes of programmers, which he likens to a form of religion. Additionally, he discusses how different languages are created to address specific problems, indicating that some languages are indeed better suited for certain tasks than others.
    
    



```python

```
```

---

## File: 3_7_deep_agents.md

```markdown
# Building Deep Agents with LangChain's DeepAgents Package

## Introduction

This tutorial teaches you how to build and run **deep agents** using LangChain's DeepAgents package. You'll learn what makes deep agents powerful and how to implement sophisticated agentic systems capable of handling complex, long-running tasks.

### What You'll Learn
- Understanding deep planning in AI agents
- The four core characteristics of deep agents
- How to install and configure the deepagents package
- Building a deep agent with ChatOpenAI and Tavily search
- Running and testing deep agents
- Practical examples demonstrating deep agent capabilities

### Prerequisites
- Basic Python knowledge
- Understanding of LLMs and AI agents
- OpenAI API key
- Tavily API key (for search functionality)

### Learning Objectives
By the end of this tutorial, you'll be able to:
1. Identify the four core characteristics that make an agent "deep"
2. Build a functional deep agent using the deepagents package
3. Implement planning tools, file system access, and subagents
4. Deploy deep agents for complex, multi-step tasks

## Part 1: Understanding Deep Agents

### What Are Deep Agents?

**Deep agents** are advanced AI systems that:
- Go beyond basic tool-calling loops
- Handle complex, long-running tasks
- Maintain sophisticated coordination and memory management
- Use persistent storage and planning tools
- Examples include: Claude Code, Deep Research systems, Manus

### The Four Core Characteristics of Deep Agents

| Characteristic | Description |
|----------------|-------------|
| **1. System Prompts** | Detailed instructions with examples, edge cases, and workflows |
| **2. Planning Tools** | Explicit planning tools (todo lists, progress tracking) |
| **3. Architecture** | Multiple specialized sub-agents for task decomposition |
| **4. Memory/Storage** | File system access + persistent storage |

Let's explore each characteristic in detail:

### 1. Detailed System Prompts

**Example Deep Agent Prompt:**
```
You are an expert researcher with access to web search and file tools.

TOOL USAGE PATTERNS:
- When searching: start broad, then narrow based on results
- When analyzing code: try function definitions first, then usage examples
- For debugging: read full error → check related files → test incrementally

ERROR HANDLING:
- If a search returns no results, try alternative keywords
- If a file is not found, check the directory structure first

MULTI-STEP WORKFLOWS:
1. Break complex tasks into subtasks using the todo tool
2. Save intermediate findings to files for later reference
3. Use subagents for specialized analysis
```

Deep agent prompts provide comprehensive guidance on tool usage, error handling, and workflows.

### 2. Planning Tools

Planning tools help agents maintain focus on long-term objectives:
- **Purpose**: Context engineering to keep agents organized
- **Implementation**: Todo lists, step trackers, progress monitors
- **Benefit**: Agent stays on track across complex, multi-step tasks
- **Key Insight**: Even if functionally simple, planning tools serve as prompts that structure the agent's thinking

### 3. Sub-agents

Sub-agents enable task decomposition:
- **Task decomposition**: Break complex work into specialized subtasks
- **Focused expertise**: Each sub-agent handles a specific domain
- **Context management**: Reduce prompt complexity per agent
- **Example**: Main agent delegates to `code_analyzer`, `test_generator`, `docs_writer`
- **Benefit**: Enables deep focus while maintaining coordination

### 4. File System Access & Persistent Memory

File system access provides:
- **Persistent memory** beyond conversation context
- **Shared workspace** for multi-agent collaboration
- **Long-term state** across sessions or restarts
- **Artifact storage** for intermediate results

This allows agents to:
- Save analysis findings for later reference
- Store plans that multiple sub-agents can access
- Build up a knowledge base over extended workflows
- Enable asynchronous agent coordination

## Part 2: Setup and Installation

Let's set up our environment and install the necessary packages.


```python
# Install required packages
# Run this cell first if you don't have these packages installed
# !pip install -q deepagents langchain-openai tavily-python python-dotenv
```

### Environment Setup

We'll use `load_dotenv()` to load API keys from a `.env` file. Create a `.env` file in your project directory with:

```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Get your API keys from:
- OpenAI: https://platform.openai.com/api-keys
- Tavily: https://tavily.com/


```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify API keys are loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment")
if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY not found in environment")

print("Environment variables loaded successfully!")
```

    Environment variables loaded successfully!


## Part 3: Building Your First Deep Agent

Now let's build a deep agent step by step. We'll start with the basic components and gradually add more sophisticated features.

### Step 1: Import Required Libraries


```python
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
```

### Step 2: Configure the LLM Model

We'll use ChatOpenAI as our language model. The deepagents package defaults to Claude Sonnet 4.5, but we'll explicitly use GPT-4o for this tutorial.


```python
# Initialize the ChatOpenAI model
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

print(f"Model initialized: {model.model_name}")
```

    Model initialized: gpt-4o


### Step 3: Set Up the Tavily Search Tool

Tavily provides a powerful search API that deep agents can use to access current information from the web.


```python
# Initialize Tavily client
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
```

    Tavily search tool configured successfully!


### Step 4: Create a Basic Deep Agent

Let's create our first deep agent with a detailed system prompt and the search tool.


```python
from pathlib import Path
from deepagents.backends import FilesystemBackend

# Create a dedicated workspace directory for agent files
agent_workspace = Path("./agent_workspace")
agent_workspace.mkdir(exist_ok=True)

print(f"Agent workspace created at: {agent_workspace.absolute()}")
```

    Agent workspace created at: /Users/sajal/code/active/projects/oreilly_ai_agent_skill/level_3/agent_workspace


### Optional: Configure File System Directory

By default, deep agents use ephemeral storage (files are lost when the thread ends). Let's configure a persistent directory where the agent will save files:


```python
# Define a detailed system prompt (characteristic #1 of deep agents)
system_prompt = """You are an expert research assistant with access to web search and file management tools.

YOUR ROLE:
- Conduct thorough research on user queries
- Break down complex questions into manageable subtasks
- Synthesize information from multiple sources
- Save important findings to files for reference.

TOOL USAGE GUIDELINES:
- Use internet_search for current information and facts
- Start with broad searches, then narrow based on results
- Always cite sources when presenting information
- Save detailed research findings to files for later reference

WORKFLOW FOR COMPLEX TASKS:
1. Break the task into subtasks using the write_todos tool
2. Execute each subtask systematically
3. Save intermediate findings to files
4. Synthesize results into a comprehensive answer

ERROR HANDLING:
- If a search returns no results, try alternative keywords
- If information is unclear, search for clarification
- Always verify facts from multiple sources when possible
"""

# Create the deep agent with persistent filesystem
agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=system_prompt,
    backend=FilesystemBackend(root_dir=str(agent_workspace), virtual_mode=True)
)

print("Deep agent created successfully!")
print("\\nAgent capabilities:")
print("- Planning tool (write_todos)")
print("- File system tools (read, write, edit files)")
print("- Internet search via Tavily")
print("- Subagent spawning (task tool)")
print(f"- Files will be saved to: {agent_workspace.absolute()}")
```

    Deep agent created successfully!
    \nAgent capabilities:
    - Planning tool (write_todos)
    - File system tools (read, write, edit files)
    - Internet search via Tavily
    - Subagent spawning (task tool)
    - Files will be saved to: /Users/sajal/code/active/projects/oreilly_ai_agent_skill/level_3/agent_workspace


### Understanding What Just Happened

The `create_deep_agent()` function automatically equipped our agent with:

1. **TodoListMiddleware**: Provides the `write_todos` tool for planning
2. **FilesystemMiddleware**: Adds file system tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`)
3. **SubAgentMiddleware**: Enables the `task` tool for spawning specialized subagents
4. **Custom Tools**: Our `internet_search` function

This demonstrates the power of deep agents: they have built-in capabilities for planning, memory, and task decomposition that enable sophisticated workflows.

## Part 4: Running the Deep Agent

Let's test our deep agent with progressively more complex tasks to see how it leverages its deep planning capabilities.

### Helper Function: Stream Agent Responses

Before running examples, let's create a reusable helper function to stream and display agent responses with clean formatting. This function:

- **Tracks message IDs** to avoid duplicate output (since `stream_mode="values"` returns full state)
- **Formats different message types** clearly (`[USER]`, `[AGENT]`, `[TOOL]`)
- **Supports detailed mode** to show planning, search queries, and file operations
- **Handles content truncation** for long responses

This makes it easy to observe agent behavior across different examples.


```python
def stream_agent_response(agent, query, show_details=False, max_content_length=1000):
    """
    Stream and display agent responses with clean formatting.
    
    Args:
        agent: The deep agent instance
        query: The query string to send to the agent
        show_details: If True, show detailed tool arguments and planning
        max_content_length: Maximum characters to show for content (None for full content)
    """
    print(f"Query: {query if len(query) <= 100 else query[:100] + '...'}")
    print("\n" + "="*80)
    print("Streaming Agent Actions:")
    print("="*80 + "\n")
    
    # Track message IDs to avoid duplicates
    seen_message_ids = set()
    
    # Stream using stream_mode="values"
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values"
    ):
        if "messages" in chunk:
            for message in chunk["messages"]:
                msg_id = message.id
                
                # Skip if we've already printed this message
                if msg_id in seen_message_ids:
                    continue
                    
                seen_message_ids.add(msg_id)
                msg_type = getattr(message, 'type', 'unknown')
                
                # Format based on message type
                if msg_type == 'human':
                    content = message.content
                    if max_content_length and len(content) > max_content_length:
                        content = content[:max_content_length] + "..."
                    print(f"[USER]: {content}")
                    print("-" * 80)
                    
                elif msg_type == 'ai':
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        print(f"[AGENT] Calling {len(message.tool_calls)} tool(s):")
                        for tc in message.tool_calls:
                            tool_name = tc.get('name', 'unknown')
                            tool_args = tc.get('args', {})
                            
                            # Show detailed formatting for specific tools
                            if tool_name == 'write_todos' and show_details:
                                todos = tool_args.get('todos', [])
                                print(f"  - {tool_name}: Planning {len(todos)} tasks")
                                for i, todo in enumerate(todos, 1):
                                    status = todo.get('status', 'pending')
                                    content = todo.get('content', '')[:50]
                                    print(f"      {i}. [{status}] {content}...")
                            elif tool_name == 'internet_search' and show_details:
                                query_str = tool_args.get('query', '')
                                print(f"  - {tool_name}: '{query_str}'")
                            elif tool_name == 'write_file' and show_details:
                                path = tool_args.get('path', '')
                                print(f"  - {tool_name}: {path}")
                            else:
                                # Simple format: show function call with key args
                                args_str = ', '.join(f'{k}={v}' for k, v in list(tool_args.items())[:2])
                                print(f"  - {tool_name}({args_str})")
                                
                    elif message.content:
                        content = message.content
                        if max_content_length and len(content) > max_content_length:
                            content = content[:max_content_length] + "..."
                        print(f"[AGENT]: {content}")
                    print("-" * 80)
                    
                elif msg_type == 'tool':
                    tool_name = getattr(message, 'name', 'unknown')
                    print(f"[TOOL: {tool_name}] Completed")
                    print("-" * 80)
    
    print("\n" + "="*80)
    print("Execution completed!")
    print("="*80)

print("Helper function 'stream_agent_response' created!")
```

    Helper function 'stream_agent_response' created!


### Example 1: Simple Query

First, let's see how the deep agent handles a simple query.


```python
# Simple query with streaming
simple_query = "What is LangGraph?"

# Use the helper function to stream and display the response
stream_agent_response(agent, simple_query, show_details=False, max_content_length=None)
```

    Query: What is LangGraph?
    
    ================================================================================
    Streaming Agent Actions:
    ================================================================================
    
    [USER]: What is LangGraph?
    --------------------------------------------------------------------------------
    [AGENT] Calling 1 tool(s):
      - internet_search(query=LangGraph, max_results=5)
    --------------------------------------------------------------------------------
    [TOOL: internet_search] Completed
    --------------------------------------------------------------------------------
    [AGENT]: LangGraph is an open-source AI agent framework designed to build, deploy, and manage complex generative AI agent workflows. It utilizes graph-based architectures to model and manage the intricate relationships between various components of an AI agent workflow. LangGraph is built on several key technologies, including LangChain, a Python framework for building AI applications. It provides a versatile platform for developing AI solutions and workflows, such as chatbots, state graphs, and other agent-based systems. LangGraph is particularly useful for creating scalable and production-ready AI workloads, offering features like long-term memory and customizable architectures for complex task handling.
    
    For more detailed information, you can visit [IBM's LangGraph overview](https://www.ibm.com/think/topics/langgraph) or explore the [LangGraph GitHub repository](https://github.com/langchain-ai/langgraph).
    --------------------------------------------------------------------------------
    
    ================================================================================
    Execution completed!
    ================================================================================


### Example 2: Multi-Step Research Task

Now let's give the agent a complex task that requires planning and multiple steps. We'll use `show_details=True` to see the planning, search queries, and file operations in detail.


```python
# Complex multi-step task with streaming
complex_query = """Research the current state of AI agents in 2025. I need:
1. The main frameworks and tools being used
2. Key differences between agent architectures
3. Real-world applications and use cases
4. Save your findings to a file called 'ai_agents_research_2025.txt' in the current directory.
"""

# Use the helper function with detailed output for complex tasks
stream_agent_response(agent, complex_query, show_details=True, max_content_length=None)
```

    Query: Research the current state of AI agents in 2025. I need:
    1. The main frameworks and tools being used...
    
    ================================================================================
    Streaming Agent Actions:
    ================================================================================
    
    [USER]: Research the current state of AI agents in 2025. I need:
    1. The main frameworks and tools being used
    2. Key differences between agent architectures
    3. Real-world applications and use cases
    4. Save your findings to a file called 'ai_agents_research_2025.txt' in the current directory.
    
    --------------------------------------------------------------------------------
    [AGENT] Calling 1 tool(s):
      - write_todos: Planning 5 tasks
          1. [in_progress] Research the main frameworks and tools being used ...
          2. [pending] Research key differences between AI agent architec...
          3. [pending] Research real-world applications and use cases of ...
          4. [pending] Compile research findings into a comprehensive rep...
          5. [pending] Save the report to a file named 'ai_agents_researc...
    --------------------------------------------------------------------------------
    [TOOL: write_todos] Completed
    --------------------------------------------------------------------------------
    [AGENT] Calling 1 tool(s):
      - internet_search: 'AI agent frameworks and tools 2025'
    --------------------------------------------------------------------------------
    [TOOL: internet_search] Completed
    --------------------------------------------------------------------------------
    [AGENT] Calling 1 tool(s):
      - task(description=Research key differences between AI agent architectures in 2025. Focus on the architectural design, scalability, and efficiency of different AI agent systems. Provide a summary of the key differences and any notable trends or innovations in AI agent architectures., subagent_type=general-purpose)
    --------------------------------------------------------------------------------
    [TOOL: task] Completed
    --------------------------------------------------------------------------------
    [AGENT] Calling 1 tool(s):
      - task(description=Research real-world applications and use cases of AI agents in 2025. Focus on industries such as healthcare, finance, retail, and logistics. Provide examples of how AI agents are being used to solve specific problems or improve processes in these industries., subagent_type=general-purpose)
    --------------------------------------------------------------------------------
    [TOOL: task] Completed
    --------------------------------------------------------------------------------
    [AGENT] Calling 1 tool(s):
      - write_todos: Planning 5 tasks
          1. [completed] Research the main frameworks and tools being used ...
          2. [completed] Research key differences between AI agent architec...
          3. [completed] Research real-world applications and use cases of ...
          4. [in_progress] Compile research findings into a comprehensive rep...
          5. [pending] Save the report to a file named 'ai_agents_researc...
    --------------------------------------------------------------------------------
    [TOOL: write_todos] Completed
    --------------------------------------------------------------------------------
    [AGENT] Calling 1 tool(s):
      - write_file: 
    --------------------------------------------------------------------------------
    [TOOL: write_file] Completed
    --------------------------------------------------------------------------------
    [AGENT] Calling 1 tool(s):
      - write_todos: Planning 5 tasks
          1. [completed] Research the main frameworks and tools being used ...
          2. [completed] Research key differences between AI agent architec...
          3. [completed] Research real-world applications and use cases of ...
          4. [completed] Compile research findings into a comprehensive rep...
          5. [completed] Save the report to a file named 'ai_agents_researc...
    --------------------------------------------------------------------------------
    [TOOL: write_todos] Completed
    --------------------------------------------------------------------------------
    [AGENT]: I have completed the research on the current state of AI agents in 2025. The findings have been compiled into a comprehensive report and saved to a file named [ai_agents_research_2025.txt](sandbox:/ai_agents_research_2025.txt). This report includes information on the main frameworks and tools, key differences between agent architectures, and real-world applications and use cases across various industries.
    --------------------------------------------------------------------------------
    
    ================================================================================
    Execution completed!
    ================================================================================

```

---

## File: 3_8_implement_a_human_in_the_loop.md

```markdown
# Implementing Human-in-the-Loop in LangGraph: The Edit Pattern

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Set up checkpointing in LangGraph (required for human-in-the-loop)
2. Use `interrupt()` to pause workflow execution at critical points
3. Resume workflows with `Command(resume=<value>)` to pass data back to the interrupt
4. Use `interrupt_before` as an alternative interrupt mechanism

## What You'll Build

We'll build an **Email Draft Agent** that:
1. Takes a user's request for an email
2. Generates a draft email using an LLM
3. **Pauses for human review** - allowing the human to edit the draft
4. Proceeds to "send" the email after human review

## Requirements for Human-in-the-Loop in LangGraph

To implement human-in-the-loop, you need:

1. **Checkpointing**: State must be saved so the workflow can pause and resume
2. **Interrupts**: Mechanism to pause execution at specific points
3. **State updates**: Ability to modify state before resuming

## Part 1: Environment Setup

Let's install and import the required packages.


```python
# Install required packages if needed
# Uncomment the following line if you need to install the packages
# !pip install langgraph langchain-openai python-dotenv
```


```python
# Load environment variables
from dotenv import load_dotenv
import os

# Load API keys from .env file
load_dotenv()

# Verify that keys are loaded
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not found in environment"

print("Environment variables loaded successfully!")
```

    Environment variables loaded successfully!



```python
# Import dependencies
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

print("All imports successful!")
```

    All imports successful!


## Part 2: Define the State

Our Email Draft Agent tracks the user's request, the generated draft, and the workflow status.


```python
class EmailAgentState(TypedDict):
    """State schema for the Email Draft Agent."""
    
    # The user's request describing what email they want
    request: str
    
    # The generated email draft (can be edited by human)
    email_draft: str
    
    # Status of the email: 'drafting', 'pending_review', 'sent'
    status: str


print("State schema defined!")
print("\nState fields:")
print("  - request: The user's email request")
print("  - email_draft: The generated draft (editable by human)")
print("  - status: Current workflow status")
```

    State schema defined!
    
    State fields:
      - request: The user's email request
      - email_draft: The generated draft (editable by human)
      - status: Current workflow status


## Part 3: Initialize the LLM


```python
# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

print("LLM initialized: gpt-4o-mini")
```

    LLM initialized: gpt-4o-mini


## Part 4: Create the Workflow Nodes

Our workflow has three nodes:

1. **`generate_draft`**: Uses the LLM to create an email draft
2. **`human_review`**: Pauses execution with `interrupt()`, allowing human review and editing
3. **`send_email`**: Simulates sending the email

### How `interrupt()` Works

The `interrupt()` function is key to human-in-the-loop:
- When called, execution pauses immediately
- The interrupt payload is returned to the caller (for display/context)
- State is saved via the checkpointer
- When resumed with `Command(resume=<value>)`, the `<value>` is **returned by `interrupt()`**
- The node can then use this returned value to update state accordingly


```python
def generate_draft(state: EmailAgentState) -> dict:
    """
    Generates an email draft based on the user's request.
    
    This node uses the LLM to create a professional email draft
    that the human can later review and edit.
    """
    request = state["request"]
    
    print(f"Generating email draft for request: {request[:50]}...")
    
    system_prompt = """You are a professional email writing assistant.
    
Write a clear, professional email based on the user's request.
Include an appropriate subject line, greeting, body, and sign-off.
Keep the tone professional but friendly.

Format the output as:
Subject: [subject line]

[email body]
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Write an email for: {request}")
    ]
    
    response = llm.invoke(messages)
    
    print("Draft generated successfully!")
    
    return {
        "email_draft": response.content,
        "status": "pending_review"
    }


print("generate_draft node created!")
```

    generate_draft node created!



```python
def human_review(state: EmailAgentState) -> dict:
    """
    Pauses for human review and potential editing of the email draft.
    
    This node implements the HITL interrupt. When execution reaches this point:
    1. The interrupt() function pauses the workflow and returns control to the caller
    2. A human can review the draft and resume with Command(resume=<value>)
    3. The value passed to Command(resume=...) is returned by interrupt()
    """
    print("\n" + "=" * 60)
    print("HUMAN REVIEW REQUIRED")
    print("=" * 60)
    print("\nCurrent email draft:")
    print("-" * 40)
    print(state["email_draft"])
    print("-" * 40)
    
    # This interrupt pauses execution and returns control to the caller
    # When resumed with Command(resume=<value>), the value is returned here
    human_input = interrupt({
        "message": "Please review the email draft. You can edit it before sending.",
        "current_draft": state["email_draft"],
    })
    
    # human_input contains whatever was passed to Command(resume=...)
    # If it's a string, treat it as the edited draft
    # If it's True (from Command(resume=True)), keep the original draft
    print("\nHuman review complete. Proceeding with the email.")
    
    if isinstance(human_input, str):
        # Human provided an edited draft
        return {"email_draft": human_input, "status": "reviewed"}
    else:
        # Human approved as-is (Command(resume=True))
        return {"status": "reviewed"}


print("human_review node created!")
```

    human_review node created!



```python
def send_email(state: EmailAgentState) -> dict:
    """
    Simulates sending the email.
    
    In a production system, this would integrate with an email API
    (e.g., SendGrid, AWS SES, Gmail API).
    
    This node only executes AFTER human review, ensuring the human
    has had a chance to review and edit the draft.
    """
    print("\n" + "=" * 60)
    print("SENDING EMAIL")
    print("=" * 60)
    print("\nFinal email being sent:")
    print("-" * 40)
    print(state["email_draft"])
    print("-" * 40)
    print("\nEmail sent successfully!")
    
    return {"status": "sent"}


print("send_email node created!")
```

    send_email node created!


## Part 5: Build the Graph with Checkpointing

The **checkpointer** is required for human-in-the-loop because:
1. State must be persisted when the interrupt pauses execution
2. When resumed, the workflow restores from saved state
3. State updates from the human are applied correctly

We use `MemorySaver` here (in-memory). For production, use `SqliteSaver` or `PostgresSaver`.


```python
# Create the state graph
workflow = StateGraph(EmailAgentState)

# Add nodes to the graph
workflow.add_node("generate_draft", generate_draft)
workflow.add_node("human_review", human_review)
workflow.add_node("send_email", send_email)

# Define the edges (linear flow)
workflow.add_edge(START, "generate_draft")
workflow.add_edge("generate_draft", "human_review")
workflow.add_edge("human_review", "send_email")
workflow.add_edge("send_email", END)

# Create the checkpointer (required for HITL)
checkpointer = MemorySaver()

# Compile the graph with the checkpointer
app = workflow.compile(checkpointer=checkpointer)

print("Graph compiled with checkpointing!")
print("\nWorkflow structure:")
print("  START --> generate_draft --> human_review (INTERRUPT) --> send_email --> END")
```

    Graph compiled with checkpointing!
    
    Workflow structure:
      START --> generate_draft --> human_review (INTERRUPT) --> send_email --> END


### Visualize the Graph (Optional)


```python
# Try to visualize the graph
try:
    from IPython.display import Image, display
    display(Image(app.get_graph().draw_mermaid_png()))
except Exception as e:
    print(f"Visualization not available: {e}")
    print("\nGraph structure: START -> generate_draft -> human_review -> send_email -> END")
```


    
![png](3_8_implement_a_human_in_the_loop_files/3_8_implement_a_human_in_the_loop_17_0.png)
    


## Part 6: Run the Workflow - Initial Execution

The workflow will generate a draft and pause at the `human_review` node. We must provide a `thread_id` to uniquely identify this execution for later resumption.


```python
# Define our email request
email_request = "Write a professional email to my manager requesting time off next Friday for a medical appointment."

print("Email Request:")
print(f"  {email_request}")
print("\n" + "=" * 60)
print("PHASE 1: Starting workflow (will pause for human review)")
print("=" * 60)

# Configuration with thread_id for state tracking
config = {"configurable": {"thread_id": "email-session-1"}}

# Initial state
initial_state = {
    "request": email_request,
    "email_draft": "",
    "status": "drafting"
}

# Invoke the graph - it will pause at the interrupt
result = app.invoke(initial_state, config)

print("\n" + "=" * 60)
print("Workflow paused for human review!")
print("=" * 60)
```

    Email Request:
      Write a professional email to my manager requesting time off next Friday for a medical appointment.
    
    ============================================================
    PHASE 1: Starting workflow (will pause for human review)
    ============================================================
    Generating email draft for request: Write a professional email to my manager requestin...
    Draft generated successfully!
    
    ============================================================
    HUMAN REVIEW REQUIRED
    ============================================================
    
    Current email draft:
    ----------------------------------------
    Subject: Request for Time Off Next Friday
    
    Dear [Manager's Name],
    
    I hope this message finds you well. I am writing to formally request time off next Friday, [insert date], due to a scheduled medical appointment. 
    
    I will ensure that all my responsibilities are managed and that any pending tasks are completed before my absence. Please let me know if you need any further information or if there are forms I should fill out to formalize this request.
    
    Thank you for your understanding. I appreciate your support.
    
    Best regards,
    
    [Your Name]  
    [Your Job Title]  
    [Your Contact Information]  
    ----------------------------------------
    
    ============================================================
    Workflow paused for human review!
    ============================================================


## Part 7: Inspect the Interrupt

When paused, the result contains interrupt information including the payload we passed to `interrupt()`.


```python
print("INSPECTING PAUSED STATE")
print("=" * 60)

# Check current state values
print("\nCurrent State:")
print(f"  Request: {result['request'][:50]}...")
print(f"  Status: {result['status']}")
print(f"  Draft length: {len(result.get('email_draft', ''))} characters")

# Check interrupt information
if '__interrupt__' in result:
    print("\nInterrupt Information:")
    for interrupt_info in result['__interrupt__']:
        interrupt_value = interrupt_info.value
        print(f"  Message: {interrupt_value.get('message')}")

print("\n" + "=" * 60)
print("You can now review the draft and decide how to proceed.")
print("=" * 60)
```

    INSPECTING PAUSED STATE
    ============================================================
    
    Current State:
      Request: Write a professional email to my manager requestin...
      Status: pending_review
      Draft length: 591 characters
    
    Interrupt Information:
      Message: Please review the email draft. You can edit it before sending.
    
    ============================================================
    You can now review the draft and decide how to proceed.
    ============================================================


## Part 8: Review the Draft


```python
# Display the current draft for review
print("CURRENT EMAIL DRAFT FOR REVIEW")
print("=" * 60)
print()

current_draft = result.get('email_draft', '')
print(current_draft)

print()
print("=" * 60)
print("\nReview options:")
print("  1. Accept as-is: Use Command(resume=True)")
print("  2. Edit the draft: Use Command(resume='your edited version')")
```

    CURRENT EMAIL DRAFT FOR REVIEW
    ============================================================
    
    Subject: Request for Time Off Next Friday
    
    Dear [Manager's Name],
    
    I hope this message finds you well. I am writing to formally request time off next Friday, [insert date], due to a scheduled medical appointment. 
    
    I will ensure that all my responsibilities are managed and that any pending tasks are completed before my absence. Please let me know if you need any further information or if there are forms I should fill out to formalize this request.
    
    Thank you for your understanding. I appreciate your support.
    
    Best regards,
    
    [Your Name]  
    [Your Job Title]  
    [Your Contact Information]  
    
    ============================================================
    
    Review options:
      1. Accept as-is: Use Command(resume=True)
      2. Edit the draft: Use Command(resume='your edited version')


## Part 9: Resume with Human Edits

Use `Command(resume=<value>)` to pass a value back to the `interrupt()` call. The value is returned by `interrupt()`, and the node can use it to update state.


```python
# Create an edited version of the email
edited_draft = """Subject: Time Off Request - Friday, [Date]

Hi [Manager's Name],

I am writing to request time off next Friday for a medical appointment scheduled at 10:00 AM. I expect to be out for approximately half the day.

I will ensure all urgent tasks are completed before I leave and will be available by phone for any critical matters.

Please let me know if you need any additional information.

Thank you,
[Your Name]"""

print("HUMAN EDIT: Modified email draft")
print("=" * 60)
print()
print(edited_draft)
print()
print("=" * 60)
```

    HUMAN EDIT: Modified email draft
    ============================================================
    
    Subject: Time Off Request - Friday, [Date]
    
    Hi [Manager's Name],
    
    I am writing to request time off next Friday for a medical appointment scheduled at 10:00 AM. I expect to be out for approximately half the day.
    
    I will ensure all urgent tasks are completed before I leave and will be available by phone for any critical matters.
    
    Please let me know if you need any additional information.
    
    Thank you,
    [Your Name]
    
    ============================================================



```python
print("PHASE 2: Resuming workflow with human edits")
print("=" * 60)

# Resume the workflow with our edited draft
# Command(resume=<value>) passes the value back to the interrupt() call and continues execution
# The state update is applied, and the workflow continues past the interrupt point
final_result = app.invoke(
    Command(resume=edited_draft),
    config  # Same config with same thread_id to resume the right session
)

print("\n" + "=" * 60)
print("WORKFLOW COMPLETE")
print("=" * 60)
print(f"\nFinal Status: {final_result['status']}")
```

    PHASE 2: Resuming workflow with human edits
    ============================================================
    
    ============================================================
    HUMAN REVIEW REQUIRED
    ============================================================
    
    Current email draft:
    ----------------------------------------
    Subject: Request for Time Off Next Friday
    
    Dear [Manager's Name],
    
    I hope this message finds you well. I am writing to formally request time off next Friday, [insert date], due to a scheduled medical appointment. 
    
    I will ensure that all my responsibilities are managed and that any pending tasks are completed before my absence. Please let me know if you need any further information or if there are forms I should fill out to formalize this request.
    
    Thank you for your understanding. I appreciate your support.
    
    Best regards,
    
    [Your Name]  
    [Your Job Title]  
    [Your Contact Information]  
    ----------------------------------------
    
    Human review complete. Proceeding with the email.
    
    ============================================================
    SENDING EMAIL
    ============================================================
    
    Final email being sent:
    ----------------------------------------
    Subject: Time Off Request - Friday, [Date]
    
    Hi [Manager's Name],
    
    I am writing to request time off next Friday for a medical appointment scheduled at 10:00 AM. I expect to be out for approximately half the day.
    
    I will ensure all urgent tasks are completed before I leave and will be available by phone for any critical matters.
    
    Please let me know if you need any additional information.
    
    Thank you,
    [Your Name]
    ----------------------------------------
    
    Email sent successfully!
    
    ============================================================
    WORKFLOW COMPLETE
    ============================================================
    
    Final Status: sent


## Part 10: Alternative - Resume Without Changes

If the draft is good as-is, use `Command(resume=True)` to continue without modifications.


```python
# New email request
email_request_2 = "Write a thank you email to a colleague who helped me with a project presentation."

print("NEW EMAIL REQUEST:")
print(f"  {email_request_2}")
print("\n" + "=" * 60)
print("Starting new workflow session...")
print("=" * 60)

# New session with different thread_id
config_2 = {"configurable": {"thread_id": "email-session-2"}}

initial_state_2 = {
    "request": email_request_2,
    "email_draft": "",
    "status": "drafting"
}

# Start the workflow
result_2 = app.invoke(initial_state_2, config_2)

print("\nWorkflow paused. Draft generated:")
print("-" * 40)
print(result_2.get('email_draft', '')[:500])
print("-" * 40)
```

    NEW EMAIL REQUEST:
      Write a thank you email to a colleague who helped me with a project presentation.
    
    ============================================================
    Starting new workflow session...
    ============================================================
    Generating email draft for request: Write a thank you email to a colleague who helped ...
    Draft generated successfully!
    
    ============================================================
    HUMAN REVIEW REQUIRED
    ============================================================
    
    Current email draft:
    ----------------------------------------
    Subject: Thank You for Your Support!
    
    Hi [Colleague's Name],
    
    I hope this message finds you well. I wanted to take a moment to express my heartfelt thanks for your assistance with the project presentation. Your insights and suggestions were invaluable, and I truly appreciate the time and effort you dedicated to helping me prepare.
    
    The presentation was a success, and I couldn’t have done it without your support. It’s a pleasure to work with someone as knowledgeable and collaborative as you.
    
    Thanks once again for your help! I look forward to our continued collaboration on future projects.
    
    Best regards,
    
    [Your Name]  
    [Your Job Title]  
    [Your Contact Information]  
    ----------------------------------------
    
    Workflow paused. Draft generated:
    ----------------------------------------
    Subject: Thank You for Your Support!
    
    Hi [Colleague's Name],
    
    I hope this message finds you well. I wanted to take a moment to express my heartfelt thanks for your assistance with the project presentation. Your insights and suggestions were invaluable, and I truly appreciate the time and effort you dedicated to helping me prepare.
    
    The presentation was a success, and I couldn’t have done it without your support. It’s a pleasure to work with someone as knowledgeable and collaborative as you.
    
    Tha
    ----------------------------------------



```python
print("APPROVING DRAFT AS-IS")
print("=" * 60)

# Resume without changes - the draft looks good!
final_result_2 = app.invoke(
    Command(resume=True),  # No updates, just resume
    config_2
)

print(f"\nFinal Status: {final_result_2['status']}")
```

    APPROVING DRAFT AS-IS
    ============================================================
    
    ============================================================
    HUMAN REVIEW REQUIRED
    ============================================================
    
    Current email draft:
    ----------------------------------------
    Subject: Thank You for Your Support!
    
    Hi [Colleague's Name],
    
    I hope this message finds you well. I wanted to take a moment to express my heartfelt thanks for your assistance with the project presentation. Your insights and suggestions were invaluable, and I truly appreciate the time and effort you dedicated to helping me prepare.
    
    The presentation was a success, and I couldn’t have done it without your support. It’s a pleasure to work with someone as knowledgeable and collaborative as you.
    
    Thanks once again for your help! I look forward to our continued collaboration on future projects.
    
    Best regards,
    
    [Your Name]  
    [Your Job Title]  
    [Your Contact Information]  
    ----------------------------------------
    
    Human review complete. Proceeding with the email.
    
    ============================================================
    SENDING EMAIL
    ============================================================
    
    Final email being sent:
    ----------------------------------------
    Subject: Thank You for Your Support!
    
    Hi [Colleague's Name],
    
    I hope this message finds you well. I wanted to take a moment to express my heartfelt thanks for your assistance with the project presentation. Your insights and suggestions were invaluable, and I truly appreciate the time and effort you dedicated to helping me prepare.
    
    The presentation was a success, and I couldn’t have done it without your support. It’s a pleasure to work with someone as knowledgeable and collaborative as you.
    
    Thanks once again for your help! I look forward to our continued collaboration on future projects.
    
    Best regards,
    
    [Your Name]  
    [Your Job Title]  
    [Your Contact Information]  
    ----------------------------------------
    
    Email sent successfully!
    
    Final Status: sent


## Part 11: Using `interrupt_before` for Pre-Node Interrupts

Instead of calling `interrupt()` inside a node, you can use `interrupt_before` during graph compilation to pause **before** a specified node runs.

This is useful when:
- You want to review state before a critical action
- You don't want to modify node code to add interrupts


```python
# Simplified node without interrupt (we'll use interrupt_before instead)
def human_review_simple(state: EmailAgentState) -> dict:
    """
    A simpler human review node without an embedded interrupt.
    The interrupt will be configured at the graph level.
    """
    print("Human review node executed.")
    return {"status": "reviewed"}


# Create a new workflow
workflow_v2 = StateGraph(EmailAgentState)

workflow_v2.add_node("generate_draft", generate_draft)
workflow_v2.add_node("human_review", human_review_simple)
workflow_v2.add_node("send_email", send_email)

workflow_v2.add_edge(START, "generate_draft")
workflow_v2.add_edge("generate_draft", "human_review")
workflow_v2.add_edge("human_review", "send_email")
workflow_v2.add_edge("send_email", END)

# Compile with interrupt_before - pauses BEFORE send_email runs
checkpointer_v2 = MemorySaver()
app_v2 = workflow_v2.compile(
    checkpointer=checkpointer_v2,
    interrupt_before=["send_email"]  # Pause before this node
)

print("Graph compiled with interrupt_before!")
print("\nWorkflow will pause BEFORE send_email node.")
```

    Graph compiled with interrupt_before!
    
    Workflow will pause BEFORE send_email node.



```python
# Test the interrupt_before workflow
email_request_3 = "Write a brief email to schedule a team meeting for Monday at 2 PM."

print(f"Request: {email_request_3}")
print("\n" + "=" * 60)
print("Running workflow with interrupt_before...")
print("=" * 60)

config_3 = {"configurable": {"thread_id": "email-session-3"}}

initial_state_3 = {
    "request": email_request_3,
    "email_draft": "",
    "status": "drafting"
}

result_3 = app_v2.invoke(initial_state_3, config_3)

print("\n" + "=" * 60)
print("Paused before send_email node!")
print("=" * 60)
print(f"\nStatus: {result_3['status']}")
print(f"Draft preview: {result_3['email_draft'][:200]}...")
```

    Request: Write a brief email to schedule a team meeting for Monday at 2 PM.
    
    ============================================================
    Running workflow with interrupt_before...
    ============================================================
    Generating email draft for request: Write a brief email to schedule a team meeting for...
    Draft generated successfully!
    Human review node executed.
    
    ============================================================
    Paused before send_email node!
    ============================================================
    
    Status: reviewed
    Draft preview: Subject: Scheduling Team Meeting for Monday at 2 PM
    
    Dear Team,
    
    I hope this message finds you well. I would like to schedule a team meeting for this coming Monday at 2 PM. Please let me know if you a...



```python
# Resume with an edited draft
quick_edit = """Subject: Team Meeting - Monday 2 PM

Hi Team,

Let's meet Monday at 2 PM in Conference Room A to discuss project updates.

Best,
[Your Name]"""

print("Resuming with edited draft...")
print("=" * 60)

final_result_3 = app_v2.invoke(
    Command(update={"email_draft": quick_edit}),
    config_3
)

print(f"\nFinal Status: {final_result_3['status']}")
```

    Resuming with edited draft...
    ============================================================
    
    ============================================================
    SENDING EMAIL
    ============================================================
    
    Final email being sent:
    ----------------------------------------
    Subject: Team Meeting - Monday 2 PM
    
    Hi Team,
    
    Let's meet Monday at 2 PM in Conference Room A to discuss project updates.
    
    Best,
    [Your Name]
    ----------------------------------------
    
    Email sent successfully!
    
    Final Status: sent

```

---

