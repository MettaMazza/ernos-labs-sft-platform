from pathlib import Path
from sft.information_science.measure_001_016_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-MEASURE-RELATIVE-011', Path(__file__).resolve())
