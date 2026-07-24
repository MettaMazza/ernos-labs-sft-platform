from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.half_one import HalfOneProgram
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/foundation/half_one.py",root/"claims/SFT-FOUNDATION-HALF-ONE-001/execution.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-FOUNDATION-HALF-ONE-001/independent_validator.py";shared=root/"generated/foundation_prior_independent_validator.py";return ClaimExecution(HalfOneProgram(h),ExternalCommandValidator("sft-foundation-half-one-independent-python/1",(sys.executable,str(v)),root,(v,shared)),files)
