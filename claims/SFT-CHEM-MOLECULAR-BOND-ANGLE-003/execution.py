"""Official execution binding for SFT-CHEM-MOLECULAR-BOND-ANGLE-003."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.bond_angle_batch_v1 import BOND_ANGLE_SPEC, GeneratedFiniteBondAngleChemistryProgram
from sft.chemistry.bond_angle_validation_v1 import BondAngleValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/bond_angle_law_v1.py",
        root / "sft/chemistry/bond_angle_batch_v1.py",
        root / "sft/chemistry/bond_angle_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_bond_angle_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/prop-003-nist-cccbdb-bf3-v1.html', root / 'experiments/external_sources/chemistry/snapshots/prop-003-nist-cccbdb-xef2-v1.html', root / 'experiments/external_sources/chemistry/snapshots/prop-003-nist-cccbdb-xef4-v1.html',
        root / 'experiments/external_sources/chemistry/bond_angle_target_identities_v1.json', root / 'experiments/external_sources/chemistry/bond_angle_withheld_targets_v1.json',
        root / "claims/SFT-CHEM-MOLECULAR-BOND-ANGLE-003/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MOLECULAR-BOND-ANGLE-003/independent_validator.py"
    return ClaimExecution(
        program=GeneratedFiniteBondAngleChemistryProgram(BOND_ANGLE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-bond-angle-003-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=BondAngleValidator(root),
    )
