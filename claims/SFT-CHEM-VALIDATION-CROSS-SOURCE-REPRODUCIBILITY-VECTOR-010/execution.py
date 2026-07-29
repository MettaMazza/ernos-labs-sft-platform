from pathlib import Path
from sft.chemistry.valid_001_012_execution_v2 import build_execution as b
def build_execution(root:Path):return b(root,"SFT-CHEM-VALIDATION-CROSS-SOURCE-REPRODUCIBILITY-VECTOR-010",Path(__file__).resolve())
