"""Tests for schema, format, and data validation of generated results."""

import json
import csv
from pathlib import Path
import pytest


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parent.parent


def test_comparison_csv_schema(repo_root):
    csv_path = repo_root / "results" / "comparison.csv"
    assert csv_path.is_file(), "results/comparison.csv does not exist. Run analysis first."
    assert csv_path.stat().st_size > 0, "results/comparison.csv is empty."

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        expected_fields = ["Category", "Metric", "Unit", "Value_77K", "Value_4K", "Delta_Percent", "Notes"]
        assert fields == expected_fields, f"Unexpected CSV headers: {fields}"

        rows = list(reader)
        assert len(rows) >= 10, f"Expected at least 10 metrics in comparison table, found {len(rows)}"

        # Check that specific key metrics exist
        metric_names = [r["Metric"] for r in rows]
        assert any("Row-to-Column Command Delay" in m for m in metric_names)
        assert any("Standby Leakage Power" in m for m in metric_names)
        assert any("NMOS Drive Current" in m for m in metric_names)
        assert any("Bulk Wire Resistivity" in m for m in metric_names)


def test_summary_json_schema(repo_root):
    json_path = repo_root / "results" / "summary.json"
    assert json_path.is_file(), "results/summary.json does not exist. Run analysis first."
    assert json_path.stat().st_size > 0, "results/summary.json is empty."

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "metadata" in data
    assert "cryomem_results" in data
    assert "cryo_mosfet_results" in data
    assert "spice_simulations" in data
    assert "scientific_limitations" in data

    # Verify CryoMEM 77K and 4K data points
    mem = data["cryomem_results"]
    assert "77K" in mem and "4K" in mem
    assert mem["77K"]["t_RCD_ns"] == pytest.approx(3.53964, rel=1e-3)
    assert mem["4K"]["t_RCD_ns"] == pytest.approx(3.51226, rel=1e-3)

    # Verify Standby leakage values
    leak_77 = mem["77K"]["standby_leakage_per_bank_mW"]
    leak_4 = mem["4K"]["standby_leakage_per_bank_mW"]
    assert leak_77 == pytest.approx(2.33572, rel=1e-3)
    assert leak_4 == pytest.approx(0.444796, rel=1e-3)


def test_required_figure_files_exist(repo_root):
    figures = [
        "transistor_drive_current.png",
        "wire_resistivity.png",
        "dram_timing.png",
        "dram_energy.png",
        "standby_leakage.png",
        "dram_spice_waveforms.png",
    ]
    results_dir = repo_root / "results"
    for fig in figures:
        p = results_dir / fig
        assert p.is_file(), f"Required figure missing: {p}"
        assert p.stat().st_size > 5000, f"Figure file suspiciously small ({p.stat().st_size} bytes): {p}"
