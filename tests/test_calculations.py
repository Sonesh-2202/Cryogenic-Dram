"""Unit tests for CryoDRAM metric calculations and analytical models."""

import pytest
from cryodram.analyze_results import calculate_percent_delta, analyze_1t_waveform, analyze_3t_waveform


def test_calculate_percent_delta():
    # 77K -> 4K reduction of leakage (2.33572 -> 0.444796)
    delta = calculate_percent_delta(2.33572, 0.444796)
    assert delta == pytest.approx(-80.9567, rel=1e-3)

    # Increase in read energy (1.80089 -> 1.83331)
    delta_energy = calculate_percent_delta(1.80089, 1.83331)
    assert delta_energy == pytest.approx(1.8002, rel=1e-3)

    # Edge cases
    assert calculate_percent_delta(0.0, 5.0) == 0.0
    assert calculate_percent_delta(10.0, 10.0) == 0.0
    assert calculate_percent_delta(10.0, 20.0) == 100.0


def test_1t_analytical_calculations():
    header = ["time", "time", "v(wl)", "v(bl)", "v(sd)"]
    rows = [
        [0.0, 0.0, 0.0, 0.0, 0.0],
        [1e-9, 1e-9, 5.0, 5.0, 4.2],
        [2e-9, 2e-9, 0.0, 0.0, 0.9],
    ]
    res = analyze_1t_waveform(header, rows)
    assert res["v_store_max_V"] == 4.2
    assert res["v_store_min_V"] == 0.0
    assert res["threshold_loss_V"] == pytest.approx(0.8, rel=1e-4)

    # Q = C * V = 1pF * 4.2V = 4.2 pC
    assert res["analytical_charge_pC"] == pytest.approx(4.2, rel=1e-4)
    # E = C * Vdd^2 = 1pF * 25V^2 = 25 pJ
    assert res["analytical_write_energy_pJ"] == pytest.approx(25.0, rel=1e-4)
    # Retention t_ret = C * (V1 - V0) / (2 * I_leak) = 1e-12 * (4.2 - 0) / (2 * 1e-12) = 2.1 s = 2100 ms
    assert res["analytical_retention_ms"] == pytest.approx(2100.0, rel=1e-4)


def test_3t_analytical_calculations():
    header = ["time", "time", "v(wl)", "v(rl)", "v(sn)", "v(bbl)"]
    rows = [
        [0.0, 0.0, 0.0, 0.0, 0.0, 5.0],
        [1e-9, 1e-9, 5.0, 0.0, 4.69, 5.0],
        [2e-9, 2e-9, 0.0, 5.0, 4.69, 0.2],
    ]
    res = analyze_3t_waveform(header, rows)
    assert res["v_store_max_V"] == 4.69
    assert res["bitline_swing_V"] == pytest.approx(4.8, rel=1e-3)
    # Q = 2 fF * 4.69 V = 9.38 fC
    assert res["analytical_charge_fC"] == pytest.approx(9.38, rel=1e-3)
    # E = 2 fF * 25 V^2 = 50 fJ
    assert res["analytical_write_energy_fJ"] == pytest.approx(50.0, rel=1e-3)
