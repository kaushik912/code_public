## Simple Prompt Template Example

- This prompt is for Travel agent
- We use `PromptTemplate`, use {} as placeholders and then use the .format() method to inject the values.
- This is similar to f-prompt in python.
- PromptTemplate encourages re-usability, for example , we could do `template.format(name="Bob")` and again with different name. So use it in langchain wherever possible.

```python
import os
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain.prompts import PromptTemplate

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm=ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)
prompt_template = PromptTemplate(
    input_variables=["country","no_of_paras","language"],
    template="""You are an expert in traditional cuisines.
    You provide information about a specific dish from a specific country.
    Avoid giving information about fictional places. If the country is fictional
    or non-existent answer: I don't know.
    Answer the question: What is the traditional cuisine of {country}?
    Answer in {no_of_paras} short paras in {language}
    """
)

st.title("Cuisine Info")

country = st.text_input("Enter the country:")
no_of_paras = st.number_input("Enter the number of paras",min_value=1,max_value=5)
language = st.text_input("Enter the language:")

if country:
    response = llm.invoke(prompt_template.format(country=country,
                                                 no_of_paras=no_of_paras,
                                                 language=language
                                                 ))
    st.write(response.content)
```

## Interview tips Generator 

- Sample Prompt Template for Interview tips generation

```python
prompt = PromptTemplate(
    input_variables=['company', 'position',
                     'strengths', 'weaknesses'],
    template="""You are a career coach. Provide tailored interview tips for the
    position of {position} at {company}.
    Highlight your strengths in {strengths} and prepare for questions
    about your weaknesses such as {weaknesses}.""")
```

## Favorite Topic 
- Use this to inject topic and a question and ask AI to answer that question.
```python
prompt_template = PromptTemplate(
    input_variables=["topic","question"],
    template="""
    You are a helpful assistant with expertise in {topic}. 
    Answer the following question concisely:
    Question: {question}
    """
)
```