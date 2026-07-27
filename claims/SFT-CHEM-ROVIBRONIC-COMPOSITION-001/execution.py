"""Official execution binding for SFT-CHEM-ROVIBRONIC-COMPOSITION-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.rovibronic_composition_batch import ROVIBRONIC_COMPOSITION_SPEC
from sft.chemistry.rovibronic_composition_validation import RovibronicCompositionValidator
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = ROVIBRONIC_COMPOSITION_SPEC
    source_files = (
        root / "sft/chemistry/electronic_structure_derivation.py",
        root / "sft/chemistry/rovibronic_composition_derivation.py",
        root / "sft/chemistry/rovibronic_composition_batch.py",
        root / "sft/chemistry/rovibronic_composition_validation.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/molecular_spectroscopy_successor_laws_v1.py",
        root / "sft/physics/molecular_spectroscopy_successor_validation_v1.py",
        root / "claims/SFT-CHEM-ROVIBRONIC-COMPOSITION-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-ROVIBRONIC-COMPOSITION-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-rovibronic-composition-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=RovibronicCompositionValidator(root),
    )
