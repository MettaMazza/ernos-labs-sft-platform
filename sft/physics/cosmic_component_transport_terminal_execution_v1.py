"""Official frozen-engine binding for terminal cosmic transport."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.cosmic_component_transport_terminal_law_v1 import CLAIM_ID, SPEC
from sft.physics.cosmic_component_transport_terminal_validation_v1 import CosmicComponentTransportExternalValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/cosmic_component_transport_terminal_law_v1.py",
        root / "sft/physics/cosmic_component_transport_terminal_validation_v1.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measured_value.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/cosmic_component_transport_terminal_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-cosmic-component-transport-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=CosmicComponentTransportExternalValidator(root),
    )


__all__ = ("build_execution",)
