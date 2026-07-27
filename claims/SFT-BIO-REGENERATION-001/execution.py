"""Official execution binding for SFT-BIO-REGENERATION-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.biology.generated_law import BlindBiologyAuthorityValidator, GeneratedEmpiricalBiologyProgram, BIOLOGY_SPECS
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in BIOLOGY_SPECS if item.claim_id == 'SFT-BIO-REGENERATION-001')
    source_files = (
        root / "sft/biology/obligations.py", root / "sft/biology/structural_counts.py",
        root / "sft/biology/derivation.py", root / "sft/biology/generated_law.py",
        root / "sft/biology/external_bindings.py", root / "sft/biology/sources.py",
        root / "claims/SFT-BIO-REGENERATION-001/execution.py", root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py", root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py", root / "sft/engine/isolation.py", root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-BIO-REGENERATION-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalBiologyProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator('sft-bio-regeneration-001' + "-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files,
        empirical_validator=BlindBiologyAuthorityValidator(root, spec),
    )
