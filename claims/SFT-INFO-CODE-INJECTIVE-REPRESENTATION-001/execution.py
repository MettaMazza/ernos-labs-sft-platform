from pathlib import Path
from sft.information_science.code_001_018_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-CODE-INJECTIVE-REPRESENTATION-001', Path(__file__).resolve())
