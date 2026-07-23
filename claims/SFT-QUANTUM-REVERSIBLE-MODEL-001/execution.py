"""Official execution binding for SFT-QUANTUM-REVERSIBLE-MODEL-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.quantum_computation.generated_law import GeneratedQuantumProgram
from sft.quantum_computation.reversible_model.law import SPEC
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/quantum_computation/generated_law.py",
        root / "sft/quantum_computation/operations.py",
        root / "sft/quantum_computation/catalog.py",
        root / "sft/quantum_computation/reversible_model/law.py",
        root / "claims/SFT-QUANTUM-REVERSIBLE-MODEL-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-QUANTUM-REVERSIBLE-MODEL-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedQuantumProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-quantum-reversible-model-001-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
    )
