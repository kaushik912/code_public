# Sample Prompts

## ReadMe Docs

### Automate README creation to document project setup, dependencies, and usage.

Generate a structured README for a [project name] built with [tech stack].
- Include sections: Project Overview, Features, Prerequisites, Installation, Configuration, Usage, API Documentation, and Troubleshooting.
- Format output in Markdown with proper headers (`#`), bullet points, and code snippets.
- Provide example API usage and common errors with resolutions.
- Ensure the installation steps are detailed for both Mac and Windows users.


Create a professional README for a Java Spring Boot microservice named [service name].
- Include sections: Service Overview, Endpoints (GET, POST, PUT, DELETE), Authentication (JWT/OAuth), Environment Variables, and Logging Setup.
- Format it using Markdown.
- Provide example API requests and responses in JSON.
- Add a troubleshooting section for common deployment issues.
JavaDocs

### Add inline documentation for Java classes, methods, and APIs.

Generate Javadoc comments for the following Java method.
- Include a detailed method description, @param annotations for each input, and @return annotation.
- If exceptions are thrown, document them with @throws.
- Provide an example usage in the comments.
[Copy Method Here]


Write Javadoc documentation for the `PaymentProcessor` class, which processes user payments.
- Document class-level purpose, dependencies, and key methods.
- Include @author and @version annotations.
- Add usage examples for each public method.
JIRA Stories

## Streamline user story creation with clear acceptance criteria.

Generate a JIRA story for implementing Multi-Factor Authentication (MFA) in a login system.
- **Title:** Implement MFA for login authentication
- **User Story:** As a [user role], I want to enable multi-factor authentication so that my account is more secure.
- **Acceptance Criteria:**
  - Users must be prompted for an MFA code during login.
  - SMS and email-based OTPs should be supported.
  - Invalid MFA attempts should result in temporary account lockout.
- **Priority:** High
- **Labels:** Security, Authentication
- Format output as JSON for import into JIRA.


Create a JIRA epic titled **"Order Management System"**, breaking it down into user stories for:
1. Order Creation
2. Payment Processing
3. Order Fulfillment
- Provide descriptions, acceptance criteria, and priority levels for each.
- Format in Confluence Wiki Markup for direct import into JIRA.
User Guides

## Provide detailed instructions for users to navigate and utilize a system.


Generate a detailed user guide for deploying a React frontend with a Node.js backend using Docker and Kubernetes.
- **Title:** User Guide - Deploying [App Name]
- **Sections:** Overview, Prerequisites, Deployment Steps, Common Issues & Fixes.
- Provide terminal commands formatted in Markdown (`code blocks`).
- Add numbered steps for clarity.
- Output format: Confluence Wiki Markup.


Write a Markdown user guide for authenticating API requests using OAuth 2.0 in a microservices architecture.
- Cover OAuth grant types, token validation, and common error handling.
- Provide example HTTP requests and responses in JSON.
- Add a diagram illustrating token flow (in PlantUML format).
High-Level Design (HLD)

## Define the architecture, major components, and their interactions.


Generate a High-Level Design (HLD) document for a **real-time messaging platform**.
- Include the following sections:
  1. **Overview**: Briefly describe the system.
  2. **Architecture Diagram**: Generate a PlantUML representation.
  3. **Technology Stack**: List tech used for frontend, backend, database, and message queue.
  4. **Data Flow**: Describe how messages are sent and received.
- Format output in Markdown and include JSON export for Lucidchart import.


Create a structured JSON-based API contract for a `UserProfileService`.
- Define request/response schemas, error handling, and authentication methods.
- Format output in OpenAPI (Swagger) specification for direct import into API documentation tools.
Low-Level Design (LLD)

### Define data structures, APIs, and class-level details.


Generate a Low-Level Design (LLD) document for an authentication service using JWT-based authorization.
- **Include sections:**
  - Class Diagrams (in GraphViz DOT format)
  - API Contracts (in OpenAPI YAML format)
  - Database Schema (PostgreSQL DDL script)
- Format output to be easily importable into PlantUML or GraphViz.


Create a structured JSON-based API contract for a `UserProfileService`.
- Define request/response schemas, error handling, and authentication methods.
- Format output in OpenAPI (Swagger) specification for direct import into API documentation tools.

For larger codebases or customization, use the detailed prompt examples below to refine your test generation.

## Best Practices

Follow the Arrange-Act-Assert (AAA) pattern for test clarity.

Cover positive, negative, and edge cases to ensure comprehensive testing.

Mock dependencies when testing functions with external interactions (e.g., databases, APIs).

Use meaningful test method names that clearly describe test intent.

Ensure tests are isolated, reproducible, and self-contained.

### Generic Unit Test Case Prompt

Generate a comprehensive set of unit tests for the following function/class: [PASTE CODE]. Ensure the tests:
Follow the Arrange-Act-Assert pattern.
Include positive, negative, and edge cases.
Mock dependencies where necessary.
Use clear and descriptive test names.
Follow best practices for the given testing framework."
Language Specific Unit Test Case Prompts

### Java (JUnit 5 with Mockito)

Generate JUnit 5 test cases for the following Java method using Mockito for dependencies.
* Cover valid inputs, invalid inputs, and edge cases.
* Mock external dependencies where applicable.
* Follow best practices with clear method names and assertions.
* Ensure the test cases are self-contained and independent.
Code snippet: [PASTE CODE]

### Python (PyTest with Mocking)


Write unit tests for the given Python function using PyTest.
* Ensure coverage for success, failure, and edge cases.
* Mock external API calls or database interactions using unittest.mock.
* Use fixtures where necessary for setup and teardown.
* Follow PyTest conventions and use meaningful assertions.
Code snippet: [PASTE CODE]

### JavaScript (Jest with Mocks & Spies)

Write Jest test cases for the given JavaScript/TypeScript function.
* Ensure coverage for valid, invalid, and boundary conditions.
* Use Jest spies/mocks for external API calls or database interactions.
* Follow Jest best practices, including test naming conventions.
* Use snapshots if applicable.
Code snippet: [PASTE CODE]

### BigQuery (SQL Unit Testing with Dataform / Query Assertions)

Generate SQL unit tests for the following BigQuery query using Dataform or Query assertions.
* Include tests for expected results, edge cases, and NULL handling.
* Check for data integrity and correctness.
* Use mock datasets to validate query behavior.
* Ensure query performance best practices are followed.
Code snippet: [PASTE CODE]
 



Generate a boilerplate code template for a [LANGUAGE] [FRAMEWORK] project.
* Include setup instructions, key folder structure, and configuration best practices.
* Ensure support for logging, environment variables, and error handling.
* Add placeholders for main functionality and comments explaining key sections.
* Ensure compatibility with [SPECIFIC TOOL/VERSION].

## Language Specific Boilerplate Code Creation Prompts

### Java (Spring Boot REST API)

Generate a Java Spring Boot boilerplate for a REST API with the following features:
* Spring Boot 3.x with Maven/Gradle setup
* A UserController with endpoints for CRUD operations
* A UserService layer to handle business logic
* A UserRepository for database interactions using Spring Data JPA
* Application properties configured for PostgreSQL
* Include Swagger documentation setup
Ensure best practices for layered architecture, exception handling, and logging.

### Python (FastAPI with SQLAlchemy)

Create a FastAPI boilerplate in Python with the following features:
* Directory structure: app/routers, app/models, app/services
* Database integration using SQLAlchemy with a PostgreSQL connection
* JWT-based authentication setup
* Pydantic models for request validation
* Built-in exception handling and CORS support
* Swagger UI and OpenAPI documentation enabled
Ensure modular design and include instructions for running via Uvicorn.

### JavaScript (Express.js with TypeScript)
Generate an Express.js boilerplate using TypeScript with the following setup:
* Structured project folders: routes/, controllers/, middleware/, config/
* Environment variables managed via dotenv
* JWT authentication and middleware for role-based access control
* API documentation using Swagger
* Unit tests using Jest
Ensure best practices for error handling, async/await functions, and logging 

### BigQuery (SQL Data Pipeline Boilerplate)

Create a boilerplate for a BigQuery SQL-based data pipeline.
* Define standard table schemas for structured data storage
* Include partitioning and clustering for optimization
* Provide scheduled query templates for ETL processing
* **Add query performance best practices (e.g., avoiding SELECT ***
* Ensure compatibility with dbt and Dataform for pipeline automation.

### Javascript  (React: Adding a new search bar component to an existing page)

I am working on an existing JavaScript-based React page and need to add a new reusable search bar component.
Generate a SearchBar React component that includes:
* A controlled input field with a debounce mechanism
* A clear button to reset the search field
* An event handler to trigger a parent function when the search input changes
* Basic Tailwind CSS for styling
* Ensure the component follows best practices for reusability and state management.
Output: A reusable SearchBar component using React hooks and Tailwind CSS.

### JavaScript (React: Creating a full user profile page)

Generate a new React page called UserProfile.tsx. Requirements:
* Fetch user data from an API endpoint (/api/users/:id) using useEffect and axios.
* Display user details (profile picture, name, email, recent activity).
* Include a tabbed interface (Profile | Settings | Activity Log).
* Use Tailwind CSS for styling.
* Implement a basic skeleton loader while fetching data.


Best Practices

Clearly define the refactoring goal: Performance optimization, readability, reducing duplication, etc.

Specify coding standards: Mention frameworks or style guides (e.g., PEP8, Airbnb JS Style Guide).

Provide context: Include relevant portions of the code that need improvement.

Preserve functionality: Ensure behavior remains unchanged post-refactor.

Tip: For optimal refactoring, use ‘Chat with Files’ to analyze existing code:


Sample Prompts

Improving Readability & Maintainability

### Python - Function Refactoring

Refactor the following Python function to improve readability and maintainability. Apply PEP8 best practices, add meaningful docstrings, and remove redundant logic. Ensure that all variables have descriptive names and the logic is modularized into smaller, reusable functions where possible. Additionally, handle edge cases appropriately without changing functionality.
[PASTE CODE]

### Java - Modularization & Encapsulation

Refactor the following Java class to improve encapsulation and reduce redundancy. Extract repeated logic into private utility methods and follow Java best practices (e.g., adhering to SOLID principles, ensuring appropriate access modifiers, and using meaningful method names). Also, apply Javadoc comments to explain key functionalities.
[PASTE CODE]

## Performance Optimization

### Java - Using Streams & Lambdas

Refactor this Java code to replace traditional loops with Java 8 Streams and Lambda expressions for improved readability and performance. Ensure that the code follows best practices for functional programming while maintaining clarity and avoiding unnecessary complexity.
[PASTE CODE]

### JavaScript - Loop Optimization


Optimize this JavaScript function by replacing inefficient loops with ES6+ array methods like map, filter, and reduce. Ensure that performance is improved while maintaining the same functionality. If applicable, remove unnecessary temporary variables and replace them with concise one-liners where possible.
[PASTE CODE]

## Removing Code Duplication

### BigQuery - Query Optimization

Refactor the following BigQuery SQL query to remove duplicate subqueries, optimize performance, and reduce computation costs. Use common table expressions (CTEs) or temporary tables if necessary to make the query more efficient without affecting the final result.
[PASTE CODE]

### React - Component Reusability & Optimization

Refactor the following React components to remove duplicate code by extracting shared logic into a custom hook. Ensure the UI remains functionally the same, but improve maintainability by making the components more reusable.
[PASTE CODE]

## Reducing Cyclomatic Complexity

Cyclomatic complexity measures the number of independent paths through your code, often caused by excessive branching (if statements, loops, nested conditions, etc.). High complexity leads to hard-to-maintain and error-prone code.


### Python - Refactor Deeply Nested Conditionals

The following Python function has high cyclomatic complexity due to deep nesting. Refactor it to improve readability and reduce branching. Use early returns, helper functions, or a strategy pattern if applicable. Maintain the same functionality but optimize the structure.
[PASTE CODE]

### Refactoring Complex Conditionals in JavaScript

Refactor the following JavaScript function to reduce cyclomatic complexity. Convert nested conditions into a cleaner, more readable format using early exits, helper functions, or ternary operators where appropriate.
[PASTE CODE]
 

Tip: Measuring Cyclomatic Complexity with SonarQube

SonarQube is a static code analysis tool that detects complexity, code smells, and potential bugs. It assigns a complexity score to functions, helping teams prioritize refactoring efforts.