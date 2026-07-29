#!/usr/bin/env python3
"""Create mechanical per-claim execution entrypoints for QALGX."""
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from sft.quantum_computation.qalgx_001_030_laws_v1 import IDS


def main():
    for claim_id in IDS:
        path = ROOT / "claims" / claim_id / "execution.py"
        if path.exists():
            raise SystemExit("QALGX execution entrypoint already exists: " + claim_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("from pathlib import Path\nfrom sft.quantum_computation.qalgx_001_030_execution_v1 import build_execution as assemble\n" + f'def build_execution(root: Path): return assemble(root, "{claim_id}", Path(__file__).resolve())\n', encoding="utf-8")
    print(f"created {len(IDS)} QALGX execution entrypoints")


if __name__ == "__main__":
    main()
