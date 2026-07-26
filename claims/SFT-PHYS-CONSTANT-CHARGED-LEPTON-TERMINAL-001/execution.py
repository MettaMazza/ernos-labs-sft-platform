"""Official empirically gated terminal charged-lepton execution."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.charged_lepton_validation import ChargedLeptonTerminalExternalValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.physics.terminal_lepton_law import TERMINAL_LEPTON_SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/terminal_lepton_law.py",
        root / "sft/physics/charged_lepton_validation.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measured_value.py",
        root / "claims/SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001/execution.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001/independent_validator.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(TERMINAL_LEPTON_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-constant-charged-lepton-terminal-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=ChargedLeptonTerminalExternalValidator(root),
    )
