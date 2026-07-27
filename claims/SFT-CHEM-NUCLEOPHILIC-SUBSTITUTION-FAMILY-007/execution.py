"""Official execution binding for SFT-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007."""
from pathlib import Path
import json
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.nucleophilic_substitution_batch_v1 import (
    CAPTURE_INVENTORY_PATH, CORRECTION_PATH, FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH, IDENTITY_PATH, NUCLEOPHILIC_SUBSTITUTION_SPEC, PRE_SOURCE_PATH, PRIMARY_PATH, TARGET_PATH,
)
from sft.chemistry.nucleophilic_substitution_validation_v1 import NucleophilicSubstitutionValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def _paths(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _paths(item)
    elif isinstance(value, list):
        for item in value:
            yield from _paths(item)
    elif isinstance(value, str) and not value.startswith("sha256:") and "/" in value and len(value) < 512:
        yield Path(value)


def build_execution(root: Path) -> ClaimExecution:
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    referenced = tuple(path for path in _paths(targets) if (root / path).is_file())
    fixed = (
        "sft/chemistry/nucleophilic_substitution_law_v1.py", "sft/chemistry/nucleophilic_substitution_batch_v1.py",
        "sft/chemistry/nucleophilic_substitution_validation_v1.py", "sft/chemistry/generated_law.py",
        "sft/chemistry/generated_observational_law.py", "sft/physics/generated_empirical_law.py",
        "tools/capture_chemistry_org_007_blind_sources_v1.py", "tools/build_chemistry_org_007_external_v1.py",
        FAMILY_BOUNDARY_PATH, FAMILY_REGISTRY_PATH, FAMILY_INVENTORY_PATH, IDENTITY_PATH, CORRECTION_PATH,
        CAPTURE_INVENTORY_PATH, PRE_SOURCE_PATH, TARGET_PATH, PRIMARY_PATH,
        "claims/SFT-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007/execution.py",
    )
    files = tuple(dict.fromkeys(root / path for path in (*fixed, *referenced)))
    source_hash = build_source_manifest(root, files).manifest_hash
    independent = root / "claims/SFT-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(NUCLEOPHILIC_SUBSTITUTION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-nucleophilic-substitution-007-independent-python/1",
            (sys.executable, str(independent)), independent.parent, (independent,),
        ),
        files, NucleophilicSubstitutionValidator(root),
    )
