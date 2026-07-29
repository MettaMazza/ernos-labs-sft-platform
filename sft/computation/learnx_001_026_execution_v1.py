"""Execution bindings for the complete LEARNX-001 through LEARNX-026 family."""
import json
import sys
from pathlib import Path

from sft.computation.learnx_001_026_external_v1 import REGISTRY, VECTOR, LearningObservationValidator
from sft.computation.learnx_001_026_laws_v1 import LearningExtensionProgram, SPECS
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def current_certificate(root, claim_id):
    row = next(item for item in json.loads((root / "census/claims.json").read_text())["claims"] if item["claim_id"] == claim_id)
    matches = [path for path in sorted((root / "claims" / claim_id).glob("certificate*.json")) if json.loads(path.read_text()).get("engine_receipt_hash") == row["receipt_hash"]]
    if len(matches) != 1:
        raise ValueError(f"{claim_id} current certificate count {len(matches)}")
    return matches[0]


def build_execution(root: Path, claim_id: str, execution_file: Path):
    spec = SPECS[claim_id]
    source_files = [root / "sft/computation/generated_law.py", root / "sft/computation/complete_field_observation_v1.py", root / "sft/computation/learnx_001_026_laws_v1.py", root / "sft/computation/learnx_001_026_external_v1.py", root / "sft/computation/learnx_001_026_execution_v1.py", root / REGISTRY, root / VECTOR, execution_file]
    for dependency in spec.dependencies:
        source_files.extend((root / "claims" / dependency / "registration.json", current_certificate(root, dependency)))
    source_files = tuple(dict.fromkeys(source_files)); source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/computation/learnx_001_026_validator_v1.py"
    independent = ExternalCommandValidator("sft-classical-computation-learnx-001-026-independent-python/1", (sys.executable, str(validator), claim_id, str(root)), validator.parent, (validator,))
    return ClaimExecution(LearningExtensionProgram(spec, source_hash), independent, source_files, LearningObservationValidator(root, spec))
