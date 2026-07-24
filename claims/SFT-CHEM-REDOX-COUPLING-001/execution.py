"""Official execution binding for SFT-CHEM-REDOX-COUPLING-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.chemistry.generated_multi_source_law import BlindMultiSourceAuthorityValidator
from sft.chemistry.redox_batch_1 import REDOX_BATCH_1_SPECS
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in REDOX_BATCH_1_SPECS if item.claim_id == 'SFT-CHEM-REDOX-COUPLING-001')
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_multi_source_law.py",
        root / "sft/chemistry/redox_derivation.py",
        root / "sft/chemistry/redox_batch_1.py",
        root / "experiments/sealed_predictions/chemistry_redox_batch_1_pre_source.json",
        root / "claims/SFT-CHEM-REDOX-COUPLING-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-REDOX-COUPLING-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator('sft-chem-redox-coupling-001' + "-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files,
        empirical_validator=BlindMultiSourceAuthorityValidator(root, spec),
    )
