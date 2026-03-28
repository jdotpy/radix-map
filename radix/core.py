from . import scanner
from .handlers.registry import HandlerRegistry

from pathlib import Path
import sys

def make_scanner(path: str, handler_overrides=None, fallback_handler=None):
    registry = HandlerRegistry(overrides=handler_overrides, fallback=fallback_handler)
    s = scanner.ProjectScanner(registry)
    return s

def get_source(path):
    if path == "-":
        # Check if stdin is a ZIP or plain text
        # Zip files start with "PK" (0x50 0x4B)
        stream = sys.stdin.buffer
        head = stream.peek(2)[:2]
        
        if head == b"PK":
            return scanner.ZipSource.from_stream(stream)
        else:
            return scanner.StreamSource(stream) # Your new SingleFileStream
            
    p = Path(path)
    if p.suffix.lower() == ".zip":
        return scanner.ZipSource.from_path(path)
        
    return scanner.DiskSource(path)

def analyze_project(scanner, source, calls=False, lines=False):
    reports = {}
    for file_path, relative_path, handler, read_func in scanner.scan(source):
        try:
            source_file = handler(file_path, read_func())
        except Exception as e:
            sys.stderr.write(f'Failed to parse file={file_path} with handler={handler.__name__}. Skipping. Error="{str(e)}"')
            continue

        file_report = {
            "path": str(file_path),
            "lines": source_file.get_line_count(),
            "functions": list(source_file.iter_functions(include_calls=False)),
            "definitions": list(source_file.iter_definitions(include_methods=True, include_calls=False)),
        }
        reports[relative_path] = file_report
    return reports
