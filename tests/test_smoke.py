"""Smoke test for the CryoDRAM end-to-end analysis and plotting routines."""

import shutil
from pathlib import Path
import pytest
from cryodram.analyze_results import main as run_analysis
from cryodram.plot_results import main as run_plotting


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parent.parent


def test_tool_availability():
    """Verify essential system tools are present."""
    assert shutil.which("python3") is not None, "python3 must be available."
    assert shutil.which("ngspice") is not None, "ngspice must be available for circuit simulations."


def test_end_to_end_analysis_and_plotting(repo_root):
    """Test that running analysis and plotting executes cleanly without exception."""
    results_dir = repo_root / "results"
    assert (results_dir / "mosfet_77K.txt").is_file(), "mosfet_77K.txt required for smoke test"
    assert (results_dir / "cryomem_77K.txt").is_file(), "cryomem_77K.txt required for smoke test"

    # Run analysis
    run_analysis()
    assert (results_dir / "comparison.csv").is_file()
    assert (results_dir / "summary.json").is_file()

    # Run plotting
    run_plotting()
    assert (results_dir / "transistor_drive_current.png").is_file()
    assert (results_dir / "dram_timing.png").is_file()
