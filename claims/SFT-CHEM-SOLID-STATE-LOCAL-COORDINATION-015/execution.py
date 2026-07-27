from pathlib import Path
import json
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.solid_state_local_coordination_batch_v1 import (
    FAMILY_BOUNDARY_PATH,
    FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH,
    IDENTITY_PATH,
    PRIMARY_PATH,
    SOLID_STATE_LOCAL_COORDINATION_SPEC,
    TARGET_PATH,
)
from sft.chemistry.solid_state_local_coordination_validation_v1 import SolidStateLocalCoordinationValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path):
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    snapshots = tuple(dict.fromkeys(row["snapshot_path"] for row in identities["rows"]))
    files = (
        root / "sft/chemistry/solid_state_local_coordination_law_v1.py",
        root / "sft/chemistry/solid_state_local_coordination_batch_v1.py",
        root / "sft/chemistry/solid_state_local_coordination_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/build_chemistry_inorg_014_017_identities_v1.py",
        root / "tools/build_chemistry_inorg_014_017_primary_v1.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        root / PRIMARY_PATH,
        *(root / path for path in snapshots),
        root / "claims/SFT-CHEM-SOLID-STATE-LOCAL-COORDINATION-015/execution.py",
    )
    files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, files).manifest_hash
    independent = root / "claims/SFT-CHEM-SOLID-STATE-LOCAL-COORDINATION-015/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(SOLID_STATE_LOCAL_COORDINATION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-solid-state-local-coordination-015-independent-python/1",
            (sys.executable, str(independent)),
            independent.parent,
            (independent,),
        ),
        files,
        SolidStateLocalCoordinationValidator(root),
    )
