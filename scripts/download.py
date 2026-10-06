"""Fetch pinned public model/test assets. No Hugging Face account or SDK required."""
import argparse
import hashlib
from pathlib import Path
import shutil
import tempfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
CORAL = "https://raw.githubusercontent.com/google-coral/test_data/104342d2d3480b3e66203073dac24f4e2dbb4c41/"
GEMMA = "https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm/resolve/b3ca0d2f076785a8f4b2219ddbd2bdb99954eae1/"
ASSETS = {
    "gemma": [
        (GEMMA, "gemma-4-E2B-it.litertlm", "181938105e0eefd105961417e8da75903eacda102c4fce9ce90f50b97139a63c"),
    ],
    "vision": [
        (CORAL, "mobilenet_v2_1.0_224_quant.tflite", "7aad0c74c5e3c06e5eb3c827e13304fdd68a83da6087d92ee169c24ff9fd4776"),
        (CORAL, "imagenet_labels.txt", "b8aaeb5630c62626a7d124a05c0e14230a7ffdd2136a31d0190a4fb71c1d82f1"),
        (CORAL, "parrot.jpg", "a8fba9e7e29439fa414c13129aad661f2289ff891231920a7c33641b076f1833"),
    ],
}


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def download(url, expected, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if digest(target) != expected:
            raise ValueError(f"Checksum mismatch: {target}. Move the file aside, then retry.")
        print(f"Verified {target.name}", flush=True)
        return
    temporary = None
    try:
        print(f"Downloading {target.name}...", flush=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as output:
            temporary = Path(output.name)
            with urlopen(url, timeout=60) as source:
                shutil.copyfileobj(source, output)
        if digest(temporary) != expected:
            raise ValueError(f"Download checksum mismatch: {target.name}")
        temporary.replace(target)
        print(f"Verified {target.name}", flush=True)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=ASSETS)
    args = parser.parse_args()
    for base, name, sha256 in ASSETS[args.group]:
        download(base + name, sha256, ROOT / "models" / name)
