import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from .base import SourceFile, Function, Variable, Definition


def extract_decorated_function(node):
    for child in node.children:
        if child.type == 'function_definition':
            return child
    return None


class PythonSourceFile(SourceFile):
    lang = Language(tspython.language())
    
    def _parse(self):
        self.parser = Parser(self.lang)
        return self.parser.parse(self.code)

    def _get_text(self, node):
        return self.code[node.start_byte:node.end_byte].decode('utf-8')

    def iter_functions(self, include_calls=False) -> list[Function]:
        query = self.lang.query("""
            (module (function_definition 
                name: (identifier) @name
                parameters: (parameters) @params) @func)
        """)
        functions = []
        captures = query.captures(self._tree.root_node)
        for func_node in captures.get('func', []):
            name_node = func_node.child_by_field_name("name")
            param_node = func_node.child_by_field_name("parameters")
            
            if name_node and param_node:
                name = self._get_text(name_node)
                params = self._get_text(param_node).strip("()")
                
                f = Function(name=name, arguments=params)
                if include_calls:
                    f.calls = self._extract_calls(func_node)
                functions.append(f)
                
        return functions

    def iter_definitions(self, include_methods=False, include_calls=False) -> list[Definition]:
        # Query for the class and its internal methods
        query = self.lang.query("""
            (class_definition 
                name: (identifier) @name
                body: (block) @body) @class
        """)
        
        captures = query.captures(self._tree.root_node)
        definitions = []

        for class_node in captures.get('class', []):
            class_name = self._get_text(class_node.child_by_field_name("name"))
            
            # Initialize the Definition
            defn = Definition(name=class_name, kind="class")
            
            if not include_methods:
                continue
            # Walk the class body to find function_definitions (Methods)
            body_node = class_node.child_by_field_name("body")
            for child in body_node.children:
                entry = child
                if entry.type == "decorated_definition":
                    decorated_function = extract_decorated_function(entry)
                    if decorated_function is not None:
                        entry = decorated_function
                if entry.type == "function_definition":
                    method_name = self._get_text(entry.child_by_field_name("name"))
                    params = self._get_text(entry.child_by_field_name("parameters")).strip("()")
                    method = Function(name=method_name, arguments=params)
                    if include_calls:
                        method.calls = self._extract_calls(entry)
                    defn.methods.append(method)
            definitions.append(defn)
        return definitions
      
    def iter_globals(self):
        raise NotImplemented()
