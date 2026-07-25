"""Official execution binding for fusion/fission yield and thresholds."""

from pathlib import Path

from sft.physics.fusion_fission_yield_threshold_execution_v1 import (
    build_fusion_fission_yield_threshold_execution,
)


def build_execution(root: Path):
    return build_fusion_fission_yield_threshold_execution(root, Path(__file__))
