"""Official execution binding for INORG-004."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.coordination_geometry_batch_v1 import (
    COORDINATION_GEOMETRY_SPEC,
    CORRECTION_INVENTORY_PATH,
    CORRECTION_PATH,
    FAMILY_BOUNDARY_PATH,
    FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH,
    IDENTITY_PATH,
    PRIMARY_PATH,
    SOURCE_FILES,
    TARGET_PATH,
)
from sft.chemistry.coordination_geometry_validation_v1 import CoordinationGeometryValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path):
    files = (
        root / "sft/chemistry/coordination_geometry_law_v1.py",
        root / "sft/chemistry/coordination_geometry_batch_v1.py",
        root / "sft/chemistry/coordination_geometry_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_inorg_004_017_family_sources_v1.py",
        root / "tools/capture_chemistry_inorg_004_geometry_correction_v1.py",
        root / "tools/register_chemistry_coordination_geometry_identities_v1.py",
        root / "tools/build_chemistry_coordination_geometry_primary_v1.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / CORRECTION_PATH,
        root / CORRECTION_INVENTORY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        root / PRIMARY_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        root / "claims/SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004/execution.py",
    )
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "claims/SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(COORDINATION_GEOMETRY_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-coordination-geometry-004-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        files,
        CoordinationGeometryValidator(root),
    )
