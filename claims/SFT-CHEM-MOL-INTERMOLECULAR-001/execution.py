"""Official execution binding for SFT-CHEM-MOL-INTERMOLECULAR-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_goldbook_extended_law import BlindExtendedGoldBookValidator
from sft.chemistry.generated_law import GeneratedEmpiricalChemistryProgram
from sft.chemistry.molecular_structure_batch_2 import MOLECULAR_STRUCTURE_BATCH_2_SPECS
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in MOLECULAR_STRUCTURE_BATCH_2_SPECS if item.claim_id == 'SFT-CHEM-MOL-INTERMOLECULAR-001')
    source_files = (
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_goldbook_extended_law.py",
        root / "sft/chemistry/molecular_structure_derivation.py",
        root / "sft/chemistry/molecular_structure_batch_2.py",
        root / "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_pre_source.json",
        root / "experiments/sealed_predictions/chemistry_molecular_structure_batch_2_dependency_amendment.json",
        root / "claims/SFT-CHEM-MOL-INTERMOLECULAR-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MOL-INTERMOLECULAR-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalChemistryProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-chem-mol-intermolecular-001' + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindExtendedGoldBookValidator(root, spec),
    )
