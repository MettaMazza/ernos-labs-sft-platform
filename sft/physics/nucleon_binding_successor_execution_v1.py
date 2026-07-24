"""Official engine binding for terminal nucleon binding."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.nucleon_binding_successor_laws_v1 import NUCLEON_BINDING_SPEC
from sft.physics.nucleon_binding_successor_validation_v1 import NucleonBindingValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_nucleon_binding_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/matter_flavour_laws_v1.py",
        root / "sft/physics/matter_flavour_terminal_proton_laws_v1.py",
        root / "sft/physics/nucleon_binding_successor_laws_v1.py",
        root / "sft/physics/nucleon_binding_successor_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/nucleon_binding_successor_execution_v1.py",
        execution_file,
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/nucleon_binding_successor_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(NUCLEON_BINDING_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-nucleon-binding-independent-python/1",
            (sys.executable, str(validator), NUCLEON_BINDING_SPEC.claim_id),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=NucleonBindingValidator(root),
    )


__all__ = ("build_nucleon_binding_execution",)
