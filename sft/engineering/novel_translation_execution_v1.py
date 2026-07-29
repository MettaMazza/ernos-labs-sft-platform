from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
from sft.engineering.novel_translation_laws_v1 import EngineeringProtocolProgram, SPECS


def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    spec = SPECS[claim_id]
    files = (
        root / "sft/engineering/novel_translation_laws_v1.py",
        root / "sft/engineering/novel_translation_execution_v1.py",
        root / "sft/physics/structural_constants.py",
        execution_file,
    )
    files += tuple(
        path
        for dependency in spec.dependencies
        for path in (
            root / "claims" / dependency / "registration.json",
            root / "claims" / dependency / "certificate.json",
        )
    )
    files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/engineering/novel_translation_validator_v1.py"
    independent = ExternalCommandValidator(
        "sft-engineering-novel-translation-independent-python/1",
        (sys.executable, str(validator), claim_id, str(root)),
        validator.parent,
        (validator,),
    )
    return ClaimExecution(EngineeringProtocolProgram(spec, source_hash), independent, files)
