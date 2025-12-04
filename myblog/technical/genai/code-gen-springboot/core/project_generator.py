import os
import sys
import base64
import zipfile
import requests
from langchain_ollama import ChatOllama
from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate

isOllama=False

def get_model(isOllama: bool):
    """
    Returns an LLM instance based on the isOllama flag.

    Args:
    isOllama (bool): If True, returns an Ollama model; otherwise, returns a Gemini model.

    Returns:
    ChatOllama or VertexAI: The appropriate LLM instance.
    """
    if isOllama:
        model_name = "qwen2.5-coder:3b"
        return ChatOllama(model=model_name, temperature=0.8)
    else:
        return VertexAI(project="projectid", location="location1", model="gemini-1.5-flash-002")

llm = get_model(isOllama)

def generate_spring_boot_project(requirements, output_dir="generated_project"):
    
    try:
        response = llm.invoke(requirements)
        if hasattr(response, "content"):
            result= (response.content)  # For Ollama
        else:
            result= (response)  # For Gemini/GPT
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "SpringBootApplicationOutput.md")
        with open(output_file, "w") as f:
            f.write(result)
        print(f"Spring Boot code saved to {output_file}")

    except Exception as e:
        print(f"❌ Error generating project: {e}")
        sys.exit(1)

if __name__ == "__main__":
    requirements = """
    Generate a complete Spring Boot application that manages employees with a REST API. The application should include:
    A Employee entity with fields: id, name, department, and salary.
    A Controller with endpoints to create, read, update, and delete employees (/employees).
    A Service layer to handle business logic.
    A Repository interface using Spring Data JPA.
    Use MySQL as the database and configure application.properties.
    Return appropriate HTTP responses for success and failure cases.
    A main class for a Spring Boot application.
    Include Swagger documentation."
    """
    generate_spring_boot_project(requirements)
