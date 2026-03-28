import os
import io
import zipfile
from pathlib import Path
from typing import Generator, Tuple, Optional, Set
from dataclasses import dataclass
from typing import Callable

@dataclass
class FileEntry:
    full_path: Path
    rel_path: Path
    size: int
    reader: Callable[[], bytes]
    is_stream: bool = False

class DiskSource:
    requries_explicit_lang = False

    def __init__(self, root_path: Path):
        self.path = Path(root_path)
        self.is_single_file = self.path.is_file()
        self.root = self.path.parent if self.is_single_file else self.path
        
    def walk(self) -> Generator[FileEntry, None, None]:
        if self.is_single_file:
            yield FileEntry(    
                full_path=self.path,
                rel_path=Path(self.path.name),
                size=self.path.stat().st_size,
                reader=self.path.read_bytes
            )
            return
        
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ProjectScanner.DEFAULT_IGNORE_LIST]
            for f in files:
                p = Path(root) / f
                yield FileEntry(    
                    full_path=p,
                    rel_path=p.relative_to(self.root),
                    size=p.stat().st_size,
                    reader=p.read_bytes
                )

class StreamSource:
    requries_explicit_lang = True

    def __init__(self, stream, label="stdin"):
        # We read it once because we can't seek back on a pipe
        self.content = stream.read()
        self.label = Path(label)

    def walk(self) -> Generator[FileEntry, None, None]:
        yield FileEntry(
            full_path=self.label,
            rel_path=self.label,
            size=len(self.content),
            reader=lambda: self.content,
            is_stream=True,
        )

class ZipSource:
    requries_explicit_lang = False
    
    def __init__(self, buffer):
        self.zip = zipfile.ZipFile(buffer)

    @classmethod
    def from_path(cls, path):
        # Open file is seekable
        return cls(open(path, 'rb'))

    @classmethod
    def from_stream(cls, stream):
        # Pipes aren't seekable, so we must read the whole thing into memory
        # to allow ZipFile to jump to the Central Directory at the end.
        seekable_buffer = io.BytesIO(stream.read())
        return cls(seekable_buffer)

    def walk(self) -> Generator[FileEntry, None, None]:
        for info in self.zip.infolist():
            if info.is_dir():
                continue
            
            rel_path = Path(info.filename)
            yield FileEntry(
                full_path=rel_path,
                rel_path=rel_path,
                size=info.file_size,
                reader=lambda name=info.filename: self.zip.read(name)
            )


class ProjectScanner:
    DEFAULT_IGNORE_LIST = {
        "node_modules", "bower_components", "vendor", 
        "dist", "build", "out", "venv", "env", "target"
    }

    def __init__(self, registry, max_bytes: int = 200_000, extra_ignored_dirs: Optional[Set[str]] = None):
        self.registry = registry
        self.max_bytes = max_bytes
        self.ignored_segments = self.DEFAULT_IGNORE_LIST
        if extra_ignored_dirs:
            self.ignored_segments.update(extra_ignored_dirs)
    
    def is_visible(self, entry: FileEntry) -> bool:
        if entry.is_stream:
            return self.registry.fallback_loader is not None
        if entry.size > self.max_bytes:
            return False
        if not self.registry.has_handler(entry.rel_path.suffix):
            return False
        for part in entry.rel_path.parts:
            if part.startswith(".") or part in self.ignored_segments:
                return False
        return True
    """
    def make_reader(self, path):
        def reader():
            with open(path, 'rb') as f:
                content = f.read()
            return content
        return reader
    """

    def scan(self, source) -> Generator[Tuple[Path, Path, type, Callable], None, None]:
        """
        Yields (Full_Path, Relative_Path, Handler, Reader)
        """
        for entry in source.walk():
            # Check visibility based on the relative path (to catch ignored folders)
            if not self.is_visible(entry):
                continue

            if entry.is_stream and entry.rel_path.suffix == '':
                extension = None # will use fallback
            else:
                extension = entry.rel_path.suffix

            handler_class = self.registry.get_handler_class(extension)
            if handler_class:
                yield (
                    entry.full_path,
                    entry.rel_path,
                    handler_class,
                    entry.reader
                )