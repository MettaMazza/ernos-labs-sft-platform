"""Dependency-ordered, complete mathematics-branch claim catalog."""

from __future__ import annotations

from sft.mathematics.algebraic_structures import SPEC as ALGEBRA
from sft.mathematics.category_type_composition import SPEC as CATEGORY_TYPE_COMPOSITION
from sft.mathematics.combinatorics import SPEC as COMBINATORICS
from sft.mathematics.discrete_mathematics import SPEC as DISCRETE
from sft.mathematics.dynamical_systems import SPEC as DYNAMICAL_SYSTEMS
from sft.mathematics.exact_arithmetic import SPEC as EXACT_ARITHMETIC
from sft.mathematics.geometry_topology import SPEC as GEOMETRY_TOPOLOGY
from sft.mathematics.graph_network import SPEC as GRAPH_NETWORK
from sft.mathematics.logic_proof import SPEC as LOGIC_PROOF
from sft.mathematics.optimization import SPEC as OPTIMIZATION
from sft.mathematics.order_lattice import SPEC as ORDER_LATTICE
from sft.mathematics.probability_statistics import SPEC as PROBABILITY_STATISTICS


SPECS = (
    EXACT_ARITHMETIC,
    DISCRETE,
    COMBINATORICS,
    GRAPH_NETWORK,
    ALGEBRA,
    ORDER_LATTICE,
    GEOMETRY_TOPOLOGY,
    PROBABILITY_STATISTICS,
    OPTIMIZATION,
    DYNAMICAL_SYSTEMS,
    LOGIC_PROOF,
    CATEGORY_TYPE_COMPOSITION,
)


def validate_catalog() -> None:
    """Halt if the branch inventory is duplicated, incomplete or misordered."""

    if len(SPECS) != 12:
        raise ValueError("the mathematics catalog must contain exactly twelve declared obligations")
    claim_ids = tuple(spec.claim_id for spec in SPECS)
    if len(set(claim_ids)) != len(claim_ids):
        raise ValueError("the mathematics catalog contains a duplicate claim identity")
    available = {
        "SFT-ROOT-THERE-IS-NO-NOTHING",
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
        "SFT-FOUNDATION-FORM-GRAMMAR-001",
        "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    }
    for spec in SPECS:
        spec.validate()
        missing = tuple(dependency for dependency in spec.dependencies if dependency not in available)
        if missing:
            raise ValueError(f"{spec.claim_id} appears before dependencies: {missing}")
        available.add(spec.claim_id)


validate_catalog()

__all__ = ("SPECS", "validate_catalog")
