"""Admit the pre-source-sealed Molecular Structure batch."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_structure_batch_2 import (  # noqa: E402
    MOLECULAR_STRUCTURE_BATCH_2_SPECS,
)
from tools.admit_chemistry_measurement_identity_batch_2 import admit_specs  # noqa: E402


if __name__ == "__main__":
    admit_specs(MOLECULAR_STRUCTURE_BATCH_2_SPECS)
