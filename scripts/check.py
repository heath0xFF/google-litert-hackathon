"""Offline repository checks. No board, network, or ML packages required."""
import ast
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.version_info < (3, 11):
        raise SystemExit("Use Python 3.11 or newer (3.12 recommended).")
    paths = list(ROOT.glob("*.md"))
    for directory in (".agents/skills", ".claude/skills"):
        paths.extend((ROOT / directory).glob("*/SKILL.md"))
    for directory in ("docs", "examples", "scripts", "tests"):
        paths.extend(path for path in (ROOT / directory).rglob("*")
                     if path.is_file() and not any(part.startswith(".") for part in path.relative_to(ROOT).parts))
    for path in paths:
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if path.suffix == ".md":
            # Check local Markdown link destinations; external URLs and heading anchors are not fetched.
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if ":" not in link and not link.startswith("#"):
                    destination = path.parent / link.split("#")[0]
                    if not destination.exists():
                        raise ValueError(f"Broken local link in {path.relative_to(ROOT)}: {link}")
    for check in ("check_download.py", "check_skills.py"):
        subprocess.run([sys.executable, str(ROOT / "tests" / check)], check=True, cwd=ROOT)
    print("PASS: Python syntax, local documentation paths, skill structure, and downloader checks")


if __name__ == "__main__":
    main()
