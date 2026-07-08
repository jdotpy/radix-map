from .base import Function, Definition, SourceFile, Variable
from tree_sitter import Language, Parser
import tree_sitter_javascript as tsjavascript
from .tree_utils import ts_get_captures, ts_line_info, one, q
import sys

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
    
    def get_line_count(self):
        return ts_line_info(self._tree.root_node)['source_lines'][1]

    def iter_functions(self, include_calls=False) -> list[Function]:
        """Finds root-level declarations, arrow assignments, and module exports safely."""
        query = q(self.lang, """
            ;; 1. Standard function declarations at root/exported
            (program [
                (function_declaration 
                    name: (identifier) @name 
                    parameters: (formal_parameters) @params) @func
                (export_statement
                    (function_declaration 
                        name: (identifier) @name 
                        parameters: (formal_parameters) @params) @func)
            ])

            ;; 2. Arrow functions or expressions assigned at root/exported
            (program [
                (lexical_declaration
                    (variable_declarator
                        name: (identifier) @name
                        value: [
                            (arrow_function parameters: (formal_parameters) @params)
                            (function_expression parameters: (formal_parameters) @params)
                        ])) @func
                (export_statement
                    (lexical_declaration
                        (variable_declarator
                            name: (identifier) @name
                            value: [
                                (arrow_function parameters: (formal_parameters) @params)
                                (function_expression parameters: (formal_parameters) @params)
                            ]))) @func
            ])

            ;; 3. Object Literal Methods (Only include if you want object properties treated as top-level functions)
            (pair
                key: (property_identifier) @name
                value: [
                    (arrow_function parameters: (formal_parameters) @params)
                    (function_expression parameters: (formal_parameters) @params)
                ]) @func
                
            ;; 4. Shorthand Method Definitions in Objects 
            (method_definition
                name: (property_identifier) @name
                parameters: (formal_parameters) @params) @func
        """)
        
        functions = []
        all_definitions = self.iter_definitions(include_methods=True)
        
        # Prevent class methods from bleeding into top-level functions via global matching
        class_method_spans = []
        for d in all_definitions:
            for m in d.methods:
                class_method_spans.append(m.source_lines)

        for _, captures in ts_get_captures(query, self._tree.root_node):
            name_node = one(captures.get('name'))
            param_node = one(captures.get('params'))
            func_node = one(captures.get('func'))

            if not name_node or not param_node or not func_node:
                continue

            line_info = ts_line_info(func_node)
            
            # Skip if this method belongs strictly inside a class declaration block
            if any(span[0] <= line_info['source_lines'][0] <= span[1] for span in class_method_spans):
                continue

            f = Function(
                name=self._get_text(name_node), 
                arguments=self._get_text(param_node).strip("()"), 
                **line_info
            )
            functions.append(f)

        return functions

    def iter_definitions(self, include_methods=False, include_calls=False) -> list[Definition]:
        """Finds explicit class declarations and variable-assigned inline classes anywhere."""
        query = q(self.lang, """
            (class_declaration 
                name: (identifier) @name 
                body: (class_body) @body) @class
            
            ;; Captures: const Logger = class InternalLogger {}
            (variable_declarator
                value: (class name: (identifier)? @name body: (class_body) @body)) @class
        """)
        
        definitions = []

        for _, captures in ts_get_captures(query, self._tree.root_node):
            name_node = one(captures.get('name'))
            class_node = one(captures.get('class'))
            
            if not name_node or not class_node:
                continue
                
            defn = Definition(name=self._get_text(name_node), kind="class", **ts_line_info(class_node))
            
            if include_methods:
                # 1. Find the class_body node, whether it's direct or nested under a variable_declarator value
                body_node = None
                if class_node.type == "class_body":
                    body_node = class_node
                elif class_node.type == "class":
                    body_node = class_node.child_by_field_name("body")
                elif class_node.type == "class_declaration":
                    body_node = class_node.child_by_field_name("body")
                else:
                    # Look inside a variable_declarator value field
                    val = class_node.child_by_field_name("value")
                    if val:
                        body_node = val.child_by_field_name("body")

                # 2. Extract methods out of the body if found
                if body_node and body_node.type == "class_body":
                    for child in body_node.children:
                        if child.type == "method_definition":
                            m_name = child.child_by_field_name("name")
                            m_param = child.child_by_field_name("parameters")
                            if m_name and m_param:
                                method = Function(
                                    name=self._get_text(m_name),
                                    arguments=self._get_text(m_param).strip("()"),
                                    **ts_line_info(child)
                                )
                                defn.methods.append(method)
        
            definitions.append(defn)
        return definitions

    def iter_globals(self) -> list[Variable]:
        """Captures variables declared exclusively at the program root level, unpacking destructuring safely."""
        query = q(self.lang, """
            (program [
                ;; Match top-level let/const/var declarations
                (lexical_declaration (variable_declarator name: [
                    (identifier) @var_name
                    (object_pattern [
                        (shorthand_property_identifier_pattern) @var_name
                        (pair value: (identifier) @var_name)
                    ])
                ]))
                (variable_declaration (variable_declarator name: [
                    (identifier) @var_name
                    (object_pattern [
                        (shorthand_property_identifier_pattern) @var_name
                        (pair value: (identifier) @var_name)
                    ])
                ]))
                ;; Match exported let/const/var declarations
                (export_statement [
                    (lexical_declaration (variable_declarator name: [
                        (identifier) @var_name
                        (object_pattern [
                            (shorthand_property_identifier_pattern) @var_name
                            (pair value: (identifier) @var_name)
                        ])
                    ]))
                    (variable_declaration (variable_declarator name: [
                        (identifier) @var_name
                        (object_pattern [
                            (shorthand_property_identifier_pattern) @var_name
                            (pair value: (identifier) @var_name)
                        ])
                    ]))
                ])
            ])
        """)
        
        variables = []
        for _, captures in ts_get_captures(query, self._tree.root_node):
            # tree-sitter captures can return a single node or list depending on implementation details
            nodes = captures.get('var_name', [])
            if not isinstance(nodes, list):
                nodes = [nodes]
                
            for name_node in nodes:
                variables.append(Variable(name=self._get_text(name_node)))
        return variables