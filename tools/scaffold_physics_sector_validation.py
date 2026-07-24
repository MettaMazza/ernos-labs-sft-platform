#!/usr/bin/env python3
"""Scaffold the post-seal PDG sector-anchor validation package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.physics.sector_inventory_validation_v1 import SPEC  # noqa: E402
from tools.scaffold_physics_measurement_claims import (  # noqa: E402
    claim_registration,
    experiment_registration,
    independent_source,
    note,
    write,
)


def main() -> None:
    package = ROOT / "claims" / SPEC.claim_id
    execution = f'''"""Official execution for {SPEC.claim_id}."""
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
        root / "claims/{SPEC.claim_id}/execution.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{SPEC.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-sector-anchor-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=SectorAnchorValidator(root),
    )
'''
    write(package / "registration.json", json.dumps(claim_registration(SPEC), indent=2) + "\n")
    write(package / "execution.py", execution)
    write(package / "independent_validator.py", independent_source(SPEC))
    write(package / "WHY_DERIVATION_CHECK.md", note(SPEC))
    write(package / "STATUS.md", f"# {SPEC.claim_id}\n\nStatus: `registered`\n")
    experiment = ROOT / "experiments/physics" / SPEC.experiment_id
    write(experiment / "registration.json", json.dumps(experiment_registration(SPEC), indent=2) + "\n")
    print(f"scaffolded {SPEC.claim_id}")


if __name__ == "__main__":
    main()
