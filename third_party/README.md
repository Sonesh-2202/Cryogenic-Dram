# Third-Party Upstream Dependencies & Citations

This directory documents the external research projects referenced and utilized within this project.

---

## 1. CryoModel
- **Source**: [https://github.com/SNU-HPCS/CryoModel](https://github.com/SNU-HPCS/CryoModel)
- **Developed by**: HPCS Lab, Seoul National University (SNU)
- **License**: MIT License (see `CryoModel/LICENSE`)
- **Key References**:
  - ISCA '19: *Cryogenic computer architecture modeling with memory-side case studies* (CryoRAM)
  - ASPLOS '20: *CryoCache: A Fast, Large, and Cost-Effective Cache Architecture for Cryogenic Computing*
  - ISCA '20: *CryoCore: A Fast and Dense Processor Architecture for Cryogenic Computing*
  - ASPLOS '22: *CryoWire: Wire-driven microarchitecture designs for cryogenic computing*
  - ISCA '22: *XQsim: Modeling cross-technology control processors for 10+ K qubit quantum computers*
- **Local Patches Applied for Modern Linux / Ubuntu 22.04 Compatibility**:
  - `CryoModel/CryoMEM/cacti/cacti.mk`: Swapped unavailable `/opt/gcc-9.2/bin/g++-9.2` for standard system `g++ -m64` and `gcc -m64`.
  - Python scripts (`pgen.py`, `memory_model.py`): Replaced hardcoded `python3.8` invocations with standard `python3` / `sys.executable` discovery.
  - Protobuf compatibility: Requires `protobuf==3.20.3` to match generated Python bindings (`_pb2.py`).

---

## 2. 1T & 3T DRAM Cell Design (Cadence Virtuoso / SPICE)
- **Source**: [https://github.com/srivastavadi/1T-and-3T-DRAM-using-Cadence](https://github.com/srivastavadi/1T-and-3T-DRAM-using-Cadence)
- **Author**: Divyanshu Srivastava
- **Role**: Provides the schematic references, transient Spectre waveforms, and portable ngspice netlist decks for 1T-1C and 3T DRAM cells.
- **Local Patches Applied for Batch Automation**:
  - Added clean exit directives (`quit 0`) to `.control` blocks in SPICE decks so `ngspice -b` completes with return code 0.
  - Added stabilizing capacitance and transient solver gear options in `spice/dram_3t.sp`.
