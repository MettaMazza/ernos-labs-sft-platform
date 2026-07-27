"""Official execution binding for SFT-CHEM-AROMATIC-RECURRENCE-STABILITY-003."""
from pathlib import Path
import json
import sys

from sft.chemistry.aromatic_recurrence_stability_batch_v1 import (
    AROMATIC_RECURRENCE_STABILITY_SPEC, BLIND_IDENTITY_PATH, BLIND_INVENTORY_PATH,
    FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH, FAMILY_REGISTRY_PATH,
    IDENTITY_PATH, PRE_SOURCE_PATH, PRIMARY_PATH, TARGET_PATH,
)
from sft.chemistry.aromatic_recurrence_stability_validation_v1 import AromaticRecurrenceStabilityValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    snapshots = tuple(dict.fromkeys(row["opened_snapshot_path"] for row in targets["rows"]))
    files = (
        root / "sft/chemistry/aromatic_recurrence_stability_law_v1.py",
        root / "sft/chemistry/aromatic_recurrence_stability_batch_v1.py",
        root / "sft/chemistry/aromatic_recurrence_stability_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_org_001_016_family_sources_v1.py",
        root / "tools/capture_chemistry_org_003_blind_cccbdb_sources_v1.py",
        root / "tools/build_chemistry_org_003_primary_v1.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / BLIND_IDENTITY_PATH,
        root / BLIND_INVENTORY_PATH,
        root / PRE_SOURCE_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        root / PRIMARY_PATH,
        *(root / path for path in snapshots),
        root / "claims/SFT-CHEM-AROMATIC-RECURRENCE-STABILITY-003/execution.py",
    )
    files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, files).manifest_hash
    independent = root / "claims/SFT-CHEM-AROMATIC-RECURRENCE-STABILITY-003/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(AROMATIC_RECURRENCE_STABILITY_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-aromatic-recurrence-stability-003-independent-python/1",
            (sys.executable, str(independent)), independent.parent, (independent,),
        ),
        files,
        AromaticRecurrenceStabilityValidator(root),
    )
