from pathlib import Path

from sft.physics.tesla_resonance_family_execution_v1 import build_execution as _build
from sft.physics.tesla_resonance_family_law_v1 import ODD_QUARTER_ID


def build_execution(root: Path):
    return _build(root, ODD_QUARTER_ID, Path(__file__).resolve())


__all__ = ("build_execution",)
