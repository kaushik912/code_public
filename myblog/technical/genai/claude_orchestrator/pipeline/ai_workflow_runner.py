#!/usr/bin/env python3
"""
Script to execute prompts using claude_prompt_executor.py
Supports single file execution (--file), directory execution (--dir), or JSON workflow (--json)
"""

import asyncio
import logging
import sys
import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import re

# Import the execute_prompt_cli function from claude_prompt_executor
from claude_prompt_executor import execute_prompt_cli

# Configuration flag to enable/disable git commits
ENABLE_GIT_COMMITS = False  # Set to True to enable git commits

# Set up logging
def setup_logging():
    """Set up logging configuration for Claude SDK output"""
    log_filename = f"claude_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Create logger
    logger = logging.getLogger('claude_executor')
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler  
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger, log_filename

def create_commit_message(prompt: str, source: str) -> str:
    """Create a commit message from prompt content"""
    # Get first line or first 60 chars of prompt
    first_line = prompt.split('\n')[0].strip()
    if len(first_line) > 60:
        first_line = first_line[:57] + "..."
    
    # Clean up the message
    commit_msg = re.sub(r'[^\w\s\-\.\,\:]', '', first_line)
    commit_msg = re.sub(r'\s+', ' ', commit_msg).strip()
    
    if not commit_msg:
        commit_msg = f"AI prompt execution from {source}"
    else:
        commit_msg = f"AI: {commit_msg}"
    
    return commit_msg

def git_commit_changes(commit_message: str, logger) -> bool:
    """Commit all changes with the given message"""
    try:
        # Check if there are changes to commit
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if not result.stdout.strip():
            logger.info("No changes to commit")
            return True
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        logger.info("Added all changes to git")
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        logger.info(f"Successfully committed with message: {commit_message}")
        print(f"✅ Committed changes: {commit_message}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        print(f"⚠️  Git commit failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during git commit: {e}")
        print(f"⚠️  Git commit error: {e}")
        return False

def extract_prompt_from_file(file_path: Path) -> str:
    """Extract prompt content from file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        return content.strip()
    except Exception as e:
        return f"Error reading file {file_path}: {e}"

async def execute_single_file(file_path: Path, timeout: int = None):
    """Execute prompt from a single file"""
    
    # Set up logging
    logger, log_file = setup_logging()
    logger.info("Starting Claude prompt execution session (single file)")
    logger.info(f"Log file: {log_file}")
    if timeout:
        logger.info(f"Timeout set to: {timeout} seconds")
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        print(f"Error: File not found: {file_path}")
        return
    
    print(f"Processing file: {file_path.name}")
    print(f"Logging to: {log_file}")
    print("=" * 80)
    
    logger.info(f"Processing file: {file_path.name}")
    
    # Extract prompt from file
    prompt = extract_prompt_from_file(file_path)
    
    if not prompt:
        logger.warning(f"No prompt content found in {file_path.name}")
        print(f"Warning: No prompt content found in {file_path.name}")
        return
    
    logger.info(f"Extracted prompt from {file_path.name}: {prompt[:100]}...")
    print(f"Prompt: {prompt}")
    print("\nExecuting...")
    
    try:
        # Execute the prompt
        response = await execute_prompt_cli(prompt,verbose=True, timeout=timeout)
        
        # Check if the response indicates a timeout
        if response.startswith("Error: Command timed out"):
            logger.warning(f"Prompt from {file_path.name} timed out after {timeout} seconds")
            print(f"⚠️  Timeout: Prompt execution exceeded {timeout} seconds")
            print(f"Response: {response}")
            return
        
        logger.info(f"Successfully executed prompt from {file_path.name}")
        logger.debug(f"Response: {response}")
        
        print(f"Response:")
        print(response)
        
        # Create git commit after successful execution
        if ENABLE_GIT_COMMITS:
            commit_msg = create_commit_message(prompt, file_path.name)
            git_commit_changes(commit_msg, logger)
        else:
            logger.info("Git commits disabled - skipping commit")
        
    except Exception as e:
        error_msg = f"Error executing prompt from {file_path.name}: {e}"
        logger.error(error_msg)
        print(f"Error: {e}")
    
    logger.info("Completed processing file")
    print(f"\nCompleted! Check {log_file} for detailed logs.")

async def execute_directory_files(directory: Path, timeout: int = None):
    """Execute prompts from all markdown files in a directory"""
    
    # Set up logging
    logger, log_file = setup_logging()
    logger.info("Starting Claude prompt execution session (directory)")
    logger.info(f"Log file: {log_file}")
    if timeout:
        logger.info(f"Timeout set to: {timeout} seconds")
    
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        print(f"Error: Directory not found: {directory}")
        return
    
    # Get all markdown files in directory
    md_files = sorted(list(directory.glob("*.md")))
    
    if not md_files:
        logger.warning(f"No markdown files found in directory: {directory}")
        print(f"No markdown files found in directory: {directory}")
        return
    
    logger.info(f"Found {len(md_files)} markdown files to process")
    print(f"Found {len(md_files)} markdown files to process")
    print(f"Logging to: {log_file}")
    print("=" * 80)
    
    # Process each markdown file
    for i, md_file in enumerate(md_files, 1):
        print(f"\n[{i}/{len(md_files)}] Processing: {md_file.name}")
        print("-" * 60)
        
        logger.info(f"Processing file {i}/{len(md_files)}: {md_file.name}")
        
        # Extract prompt from file
        prompt = extract_prompt_from_file(md_file)
        
        if not prompt:
            logger.warning(f"No prompt content found in {md_file.name}")
            print(f"Warning: No prompt content found in {md_file.name}")
            continue
        
        logger.info(f"Extracted prompt from {md_file.name}: {prompt[:100]}...")
        print(f"Prompt: {prompt}")
        print("\nExecuting...")
        
        try:
            # Execute the prompt
            response = await execute_prompt_cli(prompt,verbose=True, timeout=timeout)
            
            # Check if the response indicates a timeout
            if response.startswith("Error: Command timed out"):
                logger.warning(f"Prompt from {md_file.name} timed out after {timeout} seconds")
                print(f"⚠️  Timeout: Prompt execution exceeded {timeout} seconds, moving to next file")
                print(f"Response: {response}")
                continue
            
            logger.info(f"Successfully executed prompt from {md_file.name}")
            logger.debug(f"Response: {response}")
            
            print(f"Response:")
            print(response)
            
            # Create git commit after successful execution
            if ENABLE_GIT_COMMITS:
                commit_msg = create_commit_message(prompt, md_file.name)
                git_commit_changes(commit_msg, logger)
            else:
                logger.info("Git commits disabled - skipping commit")
            
        except Exception as e:
            error_msg = f"Error executing prompt from {md_file.name}: {e}"
            logger.error(error_msg)
            print(f"Error: {e}")
        
        print("\n" + "=" * 80)
    
    logger.info("Completed processing all markdown files")
    print(f"\nCompleted! Check {log_file} for detailed logs.")

async def execute_json_workflow(json_file: Path, timeout: int = None):
    """Execute workflow defined in JSON file"""
    
    # Set up logging
    logger, log_file = setup_logging()
    logger.info("Starting Claude prompt execution session (JSON workflow)")
    logger.info(f"Log file: {log_file}")
    if timeout:
        logger.info(f"Global timeout set to: {timeout} seconds")
    
    if not json_file.exists():
        logger.error(f"JSON file not found: {json_file}")
        print(f"Error: JSON file not found: {json_file}")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {json_file}: {e}")
        print(f"Error: Invalid JSON in {json_file}: {e}")
        return
    except Exception as e:
        logger.error(f"Error reading JSON file {json_file}: {e}")
        print(f"Error reading JSON file {json_file}: {e}")
        return
    
    if 'ai_prompts' not in workflow_data:
        logger.error("JSON file must contain 'ai_prompts' key")
        print("Error: JSON file must contain 'ai_prompts' key")
        return
    
    ai_prompts = workflow_data['ai_prompts']
    if not isinstance(ai_prompts, list):
        logger.error("'ai_prompts' must be a list")
        print("Error: 'ai_prompts' must be a list")
        return
    
    # Sort by order
    ai_prompts.sort(key=lambda x: x.get('order', 0))
    
    logger.info(f"Found {len(ai_prompts)} prompts to process")
    print(f"Found {len(ai_prompts)} prompts to process")
    print(f"Logging to: {log_file}")
    print("=" * 80)
    
    # Process each prompt entry
    for i, prompt_entry in enumerate(ai_prompts, 1):
        if not isinstance(prompt_entry, dict):
            logger.warning(f"Skipping invalid prompt entry {i}: not a dictionary")
            print(f"Warning: Skipping invalid prompt entry {i}: not a dictionary")
            continue
        
        prompt_type = prompt_entry.get('type')
        prompt_value = prompt_entry.get('value')
        prompt_order = prompt_entry.get('order', i)
        prompt_timeout = prompt_entry.get('timeout', timeout)  # Use per-prompt timeout or global timeout
        
        if not prompt_type or not prompt_value:
            logger.warning(f"Skipping prompt entry {i}: missing 'type' or 'value'")
            print(f"Warning: Skipping prompt entry {i}: missing 'type' or 'value'")
            continue
        
        print(f"\n[{i}/{len(ai_prompts)}] Order {prompt_order}: {prompt_type.upper()} - {prompt_value}")
        print("-" * 60)
        
        logger.info(f"Processing entry {i}/{len(ai_prompts)} (order {prompt_order}): {prompt_type} - {prompt_value}")
        
        try:
            if prompt_type == 'file':
                file_path = Path(prompt_value)
                if not file_path.exists():
                    logger.error(f"File not found: {file_path}")
                    print(f"Error: File not found: {file_path}")
                    continue
                
                # Extract prompt from file
                prompt = extract_prompt_from_file(file_path)
                
                if not prompt:
                    logger.warning(f"No prompt content found in {file_path.name}")
                    print(f"Warning: No prompt content found in {file_path.name}")
                    continue
                
                logger.info(f"Extracted prompt from {file_path.name}: {prompt[:100]}...")
                print(f"File: {file_path.name}")
                print(f"Prompt: {prompt}")
                print("\nExecuting...")
                
                # Execute the prompt
                response = await execute_prompt_cli(prompt,verbose=True, timeout=prompt_timeout)
                
                # Check if the response indicates a timeout
                if response.startswith("Error: Command timed out"):
                    logger.warning(f"Prompt from {file_path.name} timed out after {prompt_timeout} seconds")
                    print(f"⚠️  Timeout: Prompt execution exceeded {prompt_timeout} seconds, moving to next prompt")
                    print(f"Response: {response}")
                    continue
                
                logger.info(f"Successfully executed prompt from {file_path.name}")
                logger.debug(f"Response: {response}")
                
                print(f"Response:")
                print(response)
                
                # Create git commit after successful execution
                if ENABLE_GIT_COMMITS:
                    commit_msg = create_commit_message(prompt, file_path.name)
                    git_commit_changes(commit_msg, logger)
                else:
                    logger.info("Git commits disabled - skipping commit")
                
            elif prompt_type == 'dir':
                directory = Path(prompt_value)
                if not directory.exists():
                    logger.error(f"Directory not found: {directory}")
                    print(f"Error: Directory not found: {directory}")
                    continue
                
                # Get all markdown files in directory
                md_files = sorted(list(directory.glob("*.md")))
                
                if not md_files:
                    logger.warning(f"No markdown files found in directory: {directory}")
                    print(f"Warning: No markdown files found in directory: {directory}")
                    continue
                
                print(f"Directory: {directory} ({len(md_files)} files)")
                
                # Process each markdown file in the directory
                for j, md_file in enumerate(md_files, 1):
                    print(f"\n  [{j}/{len(md_files)}] Processing: {md_file.name}")
                    
                    logger.info(f"Processing file {j}/{len(md_files)} in directory: {md_file.name}")
                    
                    # Extract prompt from file
                    prompt = extract_prompt_from_file(md_file)
                    
                    if not prompt:
                        logger.warning(f"No prompt content found in {md_file.name}")
                        print(f"Warning: No prompt content found in {md_file.name}")
                        continue
                    
                    logger.info(f"Extracted prompt from {md_file.name}: {prompt[:100]}...")
                    print(f"  Prompt: {prompt}")
                    print("  Executing...")
                    
                    # Execute the prompt
                    response = await execute_prompt_cli(prompt,verbose=True, timeout=prompt_timeout)
                    
                    # Check if the response indicates a timeout
                    if response.startswith("Error: Command timed out"):
                        logger.warning(f"Prompt from {md_file.name} timed out after {prompt_timeout} seconds")
                        print(f"  ⚠️  Timeout: Prompt execution exceeded {prompt_timeout} seconds, moving to next file")
                        print(f"  Response: {response}")
                        continue
                    
                    logger.info(f"Successfully executed prompt from {md_file.name}")
                    logger.debug(f"Response: {response}")
                    
                    print(f"  Response:")
                    print(f"  {response}")
                    
                    # Create git commit after successful execution
                    if ENABLE_GIT_COMMITS:
                        commit_msg = create_commit_message(prompt, md_file.name)
                        git_commit_changes(commit_msg, logger)
                    else:
                        logger.info("Git commits disabled - skipping commit")
                    
            else:
                logger.warning(f"Unknown prompt type: {prompt_type}")
                print(f"Warning: Unknown prompt type: {prompt_type}")
                continue
                
        except Exception as e:
            error_msg = f"Error executing prompt entry {i}: {e}"
            logger.error(error_msg)
            print(f"Error: {e}")
        
        print("\n" + "=" * 80)
    
    logger.info("Completed processing JSON workflow")
    print(f"\nCompleted! Check {log_file} for detailed logs.")

def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description="Execute prompts using claude_prompt_executor.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python ai_workflow_runner.py --file prompt.md\n"
               "  python ai_workflow_runner.py --dir templates/\n"
               "  python ai_workflow_runner.py --json workflow.json\n"
               "  python ai_workflow_runner.py --dir samples/"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', type=str, help='Execute prompt from a single file')
    group.add_argument('--dir', type=str, help='Execute prompts from all markdown files in a directory')
    group.add_argument('--json', type=str, help='Execute workflow defined in JSON file')
    
    parser.add_argument('--timeout', type=int, help='Timeout in seconds for each prompt execution (default: no timeout)')
    
    args = parser.parse_args()
    
    try:
        if args.file:
            file_path = Path(args.file)
            asyncio.run(execute_single_file(file_path, timeout=args.timeout))
        elif args.dir:
            directory = Path(args.dir)
            asyncio.run(execute_directory_files(directory, timeout=args.timeout))
        elif args.json:
            json_file = Path(args.json)
            asyncio.run(execute_json_workflow(json_file, timeout=args.timeout))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()