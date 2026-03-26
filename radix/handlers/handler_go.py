from .base import Definition, Function, Variable, SourceFile
from tree_sitter import Language, Parser
import tree_sitter_go as tsgo

from .tree_utils import ts_get_captures, ts_line_info, one, q

class GoSourceFile(SourceFile):
    lang = Language(tsgo.language())

    def _parse(self):
        self.parser = Parser(self.lang)
        return self.parser.parse(self.code)

    def _get_text(self, node):
        if node is None:
            return ''
        return self.code[node.start_byte:node.end_byte].decode('utf-8')

    def iter_definitions(self, include_calls=False, include_methods=False) -> list[Definition]:
        """Returns Structs and Interfaces, populating their methods."""
        # Query for type declarations (structs and interfaces)
        query = q(self.lang, """
            (type_declaration
                (type_spec
                    name: (type_identifier) @name
                    type: [
                        (struct_type) 
                        (interface_type)
                    ] @type_body)) @definition
        """)
        definitions = []
        
        all_methods = self._get_all_methods()

        for _, captures in ts_get_captures(query, self._tree.root_node):
            node = one(captures.get('definition'))
            name_node = node.child_by_field_name("name") or node.named_child(0).child_by_field_name("name")
            
            if not name_node:
                continue
                
            type_name = self._get_text(name_node)
            type_body = node.named_child(0).child_by_field_name("type")
            kind = "struct" if type_body.type == "struct_type" else "interface"
            
            defn = Definition(name=type_name, kind=kind, **ts_line_info(node))
            defn.methods = [m for m in all_methods if m._receiver_type == type_name]
            definitions.append(defn)
            
        return definitions

    def iter_functions(self, include_calls=False) -> list[Function]:
        """Returns top-level functions (those without receivers)."""
        query = q(self.lang, """
            (function_declaration
                name: (identifier) @name
                parameters: (parameter_list) @params) @func
        """)
        
        functions = []
        for _, captures in ts_get_captures(query, self._tree.root_node):
            func_node = captures.get('func')
            name = self._get_text(one(captures.get('name')))
            params = self._get_text(one(captures.get('params'))).strip("()")
            functions.append(Function(name=name, arguments=params, **ts_line_info(func_node)))
                
        return functions

    def iter_globals(self) -> list[Variable]:
        """Returns top-level var and const declarations."""
        query = q(self.lang, """
            (var_declaration
                (var_spec name: (identifier) @name)) @var
            (const_declaration
                (const_spec name: (identifier) @name)) @const
        """)
        
        variables = []
        
        for _, captures in ts_get_captures(query, self._tree.root_node):
            # Simplification: grabbing the first identifier in the spec
            node = captures.get('var') or captures.get('const')
            name_node = node.named_child(0).child_by_field_name("name")
            if name_node:
                variables.append(Variable(name=self._get_text(name_node)))
        
        return variables

    def _get_all_methods(self) -> list:
        """Helper to find all method_declarations and identify their receiver type."""
        query = q(self.lang, """
            (method_declaration
                receiver: (parameter_list 
                    (parameter_declaration 
                        type: [
                            (pointer_type (type_identifier) @recv) 
                            (type_identifier) @recv
                        ]
                    )
                )
                name: (field_identifier) @name
                parameters: (parameter_list) @params
            ) @method
        """)
        
        methods = []
        for _, captures in ts_get_captures(query, self._tree.root_node):
            method_node = one(captures.get('method'))
            name_node = one(captures.get('name'))
            recv_node = one(captures.get('recv'))
            param_node = one(captures.get('params'))
            
            func = Function(
                name=self._get_text(name_node),
                arguments=self._get_text(param_node).strip("()"),
                **ts_line_info(method_node)
            )
            # Temporary attribute to help iter_definitions link them
            func._receiver_type = self._get_text(recv_node)
            methods.append(func)
            
        return methods