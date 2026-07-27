"""Official execution binding for SFT-CHEM-ELECTRON-COUNT-SPIN-002."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.electron_count_spin_batch_v1 import ELECTRON_COUNT_SPIN_SPEC
from sft.chemistry.electron_count_spin_validation_v1 import ElectronCountSpinValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = ELECTRON_COUNT_SPIN_SPEC
    source_files = (
        root / "sft/chemistry/electronic_structure_derivation.py",
        root / "sft/chemistry/electron_count_spin_law_v1.py",
        root / "sft/chemistry/electron_count_spin_batch_v1.py",
        root / "sft/chemistry/electron_count_spin_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "claims/SFT-CHEM-ELECTRON-COUNT-SPIN-002/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-ELECTRON-COUNT-SPIN-002/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-electron-count-spin-002-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=ElectronCountSpinValidator(root),
    )
