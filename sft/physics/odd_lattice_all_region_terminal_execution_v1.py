"""Official frozen-engine binding for odd-lattice all-region occupancy."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.odd_lattice_all_region_terminal_law_v1 import CLAIM_ID, OddLatticeAllRegionProgram
from sft.physics.odd_lattice_all_region_terminal_validation_v1 import OddLatticeAllRegionValidator
from sft.verification import ClaimExecution


def build_odd_lattice_all_region_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/vacuum_lineage_laws_v1.py",
        root / "sft/physics/odd_lattice_all_region_terminal_law_v1.py",
        root / "sft/physics/odd_lattice_all_region_terminal_validation_v1.py",
        root / "sft/physics/odd_lattice_all_region_terminal_execution_v1.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        root / "sft/engine/empirical.py",
        root / "sft/engine/isolation.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/odd_lattice_all_region_terminal_validator_v1.py"
    return ClaimExecution(
        program=OddLatticeAllRegionProgram(source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-odd-lattice-all-region-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=OddLatticeAllRegionValidator(root),
    )


__all__ = ("build_odd_lattice_all_region_execution",)
