from . import scanner
from .handlers.registry import HandlerRegistry

from pathlib import Path
import sys

def default_scanner(path: str):
    registry = HandlerRegistry()
    s = scanner.ProjectScanner(registry)
    return s

def default_source(path):
    return scanner.DiskSource(path)

def analyze_project(scanner, source, calls=False, params=False):
    reports = {}
    for file_path, relative_path, handler, read_func in scanner.scan(source):
        try:
            source_file = handler(file_path, read_func())
        except Exception as e:
            sys.stderr.write(f'Failed to parse file={file_path} with handler={handler.__name__}. Skipping. Error="{str(e)}"')
            continue

        file_report = {
            "path": str(file_path),
            "functions": list(source_file.iter_functions(include_calls=calls)),
            "definitions": list(source_file.iter_definitions(include_methods=True, include_calls=calls)),
        }
        reports[relative_path] = file_report
    return reports
