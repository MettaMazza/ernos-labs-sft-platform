from pathlib import Path
from sft.mathematics.logic_001_016_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-LOGIC-INFERENCE-CONSEQUENCE-002', Path(__file__).resolve())
