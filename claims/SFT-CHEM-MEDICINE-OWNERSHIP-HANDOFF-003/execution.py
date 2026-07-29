from pathlib import Path
from sft.chemistry.hand_001_006_execution_v2 import build_execution as _build
CLAIM_ID = "SFT-CHEM-MEDICINE-OWNERSHIP-HANDOFF-003"
def build_execution(root: Path): return _build(root, CLAIM_ID, Path(__file__).resolve())
