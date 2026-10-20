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

# 1. Check system utilities and libraries
echo "[*] Checking system dependencies..."
NEED_INSTALL=false

for cmd in python3 g++ make ngspice; do
    if ! command -v "$cmd" &> /dev/null; then
        NEED_INSTALL=true
        break
    fi
done

# Also check for python3-venv and dev libraries if on Debian/Ubuntu
if command -v dpkg-query &> /dev/null; then
    for pkg in python3-venv libboost-all-dev libprotobuf-dev; do
        if ! dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q "ok installed"; then
            NEED_INSTALL=true
            break
        fi
    done
fi

if [ "$NEED_INSTALL" = true ]; then
    echo "[!] System dependencies missing. Installing via apt-get (requires sudo)..."
    if command -v sudo &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y \
            build-essential g++ make ngspice python3-pip python3-venv \
            libboost-all-dev libprotobuf-dev protobuf-compiler
    else
        echo "[!] 'sudo' not available. Please install the following packages manually:"
        echo "    build-essential g++ make ngspice python3-pip python3-venv libboost-all-dev libprotobuf-dev protobuf-compiler"
        exit 1
    fi
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
