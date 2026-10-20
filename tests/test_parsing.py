"""Unit tests for CryoDRAM data parsing routines."""

import pytest
from pathlib import Path
import tempfile
from cryodram.analyze_results import (
    parse_cryomem_file,
    parse_mosfet_file,
    parse_waveform_dat,
    analyze_1t_waveform,
    analyze_3t_waveform,
)


def test_parse_cryomem_sample():
    sample_text = """
    Results:
    Timing Components:
	   t_RCD (Row to column command delay): 3.53964 ns
	   t_RAS (Row access strobe latency): 5.64935 ns
	   t_RC (Row cycle): 7.74234 ns
	   t_CAS (Column access strobe latency): 6.86159 ns
	   t_RP (Row precharge latency): 2.09299 ns
	   t_RRD (Row activation to row activation delay): 1.66303 ns
    Power Components:
	   Activation energy: 0.507796 nJ
	   Read energy: 1.80089 nJ
	   Write energy: 1.80094 nJ
	   Precharge energy: 0.221989 nJ
           Standby leakage per bank: 2.33572 mW
    Area Components:
	   DRAM core area: 134 mm2
	   DRAM area per die: 172.593 mm2
	   Area efficiency: 34.4009%
    """
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
        tmp.write(sample_text)
        tmp_path = Path(tmp.name)

    try:
        parsed = parse_cryomem_file(tmp_path)
        assert parsed["t_RCD_ns"] == pytest.approx(3.53964, rel=1e-4)
        assert parsed["t_RAS_ns"] == pytest.approx(5.64935, rel=1e-4)
        assert parsed["read_energy_nJ"] == pytest.approx(1.80089, rel=1e-4)
        assert parsed["standby_leakage_per_bank_mW"] == pytest.approx(2.33572, rel=1e-4)
        assert parsed["area_efficiency_percent"] == pytest.approx(34.4009, rel=1e-4)
    finally:
        tmp_path.unlink()


def test_parse_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_cryomem_file(Path("non_existent_file_xyz.txt"))


def test_parse_waveform_dat_valid():
    sample_waveform = """
    time time v(wl) v(bl) v(sd)
    0.00e+00 0.00e+00 0.0 0.0 0.0
    1.00e-09 1.00e-09 5.0 5.0 4.05
    2.00e-09 2.00e-09 0.0 0.0 4.05
    """
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
        tmp.write(sample_waveform)
        tmp_path = Path(tmp.name)

    try:
        header, rows = parse_waveform_dat(tmp_path)
        assert len(header) == 5
        assert len(rows) == 3
        assert rows[1][4] == 4.05

        analysis = analyze_1t_waveform(header, rows)
        assert analysis["v_store_max_V"] == 4.05
        assert analysis["threshold_loss_V"] == pytest.approx(0.95, rel=1e-3)
    finally:
        tmp_path.unlink()


def test_parse_waveform_dat_empty():
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
        tmp.write("")
        tmp_path = Path(tmp.name)

    try:
        with pytest.raises(ValueError, match="empty"):
            parse_waveform_dat(tmp_path)
    finally:
        tmp_path.unlink()


def test_parse_waveform_dat_malformed():
    sample_corrupted = """
    time time v(wl) v(bl) v(sd)
    0.00e+00 0.00e+00 NOT_A_FLOAT 0.0 0.0
    """
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
        tmp.write(sample_corrupted)
        tmp_path = Path(tmp.name)

    try:
        with pytest.raises(ValueError, match="Malformed numerical data"):
            parse_waveform_dat(tmp_path)
    finally:
        tmp_path.unlink()
