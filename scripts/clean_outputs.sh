#!/usr/bin/env bash
# =============================================================================
# CryoDRAM Safe Output Cleanup Script
# Removes only known generated files in results/ without touching code or docs.
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RESULTS_DIR="${REPO_ROOT}/results"

echo "============================================================"
echo " Cleaning Generated Results"
echo " Target: ${RESULTS_DIR}"
echo "============================================================"

# List of known generated patterns
rm -f "${RESULTS_DIR}"/*.dat
rm -f "${RESULTS_DIR}"/*.log
rm -f "${RESULTS_DIR}"/mosfet_*.txt
rm -f "${RESULTS_DIR}"/cryomem_*.txt
rm -f "${RESULTS_DIR}"/comparison.csv
rm -f "${RESULTS_DIR}"/summary.json
rm -f "${RESULTS_DIR}"/*.png

echo "[+] Cleaned generated simulation outputs and plots."
echo "    Preserved: ${RESULTS_DIR}/README.md, ${RESULTS_DIR}/.gitkeep"
