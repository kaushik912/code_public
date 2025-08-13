import anyio
import asyncio
import sys
import subprocess
import json
import datetime
from claude_code_sdk import query, ClaudeCodeOptions, Message
from pathlib import Path

async def execute_prompt(prompt: str, max_turns: int = 3, verbose: bool = False):
    """Execute a Claude Code prompt and return the response."""
    messages: list[Message] = []
    
    # Configure options for headless operation
    options = ClaudeCodeOptions(
        max_turns=max_turns
    )
    
    options = ClaudeCodeOptions(
        max_turns=3,
        system_prompt="You are a helpful assistant",
        cwd=Path("cpp_source/Core-R"),  # Can be string or Path
        allowed_tools=["Read", "Write", "Bash","Replace","View","LS","Glob","Grep","Agent","Edit"]
        # permission_mode="acceptEdits"
    )

    try:
        # Run Claude Code with the prompt
        async for message in query(prompt=prompt, options=options):
            messages.append(message)
        
        # Extract and return the response
        response_text = ""
        for message in messages:
            if hasattr(message, 'content') and message.content:
                if isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            response_text += block.text + "\n"
                elif hasattr(message.content, 'text'):
                    response_text += message.content.text + "\n"
                else:
                    response_text += str(message.content) + "\n"
            elif verbose:
                response_text += f"Message type: {type(message).__name__}\n"
        
        return response_text.strip()
                
    except Exception as e:
        return f"Error: {e}"

async def execute_prompt_cli(prompt: str, verbose: bool = False, timeout: int = None):
    """Execute a Claude Code prompt using CLI and return the response."""
    try:
        # Build the command
        cmd = [
            "claude", 
            "-p", prompt,
            "--output-format", "stream-json",
            "--verbose",
            "--dangerously-skip-permissions"
        ]
        
        if verbose:
            print(f"Executing command: {' '.join(cmd)}")
            if timeout:
                print(f"Timeout set to: {timeout} seconds")
        
        # Run the command asynchronously
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Handle timeout if specified
        if timeout:
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                # Kill the process if it times out
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                return f"Error: Command timed out after {timeout} seconds"
        else:
            stdout, stderr = await process.communicate()
        
        # Store stdout to file if verbose mode is enabled
        if verbose:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            stdout_filename = f"claude_cli_execution_{timestamp}.log"
            with open(stdout_filename, 'w') as f:
                f.write(stdout.decode())
            print(f"Verbose mode: stdout saved to {stdout_filename}")
        
        if process.returncode != 0:
            return f"Command failed with exit code {process.returncode}: {stderr.decode()}"
        
        # Parse the stream-json output
        response_text = ""
        seen_responses = set()
        
        for line in stdout.decode().strip().split('\n'):
            if line.strip():
                try:
                    json_obj = json.loads(line)
                    # Look for assistant messages with text content
                    if json_obj.get('type') == 'assistant' and 'message' in json_obj:
                        message = json_obj['message']
                        if 'content' in message and isinstance(message['content'], list):
                            for content_block in message['content']:
                                if content_block.get('type') == 'text' and 'text' in content_block:
                                    text_content = content_block['text']
                                    if text_content not in seen_responses:
                                        response_text += text_content + "\n"
                                        seen_responses.add(text_content)
                    # Also look for result type messages (final result)
                    elif json_obj.get('type') == 'result' and 'result' in json_obj:
                        result_text = json_obj['result']
                        if result_text not in seen_responses:
                            response_text += result_text + "\n"
                            seen_responses.add(result_text)
                except json.JSONDecodeError:
                    # If not JSON, treat as regular text
                    if verbose:
                        response_text += f"Non-JSON line: {line}\n"
        
        return response_text.strip()
        
    except Exception as e:
        return f"Error: {e}"

async def main():
    # Check if prompt is provided as command line argument
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        # Default prompt for testing
        prompt = "print 5 prime numbers to a file prime.txt"
    
    print(f"Prompt: {prompt}")
    print("=" * 50)
    
    # Use CLI version as default
    response = await execute_prompt_cli(prompt, verbose=True)
    print(response)

# Run the function
if __name__ == "__main__":
    asyncio.run(main())

## Reference: https://docs.anthropic.com/en/docs/claude-code/sdk