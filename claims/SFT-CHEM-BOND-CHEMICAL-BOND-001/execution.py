"""Official execution binding for SFT-CHEM-BOND-CHEMICAL-BOND-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.bonding_molecular_batch_1 import BONDING_MOLECULAR_BATCH_1_SPECS
from sft.chemistry.generated_goldbook_extended_law import BlindExtendedGoldBookValidator
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in BONDING_MOLECULAR_BATCH_1_SPECS if item.claim_id == 'SFT-CHEM-BOND-CHEMICAL-BOND-001')
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_goldbook_extended_law.py",
        root / "sft/chemistry/bonding_molecular_batch_1.py",
        root / "claims/SFT-CHEM-BOND-CHEMICAL-BOND-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-BOND-CHEMICAL-BOND-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-chem-bond-chemical-bond-001' + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindExtendedGoldBookValidator(root, spec),
    )
