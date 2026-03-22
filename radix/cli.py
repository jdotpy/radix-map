from . import core
from . import report
from .handlers.registry import HandlerRegistry

import importlib.util

def cli_map(args):
    reports_by_file = core.analyze_project(args.path, calls=args.calls, params=args.params)
    report.display_txt(reports_by_file)



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

