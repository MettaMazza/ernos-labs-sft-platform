"""Official execution binding for SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.entropy_multiplicity_correspondence_batch_v1 import ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC
from sft.chemistry.entropy_multiplicity_correspondence_validation_v1 import EntropyMultiplicityCorrespondenceValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.internal_energy_composition_batch_v1 import SNAPSHOT_PATH, PRIMARY_PATH, IDENTITY_PATH, TARGET_PATH
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/entropy_multiplicity_correspondence_law_v1.py",
        root / "sft/chemistry/entropy_multiplicity_correspondence_batch_v1.py",
        root / "sft/chemistry/entropy_multiplicity_correspondence_validation_v1.py",
        root / "sft/chemistry/internal_energy_composition_batch_v1.py",
        root / "sft/chemistry/internal_energy_composition_validation_v1.py",
        root / "sft/information_science/entropy_uncertainty/law.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_thermophysical_state_sources_v1.py",
        root / SNAPSHOT_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / "claims/SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(ENTROPY_MULTIPLICITY_CORRESPONDENCE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-entropy-multiplicity-correspondence-005-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=EntropyMultiplicityCorrespondenceValidator(root),
    )
