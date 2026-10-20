#!/usr/bin/env bash
# =============================================================================
# CryoDRAM Environment Setup Script
# Works on Windows 11 with WSL 2 (Ubuntu 22.04) and native Ubuntu 22.04 LTS.
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "============================================================"
echo " CryoDRAM Research Environment Setup"
echo " Target Root: ${REPO_ROOT}"
echo "============================================================"

# 1. Check system utilities
echo "[*] Checking system dependencies..."
MISSING_PKGS=()

for cmd in python3 g++ make ngspice; do
    if ! command -v "$cmd" &> /dev/null; then
        MISSING_PKGS+=("$cmd")
    fi
done

if [ ${#MISSING_PKGS[@]} -ne 0 ]; then
    echo "[!] Warning: The following system tools are missing: ${MISSING_PKGS[*]}"
    echo "    On Ubuntu/Debian/WSL 2, install them using:"
    echo "    sudo apt-get update && sudo apt-get install -y build-essential g++ make ngspice python3-pip python3-venv libboost-all-dev libprotobuf-dev protobuf-compiler"
fi

# 2. Setup Python virtual environment
VENV_DIR="${REPO_ROOT}/.venv"
if [ ! -d "${VENV_DIR}" ]; then
    echo "[*] Creating virtual environment at ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
fi

# Activate venv
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "[*] Upgrading pip and installing Python requirements..."
pip install --upgrade pip
pip install -r "${REPO_ROOT}/requirements.txt"

# 3. Build CACTI memory model if binary missing
CACTI_DIR="${REPO_ROOT}/CryoModel/CryoMEM/cacti"
if [ ! -f "${CACTI_DIR}/cacti" ]; then
    echo "[*] Building CACTI engine at ${CACTI_DIR}..."
    make -C "${CACTI_DIR}"
fi

echo "============================================================"
echo "[+] Setup completed successfully!"
echo "To activate your environment in this shell, run:"
echo "    source .venv/bin/activate"
echo "Then verify the pipeline with:"
echo "    make check"
echo "    make all"
echo "============================================================"
