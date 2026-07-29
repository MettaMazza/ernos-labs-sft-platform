#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    from sft.quantum_computation.hand_001_006_laws_v1 import IDS
    for claim_id in IDS:
        path = ROOT / "claims" / claim_id / "execution.py"
        if path.exists():
            raise SystemExit("HAND execution entrypoint already exists: " + claim_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("from pathlib import Path\nfrom sft.quantum_computation.hand_001_006_execution_v1 import build_execution as assemble\n" + f'def build_execution(root: Path): return assemble(root, "{claim_id}", Path(__file__).resolve())\n', encoding="utf-8")
    print(f"created {len(IDS)} HAND execution entrypoints")


if __name__ == "__main__":
    main()
