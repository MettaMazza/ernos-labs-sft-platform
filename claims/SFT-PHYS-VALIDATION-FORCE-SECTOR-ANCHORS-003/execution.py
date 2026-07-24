"""Official execution for SFT-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram
from sft.physics.sector_inventory_validation_v1 import SPEC, SectorAnchorValidator
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/lineage_particle_laws.py",
        root / "sft/physics/sector_inventory_law_v1.py",
        root / "sft/physics/sector_inventory_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "claims/SFT-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003/execution.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-sector-anchor-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=SectorAnchorValidator(root),
    )
