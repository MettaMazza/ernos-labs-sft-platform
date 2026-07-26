from pathlib import Path

from sft.physics.criticality_universality_turbulence_terminal_execution_v1 import build_execution as _build


def build_execution(root: Path):
    return _build(root, Path(__file__).resolve())
