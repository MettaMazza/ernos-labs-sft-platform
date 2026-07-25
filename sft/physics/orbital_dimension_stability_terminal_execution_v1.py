from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.orbital_dimension_stability_terminal_law_v1 import CLAIM_ID,OrbitalDimensionStabilityProgram
from sft.physics.orbital_dimension_stability_terminal_validation_v1 import OrbitalDimensionStabilityValidator
from sft.verification import ClaimExecution
def build_orbital_dimension_stability_execution(root:Path,execution_file:Path)->ClaimExecution:
 files=(root/"sft/physics/orbital_dimension_stability_terminal_law_v1.py",root/"sft/physics/orbital_dimension_stability_terminal_validation_v1.py",root/"sft/physics/orbital_dimension_stability_terminal_execution_v1.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/canonical.py",root/"sft/engine/exact.py",root/"sft/engine/empirical.py",root/"sft/engine/isolation.py",execution_file);h=build_source_manifest(root,files).manifest_hash;v=root/"generated/physics/orbital_dimension_stability_terminal_validator_v1.py";return ClaimExecution(OrbitalDimensionStabilityProgram(h),ExternalCommandValidator("sft-physics-orbital-dimension-stability-independent-python/1",(sys.executable,str(v),CLAIM_ID),v.parent,(v,)),files,OrbitalDimensionStabilityValidator(root))
__all__=("build_orbital_dimension_stability_execution",)
