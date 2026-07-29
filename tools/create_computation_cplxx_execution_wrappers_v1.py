#!/usr/bin/env python3
"""Mechanically create the fixed CPLXX claim execution entry points."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from sft.computation.cplxx_001_033_laws_v1 import IDS
TEMPLATE='from pathlib import Path\nfrom sft.computation.cplxx_001_033_execution_v1 import build_execution as assemble\ndef build_execution(root: Path): return assemble(root, "{claim_id}", Path(__file__).resolve())\n'
def main():
    for claim_id in IDS:
        path=ROOT/"claims"/claim_id/"execution.py"
        if path.exists():raise SystemExit("CPLXX execution wrapper already exists: "+claim_id)
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(TEMPLATE.format(claim_id=claim_id))
    print(f"created {len(IDS)} CPLXX execution entry points")
if __name__=="__main__":main()
