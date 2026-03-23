from .base import Definition, Function, Variable, SourceFile
from tree_sitter import Language, Parser
import tree_sitter_go as tsgo

class GoSourceFile(SourceFile):
    lang = Language(tsgo.language())

    def _parse(self):
        self.parser = Parser(self.lang)
        return self.parser.parse(self.code)

    def _get_text(self, node):
        return self.code[node.start_byte:node.end_byte].decode('utf-8')

    def iter_definitions(self, include_calls=False, include_methods=False) -> list[Definition]:
        """Returns Structs and Interfaces, populating their methods."""
        # Query for type declarations (structs and interfaces)
        query = self.lang.query("""
            (type_declaration
                (type_spec
                    name: (type_identifier) @name
                    type: [
                        (struct_type) 
                        (interface_type)
                    ] @type_body)) @definition
        """)
        definitions = []
        captures = query.captures(self._tree.root_node)
        
        all_methods = self._get_all_methods()

        for node in captures.get('definition', []):
            name_node = node.child_by_field_name("name") or node.named_child(0).child_by_field_name("name")
            
            if not name_node:
                continue
                
            type_name = self._get_text(name_node)
            type_body = node.named_child(0).child_by_field_name("type")
            kind = "struct" if type_body.type == "struct_type" else "interface"
            
            defn = Definition(name=type_name, kind=kind)
            defn.methods = [m for m in all_methods if m._receiver_type == type_name]
            definitions.append(defn)
            
        return definitions

    def iter_functions(self, include_calls=False) -> list[Function]:
        """Returns top-level functions (those without receivers)."""
        query = self.lang.query("""
            (function_declaration
                name: (identifier) @name
                parameters: (parameter_list) @params) @func
        """)
        
        functions = []
        captures = query.captures(self._tree.root_node)
        for func_node in captures.get('func', []):
            name = self._get_text(func_node.child_by_field_name("name"))
            params = self._get_text(func_node.child_by_field_name("parameters")).strip("()")
            functions.append(Function(name=name, arguments=params))
                
        return functions

    def iter_globals(self) -> list[Variable]:
        """Returns top-level var and const declarations."""
        query = self.lang.query("""
            (var_declaration
                (var_spec name: (identifier) @name)) @var
            (const_declaration
                (const_spec name: (identifier) @name)) @const
        """)
        
        variables = []
        captures = query.captures(self._tree.root_node)
        # Combine results from both @var and @const
        all_nodes = captures.get('var', []) + captures.get('const', [])
        
        for node in all_nodes:
            # Simplification: grabbing the first identifier in the spec
            name_node = node.named_child(0).child_by_field_name("name")
            if name_node:
                variables.append(Variable(name=self._get_text(name_node)))
        
        return variables

    def _get_all_methods(self) -> list:
        """Helper to find all method_declarations and identify their receiver type."""
        query = self.lang.query("""
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
        captures = query.captures(self._tree.root_node)
        for i in range(len(captures.get('method', []))):
            name_node = captures['name'][i]
            recv_node = captures['recv'][i]
            param_node = captures['params'][i]
            
            func = Function(
                name=self._get_text(name_node),
                arguments=self._get_text(param_node).strip("()")
            )
            # Temporary attribute to help iter_definitions link them
            func._receiver_type = self._get_text(recv_node)
            methods.append(func)
            
        return methods