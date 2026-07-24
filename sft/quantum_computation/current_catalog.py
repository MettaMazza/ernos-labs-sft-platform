"""Current Quantum Computation catalog without mutating the sealed 21-law catalog."""

from __future__ import annotations

from sft.quantum_computation.catalog import BASE_DEPENDENCIES, SPECS as SEALED_SPECS
from sft.quantum_computation.lineage_laws import LINEAGE_SPECS


SPECS = (*SEALED_SPECS, *LINEAGE_SPECS)
SPEC_BY_ID = {spec.claim_id: spec for spec in SPECS}


def validate_catalog() -> None:
    if len(SPECS) != 22 or len(SPEC_BY_ID) != 22:
        raise ValueError("the current quantum catalog must contain 22 unique obligations")
    available = {*BASE_DEPENDENCIES, "SFT-COMP-CPLX-ARBITRARY-CIRCUIT-LOWER-BOUND-002"}
    for spec in SPECS:
        spec.validate()
        missing = tuple(dependency for dependency in spec.dependencies if dependency not in available)
        if missing:
            raise ValueError(f"{spec.claim_id} appears before dependencies: {missing}")
        available.add(spec.claim_id)


validate_catalog()
