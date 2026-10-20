# Troubleshooting & FAQ Guide

This document catalogs known issues, error signatures, and exact solutions encountered during environment setup and execution.

---

## 1. Missing System Dependencies / Tools

### Issue: `ngspice: command not found`
- **Cause**: ngspice is not installed on the Linux system / WSL environment.
- **Solution**:
  ```bash
  sudo apt-get update && sudo apt-get install -y ngspice
  ```

### Issue: `g++: command not found` or `make: command not found`
- **Cause**: Standard build tools missing.
- **Solution**:
  ```bash
  sudo apt-get update && sudo apt-get install -y build-essential g++ make
  ```

---

## 2. Python & Protobuf Version Mismatch

### Issue: `TypeError: Descriptors cannot not be created directly`
- **Cause**: CryoModel uses Protocol Buffers files generated with an older `protoc` compiler. Modern `protobuf>=4.x` rejects these descriptors.
- **Solution**:
  Pin protobuf to version `3.20.3`:
  ```bash
  pip install "protobuf==3.20.3"
  ```
  Or set environment fallback:
  ```bash
  export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
  ```

### Issue: `ModuleNotFoundError: No module named 'numpy'`
- **Cause**: Python script executed outside the active virtual environment.
- **Solution**:
  ```bash
  source .venv/bin/activate
  ```

---

## 3. CACTI Build Failures

### Issue: `/opt/gcc-9.2/bin/g++-9.2: No such file or directory`
- **Cause**: The original CACTI Makefile referenced a custom hardcoded compiler path.
- **Solution**:
  The Makefile has been patched in this repository. If rebuilding manually:
  ```bash
  cd CryoModel/CryoMEM/cacti
  make clean
  make
  ```
  Ensure `libboost-all-dev` and `libprotobuf-dev` are installed:
  ```bash
  sudo apt-get install -y libboost-all-dev libprotobuf-dev protobuf-compiler
  ```

---

## 4. SPICE Simulation Issues

### Issue: `ngspice -b` returns exit code 1 despite simulation completing
- **Cause**: ngspice `.control` blocks without an explicit `quit 0` statement exit with code 1 in batch mode.
- **Solution**:
  Ensure `.control` scripts in `spice/*.sp` end with:
  ```spice
  quit 0
  .endc
  ```

### Issue: Solver non-convergence in 3T DRAM simulation
- **Cause**: Floating internal node `n1` or numerical oscillations during sharp pulse transitions.
- **Solution**:
  The netlist `spice/dram_3t.sp` includes a stabilizing node capacitance (`Cn1 n1 0 10f`) and uses the Gear integration algorithm:
  ```spice
  .options method=gear reltol=0.003 abstol=1e-12 vntol=1e-6
  ```

---

## 5. File Permissions & Line Endings

### Issue: `/bin/bash^M: bad interpreter: No such file or directory`
- **Cause**: Windows CRLF line endings in shell scripts.
- **Solution**:
  Convert line endings to Unix LF:
  ```bash
  dos2unix scripts/*.sh
  # or via sed:
  sed -i 's/\r$//' scripts/*.sh
  ```
  Repository line endings are enforced via [.gitattributes](file:///e:/CryoDRAM/.gitattributes).

### Issue: `Permission denied` when running scripts
- **Solution**:
  ```bash
  chmod +x scripts/*.sh
  ```

---

## 6. Headless Linux / WSL Display Errors

### Issue: `UserWarning: Matplotlib is currently using agg, which is a non-GUI backend`
- **Explanation**: This is expected and intended. All CryoDRAM plotting scripts explicitly use `matplotlib.use("Agg")` so figures render cleanly in headless WSL and automated CI environments without requiring an X server or GUI display.
