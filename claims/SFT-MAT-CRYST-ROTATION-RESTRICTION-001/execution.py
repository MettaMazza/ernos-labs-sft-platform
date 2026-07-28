"""Official execution binding for SFT-MAT-CRYST-ROTATION-RESTRICTION-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.materials.generated_law import BlindMaterialsAuthorityValidator, GeneratedEmpiricalMaterialsProgram, MATERIALS_SPECS
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in MATERIALS_SPECS if item.claim_id == 'SFT-MAT-CRYST-ROTATION-RESTRICTION-001')
    source_files = (
        root / "sft/materials/obligations.py",
        root / "sft/materials/structural_counts.py",
        root / "sft/materials/derivation.py",
        root / "sft/materials/generated_law.py",
        root / "sft/materials/external_bindings.py",
        root / "sft/materials/sources.py",
        root / "claims/SFT-MAT-CRYST-ROTATION-RESTRICTION-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-MAT-CRYST-ROTATION-RESTRICTION-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalMaterialsProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-mat-cryst-rotation-restriction-001' + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindMaterialsAuthorityValidator(root, spec),
    )
