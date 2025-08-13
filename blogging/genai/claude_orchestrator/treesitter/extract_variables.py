import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser, Node
import json
import sys
import os

def extract_variables(code: str) -> list:
    """Extract variable declarations from C++ code and return as JSON format."""
    
    # Set up the parser
    cpp_language_capsule = tscpp.language()
    CPP_LANGUAGE = Language(cpp_language_capsule)
    parser = Parser()
    parser.language = CPP_LANGUAGE
    
    # Parse the code
    tree = parser.parse(code.encode('utf-8'))
    
    variables = []
    
    def visit_node(node: Node):
        """Recursively visit nodes to find variable declarations."""
        
        # Look for regular declaration nodes
        if node.type == 'declaration':
            # Get the type and declarator
            type_node = None
            declarator_node = None
            
            for child in node.children:
                if child.type in ['primitive_type', 'type_identifier', 'qualified_identifier']:
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
                if child.type in ['primitive_type', 'type_identifier', 'qualified_identifier']:
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
            visit_node(child)
    
    visit_node(tree.root_node)
    return variables

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

def extract_variables_with_parent(file_path: str) -> dict:
    """Extract variables from a file and its parent class if no variables found."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        return {"error": f"Error reading file: {e}"}
    
    # Extract variables from current file
    variables = extract_variables(code)
    
    result = {
        "current_file": file_path,
        "variables": variables,
        "parent_info": None
    }
    
    # If no variables found, try to find parent class
    if not variables:
        parent_class = extract_parent_class(code)
        if parent_class:
            parent_file = find_header_file(parent_class, "cpp_source/Core-R")
            if parent_file:
                try:
                    with open(parent_file, 'r', encoding='utf-8') as f:
                        parent_code = f.read()
                    parent_variables = extract_variables(parent_code)
                    
                    result["parent_info"] = {
                        "parent_class": parent_class,
                        "parent_file": parent_file,
                        "parent_variables": parent_variables
                    }
                    
                    # Use parent variables as the main result
                    result["variables"] = parent_variables
                    
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
    result = extract_variables_with_parent(file_path)
    output = json.dumps(result, indent=2)
    print(output)

if __name__ == "__main__":
    main()