"""Official execution binding for SFT-MATH-ORDER-LATTICE-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.mathematics.order_lattice.law import SPEC
from sft.mathematics.generated_law import GeneratedMathematicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/mathematics/generated_law.py",
        root / "sft/mathematics/order_lattice/law.py",
        root / "claims/SFT-MATH-ORDER-LATTICE-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-MATH-ORDER-LATTICE-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedMathematicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-math-order-lattice-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
