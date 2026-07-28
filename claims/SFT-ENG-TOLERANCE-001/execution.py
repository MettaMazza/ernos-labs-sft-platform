"""Official execution binding for SFT-ENG-TOLERANCE-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.engineering_translation.empirical_program import ENGINEERING_SPECS, BlindEngineeringBoundaryValidator, GeneratedEmpiricalEngineeringProgram
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec=next(x for x in ENGINEERING_SPECS if x.claim_id=='SFT-ENG-TOLERANCE-001')
    source_files=(root/"sft/engineering_translation/obligations.py",root/"sft/engineering_translation/structural_model.py",root/"sft/engineering_translation/generated_law.py",root/"sft/engineering_translation/empirical_program.py",root/"experiments/sealed_predictions/engineering_translation_foundation_complete_pre_source.json",root/"experiments/engineering_translation/source_registry.json",root/"experiments/engineering_translation/claim_source_bindings.json",root/"experiments/engineering_translation/source_transports.json",root/"experiments/engineering_translation/source_feature_audit.json",root/"experiments/engineering_translation/external_targets.json",root/spec.source_snapshot_path,root/"claims/SFT-ENG-TOLERANCE-001/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py")
    source_hash=build_source_manifest(root,source_files).manifest_hash
    validator=root/"claims/SFT-ENG-TOLERANCE-001/independent_validator.py"
    return ClaimExecution(program=GeneratedEmpiricalEngineeringProgram(spec,source_hash),independent_validator=ExternalCommandValidator('sft-eng-tolerance-001-independent-python/1',(sys.executable,str(validator)),validator.parent,(validator,)),source_files=source_files,empirical_validator=BlindEngineeringBoundaryValidator(root,spec))
