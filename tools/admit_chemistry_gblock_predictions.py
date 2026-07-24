"""Admit the clean V3 g-block prediction chain in dependency order."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.gblock_predictions import GBLOCK_PREDICTION_SPECS  # noqa: E402
from tools.admit_chemistry_measurement_identity_batch_2 import admit_specs  # noqa: E402


if __name__ == "__main__":
    admit_specs(GBLOCK_PREDICTION_SPECS)
