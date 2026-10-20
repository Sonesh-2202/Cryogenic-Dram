#!/usr/bin/env python3
"""1T vs 3T DRAM quantitative comparison.

Measured values are read off the Cadence Virtuoso transient sims (waveform PNGs
in the repo root); charge/energy/retention are derived analytically.

    python3 dram_analysis.py            # print table
    python3 dram_analysis.py --plot    
"""

import argparse

VDD          = 5.0
W_ACCESS     = 2.0e-6
L_ACCESS     = 180e-9

# 1T-1C cell
CS_1T        = 1.0e-12       # storage cap C0
V1_STORE_1T  = 4.2          # measured stored '1'
V0_STORE_1T  = 0.9          # measured stored '0'
BL_SWING_1T  = 15e-3        # measured bit-line swing on read

# 3T cell (charge on read-transistor gate cap)
CS_3T        = 2.0e-15
V_STORE_3T   = 4.69

I_LEAK       = 1.0e-12       # assumed worst-case cell leakage for retention est.


def report():
    vt = VDD - V1_STORE_1T
    q1 = CS_1T * V1_STORE_1T
    e1 = CS_1T * VDD * VDD
    tret1 = CS_1T * ((V1_STORE_1T - V0_STORE_1T) / 2.0) / I_LEAK
    q3 = CS_3T * V_STORE_3T
    e3 = CS_3T * VDD * VDD
    tret3 = CS_3T * (V_STORE_3T / 2.0) / I_LEAK

    print("\n=== 1T vs 3T DRAM ===\n")
    print(f"{'Metric':<34}{'1T-1C':>16}{'3T':>16}")
    print("-" * 66)
    print(f"{'Transistors / cell':<34}{'1 (+1 cap)':>16}{'3':>16}")
    print(f"{'Storage capacitance':<34}{CS_1T*1e12:>13.2f} pF{CS_3T*1e15:>13.2f} fF")
    print(f"{'Stored 1 level (measured)':<34}{V1_STORE_1T:>14.2f} V{V_STORE_3T:>14.2f} V")
    print(f"{'Threshold drop on write-1':<34}{vt:>14.2f} V{'0.00':>14} V")
    print(f"{'Stored charge Q = CV':<34}{q1*1e12:>12.2f} pC{q3*1e15:>12.2f} fC")
    print(f"{'Write energy C*Vdd^2':<34}{e1*1e12:>11.2f} pJ{e3*1e15:>12.3f} fJ")
    print(f"{'Read type':<34}{'destructive':>16}{'non-destructive':>16}")
    print(f"{'Bit-line read swing (measured)':<34}{BL_SWING_1T*1e3:>13.1f} mV{'full-rail':>16}")
    print(f"{'Retention @ 1 pA (analytical)':<34}{tret1*1e3:>13.2f} ms{tret3*1e6:>13.2f} us")
    print()


def make_plot():
    import os
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))

    axes[0].bar(["1T-1C", "3T"], [1, 3], color=["#2980b9", "#c0392b"])
    axes[0].set_title("Transistors per cell"); axes[0].set_ylabel("count")
    for i, v in enumerate([1, 3]):
        axes[0].text(i, v + 0.05, str(v), ha="center", fontweight="bold")

    stored = [V1_STORE_1T, V_STORE_3T]
    axes[1].bar(["1T-1C", "3T"], [VDD, VDD], color="#dfe6e9", label="Vdd rail")
    axes[1].bar(["1T-1C", "3T"], stored, color=["#2980b9", "#c0392b"], label="stored '1'")
    axes[1].axhline(VDD, ls="--", color="gray", lw=0.8)
    axes[1].set_title("Stored '1' level vs 5 V rail"); axes[1].set_ylabel("V"); axes[1].set_ylim(0, 5.6)
    axes[1].legend(fontsize=8)
    for i, v in enumerate(stored):
        axes[1].text(i, v + 0.08, f"{v} V", ha="center", fontweight="bold")

    leak = np.logspace(-15, -9, 100)
    axes[2].loglog(leak * 1e12, CS_1T * ((V1_STORE_1T - V0_STORE_1T) / 2.0) / leak * 1e3,
                   color="#2980b9", label="1T-1C (1 pF)")
    axes[2].loglog(leak * 1e12, CS_3T * (V_STORE_3T / 2.0) / leak * 1e3,
                   color="#c0392b", label="3T (~2 fF)")
    axes[2].set_title("Analytical retention vs leakage")
    axes[2].set_xlabel("cell leakage (pA)"); axes[2].set_ylabel("retention (ms)")
    axes[2].grid(True, which="both", ls=":", lw=0.5); axes[2].legend(fontsize=8)

    fig.suptitle("1T vs 3T DRAM comparison", fontweight="bold")
    fig.tight_layout()
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results", "dram_comparison.png"))
    fig.savefig(out, dpi=120)
    print(f"Wrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plot", action="store_true")
    args = ap.parse_args()
    report()
    if args.plot:
        make_plot()


if __name__ == "__main__":
    main()
