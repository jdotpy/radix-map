import argparse
import subprocess
import sys
from pathlib import Path
import pytest

# Setup paths
TEST_DATA_DIR = Path(__file__).parent / "snapshots"
SNAPSHOT_SUFFIX = '.snapshot'

# Dynamically locate the radix executable inside your .env directory
# Falls back to standard system path lookup if .env isn't present
VENV_BIN = Path(__file__).parents[1] / ".env" / "bin" / "radix"
RADIX_EXE = str(VENV_BIN) if VENV_BIN.exists() else "radix"


def get_test_pairs():
    """Finds all source files and pairs them with their corresponding .snapshot output."""
    pairs = []
    supported_extensions = ['.py', '.go', '.js', '.md', '.scala']
    for ext in supported_extensions:
        for source_file in TEST_DATA_DIR.glob(f"*{ext}"):
            snapshot_file = source_file.with_suffix(source_file.suffix + SNAPSHOT_SUFFIX)
            pairs.append((source_file, snapshot_file))
    return pairs


def run_radix_subprocess(source_path: Path) -> str:
    """Executes radix as a true CLI subprocess and captures its stdout."""
    # Simulates: radix map tests/snapshots/file.ext
    cmd = [RADIX_EXE, "map", str(source_path)]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False  # Allow us to safely assert on non-zero exit codes if things fail
    )
    
    if result.returncode != 0:
        raise RuntimeError(
            f"CLI Execution failed with exit code {result.returncode}.\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        
    return result.stdout


# ============================================================================
# MODE 1: PYTEST E2E CONTEXT
# ============================================================================
@pytest.mark.parametrize("source_path, expected_path", get_test_pairs())
def test_e2e_pipeline_snapshot(source_path, expected_path):
    if not expected_path.exists():
        pytest.fail(f"Snapshot missing for {source_path.name}. Run generation tool first.")
        
    # Execute the actual binary application
    cli_output = run_radix_subprocess(source_path)
    expected_output = expected_path.read_text()
    
    assert cli_output == expected_output, (
        f"E2E Pipeline snapshot comparison failed for {source_path.name}.\n"
        f"This could mean your CLI formatting, entrypoint logic, or parser broke."
    )


# ============================================================================
# MODE 2: CLI GENERATION/UPDATE CONTEXT
# ============================================================================

def clitool_main():
    # 1. Base Parser Setup
    parser = argparse.ArgumentParser(description="Radix E2E Snapshot Manager")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available subcommands")

    # 2. Define the 'update' subcommand
    # nargs='*' allows 0 or more positional arguments
    update_parser = subparsers.add_parser("update", help="Update snapshots via binary execution")
    update_parser.add_argument(
        "targets",
        metavar="TARGET",
        nargs="*",
        help="Target names to update (e.g., 'js_ex2', 'all'). Leaves empty to prompt interactive selection."
    )
    
    args = parser.parse_args()

    # Right now we only have 'update', but this sets up a clean architecture for future commands
    if args.command == "update":
        targets = args.targets
        if not targets:
            print("💡 No snapshot targets specified.")
            try:
                raw_input = input("👉 Enter target name(s) separated by spaces (or 'all'): ").strip()
                # Split user input into a list of targets, discarding empty spaces
                targets = [t for t in raw_input.split() if t]
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Cancelled.")
                sys.exit(1)

        if not targets:
            print("❌ Error: Target name list cannot be empty.")
            sys.exit(1)

        pairs = get_test_pairs()
        updated_count = 0

        run_all = "all" in targets

        for source_path, expected_path in pairs:
            # Check if this specific file matches any of the requested targets
            if run_all or source_path.stem in targets:
                print(f"Spawning subprocess pipeline for {source_path.name}...")
                try:
                    cli_output = run_radix_subprocess(source_path)
                    expected_path.write_text(cli_output)
                    updated_count += 1
                except RuntimeError as err:
                    print(f"❌ Failed to generate snapshot for {source_path.name}:\n{err}")
                    sys.exit(1)

        if updated_count == 0:
            print(f"❌ Error: No local snapshot source files found matching target names: {', '.join(targets)}")
            sys.exit(1)
        else:
            print(f"✅ Successfully updated {updated_count} snapshot file(s) via subprocess execution.")

if __name__ == "__main__":
    clitool_main()