#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.information_science.retr_001_012_laws_v1 import SPECS


def main():
    for claim_id in SPECS:
        path = ROOT / "claims" / claim_id / "execution.py"
        if path.exists():
            raise SystemExit("refusing overwrite " + str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "from pathlib import Path\n"
            "from sft.information_science.retr_001_012_execution_v1 import build_execution as assemble\n"
            "def build_execution(root: Path):\n"
            f"    return assemble(root, {claim_id!r}, Path(__file__).resolve())\n"
        )
    print("scaffolded", len(SPECS), "Information Science RETR execution entrypoints")


if __name__ == "__main__":
    main()
