#!/usr/bin/env python3
"""Model and Simulation Runner for CryoDRAM.

Orchestrates execution of:
1. CryoMOSFET parameter generation at 77 K and 4 K
2. CryoMEM 32 nm DRAM modeling at 77 K and 4 K (via CACTI)
3. 1T and 3T DRAM transient simulations (via ngspice)

All outputs are saved to the results/ directory.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def get_repo_root() -> Path:
    """Return the absolute path to the repository root directory."""
    return Path(__file__).resolve().parent.parent.parent


def check_tool(tool_name: str) -> bool:
    """Check if a CLI tool is available in PATH."""
    return shutil.which(tool_name) is not None


def run_command(cmd, cwd=None, output_file=None, env=None) -> int:
    """Run a command, streaming or writing output to a file, returning exit code."""
    cmd_str = " ".join(str(c) for c in cmd)
    print(f"[*] Running: {cmd_str}")
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            env=merged_env,
            check=False
        )
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(proc.stdout)
                if proc.stderr:
                    f.write("\n--- STDERR ---\n")
                    f.write(proc.stderr)
        if proc.returncode != 0:
            print(f"[!] Error (exit {proc.returncode}) executing: {cmd_str}")
            if proc.stderr:
                print(f"    {proc.stderr.strip()[:300]}")
        return proc.returncode
    except Exception as e:
        print(f"[!] Exception running {cmd_str}: {e}")
        return 1


def run_cryo_mosfet(repo_root: Path, results_dir: Path) -> bool:
    """Run CryoMOSFET parameter generator for 77 K and 4 K."""
    print("\n=== [1/3] Running CryoMOSFET Transistor & Wire Generator ===")
    pgen_77k = repo_root / "CryoModel" / "CryoMOSFET" / "CryoMOSFET_77K" / "pgen.py"
    pgen_4k = repo_root / "CryoModel" / "CryoMOSFET" / "CryoMOSFET_4K" / "pgen.py"

    if not pgen_77k.is_file() or not pgen_4k.is_file():
        print(f"[!] CryoMOSFET script not found under {repo_root / 'CryoModel' / 'CryoMOSFET'}")
        return False

    # 77 K Run: HP transistor (mode 1), T=77K, 32nm node, Vdd=1.2V, Vth=0.4V, Bulk wire (mode 1)
    cmd_77k = [
        sys.executable, str(pgen_77k),
        "--mosfet_mode", "1",
        "--temperature", "77",
        "--node", "32",
        "--vdd", "1.2",
        "--vth", "0.4",
        "--wire_mode", "1"
    ]
    code_77k = run_command(
        cmd_77k,
        cwd=pgen_77k.parent,
        output_file=results_dir / "mosfet_77K.txt"
    )

    # 4 K Run: HP transistor (mode 1), T=4K, 32nm node, Vdd=1.2V, Vth=0.4V, Bulk wire (mode 1)
    cmd_4k = [
        sys.executable, str(pgen_4k),
        "--mosfet_mode", "1",
        "--temperature", "4",
        "--node", "32",
        "--vdd", "1.2",
        "--vth", "0.4",
        "--wire_mode", "1"
    ]
    code_4k = run_command(
        cmd_4k,
        cwd=pgen_4k.parent,
        output_file=results_dir / "mosfet_4K.txt"
    )

    success = (code_77k == 0 and code_4k == 0)
    print(f"[{'+' if success else '!'}] CryoMOSFET runs: {'PASSED' if success else 'FAILED'}")
    return success


def run_cryo_mem(repo_root: Path, results_dir: Path) -> bool:
    """Run CryoMEM DRAM model for 77 K and 4 K configurations."""
    print("\n=== [2/3] Running CryoMEM Memory Array Model (CACTI) ===")
    mem_model = repo_root / "CryoModel" / "CryoMEM" / "memory_model.py"
    cacti_bin = repo_root / "CryoModel" / "CryoMEM" / "cacti" / "cacti"
    dram_cfg = repo_root / "configs" / "DRAM.cfg"

    if not mem_model.is_file():
        print(f"[!] memory_model.py not found at {mem_model}")
        return False

    if not cacti_bin.is_file():
        print(f"[*] Compiling CACTI engine at {cacti_bin.parent}...")
        make_code = run_command(["make", "-C", str(cacti_bin.parent)])
        if make_code != 0 or not cacti_bin.is_file():
            print(f"[!] Failed to compile CACTI binary. Ensure g++, make, boost, and protobuf-dev are installed.")
            return False

    # Target arguments: config, temp, node (nm), vdd, vth, capacity (Bytes), cell_type, acc_vdd, acc_vth
    # 262144 Bytes = 256 KB subarray / bank block
    cmd_77k = [
        sys.executable, str(mem_model),
        str(dram_cfg),
        "77", "32", "1.2", "0.4", "262144", "dram", "1.2", "0.4"
    ]
    code_77k = run_command(
        cmd_77k,
        cwd=mem_model.parent,
        output_file=results_dir / "cryomem_77K.txt"
    )

    cmd_4k = [
        sys.executable, str(mem_model),
        str(dram_cfg),
        "4", "32", "1.2", "0.4", "262144", "dram", "1.2", "0.4"
    ]
    code_4k = run_command(
        cmd_4k,
        cwd=mem_model.parent,
        output_file=results_dir / "cryomem_4K.txt"
    )

    success = (code_77k == 0 and code_4k == 0)
    print(f"[{'+' if success else '!'}] CryoMEM runs: {'PASSED' if success else 'FAILED'}")
    return success


def run_spice_simulations(repo_root: Path, results_dir: Path) -> bool:
    """Run 1T-1C and 3T DRAM SPICE simulations using ngspice."""
    print("\n=== [3/3] Running 1T and 3T DRAM SPICE Simulations ===")
    if not check_tool("ngspice"):
        print("[!] ngspice executable not found in PATH.")
        print("    Install via: sudo apt-get install -y ngspice")
        return False

    sp_1t = repo_root / "spice" / "dram_1t.sp"
    sp_3t = repo_root / "spice" / "dram_3t.sp"

    if not sp_1t.is_file() or not sp_3t.is_file():
        print(f"[!] SPICE decks not found in {repo_root / 'spice'}")
        return False

    code_1t = run_command(
        ["ngspice", "-b", str(sp_1t.relative_to(repo_root))],
        cwd=repo_root,
        output_file=results_dir / "dram_1t.log"
    )

    code_3t = run_command(
        ["ngspice", "-b", str(sp_3t.relative_to(repo_root))],
        cwd=repo_root,
        output_file=results_dir / "dram_3t.log"
    )

    dat_1t = results_dir / "dram_1t_waveform.dat"
    dat_3t = results_dir / "dram_3t_waveform.dat"

    success = (code_1t == 0 and code_3t == 0 and dat_1t.is_file() and dat_3t.is_file())
    if success:
        print(f"[+] SPICE simulations: PASSED (Waveforms generated in {results_dir})")
    else:
        print(f"[!] SPICE simulations: FAILED (Exit codes: 1T={code_1t}, 3T={code_3t})")
    return success


def main():
    root = get_repo_root()
    results = root / "results"
    results.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CryoDRAM Simulation & Modeling Workflow")
    print(f"Root: {root}")
    print(f"Results: {results}")
    print("=" * 60)

    s1 = run_cryo_mosfet(root, results)
    s2 = run_cryo_mem(root, results)
    s3 = run_spice_simulations(root, results)

    print("\n" + "=" * 60)
    print("Execution Summary:")
    print(f"  - CryoMOSFET (77K, 4K):   {'OK' if s1 else 'FAILED'}")
    print(f"  - CryoMEM (77K, 4K):      {'OK' if s2 else 'FAILED'}")
    print(f"  - SPICE 1T & 3T DRAM:     {'OK' if s3 else 'FAILED'}")
    print("=" * 60)

    if not (s1 and s2 and s3):
        sys.exit(1)
    print("[+] All simulations completed successfully.")


if __name__ == "__main__":
    main()
