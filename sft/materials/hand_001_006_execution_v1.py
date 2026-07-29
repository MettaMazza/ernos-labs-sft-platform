import json
import sys
from pathlib import Path
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
from sft.materials.hand_001_006_laws_v1 import REGISTRY_PATH, SPECS, HandoffProgram
from sft.materials.hand_001_006_external_v1 import MaterialsHandoffValidator, VECTOR


def current_certificate(root, cid):
    row = next(item for item in json.loads((root / "census/claims.json").read_text())["claims"] if item["claim_id"] == cid)
    matches = [path for path in sorted((root / "claims" / cid).glob("certificate*.json")) if json.loads(path.read_text()).get("engine_receipt_hash") == row["receipt_hash"]]
    if len(matches) != 1: raise ValueError(f"{cid} current certificate count {len(matches)}")
    return matches[0]


def build_execution(root: Path, cid: str, execution_file: Path):
    spec = SPECS[cid]
    common = (root / "sft/materials/hand_001_006_laws_v1.py", root / "sft/materials/hand_001_006_external_v1.py", root / "sft/materials/hand_001_006_execution_v1.py", root / "sft/physics/structural_constants.py", REGISTRY_PATH, root / VECTOR, execution_file)
    files = list(common)
    vector = json.loads((root / VECTOR).read_text())
    if spec.number == "006":
        registry = json.loads(REGISTRY_PATH.read_text())
        files.extend(root / row["registration_path"] for row in registry["complete_owner_dependency_graph"])
    else:
        for row in vector["paired_records"][spec.number]:
            files.extend(root / row[name + "_path"] for name in ("registration", "certificate", "controls", "empirical_validation", "receipt"))
    for dep in spec.dependencies:
        files.extend((root / "claims" / dep / "registration.json", current_certificate(root, dep)))
    files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/materials/hand_001_006_validator_v1.py"
    independent = ExternalCommandValidator("sft-materials-hand-001-006-independent-python/1", (sys.executable, str(validator), cid, str(root)), validator.parent, (validator,))
    return ClaimExecution(HandoffProgram(spec, source_hash), independent, files, MaterialsHandoffValidator(root, spec))
