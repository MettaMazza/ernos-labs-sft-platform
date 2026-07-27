"""Official execution binding for SFT-CHEM-AB-PROTON-TRANSFER-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.acid_base_batch_1 import ACID_BASE_BATCH_1_SPECS
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.chemistry.generated_multi_source_law import BlindMultiSourceAuthorityValidator
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in ACID_BASE_BATCH_1_SPECS if item.claim_id == 'SFT-CHEM-AB-PROTON-TRANSFER-001')
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_multi_source_law.py",
        root / "sft/chemistry/acid_base_derivation.py",
        root / "sft/chemistry/acid_base_batch_1.py",
        root / "experiments/sealed_predictions/chemistry_acid_base_batch_1_pre_source.json",
        root / "claims/SFT-CHEM-AB-PROTON-TRANSFER-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-AB-PROTON-TRANSFER-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-chem-ab-proton-transfer-001' + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindMultiSourceAuthorityValidator(root, spec),
    )
