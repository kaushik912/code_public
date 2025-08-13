#!/usr/bin/env python3
"""
Deterministic Task Pipeline
A configurable pipeline to run deterministic tools in sequence.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime


class TaskPipeline:
    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self.results = []
        self.default_tasks = [
            {
                "name": "Generate App Skeleton",
                "command": ["bash", "tools/skeleton/generate_app.sh"],
                "description": "Generate Raptor application skeleton using Maven archetype",
                "timeout": 300,
                "continue_on_failure": False
            },
            {
                "name": "Extract Downstream Interfaces",
                "command": ["python3", "tools/downstream_interfaces/extract_downstream_interfaces.py"],
                "description": "Extract downstream interface definitions",
                "timeout": 120,
                "continue_on_failure": True
            },
            {
                "name": "Run DB Generator",
                "command": ["bash", "tools/db/run_db_generator.sh"],
                "description": "Run database code generation",
                "timeout": 180,
                "continue_on_failure": True
            }
        ]
    
    def load_config(self) -> List[Dict[str, Any]]:
        """Load task configuration from file or use defaults"""
        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('tasks', self.default_tasks)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading config file {self.config_file}: {e}")
                print("Using default task configuration")
                return self.default_tasks
        else:
            return self.default_tasks
    
    def save_default_config(self, output_file: str = "pipeline_config.json"):
        """Save default configuration to a JSON file"""
        config = {
            "description": "Deterministic Task Pipeline Configuration",
            "tasks": self.default_tasks
        }
        
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Default configuration saved to {output_file}")
    
    def validate_task(self, task: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a task configuration"""
        required_fields = ['name', 'command']
        for field in required_fields:
            if field not in task:
                return False, f"Missing required field: {field}"
        
        if not isinstance(task['command'], list):
            return False, "Command must be a list"
        
        if len(task['command']) == 0:
            return False, "Command cannot be empty"
        
        return True, ""
    
    def run_task(self, task: Dict[str, Any]) -> Tuple[bool, str, str]:
        """Run a single task"""
        task_name = task['name']
        command = task['command']
        timeout = task.get('timeout', 120)
        description = task.get('description', '')
        
        print(f"\n🔄 Running task: {task_name}")
        if description:
            print(f"   Description: {description}")
        print(f"   Command: {' '.join(command)}")
        print(f"   Timeout: {timeout}s")
        
        try:
            # Check if the command file exists for script commands
            if command[0] in ['python3', 'python', 'bash', 'sh']:
                script_path = Path(command[1]) if len(command) > 1 else None
                if script_path and not script_path.exists():
                    return False, f"Script not found: {script_path}", ""
            
            # Run the command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                print(f"   ✅ Task completed successfully")
                if result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()[:200]}...")
                return True, result.stdout, result.stderr
            else:
                print(f"   ❌ Task failed with return code {result.returncode}")
                if result.stderr.strip():
                    print(f"   Error: {result.stderr.strip()[:200]}...")
                return False, result.stdout, result.stderr
        
        except subprocess.TimeoutExpired:
            error_msg = f"Task timed out after {timeout} seconds"
            print(f"   ⏰ {error_msg}")
            return False, "", error_msg
        
        except FileNotFoundError:
            error_msg = f"Command not found: {command[0]}"
            print(f"   ❌ {error_msg}")
            return False, "", error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"   ❌ {error_msg}")
            return False, "", error_msg
    
    def run_pipeline(self) -> bool:
        """Run the complete task pipeline"""
        print("🚀 Starting Deterministic Task Pipeline")
        print("=" * 80)
        
        # Load task configuration
        tasks = self.load_config()
        
        if not tasks:
            print("❌ No tasks configured")
            return False
        
        print(f"Loaded {len(tasks)} tasks to execute")
        
        # Validate all tasks first
        for i, task in enumerate(tasks, 1):
            valid, error = self.validate_task(task)
            if not valid:
                print(f"❌ Task {i} validation failed: {error}")
                return False
        
        # Execute tasks in sequence
        successful_tasks = 0
        failed_tasks = 0
        
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] Executing: {task['name']}")
            print("-" * 60)
            
            success, stdout, stderr = self.run_task(task)
            
            # Store result
            result = {
                "task_name": task['name'],
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "command": ' '.join(task['command']),
                "description": task.get('description', '')
            }
            self.results.append(result)
            
            if success:
                successful_tasks += 1
            else:
                failed_tasks += 1
                # Check if we should continue on failure
                continue_on_failure = task.get('continue_on_failure', False)
                if not continue_on_failure:
                    print(f"   ⛔ Pipeline stopped due to task failure (continue_on_failure=False)")
                    break
                else:
                    print(f"   ⚠️  Continuing despite failure (continue_on_failure=True)")
        
        # Print summary
        self.print_summary(successful_tasks, failed_tasks, len(tasks))
        
        return failed_tasks == 0
    
    def print_summary(self, successful_tasks: int, failed_tasks: int, total_tasks: int):
        """Print pipeline execution summary"""
        print("\n" + "=" * 80)
        print("📊 PIPELINE SUMMARY")
        print("=" * 80)
        
        print(f"Total tasks: {total_tasks}")
        print(f"Successful: {successful_tasks}")
        print(f"Failed: {failed_tasks}")
        print(f"Success rate: {(successful_tasks/total_tasks)*100:.1f}%")
        
        print("\nDetailed Results:")
        for i, result in enumerate(self.results, 1):
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"  [{i}] {status} {result['task_name']}")
            if not result["success"] and result["stderr"]:
                print(f"       Error: {result['stderr'][:100]}...")
        
        # Overall result
        if failed_tasks == 0:
            print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY! All {successful_tasks} tasks passed.")
        else:
            print(f"\n⚠️  PIPELINE COMPLETED WITH FAILURES: {failed_tasks} of {total_tasks} tasks failed.")
    
    def save_results(self, output_file: str = None):
        """Save pipeline results to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"pipeline_results_{timestamp}.json"
        
        results_data = {
            "pipeline_execution": {
                "timestamp": datetime.now().isoformat(),
                "total_tasks": len(self.results),
                "successful_tasks": sum(1 for r in self.results if r["success"]),
                "failed_tasks": sum(1 for r in self.results if not r["success"])
            },
            "task_results": self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to {output_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Deterministic Task Pipeline - Run configurable tools in sequence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python deterministic_task_pipeline.py\n"
               "  python deterministic_task_pipeline.py --config my_tasks.json\n"
               "  python deterministic_task_pipeline.py --save-config\n"
               "  python deterministic_task_pipeline.py --save-results results.json"
    )
    
    parser.add_argument('--config', '-c', type=str, 
                       help='JSON configuration file with task definitions')
    parser.add_argument('--save-config', action='store_true',
                       help='Save default configuration to pipeline_config.json and exit')
    parser.add_argument('--save-results', type=str, 
                       help='Save execution results to specified JSON file')
    
    args = parser.parse_args()
    
    # Create pipeline instance
    pipeline = TaskPipeline(config_file=args.config)
    
    # Handle save-config option
    if args.save_config:
        pipeline.save_default_config()
        return
    
    try:
        # Run the pipeline
        success = pipeline.run_pipeline()
        
        # Save results if requested
        if args.save_results:
            pipeline.save_results(args.save_results)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⛔ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()