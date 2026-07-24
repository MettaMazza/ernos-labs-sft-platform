"""Materialize the immutable Composition and Stoichiometry batch."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.composition_stoichiometry_batch_1 import (  # noqa: E402
    COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS,
)
from tools.scaffold_chemistry_measurement_identity_batch_2 import scaffold_specs  # noqa: E402


if __name__ == "__main__":
    scaffold_specs(
        COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS,
        "sft.chemistry.composition_stoichiometry_batch_1",
        "COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS",
        "sft/chemistry/composition_stoichiometry_batch_1.py",
    )
