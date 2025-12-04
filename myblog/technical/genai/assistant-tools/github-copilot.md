1. github copilot demonstration of a good concept like boiler plate code generation,etc.

# Agent mode
- Available in VSCode insiders that has access to agent mode.

## Vue Agent Example
- create an app using vue. use the current directory.
- remove the default component. Add a new component for creating a new user.
- update to have a modern feel and onboarding flow

## React Agent Example
- create a tic-tac-toe react app
- X should be in center of the square.

## eCommerce Example github prompts
 - can you help me get all tailwind color classes?
 - can you help me learn all inbuilt react hooks?
 - Copilot-Edit: 
    - create one webpage to welcome user in website
    - create a css file with clean styling for the welcome page
    - Reference: https://youtu.be/McB52kJ4s8M?si=E1upYeDl_UnojTKB
    - Not so useful

## VSCode Useful feature demo
 - https://www.youtube.com/watch?v=2pFPJYdPM7Q

## Differences
- Copilot Edits is your go-to for fast, precise tweaks—think refactoring a function, squashing a bug, or applying consistent changes across files without losing your flow.
- Agent mode, on the other hand, steps up as your AI collaborator for thornier, multi-file challenges—analyzing your codebase, proposing architectural fixes, and even running terminal commands while you steer the ship and approve each move.

## Chat Prompts
 - What can i ask you in this chat window?

## Combining With Other Development Tools
- Agent mode works best as part of a broader toolset. Consider integrating it with:
    - Git operations for version control management
    - Project management tools for task tracking
    - Testing frameworks for automated quality assurance
    - Documentation generators for comprehensive technical documentation
 
## Official Trainings
https://learn.microsoft.com/en-us/training/modules/generate-documentation-using-github-copilot-tools/

## Documentation 
@workspace document this project

## gh copilot cli
- generate alias using `gh copilot alias` and copy-paste them in ~/.zshrc
- ghce : to ask AI to explain the command. e is for explain.
- ghcs : use AI to suggest a command or create script etc. s is for suggest.
    - ghce "docker image ls"
        - Explains the command.
    - ghce "docker container ls -a"
    - ghcs "find all csv files in the directory"
        - `find . -name "*.csv"`
    - ghcs "maven install without tests and javadoc generation" 
        - `mvn install -DskipTests -Dmaven.javadoc.skip=true `
    - ghcs "write a script that keeps running maven clean install for n times. If the maven clean install is successful, then stop it. Otherwise keep trying till n times."
    ```bash
    for i in $(seq 1 n); do
        mvn clean install && break || sleep 1;
    done
    ```