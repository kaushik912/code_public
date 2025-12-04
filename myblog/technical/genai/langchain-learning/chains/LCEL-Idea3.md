## LCEL Sequential Chain
- In Sequential Chain, we can have multiple inputs to the chain.
- In this example, we have two prompt templates : one for title generation and other for speech generation. 
- As usual, we can setup the initial chains as :
    - `first_chain = title_prompt | llm`
    - `second_chain = speech_prompt | llm`
- However, we also capture an additional input called `emotion`. This needs to be passed to the second chain i.e. speech_prompt

### Pass Two values
- So, we have to pass two values to the second chain, one for `emotion` and another being `title` from the `first_chain`.
- So the final chain looks like :
    - `final_chain = first_chain | (lambda title:{"title": title,"emotion": emotion}) | second_chain`
    - We are using the lambda to pass a dictionary(key/value pair) to the second_chain
    - All chains expect a dictionary as input.
- Finally we invoke the final_chain

```python
import os
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser

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
    input_variables=["title", "emotion"],
    template="""You need to write a powerful {emotion} speech of 350 words
     for the following title: {title}  
     Format the output with 2 keys: 'title','speech' and fill them
     with the respective values  
    """
)

first_chain = title_prompt | llm | StrOutputParser() | (lambda title: (st.write(title),title)[1])
second_chain = speech_prompt | llm | JsonOutputParser()
final_chain = first_chain | (lambda title:{"title": title,"emotion": emotion}) | second_chain

st.title("Speech Generator")

topic = st.text_input("Enter the topic:")
emotion = st.text_input("Enter the emotion:")

if topic and emotion:
    response = final_chain.invoke({"topic":topic})
    st.write(response)
    st.write(response['title'])


```

### Quick note on Lamdbas
- We are using lamdba to generate dict object in python based on chain response and user inputs.
- Below is an example of using lambdas to return dict object from values.
```python
import json

# External variables
name = "Alice"
age = 30
city = "Wonderland"

# Lambda that returns a dictionary (which can be JSON)
get_user_info = lambda: {
    "name": name,
    "age": age,
    "location": city
}

# Call the lambda and print as JSON
user_json = get_user_info()
print(json.dumps(user_json, indent=2))
```