from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.exact_operations import ExactOperationsProgram
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/foundation/exact_operations.py",root/"claims/SFT-FOUNDATION-EXACT-OPERATIONS-001/execution.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-FOUNDATION-EXACT-OPERATIONS-001/independent_validator.py";shared=root/"generated/foundation_prior_independent_validator.py";return ClaimExecution(ExactOperationsProgram(h),ExternalCommandValidator("sft-foundation-exact-operations-independent-python/1",(sys.executable,str(v)),root,(v,shared)),files)
