from . import core
from . import report

def cli_map(args):
    reports_by_file = core.analyze_project(args.path, calls=args.calls, params=args.params)
    report.display_txt(reports_by_file)

