from pathlib import Path
from sft.chemistry.valid_001_012_execution_v2 import build_execution as b
def build_execution(root:Path):return b(root,"SFT-CHEM-VALIDATION-ADVERSE-OUT-OF-BOUND-VECTOR-011",Path(__file__).resolve())
