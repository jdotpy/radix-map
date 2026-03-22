import os
from pathlib import Path
from typing import Generator, Tuple, Optional, Set

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

    def is_visible(self, path: Path) -> bool:
        """The core visibility logic: Ignore dots, junk, and oversized files."""
        # 1. Check if it's an extension we actually have a handler for
        if not self.registry.has_handler(path.suffix):
            return False

        # 2. Check path segments (any part of the path starts with . or is in forbidden list)
        for part in path.parts:
            if part.startswith(".") and part != ".": # Allow current dir '.'
                return False
            if part in self.ignored_segments:
                return False

        # 3. Check File Size (Avoid minified JS or large data blobs)
        try:
            if path.stat().st_size > self.max_bytes:
                return False
        except FileNotFoundError:
            return False

        return True

    def scan(self, target: str) -> Generator[Tuple[Path, type], None, None]:
        """
        Yields (Path, HandlerClass) for every valid file found.
        Handles both single file and directory walking.
        """
        target_path = Path(target).resolve()

        if target_path.is_file():
            if self.is_visible(target_path):
                yield target_path, self.registry.get_handler_class(target_path.suffix)
            return

        # If it's a directory, walk it
        for root, dirs, files in os.walk(target_path):
            # Optimization: Modify 'dirs' in-place to prevent os.walk from entering ignored folders
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in self.ignored_segments]

            for file in files:
                file_path = Path(root) / file
                if self.is_visible(file_path):
                    handler_class = self.registry.get_handler_class(file_path.suffix)
                    if handler_class is None:
                        # We recognize the file but its missing
                        continue
                    yield file_path, handler_class