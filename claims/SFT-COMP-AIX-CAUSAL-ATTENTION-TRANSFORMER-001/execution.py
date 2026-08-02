"""Official execution binding for the exact SFT causal attention-transformer law."""

from pathlib import Path
import sys

from sft.computation.aix_001_002_laws_v1 import ATTENTION_SPEC
from sft.computation.generated_law import GeneratedComputationProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "census/computation_aix_001_002_target_registry_v1.json",
        root / "sft/computation/generated_law.py",
        root / "sft/computation/aix_001_002_laws_v1.py",
        root / "claims/SFT-COMP-AIX-CAUSAL-ATTENTION-TRANSFORMER-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-COMP-AIX-CAUSAL-ATTENTION-TRANSFORMER-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedComputationProgram(ATTENTION_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-comp-aix-causal-attention-transformer-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )

