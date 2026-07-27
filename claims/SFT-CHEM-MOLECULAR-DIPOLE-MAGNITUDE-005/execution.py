"""Official execution binding for SFT-CHEM-MOLECULAR-DIPOLE-MAGNITUDE-005."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.molecular_dipole_batch_v1 import MOLECULAR_DIPOLE_SPEC, GeneratedFiniteMolecularDipoleChemistryProgram
from sft.chemistry.molecular_dipole_validation_v1 import MolecularDipoleValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/molecular_dipole_law_v1.py",
        root / "sft/chemistry/molecular_dipole_batch_v1.py",
        root / "sft/chemistry/molecular_dipole_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_molecular_dipole_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/prop-005-nist-water-dipole-1973-v1.pdf', root / 'experiments/external_sources/chemistry/snapshots/prop-005-nist-cccbdb-experimental-dipoles-v1.html', root / 'experiments/external_sources/chemistry/snapshots/prop-005-molecular-dipole-primary-records-v1.json',
        root / 'experiments/external_sources/chemistry/molecular_dipole_target_identities_v1.json', root / 'experiments/external_sources/chemistry/molecular_dipole_withheld_targets_v1.json',
        root / "claims/SFT-CHEM-MOLECULAR-DIPOLE-MAGNITUDE-005/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MOLECULAR-DIPOLE-MAGNITUDE-005/independent_validator.py"
    return ClaimExecution(
        program=GeneratedFiniteMolecularDipoleChemistryProgram(MOLECULAR_DIPOLE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-dipole-005-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularDipoleValidator(root),
    )
