from pathlib import Path
from sft.physics.new_sector_complete_family_empirical_execution_v1 import build_execution as _build
def build_execution(root: Path): return _build(root, Path(__file__).resolve())
__all__ = ("build_execution",)
