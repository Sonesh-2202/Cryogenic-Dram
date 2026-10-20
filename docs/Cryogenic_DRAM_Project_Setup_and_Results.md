# Impacts of Extreme Low Temperatures on Silicon Physics and DIMM Operations by Evaluating Cryogenic DRAM

## End-to-End Setup, Execution, Results, and Limitations

**Document type:** Reproducibility and project handover guide  
**Environment:** Windows 11 Pro + WSL 2 + Ubuntu 22.04  
**Project status:** CryoModel runs completed; 1T/3T SPICE demonstrations configured; results require final packaging and validation.

---

## 1. Project objective

This project investigates how very low temperatures may affect silicon transistor behaviour, interconnect resistance, and DRAM-level timing, energy, and leakage estimates.

The work uses two complementary tracks:

1. **CryoModel:** a research model that generates temperature-dependent MOSFET and wire parameters and feeds parameters into a CACTI-based memory model.
2. **1T and 3T DRAM SPICE circuits:** small circuit-level demonstrations that illustrate basic DRAM storage and access behaviour.

These tracks answer different questions. The generic SPICE circuits demonstrate circuit operation; they are not calibrated cryogenic simulations. CryoModel produces model-based estimates; it does not provide experimental measurements from a physical cryogenic DIMM.

## 2. Host computer and environment

The host is Windows 11 Pro. Linux tools were installed through Windows Subsystem for Linux (WSL 2), using Ubuntu 22.04.

Initial PowerShell checks showed:

```powershell
wsl --status
wsl --list --verbose
py --list
git --version
```

The initial WSL listing included `docker-desktop` but no Ubuntu distribution. The Windows Python launcher showed Python 3.14, and Git was installed. A separate Linux Python environment was subsequently used because the model dependencies and build process are easier to manage in Ubuntu.

### 2.1 Install Ubuntu 22.04 in WSL

Open **PowerShell as Administrator** and run:

```powershell
wsl --install -d Ubuntu-22.04
```

If Windows asks for a restart, restart and open **Ubuntu 22.04** from the Start menu. On first launch, create a Linux username and password. The password will not visibly echo while typing; this is normal terminal behaviour.

Check the distribution and WSL version:

```powershell
wsl --status
wsl --list --verbose
```

Expected outcome: Ubuntu 22.04 is listed, ideally with WSL version 2. The Docker Desktop distribution may also appear. Do not use `docker-desktop` as the working Linux distribution.

From the Ubuntu terminal, confirm the operating system:

```bash
cat /etc/os-release
uname -a
```

### 2.2 Install system packages

Run in Ubuntu:

```bash
sudo apt update
sudo apt upgrade -y

sudo apt install -y \
  git build-essential make gcc g++ \
  curl wget ca-certificates \
  python3 python3-pip python3-venv \
  ngspice \
  protobuf-compiler libprotobuf-dev \
  libboost-all-dev
```

These packages provide Git, compilers, Python and virtual-environment support, ngspice, Protocol Buffers, and Boost dependencies used by the project.

Check the tools:

```bash
git --version
python3 --version
g++ --version
ngspice --version
protoc --version
```

The active Ubuntu Python version during this project was **Python 3.10.12**. CryoModel's original scripts refer to Python 3.8 in subprocess calls, so a compatibility edit was needed later.

## 3. Create a project workspace and clone repositories

The project workspace is:

```text
~/CryoDRAM/
├── CryoModel/
└── 1T-and-3T-DRAM-using-Cadence/
```

Create the workspace and clone the repositories:

```bash
mkdir -p ~/CryoDRAM
cd ~/CryoDRAM

git clone https://github.com/SNU-HPCS/CryoModel.git

git clone https://github.com/srivastavadi/1T-and-3T-DRAM-using-Cadence.git
```

If either clone already exists, do not clone it again into the same directory. Use `cd` into the existing checkout and inspect it with `git status`.

The two repositories have different purposes:

- `CryoModel/` contains cryogenic device-parameter generators and the CryoMEM memory model.
- `1T-and-3T-DRAM-using-Cadence/` contains SPICE netlists for small 1T and 3T DRAM examples and a Python plotting script.

## 4. Set up Python dependencies

A virtual environment was created inside the circuit repository:

```bash
cd ~/CryoDRAM/1T-and-3T-DRAM-using-Cadence

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install numpy matplotlib
```

The shell prompt should begin with `(.venv)` while the environment is active. The environment is physically located in the circuit repository, but Python commands can also be run against CryoModel from the same shell.

For the older generated Protocol Buffers code in this CryoModel checkout, the installed `protobuf` package was pinned to 3.20.3:

```bash
python -m pip install "protobuf==3.20.3"
```

Check:

```bash
python --version
python -m pip show protobuf numpy matplotlib
```

The project ran with Python 3.10.12 and protobuf 3.20.3. Dependency compatibility may differ if the repositories change in future.

To reactivate the environment in a new Ubuntu terminal:

```bash
source ~/CryoDRAM/1T-and-3T-DRAM-using-Cadence/.venv/bin/activate
```

To leave the environment:

```bash
deactivate
```

## 5. Prepare the 1T and 3T DRAM SPICE demonstrations

### 5.1 Repository contents

The circuit repository contained:

```text
1T-and-3T-DRAM-using-Cadence/
├── 1T DRAM.png
├── 1T DRAM test circuit.png
├── 3T DRAM.png
├── 3T DRAM test circuit.png
├── README.md
├── analysis/
│   └── dram_analysis.py
├── results/
└── spice/
    ├── dram_1t.sp
    ├── dram_3t.sp
    └── nmos_generic.inc
```

### 5.2 Correct the 1T model include path

The 1T SPICE netlist originally used:

```spice
.include nmos_generic.inc
```

Because the shared model file is in the `spice/` directory and the simulation is launched from the repository root, it was changed to:

```spice
.include spice/nmos_generic.inc
```

This makes the include path resolve when commands are run from the repository root.

### 5.3 Make the simulations batch-friendly

Interactive `plot` statements in the netlists were removed or disabled so ngspice could run without waiting for a graphical session. Waveform data was written to files instead.

The 1T netlist includes a data export command after the simulation:

```spice
set wr_singlescale
set wr_vecnames
wrdata results/dram_1t_waveform.dat v(wl) v(bl) v(sd)
```

The 3T netlist includes:

```spice
set wr_singlescale
set wr_vecnames
wrdata results/dram_3t_waveform.dat v(wl) v(rl) v(sn) v(bbl)
```

These commands assume the simulation is launched from the circuit repository root and that `results/` exists. If ngspice reports that it cannot open an output file, check the working directory and create the folder:

```bash
mkdir -p results
```

`wr_singlescale` writes the scale column once. The independent variable is normally the transient time scale, so the time variable does not need to be listed explicitly among the vectors in `wrdata`.

### 5.4 Fix 3T transistor instance names

The 3T netlist had transistor instance names beginning with `NM`, such as `NM0`, `NM1`, and `NM2`. These were changed to names beginning with `M`, such as `M0`, `M1`, and `M2`, to follow standard SPICE MOSFET instance naming.

### 5.5 Improve transient convergence for the 3T example

The 3T netlist needed a small capacitance at node `n1` and more tolerant transient solver settings. The following additions were used:

```spice
Cn1 n1 0 10f
.options method=gear reltol=0.003 abstol=1e-12 vntol=1e-6
.tran 0.5n 800n
```

These settings helped the transient simulation complete. They are numerical/convergence choices, not evidence of cryogenic device physics.

### 5.6 Generic transistor model and its limitation

The shared transistor include file uses a generic Level-1 NMOS model:

```spice
.model nmos nmos (level=1 vto=0.4 kp=120u gamma=0.4 lambda=0.04 phi=0.65 tox=4n)
```

This is a simplified generic model. It is **not** a cryogenic-calibrated MOSFET model, and the circuit simulations ran at approximately room temperature (27 °C in the logs).

### 5.7 Run the SPICE simulations

From the circuit repository root:

```bash
cd ~/CryoDRAM/1T-and-3T-DRAM-using-Cadence
mkdir -p results

ngspice -b spice/dram_1t.sp | tee results/dram_1t.log
ngspice -b spice/dram_3t.sp | tee results/dram_3t.log
```

Check that waveform files exist:

```bash
ls -lh results/
head results/dram_1t_waveform.dat
head results/dram_3t_waveform.dat
```

Observed successful run summaries during this project:

- 1T transient run: approximately 1,655 rows of output; reported stored-high node voltage about **4.051767 V** at approximately **700 ns** and stored-low near zero.
- 3T transient run: approximately 1,701 rows of output; reported stored node voltage about **4.099604 V** at approximately **605 ns**.

The exact rows and voltages depend on the current netlist, solver settings, and version. Treat these as outputs from the present circuit setup, not universal DRAM specifications.

### 5.8 Existing Python analysis script

The repository includes `analysis/dram_analysis.py`, which generates:

```text
results/dram_comparison.png
```

The script uses several hard-coded parameters, including:

```python
VDD = 5.0
W_ACCESS = 2e-6
L_ACCESS = 180e-9
CS_1T = 1e-12
V1_STORE_1T = 4.2
V0_STORE_1T = 0.9
BL_SWING_1T = 15e-3
CS_3T = 2e-15
V_STORE_3T = 4.69
I_LEAK = 1e-12
```

Consequently, its comparison plot is preliminary and partly assumption-driven. Unless the script is revised to parse simulation waveforms and clearly separate simulated values from assumptions, do not describe every plotted quantity as directly measured by ngspice.

Run it from the repository root with the virtual environment activated:

```bash
python analysis/dram_analysis.py
```

If the script needs to be included in a formal report, document its assumptions and verify that each plotted value has a clear source.

## 6. Build CryoModel's CACTI component

### 6.1 Move into the CACTI directory

```bash
cd ~/CryoDRAM/CryoModel/CryoMEM/cacti
```

The original build file specified a compiler path that was not present on this machine:

```text
/opt/gcc-9.2/bin/g++-9.2
```

The system compiler was used instead. A backup was made before changing the build file:

```bash
cp cacti.mk cacti.mk.backup
sed -i 's|^CXX = .*|CXX = g++ -m64|' cacti.mk
```

Then CACTI was compiled:

```bash
make -j2
```

The build completed successfully. Because the compiled CACTI executable is already available, avoid running `make clean` or deleting build products unless you intend to rebuild.

If a future clean build fails, check the compiler and dependency versions, inspect the build log, and restore or update the compiler setting only as needed.

## 7. Make CryoModel scripts compatible with the installed Python

The CryoModel checkout used `python3.8` in subprocess commands, but the available Ubuntu Python was 3.10.12. Backups were created and the subprocess references were changed to `python3`:

```bash
cd ~/CryoDRAM/CryoModel

cp CryoMEM/pgen.py CryoMEM/pgen.py.backup
cp CryoMOSFET/CryoMOSFET_77K/pgen.py \
   CryoMOSFET/CryoMOSFET_77K/pgen.py.backup
cp CryoMOSFET/CryoMOSFET_4K/pgen.py \
   CryoMOSFET/CryoMOSFET_4K/pgen.py.backup

sed -i 's/python3\.8/python3/g' \
   CryoMEM/pgen.py \
   CryoMOSFET/CryoMOSFET_77K/pgen.py \
   CryoMOSFET/CryoMOSFET_4K/pgen.py
```

Python syntax was checked:

```bash
cd ~/CryoDRAM/CryoModel/CryoMEM
python3 -m py_compile memory_model.py pgen.py
```

These are local compatibility changes to the cloned checkout. The backups allow comparison with the original repository versions.

## 8. Run the CryoMOSFET parameter generator

The CryoMOSFET model provides target-temperature transistor and wire parameters, along with a 300 K reference.

From the CryoModel root, run:

```bash
cd ~/CryoDRAM/CryoModel

python3 CryoMOSFET/CryoMOSFET_77K/pgen.py \
  --mosfet_mode 1 --temperature 77 --node 32 --vdd 1.2 --vth 0.4 \
  | tee /tmp/mosfet_77K.txt

python3 CryoMOSFET/CryoMOSFET_4K/pgen.py \
  --mosfet_mode 1 --temperature 4 --node 32 --vdd 1.2 --vth 0.4 \
  | tee /tmp/mosfet_4K.txt
```

Extract the important output lines:

```bash
grep -E 'running at|Vth0:|Vth_on:|Vth_off:|Ion:|Isub:|Igate:|Rwire:' \
  /tmp/mosfet_77K.txt /tmp/mosfet_4K.txt
```

### 8.1 Recorded MOSFET and wire outputs

| Parameter | 300 K reference printed by 77 K run | 77 K target | 300 K reference printed by 4 K run | 4 K target |
|---|---:|---:|---:|---:|
| NMOS Vth0 (V) | 0.493960 | 0.480000 | 0.493960 | 0.518519 |
| NMOS Vth_on (V) | 0.319979 | 0.242606 | 0.319979 | 0.351513 |
| NMOS Vth_off (V) | 0.360301 | 0.296909 | 0.360301 | 0.386330 |
| NMOS Ion (µA/µm) | 1668.144 | 3832.680 | 1668.144 | 3418.772 |
| NMOS Isub (µA/µm) | 0.045316 | 0.000000 | 0.045316 | 0.000000 |
| NMOS Igate (µA/µm) | 0.003035 | 0.007435 | 0.000265 | 0.001661 |
| PMOS Vth0 (V) | 0.491550 | 0.462000 | 0.491550 | 0.512037 |
| PMOS Vth_on (V) | 0.279274 | 0.172208 | 0.279274 | 0.312007 |
| PMOS Vth_off (V) | 0.335682 | 0.248242 | 0.335682 | 0.359936 |
| PMOS Ion (µA/µm) | 1233.393 | 2822.540 | 1233.393 | 2508.649 |
| PMOS Isub (µA/µm) | 0.011520 | 0.000001 | 0.011520 | 0.000000 |
| PMOS Igate (µA/µm) | 0.001453 | 0.003208 | 0.000000 | 0.000000 |
| Bulk wire Rwire (µΩ·cm as printed) | 1.772766788 | 0.219196256 | 1.767317200 | 0.203607972 |

**Important voltage caveat:** the reference runs use `Vdd = 0.9 V`; the target runs use `Vdd = 1.2 V`. The target drive-current outputs are therefore not a controlled temperature-only comparison. Do not attribute the full current difference to temperature alone.

The displayed zero values for leakage may reflect output precision or model behaviour. They are not proof that real leakage is physically zero.

## 9. Run CryoMEM for 77 K and 4 K

The memory configuration used is:

```text
CryoMEM/configs/DRAM.cfg
```

This configuration specifies a 32 nm technology node (`0.032` in the model configuration). The model commands used a 32 nm node.

Run from `CryoMEM` with the Python virtual environment active:

```bash
cd ~/CryoDRAM/CryoModel/CryoMEM

python3 memory_model.py ./configs/DRAM.cfg \
  77 32 1.2 0.4 262144 dram 1.2 0.4 \
  | tee results_77K.txt

python3 memory_model.py ./configs/DRAM.cfg \
  4 32 1.2 0.4 262144 dram 1.2 0.4 \
  | tee results_4K.txt
```

The parameter order follows the model's command-line interface in this checkout: configuration file, target temperature, technology node, supply/threshold and capacity-related arguments, memory type, and additional supply/threshold values. If the script's interface changes in a future version, consult its current help/source before reusing the command.

The saved outputs reported:
- Technology: 0.032 (32 nm)
- Memory type/configuration output: DDR4, UDIMM
- Capacity: 8 Gb, 16 banks
- CACTI banner: “3D DRAM Main Memory”

These printed labels describe the configuration/model path. They do not establish that a real UDIMM or 3D DRAM was physically tested.

### 9.1 Verify the saved outputs

```bash
grep -E \
'Temperature:|t_RCD|t_RAS|t_RC|t_CAS|t_RP|t_RRD|Activation energy|Read energy|Write energy|Precharge energy|Standby leakage|DRAM core area|DRAM area per die|Area efficiency' \
results_77K.txt results_4K.txt
```

The `Temperature:` string did not appear in the filtered lines from the saved outputs, so the temperature labels in this report are tied to the exact commands used to create each file.

## 10. CryoMEM results

### 10.1 Timing estimates

| Metric | 77 K | 4 K | Change at 4 K vs 77 K |
|---|---:|---:|---:|
| t_RCD (ns) | 3.53964 | 3.51226 | −0.77% |
| t_RAS (ns) | 5.64935 | 5.72901 | +1.41% |
| t_RC (ns) | 7.74234 | 7.84487 | +1.33% |
| t_CAS (ns) | 6.86159 | 7.06046 | +2.90% |
| t_RP (ns) | 2.09299 | 2.11585 | +1.09% |
| t_RRD (ns) | 1.66303 | 1.72080 | +3.48% |

The results are mixed: `t_RCD` is slightly lower in the 4 K run, while the other listed timing parameters are higher. This does not support a claim that every timing metric improves as temperature decreases.

### 10.2 Energy estimates

| Metric | 77 K | 4 K | Change at 4 K vs 77 K |
|---|---:|---:|---:|
| Activation energy (nJ) | 0.507796 | 0.514117 | +1.24% |
| Read energy (nJ) | 1.80089 | 1.83331 | +1.80% |
| Write energy (nJ) | 1.80094 | 1.83336 | +1.80% |
| Precharge energy (nJ) | 0.221989 | 0.221990 | approximately +0.0005% |

### 10.3 Standby leakage, area, and area efficiency

| Metric | 77 K | 4 K | Change at 4 K vs 77 K |
|---|---:|---:|---:|
| Standby leakage per bank (mW) | 2.33572 | 0.444796 | −80.95% |
| DRAM core area (mm²) | 134.000 | 135.945 | +1.45% |
| DRAM area per die (mm²) | 172.593 | 174.538 | +1.13% |
| Area efficiency (%) | 34.4009 | 34.0176 | −1.11% |

The reported area-per-bank output was printed with questionable units/magnitude in the original CACTI output. Do not use that field as a validated physical area figure without checking the implementation and units.

### 10.4 Interpretation

Within this particular model configuration:
- The most dramatic difference is the reduction in estimated standby leakage per bank at 4 K relative to 77 K.
- Read and write energy are slightly higher at 4 K.
- Timing changes are small but mixed, with no universal improvement across all parameters.
- The transistor generator predicts higher target drive currents than its 300 K references, but the supply-voltage difference confounds the comparison.
- Lower wire-resistivity values are reported by the target-temperature generator, but they remain model outputs rather than physical measurements.

## 11. Model limitations and how to describe them in the report

These caveats are essential, not optional fine print.

1. **No physical cryogenic DIMM was tested.** The DRAM results are outputs from a software model.
2. **CryoModel is a research model whose release/validation status is still in progress.** Treat the outputs as comparative estimates.
3. **CACTI's own temperature handling remains at 300 K in this code path.** CryoMEM passes temperature-dependent transistor and wire parameters into CACTI, but that does not make every CACTI calculation fully temperature-aware.
4. **The MOSFET reference and target supply voltages differ.** The reference is 0.9 V and target runs are 1.2 V. Current ratios cannot be interpreted as temperature-only effects.
5. **The 1T/3T SPICE demo is separate from CryoModel.** It uses a generic Level-1 MOSFET model at room temperature. It demonstrates circuit behaviour, not cryogenic operation.
6. **Absolute predictions need caution.** Prefer relative comparisons under clearly stated assumptions, as recommended by the CryoModel project documentation.
7. **Do not claim that a standard DIMM can simply be cooled to 4 K and operate normally.** Cryogenic memory operation raises device, packaging, interface, thermal-budget, and system-integration issues beyond these model outputs.

### Suggested report wording

> The CryoMEM model estimates a substantial reduction in standby leakage per bank in the 4 K configuration compared with the 77 K configuration, while active energy and timing metrics exhibit small mixed changes. The CryoMOSFET generator also reports temperature-dependent changes in transistor and wire parameters. These results are comparative model outputs rather than experimental DIMM measurements. Interpretation is limited by the model's temperature-handling path and by the use of different supply voltages for target and reference transistor runs.

## 12. Useful commands for future sessions

### Activate the Python environment

```bash
source ~/CryoDRAM/1T-and-3T-DRAM-using-Cadence/.venv/bin/activate
```

### Check repository status

```bash
cd ~/CryoDRAM/CryoModel
git status --short

cd ~/CryoDRAM/1T-and-3T-DRAM-using-Cadence
git status --short
```

### Rerun CryoMOSFET parameter generators

```bash
cd ~/CryoDRAM/CryoModel

python3 CryoMOSFET/CryoMOSFET_77K/pgen.py \
  --mosfet_mode 1 --temperature 77 --node 32 --vdd 1.2 --vth 0.4 \
  | tee /tmp/mosfet_77K.txt

python3 CryoMOSFET/CryoMOSFET_4K/pgen.py \
  --mosfet_mode 1 --temperature 4 --node 32 --vdd 1.2 --vth 0.4 \
  | tee /tmp/mosfet_4K.txt
```

### Rerun CryoMEM

```bash
cd ~/CryoDRAM/CryoModel/CryoMEM

python3 memory_model.py ./configs/DRAM.cfg \
  77 32 1.2 0.4 262144 dram 1.2 0.4 \
  | tee results_77K.txt

python3 memory_model.py ./configs/DRAM.cfg \
  4 32 1.2 0.4 262144 dram 1.2 0.4 \
  | tee results_4K.txt
```

### Rerun SPICE circuits

```bash
cd ~/CryoDRAM/1T-and-3T-DRAM-using-Cadence

ngspice -b spice/dram_1t.sp | tee results/dram_1t.log
ngspice -b spice/dram_3t.sp | tee results/dram_3t.log
```

### Check generated files

```bash
find ~/CryoDRAM -maxdepth 4 -type f \
  \( -name 'results_77K.txt' -o -name 'results_4K.txt' \
     -o -name 'dram_1t_waveform.dat' -o -name 'dram_3t_waveform.dat' \) \
  -print
```

## 13. Repository references

- CryoModel repository: https://github.com/SNU-HPCS/CryoModel
- 1T/3T DRAM SPICE repository: https://github.com/srivastavadi/1T-and-3T-DRAM-using-Cadence
- WSL installation documentation: https://learn.microsoft.com/windows/wsl/install
- ngspice documentation: https://ngspice.sourceforge.io/docs.html

The repository READMEs and scripts should be checked again if the project is rerun against a newer revision. This document records the setup and outputs observed during the current project work, not a guarantee that future repository versions will behave identically.

---

## 14. Current status and remaining work

### Completed
- [x] Installed Ubuntu 22.04 under WSL 2.
- [x] Installed Linux build tools, Python, ngspice, Protocol Buffers, and Boost.
- [x] Created a Python virtual environment and installed dependencies.
- [x] Cloned CryoModel and the 1T/3T circuit repository.
- [x] Built CACTI with the system C++ compiler.
- [x] Applied local Python compatibility edits for `python3`.
- [x] Ran CryoMOSFET generators for 77 K and 4 K.
- [x] Ran CryoMEM for 77 K and 4 K and saved output files.
- [x] Ran the 1T and 3T ngspice demonstrations and saved waveform data.

### Remaining before final submission
- [ ] Inspect and validate the exported SPICE waveforms and the existing Python analysis script.
- [ ] Regenerate final graphs in a form that opens reliably on the user's computer.
- [ ] Prepare the final report with methodology, figures, results, limitations, and references.
- [ ] Prepare a presentation and viva questions/answers.
- [ ] Verify all screenshots, plots, paths, and claims before submission.

**End of setup and results record.**
