from typing import Dict, Callable, Type
from .base import SourceFile

import sys

def _load_python():
    from .handler_py import PythonSourceFile
    return PythonSourceFile

def _load_go():
    from .handler_go import GoSourceFile
    return GoSourceFile

def _load_js():
    from .handler_js import JsSourceFile
    return JsSourceFile

class HandlerRegistry:
    LIBRARIES = {
            "py": {
                'package_name': 'tree-sitter-python',
                'lib': 'tree_sitter_python',
                'loader': _load_python,
            },
            "go": {
                'package_name': 'tree-sitter-go',
                'lib': 'tree_sitter_go',
                'loader': _load_go,
            },
            "js": {
                'package_name': 'tree-sitter-javascript',
                'lib': 'tree_sitter_javascript',
                'loader': _load_js,
            },
    }

    def __init__(self):
        # Maps extension -> A function that returns the Class
        self._loaders = {
            ".py": LIBRARIES['py']['loader'],
            ".go": LIBRARIES['go']['loader'],
            ".js": LIBRARIES['js']['loader'],
        }
        self._handlers: Dict[str, Type[SourceFile]] = {}
        self._errors = {}

    def get_handler_class(self, extension: str) -> Type[SourceFile]:
        ext = extension.lower()
        if not self.has_handler(ext):
            raise ValueError(f"Unsupported extension: {ext}")

        # Check cache so we don't re-import every time
        if ext not in self._handlers:
            loader_func = self._loaders[ext]
            try:
                self._handlers[ext] = loader_func()
            except ModuleNotFoundError as e:
                sys.stderr.write(f"Skipping files of type {ext} due to import failure for required module. Error: {str(e)}\n")
                self._errors[ext] = e
                return None
        
        return self._handlers[ext]

    def has_handler(self, extension: str) -> bool:
        ext = extension.lower()
        if ext in self._errors:
            return False
        return ext in self._loaders or ext in self._handlers