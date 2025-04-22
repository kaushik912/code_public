## Open AI
```python
import os
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm=ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

question = input("Enter the question")
response = llm.invoke(question)
print(response.content)
```

## Mistral
We use `ChatOllama` instead of `ChatOpenAI`

```python
import os
from langchain_community.chat_models import ChatOllama

## The LLM piece is only changing 
llm=ChatOllama(model="mistral")

## Everything else remains same!

question = input("Enter the question")
response = llm.invoke(question)
print(response.content)

```

## Other examples 
```python
## Gemma
llm=ChatOllama(model="gemma:2b")
## Deekseek
llm=ChatOllama(model="deepseek-r1:8b")

```


## Streamlit
```python
##File: streamlit_demo.py
import os
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain import globals
globals.set_debug(True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm=ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

st.title("Ask Anything")

question = st.text_input("Enter the question:")

if question:
    response = llm.invoke(question)
    st.write(response.content)
```
- To run this , we need to run `streamlit run streamlit_demo.py` in the terminal
- We also need to install the dependencies.


# Streaming Response Example
- Streaming often improves responsiveness of the application.
- langchain has the `stream=True` parameter that can be used.
- Also, it provides a stream() method

```python
import os
from langchain_community.chat_models import ChatOllama

## The LLM piece 
llm=ChatOllama(model="gemma:2b",stream=True)

## Everything else remains same!

question = input("Enter the question")

# Step 3: Call the OpenAI model and stream the response
response = llm.stream(question)

# Choose whether to accumulate the response into a single string (False) or stream output (True)
stream_output = False  # Change this to False to accumulate into a string

# Approach 1: Accumulate into a string
if not stream_output:
    full_response = ""
    for chunk in response:
        full_response += chunk.content  # Accumulate content from each chunk
    print(full_response)

# Approach 2: Stream the output as it arrives
else:
    for chunk in response:
        print(chunk.content, end="", flush=True)  # Print content immediately on the same line


```