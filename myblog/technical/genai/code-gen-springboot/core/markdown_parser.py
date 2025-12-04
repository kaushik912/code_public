import os
import re

def extract_code_blocks(markdown_content, language):
    """Extracts code blocks of a specific language from markdown content."""
    return re.findall(rf"```{language}\n(.*?)```", markdown_content, re.DOTALL)

def determine_java_file_path(code):
    """Determines the correct file path for a Java class based on its package."""
    package_match = re.search(r'package\s+([\w.]+);', code)
    package_path = package_match.group(1).replace('.', '/') if package_match else "default"

    # First try finding a public class/interface/enum
    class_match = re.search(r'public\s+(class|interface|enum)\s+(\w+)', code)
    
    # If no public class is found, look for any class/interface/enum declaration
    if not class_match:
        class_match = re.search(r'(class|interface|enum)\s+(\w+)', code)
    
    class_name = class_match.group(2) if class_match else "Unknown"
    file_name = f"{class_name}.java"
    
    # Check if it's a test class (ends with "Test" or "Tests")
    if class_name.endswith("Test") or class_name.endswith("Tests"):
        return os.path.join("src/test/java", package_path, file_name)
    else:
        return os.path.join("src/main/java", package_path, file_name)

def save_file(parent_directory, relative_path, content):
    """Creates directories and saves the content in a file."""
    full_path = os.path.join(parent_directory, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, "w", encoding="utf-8") as file:
        file.write(content.strip())
    
    print(f"Saved: {full_path}")

def process_markdown(markdown_file, parent_directory):
    """Extracts Java files, pom.xml, and application.properties from markdown."""
    with open(markdown_file, "r", encoding="utf-8") as file:
        markdown_content = file.read()

    # Extract Java code blocks
    java_blocks = extract_code_blocks(markdown_content, "java")
    for code in java_blocks:
        file_path = determine_java_file_path(code)
        save_file(parent_directory, file_path, code)

    # Extract and save pom.xml (assumes only one pom.xml in the markdown)
    pom_blocks = extract_code_blocks(markdown_content, "xml")
    for pom_content in pom_blocks:
        if "<project" in pom_content and "<dependencies>" in pom_content:
            save_file(parent_directory, "pom.xml", pom_content)

    # Extract and save application.properties
    properties_blocks = extract_code_blocks(markdown_content, "properties")
    for properties_content in properties_blocks:
        save_file(parent_directory, "src/main/resources/application.properties", properties_content)
