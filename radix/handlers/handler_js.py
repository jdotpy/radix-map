from .base import Variable, Function, Definition, SourceFile
from tree_sitter import Language, Parser
import tree_sitter_javascript as tsjavascript
from .tree_utils import ts_get_captures, one, q

def get_child_by_type(node, node_type):
    for child in node.children:
        if child.type == node_type:
            return child
    return None

class JsSourceFile(SourceFile):
    lang = Language(tsjavascript.language())
    
    def _parse(self):
        self.parser = Parser(self.lang)
        self._tree = self.parser.parse(self.code)
        return self._tree

    def _get_text(self, node):
        if node is None:
            return ''
        return self.code[node.start_byte:node.end_byte].decode('utf-8')

    def iter_functions(self, include_calls=False) -> list[Function]:
        """

            Use case 1: Arrow functions:

                query:
                    (lexical_declaration
                        (variable_declarator
                            value: (arrow_function)
                        )
                    ) @arrowfunc1
                example:
                    const foobar = () => {
                        console.log('im an arrow function')
                    }

            Use case 2: actual functions

                query:
                    (function_declaration) @func
                example:
                    function applyDiscount(p) {
                        return p * 0.9;
                    }
            
            Use case 3: anon functions

                query:
                    (lexical_declaration
                        (variable_declarator
                            value: (function_expression)
                        )
                    ) @anonFunc
                example:
                    const anonymousExpress = function(a, b) {
                        return a + b;
                    };



        """
        query = q(self.lang, """
            (program [
                ;; 1. Standard or Exported Declaration
                (function_declaration 
                    name: (identifier) @name 
                    parameters: (formal_parameters) @params) @anchor
                (export_statement 
                    (function_declaration 
                        name: (identifier) @name 
                        parameters: (formal_parameters) @params)) @anchor

                ;; 2. Lexical Assignments (Arrow or Expression)
                (lexical_declaration
                    (variable_declarator
                        name: (identifier) @name
                        value: [
                            (function_expression parameters: (formal_parameters) @params)
                            (arrow_function parameters: (formal_parameters) @params)
                        ]
                    )
                ) @anchor
            ])
        """)
        functions = []
        for _, captures in ts_get_captures(query, self._tree.root_node):
            
            name_node = one(captures.get('name', [None]))
            param_node = one(captures.get('params', [None]))
            anchor_node = one(captures.get('anchor', [None]))

            if name_node and param_node:
                name = self._get_text(name_node)
                args = self._get_text(param_node).strip("()")
                
                f = Function(name=name, arguments=args)
                if include_calls and anchor_node:
                    f.calls = self._extract_calls(anchor_node)
                functions.append(f)

        return functions

    def iter_definitions(self, include_methods=False, include_calls=False) -> list[Definition]:
        query = q(self.lang, """
            (class_declaration 
                name: (identifier) @name 
                body: (class_body) @body) @class
        """)
        
        definitions = []

        for _, captures in ts_get_captures(query, self._tree.root_node):
            name_node = one(captures.get('name'))
            class_name = self._get_text(name_node)
            defn = Definition(name=class_name, kind="class")
            
            if not include_methods:
                definitions.append(defn)
                continue

            body_node = class_node.child_by_field_name("body")
            # In JS class_body, we look for method_definition
            for child in body_node.children:
                if child.type == "method_definition":
                    name_node = child.child_by_field_name("name")
                    param_node = child.child_by_field_name("parameters")
                    
                    method = Function(
                        name=self._get_text(name_node),
                        arguments=self._get_text(param_node).strip("()")
                    )
                    if include_calls:
                        method.calls = self._extract_calls(child)
                    defn.methods.append(method)
        
            definitions.append(defn)
        return definitions

    def iter_globals(self):
        query = q(self.lang, """
            (program [
                (lexical_declaration (variable_declarator name: (identifier) @name))
                (variable_declaration (variable_declarator name: (identifier) @name))
            ] @global)
        """)
        captures = query.captures(self._tree.root_node)
        return [self._get_text(node.child_by_field_name("name")) for node in captures.get('global', [])]