from .base import Definition, Function, Variable, SourceFile
from tree_sitter import Language, Parser
import tree_sitter_scala as tsscala

from .tree_utils import ts_get_captures, ts_line_info, one, q

class ScalaSourceFile(SourceFile):
    lang = Language(tsscala.language())

    def _parse(self):
        self.parser = Parser(self.lang)
        return self.parser.parse(self.code)

    def _get_text(self, node):
        if node is None:
            return ''
        return self.code[node.start_byte:node.end_byte].decode('utf-8')
    
    def get_line_count(self):
        return ts_line_info(self._tree.root_node)['source_lines'][1]

    def iter_definitions(self, include_calls=False, include_methods=False) -> list[Definition]:
        """Returns classes, traits, and objects (singletons) in Scala, optionally linking their methods."""
        # Query captures the template body if it exists, alongside the name and definition
        query = q(self.lang, """
            [
                (class_definition name: (identifier) @name body: (template_body)? @body)
                (trait_definition name: (identifier) @name body: (template_body)? @body)
                (object_definition name: (identifier) @name body: (template_body)? @body)
            ] @definition
        """)
        definitions = []
        
        # Pull all functions in the file to resolve nesting if requested
        all_functions = self.iter_functions() if include_methods else []

        for _, captures in ts_get_captures(query, self._tree.root_node):
            node = one(captures.get('definition'))
            name_node = one(captures.get('name'))
            body_node = one(captures.get('body'))
            
            if not node or not name_node:
                continue
                
            kind = node.type.split('_')[0] 
            defn = Definition(
                name=self._get_text(name_node),
                kind=kind,
                **ts_line_info(node)
            )
            
            # If a body exists, filter functions that physically sit inside its line boundaries
            if body_node and include_methods:
                body_info = ts_line_info(body_node)
                start_line, end_line = body_info['source_lines']
                
                defn.methods = [
                    f for f in all_functions 
                    if start_line <= f.source_lines[0] <= end_line
                ]
                
            definitions.append(defn)
            
        return definitions
    
    def iter_functions(self, include_calls=False) -> list[Function]:
        """Returns top-level functions (those not declared inside a class, trait, or object)."""
        # 1. Grab all functions/methods across the file
        func_query = q(self.lang, """
            (function_definition
                name: (identifier) @name
                parameters: (parameters)? @params) @func
        """)
        
        all_functions = []
        for _, captures in ts_get_captures(func_query, self._tree.root_node):
            func_node = captures.get('func')
            name = self._get_text(one(captures.get('name')))
            params_node = captures.get('params')
            params = self._get_text(one(params_node)).strip("()") if params_node else ""
            all_functions.append(Function(name=name, arguments=params, **ts_line_info(func_node)))

        # 2. Grab the boundaries of all template bodies
        body_query = q(self.lang, """
            [
                (class_definition body: (template_body) @body)
                (trait_definition body: (template_body) @body)
                (object_definition body: (template_body) @body)
            ]
        """)
        
        bodies = []
        for _, captures in ts_get_captures(body_query, self._tree.root_node):
            body_node = one(captures.get('body'))
            if body_node:
                info = ts_line_info(body_node)
                bodies.append(info['source_lines']) # Contains (start_line, end_line)

        # 3. Filter down to functions that don't fall within any body span
        top_level_functions = []
        for f in all_functions:
            f_line = f.source_lines[0]
            # If the function line falls inside any structural body, skip it
            if any(start <= f_line <= end for start, end in bodies):
                continue
            top_level_functions.append(f)
                
        return top_level_functions
 
    def iter_globals(self) -> list[Variable]:
        """Returns top-level/package variables and constants (val and var)."""
        query = q(self.lang, """
            (val_definition pattern: (identifier) @name) @val
            (var_definition pattern: (identifier) @name) @var
        """)
        
        variables = []
        for _, captures in ts_get_captures(query, self._tree.root_node):
            name_node = captures.get('name')
            name = self._get_text(one(captures.get('name')))
            if name:
                variables.append(name)
        
        return variables