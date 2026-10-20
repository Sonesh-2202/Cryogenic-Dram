# =============================================================================
# CryoDRAM Research Framework Makefile
# =============================================================================

SHELL := /bin/bash
PYTHON ?= $(shell which python3 2>/dev/null || echo python3)
export PYTHONPATH := src:$(PYTHONPATH)

.PHONY: help setup check run-mosfet run-cryo-mem run-spice analyze plot all test clean

help:
	@echo "========================================================================"
	@echo " CryoDRAM Research Framework - Available Targets"
	@echo "========================================================================"
	@echo "  make setup        : Configure virtual environment & install dependencies"
	@echo "  make check        : Verify environment tools, libraries, and binaries"
	@echo "  make run-mosfet   : Run 77 K and 4 K CryoMOSFET device parameter generator"
	@echo "  make run-cryo-mem : Run 77 K and 4 K CryoMEM 32nm DRAM array model (CACTI)"
	@echo "  make run-spice    : Run 1T-1C and 3T DRAM transient SPICE simulations"
	@echo "  make analyze      : Parse actual simulation outputs, generate CSV & JSON"
	@echo "  make plot         : Render publication-quality comparison charts"
	@echo "  make all          : Execute full end-to-end simulation & analysis pipeline"
	@echo "  make test         : Run automated pytest test suite"
	@echo "  make clean        : Safely remove generated output files from results/"
	@echo "========================================================================"

setup:
	@bash scripts/setup.sh

check:
	@echo "[*] Checking environment dependencies..."
	@command -v $(PYTHON) >/dev/null 2>&1 || (echo "[!] Error: python3 not found"; exit 1)
	@command -v ngspice >/dev/null 2>&1 || (echo "[!] Error: ngspice not found. Install via 'sudo apt-get install ngspice'"; exit 1)
	@command -v g++ >/dev/null 2>&1 || (echo "[!] Error: g++ not found. Install via 'sudo apt-get install build-essential'"; exit 1)
	@command -v make >/dev/null 2>&1 || (echo "[!] Error: make not found"; exit 1)
	@$(PYTHON) -c "import google.protobuf; assert google.protobuf.__version__.startswith('3.20'), 'Protobuf 3.20.x required'" 2>/dev/null || (echo "[!] Warning: protobuf==3.20.3 not detected in active python environment"; true)
	@test -f CryoModel/CryoMEM/cacti/cacti || (echo "[*] CACTI binary missing. Building..."; make -C CryoModel/CryoMEM/cacti)
	@echo "[+] Environment check passed!"

run-mosfet:
	@mkdir -p results
	@$(PYTHON) CryoModel/CryoMOSFET/CryoMOSFET_77K/pgen.py --mosfet_mode 1 --temperature 77 --node 32 --vdd 1.2 --vth 0.4 --wire_mode 1 > results/mosfet_77K.txt
	@$(PYTHON) CryoModel/CryoMOSFET/CryoMOSFET_4K/pgen.py --mosfet_mode 1 --temperature 4 --node 32 --vdd 1.2 --vth 0.4 --wire_mode 1 > results/mosfet_4K.txt
	@echo "[+] CryoMOSFET outputs saved to results/mosfet_77K.txt and results/mosfet_4K.txt"

run-cryo-mem:
	@mkdir -p results
	@test -f CryoModel/CryoMEM/cacti/cacti || make -C CryoModel/CryoMEM/cacti
	@$(PYTHON) CryoModel/CryoMEM/memory_model.py configs/DRAM.cfg 77 32 1.2 0.4 262144 dram 1.2 0.4 > results/cryomem_77K.txt
	@$(PYTHON) CryoModel/CryoMEM/memory_model.py configs/DRAM.cfg 4 32 1.2 0.4 262144 dram 1.2 0.4 > results/cryomem_4K.txt
	@echo "[+] CryoMEM outputs saved to results/cryomem_77K.txt and results/cryomem_4K.txt"

run-spice:
	@mkdir -p results
	@ngspice -b spice/dram_1t.sp > results/dram_1t.log
	@ngspice -b spice/dram_3t.sp > results/dram_3t.log
	@echo "[+] SPICE simulations completed (waveforms in results/)"

analyze:
	@$(PYTHON) src/cryodram/analyze_results.py

plot:
	@$(PYTHON) src/cryodram/plot_results.py

all: check run-mosfet run-cryo-mem run-spice analyze plot
	@echo "========================================================================"
	@echo "[+] Full reproduction workflow completed successfully!"
	@echo "========================================================================"

test:
	@PYTHONPATH=src $(PYTHON) -m pytest -v

clean:
	@bash scripts/clean_outputs.sh
