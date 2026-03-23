import os
from pathlib import Path
from typing import Generator, Tuple, Optional, Set


class ProjectScanner:
    DEFAULT_IGNORE_LIST = {
        "node_modules", "bower_components", "vendor", 
        "dist", "build", "out", "venv", "env", "target"
    }

    def __init__(self, registry, path, max_bytes: int = 200_000, extra_ignored_dirs: Optional[Set[str]] = None):
        self.target_path = Path(path).resolve()
        self.registry = registry
        self.max_bytes = max_bytes
        self.ignored_segments = self.DEFAULT_IGNORE_LIST
        if extra_ignored_dirs:
            self.ignored_segments.update(extra_ignored_dirs)

    def is_visible(self, path: Path) -> bool:
        """The core visibility logic: Ignore dots, junk, and oversized files."""
        if not self.registry.has_handler(path.suffix):
            return False

        for part in path.parts:
            if part.startswith(".") and part != ".": # Allow current dir '.'
                return False
            if part in self.ignored_segments:
                return False
        try:
            if path.stat().st_size > self.max_bytes:
                return False
        except FileNotFoundError:
            return False

        return True

    def make_reader(self, path):
        def reader():
            with open(path, 'rb') as f:
                content = f.read()
            return content
        return reader

    def scan(self) -> Generator[Tuple[Path, type], None, None]:
        """
        Yields (Path, HandlerClass) for every valid file found.
        Handles both single file and directory walking.
        """

        if self.target_path.is_file():
            if self.is_visible(self.target_path):
                yield (
                    self.target_path,
                    self.target_path.name,
                    self.registry.get_handler_class(self.target_path.suffix),
                    self.make_reader(self.target_path)
                )
            return

        for root, dirs, files in os.walk(self.target_path):
            # Optimization: Modify 'dirs' in-place to prevent os.walk from entering ignored folders
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in self.ignored_segments]

            for file in files:
                file_path = Path(root) / file
                if self.is_visible(file_path):
                    handler_class = self.registry.get_handler_class(file_path.suffix)
                    if handler_class is None:
                        # We recognize the file but its module is missing
                        continue
                    yield (
                        file_path,
                        file_path.relative_to(self.target_path),
                        handler_class,
                        self.make_reader(file_path)
                    )