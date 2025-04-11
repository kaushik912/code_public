Below is a simple pipeline that does the following
- create a simple maven project
- compiles
- run the main app
- push it to github

```yaml
pipeline:
  projectIdentifier: agentiveworkflow
  orgIdentifier: default
  tags: {}
  stages:
    - stage:
        name: agentive-flow
        identifier: agentiveflow
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
                  when:
                    stageStatus: Success
                    condition: "false"
              - step:
                  type: Run
                  name: generate code
                  identifier: Run_1
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: |-
                      export MAVEN_OPTS="-Xmx4g"
                      cd /genai
                      mvn org.apache.maven.plugins:maven-archetype-plugin:2.4:generate \
                      -DgroupId=com.organization.agentiveai \
                      -DartifactId=agentiveai \
                      -Dversion="0.1" \
                      -Dpackage=com.organization.agentiveai.code \
                      -DinteractiveMode=false
                  description: run a maven generate command
              - step:
                  type: Run
                  name: compile code
                  identifier: compile_code
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: |-
                      export MAVEN_OPTS="-Xmx4g"
                      cd /genai/agentiveai
                      mvn package
                  description: compile code
                  when:
                    stageStatus: Success
                    condition: "false"
              - step:
                  type: Run
                  name: code run
                  identifier: code_run
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: |-
                      cd /genai/agentiveai
                      java -cp target/agentiveai-0.1.jar com.organization.agentiveai.code.App
                  description: code run
                  when:
                    stageStatus: Success
                    condition: "false"
              - step:
                  type: Run
                  name: git mock push
                  identifier: gitpush2
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: |-
                      #!/bin/bash

                      # === Configuration ===
                      GITHUB_USER="yourusername"
                      REPO="genaisamples"
                   
                      # Reconstruct the full string
                      full_string="your_PAT"

                      TARGET_BRANCH="main"

                      # === Create Project Directory ===
                      cd /genai

                      git clone https://${GITHUB_USER}:${full_string}@github.organization.com/${GITHUB_USER}/${REPO}.git
                      cd $REPO

                      # Generate dynamic name with timestamp
                      timestamp=$(date +%Y%m%d_%H%M%S)
                      filename="sample_file_${timestamp}.txt"

                      # Create file with some content
                      echo "This is a sample file created at $timestamp" > "$filename"

                      # Print file name
                      echo "File created: $filename"

                      # === Git Setup ===
                      git config --global user.email "yourusername@organization.com"
                      git config --global user.name "yourusername"

                      git add .
                      git commit -m "Add mock file for test push"

                      # === Push to GitHub ===

                      git branch -M ${TARGET_BRANCH}
                      git push -u origin ${TARGET_BRANCH}
                  when:
                    stageStatus: Success
                    condition: "false"
                  description: git mock push
              - step:
                  type: Run
                  name: git push new project
                  identifier: git_push_new_project
                  spec:
                    connectorRef: account.organizationdockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: |-
                      #!/bin/bash

                      # === Configuration ===
                      GITHUB_USER="yourusername"
                      REPO="genaisamples"
    

                      # Reconstruct the full string
                      full_string="your_PAT"

                      TARGET_BRANCH="main"

                      # === Create Project Directory ===
                      cd /genai

                      git clone https://${GITHUB_USER}:${full_string}@github.organization.com/${GITHUB_USER}/${REPO}.git
                      cd $REPO

                      # Generate dynamic name with timestamp
                      timestamp=$(date +%Y%m%d_%H%M%S)
                      dirname="output_${timestamp}"

                      cp -r /genai/agentiveai $dirname

                      # === Git Setup ===
                      git config --global user.email "yourusername@organization.com"
                      git config --global user.name "yourusername"

                      git add .
                      git commit -m "Add files for push"

                      # === Push to GitHub ===

                      git branch -M ${TARGET_BRANCH}
                      git push -u origin ${TARGET_BRANCH}
                  description: git push project
          sharedPaths:
            - /genai
          caching:
            enabled: false
            paths: []
          buildIntelligence:
            enabled: false
  identifier: gitpusher
  name: git-pusher
```