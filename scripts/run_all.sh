#!/usr/bin/env bash
# =============================================================================
# CryoDRAM Full Reproduction Runner
# Executes CryoMOSFET, CryoMEM, ngspice, analysis, and plot generation.
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Activate local venv if exists
if [ -d "${REPO_ROOT}/.venv" ]; then
    # shellcheck disable=SC1091
    source "${REPO_ROOT}/.venv/bin/activate"
elif [ -d "/home/${USER}/CryoDRAM/1T-and-3T-DRAM-using-Cadence/.venv" ]; then
    # shellcheck disable=SC1091
    source "/home/${USER}/CryoDRAM/1T-and-3T-DRAM-using-Cadence/.venv/bin/activate"
fi

export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH}"

echo "============================================================"
echo " Starting Full CryoDRAM Reproduction Pipeline"
echo " Working Directory: ${REPO_ROOT}"
echo " Python: $(which python3)"
echo "============================================================"

# Step 1: Run Simulation & Model Generation
python3 "${REPO_ROOT}/src/cryodram/run_models.py"

# Step 2: Quantitative Analysis & Data Export
python3 "${REPO_ROOT}/src/cryodram/analyze_results.py"

# Step 3: Publication-Quality Plot Generation
python3 "${REPO_ROOT}/src/cryodram/plot_results.py"

echo "============================================================"
echo "[+] Full CryoDRAM pipeline completed successfully!"
echo "Outputs generated under: ${REPO_ROOT}/results/"
echo "============================================================"
