"""Admit the pre-source-sealed first acid/base batch."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.acid_base_batch_1 import ACID_BASE_BATCH_1_SPECS  # noqa: E402
from tools.admit_chemistry_measurement_identity_batch_2 import admit_specs  # noqa: E402


if __name__ == "__main__":
    admit_specs(ACID_BASE_BATCH_1_SPECS)
