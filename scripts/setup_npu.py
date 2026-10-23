"""Fetch what the NPU examples need into ./npu (Ventuno Q / Qualcomm QCS8275). Run once on the board.

Nothing here needs sudo. Qualcomm and LiteRT downloads are pinned and SHA-256 verified; libatomic comes
from the board or its configured apt repositories. Qualcomm's libraries are fetched from Qualcomm at setup
time and are not redistributed by this repository.
"""
import argparse
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import time
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "npu" / "lib"
LITERTLM = ROOT / "npu" / "litertlm"

# Qualcomm AI Runtime (QAIRT) community SDK. The zip is 2.6 GB, so read only the members we need.
QAIRT_URL = ("https://softwarecenter.qualcomm.com/api/download/software/sdks/"
             "Qualcomm_AI_Runtime_Community/All/2.50.0.260828/v2.50.0.260828.zip")
QAIRT_SIZE = 2601473189
QAIRT_ROOT = "qairt/2.50.0.260828/lib/"
QAIRT_FILES = {  # file name -> (folder inside the zip, SHA-256)
    "libQnnTFLiteDelegate.so": ("aarch64-oe-linux-gcc11.2/", "88d5ec6b722d21fc165a4519aa772822ab1b4e3a8548c3ed51046e2821aa9047"),
    "libQnnHtpPrepare.so": ("aarch64-oe-linux-gcc11.2/", "7c9a8a59ce090bb0766f5ff660809ef58e0a5e65d1c6ba46c7fa182f8d032682"),
    "libQnnHtp.so": ("aarch64-oe-linux-gcc11.2/", "823f764d434869919c7e01825ba76da7db828225525b0d27a4c21f4b2841e25b"),
    "libQnnSystem.so": ("aarch64-oe-linux-gcc11.2/", "65c1faa1c2175128fd3c3c8a8edb276e93520666afd9696977e947e6d7a3d1d2"),
    "libQnnHtpV75Stub.so": ("aarch64-oe-linux-gcc11.2/", "c9ca7044e946248ce8bbac85c54f720e9d732793fada9160ef82d037629e7046"),
    "libQnnHtpV75Skel.so": ("hexagon-v75/unsigned/", "2f6cfe5aae553d8ec88b6741bf8598a557375eacfc58056c2667fc43fda64f6a"),
}

# LiteRT-LM runtime + LiteRT's Qualcomm dispatch library for Linux arm64, built in CI by the flutter_edge_ai
# project (MIT) from the LiteRT-LM v0.18.0 sources against QAIRT 2.50, with the Linux NPU settings enabled.
BUNDLE_URL = "https://github.com/DenisovAV/flutter_edge_ai/releases/download/native-v0.18.0-e/litertlm-linux_arm64.tar.gz"
BUNDLE_SHA256 = "29c2306f8d42d88b500f033acf878109a9de8e58d34eb0bc75c464c536be3214"
BUNDLE_FILES = {  # file name -> (destination folder, SHA-256)
    "libLiteRtLm.so": (LITERTLM, "5a64a057bbdf8baeea5c77e78e3c470680d9a4b5629ae98db629341f8113de39"),
    "libLiteRt.so": (LITERTLM, "eb5120d0887d8b532518a7f025900ba9b4c4ac6f43e71ca3570a7ba0bb726a24"),
    "libGemmaModelConstraintProvider.so": (LITERTLM, "016f5d615a6009e8c5f3a1c3700291be3f94a8638f423460953e1c290b451f43"),
    "libLiteRtDispatch_Qualcomm.so": (LIB, "06a9be66f6e8bc58de6ec020844b381dfe3df10f891dbec0f4aaeeb68c7d269e"),
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha256(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def fetch(request, what):
    """Open a URL, retrying briefly: Wi-Fi at a busy event drops connections."""
    for attempt in range(4):
        try:
            return urlopen(request, timeout=120)
        except OSError as error:
            if attempt == 3:
                raise SystemExit(f"Could not download {what}: {error}\nCheck the board's internet connection and run this script again.")
            time.sleep(2 * (attempt + 1))


class RemoteFile(io.RawIOBase):
    """Read a big remote zip in pieces (HTTP range requests) so zipfile can pick out single members."""

    def __init__(self, url, size):
        self.url, self.size, self.position = url, size, 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        self.position = {0: offset, 1: self.position + offset, 2: self.size + offset}[whence]
        return self.position

    def readinto(self, buffer):
        if not len(buffer) or self.position >= self.size:
            return 0
        end = min(self.position + len(buffer), self.size) - 1
        with fetch(Request(self.url, headers={"Range": f"bytes={self.position}-{end}"}), "the Qualcomm libraries") as response:
            if response.status != 206:
                raise SystemExit("The Qualcomm download server did not honor a partial-download request.")
            data = response.read()
        buffer[:len(data)] = data
        self.position += len(data)
        return len(data)


def check_board(skip):
    machine = Path("/sys/devices/soc0/machine")
    found = machine.read_text().strip() if machine.exists() else "unknown"
    if found != "QCS8275" and not skip:
        raise SystemExit(f"This board reports '{found}', not QCS8275 (Ventuno Q). The libraries here target QCS8275 only. "
                         "Use --skip-board-check to continue anyway.")
    if not os.access("/dev/fastrpc-cdsp", os.R_OK | os.W_OK):
        raise SystemExit("Cannot open /dev/fastrpc-cdsp. Your account needs the 'fastrpc' group "
                         "(check with: id). Ask an organizer; do not change permissions yourself.")
    print(f"Board: {found}; NPU device is accessible.")


def get_qualcomm_libraries(force):
    LIB.mkdir(parents=True, exist_ok=True)
    pending = {name for name, (_, expected) in QAIRT_FILES.items()
               if force or not (LIB / name).is_file() or file_sha256(LIB / name) != expected}
    for name in sorted(set(QAIRT_FILES) - pending):
        print(f"Verified {name}", flush=True)
    if not pending:
        return
    print(f"Fetching {len(pending)} Qualcomm libraries (about 110 MB; the SDK zip is read in pieces)...", flush=True)
    archive = zipfile.ZipFile(io.BufferedReader(RemoteFile(QAIRT_URL, QAIRT_SIZE), 1 << 20))
    for name in sorted(pending):
        folder, expected = QAIRT_FILES[name]
        data = archive.read(QAIRT_ROOT + folder + name)
        if sha256(data) != expected:
            raise SystemExit(f"Checksum mismatch for {name}. Run this script again; if it repeats, tell an organizer.")
        (LIB / name).write_bytes(data)
        print(f"Verified {name}", flush=True)


def get_runtime_bundle(force):
    LITERTLM.mkdir(parents=True, exist_ok=True)
    wanted = {name: folder / name for name, (folder, _) in BUNDLE_FILES.items()}
    ready = {name: path.is_file() and file_sha256(path) == BUNDLE_FILES[name][1] for name, path in wanted.items()}
    if all(ready.values()) and not force:
        for name in wanted:
            print(f"Verified {name}", flush=True)
        return
    print("Fetching the LiteRT-LM NPU runtime bundle (33 MB)...", flush=True)
    with tempfile.NamedTemporaryFile(dir=ROOT / "npu", suffix=".tar.gz") as temporary:
        with fetch(Request(BUNDLE_URL), "the LiteRT-LM runtime bundle") as response:
            shutil.copyfileobj(response, temporary)
        temporary.flush()
        if file_sha256(Path(temporary.name)) != BUNDLE_SHA256:
            raise SystemExit("Checksum mismatch for the runtime bundle. Run this script again; if it repeats, tell an organizer.")
        with tarfile.open(temporary.name) as bundle:
            for member in bundle.getmembers():
                name = Path(member.name).name
                if name in wanted and member.isfile():
                    data = bundle.extractfile(member).read()
                    if sha256(data) != BUNDLE_FILES[name][1]:
                        raise SystemExit(f"Checksum mismatch for {name} inside the bundle.")
                    wanted[name].write_bytes(data)
                    print(f"Verified {name}", flush=True)


def get_libatomic(force):
    """libQnnSystem.so needs libatomic.so.1, which a stock image may not have. Get it without sudo."""
    target = LIB / "libatomic.so.1"
    if not force and target.is_file() and target.stat().st_size > 0:
        print("Using cached libatomic.so.1 (use --force to replace it)", flush=True)
        return
    found = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True).stdout
    system_copy = next((line.split("=>")[1].strip() for line in found.splitlines() if " libatomic.so.1 " in line), None)
    # Stage on the same filesystem so an interrupted copy cannot damage the cached library.
    with tempfile.TemporaryDirectory(dir=LIB) as work:
        if system_copy:
            source = Path(system_copy)
        else:
            print("Fetching libatomic1 from the Ubuntu archive (no sudo needed)...", flush=True)
            download = subprocess.run(["apt-get", "download", "libatomic1"], cwd=work, capture_output=True, text=True)
            packages = list(Path(work).glob("libatomic1_*.deb"))
            if download.returncode or not packages:
                raise SystemExit("Could not download libatomic1 (" + download.stderr.strip()[-200:] + ").\n"
                                 "Ask an organizer, or install it yourself with: sudo apt install libatomic1")
            subprocess.run(["dpkg-deb", "-x", str(packages[0]), work + "/unpacked"], check=True)
            source = Path(work, "unpacked/usr/lib/aarch64-linux-gnu/libatomic.so.1.2.0")
        staged = Path(work) / target.name
        shutil.copy(source, staged)
        staged.replace(target)
    print("Installed libatomic.so.1 into npu/lib", flush=True)


def link_fastrpc():
    """The Qualcomm libraries look for libcdsprpc.so; the board ships it as libcdsprpc.so.1."""
    system_copy = Path("/usr/lib/aarch64-linux-gnu/libcdsprpc.so.1")
    if not system_copy.exists():
        raise SystemExit("The board's FastRPC library (libcdsprpc.so.1) is missing. Ask an organizer; "
                         "it ships with the Ventuno Q image.")
    link = LIB / "libcdsprpc.so"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(system_copy)
    print("Linked libcdsprpc.so to the board's FastRPC library", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="download everything again")
    parser.add_argument("--skip-board-check", action="store_true", help="continue on a board that is not a QCS8275")
    args = parser.parse_args()
    check_board(args.skip_board_check)
    (ROOT / "npu").mkdir(exist_ok=True)
    get_qualcomm_libraries(args.force)
    get_runtime_bundle(args.force)
    get_libatomic(args.force)
    link_fastrpc()
    print("\nNPU files are ready in ./npu. Next, try the NPU examples:\n"
          "  .venv-litert/bin/python examples/standalone-litert/main.py --backend npu --check\n"
          "  .venv-lm/bin/python examples/standalone-embedding/main.py --backend npu --check\n"
          "  .venv-lm/bin/python examples/standalone-litert-lm-npu/main.py")
