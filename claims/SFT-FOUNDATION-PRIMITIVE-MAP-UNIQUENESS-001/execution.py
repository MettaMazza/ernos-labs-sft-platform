from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.primitive_map_uniqueness import PrimitiveMapUniquenessProgram
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/foundation/primitive_map_uniqueness.py",root/"claims/SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001/execution.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001/independent_validator.py";shared=root/"generated/foundation_prior_independent_validator.py";return ClaimExecution(PrimitiveMapUniquenessProgram(h),ExternalCommandValidator("sft-foundation-primitive-map-independent-python/1",(sys.executable,str(v)),root,(v,shared)),files)
