"""Official execution binding for SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.dihedral_torsion_batch_v1 import DIHEDRAL_TORSION_SPEC, GeneratedFiniteDihedralTorsionChemistryProgram
from sft.chemistry.dihedral_torsion_validation_v1 import DihedralTorsionValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/dihedral_torsion_law_v1.py",
        root / "sft/chemistry/dihedral_torsion_batch_v1.py",
        root / "sft/chemistry/dihedral_torsion_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_dihedral_torsion_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/configuration-order-v1/nist-cccbdb-ethanol-experimental-rotational-barrier.html', root / 'experiments/external_sources/chemistry/dihedral_torsion_target_identities_v1.json', root / 'experiments/external_sources/chemistry/dihedral_torsion_withheld_targets_v1.json',
        root / "claims/SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004/independent_validator.py"
    return ClaimExecution(
        program=GeneratedFiniteDihedralTorsionChemistryProgram(DIHEDRAL_TORSION_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-dihedral-torsional-state-004-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=DihedralTorsionValidator(root),
    )
