import subprocess
import openai
import re
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
        return VertexAI(project="projectid", location="loc1", model="gemini-1.5-flash-002")

llm = get_model(isOllama)

import subprocess
import os

def run_maven_install(project_dir):
    """Runs `mvn install` inside a given project directory and checks for errors."""
    if not os.path.isdir(project_dir):
        return "Error: The specified directory does not exist."

    try:
        result = subprocess.run(
            ["mvn", "install"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return "Maven build successful!\n" + result.stdout
        else:
            maven_log = result.stdout+ result.stderr
            print("\nExtracting error message...")
            error_message = extract_maven_error(maven_log)
            pom_file_path = os.path.join(project_dir, "pom.xml")
            
            if os.path.exists(pom_file_path):
                with open(pom_file_path, "r") as f:
                    current_pom = f.read()
            else:
                current_pom = "<Error: pom.xml not found>"

            # Call GPT to fix the pom.xml
            fixed_pom = get_gpt_fix(error_message, current_pom)

            # Save the fixed pom.xml
            with open("generated_project/fix_pom_xml.md", "w") as f:
                f.write(fixed_pom)

            return f"Maven build failed. Fixed pom.xml generated:\n{fixed_pom}"

    except Exception as e:
        return f"Error while running Maven: {str(e)}"


def extract_maven_error(log):
    """Extracts relevant Maven error messages."""
    error_lines = []
    capturing = False

    for line in log.split("\n"):
        if "ERROR" in line or "[ERROR]" in line:
            capturing = True
        if capturing:
            error_lines.append(line)

    return "\n".join(error_lines[-15:])  # Get last 15 error lines

def get_gpt_fix(error_message,current_pom):
    """Uses AI to analyze and fix Maven errors."""

    prompt = f"""
    I encountered the following Maven build error:

    ```
    {error_message}
    ```

    Here is my current `pom.xml` file:

    ```xml
    {current_pom}
    ```

    Please analyze this error and generate a corrected `pom.xml` that fixes the issue. 
    Provide only the final corrected `pom.xml` without any explanations.
    Also, use the following suggestions for fixing pom.xml:
     
    problem1:
     <!-- mysql dependency issue in pom.xml, incorrect groupId and/or version missing-->
     dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
    </dependency>
    solution1:
    <!-- mysql dependency fix with groupId and artifactId -->
    <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.33</version>
    </dependency>
   
    """

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
            result= (response.content)  # For Ollama
    else:
            result= (response)  # For Gemini/GPT
    return result

def main():
    print("Running Maven install...")
    project_path = "codev1"
    result = run_maven_install(project_path)
    print(result)
    


if __name__ == "__main__":
    main()
