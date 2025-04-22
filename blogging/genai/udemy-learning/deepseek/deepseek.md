# Key Features
- Uses advanced reasoning
- thinks before responding
- cost effective , 90% cheaper than OpenAI
- Open-Source and Deployable

# Why use it?
- Most of LLMs struggle with reasoning
- However, it "overthinks", say for simple tasks like 2+3
- Useful for AI agents and chatbots.
- Useful for Code Generation

## Local run
- Depending on your RAM, pick the model.
- We can use the 8B parameter or lower ones based on RAM.
- `ollama run deepseek-r1:7b`
- Ask a question like `what is AI`, it will generate the <think> tags as well as the response.
    - In this case of `what is AI`, it was straight-forward ,so <think> tags are empty.
    - In complex queries, it will also populate the <think> tag.

## Using Langchain
```python
from langchain_community.chat_models import ChatOllama
## The LLM piece is now changing to gemma
llm=ChatOllama(model="deepseek-r1:8b")

## Everything else remains same!

question = input("Enter the question")
response = llm.invoke(question)
print(response.content)

```

### Sample RAG Think Response
```
<think> Okay, so the user is asking about the features of the XYZ smartphone. From the context provided, I remember there's a previous response that lists the features as follows: 6.5-inch display, 128GB storage, 6GB RAM, 48MP camera, and a 4000mAh battery. The colors available are black, blue, and white.
I should structure this information clearly, maybe in bullet points for better readability. I'll start by listing each feature with its details, making sure to mention the display size, storage options, RAM, camera specs, battery capacity, and available colors.

Wait, I need to ensure that all the information is accurate based on the context. The user didn't ask for anything beyond the features, so I don't need to add extra info. Just present what's given clearly. </think>

The XYZ smartphone features:

A 6.5-inch display
128GB storage
6GB RAM
A 48MP camera
A 4000mAh battery
Available in black, blue, and white colors.
```

## Removing the think tag

We can use regex to remove the think tag as follows:
```python
response = llm.invoke(question)
final_response = re.sub(r'<think>.*?</think>','',response['answer'],flags=re.DOTALL).strip()
st.write(final_response)
```

