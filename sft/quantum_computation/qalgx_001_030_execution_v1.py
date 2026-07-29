"""Execution bindings for QALGX-001 through QALGX-030."""
import json
import sys
from pathlib import Path
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.quantum_computation.qalgx_001_030_external_v1 import QuantumAlgorithmExecutionValidator, REGISTRY, VECTOR
from sft.quantum_computation.qalgx_001_030_laws_v1 import QuantumAlgorithmExtensionProgram, SPECS
from sft.verification import ClaimExecution


def current_certificate(root, claim_id):
    row = next(entry for entry in json.loads((root / "census/claims.json").read_text())["claims"] if entry["claim_id"] == claim_id)
    matches = [path for path in sorted((root / "claims" / claim_id).glob("certificate*.json")) if json.loads(path.read_text()).get("engine_receipt_hash") == row["receipt_hash"]]
    if len(matches) != 1:
        raise ValueError(f"{claim_id} current certificate count {len(matches)}")
    return matches[0]


def build_execution(root: Path, claim_id: str, execution_file: Path):
    spec = SPECS[claim_id]
    source_files = [root / "sft/quantum_computation/generated_law.py", root / "sft/quantum_computation/qalgx_001_030_laws_v1.py", root / "sft/quantum_computation/qalgx_001_030_external_v1.py", root / "sft/quantum_computation/qalgx_001_030_execution_v1.py", root / REGISTRY, root / VECTOR, execution_file]
    for dependency in spec.dependencies:
        source_files.extend((root / "claims" / dependency / "registration.json", current_certificate(root, dependency)))
    source_files = tuple(dict.fromkeys(source_files))
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/quantum_computation/qalgx_001_030_validator_v1.py"
    independent = ExternalCommandValidator("sft-quantum-computation-qalgx-001-030-independent-python/1", (sys.executable, str(validator), claim_id, str(root)), validator.parent, (validator,))
    return ClaimExecution(QuantumAlgorithmExtensionProgram(spec, source_hash), independent, source_files, QuantumAlgorithmExecutionValidator(root, spec))
