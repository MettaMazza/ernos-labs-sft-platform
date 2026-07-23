from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.fold_assembly import FoldAssemblyProgram
from sft.verification import ClaimExecution
def build_execution(root:Path):
    files=(root/"sft/foundation/fold_assembly.py",root/"claims/SFT-FOUNDATION-FOLD-ASSEMBLY-001/execution.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-FOUNDATION-FOLD-ASSEMBLY-001/independent_validator.py";return ClaimExecution(FoldAssemblyProgram(h),ExternalCommandValidator("sft-fold-assembly-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),files)
