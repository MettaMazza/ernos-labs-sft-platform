"""Official execution binding for Chemistry INORG-007."""

from pathlib import Path
import json
import sys

from sft.chemistry.complex_spin_state_order_batch_v1 import (
    COMPLEX_SPIN_STATE_ORDER_SPEC, FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH, FAMILY_REGISTRY_PATH,
    IDENTITY_PATH, PRIMARY_PATH, TARGET_PATH,
)
from sft.chemistry.complex_spin_state_order_validation_v1 import ComplexSpinStateOrderValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path):
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    snapshot_paths = tuple(dict.fromkeys(row["snapshot_path"] for row in identities["rows"]))
    files = (
        root / "sft/chemistry/complex_spin_state_order_law_v1.py",
        root / "sft/chemistry/complex_spin_state_order_batch_v1.py",
        root / "sft/chemistry/complex_spin_state_order_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_inorg_004_017_family_sources_v1.py",
        root / "tools/build_chemistry_complex_spin_state_order_primary_v1.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        root / PRIMARY_PATH,
        *(root / path for path in snapshot_paths),
        root / "claims/SFT-CHEM-COMPLEX-SPIN-STATE-ORDER-007/execution.py",
    )
    unique_files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, unique_files).manifest_hash
    validator = root / "claims/SFT-CHEM-COMPLEX-SPIN-STATE-ORDER-007/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(COMPLEX_SPIN_STATE_ORDER_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-complex-spin-state-order-007-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        unique_files,
        ComplexSpinStateOrderValidator(root),
    )
