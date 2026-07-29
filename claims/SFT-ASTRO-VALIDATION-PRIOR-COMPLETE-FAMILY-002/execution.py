from pathlib import Path
from sft.astronomy.prior_return_execution_v1 import build_execution as _build
def build_execution(root: Path): return _build(root,"SFT-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002",Path(__file__).resolve())
