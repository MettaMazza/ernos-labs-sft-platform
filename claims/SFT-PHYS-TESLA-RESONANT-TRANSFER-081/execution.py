from pathlib import Path

from sft.physics.tesla_resonance_family_execution_v1 import build_execution as _build
from sft.physics.tesla_resonance_family_law_v1 import RESONANT_TRANSFER_ID


def build_execution(root: Path):
    return _build(root, RESONANT_TRANSFER_ID, Path(__file__).resolve())


__all__ = ("build_execution",)
