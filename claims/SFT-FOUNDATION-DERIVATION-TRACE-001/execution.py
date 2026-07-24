from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.derivation_trace import DerivationTraceProgram
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/foundation/derivation_trace.py",root/"claims/SFT-FOUNDATION-DERIVATION-TRACE-001/execution.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-FOUNDATION-DERIVATION-TRACE-001/independent_validator.py";shared=root/"generated/foundation_prior_independent_validator.py";return ClaimExecution(DerivationTraceProgram(h),ExternalCommandValidator("sft-foundation-derivation-trace-independent-python/1",(sys.executable,str(v)),root,(v,shared)),files)
