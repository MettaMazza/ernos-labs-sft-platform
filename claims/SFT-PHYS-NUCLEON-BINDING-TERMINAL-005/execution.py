"""Official execution binding for SFT-PHYS-NUCLEON-BINDING-TERMINAL-005."""

from pathlib import Path

from sft.physics.nucleon_binding_successor_execution_v1 import build_nucleon_binding_execution


def build_execution(root: Path):
    return build_nucleon_binding_execution(root, Path(__file__))
