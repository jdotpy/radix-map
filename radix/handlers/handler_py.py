import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from .base import SourceFile, Function, Variable, Definition
from .tree_utils import ts_get_captures,ts_line_info, one, q


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
        if node is None:
            return ''
        return self.code[node.start_byte:node.end_byte].decode('utf-8')

    def get_line_count(self):
        """Fetch total lines in source file"""
        return ts_line_info(self._tree.root_node)['source_lines'][1]

    def iter_functions(self, include_calls=False):
        query = q(self.lang, """
            (module (function_definition 
                name: (identifier) @name
                parameters: (parameters) @params) @func)
        """)
        functions = []
        for _, captures in ts_get_captures(query, self._tree.root_node):
            func_node = one(captures.get('func'))
            name_node = one(captures.get("name"))
            param_node = one(captures.get("params"))
            
            if name_node:
                name = self._get_text(name_node)
                params = self._get_text(param_node).strip("()")
                
                f = Function(name=name, arguments=params, **ts_line_info(func_node))
                if include_calls:
                    f.calls = self._extract_calls(func_node)
                functions.append(f)
                
        return functions

    def iter_definitions(self, include_methods=False, include_calls=False) -> list[Definition]:
        # Query for the class and its internal methods
        query = q(self.lang, """
            (class_definition 
                name: (identifier) @name
                body: (block) @body) @class
        """)
        definitions = []
        for _, captures in ts_get_captures(query, self._tree.root_node):
            class_name = self._get_text(captures.get('name')[0])
            body_node = one(captures.get('body'))
            class_node = one(captures.get('class'))
            
            # Initialize the Definition
            defn = Definition(name=class_name, kind="class", **ts_line_info(class_node))
            
            if not include_methods:
                continue
            # Walk the class body to find function_definitions (Methods)
            for child in body_node.children:
                entry = child
                if entry.type == "decorated_definition":
                    decorated_function = extract_decorated_function(entry)
                    if decorated_function is not None:
                        entry = decorated_function
                if entry.type == "function_definition":
                    method_name = self._get_text(entry.child_by_field_name("name"))
                    params = self._get_text(entry.child_by_field_name("parameters")).strip("()")
                    method = Function(name=method_name, arguments=params, **ts_line_info(child))
                    if include_calls:
                        method.calls = self._extract_calls(entry)
                    defn.methods.append(method)
            definitions.append(defn)
        return definitions
      
    def iter_globals(self):
        raise NotImplementedError()
