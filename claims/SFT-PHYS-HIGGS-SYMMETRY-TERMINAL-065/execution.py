from pathlib import Path

from sft.physics.higgs_symmetry_terminal_execution_v1 import build_execution as _build_execution


def build_execution(root: Path):
    return _build_execution(root, Path(__file__).resolve())
