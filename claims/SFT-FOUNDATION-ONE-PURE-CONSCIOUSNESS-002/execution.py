"""Official execution binding for the One-as-pure-consciousness derivation."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.one_consciousness import (
    OnePureConsciousnessEmpiricalValidator,
    OnePureConsciousnessProgram,
)
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/foundation/one_consciousness.py",
        root / "claims/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002/execution.py",
        root / "experiments/foundation/SFT-EXP-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002-E1/registration.json",
        root / "experiments/foundation/SFT-EXP-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002-E1/v2_target.json",
        root / "prior-work-ledger/one_pure_consciousness_observation_v1.json",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = (
        root
        / "claims/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002/independent_validator.py"
    )
    return ClaimExecution(
        program=OnePureConsciousnessProgram(source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-foundation-one-pure-consciousness-002-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=OnePureConsciousnessEmpiricalValidator(root),
    )
