"""Official execution binding for Chemistry INORG-008."""

from pathlib import Path
import json
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.inorganic_colour_transition_batch_v1 import (
    ADDENDUM_PATH, FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH, FAMILY_REGISTRY_PATH,
    IDENTITY_PATH, INORGANIC_COLOUR_TRANSITION_SPEC, PRIMARY_PATH, SHARED_TARGET_PATH, TARGET_PATH,
)
from sft.chemistry.inorganic_colour_transition_validation_v1 import InorganicColourTransitionValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path):
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    snapshot_paths = tuple(dict.fromkeys(row["snapshot_path"] for row in identities["rows"]))
    files = (
        root / "sft/chemistry/inorganic_colour_transition_law_v1.py",
        root / "sft/chemistry/inorganic_colour_transition_batch_v1.py",
        root / "sft/chemistry/inorganic_colour_transition_validation_v1.py",
        root / "sft/chemistry/generated_law.py", root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/build_chemistry_inorganic_colour_transition_primary_v1.py",
        root / FAMILY_BOUNDARY_PATH, root / FAMILY_REGISTRY_PATH, root / FAMILY_INVENTORY_PATH,
        root / ADDENDUM_PATH, root / IDENTITY_PATH, root / TARGET_PATH, root / PRIMARY_PATH,
        root / SHARED_TARGET_PATH, *(root / path for path in snapshot_paths),
        root / "claims/SFT-CHEM-INORGANIC-COLOUR-ELECTRONIC-TRANSITION-008/execution.py",
    )
    unique_files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, unique_files).manifest_hash
    validator = root / "claims/SFT-CHEM-INORGANIC-COLOUR-ELECTRONIC-TRANSITION-008/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(INORGANIC_COLOUR_TRANSITION_SPEC, source_hash),
        ExternalCommandValidator("sft-chem-inorganic-colour-transition-008-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        unique_files,
        InorganicColourTransitionValidator(root),
    )
