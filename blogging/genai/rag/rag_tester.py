import os
import re
import json

def load_json(file_path):
    """Loads and reads a JSON file containing Q&A."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        return None

# Example usage
# pwd = os.getcwd()
# file_path = pwd + "/organization_rag/rag-data/ladakh-questions.json"
# qa_data = load_json(file_path)

# if qa_data:
#     for key, value in qa_data.items():
#         print(f"Q{key}: {value['question']}")
#         print(f"A{key}: {value['answer']}\n")
