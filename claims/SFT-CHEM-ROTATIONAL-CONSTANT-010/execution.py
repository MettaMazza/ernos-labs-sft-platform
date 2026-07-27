"""Official execution binding for SFT-CHEM-ROTATIONAL-CONSTANT-010."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.rotational_constant_batch_v1 import ROTATIONAL_CONSTANT_SPEC
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.rotational_constant_validation_v1 import RotationalConstantValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/rotational_constant_law_v1.py",
        root / "sft/chemistry/rotational_constant_batch_v1.py",
        root / "sft/chemistry/rotational_constant_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_rotational_constant_sources_v1.py",
        root / 'experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1/nist-cccbdb-complete-species-list.html', root / 'experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1/nist-cccbdb-complete-rotational-choice-surface.html',
        root / 'experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1/nist-cccbdb-complete-rotational-constant-surface.html', root / 'experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1/rotational-constant-primary-records-v1.json',
        root / 'experiments/external_sources/chemistry/rotational_constant_target_identities_v1.json', root / 'experiments/external_sources/chemistry/rotational_constant_withheld_targets_v1.json',
        root / "claims/SFT-CHEM-ROTATIONAL-CONSTANT-010/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-ROTATIONAL-CONSTANT-010/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(ROTATIONAL_CONSTANT_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-rotational-constant-010-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=RotationalConstantValidator(root),
    )
