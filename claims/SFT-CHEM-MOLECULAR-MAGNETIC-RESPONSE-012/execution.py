"""Official execution binding for SFT-CHEM-MOLECULAR-MAGNETIC-RESPONSE-012."""
from pathlib import Path
import json
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.magnetic_response_batch_v1 import (
    MAGNETIC_RESPONSE_SPEC, PRIMARY_PATH, RESOLUTION_PATH,
    DIATOMIC_HOLDINGS_PATH, TRIATOMIC_HOLDINGS_PATH, HYDROCARBON_HOLDINGS_PATH,
    DIATOMIC_PDF_PATH, DIATOMIC_TEXT_PATH, IDENTITY_PATH, TARGET_PATH,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.magnetic_response_validation_v1 import MagneticResponseValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    primary = json.loads((root / PRIMARY_PATH).read_text(encoding="utf-8"))
    constants_pages = tuple(
        root / row["snapshot_path"] for row in primary["complete_constants_page_manifest"]
        if row["snapshot_path"] is not None
    )
    source_files = (
        root / "sft/chemistry/magnetic_response_law_v1.py",
        root / "sft/chemistry/magnetic_response_batch_v1.py",
        root / "sft/chemistry/magnetic_response_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_magnetic_response_sources_v1.py",
        root / RESOLUTION_PATH,
        root / DIATOMIC_HOLDINGS_PATH, root / TRIATOMIC_HOLDINGS_PATH, root / HYDROCARBON_HOLDINGS_PATH,
        *constants_pages,
        root / DIATOMIC_PDF_PATH, root / DIATOMIC_TEXT_PATH,
        root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / "claims/SFT-CHEM-MOLECULAR-MAGNETIC-RESPONSE-012/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MOLECULAR-MAGNETIC-RESPONSE-012/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MAGNETIC_RESPONSE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-magnetic-response-012-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MagneticResponseValidator(root),
    )
