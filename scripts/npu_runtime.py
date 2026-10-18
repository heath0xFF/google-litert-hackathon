"""Shared helpers for the NPU examples (Ventuno Q, Qualcomm QCS8275). Not an example itself.

The LiteRT calls you should read live in each example's main.py. This file holds the plumbing around them:
where setup_npu.py put the libraries, the environment those libraries need, and a check that the NPU
was really used. Run `python3 scripts/setup_npu.py` once before using it.
"""
import ctypes
import importlib
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
QNN_LIB = ROOT / "npu" / "lib"             # Qualcomm libraries + LiteRT's Qualcomm dispatch library + libatomic
LITERTLM_LIB = ROOT / "npu" / "litertlm"   # LiteRT-LM runtime built with the NPU settings enabled on Linux
_ALREADY_SET = "LITERT_HACKATHON_NPU_ENV"


def ensure_env():
    """Restart this program once with the environment the Qualcomm libraries need.

    Linux reads LD_LIBRARY_PATH only when a program starts, so it cannot be changed from inside Python.
    This restarts the same command with it set; a marker variable stops the restart from repeating.
    """
    if not (QNN_LIB / "libQnnHtp.so").is_file():
        raise SystemExit("NPU libraries not found. Run once: python3 scripts/setup_npu.py")
    if os.environ.get(_ALREADY_SET) == "1":
        return
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = os.pathsep.join(filter(None, [str(QNN_LIB), env.get("LD_LIBRARY_PATH")]))
    env["ADSP_LIBRARY_PATH"] = str(QNN_LIB)  # where the NPU-side (Hexagon) library is found
    env[_ALREADY_SET] = "1"
    os.execve(sys.executable, [sys.executable, *sys.orig_argv[1:]], env)


def use_bundled_litertlm():
    """Make the litert-lm-api Python package load our LiteRT-LM C library instead of its own.

    The pip package ships a LiteRT-LM library that leaves the NPU in its default power mode on Linux
    (about 3x slower here). The library from setup_npu.py sets the high-performance mode. This swap relies
    on the package's internals, which is why requirements.txt pins an exact litert-lm-api version.
    """
    ffi = importlib.import_module("litert_lm._ffi")
    bundled = str(LITERTLM_LIB / "libLiteRtLm.so")
    real_cdll = ctypes.CDLL

    def cdll(path, *args, **kwargs):
        return real_cdll(bundled if str(path).endswith("liblitert-lm.so") else path, *args, **kwargs)

    ctypes.CDLL = cdll
    try:
        ffi._get_lib()
    finally:
        ctypes.CDLL = real_cdll
    if not str(getattr(ffi._LIB, "_name", "")).endswith("libLiteRtLm.so"):
        raise RuntimeError("Could not switch litert-lm-api to the NPU runtime library; is litert-lm-api 0.18.0 installed?")


def redirect_native_logs():
    """Send the NPU libraries' very chatty output to npu/last-run.log, keeping the terminal readable.

    The native libraries print hundreds of lines (mostly harmless shutdown messages) straight to the
    process's output. Python's own output keeps going to the terminal. If the run fails, the end of the
    log is shown. Call this once, after ensure_env() and before loading any LiteRT library.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    terminal_out, terminal_err = os.dup(1), os.dup(2)
    log_path = ROOT / "npu" / "last-run.log"
    log_fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.dup2(log_fd, 1)
    os.dup2(log_fd, 2)
    os.close(log_fd)
    sys.stdout = os.fdopen(terminal_out, "w", buffering=1)
    sys.stderr = os.fdopen(terminal_err, "w", buffering=1)

    def show_log_then_report(kind, value, traceback):
        print(f"--- last lines of {log_path.relative_to(ROOT)} ---", file=sys.stderr)
        print("\n".join(log_path.read_text(errors="replace").splitlines()[-25:]), file=sys.stderr)
        sys.__excepthook__(kind, value, traceback)

    sys.excepthook = show_log_then_report
    return log_path


def fail(message):
    """Exit with an error message, showing the end of the native log first."""
    log_path = ROOT / "npu" / "last-run.log"
    if log_path.exists():
        print(f"--- last lines of {log_path.relative_to(ROOT)} ---", file=sys.stderr)
        print("\n".join(log_path.read_text(errors="replace").splitlines()[-25:]), file=sys.stderr)
    raise SystemExit(message)


def cdsp_interrupts():
    """Interrupts received from the NPU's processor (cDSP), or None if this kernel names them differently."""
    with open("/proc/interrupts") as table:
        cpus = len(table.readline().split())
        for line in table:
            if "ipcc 393216" in line:  # inter-processor channel of the cDSP on this SoC
                return sum(int(count) for count in line.split()[1:1 + cpus])
    return None


def check_npu_used(interrupts_before, interrupts_after):
    """Return (ok, message). Look for traces of NPU use in this process; a model that loaded is not proof."""
    maps = Path("/proc/self/maps").read_text()
    htp_loaded = "libQnnHtp.so" in maps
    channel_open = any("fastrpc" in os.readlink(f"/proc/self/fd/{fd}") for fd in os.listdir("/proc/self/fd")
                       if os.path.islink(f"/proc/self/fd/{fd}"))
    notes = [f"Qualcomm NPU library loaded: {htp_loaded}", f"NPU channel open: {channel_open}"]
    ok = htp_loaded and channel_open
    if interrupts_before is not None and interrupts_after is not None:
        delta = interrupts_after - interrupts_before
        notes.append(f"NPU interrupts during the run: +{delta}")
        ok = ok and delta > 0
    else:
        notes.append("NPU interrupt counter unavailable on this kernel")
    return ok, "NPU evidence: " + "; ".join(notes)
