"""Official execution binding for INORG-001."""
from pathlib import Path
import sys
from sft.chemistry.coordination_entity_batch_v1 import COORDINATION_ENTITY_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.coordination_entity_validation_v1 import CoordinationEntityValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path):
    files = (
        root / "sft/chemistry/coordination_entity_law_v1.py",
        root / "sft/chemistry/coordination_entity_batch_v1.py",
        root / "sft/chemistry/coordination_entity_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_coordination_entity_sources_v1.py",
        root / "tools/register_chemistry_coordination_entity_identities_v1.py",
        root / "tools/build_chemistry_coordination_entity_primary_v1.py",
        root / SPEC_PATH,
        root / INVENTORY_PATH,
        root / PRIMARY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        root / "claims/SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001/execution.py",
    )
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "claims/SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(COORDINATION_ENTITY_SPEC, source_hash),
        ExternalCommandValidator("sft-chem-coordination-entity-001-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        files,
        CoordinationEntityValidator(root),
    )
