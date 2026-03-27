import pytest
from pathlib import Path
from radix.core import analyze_project
from radix.report import display_txt
from radix.handlers.registry import HandlerRegistry
from .utils import MockScanner, MockSource

import io

# Setup paths
TEST_DATA_DIR = Path(__file__).parent / "snapshots"
SNAPSHOT_SUFFIX = '.snapshot'

def get_test_pairs():
    """
    Finds all source files and pairs them with their corresponding .snapshot output.
    Returns a list of tuples: (source_path, expected_output_path)
    """
    pairs = []
    for snapshot_file in TEST_DATA_DIR.glob("*" + SNAPSHOT_SUFFIX):
        # Matches 'python_ex1.py' with 'python_ex1.py.snapshot'
        source_file = TEST_DATA_DIR / str(snapshot_file)[:-len(SNAPSHOT_SUFFIX)]
        if source_file.exists():
            pairs.append((source_file, snapshot_file))
    return pairs

@pytest.mark.parametrize("source_path, expected_path", get_test_pairs())
def test_report_generation(source_path, expected_path):
    source_code = source_path.read_bytes()
    expected_output = expected_path.read_text()

    virtual_path = source_path.name
    handler = HandlerRegistry().get_handler_class(source_path.suffix)
    
    source = MockSource([])
    scanner = MockScanner(None, [
        (
            virtual_path,
            virtual_path,
            handler,
            lambda: source_code,
        )
    ])

    test_output = io.StringIO()
    reports_by_file = analyze_project(scanner, source)
    display_txt(reports_by_file, test_output)
    result = test_output.getvalue()
    assert result == expected_output, f"Snapshot comparison failed for {source_path.name}"