from . import scanner
from .handlers.registry import HandlerRegistry

from pathlib import Path
import sys

def get_smart_relative_path(target_path, base_path):
    target = Path(target_path)
    
    # Handle worker directory
    if not base_path or base_path == ".":
        base = Path.cwd()
    else:
        base = Path(base_path)

    # if we just got a file path/name then its not "relative" to anything really
    if base.is_file():
        return target.name
    try:
        return target.relative_to(base)
    except ValueError:
        return target_path

def analyze_project(path: str, calls=False, params=False):
    print(f"Scanning {path} with Calls={calls}, Params={params}...")
    registry = HandlerRegistry()
    s = scanner.ProjectScanner(registry)
    reports = {}
    for file_path, handler in s.scan(path):
        try:
            with open(file_path, 'rb') as f:
                source_file = handler(file_path, f.read())
        except Exception as e:
            sys.stderr.write(f'Failed to parse file={file_path} with handler={handler.__name__}. Skipping. Error="{str(e)}"')
            continue

        file_report = {
            "path": str(file_path),
            "functions": list(source_file.iter_functions(include_calls=calls)),
            "definitions": list(source_file.iter_definitions(include_methods=True, include_calls=calls)),
        }
        relative_path = get_smart_relative_path(file_path, path)
        reports[relative_path] = file_report
    return reports
