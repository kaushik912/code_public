# 🧭 LCEL LangChain Demo — *Travel Guide Recommendation App*

This demo shows how to use **LangChain Expression Language (LCEL)** syntax to build a **Travel Guide Recommendation** app using **Streamlit** and **LangChain**.

---

## 🧩 Concept Overview

LCEL allows you to **connect components** (like prompt templates and LLMs) using a **pipeline syntax**:

```python
chain = prompt_template | llm
```

> 💡 **Key Idea:**
> LCEL lets you *chain* multiple LangChain components seamlessly — no need to call them manually one after another.

---

## 🗂️ Input Data for the Model

When calling `llm.invoke()`, you must provide **a JSON object** with values for all input variables defined in your prompt template.

```json
{
    "city": "Paris",
    "month": "June",
    "language": "French",
    "budget": "Medium"
}
```

> ⚠️ **Important:**
> The keys in the JSON must exactly match the variable names in the prompt (`city`, `month`, `language`, `budget`).

These values come from **user inputs** in the Streamlit interface.

---

## 💻 Full Python Example

Here’s the complete demo code:

```python
import os
from langchain_openai import ChatOpenAI
import streamlit as st
from langchain.prompts import PromptTemplate

# 1️⃣ Load API key and initialize LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

# 2️⃣ Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["city", "month", "language", "budget"],
    template="""Welcome to the {city} travel guide!
If you're visiting in {month}, here's what you can do:
1. Must-visit attractions.
2. Local cuisine you must try.
3. Useful phrases in {language}.
4. Tips for traveling on a {budget} budget.
Enjoy your trip!
"""
)

# 3️⃣ Streamlit user interface
st.title("🌍 Travel Guide")

city = st.text_input("Enter the city:")
month = st.text_input("Enter the month of travel:")
language = st.text_input("Enter the language:")
budget = st.selectbox("Travel Budget", ["Low", "Medium", "High"])

# 4️⃣ Build the LCEL chain
chain = prompt_template | llm

# 5️⃣ Invoke the chain when inputs are ready
if city and month and language and budget:
    response = chain.invoke({
        "city": city,
        "month": month,
        "language": language,
        "budget": budget
    })
    st.write(response.content)
```

---

## 🧠 How It Works

1. **PromptTemplate** defines how your message will look — with placeholders for user inputs.
2. **ChatOpenAI** is your LLM model (e.g., `gpt-4o`).
3. **LCEL Chain (`|`)** connects them, creating a pipeline.
4. **User Inputs (Streamlit)** feed into the template dynamically.
5. **LLM Response** is displayed as a personalized travel guide.

> 💬 **Example Output:**
>
> “Welcome to Paris!
> In June, visit the Eiffel Tower and Montmartre. Try French pastries like croissants.
> Learn basic phrases such as *Bonjour* and *Merci!*...”

---

## 🚀 Takeaway

* LCEL simplifies workflow chaining — no need to manage calls manually.
* JSON input must match the prompt variables.
* Perfect for dynamic, user-driven apps with **Streamlit + LangChain**.

