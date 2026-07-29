#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sft.mathematics.arith_001_018_laws_v1 import SPECS
def main():
 for cid in SPECS:
  path=ROOT/"claims"/cid/"execution.py"
  if path.exists():raise SystemExit("refusing overwrite "+str(path))
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text("from pathlib import Path\nfrom sft.mathematics.arith_001_018_execution_v1 import build_execution as assemble\ndef build_execution(root: Path):\n    return assemble(root, "+repr(cid)+", Path(__file__).resolve())\n")
 print("scaffolded",len(SPECS),"Mathematics ARITH execution entrypoints")
if __name__=="__main__":main()
