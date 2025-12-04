import os
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

# Configure LangChain with your LLM API key
# llm = OpenAI(model="text-davinci-003", api_key="<YOUR_API_KEY>")
llm = ChatOllama(model="qwen2.5-coder:3b")

# Step 1: Concatenate all C++ source files in the directory
def concatenate_cpp_files(directory):
    concatenated_code = ""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".cpp") or file.endswith(".h"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                    concatenated_code += f"\n// START OF FILE: {file}\n" + content + f"\n// END OF FILE: {file}\n"
    return concatenated_code

# Step 2: Generate a documentation summary using LangChain
def generate_documentation_summary(code):
    prompt = PromptTemplate(
        input_variables=["code"],
        template=(
            "You are a software engineer. Read the provided C++ code and generate a concise documentation summary.\n"
            "Include key functionality, classes, and methods described in the code.\n"
            "Code: \n{code}\n"
        ),
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    summary = chain.run(code=code)
    return summary

# Step 3: Generate Spring Boot code using the documentation summary
def generate_spring_boot_code(summary):
    prompt = PromptTemplate(
        input_variables=["summary"],
        template=(
            "You are a software engineer. Based on the following documentation summary, generate a Spring Boot application.\n"
            "Include relevant controllers, services, and endpoints. Ensure the generated code is clear and modular.\n"
            "Summary: \n{summary}\n"
        ),
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    spring_boot_code = chain.run(summary=summary)
    return spring_boot_code

# Main workflow
def main():
    cpp_directory = "/Users/kkailasnath/Downloads/genai/MathOperationsProject"  # Replace with the path to your C++ directory
    output_directory = "springbootcode"    # Replace with the desired output directory

    # Step 1: Concatenate C++ files
    print("Concatenating C++ files...")
    concatenated_code = concatenate_cpp_files(cpp_directory)

    # Step 2: Generate documentation summary
    print("Generating documentation summary...")
    documentation_summary = generate_documentation_summary(concatenated_code)
    print("Documentation Summary:\n", documentation_summary)

    # Step 3: Generate Spring Boot code
    print("Generating Spring Boot code...")
    spring_boot_code = generate_spring_boot_code(documentation_summary)
    print("Spring Boot Code Generated:\n", spring_boot_code)

    # Save the generated Spring Boot code to a file
    os.makedirs(output_directory, exist_ok=True)
    output_file = os.path.join(output_directory, "SpringBootApplication.java")
    with open(output_file, "w") as f:
        f.write(spring_boot_code)

    print(f"Spring Boot code saved to {output_file}")

if __name__ == "__main__":
    main()
