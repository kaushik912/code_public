import tree_sitter_java as tsjava
from tree_sitter import Language, Parser, Node
import json
import sys
import argparse

def extract_java_fields(code: str) -> list:
    """Extract field declarations from Java code and return as JSON format."""
    
    # Set up the parser
    java_language_capsule = tsjava.language()
    JAVA_LANGUAGE = Language(java_language_capsule)
    parser = Parser()
    parser.language = JAVA_LANGUAGE
    
    # Parse the code
    tree = parser.parse(code.encode('utf-8'))
    
    fields = []
    
    def visit_node(node: Node):
        """Recursively visit nodes to find field declarations."""
        
        # Look for field declarations in classes and constant declarations in interfaces
        if node.type in ['field_declaration', 'constant_declaration']:
            type_node = None
            field_names = []
            modifiers = []
            
            for child in node.children:
                if child.type == 'modifiers':
                    # Extract modifiers like private, public, static, final
                    for modifier in child.children:
                        if modifier.type in ['private', 'public', 'protected', 'static', 'final', 'volatile', 'transient']:
                            modifiers.append(code[modifier.start_byte:modifier.end_byte])
                elif child.type in ['type_identifier', 'generic_type', 'array_type', 'integral_type', 'floating_point_type', 'boolean_type']:
                    type_node = child
                elif child.type == 'variable_declarator':
                    # Get the variable name from the declarator
                    for grandchild in child.children:
                        if grandchild.type == 'identifier':
                            field_names.append(code[grandchild.start_byte:grandchild.end_byte])
                            break
            
            if type_node and field_names:
                var_type = code[type_node.start_byte:type_node.end_byte]
                
                # Add each field name found
                for field_name in field_names:
                    field_info = {
                        "name": field_name,
                        "type": var_type
                    }
                    
                    # Add modifiers if any
                    if modifiers:
                        field_info["modifiers"] = modifiers
                    
                    fields.append(field_info)
        
        # Recursively visit children
        for child in node.children:
            visit_node(child)
    
    visit_node(tree.root_node)
    return fields

def main():
    parser = argparse.ArgumentParser(description="Extract field declarations from Java code")
    parser.add_argument("file", help="Path to the Java file to analyze")
    parser.add_argument("-o", "--output", help="Output JSON file (default: stdout)")
    parser.add_argument("--include-modifiers", action="store_true", 
                       help="Include field modifiers in output")
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    fields = extract_java_fields(code)
    
    # Filter out modifiers if not requested
    if not args.include_modifiers:
        for field in fields:
            if 'modifiers' in field:
                del field['modifiers']
    
    output = json.dumps(fields, indent=2)
    
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Fields extracted and saved to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)

if __name__ == "__main__":
    main()