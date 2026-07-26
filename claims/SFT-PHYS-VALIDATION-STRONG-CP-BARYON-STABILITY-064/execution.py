from pathlib import Path

from sft.physics.strong_cp_baryon_stability_empirical_execution_v1 import build_execution as _build_execution


def build_execution(root: Path):
    return _build_execution(root, Path(__file__).resolve())
