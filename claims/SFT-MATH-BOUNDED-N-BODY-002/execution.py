"""Official execution binding for SFT-MATH-BOUNDED-N-BODY-002."""
from pathlib import Path
from sft.mathematics.lineage_execution import build_lineage_execution
CLAIM_ID = "SFT-MATH-BOUNDED-N-BODY-002"
def build_execution(root: Path):
    return build_lineage_execution(root, CLAIM_ID, Path(__file__), Path(__file__).with_name("independent_validator.py"))
