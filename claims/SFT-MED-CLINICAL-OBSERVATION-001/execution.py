"""Official execution binding for SFT-MED-CLINICAL-OBSERVATION-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.medicine.empirical_program import BlindMedicineAuthorityValidator, GeneratedEmpiricalMedicineProgram, MEDICINE_SPECS
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in MEDICINE_SPECS if item.claim_id == 'SFT-MED-CLINICAL-OBSERVATION-001')
    source_files = (
        root / "sft/medicine/obligations.py", root / "sft/medicine/structural_counts.py",
        root / "sft/medicine/generated_law.py", root / "sft/medicine/empirical_program.py",
        root / "sft/medicine/external_bindings.py", root / "sft/medicine/sources.py",
        root / "claims/SFT-MED-CLINICAL-OBSERVATION-001/execution.py", root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py", root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py", root / "sft/engine/isolation.py", root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-MED-CLINICAL-OBSERVATION-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalMedicineProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator('sft-med-clinical-observation-001' + "-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files,
        empirical_validator=BlindMedicineAuthorityValidator(root, spec),
    )
