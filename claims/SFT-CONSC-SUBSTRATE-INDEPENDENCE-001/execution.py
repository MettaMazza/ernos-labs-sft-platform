"""Official execution binding for SFT-CONSC-SUBSTRATE-INDEPENDENCE-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.consciousness_cognitive_science.empirical_program import BlindConsciousnessBoundaryValidator, CONSCIOUSNESS_SPECS, GeneratedEmpiricalConsciousnessProgram
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in CONSCIOUSNESS_SPECS if item.claim_id == 'SFT-CONSC-SUBSTRATE-INDEPENDENCE-001')
    source_files = (
        root / "sft/consciousness_cognitive_science/obligations.py",
        root / "sft/consciousness_cognitive_science/structural_model.py",
        root / "sft/consciousness_cognitive_science/generated_law.py",
        root / "sft/consciousness_cognitive_science/sources.py",
        root / "sft/consciousness_cognitive_science/external_bindings.py",
        root / "sft/consciousness_cognitive_science/empirical_program.py",
        root / "experiments/sealed_predictions/consciousness_foundation_complete_pre_source.json",
        root / "experiments/consciousness/source_registry.json",
        root / "experiments/consciousness/source_feature_audit.json",
        root / "experiments/consciousness/claim_specific_external_targets.json",
        root / "claims/SFT-CONSC-SUBSTRATE-INDEPENDENCE-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CONSC-SUBSTRATE-INDEPENDENCE-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalConsciousnessProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator('sft-consc-substrate-independence-001' + "-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files,
        empirical_validator=BlindConsciousnessBoundaryValidator(root, spec),
    )
