from pathlib import Path
from sft.materials.ext_001_008_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-EXT-COMBINED-PATH-CUSTODY-008', Path(__file__).resolve())
