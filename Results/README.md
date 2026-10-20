# Results Catalogue & Data Provenance

This directory stores the authoritative simulation logs, waveform data, numerical comparisons, and generated plots for the CryoDRAM project.

---

## Output Catalogue

| Filename | Description | Source / Model | Key Metric(s) & Units | Regeneration Command |
|---|---|---|---|---|
| `mosfet_77K.txt` | 77 K MOSFET & interconnect parameters | CryoMOSFET (`pgen.py`) | $I_{on}$ (µA/µm), $V_{th}$ (V), $R_{wire}$ (µΩ·cm) | `make run-mosfet` |
| `mosfet_4K.txt` | 4 K MOSFET & interconnect parameters | CryoMOSFET (`pgen.py`) | $I_{on}$ (µA/µm), $V_{th}$ (V), $R_{wire}$ (µΩ·cm) | `make run-mosfet` |
| `cryomem_77K.txt` | 77 K 32 nm DRAM array performance | CryoMEM (CACTI) | $t_{RCD}, t_{RAS}, t_{RC}$ (ns), energy (nJ), leakage (mW) | `make run-cryo-mem` |
| `cryomem_4K.txt` | 4 K 32 nm DRAM array performance | CryoMEM (CACTI) | $t_{RCD}, t_{RAS}, t_{RC}$ (ns), energy (nJ), leakage (mW) | `make run-cryo-mem` |
| `dram_1t.log` | ngspice simulation log for 1T-1C DRAM | ngspice (`dram_1t.sp`) | Stored high/low voltage (V) | `make run-spice` |
| `dram_3t.log` | ngspice simulation log for 3T DRAM | ngspice (`dram_3t.sp`) | Stored high voltage (V) | `make run-spice` |
| `dram_1t_waveform.dat` | Transient voltage trace for 1T-1C cell | ngspice (`dram_1t.sp`) | Time (s), $V(WL), V(BL), V(SD)$ (V) | `make run-spice` |
| `dram_3t_waveform.dat` | Transient voltage trace for 3T cell | ngspice (`dram_3t.sp`) | Time (s), $V(WL), V(RL), V(SN), V(BBL)$ (V) | `make run-spice` |
| `comparison.csv` | Unified 77 K vs 4 K comparison table | `analyze_results.py` | Metrics, values, and percentage deltas (%) | `make analyze` |
| `summary.json` | Machine-readable metrics & provenance | `analyze_results.py` | Full structured JSON with metadata | `make analyze` |
| `transistor_drive_current.png` | NMOS & PMOS drive current figure | `plot_results.py` | $I_{on}$ (µA/µm) at 300 K, 77 K, 4 K | `make plot` |
| `wire_resistivity.png` | Bulk wire resistivity scaling figure | `plot_results.py` | $R_{wire}$ (µΩ·cm) at 300 K, 77 K, 4 K | `make plot` |
| `dram_timing.png` | Access latency components bar chart | `plot_results.py` | $t_{RCD}, t_{RAS}, t_{RC}, t_{CAS}, t_{RP}, t_{RRD}$ (ns) | `make plot` |
| `dram_energy.png` | Access energy components bar chart | `plot_results.py` | Activation, Read, Write, Precharge energy (nJ) | `make plot` |
| `standby_leakage.png` | Standby leakage reduction plot | `plot_results.py` | Leakage power (mW) per bank (-80.96% at 4 K) | `make plot` |
| `dram_spice_waveforms.png` | 1T & 3T SPICE transient waveform plot | `plot_results.py` | Time (ns) vs Voltage (V) | `make plot` |

---

## Safe Cleanup

To remove generated result files without touching documentation or configuration:
```bash
make clean
# or directly:
bash scripts/clean_outputs.sh
```
