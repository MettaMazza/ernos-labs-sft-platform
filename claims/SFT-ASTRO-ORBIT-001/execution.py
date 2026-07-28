"""Official execution binding for SFT-ASTRO-ORBIT-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.astronomy_cosmology.empirical_program import ASTRONOMY_SPECS, BlindAstronomyBoundaryValidator, GeneratedEmpiricalAstronomyProgram
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec=next(x for x in ASTRONOMY_SPECS if x.claim_id=='SFT-ASTRO-ORBIT-001')
    source_files=(root/"sft/astronomy_cosmology/obligations.py",root/"sft/astronomy_cosmology/structural_model.py",root/"sft/astronomy_cosmology/generated_law.py",root/"sft/astronomy_cosmology/empirical_program.py",root/"experiments/sealed_predictions/astronomy_cosmology_foundation_complete_pre_source.json",root/"experiments/astronomy_cosmology/source_registry.json",root/"experiments/astronomy_cosmology/claim_source_bindings.json",root/"experiments/astronomy_cosmology/source_transports.json",root/"experiments/astronomy_cosmology/source_feature_audit.json",root/"experiments/astronomy_cosmology/external_targets.json",root/spec.source_snapshot_path,root/"claims/SFT-ASTRO-ORBIT-001/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py")
    source_hash=build_source_manifest(root,source_files).manifest_hash
    validator=root/"claims/SFT-ASTRO-ORBIT-001/independent_validator.py"
    return ClaimExecution(program=GeneratedEmpiricalAstronomyProgram(spec,source_hash),independent_validator=ExternalCommandValidator('sft-astro-orbit-001-independent-python/1',(sys.executable,str(validator)),validator.parent,(validator,)),source_files=source_files,empirical_validator=BlindAstronomyBoundaryValidator(root,spec))
