## Harness Rapid Prototyping
- generates code
- push to github
```yaml
pipeline:
  projectIdentifier: agentiveworkflow
  orgIdentifier: default
  tags: {}
  stages:
    - stage:
        name: agentive-project-generation
        identifier: pythonchecker
        description: ""
        type: CI
        spec:
          cloneCodebase: false
          infrastructure:
            type: KubernetesDirect
            spec:
              connectorRef: account.testappsprimaryk8s
              namespace: pre-prod
              serviceAccountName: harness-service-account
              automountServiceAccountToken: true
              nodeSelector: {}
              harnessImageConnectorRef: account.organizationdockerhub
              os: Linux
          execution:
            steps:
              - step:
                  type: Run
                  name: mockexit
                  identifier: mockexit
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: exit 1
                  description: exit
                  when:
                    stageStatus: Success
                    condition: "false"
                contextType: Pipeline
              - step:
                  type: Run
                  name: generate code
                  identifier: Run_1
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Python
                    command: |-
                      import requests
                      import os
                      import sys
                      import time
                      class LLMProvider:
                          """Base class for LLM API providers."""
                          
                          def __call__(self, prompt):
                              """Call the LLM with a prompt."""
                              raise NotImplementedError("Subclasses must implement this method")

                      class SeldonProvider(LLMProvider):
                          """Provider for Seldon Qwen-Coder API."""
                          
                          def __init__(self, system_prompt="You are an expert in spring boot and Java development."):
                              self.url = "your_ai_endpoint"
                              self.system_prompt = system_prompt
                              self.headers = {"Content-Type": "application/json"}
                          
                          def __call__(self, prompt):
                              """
                              Call the Seldon API with a prompt.
                              
                              Args:
                                  prompt (str): The prompt to send
                                  
                              Returns:
                                  str: The model's response text
                              """
                              payload = {
                                  "parameters": {
                                      "extra": {
                                          "temperature": 0.3,
                                          "max_new_tokens": 10000,
                                          "repetition_penalty": 1
                                      }
                                  },
                                  "inputs": [
                                      {
                                          "name": "input",
                                          "shape": [1],
                                          "datatype": "str",
                                          "data": [prompt]
                                      },
                                      {
                                          "name": "system",
                                          "shape": [1],
                                          "datatype": "str",
                                          "data": [self.system_prompt]
                                      }
                                  ]
                              }
                              
                              try:
                                  response = requests.post(self.url, headers=self.headers, json=payload)
                                  response.raise_for_status()
                                  
                                  response_data = response.json()
                                  # Extract the response from the Seldon API format
                                  if "outputs" in response_data and len(response_data["outputs"]) > 0:
                                      return response_data["outputs"][0]["data"][0]
                                  return "No valid response received from model"
                              except requests.exceptions.RequestException as e:
                                  return f"API request failed: {e}"

                      class GeminiProvider(LLMProvider):
                          """Provider for Gemini API."""
                          
                          def __init__(self):
                              self.url = "your_ai_endpoint"
                              self.headers = {"Content-Type": "application/json"}
                          
                          def __call__(self, prompt):
                              """
                              Call the Gemini API with a prompt.
                              
                              Args:
                                  prompt (str): The prompt to send
                                  
                              Returns:
                                  str: The model's response text
                              """
                              payload = {
                                  "inputs": {
                                      "_content_": prompt
                                  }
                              }
                              
                              try:
                                  # Wait for 30 seconds to avoid clogging the LLM endpoint
                                  time.sleep(30)
                                  response = requests.post(self.url, headers=self.headers, json=payload)
                                  response.raise_for_status()
                                  
                                  response_data = response.json()
                                  return response_data.get("outputs", {}).get("text", "")
                              except requests.exceptions.RequestException as e:
                                  return f"API request failed: {e}"

                      def get_model():
                          """
                          Returns a function that can call an LLM via API endpoint.

                          Returns:
                              LLMProvider: A provider that calls the Gemini endpoint
                          """
                          return SeldonProvider()

                      def save_ai_output(result, output_dir="generated_project"):
                          
                          try:
                              os.makedirs(output_dir, exist_ok=True)
                              output_file = os.path.join(output_dir, "SpringBootApplicationOutput.md")
                              with open(output_file, "w") as f:
                                  f.write(result)
                              print(f"Spring Boot code saved to {output_file}")

                          except Exception as e:
                              print(f"❌ Error generating project: {e}")
                              sys.exit(1)

                      requirements = "<+pipeline.variables.PROMPT>"
                      print(requirements)

                      def main():
                          # Initialize the LLM provider
                          llm = get_model()
                          
                          try:
                              # Call the LLM with the requirements
                              output_text = llm(requirements)
                              
                              # Save the output
                              print(output_text)
                              save_ai_output(output_text,"/genai/generated_project")

                          except Exception as e:
                              print(f"Error: {e}")
                              sys.exit(1)

                      if __name__ == "__main__":
                          main()
                  description: generate code based on prompt
                  timeout: 5m
                contextType: Pipeline
              - step:
                  type: Run
                  name: add_settings_xml
                  identifier: add_settings_xml
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: |-
                      mkdir -p /genai/generated_project/
                      cat <<'EOF' > /genai/settings.xml
                      <?xml version="1.0" encoding="UTF-8"?>
                      <settings>
                              <localRepository>/genai/raptor</localRepository>

                              <servers>
                                      <server>
                                              <id>raptor.releases</id>
                                              <username></username>
                                              <password></password>
                                      </server>
                                      <server>
                                              <id>raptor.snapshots</id>
                                              <username></username>
                                              <password></password>
                                      </server>
                              </servers>

                              <mirrors>
                                      <mirror>
                                              <id>central</id>
                                               <mirrorOf>*,!public</mirrorOf>
                                              <url>https://organizationcentral.es.organizationcorp.com/nexus/content/repositories/central</url>
                                      </mirror>
                              </mirrors>

                              <profiles>
                                      <profile>
                                              <id>organization</id>
                                              <!-- add a repository property to ease the archetype:generate useage -->
                                              <properties>
                                                      <archetypeCatalog>https://organizationcentral.es.organizationcorp.com/nexus/content/groups/public/archetype-catalog.xml
                                                      </archetypeCatalog>
                                              </properties>
                                              <repositories>
                                                      <!-- Raptor Repository -->
                                                      <repository>
                                                              <id>public</id>
                                                              <url>https://organizationcentral.es.organizationcorp.com/nexus/content/groups/public/</url>
                                                              <releases>
                                                                      <enabled>true</enabled>
                                                              </releases>
                                                              <snapshots>
                                                                      <enabled>true</enabled>
                                                              </snapshots>
                                                      </repository>
                                              </repositories>
                                              <pluginRepositories>
                                                      <pluginRepository>
                                                              <id>public</id>
                                                              <url>https://organizationcentral.es.organizationcorp.com/nexus/content/groups/public/</url>
                                                              <releases>
                                                                      <enabled>true</enabled>
                                                              </releases>
                                                              <snapshots>
                                                                      <enabled>true</enabled>
                                                              </snapshots>
                                                      </pluginRepository>
                                                      <pluginRepository>
                                                              <id>central</id>
                                                              <url>https://organizationcentral.es.organizationcorp.com/nexus/content/repositories/central</url>
                                                              <releases>
                                                                      <enabled>true</enabled>
                                                              </releases>
                                                              <snapshots>
                                                                      <enabled>false</enabled>
                                                              </snapshots>
                                                      </pluginRepository>
                                              </pluginRepositories>
                                      </profile>
                              </profiles>

                              <activeProfiles>
                                      <activeProfile>organization</activeProfile>
                              </activeProfiles>

                              <pluginGroups>
                                      <pluginGroup>org.mortbay.jetty</pluginGroup>
                                      <pluginGroup>com.ebay.raptor.build</pluginGroup>
                                      <pluginGroup>org.codehaus.mojo</pluginGroup>
                                      <pluginGroup>org.sonatype.maven.plugins</pluginGroup>
                              </pluginGroups>
                      </settings>
                      EOF
                  description: add settings.xml file
              - step:
                  type: Run
                  name: parse-markdown
                  identifier: parsegeneratedmd
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Python
                    command: |-
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


                      markdown_file = "/genai/generated_project/SpringBootApplicationOutput.md"  # Replace with your markdown file
                      parent_directory = "/genai/codev1"  # Change as needed
                      process_markdown(markdown_file, parent_directory)
                  description: parse the generated code markdown response
              - step:
                  type: Run
                  name: mvn-install
                  identifier: mvninstall
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: |-
                      # Set the JAVA_HOME environment variable to the value of stage.variables.jdk
                      export JAVA_HOME=/opt/jdk/zulu-jdk-17

                      # Set the MAVEN_HOME environment variable to the value of stage.variables.maven
                      export MAVEN_HOME=/opt/maven/maven-3.9.2

                      # Add the JAVA_HOME and MAVEN_HOME directories to the PATH environment variable
                      export PATH=$JAVA_HOME/bin:$MAVEN_HOME/bin:$PATH

                      # Get the last part of the JAVA_HOME directory path and store it in the jdkdir variable
                      jdkdir=$(basename $JAVA_HOME)

                      # Set the JDK_VERSION variable to 8 by default.
                      JDK_VERSION=8

                      # Check if the jdkdir contains the string "17"
                      if [[ "$jdkdir" =~ "17" ]]; then
                          # If it does, set JDK_VERSION to 17
                          JDK_VERSION=17
                      # Check if the jdkdir contains the string "21"
                      elif [[ "$jdkdir" =~ "21" ]]; then
                          # If it does, set JDK_VERSION to 21
                          JDK_VERSION=21
                      fi
                      echo "JDK_VERSION=$JDK_VERSION"
                      cd /genai/codev1

                      #mvn clean install -s /genai/settings.xml
                      mvn clean install -DskipTests -s /genai/settings.xml > /genai/maven.log 2>&1
                    outputVariables:
                      - name: MAVEN_STATUS
                        type: String
                        value: MAVEN_STATUS
                  description: run maven install
                  failureStrategies:
                    - onFailure:
                        errors:
                          - AllErrors
                        action:
                          type: Ignore
              - step:
                  type: Run
                  name: print_maven_status
                  identifier: print_maven_status
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: cat /genai/maven.log
                    envVariables:
                      MAVEN_STATUS: MAVEN_STATUS
                  description: maven status
                  when:
                    stageStatus: Success
              - step:
                  type: Run
                  name: github push
                  identifier: github_push
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: |-
                      #!/bin/bash

                      # === Configuration ===
                      GITHUB_USER="your_username"
                      REPO="genaisamples"
                      
                      # Reconstruct the full string
                      full_string="PAT_From_Harness_Secret_Store"

                      TARGET_BRANCH="main"

                      # === Create Project Directory ===
                      cd /genai

                      git clone https://${GITHUB_USER}:${full_string}@github.organization.com/${GITHUB_USER}/${REPO}.git
                      cd $REPO

                      # Generate dynamic name with timestamp
                      timestamp=$(date +%Y%m%d_%H%M%S)
                      dirname="output_${timestamp}"
                      mkdir -p $dirname
                      cp -r /genai/codev1 $dirname

                      # === Git Setup ===
                      git config --global user.email "your_username@organization.com"
                      git config --global user.name "your_username"

                      git add .
                      git commit -m "Add files for push"

                      # === Push to GitHub ===

                      git branch -M ${TARGET_BRANCH}
                      git push -u origin ${TARGET_BRANCH}
                  description: push to github
          sharedPaths:
            - /genai
          caching:
            enabled: false
            paths: []
          buildIntelligence:
            enabled: false
  identifier: genprojectsimple
  name: ai-rapid-prototyper
  variables:
    - name: PROMPT
      type: String
      description: PROMPT VALUE for Code Generation
      required: false
      value: <+input>
```