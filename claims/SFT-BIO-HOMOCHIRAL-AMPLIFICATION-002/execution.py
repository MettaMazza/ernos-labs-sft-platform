from pathlib import Path
from sft.biology.prior_mechanisms_execution_v1 import build_execution as _build
from sft.biology.prior_mechanisms_laws_v1 import CHIRAL_ID
def build_execution(root: Path): return _build(root, CHIRAL_ID, Path(__file__).resolve())
__all__ = ("build_execution",)
