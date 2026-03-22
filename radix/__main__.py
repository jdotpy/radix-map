from . import core
from . import cli
import argparse
import sys

def create_parser():
    parser = argparse.ArgumentParser(prog="radix", description="Codebase Mapping Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")


    # 'registry' subcommand
    registry_parser = subparsers.add_parser("registry", help="Show registered file handlers and their libraries")

    # 'map' subcommand
    map_parser = subparsers.add_parser("map", help="Generate a structural map of the codebase")
    
    # Positional argument
    map_parser.add_argument("path", help="Path to file or directory to scan")

    # Fine-grained Overrides (Your original flags)
    group = map_parser.add_argument_group("Detail Overrides")
    group.add_argument("--params", action="store_true", help="Include function parameters")
    group.add_argument("--calls", action="store_true", help="Include internal function calls")
    group.add_argument("--types", action="store_true", help="Include type definitions/properties")
    
    # Configuration
    map_parser.add_argument("--max-size", type=int, default=200000, 
                            help="Skip files larger than this size in bytes")



    return parser


def entrypoint():
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "map":
        cli.cli_map(args)
    elif args.command == "registry":
        cli.cli_registry(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    entrypoint()