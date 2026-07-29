from pathlib import Path
from sft.materials.bio_001_008_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-BIO-BIORESORPTION-DEGRADATION-002', Path(__file__).resolve())
