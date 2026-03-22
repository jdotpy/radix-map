from typing import Dict, Callable, Type
from .base import SourceFile

import sys

class HandlerRegistry:
    def __init__(self):
        # Maps extension -> A function that returns the Class
        self._loaders = {
            ".py": self._load_python,
            ".go": self._load_go,
            ".js": self._load_js,
            ".vue": self._load_js, # Pointing to JS for now
        }
        self._handlers: Dict[str, Type[SourceFile]] = {}
        self._errors = {}

    def _load_python(self):
        from .handler_py import PythonSourceFile
        return PythonSourceFile

    def _load_go(self):
        from .handler_go import GoSourceFile
        return GoSourceFile

    def _load_js(self):
        from .handler_js import JsSourceFile
        return JsSourceFile

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