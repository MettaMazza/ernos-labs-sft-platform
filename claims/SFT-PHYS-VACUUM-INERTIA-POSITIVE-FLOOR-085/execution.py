from pathlib import Path
from sft.physics.vacuum_inertia_drive_family_execution_v1 import build_execution as _build
from sft.physics.vacuum_inertia_drive_family_law_v1 import POSITIVE_FLOOR_ID
def build_execution(root: Path): return _build(root, POSITIVE_FLOOR_ID, Path(__file__).resolve())
__all__ = ("build_execution",)
