"""Official execution binding for SFT-CHEM-MOLECULAR-POLARIZABILITY-006."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.molecular_polarizability_batch_v1 import MOLECULAR_POLARIZABILITY_SPEC
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_polarizability_validation_v1 import MolecularPolarizabilityValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/molecular_polarizability_law_v1.py",
        root / "sft/chemistry/molecular_polarizability_batch_v1.py",
        root / "sft/chemistry/molecular_polarizability_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_molecular_polarizability_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/prop-006-nist-cccbdb-experimental-polarizabilities-v1.html', root / 'experiments/external_sources/chemistry/snapshots/prop-006-molecular-polarizability-primary-records-v1.json',
        root / 'experiments/external_sources/chemistry/molecular_polarizability_target_identities_v1.json', root / 'experiments/external_sources/chemistry/molecular_polarizability_withheld_targets_v1.json',
        root / "claims/SFT-CHEM-MOLECULAR-POLARIZABILITY-006/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MOLECULAR-POLARIZABILITY-006/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MOLECULAR_POLARIZABILITY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-polarizability-006-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularPolarizabilityValidator(root),
    )
