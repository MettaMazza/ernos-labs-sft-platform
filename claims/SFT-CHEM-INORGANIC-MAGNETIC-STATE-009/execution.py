"""Official execution binding for Chemistry INORG-009."""

from pathlib import Path
import json
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.inorganic_magnetic_state_batch_v1 import (
    ADDENDUM_PATH, FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH, FAMILY_REGISTRY_PATH,
    IDENTITY_PATH, INORGANIC_MAGNETIC_STATE_SPEC, PRIMARY_PATH, SHARED_IDENTITY_PATH,
    SHARED_PRIMARY_PATH, SHARED_TARGET_PATH, TARGET_PATH,
)
from sft.chemistry.inorganic_magnetic_state_validation_v1 import InorganicMagneticStateValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path):
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    snapshot_paths = tuple(dict.fromkeys(row["snapshot_path"] for row in identities["rows"] if "snapshot_path" in row))
    files = (
        root / "sft/chemistry/inorganic_magnetic_state_law_v1.py",
        root / "sft/chemistry/inorganic_magnetic_state_batch_v1.py",
        root / "sft/chemistry/inorganic_magnetic_state_validation_v1.py",
        root / "sft/chemistry/generated_law.py", root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/build_chemistry_inorganic_magnetic_state_identities_v1.py",
        root / "tools/build_chemistry_inorganic_magnetic_state_primary_v1.py",
        root / FAMILY_BOUNDARY_PATH, root / FAMILY_REGISTRY_PATH, root / FAMILY_INVENTORY_PATH,
        root / ADDENDUM_PATH, root / IDENTITY_PATH, root / TARGET_PATH, root / PRIMARY_PATH,
        root / SHARED_IDENTITY_PATH, root / SHARED_TARGET_PATH, root / SHARED_PRIMARY_PATH,
        *(root / path for path in snapshot_paths),
        root / "claims/SFT-CHEM-INORGANIC-MAGNETIC-STATE-009/execution.py",
    )
    unique_files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, unique_files).manifest_hash
    validator = root / "claims/SFT-CHEM-INORGANIC-MAGNETIC-STATE-009/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(INORGANIC_MAGNETIC_STATE_SPEC, source_hash),
        ExternalCommandValidator("sft-chem-inorganic-magnetic-state-009-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        unique_files,
        InorganicMagneticStateValidator(root),
    )
