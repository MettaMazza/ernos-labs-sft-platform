"""Admit the second immutable Elements and Periodicity batch."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.elements_periodicity_batch_2 import (  # noqa: E402
    ELEMENTS_PERIODICITY_BATCH_2_SPECS,
)
from tools.admit_chemistry_measurement_identity_batch_2 import admit_specs  # noqa: E402


if __name__ == "__main__":
    admit_specs(ELEMENTS_PERIODICITY_BATCH_2_SPECS)
