from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.fold_dynamics import FoldDynamicsProgram
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/foundation/fold_dynamics.py",root/"claims/SFT-FOUNDATION-FOLD-DYNAMICS-001/execution.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-FOUNDATION-FOLD-DYNAMICS-001/independent_validator.py";shared=root/"generated/foundation_prior_independent_validator.py";return ClaimExecution(FoldDynamicsProgram(h),ExternalCommandValidator("sft-foundation-fold-dynamics-independent-python/1",(sys.executable,str(v)),root,(v,shared)),files)
