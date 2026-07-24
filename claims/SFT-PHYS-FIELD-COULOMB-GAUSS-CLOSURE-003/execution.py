"""Official execution binding for SFT-PHYS-FIELD-COULOMB-GAUSS-CLOSURE-003."""

from pathlib import Path
from sft.physics.relativistic_field_execution_v1 import build_relativistic_field_execution


def build_execution(root: Path):
    return build_relativistic_field_execution(root, 'SFT-PHYS-FIELD-COULOMB-GAUSS-CLOSURE-003', Path(__file__))
