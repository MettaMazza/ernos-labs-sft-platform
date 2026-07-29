from pathlib import Path
from sft.materials.nano_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-NANO-AGGREGATION-DISPERSION-CUSTODY-010', Path(__file__).resolve())
