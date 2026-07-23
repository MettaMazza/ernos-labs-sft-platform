from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.form_enforcement import FormEnforcementProgram
from sft.verification import ClaimExecution
def build_execution(root:Path):
 f=(root/"sft/foundation/form_enforcement.py",root/"claims/SFT-FOUNDATION-FORM-ENFORCEMENT-001/execution.py");h=build_source_manifest(root,f).manifest_hash;v=root/"claims/SFT-FOUNDATION-FORM-ENFORCEMENT-001/independent_validator.py";return ClaimExecution(FormEnforcementProgram(h),ExternalCommandValidator("sft-form-enforcement-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),f)
