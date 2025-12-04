#!/usr/bin/env python3
"""
TypeResolutor.py - Resolves variable types from method invocations in parsed C++ code

This script analyzes method invocations in a JSON file (from treesitter parsing)
and resolves variable types by looking up local variable declarations.

For method calls with single dot or arrow notation (e.g., "variable.method", "ptr->func"), it:
1. Extracts the variable name from the method_name
2. Searches for the variable declaration using multiple lookup strategies
3. Returns the resolved type information
"""

import json
import sys
from typing import Dict, List, Optional, Tuple


class TypeResolutor:
    def __init__(self, json_file_path: str):
        """Initialize with JSON data from file"""
        with open(json_file_path, 'r') as f:
            self.data = json.load(f)
        
        self.method_invocations = self.data.get('method_invocations', {})
        self.method_local_variables = self.data.get('method_local_variables', {})
        self.methods = self.data.get('methods', [])
        self.member_initializer_variables = self.data.get('member_initializer_variables', [])
        self.variables = self.data.get('variables', [])
        
    def extract_variable_name(self, method_name: str) -> Optional[str]:
        """
        Extract variable name from method_name with single dot or arrow
        e.g., "a.b" -> "a", "obj.method" -> "obj", "ptr->func" -> "ptr"
        Returns None if not single dot or arrow pattern
        """
        if method_name.count('.') == 1 and '->' not in method_name:
            return method_name.split('.')[0]
        elif method_name.count('->') == 1 and '.' not in method_name:
            return method_name.split('->')[0]
        return None
    
    def find_in_local_variables(self, method_name: str, variable_name: str, 
                               line_number: int) -> Optional[Dict]:
        """
        Strategy 1: Find variable in local method declarations
        """
        if method_name not in self.method_local_variables:
            return None
            
        variables = self.method_local_variables[method_name]
        
        # Find all declarations of this variable before the line
        candidates = []
        for var in variables:
            if var['name'] == variable_name and var['line'] < line_number:
                candidates.append(var)
        
        # Return the one with the highest line number (nearest)
        if candidates:
            result = max(candidates, key=lambda x: x['line'])
            result['lookup_strategy'] = 'local_variables'
            return result
        
        return None
    
    def find_in_method_parameters(self, method_name: str, variable_name: str) -> Optional[Dict]:
        """
        Strategy 2: Find variable in method parameters
        """
        for method in self.methods:
            if method['name'] == method_name:
                for param in method.get('parameters', []):
                    if param['name'] == variable_name:
                        return {
                            'name': variable_name,
                            'type': param['type'],
                            'line': method['line_start'],
                            'lookup_strategy': 'method_parameters'
                        }
        return None
    
    def find_in_member_initializer_variables(self, variable_name: str) -> Optional[Dict]:
        """
        Strategy 3: Find variable in member initializer variables
        """
        for var in self.member_initializer_variables:
            if var['name'] == variable_name:
                return {
                    'name': variable_name,
                    'type': var['type'],
                    'line': var['line'],
                    'lookup_strategy': 'member_initializer_variables'
                }
        return None
    
    def find_in_global_variables(self, variable_name: str) -> Optional[Dict]:
        """
        Strategy 4: Find variable in global variables list
        """
        for var in self.variables:
            if var['name'] == variable_name:
                return {
                    'name': variable_name,
                    'type': var.get('type', 'unknown'),
                    'line': var.get('line', 0),
                    'lookup_strategy': 'global_variables'
                }
        return None
    
    def resolve_variable_type(self, method_name: str, variable_name: str, 
                             line_number: int) -> Optional[Dict]:
        """
        Use three-lookup strategy to resolve variable type:
        1. Local method declarations
        2. Method parameters
        3. Member initializer variables
        4. Global variables
        """
        # Strategy 1: Local variables
        result = self.find_in_local_variables(method_name, variable_name, line_number)
        if result:
            return result
        
        # Strategy 2: Method parameters
        result = self.find_in_method_parameters(method_name, variable_name)
        if result:
            return result
        
        # Strategy 3: Member initializer variables
        result = self.find_in_member_initializer_variables(variable_name)
        if result:
            return result
        
        # Strategy 4: Global variables
        result = self.find_in_global_variables(variable_name)
        if result:
            return result
        
        return None
    
    def resolve_types_for_method(self, method_name: str) -> List[Dict]:
        """
        Resolve types for all method invocations in a specific method
        """
        if method_name not in self.method_invocations:
            return []
            
        results = []
        invocations = self.method_invocations[method_name]
        
        for invocation in invocations:
            call_method_name = invocation['method_name']
            line = invocation['line']
            
            # Extract variable name from method call
            variable_name = self.extract_variable_name(call_method_name)
            
            if variable_name:
                # Use enhanced lookup strategy
                var_declaration = self.resolve_variable_type(
                    method_name, variable_name, line
                )
                
                result = {
                    'method_name': method_name,
                    'method_call': call_method_name,
                    'line': line,
                    'variable_name': variable_name,
                    'resolved_type': var_declaration['type'] if var_declaration else None,
                    'declaration_line': var_declaration['line'] if var_declaration else None,
                    'lookup_strategy': var_declaration['lookup_strategy'] if var_declaration else None,
                    'declaration_found': var_declaration is not None
                }
                results.append(result)
        
        return results
    
    def resolve_all_types(self) -> Dict:
        """
        Resolve types for all methods in the file
        """
        method_results = {}
        
        for method_name in self.method_invocations.keys():
            results = self.resolve_types_for_method(method_name)
            if results:  # Only include methods with resolvable types
                method_results[method_name] = results
        
        # Return structure with file_name field
        return {
            'file_name': self.data.get('current_file', 'Unknown file'),
            'type_resolutions': method_results
        }
    
    def print_summary(self, results: Dict):
        """
        Print a summary of type resolution results
        """
        total_calls = 0
        resolved_calls = 0
        strategy_counts = {
            'local_variables': 0,
            'method_parameters': 0,
            'member_initializer_variables': 0,
            'global_variables': 0
        }
        
        file_name = results.get('file_name', 'Unknown file')
        type_resolutions = results.get('type_resolutions', {})
        
        print(f"Type Resolution Summary for: {file_name}")
        print("=" * 80)
        
        for method_name, method_results in type_resolutions.items():
            print(f"\nMethod: {method_name}")
            print("-" * 60)
            
            for result in method_results:
                total_calls += 1
                if result['declaration_found']:
                    resolved_calls += 1
                    strategy = result['lookup_strategy']
                    if strategy in strategy_counts:
                        strategy_counts[strategy] += 1
                    
                status = "✓" if result['declaration_found'] else "✗"
                print(f"  {status} Line {result['line']:3}: {result['method_call']}")
                print(f"    Variable: {result['variable_name']}")
                
                if result['declaration_found']:
                    strategy_display = result['lookup_strategy'].replace('_', ' ').title()
                    print(f"    Type: {result['resolved_type']} (from {strategy_display} at line {result['declaration_line']})")
                else:
                    print(f"    Type: UNRESOLVED")
                print()
        
        print(f"Resolution Statistics:")
        print(f"  Total single-dot/arrow method calls: {total_calls}")
        print(f"  Successfully resolved: {resolved_calls}")
        print(f"  Resolution rate: {(resolved_calls/total_calls*100):.1f}%" if total_calls > 0 else "N/A")
        print(f"\nResolution by Strategy:")
        for strategy, count in strategy_counts.items():
            strategy_display = strategy.replace('_', ' ').title()
            percentage = (count/resolved_calls*100) if resolved_calls > 0 else 0
            print(f"  {strategy_display}: {count} ({percentage:.1f}%)")


def main():
    if len(sys.argv) != 2:
        print("Usage: python TypeResolutor.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    try:
        resolver = TypeResolutor(json_file)
        results = resolver.resolve_all_types()
        
        # Print detailed results
        resolver.print_summary(results)
        
        # Optionally save results to JSON
        output_file = json_file.replace('.json', '_type_resolved.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{json_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()