from pathlib import Path

from sft.physics.dark_smithion_lfv_terminal_execution_v1 import build_execution as _build_execution


def build_execution(root: Path):
    return _build_execution(root, Path(__file__).resolve())
