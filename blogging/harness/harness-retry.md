# Retry Strategy Example
- Here is an example of retry strategy in Harness.
- In this example, i mock it to fail 2 times and it passes in the 3rd attempt.
- Overall it tries 3 times and it succeeds in the 3rd attempt.
- We could configure it to repeat n- times before marking the step as failed.
- This could be useful in Harness while we try to fix compile errors multiple times using AI.
- Below is a sample YAML
- Key part is the `RetryStep` section where we define the failureStrategies.
- Also, if we look at `onRetryFailure` section, we could mark action as :
        - MarkAsFailure: Mark the step as Failed if retry failed
        - Ignore : ignore the failure
        - MarkAsSuccess: Still mark the step as success even if retry failed.
 
```yaml
pipeline:
  name: Retry Step Example
  identifier: RetryExample
  projectIdentifier: agentiveworkflow
  orgIdentifier: default
  stages:
    - stage:
        name: Retry Step Example
        identifier: RetryDemoStage
        type: CI
        spec:
          execution:
            steps:
              - step:
                  name: Retry Step
                  identifier: RetryStep
                  type: Run
                  spec:
                    connectorRef: account.orgnamedockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: |-
                      file_path="${HARNESS_WORKSPACE}/retry_count.txt"

                      if [ ! -f "$file_path" ]; then
                        echo "0" > "$file_path"
                      fi

                      count=$(cat "$file_path")
                      echo "Current retry count: $count"
                      count=$((count + 1))
                      echo "$count" > "$file_path"

                      if [ "$count" -lt 3 ]; then
                        echo "Failing step (attempt $count)"
                        exit 1
                      else
                        echo "Step succeeded on attempt $count"
                      fi
                  failureStrategies:
                    - onFailure:
                        errors:
                          - AllErrors
                        action:
                          type: Retry
                          spec:
                            retryCount: 3
                            onRetryFailure:
                              action:
                                type: MarkAsFailure
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
              harnessImageConnectorRef: account.orgnamedockerhub
              os: Linux
          cloneCodebase: false
          caching:
            enabled: false
            paths: []
          buildIntelligence:
            enabled: false
        description: ""
```