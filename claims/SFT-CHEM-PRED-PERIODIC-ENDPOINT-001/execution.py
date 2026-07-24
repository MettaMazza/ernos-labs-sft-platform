"""Official execution binding for SFT-CHEM-PRED-PERIODIC-ENDPOINT-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.gblock_predictions import GBLOCK_PREDICTION_SPECS
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.chemistry.generated_periodic_law import BlindPeriodicChemistryValidator
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in GBLOCK_PREDICTION_SPECS if item.claim_id == 'SFT-CHEM-PRED-PERIODIC-ENDPOINT-001')
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_periodic_law.py",
        root / "sft/chemistry/gblock_predictions.py",
        root / "sft/physics/atomic_constants.py",
        root / "claims/SFT-CHEM-PRED-PERIODIC-ENDPOINT-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-PRED-PERIODIC-ENDPOINT-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-chem-pred-periodic-endpoint-001' + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindPeriodicChemistryValidator(root, spec),
    )
