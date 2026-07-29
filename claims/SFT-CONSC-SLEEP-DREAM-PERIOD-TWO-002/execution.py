from pathlib import Path
from sft.consciousness.nonordinary_execution_v1 import build_execution as _build


def build_execution(root: Path):
    return _build(root, "SFT-CONSC-SLEEP-DREAM-PERIOD-TWO-002", Path(__file__).resolve())
