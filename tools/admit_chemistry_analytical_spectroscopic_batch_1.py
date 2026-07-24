from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.analytical_spectroscopic_batch_1 import ANALYTICAL_SPECTROSCOPIC_BATCH_1_SPECS  # noqa:E402
from tools.admit_chemistry_measurement_identity_batch_2 import admit_specs  # noqa:E402


if __name__ == "__main__":
    admit_specs(ANALYTICAL_SPECTROSCOPIC_BATCH_1_SPECS)
