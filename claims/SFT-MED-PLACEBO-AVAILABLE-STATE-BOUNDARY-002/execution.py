from pathlib import Path
from sft.medicine.placebo_nocebo_execution_v1 import build_execution as _build
from sft.medicine.placebo_nocebo_laws_v1 import BOUND_ID
def build_execution(root: Path): return _build(root, BOUND_ID, Path(__file__).resolve())
__all__ = ("build_execution",)
