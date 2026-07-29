from pathlib import Path
from sft.chemistry.smithium_return_execution_v1 import build_execution as _build
from sft.chemistry.smithium_return_laws_v1 import DETECTION_ID
def build_execution(root: Path): return _build(root, DETECTION_ID, Path(__file__).resolve())
__all__ = ("build_execution",)
