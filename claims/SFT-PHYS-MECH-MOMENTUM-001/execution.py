"""Official execution binding for SFT-PHYS-MECH-MOMENTUM-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.generated_empirical_law import BlindExternalMeasurementValidator, GeneratedEmpiricalPhysicsProgram
from sft.physics.mechanics_laws import MECHANICS_SPECS
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in MECHANICS_SPECS if item.claim_id == 'SFT-PHYS-MECH-MOMENTUM-001')
    source_files = (
        root / "sft/physics/generated_empirical_law.py",
        root / 'sft/physics/mechanics_laws.py',
        root / "claims/SFT-PHYS-MECH-MOMENTUM-001/execution.py",
        root / "sft/engine/fold_language.py", root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py", root / "sft/engine/isolation.py", root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-MECH-MOMENTUM-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator('sft-phys-mech-momentum-001' + "-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files,
        empirical_validator=BlindExternalMeasurementValidator(root, spec),
    )
