from pathlib import Path
from sft.materials.therm_001_007_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-THERM-PHONON-MEAN-PATH-003', Path(__file__).resolve())
