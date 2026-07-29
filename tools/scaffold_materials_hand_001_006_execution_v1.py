#!/usr/bin/env python3
"""Create the six Materials HAND execution entrypoints from frozen specs."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from sft.materials.hand_001_006_laws_v1 import SPECS
def main():
 for cid in SPECS:
  p=ROOT/"claims"/cid/"execution.py"
  if p.exists(): raise SystemExit("refusing overwrite "+str(p))
  p.parent.mkdir(parents=True,exist_ok=True); p.write_text("from pathlib import Path\nfrom sft.materials.hand_001_006_execution_v1 import build_execution as assemble\ndef build_execution(root: Path):\n    return assemble(root, "+repr(cid)+", Path(__file__).resolve())\n")
 print("scaffolded",len(SPECS),"Materials HAND execution entrypoints")
if __name__=="__main__": main()
