from pathlib import Path

from sft.engineering.vacuum_recurrence_cycle_execution_v1 import build_execution as _build


def build_execution(root: Path):
    return _build(root, Path(__file__).resolve())


__all__ = ("build_execution",)
