from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.post_newtonian_fixed_point_terminal_law_v1 import CLAIM_ID,PostNewtonianFixedPointProgram
from sft.physics.post_newtonian_fixed_point_terminal_validation_v1 import PostNewtonianFixedPointValidator
from sft.verification import ClaimExecution
def build_post_newtonian_fixed_point_execution(root:Path,execution_file:Path)->ClaimExecution:
 files=(root/"sft/physics/post_newtonian_fixed_point_terminal_law_v1.py",root/"sft/physics/post_newtonian_fixed_point_terminal_validation_v1.py",root/"sft/physics/post_newtonian_fixed_point_terminal_execution_v1.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/canonical.py",root/"sft/engine/exact.py",root/"sft/engine/empirical.py",root/"sft/engine/isolation.py",execution_file);source_hash=build_source_manifest(root,files).manifest_hash;validator=root/"generated/physics/post_newtonian_fixed_point_terminal_validator_v1.py";return ClaimExecution(PostNewtonianFixedPointProgram(source_hash),ExternalCommandValidator("sft-physics-post-newtonian-fixed-point-independent-python/1",(sys.executable,str(validator),CLAIM_ID),validator.parent,(validator,)),files,PostNewtonianFixedPointValidator(root))
__all__=("build_post_newtonian_fixed_point_execution",)
