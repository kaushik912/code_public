import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser, Node
import json
import sys
import os

def extract_code_elements(code: str) -> dict:
    """Extract variables, method declarations, and method invocations from C++ code and return as JSON format."""
    
    # Set up the parser
    cpp_language_capsule = tscpp.language()
    CPP_LANGUAGE = Language(cpp_language_capsule)
    parser = Parser()
    parser.language = CPP_LANGUAGE
    
    # Parse the code
    tree = parser.parse(code.encode('utf-8'))
    
    variables = []
    methods = []
    member_initializer_variables = []
    current_method = None
    method_invocations = {}
    method_local_variables = {}
    
    def visit_node(node: Node, parent_method=None):
        """Recursively visit nodes to find variable declarations, method declarations, and invocations."""
        
        nonlocal current_method
        
        # Look for method declarations
        if node.type == 'function_definition':
            method_info = extract_method_declaration(node, code)
            if method_info:
                methods.append(method_info)
                current_method = method_info['name']
                method_invocations[current_method] = []
                method_local_variables[current_method] = []
                
                # Extract member initializer list if this is a constructor
                initializer_vars = extract_member_initializer_list(node, code, method_info.get('parameters', []))
                if initializer_vars:
                    member_initializer_variables.extend(initializer_vars)
                
                # Visit function body to find invocations and local variables
                for child in node.children:
                    if child.type == 'compound_statement':
                        visit_node(child, current_method)
                        
                current_method = None
                return
                
        # Look for method invocations
        elif node.type == 'call_expression' and parent_method:
            invocation = extract_method_invocation(node, code)
            if invocation and parent_method in method_invocations:
                method_invocations[parent_method].append(invocation)
        
        # Look for local variable declarations within methods
        elif node.type == 'declaration' and parent_method:
            local_var = extract_local_variable_declaration(node, code)
            if local_var and parent_method in method_local_variables:
                method_local_variables[parent_method].append(local_var)
        
        # Look for regular declaration nodes (class-level variables)
        elif node.type == 'declaration' and not parent_method:
            # Get the type and declarator
            type_node = None
            declarator_node = None
            
            for child in node.children:
                if child.type in ['primitive_type', 'type_identifier', 'qualified_identifier', 'template_type']:
                    type_node = child
                elif child.type == 'init_declarator':
                    declarator_node = child
                elif child.type == 'identifier':
                    # Simple declaration without initialization
                    declarator_node = child
            
            if type_node and declarator_node:
                var_type = code[type_node.start_byte:type_node.end_byte]
                
                # Handle init_declarator (variable with initialization)
                if declarator_node.type == 'init_declarator':
                    for child in declarator_node.children:
                        if child.type == 'identifier':
                            var_name = code[child.start_byte:child.end_byte]
                            variables.append({
                                "name": var_name,
                                "type": var_type
                            })
                            break
                # Handle simple identifier
                elif declarator_node.type == 'identifier':
                    var_name = code[declarator_node.start_byte:declarator_node.end_byte]
                    variables.append({
                        "name": var_name,
                        "type": var_type
                    })
        
        # Look for struct/class field declarations
        elif node.type == 'field_declaration':
            type_node = None
            field_node = None
            type_qualifiers = []
            
            for child in node.children:
                if child.type in ['primitive_type', 'type_identifier', 'qualified_identifier', 'template_type']:
                    type_node = child
                elif child.type == 'field_identifier':
                    field_node = child
                elif child.type == 'type_qualifier':
                    type_qualifiers.append(code[child.start_byte:child.end_byte])
                elif child.type == 'pointer_declarator':
                    # Handle pointer declarations like "const PimpXClick* xclick"
                    for grandchild in child.children:
                        if grandchild.type == 'field_identifier':
                            field_node = grandchild
            
            if type_node and field_node:
                var_type = code[type_node.start_byte:type_node.end_byte]
                if type_qualifiers:
                    var_type = ' '.join(type_qualifiers) + ' ' + var_type
                
                # Check if it's a pointer
                pointer_parent = field_node.parent
                if pointer_parent and pointer_parent.type == 'pointer_declarator':
                    var_type += '*'
                
                var_name = code[field_node.start_byte:field_node.end_byte]
                variables.append({
                    "name": var_name,
                    "type": var_type
                })
        
        # Recursively visit children
        for child in node.children:
            visit_node(child, parent_method)
    
    def extract_method_declaration(node: Node, code: str) -> dict:
        """Extract method declaration information."""
        method_name = None
        return_type = None
        parameters = []
        
        for child in node.children:
            if child.type == 'function_declarator':
                # Extract method name and parameters
                for grandchild in child.children:
                    if grandchild.type == 'identifier':
                        method_name = code[grandchild.start_byte:grandchild.end_byte]
                    elif grandchild.type == 'qualified_identifier':
                        # Handle qualified method names like PimpInternal::Event::method_name
                        method_name = code[grandchild.start_byte:grandchild.end_byte]
                    elif grandchild.type == 'parameter_list':
                        parameters = extract_parameters(grandchild, code)
            elif child.type in ['primitive_type', 'type_identifier', 'qualified_identifier']:
                return_type = code[child.start_byte:child.end_byte]
        
        if method_name:
            return {
                'name': method_name,
                'return_type': return_type or 'void',
                'parameters': parameters,
                'line_start': node.start_point[0] + 1,
                'line_end': node.end_point[0] + 1
            }
        return None
    
    def extract_parameters(param_list_node: Node, code: str) -> list:
        """Extract parameter information from parameter list."""
        parameters = []
        
        for child in param_list_node.children:
            if child.type == 'parameter_declaration':
                param_type = None
                param_name = None
                
                for grandchild in child.children:
                    if grandchild.type in ['primitive_type', 'type_identifier', 'qualified_identifier']:
                        param_type = code[grandchild.start_byte:grandchild.end_byte]
                    elif grandchild.type == 'identifier':
                        param_name = code[grandchild.start_byte:grandchild.end_byte]
                    elif grandchild.type == 'reference_declarator':
                        # Handle reference parameters
                        for ggchild in grandchild.children:
                            if ggchild.type == 'identifier':
                                param_name = code[ggchild.start_byte:ggchild.end_byte]
                        if param_type:
                            param_type += '&'
                    elif grandchild.type == 'pointer_declarator':
                        # Handle pointer parameters
                        for ggchild in grandchild.children:
                            if ggchild.type == 'identifier':
                                param_name = code[ggchild.start_byte:ggchild.end_byte]
                        if param_type:
                            param_type += '*'
                
                if param_type and param_name:
                    parameters.append({
                        'type': param_type,
                        'name': param_name
                    })
                elif param_type:  # Handle cases where only type is present
                    parameters.append({
                        'type': param_type,
                        'name': ''
                    })
        
        return parameters
    
    def extract_method_invocation(node: Node, code: str) -> dict:
        """Extract method invocation information."""
        method_name = None
        arguments = []
        
        for child in node.children:
            if child.type == 'identifier':
                method_name = code[child.start_byte:child.end_byte]
            elif child.type == 'field_expression':
                # Handle object.method() calls
                method_name = code[child.start_byte:child.end_byte]
            elif child.type == 'qualified_identifier':
                # Handle namespace::method() calls
                method_name = code[child.start_byte:child.end_byte]
            elif child.type == 'argument_list':
                arguments = extract_arguments(child, code)
        
        if method_name:
            return {
                'method_name': method_name,
                'arguments': arguments,
                'line': node.start_point[0] + 1
            }
        return None
    
    def extract_arguments(arg_list_node: Node, code: str) -> list:
        """Extract argument information from argument list."""
        arguments = []
        
        for child in arg_list_node.children:
            if child.type not in ['(', ')', ',']:
                arg_text = code[child.start_byte:child.end_byte]
                arguments.append(arg_text)
        
        return arguments
    
    def extract_member_initializer_list(node: Node, code: str, parameters: list) -> list:
        """Extract member variables from member initializer list in constructors."""
        initializer_vars = []
        
        # Create a mapping from parameter names to their types (removing leading underscore if present)
        param_type_map = {}
        for param in parameters:
            param_name = param.get('name', '')
            param_type = param.get('type', '')
            # Map both with and without leading underscore
            if param_name.startswith('_'):
                member_name = 'm' + param_name  # _th -> m_th, _context -> m_context
                param_type_map[member_name] = param_type
            param_type_map[param_name] = param_type
        
        for child in node.children:
            if child.type == 'field_initializer_list':
                for grandchild in child.children:
                    if grandchild.type == 'field_initializer':
                        # Extract member variable name and initialization value
                        var_name = None
                        initialization = None
                        
                        for ggchild in grandchild.children:
                            if ggchild.type == 'field_identifier':
                                var_name = code[ggchild.start_byte:ggchild.end_byte]
                            elif ggchild.type == 'argument_list':
                                # Extract the initialization expression
                                initialization = code[ggchild.start_byte:ggchild.end_byte]
                        
                        if var_name:
                            # Try to find the corresponding parameter type
                            var_type = param_type_map.get(var_name, "member_variable")
                            
                            # If not found, try to infer from initialization parameter
                            if var_type == "member_variable" and initialization:
                                # Extract parameter name from initialization (e.g., "(_th)" -> "_th")
                                init_param = initialization.strip('()')
                                var_type = param_type_map.get(init_param, "member_variable")
                            
                            initializer_vars.append({
                                "name": var_name,
                                "type": var_type,
                                "initialization": initialization or "",
                                "line": grandchild.start_point[0] + 1
                            })
        
        return initializer_vars
    
    def extract_local_variable_declaration(node: Node, code: str) -> dict:
        """Extract local variable declaration information."""
        type_node = None
        declarator_node = None
        initialization = None
        type_qualifiers = []
        
        assignment_found = False
        assignment_value = None
        
        for child in node.children:
            if child.type in ['primitive_type', 'type_identifier', 'qualified_identifier', 'template_type']:
                type_node = child
            elif child.type == 'type_qualifier':
                type_qualifiers.append(code[child.start_byte:child.end_byte])
            elif child.type == 'init_declarator':
                declarator_node = child
            elif child.type == 'reference_declarator':
                # Handle reference declarations like "const TxnNotificationInfoVO & txn_notification_info"
                declarator_node = child
            elif child.type == 'function_declarator':
                # Handle constructor-style declarations like "PayIPNProcessor process_ipn(m_th, m_context)"
                declarator_node = child
            elif child.type == 'identifier':
                # Simple declaration without initialization
                declarator_node = child
            elif child.type == '=':
                assignment_found = True
            elif assignment_found and child.type not in [';']:
                # This is the initialization value after =
                assignment_value = code[child.start_byte:child.end_byte]
        
        if type_node and declarator_node:
            var_type = code[type_node.start_byte:type_node.end_byte]
            if type_qualifiers:
                var_type = ' '.join(type_qualifiers) + ' ' + var_type
            var_name = None
            
            # Handle reference_declarator
            if declarator_node.type == 'reference_declarator':
                var_type += '&'
                for child in declarator_node.children:
                    if child.type == 'identifier':
                        var_name = code[child.start_byte:child.end_byte]
                        break
            
            # Handle init_declarator (variable with initialization)
            elif declarator_node.type == 'init_declarator':
                for child in declarator_node.children:
                    if child.type == 'identifier':
                        var_name = code[child.start_byte:child.end_byte]
                    elif child.type == 'pointer_declarator':
                        # Handle pointer declarations like "* impl"
                        var_type += '*'
                        for grandchild in child.children:
                            if grandchild.type == 'identifier':
                                var_name = code[grandchild.start_byte:grandchild.end_byte]
                    elif child.type == 'reference_declarator':
                        # Handle reference inside init_declarator
                        var_type += '&'
                        for grandchild in child.children:
                            if grandchild.type == 'identifier':
                                var_name = code[grandchild.start_byte:grandchild.end_byte]
                    elif child.type == '=' or child.type == 'assignment_expression':
                        # Find the initialization expression
                        next_sibling = child.next_sibling
                        if next_sibling:
                            initialization = code[next_sibling.start_byte:next_sibling.end_byte]
                        break
                    elif child.type == 'call_expression':
                        initialization = code[child.start_byte:child.end_byte]
                
                # If we didn't find initialization through assignment, look for method calls
                if not initialization:
                    for child in declarator_node.children:
                        if child.type == 'call_expression':
                            initialization = code[child.start_byte:child.end_byte]
                            break
                        elif child.type not in ['identifier', '=', 'reference_declarator', 'pointer_declarator']:
                            initialization = code[child.start_byte:child.end_byte]
                            break
            # Handle function_declarator (constructor-style declarations)
            elif declarator_node.type == 'function_declarator':
                for child in declarator_node.children:
                    if child.type == 'identifier':
                        var_name = code[child.start_byte:child.end_byte]
                    elif child.type == 'parameter_list':
                        # Constructor arguments become the initialization
                        initialization = code[child.start_byte:child.end_byte]
                        break
            # Handle simple identifier
            elif declarator_node.type == 'identifier':
                var_name = code[declarator_node.start_byte:declarator_node.end_byte]
            
            if var_name:
                result = {
                    "name": var_name,
                    "type": var_type,
                    "line": node.start_point[0] + 1
                }
                # Use assignment_value if found, otherwise use initialization
                if assignment_value:
                    result["initialization"] = assignment_value
                elif initialization:
                    result["initialization"] = initialization
                return result
        
        return None
    
    visit_node(tree.root_node)
    
    return {
        'variables': variables,
        'methods': methods,
        'member_initializer_variables': member_initializer_variables,
        'method_invocations': method_invocations,
        'method_local_variables': method_local_variables
    }

def extract_parent_class(code: str) -> str:
    """Extract the parent class name from C++ inheritance using tree-sitter."""
    
    # Set up the parser
    cpp_language_capsule = tscpp.language()
    CPP_LANGUAGE = Language(cpp_language_capsule)
    parser = Parser()
    parser.language = CPP_LANGUAGE
    
    # Parse the code
    tree = parser.parse(code.encode('utf-8'))
    
    def visit_node(node: Node):
        """Recursively visit nodes to find class declarations with inheritance."""
        
        if node.type == 'class_specifier':
            # Look for base_class_clause
            for child in node.children:
                if child.type == 'base_class_clause':
                    # Find the parent class identifier
                    for grandchild in child.children:
                        if grandchild.type == 'type_identifier':
                            return code[grandchild.start_byte:grandchild.end_byte]
        
        # Recursively visit children
        for child in node.children:
            result = visit_node(child)
            if result:
                return result
        
        return None
    
    return visit_node(tree.root_node)

def find_header_file(class_name: str, search_dir: str) -> str:
    """Find the header file for a given class name in the search directory."""
    
    header_filename = f"{class_name}.h"
    
    for root, dirs, files in os.walk(search_dir):
        if header_filename in files:
            return os.path.join(root, header_filename)
    
    return None

def extract_code_elements_with_parent(file_path: str) -> dict:
    """Extract code elements from a file and its parent class if no variables found."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        return {"error": f"Error reading file: {e}"}
    
    # Extract code elements from current file
    code_elements = extract_code_elements(code)
    
    result = {
        "current_file": file_path,
        "variables": code_elements['variables'],
        "methods": code_elements['methods'],
        "member_initializer_variables": code_elements['member_initializer_variables'],
        "method_invocations": code_elements['method_invocations'],
        "method_local_variables": code_elements['method_local_variables'],
        "parent_info": None
    }
    
    # If no variables found, try to find parent class
    if not code_elements['variables']:
        parent_class = extract_parent_class(code)
        if parent_class:
            parent_file = find_header_file(parent_class, "cpp_source/Core-R")
            if parent_file:
                try:
                    with open(parent_file, 'r', encoding='utf-8') as f:
                        parent_code = f.read()
                    parent_elements = extract_code_elements(parent_code)
                    
                    result["parent_info"] = {
                        "parent_class": parent_class,
                        "parent_file": parent_file,
                        "parent_variables": parent_elements['variables'],
                        "parent_methods": parent_elements['methods'],
                        "parent_member_initializer_variables": parent_elements['member_initializer_variables'],
                        "parent_method_invocations": parent_elements['method_invocations'],
                        "parent_method_local_variables": parent_elements['method_local_variables']
                    }
                    
                    # Use parent variables as the main result
                    result["variables"] = parent_elements['variables']
                    
                except Exception as e:
                    result["parent_info"] = {
                        "parent_class": parent_class,
                        "parent_file": parent_file,
                        "error": f"Error reading parent file: {e}"
                    }
            else:
                result["parent_info"] = {
                    "parent_class": parent_class,
                    "error": "Parent header file not found"
                }
    
    return result

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_variables.py <cpp_file>", file=sys.stderr)
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Always use the enhanced function that handles parent classes
    result = extract_code_elements_with_parent(file_path)
    output = json.dumps(result, indent=2)
    print(output)

if __name__ == "__main__":
    main()