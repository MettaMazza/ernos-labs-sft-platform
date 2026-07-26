from pathlib import Path
import json
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.grand_lock_empirical_v1 import CLAIM_ID, ObservationalGrandLockProgram, SOURCE_PATH, SPEC
from sft.physics.grand_lock_empirical_validation_v1 import GrandLockEmpiricalValidator
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path):
    source = root / SOURCE_PATH
    record = json.loads(source.read_text(encoding="utf-8"))
    fixed = (
        root / "sft/physics/grand_lock_empirical_v1.py",
        root / "sft/physics/grand_lock_empirical_validation_v1.py",
        root / "sft/physics/grand_lock_empirical_execution_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        root / "sft/engine/empirical.py",
        root / "sft/engine/isolation.py",
        source,
        root / record["prelock_input_path"],
        root / record["formal_grand_lock"]["receipt_path"],
        execution_file,
    )
    evidence = []
    for row in record["empirical_claims"]:
        evidence.extend((root / row["receipt_path"], root / row["certificate_path"]))
    files = tuple(dict.fromkeys(fixed + tuple(evidence)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/grand_lock_empirical_validator_v1.py"
    return ClaimExecution(
        ObservationalGrandLockProgram(SPEC, source_hash),
        ExternalCommandValidator(
            "sft-physics-grand-lock-empirical-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID, str(source), str(root)),
            validator.parent,
            (validator,),
        ),
        files,
        GrandLockEmpiricalValidator(root, SPEC),
    )


__all__ = ("build_execution",)
