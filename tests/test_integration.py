import pytest
from pathlib import Path
from project.handler_registry import HandlerRegistry
from project.analyzer import ViewEngine

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
        source_file = TEST_DATA_DIR / snapshot_file[:-len(SNAPSHOT_SUFFIX)]
        if source_file.exists():
            pairs.append((source_file, snapshot_file))
    return pairs

@pytest.mark.parametrize("source_path, expected_path", get_test_pairs())
def test_deep_header_generation(source_path, expected_path):
    source_code = source_path.read_bytes()
    expected_output = expected_path.read_text().strip()
    
    handler = HandlerRegistry.get_handler_for_ext(source_path.suffix)
    
    # 3. Process: Source -> Normalized Symbols
    # We pass the 'project/filename' part as the virtual path for the header
    virtual_path = f"project/{source_path.name}"
    report = handler.get_report(virtual_path, source_code)
    
    # 4. Render: Symbols -> Deep-Header String
    # Note: Using Tier 3 to verify the ---:: calls are working
    engine = ViewEngine()
    actual_output = engine.render_deep_header(report, tier=3).strip()
    
    # 5. Assert (using strip to ignore trailing newlines)
    assert actual_output == expected_output, f"Snapshot comparison failed for {source_path.name}"