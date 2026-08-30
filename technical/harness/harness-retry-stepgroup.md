# Step-group Retry
- CompileCode + FixErrors combined under a Step-group named "CompileAndFix".
- first time, it fails in compilation and runs a mock fix (imagine AI based fix)
- second time , the compilation passes and fix step is skipped.

```yaml
pipeline:
  projectIdentifier: agentiveworkflow
  orgIdentifier: default
  stages:
    - stage:
        name: Retry Step Group Example
        identifier: RetryDemoStage
        type: CI
        spec:
          execution:
            steps:
              - stepGroup:
                  name: CompileAndFix
                  identifier: CompileAndFix
                  steps:
                    - step:
                        type: Run
                        name: CompileCode
                        identifier: CompileCode
                        spec:
                          connectorRef: account.organizationdockerhub
                          image: developerexperience-r/jdk-maven:latest
                          shell: Bash
                          command: |-
                            file="${HARNESS_WORKSPACE}/compile_retry.txt"
                            if [ ! -f "$file" ]; then
                                echo "0" > "$file"
                            fi

                            count=$(cat "$file")
                            echo "Compile attempt: $count"
                            count=$((count + 1))
                            echo "$count" > "$file"

                            if [ "$count" -lt 2 ]; then
                                echo "❌ Compilation failed"
                                exit 1
                            else
                                echo "✅ Compilation successful"
                            fi
                    - step:
                        type: Run
                        name: FixErrors
                        identifier: FixErrors
                        spec:
                          connectorRef: account.organizationdockerhub
                          image: developerexperience-r/jdk-maven:latest
                          shell: Bash
                          command: echo "🔧 Fixing compilation issues..."
                        when:
                          stageStatus: Failure
                  failureStrategies:
                    - onFailure:
                        errors:
                          - AllErrors
                        action:
                          type: RetryStepGroup
                          spec:
                            retryCount: 2
                            retryIntervals:
                              - 10s
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
          cloneCodebase: false
          caching:
            enabled: false
            paths: []
          buildIntelligence:
            enabled: false
        description: ""
  identifier: Retry_Step_Group
  tags: {}
  name: Retry Step Group
```