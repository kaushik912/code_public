###  Harness Approval
- Below is an example in Harness to take user input 
- If input for proceed is "yes", we proceed to next step

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
              harnessImageConnectorRef: account.pypldockerhub
              os: Linux
          execution:
            steps:
              - step:
                  type: Run
                  name: hellostep
                  identifier: mockexit
                  spec:
                    connectorRef: account.pypldockerhub
                    image: developerexperience-r/jdk-maven:latest
                    shell: Bash
                    command: echo "Hi"
                  description: hello
                  when:
                    stageStatus: Success
                contextType: Pipeline
          sharedPaths:
            - /genai
          caching:
            enabled: false
            paths: []
          buildIntelligence:
            enabled: false
    - stage:
        name: approve
        identifier: approve
        description: ""
        type: Approval
        spec:
          execution:
            steps:
              - step:
                  name: user decision
                  identifier: user_decision
                  type: HarnessApproval
                  timeout: 1d
                  spec:
                    approvalMessage: Please type "yes" in case you wish to proceed ahead
                    includePipelineExecutionHistory: true
                    approvers:
                      minimumCount: 1
                      disallowPipelineExecutor: false
                      userGroups:
                        - _project_all_users
                    isAutoRejectEnabled: false
                    approverInputs:
                      - name: proceed
                        defaultValue: "no"
                        description: proceed to next step
                        required: true
              - step:
                  type: ShellScript
                  name: nextStep
                  identifier: nextStep
                  spec:
                    shell: Bash
                    executionTarget: {}
                    source:
                      type: Inline
                      spec:
                        script: echo "Proceeding to next step"
                    environmentVariables: []
                    outputVariables: []
                  timeout: 10m
                  when:
                    stageStatus: Success
                    condition: <+pipeline.stages.approve.spec.execution.steps.user_decision.output.approvalActivities[0].approverInputs[0].value>=="yes"
        tags: {}
  identifier: simpleapproval
  name: simpleapproval

```