from pathlib import Path
from sft.information_science.noise_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-NOISE-BURST-CORRELATION-009', Path(__file__).resolve())
