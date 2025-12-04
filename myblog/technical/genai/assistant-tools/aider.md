# Aider AI Assistant Tool - Setup, Configuration, and Usage

This document provides a comprehensive guide on setting up, configuring, and using the Aider AI assistant tool for code development and refactoring.

## Setup

### Creating the Environment

*   Create a directory for Aider:
    ```bash
    mkdir aider
    ```
*   Create a virtual environment within the `aider` directory. You can use the command line or VS Code's interface (Command+Shift+P > Python: Create Environment...).
*   Select a suitable Python runtime version (e.g., Python 3.11.6).

### Installing Aider

*   Install `aider-install`:
    ```bash
    python -m pip install aider-install
    ```
*   Run the Aider installer:
    ```bash
    aider-install
    ```

### Configuring the PATH

*   After installation, update your `~/.zshrc` file (recommended) or manually run the following command:
    ```bash
    export PATH="/Users/kkailasnath/.local/bin:$PATH"
    ```
    *   This ensures that the `aider` command is accessible from your terminal.

## Using Ollama Models as the Language Model (LLM)

### Installing `aider-chat`

*   Install `aider-chat` for better Git integration and improved code refactoring:
    ```bash
    python -m pip install -U aider-chat
    ```

### Configuring Ollama API Base

*   Add the following line to your `~/.zshrc` file to set the Ollama API base:
    ```bash
    export OLLAMA_API_BASE=http://127.0.0.1:11434
    ```

### Starting Aider with Ollama

*   To start Aider with a specific Ollama model, use:
    ```bash
    aider --model ollama_chat/<model>
    ```
    *   Example:
        ```bash
        aider --model ollama/qwen2.5-coder:3b
        ```
    *   `ollama/qwen2.5-coder:3b` is a recommended model for use with Aider.

## Context Window Tweaking

### `.aider.model.settings.yml` Configuration

*   Create a `.aider.model.settings.yml` file in your home directory (`~`) for global model settings.
*   Add context window specifications to this file:
    ```yaml
    - name: ollama/qwen2.5-coder:3b
      extra_params:
        num_ctx: 8192
    ```
    *   This example sets a context window of 8192 tokens for `ollama/qwen2.5-coder:3b`.
*   Aider often auto-detects the context window, but this allows manual control if needed.

## Disabling Auto-Commit

### `AIDER_NO_AUTO_COMMIT` Environment Variable

*   To prevent Aider from automatically committing changes to Git, set:
    ```bash
    export AIDER_NO_AUTO_COMMIT=true
    ```

## Ollama Context Settings

### Modifying Context Size During Chat

*   Ollama's default context window size is 2048 tokens.
*   To modify it while using Aider with Ollama, use the `/set parameter` command in the Aider chat:
    ```
    /set parameter num_ctx 4096
    ```
    *   This example changes the context window to 4096 tokens.

## Basic Usage

### Getting Help

*   Display the available Aider commands:
    ```bash
    aider --help
    ```

### Example 1: Prime Number Checker

*   Start Aider with an Ollama model and a file name (existing or new):
    ```bash
    aider --model ollama_chat/qwen2.5-coder:3b checkprime.py
    ```
*   In the Aider prompt, request the prime number checking program:
    ```
    Create a python program that checks if a number is prime or not
    ```
*   Aider will generate the Python code. You can review and discard if necessary.

### Example 2: Palindrome Checker

*   Start Aider:
    ```bash
    aider --model ollama_chat/qwen2.5-coder:3b
    ```
*   To have Aider create a new file, add it to the repository first:
    ```
    /add palindrome.py
    ```
*   Then, in the prompt, ask for the palindrome code:
    ```
    create a python code that checks if a number is palindrome or not.
    ```
*   Aider generates the requested code.

### Example 3: Fixing Errors in Code

*   Add a new file to the Aider chat:
    ```
    /add hello.py
    ```
*   Aider will indicate that the file doesn't exist. Enter `Y` to confirm file creation.
*   Add erroneous code to `hello.py`:
    ```python
    def greeting(name):
        prinln(f"Hey {name}")
    ```
*   Verify that the file is in the chat:
    ```
    /ls
    ```
*   If issues arise (e.g., responses for other code), reset and re-add:
    ```
    /reset
    /add hello.py
    ```
*   Make sure that only `hello.py` is in the chat.
*   Ask Aider to fix the compilation errors:
    ```
    can you fix the compile errors
    ```
* It will correct the error in the `hello.py` file.

### Example 4: Generating React Code

*   **Project Path**
    *   `/Users/kkailasnath/projects/react_project/learning_app`
*   Start Aider with the `deepseek-r1:7b` model:
    ```bash
    aider --model ollama_chat/deepseek-r1:7b
    ```
*   Add the file `src/Counter.js` to the chat:
    ```
    /add src/Counter.js
    ```
*   Provide the prompt for the React component:
    ```
    create a React javascript file that counts when user clicks on a button. Do not use typescript
    ```
*   Aider will produce the following React code:

    ```javascript
    import React, { useState } from "react";

    const Counter = () => {
      const [count, setCount] = useState(0);

      const handleClick = () => {
        setCount((prevCount) => prevCount + 1);
      };

      return (
        <div className="text-center">
          <h1>Click Counter</h1>
          <p>The counter is: {count}</p>
          <button onClick={handleClick}>Click Me!</button>
        </div>
      );
    };

    export default Counter;
    ```
