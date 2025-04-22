```python
import streamlit as st
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
import re

llm =ChatOllama(model="deepseek-r1:8b")
embed_model="deepseek-r1:8b"
# deepseek-r1:8b can also generate embeddings

loader=TextLoader("product-data.txt")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)

chunks = text_splitter.split_documents(documents)

embeddings = OllamaEmbeddings(model=embed_model)
vector_store=Chroma.from_documents(chunks,embeddings)
retriever = vector_store.as_retriever()

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an assistant for answering questions.
    Use the provided context to respond.If the answer isn't clear, acknowledge that you don't know. 
    {context}
    """),
    MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ]
)

history_aware_retriever = create_history_aware_retriever(llm, retriever,prompt_template)
qa_chain=create_stuff_documents_chain(llm,prompt_template)
rag_chain=create_retrieval_chain(history_aware_retriever,qa_chain)

history_for_chain=StreamlitChatMessageHistory()

chain_with_history=RunnableWithMessageHistory(
    rag_chain,
    lambda session_id:history_for_chain,
    input_messages_key="input",
    history_messages_key="chat_history"
)

st.write("Chat with Document")
question= st.text_input("Your Question")

if question:
    response = chain_with_history.invoke({"input": question},{"configurable":{"session_id":"abc124"}})
    final_response = re.sub(r'<think>.*?</think>','',response['answer'],flags=re.DOTALL).strip()
    st.write(final_response)


```