"""Official execution binding for SFT-CHEM-VIBRATIONAL-FREQUENCY-009."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.vibrational_frequency_batch_v1 import VIBRATIONAL_FREQUENCY_SPEC
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.vibrational_frequency_validation_v1 import VibrationalFrequencyValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/vibrational_frequency_law_v1.py",
        root / "sft/chemistry/vibrational_frequency_batch_v1.py",
        root / "sft/chemistry/vibrational_frequency_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_vibrational_frequency_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/prop-009-vibrational-frequency-v1/nist-cccbdb-complete-paired-fundamental-frequency-surface.html', root / 'experiments/external_sources/chemistry/snapshots/prop-009-vibrational-frequency-v1/vibrational-frequency-primary-records-v1.json',
        root / 'experiments/external_sources/chemistry/vibrational_frequency_target_identities_v1.json', root / 'experiments/external_sources/chemistry/vibrational_frequency_withheld_targets_v1.json',
        root / "claims/SFT-CHEM-VIBRATIONAL-FREQUENCY-009/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-VIBRATIONAL-FREQUENCY-009/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(VIBRATIONAL_FREQUENCY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-vibrational-frequency-009-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=VibrationalFrequencyValidator(root),
    )
