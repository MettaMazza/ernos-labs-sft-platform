from pathlib import Path
import json
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.grand_lock_terminal_law_v1 import CLAIM_ID, INPUT_PATH, SPEC
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path):
    record = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    fixed = (
        root / "sft/physics/grand_lock_terminal_law_v1.py",
        root / "sft/physics/grand_lock_terminal_execution_v1.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/cosmology_prior_value_laws.py",
        root / "sft/physics/hubble_calibration_law.py",
        root / "sft/physics/matter_flavour_laws_v1.py",
        root / "sft/physics/precision_value_laws_v1.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/terminal_lepton_law.py",
        root / "sft/physics/vacuum_density_scale_terminal_law_v1.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        INPUT_PATH,
        execution_file,
    )
    evidence = []
    for row in record["dependency_dictionary"]:
        evidence.append(root / row["registration_path"])
    for row in record["physics_claims"]:
        evidence.extend((root / row["receipt_path"], root / row["certificate_path"]))
    files = tuple(dict.fromkeys(fixed + tuple(evidence)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/grand_lock_terminal_validator_v1.py"
    return ClaimExecution(
        StructuralPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator(
            "sft-physics-grand-lock-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID, str(INPUT_PATH), str(root)),
            validator.parent,
            (validator,),
        ),
        files,
    )


__all__ = ("build_execution",)
