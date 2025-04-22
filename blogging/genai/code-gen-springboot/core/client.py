from project_generator import generate_spring_boot_project
from markdown_parser import process_markdown
from pom_build_error_fixer import run_maven_install
def main():
    print("Beginning of AI Flow!")
    output_dir="generated_project"
    requirements = """
    Generate a complete Spring Boot application that manages employees with a REST API. The application should include:
    A Employee entity with fields: id, name, department, and salary.
    A Controller with endpoints to create, read, update, and delete employees (/employees).
    A Service layer to handle business logic.
    A Repository interface using Spring Data JPA.
    Use MySQL as the database and configure application.properties.
    Return appropriate HTTP responses for success and failure cases.
    A main class for a Spring Boot application.
    A pom.xml file that includes all dependencies.
    "
    """
    generate_spring_boot_project(requirements,output_dir)

    ## Parse markdown to directory/files
    markdown_file = output_dir+"/SpringBootApplicationOutput.md"
    parent_directory = "codev1"  # Change as needed
    process_markdown(markdown_file, parent_directory)

    ### Compile, build and fix any errors using AI
    for attempt in range(3):
        print(f"Attempt {attempt + 1}: Running Maven install...")
        result = run_maven_install(parent_directory)
        print(result)

        if "Maven build successful" in result:
            print("Maven build successful. Exiting loop.")
            break

        ### Parse fix markdown to pom.xml
        markdown_file = output_dir + "/fix_pom_xml.md"
        process_markdown(markdown_file, parent_directory)

    # If the loop completes without success, you can handle it here if needed

if __name__ == "__main__":
    main()