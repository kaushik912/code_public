# 🧠 LangChain LLM Integration Guide

This guide demonstrates how to use various **LLM providers** (OpenAI, Mistral, Gemma, DeepSeek) with LangChain, and how to integrate them with **Streamlit** or use **streaming responses**.

---

## 🚀 1. Using OpenAI Models

### Code Example

```python
import os
from langchain_openai import ChatOpenAI

# Load your API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI LLM
llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

# Get user input and invoke the model
question = input("Enter the question: ")
response = llm.invoke(question)

# Print the model's response
print(response.content)
```

✅ **Key Points**

* Uses the `ChatOpenAI` class from `langchain_openai`.
* Model name: `"gpt-4o"`.
* Requires an environment variable `OPENAI_API_KEY`.

---

## 🌪️ 2. Using Mistral via ChatOllama

When switching to **Mistral**, only the model initialization changes.

### Code Example

```python
import os
from langchain_community.chat_models import ChatOllama

# Initialize Mistral model
llm = ChatOllama(model="mistral")

# The rest remains the same
question = input("Enter the question: ")
response = llm.invoke(question)
print(response.content)
```

✅ **Key Points**

* `ChatOllama` is used instead of `ChatOpenAI`.
* No API key required for local Ollama setup.

---

## 🧩 3. Other Model Examples

You can easily switch between models by changing the model name:

```python
# Gemma
llm = ChatOllama(model="gemma:2b")

# DeepSeek
llm = ChatOllama(model="deepseek-r1:8b")
```

✅ **Tip:**
You can experiment with various models supported by **Ollama** simply by updating the model name.

---

## 🖥️ 4. Streamlit Integration

Here’s how to build a simple Streamlit app that queries an LLM.

### File: `streamlit_demo.py`

```python
import os
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain import globals

# Enable debug logging
globals.set_debug(True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

st.title("Ask Anything")

question = st.text_input("Enter the question:")

if question:
    response = llm.invoke(question)
    st.write(response.content)
```

### 🧩 Run the App

```bash
streamlit run streamlit_demo.py
```

### 📦 Install Dependencies

Ensure Streamlit and LangChain packages are installed:

```bash
pip install streamlit langchain_openai
```

---

## ⚡ 5. Streaming Responses

Streaming provides **faster, incremental output** while the model generates text.

LangChain supports:

* `stream=True` (to enable streaming)
* `llm.stream()` (to handle streamed responses)

### Example

```python
import os
from langchain_community.chat_models import ChatOllama

# Initialize LLM with streaming enabled
llm = ChatOllama(model="gemma:2b", stream=True)

question = input("Enter the question: ")

# Stream the response
response = llm.stream(question)

# Choose output behavior
stream_output = False  # Set to True for real-time streaming

# Option 1: Accumulate full response
if not stream_output:
    full_response = ""
    for chunk in response:
        full_response += chunk.content
    print(full_response)

# Option 2: Stream response in real-time
else:
    for chunk in response:
        print(chunk.content, end="", flush=True)
```

✅ **Best Practices**

* Use streaming for chatbots or real-time UIs.
* For logs or debugging, accumulation is often easier.

---

### 🧭 Summary

| Model Provider | Class Used   | Example Model Name | Notes              |
| -------------- | ------------ | ------------------ | ------------------ |
| OpenAI         | `ChatOpenAI` | `"gpt-4o"`         | Requires API key   |
| Mistral        | `ChatOllama` | `"mistral"`        | Local inference    |
| Gemma          | `ChatOllama` | `"gemma:2b"`       | Smaller open model |
| DeepSeek       | `ChatOllama` | `"deepseek-r1:8b"` | Reasoning-focused  |


