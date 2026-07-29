#!/usr/bin/env python3
"""Create the mechanical per-claim execution entrypoints for REVX."""
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.quantum_computation.revx_001_018_laws_v1 import IDS


def main():
    for claim_id in IDS:
        path = ROOT / "claims" / claim_id / "execution.py"
        if path.exists():
            raise SystemExit("REVX execution entrypoint already exists: " + claim_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "from pathlib import Path\n"
            "from sft.quantum_computation.revx_001_018_execution_v1 import build_execution as assemble\n"
            f'def build_execution(root: Path): return assemble(root, "{claim_id}", Path(__file__).resolve())\n',
            encoding="utf-8",
        )
    print(f"created {len(IDS)} REVX execution entrypoints")


if __name__ == "__main__":
    main()
