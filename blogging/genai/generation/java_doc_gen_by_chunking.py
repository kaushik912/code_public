import os

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
import sys
model_name="qwen2.5-coder:3b"

"""
Code to generate documentation for a java project using generativeAI
tag:genai
"""

def read_file_chunks(file_path, chunk_size=4000):
    """
    Reads a file and splits its content into manageable chunks.

    Args:
        file_path (str): Path to the file.
        chunk_size (int): Maximum size of each chunk in characters.

    Returns:
        list: List of chunks.
    """
    try:
        with open(file_path, "r") as file:
            content = file.read()
            return [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []


def scan_directory(directory):
    """
    Recursively scans a directory for Java files.

    Args:
        directory (str): Path to the directory.

    Returns:
        list: List of Java file paths.
    """
    java_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files


def summarize_java_file(file_path):
    """
    Uses AI to summarize a Java file's content.

    Args:
        file_path (str): Path to the Java file.

    Returns:
        str: Summary of the file's content.
    """
    chunks = read_file_chunks(file_path)
    summary = []

    for chunk in chunks:
        llm = ChatOllama(model=model_name, temperature=0.8)
        prompt = PromptTemplate(
            input_variables=["chunk"],
            template="""
               Summarize the following Java code and explain its purpose, main functionality, and any notable features:\n\n{chunk}
                       """
        )
        try:
            response = llm.invoke(prompt.format(chunk=chunk))
            summary.append(response.content)
        except Exception as e:
            print(f"Error summarizing file {file_path}: {e}")
            sys.exit(1)

    return "\n".join(summary)


def analyze_java_files(java_files):
    """
    Analyzes Java files to generate summaries and identify associations.

    Args:
        java_files (list): List of Java file paths.

    Returns:
        tuple: Summaries and associations.
    """
    summaries = {}

    for file_path in java_files:
        print(f"Analyzing {file_path}...")
        summary = summarize_java_file(file_path)
        summaries[file_path] = summary

    return summaries


def generate_documentation(directory):
    """
    Generates documentation for a Java application.

    Args:
        directory (str): Path to the Java application directory.

    Returns:
        str: Generated documentation.
    """
    java_files = scan_directory(directory)
    summaries = analyze_java_files(java_files)

    # Create documentation
    documentation = ["# Java Application Documentation"]
    documentation.append("\n## Main Functionality and Key Features")
    documentation.append("This document summarizes the main functionality and key features of the application.")
    documentation.append("\n### File Summaries")

    for file, summary in summaries.items():
        documentation.append(f"\n#### {os.path.basename(file)}")
        documentation.append(summary)

    return "\n".join(documentation)


def main():
    directory = input("Enter the path to the Java application directory: ")

    if not os.path.exists(directory) or not os.path.isdir(directory):
        print("Invalid directory path.")
        return

    documentation = generate_documentation(directory)

    # Save the documentation to a file
    output_file = os.path.join(directory, "Documentation_ollama.md")
    with open(output_file, "w") as file:
        file.write(documentation)

    print(f"Documentation has been generated and saved to {output_file}")


if __name__ == "__main__":
    main()
