"""Execution assembly for Materials MICRO-001--009."""

import json
from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.materials.micro_001_009_external_v1 import ADDENDUM, MANIFEST, REGISTRY, VECTOR, MicrostructureExternalValidator
from sft.materials.micro_001_009_laws_v1 import MicrostructureProgram, SPECS
from sft.verification import ClaimExecution


def current_certificate(root, claim_id):
    row = next(item for item in json.loads((root / "census/claims.json").read_text())["claims"] if item["claim_id"] == claim_id)
    matches = [path for path in sorted((root / "claims" / claim_id).glob("certificate*.json")) if json.loads(path.read_text()).get("engine_receipt_hash") == row["receipt_hash"]]
    if len(matches) != 1:
        raise ValueError(f"{claim_id} current certificate count {len(matches)}")
    return matches[0]


def build_execution(root: Path, claim_id: str, execution_file: Path):
    spec = SPECS[claim_id]
    manifest = json.loads((root / MANIFEST).read_text())
    vector = json.loads((root / VECTOR).read_text())
    fixed = (root / "sft/materials/micro_001_009_laws_v1.py", root / "sft/materials/micro_001_009_external_v1.py", root / "sft/materials/micro_001_009_execution_v1.py", root / "sft/physics/structural_constants.py", root / REGISTRY, root / ADDENDUM, root / MANIFEST, root / VECTOR, execution_file)
    sources = tuple(root / row["snapshot_path"] for row in manifest["documents"])
    reconstructions = tuple(root / row["text_path"] for row in vector["pdf_text_reconstructions"])
    dependencies = tuple(path for dependency in spec.dependencies for path in (root / "claims" / dependency / "registration.json", current_certificate(root, dependency)))
    source_files = tuple(dict.fromkeys(fixed + sources + reconstructions + dependencies))
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/materials/micro_001_009_validator_v1.py"
    independent = ExternalCommandValidator("sft-materials-micro-001-009-independent-python/1", (sys.executable, str(validator), claim_id, str(root)), validator.parent, (validator,))
    return ClaimExecution(MicrostructureProgram(spec, source_hash), independent, source_files, MicrostructureExternalValidator(root, spec))


__all__ = ("build_execution",)
