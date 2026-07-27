"""Official execution binding for SFT-CHEM-VISCOUS-TRANSPORT-RELATION-017."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.viscous_transport_batch_v1 import IDENTITY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH, VISCOUS_TRANSPORT_SPEC
from sft.chemistry.viscous_transport_validation_v1 import ViscousTransportValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/viscous_transport_law_v1.py", root / "sft/chemistry/viscous_transport_batch_v1.py",
        root / "sft/chemistry/viscous_transport_validation_v1.py", root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py", root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_viscous_transport_sources_v1.py", root / SPEC_PATH, root / PRIMARY_PATH,
        root / IDENTITY_PATH, root / TARGET_PATH, *(root / path for path, _hash in SOURCE_FILES),
        root / "claims/SFT-CHEM-VISCOUS-TRANSPORT-RELATION-017/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-VISCOUS-TRANSPORT-RELATION-017/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(VISCOUS_TRANSPORT_SPEC, source_hash),
        independent_validator=ExternalCommandValidator("sft-chem-viscous-transport-017-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files, empirical_validator=ViscousTransportValidator(root),
    )
