"""Official execution binding for SFT-CHEM-MEAS-CHEMICAL-SPECIES-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.catalog import CHEMISTRY_SPECS
from sft.chemistry.generated_law import BlindExternalChemistryValidator, GeneratedEmpiricalChemistryProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in CHEMISTRY_SPECS if item.claim_id == 'SFT-CHEM-MEAS-CHEMICAL-SPECIES-001')
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/catalog.py",
        root / "sft/chemistry/obligations.py",
        root / "claims/SFT-CHEM-MEAS-CHEMICAL-SPECIES-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MEAS-CHEMICAL-SPECIES-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-chem-meas-chemical-species-001' + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindExternalChemistryValidator(root, spec),
    )
