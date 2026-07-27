"""Official execution binding for INORG-005."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.coordination_isomerism_batch_v1 import (
    ADDENDUM_INVENTORY_PATH,
    ADDENDUM_PATH,
    COORDINATION_ISOMERISM_SPEC,
    FAMILY_BOUNDARY_PATH,
    FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH,
    IDENTITY_PATH,
    PRELIMINARY_IDENTITY_PATH,
    PRIMARY_PATH,
    SOURCE_FILES,
    TARGET_PATH,
)
from sft.chemistry.coordination_isomerism_validation_v1 import CoordinationIsomerismValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path):
    files = (
        root / "sft/chemistry/coordination_isomerism_law_v1.py",
        root / "sft/chemistry/coordination_isomerism_batch_v1.py",
        root / "sft/chemistry/coordination_isomerism_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_inorg_004_017_family_sources_v1.py",
        root / "tools/register_chemistry_coordination_isomerism_identities_v1.py",
        root / "tools/capture_chemistry_inorg_005_linkage_addendum_v1.py",
        root / "tools/register_chemistry_coordination_isomerism_identities_v2.py",
        root / "tools/build_chemistry_coordination_isomerism_primary_v1.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / ADDENDUM_PATH,
        root / ADDENDUM_INVENTORY_PATH,
        root / PRELIMINARY_IDENTITY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        root / PRIMARY_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        root / "claims/SFT-CHEM-COORDINATION-ISOMERISM-EQUIVALENCE-005/execution.py",
    )
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "claims/SFT-CHEM-COORDINATION-ISOMERISM-EQUIVALENCE-005/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(COORDINATION_ISOMERISM_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-coordination-isomerism-005-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        files,
        CoordinationIsomerismValidator(root),
    )
