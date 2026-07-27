"""Official execution binding for SFT-CHEM-MOLECULAR-IONIZATION-ENERGY-007."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.molecular_ionization_batch_v1 import MOLECULAR_IONIZATION_SPEC
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_ionization_validation_v1 import MolecularIonizationValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/molecular_ionization_law_v1.py",
        root / "sft/chemistry/molecular_ionization_batch_v1.py",
        root / "sft/chemistry/molecular_ionization_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_molecular_ionization_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/prop-007-molecular-ionization-v1/nist-webbook-gas-phase-ion-thermochemistry.html', root / 'experiments/external_sources/chemistry/snapshots/prop-007-molecular-ionization-v1/molecular-ionization-primary-records-v1.json',
        root / 'experiments/external_sources/chemistry/molecular_ionization_target_identities_v1.json', root / 'experiments/external_sources/chemistry/molecular_ionization_withheld_targets_v1.json',
        root / "claims/SFT-CHEM-MOLECULAR-IONIZATION-ENERGY-007/execution.py",
    ) + tuple(sorted((root / "experiments/external_sources/chemistry/snapshots/prop-007-molecular-ionization-v1").glob("[0-9][0-9]-*.html")))
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MOLECULAR-IONIZATION-ENERGY-007/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MOLECULAR_IONIZATION_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-ionization-007-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularIonizationValidator(root),
    )
