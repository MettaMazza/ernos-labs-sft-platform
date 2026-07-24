"""Official execution binding for SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005."""

from pathlib import Path

from sft.physics.nuclear_binding_curve_successor_execution_v1 import build_nuclear_binding_curve_execution


def build_execution(root: Path):
    return build_nuclear_binding_curve_execution(root, Path(__file__))
