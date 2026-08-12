from pathlib import Path

from sft.physics.vacuum_recurrence_work_cycle_execution_v1 import build_execution as _build
from sft.physics.vacuum_recurrence_work_cycle_law_v1 import WORK_CYCLE_ID


def build_execution(root: Path):
    return _build(root, WORK_CYCLE_ID, Path(__file__).resolve())


__all__ = ("build_execution",)
