from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Variable:
    name: str
    type_hint: Optional[str] = None
    value_snippet: Optional[str] = None  # For constants like MAX_RETRIES = 5

    def __str__(self):
        type_prefix = ''
        if self.type_hint:
            type_prefix = f'{self.type_hint} '
        value_suffix = ''
        if self.value_snippet:
            value_suffix = f' {self.value_snippet}'
        return f'{type_prefix}{self.name}{value_suffix}'

@dataclass
class Function:
    name: str
    source_lines: tuple[int, int]
    arguments: str = ""
    return_type: str = ""
    is_public: bool = False
    calls: List[str] = field(default_factory=list)

    def __str__(self):
        return_suffix = ''
        if self.return_type:
            return_suffix = ' ➜ {return_type}'
        return f'ƒ {self.name}({self.arguments}){return_suffix}'


@dataclass
class Definition:
    name: str
    kind: str                 # "class", "struct", "interface"
    source_lines: tuple[int, int]
    properties: List[Variable] = field(default_factory=list)
    methods: List[Function] = field(default_factory=list)
    

    def __str__(self):
        return f'{self.kind} {self.name}'

class SourceFile(ABC):
    def __init__(self, path: str, code: bytes):
        self.path = path
        self.code = code
        self._tree = self._parse()
    
    @abstractmethod
    def get_line_count(self):
        """Fetch total lines in source file"""
        pass

    @abstractmethod
    def _parse(self):
        """Initialize the Tree-sitter parser for the specific language."""
        pass

    @abstractmethod
    def iter_definitions(self) -> List[Definition]:
        """
        Returns Classes or Structs. 
        Implementation should populate .properties and .methods.
        """
        pass

    @abstractmethod
    def iter_functions(self) -> List[Function]:
        """Returns top-level functions (logic not bound to a class/struct)."""
        pass

    @abstractmethod
    def iter_globals(self) -> List[Variable]:
        """Returns top-level constants and global variables."""
        pass