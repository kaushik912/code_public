import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser

# Get the language object from the compiled bindings
cpp_language_capsule = tscpp.language()
CPP_LANGUAGE = Language(cpp_language_capsule)

# Test that it works
parser = Parser()
parser.language = CPP_LANGUAGE
code = b'int main() { return 0; }'
tree = parser.parse(code)
print(f"Successfully parsed C++ code. Root node type: {tree.root_node.type}")

