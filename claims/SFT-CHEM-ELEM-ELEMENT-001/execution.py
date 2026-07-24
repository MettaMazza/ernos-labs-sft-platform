"""Official execution binding for SFT-CHEM-ELEM-ELEMENT-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.elements_periodicity_batch_1 import ELEMENTS_PERIODICITY_BATCH_1_SPECS
from sft.chemistry.generated_law import BlindExternalChemistryValidator, GeneratedEmpiricalChemistryProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in ELEMENTS_PERIODICITY_BATCH_1_SPECS if item.claim_id == 'SFT-CHEM-ELEM-ELEMENT-001')
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / 'sft/chemistry/elements_periodicity_batch_1.py',
        root / "claims/SFT-CHEM-ELEM-ELEMENT-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-ELEM-ELEMENT-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-chem-elem-element-001' + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindExternalChemistryValidator(root, spec),
    )
