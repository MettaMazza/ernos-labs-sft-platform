from pathlib import Path
import sys
import json
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
from sft.synthesis.prior_identity_laws_v1 import INPUT_PATH, SPECS, SynthesisProgram

def current_certificate(root: Path, dependency: str) -> Path:
    row = next(row for row in json.loads((root / "census/claims.json").read_text())["claims"] if row["claim_id"] == dependency)
    matches = []
    for path in sorted((root / "claims" / dependency).glob("certificate*.json")):
        if json.loads(path.read_text()).get("engine_receipt_hash") == row["receipt_hash"]:
            matches.append(path)
    if len(matches) != 1:
        raise ValueError(f"{dependency} requires exactly one current receipt-bound certificate")
    return matches[0]

def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    spec = SPECS[claim_id]
    files = (root / "sft/synthesis/prior_identity_laws_v1.py", root / "sft/synthesis/prior_identity_execution_v1.py", root / "sft/physics/structural_constants.py", INPUT_PATH, execution_file)
    files += tuple(path for dependency in spec.dependencies for path in (root / "claims" / dependency / "registration.json", current_certificate(root, dependency)))
    files = tuple(dict.fromkeys(files)); source_hash = build_source_manifest(root, files).manifest_hash; validator = root / "generated/synthesis/prior_identity_validator_v1.py"
    independent = ExternalCommandValidator("sft-cross-branch-prior-identity-independent-python/1", (sys.executable, str(validator), claim_id, str(root)), validator.parent, (validator,))
    return ClaimExecution(SynthesisProgram(spec, source_hash), independent, files)
