from pathlib import Path
from sft.synthesis.prior_identity_execution_v1 import build_execution as b
def build_execution(root:Path):return b(root,"SFT-SYNTH-ONE-OWNER-NO-OMISSION-LEDGER-001",Path(__file__).resolve())
