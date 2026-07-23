from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.measurement_boundary import MeasurementBoundaryProgram
from sft.verification import ClaimExecution
def build_execution(root:Path):
 f=(root/"sft/foundation/measurement_boundary.py",root/"claims/SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001/execution.py");h=build_source_manifest(root,f).manifest_hash;v=root/"claims/SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001/independent_validator.py";return ClaimExecution(MeasurementBoundaryProgram(h),ExternalCommandValidator("sft-measurement-boundary-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),f)
