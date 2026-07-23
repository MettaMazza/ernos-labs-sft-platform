"""Dependency-ordered, complete information-science branch claim catalog."""

from __future__ import annotations

from sft.information_science.channels_capacity import SPEC as CHANNELS_CAPACITY
from sft.information_science.classical_probabilistic_information import SPEC as CLASSICAL_PROBABILISTIC
from sft.information_science.coding_theory import SPEC as CODING
from sft.information_science.compression_redundancy import SPEC as COMPRESSION_REDUNDANCY
from sft.information_science.conservation_loss_transformation import SPEC as CONSERVATION_LOSS
from sft.information_science.encoding_decoding import SPEC as ENCODING_DECODING
from sft.information_science.entropy_uncertainty import SPEC as ENTROPY_UNCERTAINTY
from sft.information_science.information_quantity import SPEC as INFORMATION_QUANTITY
from sft.information_science.mutual_conditional_information import SPEC as MUTUAL_CONDITIONAL
from sft.information_science.noise_error import SPEC as NOISE_ERROR
from sft.information_science.quantum_information_correspondence import SPEC as QUANTUM_CORRESPONDENCE
from sft.information_science.symbols_distinguishability import SPEC as SYMBOLS_DISTINGUISHABILITY


SPECS = (
    SYMBOLS_DISTINGUISHABILITY,
    ENCODING_DECODING,
    INFORMATION_QUANTITY,
    ENTROPY_UNCERTAINTY,
    COMPRESSION_REDUNDANCY,
    CHANNELS_CAPACITY,
    NOISE_ERROR,
    CODING,
    MUTUAL_CONDITIONAL,
    CONSERVATION_LOSS,
    CLASSICAL_PROBABILISTIC,
    QUANTUM_CORRESPONDENCE,
)


def validate_catalog() -> None:
    """Halt if the branch inventory is duplicated, incomplete or misordered."""

    if len(SPECS) != 12:
        raise ValueError("the information-science catalog must contain exactly twelve declared obligations")
    claim_ids = tuple(spec.claim_id for spec in SPECS)
    if len(set(claim_ids)) != len(claim_ids):
        raise ValueError("the information-science catalog contains a duplicate claim identity")
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
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-DISCRETE-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-ALGEBRA-001",
        "SFT-MATH-ORDER-LATTICE-001",
        "SFT-MATH-GEOMETRY-TOPOLOGY-001",
        "SFT-MATH-PROBABILITY-STATISTICS-001",
        "SFT-MATH-OPTIMIZATION-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-MATH-LOGIC-PROOF-001",
        "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    }
    for spec in SPECS:
        spec.validate()
        missing = tuple(dependency for dependency in spec.dependencies if dependency not in available)
        if missing:
            raise ValueError(f"{spec.claim_id} appears before dependencies: {missing}")
        available.add(spec.claim_id)


validate_catalog()

__all__ = ("SPECS", "validate_catalog")
