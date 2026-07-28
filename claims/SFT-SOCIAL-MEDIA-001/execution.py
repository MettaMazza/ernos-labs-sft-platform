"""Official execution binding for SFT-SOCIAL-MEDIA-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.social_collective_systems.empirical_program import SOCIAL_SPECS, BlindSocialBoundaryValidator, GeneratedEmpiricalSocialProgram
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec=next(x for x in SOCIAL_SPECS if x.claim_id=='SFT-SOCIAL-MEDIA-001')
    source_files=(root/"sft/social_collective_systems/obligations.py",root/"sft/social_collective_systems/structural_model.py",root/"sft/social_collective_systems/generated_law.py",root/"sft/social_collective_systems/empirical_program.py",root/"experiments/sealed_predictions/social_collective_foundation_complete_pre_source.json",root/"experiments/social_collective_systems/source_registry.json",root/"experiments/social_collective_systems/claim_source_bindings.json",root/"experiments/social_collective_systems/source_transports.json",root/"experiments/social_collective_systems/source_feature_audit.json",root/"experiments/social_collective_systems/external_targets.json",root/spec.source_snapshot_path,root/"claims/SFT-SOCIAL-MEDIA-001/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py")
    source_hash=build_source_manifest(root,source_files).manifest_hash
    validator=root/"claims/SFT-SOCIAL-MEDIA-001/independent_validator.py"
    return ClaimExecution(program=GeneratedEmpiricalSocialProgram(spec,source_hash),independent_validator=ExternalCommandValidator('sft-social-media-001-independent-python/1',(sys.executable,str(validator)),validator.parent,(validator,)),source_files=source_files,empirical_validator=BlindSocialBoundaryValidator(root,spec))
