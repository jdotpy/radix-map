from .base import SourceFile, Definition, Variable, Function

class MarkdownSourceFile(SourceFile):
    def _parse(self):
        # Initial extraction of headers
        headers = []
        in_comment = False
        for i, line in enumerate(self.code.decode('utf-8').splitlines()):
            # Toggle blocks
            if line.startswith('```'):
                in_comment = not in_comment
            if in_comment:
                continue
        
            if line.startswith('#'):
                # Count the hashes and clean the text
                hashes = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                if hashes > 6:
                    continue
                headers.append({
                    'prefix': '#' * min(hashes, 6), # cap out headers at 6
                     'title': title,
                    'starting_line': i
                })
        self.total_lines = i + 1 # convert from 0-based
        self.headers = headers

        # Now calculate line ranges
        headers_state = {'#' * i: self.total_lines for i in range(1,7)}
        for header in reversed(headers):
            prefix = header.get('prefix')
            line = header.get('starting_line')
            
            # Record this line's status
            end_line = headers_state[prefix]
            header['ending_line'] = end_line

            # now reset headers less than or equal to this
            for i in range(len(prefix), 7):
                p = '#' * i
                headers_state[p] = line - 1 # Non-overlapping


        # Now determine "end" line by iterating in reverse and 

    def get_line_count(self):
        """Fetch total lines in source file"""
        return self.total_lines

    def iter_definitions(self, include_calls=False, include_methods=False) -> list[Definition]:
        """Returns Structs and Interfaces, populating their methods."""
        definitions = []
        for header in self.headers:
            defn = Definition(
                name=header['title'],
                kind=header['prefix'],
                source_lines=(header['starting_line'],header['ending_line']),
            )
            definitions.append(defn)
            
        return definitions
    
    def iter_functions(self, include_calls=False) -> list[Function]:
        """Returns top-level functions (those without receivers)."""
        return []
    
    def iter_globals(self) -> list[Variable]:
        """Returns top-level var and const declarations."""
        return []
        