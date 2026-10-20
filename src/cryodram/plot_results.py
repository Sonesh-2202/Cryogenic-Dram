#!/usr/bin/env python3
"""Automated Figure Generation for CryoDRAM Research Results.

Generates publication-quality figures:
1. transistor_drive_current.png: NMOS & PMOS drive currents at 77 K and 4 K (vs 300 K ref)
2. wire_resistivity.png: Interconnect resistivity scaling
3. dram_timing.png: CACTI access latency components (tRCD, tRAS, tRC, tCAS, tRP, tRRD)
4. dram_energy.png: Energy per access components (Activation, Read, Write, Precharge)
5. standby_leakage.png: Standby leakage power per bank (77 K vs 4 K)
6. dram_spice_waveforms.png: 1T-1C write/read & 3T non-destructive read waveforms
"""

import os
import sys
import json
from pathlib import Path
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def load_summary(results_dir: Path) -> dict:
    summary_path = results_dir / "summary.json"
    if not summary_path.is_file():
        raise FileNotFoundError(f"summary.json not found in {results_dir}. Run analyze_results.py first.")
    with open(summary_path, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_drive_current(summary: dict, output_path: Path):
    """Plot NMOS & PMOS drive currents across 300 K (ref), 77 K, and 4 K."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

    mos_77 = summary["cryo_mosfet_results"]["77K"]
    mos_4 = summary["cryo_mosfet_results"]["4K"]

    nmos_ref = mos_77.get("nmos_ref", {}).get("Ion", 1668.14)
    nmos_77k = mos_77.get("nmos_target", {}).get("Ion", 3832.68)
    nmos_4k = mos_4.get("nmos_target", {}).get("Ion", 3418.77)

    pmos_ref = mos_77.get("pmos_ref", {}).get("Ion", 1233.39)
    pmos_77k = mos_77.get("pmos_target", {}).get("Ion", 2822.54)
    pmos_4k = mos_4.get("pmos_target", {}).get("Ion", 2508.65)

    x = np.arange(3)
    width = 0.35

    nmos_vals = [nmos_ref, nmos_77k, nmos_4k]
    pmos_vals = [pmos_ref, pmos_77k, pmos_4k]

    rects1 = ax.bar(x - width/2, nmos_vals, width, label="NMOS Ion", color="#1f77b4")
    rects2 = ax.bar(x + width/2, pmos_vals, width, label="PMOS Ion", color="#d62728")

    ax.set_ylabel("Drive Current Ion (µA/µm)", fontsize=11, fontweight="bold")
    ax.set_title("MOSFET Drive Current: 300 K (Ref 0.9 V) vs 77 K & 4 K (Target 1.2 V)", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["300 K (Ref, 0.9 V)", "77 K (Target, 1.2 V)", "4 K (Target, 1.2 V)"], fontsize=10)
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    # Bar value labels
    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f"{height:.1f}",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8, fontweight="bold")

    fig.text(0.5, 0.01,
             "Note: Reference configuration uses Vdd = 0.9 V; cryogenic target runs use Vdd = 1.2 V.",
             ha="center", fontsize=8, style="italic", color="#555555")

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(output_path)
    plt.close(fig)
    print(f"[+] Saved: {output_path}")


def plot_wire_resistivity(summary: dict, output_path: Path):
    """Plot Bulk wire resistivity across 300 K, 77 K, and 4 K."""
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)

    mos_77 = summary["cryo_mosfet_results"]["77K"]
    mos_4 = summary["cryo_mosfet_results"]["4K"]

    r_300 = mos_77.get("wire_ref", {}).get("Rwire", 1.7728)
    r_77 = mos_77.get("wire_target", {}).get("Rwire", 0.2192)
    r_4 = mos_4.get("wire_target", {}).get("Rwire", 0.2036)

    temps = ["300 K (Ref)", "77 K (Target)", "4 K (Target)"]
    vals = [r_300, r_77, r_4]
    colors = ["#7f7f7f", "#2ca02c", "#17becf"]

    bars = ax.bar(temps, vals, color=colors, width=0.45)
    ax.set_ylabel("Bulk Wire Resistivity (µΩ·cm)", fontsize=11, fontweight="bold")
    ax.set_title("Copper Interconnect Resistivity vs Temperature", fontsize=11, fontweight="bold")
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.4f} µΩ·cm",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"[+] Saved: {output_path}")


def plot_dram_timing(summary: dict, output_path: Path):
    """Plot CACTI DRAM timing latencies at 77 K vs 4 K."""
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)

    mem_77 = summary["cryomem_results"]["77K"]
    mem_4 = summary["cryomem_results"]["4K"]

    metrics = [
        ("tRCD", "t_RCD_ns"),
        ("tRAS", "t_RAS_ns"),
        ("tRC", "t_RC_ns"),
        ("tCAS", "t_CAS_ns"),
        ("tRP", "t_RP_ns"),
        ("tRRD", "t_RRD_ns")
    ]

    labels = [m[0] for m in metrics]
    v_77 = [mem_77.get(m[1], 0.0) for m in metrics]
    v_4 = [mem_4.get(m[1], 0.0) for m in metrics]

    x = np.arange(len(labels))
    width = 0.35

    rects1 = ax.bar(x - width/2, v_77, width, label="77 K", color="#3498db")
    rects2 = ax.bar(x + width/2, v_4, width, label="4 K", color="#9b59b6")

    ax.set_ylabel("Latency (ns)", fontsize=11, fontweight="bold")
    ax.set_title("CryoMEM 32 nm DRAM Timing: 77 K vs 4 K", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f"{height:.2f}",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"[+] Saved: {output_path}")


def plot_dram_energy(summary: dict, output_path: Path):
    """Plot CACTI DRAM energy per operation at 77 K vs 4 K."""
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)

    mem_77 = summary["cryomem_results"]["77K"]
    mem_4 = summary["cryomem_results"]["4K"]

    metrics = [
        ("Activation", "activation_energy_nJ"),
        ("Read", "read_energy_nJ"),
        ("Write", "write_energy_nJ"),
        ("Precharge", "precharge_energy_nJ")
    ]

    labels = [m[0] for m in metrics]
    v_77 = [mem_77.get(m[1], 0.0) for m in metrics]
    v_4 = [mem_4.get(m[1], 0.0) for m in metrics]

    x = np.arange(len(labels))
    width = 0.35

    rects1 = ax.bar(x - width/2, v_77, width, label="77 K", color="#2ecc71")
    rects2 = ax.bar(x + width/2, v_4, width, label="4 K", color="#e67e22")

    ax.set_ylabel("Energy per Access (nJ)", fontsize=11, fontweight="bold")
    ax.set_title("CryoMEM 32 nm DRAM Energy Components: 77 K vs 4 K", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f"{height:.3f}",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"[+] Saved: {output_path}")


def plot_standby_leakage(summary: dict, output_path: Path):
    """Plot Standby leakage reduction between 77 K and 4 K."""
    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=150)

    mem_77 = summary["cryomem_results"]["77K"]
    mem_4 = summary["cryomem_results"]["4K"]

    v_77 = mem_77.get("standby_leakage_per_bank_mW", 2.3357)
    v_4 = mem_4.get("standby_leakage_per_bank_mW", 0.4448)

    temps = ["77 K", "4 K"]
    vals = [v_77, v_4]
    colors = ["#e74c3c", "#3498db"]

    bars = ax.bar(temps, vals, color=colors, width=0.45)
    ax.set_ylabel("Standby Leakage per Bank (mW)", fontsize=11, fontweight="bold")
    ax.set_title("DRAM Standby Leakage Reduction (77 K vs 4 K)", fontsize=11, fontweight="bold")
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    delta_pct = ((v_4 - v_77) / v_77) * 100

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.4f} mW",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.annotate(f"Reduction: {abs(delta_pct):.1f}%",
                xy=(1, v_4), xytext=(0.5, (v_77 + v_4) / 2),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="red"),
                fontsize=10, fontweight="bold", color="red",
                bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.4))

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"[+] Saved: {output_path}")


def plot_spice_waveforms(results_dir: Path, output_path: Path):
    """Plot SPICE transient waveform data for 1T-1C and 3T DRAM cells."""
    dat_1t = results_dir / "dram_1t_waveform.dat"
    dat_3t = results_dir / "dram_3t_waveform.dat"

    if not dat_1t.is_file() or not dat_3t.is_file():
        print("[!] Waveform data files not found. Skipping SPICE waveform plot.")
        return

    # Load 1T data: time time v(wl) v(bl) v(sd)
    data1 = np.loadtxt(dat_1t, skiprows=1)
    t1 = data1[:, 0] * 1e9  # ns
    vwl1 = data1[:, 2]
    vbl1 = data1[:, 3]
    vsd1 = data1[:, 4]

    # Load 3T data: time time v(wl) v(rl) v(sn) v(bbl)
    data3 = np.loadtxt(dat_3t, skiprows=1)
    t3 = data3[:, 0] * 1e9  # ns
    vwl3 = data3[:, 2]
    vrl3 = data3[:, 3]
    vsn3 = data3[:, 4]
    vbbl3 = data3[:, 5]

    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True, dpi=150)

    # 1T-1C plot
    axes[0].plot(t1, vwl1, "k--", alpha=0.6, label="Wordline V(WL)")
    axes[0].plot(t1, vbl1, "b-.", alpha=0.6, label="Bitline V(BL)")
    axes[0].plot(t1, vsd1, "r-", lw=1.8, label="Storage Node V(SD)")
    axes[0].set_ylabel("Voltage (V)", fontweight="bold")
    axes[0].set_title("1T-1C DRAM Cell Transient Simulation (Threshold Voltage Loss on Write-1)", fontsize=10, fontweight="bold")
    axes[0].grid(True, linestyle=":", alpha=0.6)
    axes[0].legend(loc="upper right", fontsize=8)

    # 3T plot
    axes[1].plot(t3, vwl3, "k--", alpha=0.5, label="Write WL V(WL)")
    axes[1].plot(t3, vrl3, "g--", alpha=0.5, label="Read Line V(RL)")
    axes[1].plot(t3, vsn3, "r-", lw=1.8, label="Storage Node V(SN)")
    axes[1].plot(t3, vbbl3, "m-", lw=1.5, label="Read Bitline V(BBL)")
    axes[1].set_xlabel("Time (ns)", fontweight="bold")
    axes[1].set_ylabel("Voltage (V)", fontweight="bold")
    axes[1].set_title("3T DRAM Cell Transient Simulation (Non-Destructive Full-Rail Read)", fontsize=10, fontweight="bold")
    axes[1].grid(True, linestyle=":", alpha=0.6)
    axes[1].legend(loc="upper right", fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"[+] Saved: {output_path}")


def main():
    root = get_repo_root()
    results_dir = root / "results"

    summary = load_summary(results_dir)

    plot_drive_current(summary, results_dir / "transistor_drive_current.png")
    plot_wire_resistivity(summary, results_dir / "wire_resistivity.png")
    plot_dram_timing(summary, results_dir / "dram_timing.png")
    plot_dram_energy(summary, results_dir / "dram_energy.png")
    plot_standby_leakage(summary, results_dir / "standby_leakage.png")
    plot_spice_waveforms(results_dir, results_dir / "dram_spice_waveforms.png")

    print("[+] All figures generated successfully.")


if __name__ == "__main__":
    main()
