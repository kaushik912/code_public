# LCEL Simple Sequential Chain
- Feeding output of one chain to another
- In **Simple** Sequential Chain, we only have one input to another chain.
- Here first we setup two prompt templates
    - one is a title creator named `title_prompt`. 
        - Here title is generated based on a `topic` specified by user.
    - another is a speech creator named `speech_prompt`. 
        - The speech is generated based on the `title` generated in previous step.
- Now image we invoke our chains using: 
    - `first_chain = title_prompt | llm`
    - `second_chain= speech_prompt | llm`
- But now I want the output of first chain to go as an input to second chain
    - So we modify first_chain to extract the title and store that instead in `first_chain`
        - `first_chain = title_prompt | llm | StrOutputParser() | (lambda title: (st.write(title),title)[1])`
        - Note, we are also writing the title to the streamlit.
        - This is achieved by using lambda function and a tuple.
- finally we setup a final chain that takes input from first_chain and feeds to second chain.
    `final_chain = first_chain | second_chain`
- With this, we need to invoke the argument to first_chain and rest of the flow will happen
    - `final_chain.invoke({"topic":topic})`
    - `topic` comes from the user input.
- This is a very useful example of chaining results.

```python
import os
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm=ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)
title_prompt = PromptTemplate(
    input_variables=["topic"],
    template="""You are an experienced speech writer.
    You need to craft an impactful title for a speech 
    on the following topic: {topic}
    Answer exactly with one title.	
    """
)

speech_prompt = PromptTemplate(
    input_variables=["title"],
    template="""You need to write a powerful speech of 350 words
     for the following title: {title}
    """
)

first_chain = title_prompt | llm | StrOutputParser() | (lambda title: (st.write(title),title)[1])
second_chain = speech_prompt | llm
final_chain = first_chain | (lambda title: {"title": title}) | second_chain

st.title("Speech Generator")

topic = st.text_input("Enter the topic:")

if topic:
    response = final_chain.invoke({"topic":topic})
    st.write(response.content)
```