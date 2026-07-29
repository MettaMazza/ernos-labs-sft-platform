from pathlib import Path

from sft.physics.tesla_resonant_transfer_execution_v2 import build_execution as _build


def build_execution(root: Path):
    return _build(root, Path(__file__).resolve())


__all__ = ("build_execution",)
