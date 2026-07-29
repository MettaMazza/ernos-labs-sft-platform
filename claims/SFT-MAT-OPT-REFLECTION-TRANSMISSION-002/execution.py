from pathlib import Path
from sft.materials.opt_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-OPT-REFLECTION-TRANSMISSION-002', Path(__file__).resolve())
