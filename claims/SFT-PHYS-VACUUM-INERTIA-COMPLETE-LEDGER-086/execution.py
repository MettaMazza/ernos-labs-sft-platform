from pathlib import Path
from sft.physics.vacuum_inertia_drive_family_execution_v1 import build_execution as _build
from sft.physics.vacuum_inertia_drive_family_law_v1 import COMPLETE_LEDGER_ID
def build_execution(root: Path): return _build(root, COMPLETE_LEDGER_ID, Path(__file__).resolve())
__all__ = ("build_execution",)
