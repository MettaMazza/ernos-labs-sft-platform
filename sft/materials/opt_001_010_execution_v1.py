"""Official execution assembly for Materials OPT-001--010."""
import json
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.materials.opt_001_010_external_v1 import ADDENDUM_MANIFEST, ADDENDUM_REGISTRY, MANIFEST, REGISTRY, VECTOR, OptExternalValidator
from sft.materials.opt_001_010_laws_v1 import SPECS, OptProgram
from sft.verification import ClaimExecution

def certificate(root, claim_id):
    row = next(item for item in json.loads((root / "census/claims.json").read_text())["claims"] if item["claim_id"] == claim_id)
    matches = [path for path in (root / "claims" / claim_id).glob("certificate*.json") if json.loads(path.read_text()).get("engine_receipt_hash") == row["receipt_hash"]]
    if len(matches) != 1:
        raise ValueError("dependency certificate count")
    return matches[0]

def build_execution(root, claim_id, execution_file):
    spec = SPECS[claim_id]
    manifest = json.loads((root / MANIFEST).read_text())
    vector = json.loads((root / VECTOR).read_text())
    fixed = (root / "sft/materials/opt_001_010_laws_v1.py", root / "sft/materials/opt_001_010_external_v1.py", root / "sft/materials/opt_001_010_execution_v1.py", root / "sft/physics/structural_constants.py", root / REGISTRY, root / MANIFEST, root / ADDENDUM_REGISTRY, root / ADDENDUM_MANIFEST, root / VECTOR, execution_file)
    sources = tuple(root / row["snapshot_path"] for row in vector["source_status_rows"])
    texts = tuple(root / row["text_path"] for row in vector["pdf_text_reconstructions"])
    dependencies = tuple(path for dependency in spec.dependencies for path in (root / "claims" / dependency / "registration.json", certificate(root, dependency)))
    files = tuple(dict.fromkeys(fixed + sources + texts + dependencies))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/materials/opt_001_010_validator_v1.py"
    independent = ExternalCommandValidator("sft-materials-opt-001-010-independent-python/1", (sys.executable, str(validator), claim_id, str(root)), validator.parent, (validator,))
    return ClaimExecution(OptProgram(spec, source_hash), independent, files, OptExternalValidator(root, spec))
