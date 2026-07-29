"""Execution package for the V3 Unified Constants Object."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.physics.unified_constants_object_law_v1 import CLAIM_ID, DEPENDENCIES, SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    fixed = (
        root / "sft/physics/unified_constants_object_law_v1.py",
        root / "sft/physics/unified_constants_object_execution_v1.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/cosmology_prior_value_laws.py",
        root / "sft/physics/hubble_calibration_law.py",
        root / "sft/physics/lineage_particle_laws.py",
        root / "sft/physics/matter_flavour_laws_v1.py",
        root / "sft/physics/precision_value_laws_v1.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/terminal_lepton_law.py",
        root / "sft/physics/vacuum_density_scale_terminal_law_v1.py",
        root / "sft/physics/structural_constants.py",
        execution_file,
    )
    evidence = []
    for claim_id in DEPENDENCIES:
        package = root / "claims" / claim_id
        evidence.extend((package / "registration.json", package / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + tuple(evidence)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/unified_constants_object_validator_v1.py"
    return ClaimExecution(
        StructuralPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator(
            "sft-physics-unified-constants-object-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID, str(root)),
            validator.parent,
            (validator,),
        ),
        files,
    )


__all__ = ("build_execution",)
