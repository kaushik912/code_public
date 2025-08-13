#!/usr/bin/env python3
"""
Dependency Graph Workflow Orchestrator

Orchestrates the complete dependency graph analysis workflow by executing
a series of scripts in the correct order with proper input/output handling.
"""

import argparse
import subprocess
import sys
import os
import json
from pathlib import Path


def run_command(command, description):
    """Execute a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"EXECUTING: {description}")
    print(f"COMMAND: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False


def load_workflow_config(script_dir):
    """Load workflow configuration from JSON file."""
    config_path = script_dir / "template/dep_graph_flow/depgraph_orchestrator.json"
    if not config_path.exists():
        print(f"Error: Configuration file {config_path} does not exist")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config["workflow_steps"]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error: Invalid configuration file format: {e}")
        sys.exit(1)


def substitute_parameters(workflow_steps, dep_graph_path):
    """Substitute parameters in workflow steps."""
    substituted_steps = []
    
    for step in workflow_steps:
        substituted_command = []
        for arg in step["command"]:
            # Replace placeholders with actual values
            arg = arg.replace("{dep_graph_path}", str(dep_graph_path))
            substituted_command.append(arg)
        
        substituted_steps.append({
            "command": substituted_command,
            "description": step["description"]
        })
    
    return substituted_steps


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate dependency graph workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "dep_graph_json",
        help="Path to dep_graph.json input file"
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue execution even if a step fails"
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    dep_graph_path = Path(args.dep_graph_json)
    if not dep_graph_path.exists():
        print(f"Error: Input file {dep_graph_path} does not exist")
        sys.exit(1)
    
    # Get the current working directory where this script is invoked from
    script_dir = Path.cwd()
    
    # Load workflow steps from configuration file
    workflow_steps = load_workflow_config(script_dir)
    
    # Substitute parameters in workflow steps
    workflow_steps = substitute_parameters(workflow_steps, dep_graph_path)
    
    print(f"Starting dependency graph workflow orchestration")
    print(f"Input file: {dep_graph_path}")
    print(f"Total steps: {len(workflow_steps)}")
    
    failed_steps = []
    
    # Execute each step in sequence
    for i, step in enumerate(workflow_steps, 1):
        print(f"\n\nSTEP {i}/{len(workflow_steps)}")
        
        success = run_command(step["command"], step["description"])
        
        if not success:
            failed_steps.append((i, step["description"]))
            if not args.continue_on_error:
                print(f"\n✗ Workflow failed at step {i}. Use --continue-on-error to continue despite failures.")
                sys.exit(1)
    
    # Final summary
    print(f"\n\n{'='*60}")
    print("WORKFLOW SUMMARY")
    print(f"{'='*60}")
    
    if failed_steps:
        print(f"✗ Workflow completed with {len(failed_steps)} failed steps:")
        for step_num, description in failed_steps:
            print(f"  Step {step_num}: {description}")
        sys.exit(1)
    else:
        print("✓ All workflow steps completed successfully!")
        print("Dependency graph workflow orchestration finished.")


if __name__ == "__main__":
    main()