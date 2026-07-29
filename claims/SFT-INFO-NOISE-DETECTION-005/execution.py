from pathlib import Path
from sft.information_science.noise_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-NOISE-DETECTION-005', Path(__file__).resolve())
