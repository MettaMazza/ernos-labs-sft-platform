"""Official execution binding for SFT-EARTH-STATE-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.earth_environment.empirical_program import BlindEarthBoundaryValidator, EARTH_SPECS, GeneratedEmpiricalEarthProgram
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in EARTH_SPECS if item.claim_id == 'SFT-EARTH-STATE-001')
    source_files = (
        root / "sft/earth_environment/obligations.py",
        root / "sft/earth_environment/structural_model.py",
        root / "sft/earth_environment/generated_law.py",
        root / "sft/earth_environment/external_bindings.py",
        root / "sft/earth_environment/empirical_program.py",
        root / "experiments/sealed_predictions/earth_environment_foundation_complete_pre_source.json",
        root / "experiments/earth_environment/source_registry.json",
        root / "experiments/earth_environment/claim_source_bindings.json",
        root / "experiments/earth_environment/source_feature_audit.json",
        root / "experiments/earth_environment/claim_specific_external_targets.json",
        root / "experiments/earth_environment/quake_magnitude_frequency_protocol.json",
        root / "experiments/earth_environment/quake_magnitude_frequency_result.json",
        root / "experiments/earth_environment/quake_magnitude_frequency_holdout_protocol_v2.json",
        root / "experiments/earth_environment/quake_magnitude_frequency_holdout_result_v2.json",
        root / "claims/SFT-EARTH-STATE-001/execution.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-EARTH-STATE-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalEarthProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator('sft-earth-state-001' + "-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files,
        empirical_validator=BlindEarthBoundaryValidator(root, spec),
    )
