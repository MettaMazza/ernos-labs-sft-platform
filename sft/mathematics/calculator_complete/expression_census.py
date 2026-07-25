"""One-to-one current-knowledge Mathematics expression coverage census."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from sft.mathematics.catalog import SPECS

from .evidence import CALCULATOR_CLAIM_ID


@dataclass(frozen=True)
class ExpressionFamily:
    claim_id: str
    interaction: str
    operations: tuple[str, ...]


STRUCTURED_OPERATIONS = {
    "SFT-MATH-EXACT-ARITHMETIC-001": (
        "junction", "product", "quotient", "comparison", "oriented remainder",
    ),
    "SFT-MATH-DISCRETE-001": (
        "collection", "selection", "relation", "finite function", "induction trace",
    ),
    "SFT-MATH-COMBINATORICS-001": (
        "arrangements", "selections", "class ledger", "recurrence extension",
    ),
    "SFT-MATH-GRAPH-NETWORK-001": (
        "graph", "path", "reachability", "cycle", "cut", "network balance",
    ),
    "SFT-MATH-ALGEBRA-001": (
        "operation table", "identity", "associativity", "return mate", "homomorphism",
    ),
    "SFT-MATH-ORDER-LATTICE-001": (
        "partial order", "comparability", "meet", "join", "monotone map",
    ),
    "SFT-MATH-GEOMETRY-TOPOLOGY-001": (
        "incidence", "dimension", "adjacency", "path distance", "finite topology", "continuity",
    ),
    "SFT-MATH-PROBABILITY-STATISTICS-001": (
        "event", "exact weight", "conditional weight", "independence", "mode", "observation class",
    ),
    "SFT-MATH-OPTIMIZATION-001": (
        "feasible carrier", "undominated carrier", "exact optimum", "Pareto frontier", "approximation ratio",
    ),
    "SFT-MATH-DYNAMICAL-SYSTEMS-001": (
        "transition law", "trajectory", "time", "fixed form", "return", "reversibility", "stability",
    ),
    "SFT-MATH-LOGIC-PROOF-001": (
        "proposition", "denial", "junction", "alternative", "proof", "consistency", "grammar completeness",
    ),
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001": (
        "identity arrow", "composition", "canonical path", "type", "product", "sum", "functor", "naturality",
    ),
}


SCALAR_AND_CERTIFICATE_CLAIMS = {
    "SFT-MATH-EXACT-RELATIONS-002",
    "SFT-MATH-ORBIT-NUMBER-THEORY-002",
    "SFT-MATH-LIMIT-CONTINUUM-002",
    "SFT-MATH-ALGEBRAIC-BALANCE-002",
    "SFT-MATH-BOUNDED-N-BODY-002",
    "SFT-MATH-FLOORED-FLUID-REGULARITY-002",
    "SFT-MATH-PRIME-PAIR-CENSUS-002",
    "SFT-MATH-RIEMANN-MIRROR-002",
    "SFT-MATH-COLLATZ-FINITE-CENSUS-002",
    "SFT-MATH-SELF-SIMILAR-CONVERGENCE-002",
    "SFT-MATH-SCIENTIFIC-CALCULATOR-004",
    "SFT-MATH-SCIENTIFIC-CALCULATOR-005",
}


def expression_families() -> tuple[ExpressionFamily, ...]:
    predecessor_ids = tuple(spec.claim_id for spec in SPECS if spec.claim_id != CALCULATOR_CLAIM_ID)
    families: list[ExpressionFamily] = []
    for claim_id in predecessor_ids:
        if claim_id in STRUCTURED_OPERATIONS:
            families.append(ExpressionFamily(claim_id, "structured_exact_library_and_law_replay", STRUCTURED_OPERATIONS[claim_id]))
        elif claim_id in SCALAR_AND_CERTIFICATE_CLAIMS:
            families.append(
                ExpressionFamily(
                    claim_id,
                    "scalar_or_certificate_evaluator_and_law_replay",
                    ("exact value", "certified enclosure", "registered enumeration replay"),
                )
            )
        else:
            raise RuntimeError(f"Mathematics expression family lacks a calculator translation: {claim_id}")
    if (
        len(set(predecessor_ids)) != len(predecessor_ids)
        or len(families) != len(predecessor_ids)
        or {item.claim_id for item in families} != set(predecessor_ids)
    ):
        raise RuntimeError("Mathematics expression census is not one-to-one")
    return tuple(families)


def expression_census_json() -> str:
    families = expression_families()
    return json.dumps(
        {
            "calculator_claim_id": CALCULATOR_CLAIM_ID,
            "scope": "every registered predecessor in the current SFT Mathematics branch",
            "family_count": len(families),
            "families": [asdict(item) for item in families],
        },
        indent=2,
        sort_keys=True,
    ) + "\n"


__all__ = ("ExpressionFamily", "expression_census_json", "expression_families")
