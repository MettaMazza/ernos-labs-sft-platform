#!/usr/bin/env python3
"""Create the twelve mechanical VALID execution entry points."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from sft.computation.valid_001_012_laws_v1 import IDS


def main():
    for claim_id in IDS:
        path = ROOT / "claims" / claim_id / "execution.py"
        if path.exists():
            raise SystemExit("VALID execution entry already exists: " + claim_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "from pathlib import Path\n"
            "from sft.computation.valid_001_012_execution_v1 import build_execution as assemble\n"
            f"def build_execution(root: Path): return assemble(root, {claim_id!r}, Path(__file__).resolve())\n"
        )
    print(f"created {len(IDS)} VALID execution entry points")


if __name__ == "__main__":
    main()
