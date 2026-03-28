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

    def __init__(self, overrides=None, fallback=None):
        # Maps extension -> A function that returns the Class
        self._loaders = {
            ".py": self.LIBRARIES['py']['loader'],
            ".go": self.LIBRARIES['go']['loader'],
            ".js": self.LIBRARIES['js']['loader'],
        }
        self._handlers: Dict[str, Type[SourceFile]] = {}
        self._errors = {}
        self.fallback_loader = None

        if overrides is not None:
            for ext, target_ext in overrides.items():
                target_loader = self._loaders.get(f'.{target_ext}', None)
                if target_loader is None:
                    sys.stderr.write(f"Attempted to map to loader {target_ext} but it didnt exist")
                    continue
                self._loaders[f'.{ext}'] = target_loader
        
        if fallback is not None:
            # Register the fallback as the None handler
            self.fallback_loader = self._loaders.get(f'.{fallback}', None)
            self._loaders[None] = self.fallback_loader

    def get_handler_class(self, extension: str) -> Type[SourceFile]:
        if extension is not None:
            extension = extension.lower()

        if not self.has_handler(extension):
            raise ValueError(f"Unsupported extension: {extension}")

        # Check cache so we don't re-import every time
        if extension not in self._handlers:
            loader_func = self._loaders[extension]
            try:
                self._handlers[extension] = loader_func()
            except ModuleNotFoundError as e:
                sys.stderr.write(f"Skipping files of type {extension} due to import failure for required module. Error: {str(e)}\n")
                self._errors[extension] = e
                return None
        
        return self._handlers[extension]

    def has_handler(self, extension: str) -> bool:
        if extension is not None:
            extension = extension.lower()
        if extension in self._errors:
            return False
        return extension in self._loaders or extension in self._handlers