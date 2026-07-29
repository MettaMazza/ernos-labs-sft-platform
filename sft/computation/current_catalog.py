"""Current Classical Computation catalog without mutating sealed source catalogs."""

from __future__ import annotations

from sft.computation.catalog import FOUNDATION_DEPENDENCIES, SPECS as SEALED_SPECS
from sft.computation.correspondence_return_laws import RETURN_SPECS
from sft.computation.lineage_laws import LINEAGE_SPECS


SPECS = (*SEALED_SPECS, *LINEAGE_SPECS, *RETURN_SPECS)
SPEC_BY_ID = {spec.claim_id: spec for spec in SPECS}


def validate_catalog() -> None:
    if len(SPECS) != 117 or len(SPEC_BY_ID) != 117:
        raise ValueError("the current classical-computation catalog must contain 117 unique obligations")
    available = set(FOUNDATION_DEPENDENCIES)
    for spec in SPECS:
        spec.validate()
        missing = tuple(dependency for dependency in spec.dependencies if dependency not in available)
        if missing:
            raise ValueError(f"{spec.claim_id} appears before dependencies: {missing}")
        available.add(spec.claim_id)


validate_catalog()
