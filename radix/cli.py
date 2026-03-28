from . import core
from . import report
from .handlers.registry import HandlerRegistry

import sys
import importlib.util

def parse_language_settings(lang_args):
    fallback = None
    overrides = {}
    
    if not lang_args:
        return None, {}
    if isinstance(lang_args, str):
        lang_args = [lang_args]

    for entry in lang_args:
        if ':' in entry:
            source, target = entry.split(':', 1)
            overrides[source.lower()] = target.lower()
        else:
            fallback = entry
    return fallback, overrides

def cli_map(args):
    handler_fallback, lang_overrides = parse_language_settings(args.lang)
    scanner = core.make_scanner(args.path, handler_overrides=lang_overrides, fallback_handler=handler_fallback)
    source = core.get_source(args.path)
    if source.requries_explicit_lang and handler_fallback is None:
        print("Using stdin as input but cant guess content. No lang fallback given with --lang")
        print("Use `--lang py` or similar to tell us what to parse")
        sys.exit(1)

    reports_by_file = core.analyze_project(scanner, source, calls=args.calls, lines=args.lines)
    report.display_txt(
        reports_by_file,
        sys.stdout,
        lines=args.lines,
    )

def cli_registry(args):
    print('Supported languages:')
    for file_type, info in HandlerRegistry.LIBRARIES.items():
        spec = importlib.util.find_spec(info['lib'])
        has_package = spec is not None
        extra_info = []
        if not has_package:
            status = "Missing"
            extra_info.append('\t')
            extra_info.append(f'to install run `pip install {info["package_name"]}`')
        else:
            status = "Installed"
        print('\t', file_type, '\t', status, *extra_info)

