from pathlib import Path
from sft.materials.proc_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-PROC-POLYMER-ORIENTATION-008', Path(__file__).resolve())
