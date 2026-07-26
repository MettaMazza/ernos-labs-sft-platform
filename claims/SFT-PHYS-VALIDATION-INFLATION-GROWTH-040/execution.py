from pathlib import Path

from sft.physics.inflation_growth_empirical_execution_v1 import build_execution as _build


def build_execution(root: Path):
    return _build(root, Path(__file__).resolve())
