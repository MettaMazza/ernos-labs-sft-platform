"""Official execution binding for SFT-CHEM-RESONANCE-EQUIVALENT-REPRESENTATION-002."""
from pathlib import Path
import json
import sys

from sft.chemistry.resonance_equivalent_representation_batch_v1 import (
    FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH, FAMILY_REGISTRY_PATH,
    IDENTITY_PATH, PRE_SOURCE_PATH, PRIMARY_PATH,
    RESONANCE_EQUIVALENT_REPRESENTATION_SPEC, TARGET_PATH,
    V1_PRIMARY_PATH, V1_TARGET_PATH,
)
from sft.chemistry.resonance_equivalent_representation_validation_v1 import ResonanceEquivalentRepresentationValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    snapshots = tuple(dict.fromkeys(row["snapshot_path"] for row in identities["rows"]))
    files = (
        root / "sft/chemistry/resonance_equivalent_representation_law_v1.py",
        root / "sft/chemistry/resonance_equivalent_representation_batch_v1.py",
        root / "sft/chemistry/resonance_equivalent_representation_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_org_001_016_family_sources_v1.py",
        root / "tools/build_chemistry_org_002_primary_v1.py",
        root / "tools/build_chemistry_org_002_primary_correction_v2.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / PRE_SOURCE_PATH,
        root / IDENTITY_PATH,
        root / V1_TARGET_PATH,
        root / V1_PRIMARY_PATH,
        root / TARGET_PATH,
        root / PRIMARY_PATH,
        *(root / path for path in snapshots),
        root / "claims/SFT-CHEM-RESONANCE-EQUIVALENT-REPRESENTATION-002/execution.py",
    )
    files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, files).manifest_hash
    independent = root / "claims/SFT-CHEM-RESONANCE-EQUIVALENT-REPRESENTATION-002/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(RESONANCE_EQUIVALENT_REPRESENTATION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-resonance-equivalent-representation-002-independent-python/1",
            (sys.executable, str(independent)),
            independent.parent,
            (independent,),
        ),
        files,
        ResonanceEquivalentRepresentationValidator(root),
    )
