"""Depth-independent composite Fold-sector confinement and orbit census.

The five earlier sector observations select the questions that must be
reconstructed.  They do not select this law, its orbit action, its coupling or
any survivor.  The theorem is proved for every generated even sector beyond
the binary fibre and the five registered cases are exact instantiations.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031"
REGISTERED_COMPOSITE_SECTORS = (8, 12, 18, 24, 30)


def _require_even_sector(sector: int) -> None:
    if isinstance(sector, bool) or sector <= 2 or sector % 2 != 0:
        raise ValueError("Fold confinement requires a generated even sector beyond the binary fibre")


def held_denominator(sector: int) -> int:
    """The positive predecessor support retained by a sector."""

    _require_even_sector(sector)
    return sector - 1


def standing_mode_labels(sector: int) -> tuple[int, ...]:
    """Every nonempty numerator label over the held predecessor support."""

    denominator = held_denominator(sector)
    return tuple(range(1, denominator))


def standing_modes(sector: int) -> tuple[Fraction, ...]:
    denominator = held_denominator(sector)
    return tuple(Fraction(label, denominator) for label in standing_mode_labels(sector))


def fold_mode_label(label: int, sector: int) -> int:
    """Double a held numerator and cast complete denominator wholes."""

    denominator = held_denominator(sector)
    if label not in standing_mode_labels(sector):
        raise ValueError("Fold mode label lies outside the complete standing support")
    folded = (label + label) % denominator
    if folded < 1:
        raise ValueError("odd predecessor support cannot Fold a nonempty mode to an empty label")
    return folded


def inverse_fold_mode_label(label: int, sector: int) -> int:
    """Exact inverse supplied by the half-successor of the odd denominator."""

    denominator = held_denominator(sector)
    if label not in standing_mode_labels(sector):
        raise ValueError("inverse Fold label lies outside the complete standing support")
    inverse_two = (denominator + 1) // 2
    predecessor = (inverse_two * label) % denominator
    if predecessor < 1 or fold_mode_label(predecessor, sector) != label:
        raise ValueError("Fold inverse did not reconstruct the held label")
    return predecessor


def orbit_from_label(label: int, sector: int) -> tuple[int, ...]:
    if label not in standing_mode_labels(sector):
        raise ValueError("orbit source lies outside the complete standing support")
    orbit = []
    current = label
    while current not in orbit:
        orbit.append(current)
        current = fold_mode_label(current, sector)
    if current != label:
        raise ValueError("Fold mode entered a distinct recurrence before returning")
    return tuple(orbit)


def orbit_partition(sector: int) -> tuple[tuple[int, ...], ...]:
    """Generate every first-return orbit exactly once in least-label order."""

    remaining = set(standing_mode_labels(sector))
    orbits = []
    while remaining:
        orbit = orbit_from_label(min(remaining), sector)
        if any(label not in remaining for label in orbit):
            raise ValueError("generated Fold orbits overlap")
        orbits.append(orbit)
        remaining.difference_update(orbit)
    return tuple(orbits)


def antipodal_pairs(sector: int) -> tuple[tuple[int, int], ...]:
    """Pair each held numerator with its unique positive One-complement."""

    denominator = held_denominator(sector)
    return tuple((label, denominator - label) for label in range(1, (denominator + 1) // 2))


def holding_coupling(sector: int) -> Fraction:
    """All predecessor parts held over the complete sector support."""

    return Fraction(held_denominator(sector), sector)


def sector_certificate(sector: int) -> dict[str, object]:
    modes = standing_mode_labels(sector)
    orbits = orbit_partition(sector)
    pairs = antipodal_pairs(sector)
    denominator = held_denominator(sector)
    images = tuple(fold_mode_label(label, sector) for label in modes)
    predecessors = tuple(inverse_fold_mode_label(label, sector) for label in modes)
    return {
        "sector": sector,
        "denominator": denominator,
        "modes": modes,
        "mode_count": len(modes),
        "orbits": orbits,
        "orbit_sizes": tuple(len(orbit) for orbit in orbits),
        "antipodal_pairs": pairs,
        "antipodal_pair_count": len(pairs),
        "coupling": holding_coupling(sector),
        "denominator_preserved": all(1 <= image < denominator for image in images),
        "Fold_is_bijective": set(images) == set(modes) and set(predecessors) == set(modes),
        "orbits_are_complete": set(label for orbit in orbits for label in orbit) == set(modes),
        "pairs_are_complete": set(label for pair in pairs for label in pair) == set(modes),
        "pairs_reassemble_One": all(left + right == denominator for left, right in pairs),
    }


def registered_sector_census() -> tuple[dict[str, object], ...]:
    return tuple(sector_certificate(sector) for sector in REGISTERED_COMPOSITE_SECTORS)


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Depth-independent composite confining-sector orbit law",
    statement=(
        "Every generated even Fold sector s beyond the binary fibre holds the odd positive predecessor "
        "d=s-1. Its complete nonempty standing modes are the d-1 labels k/d. Fold doubling has the exact "
        "inverse (d+1)/2 and therefore permutes this support without changing denominator, forcing a finite "
        "disjoint first-return orbit partition. The modes form exactly (d-1)/2=(s-2)/2 positive antipodal "
        "pairs whose members reassemble the One, and the unique all-but-one holding coupling is d/s. "
        "Consequently sectors 8, 12, 18, 24 and 30 have respectively 6, 10, 16, 22 and 28 modes; orbit-size "
        "partitions (3,3), (10), (8,8), (11,11) and (28); pair counts 3, 5, 8, 11 and 14; and couplings "
        "7/8, 11/12, 17/18, 23/24 and 29/30."
    ),
    dependencies=(
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-MATH-ORBIT-NUMBER-THEORY-002",
        "SFT-PHYS-FOLD-UNIVERSE-TRANSPORT-TERMINAL-024",
        "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003",
        "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of sector scope, held support, standing-mode census, Fold action, "
        "confinement, orbit partition, antipodal closure, pair-count law, holding coupling, external "
        "correspondence boundary and extension form."
    ),
    grammar_boundary=(
        "Every positive finite even sector beyond two; its odd positive predecessor denominator; every "
        "nonempty numerator label; every exact Fold successor and first return; every complement pair; the "
        "five registered composite-sector instances; and the already sealed force-sector anchor boundary."
    ),
    axes=(
        binary_axis("scope", "Which sector cases does the law cover?", "five-selected-case-table", "A selected table does not prove the next even sector.", "every-generated-even-sector", "The odd-predecessor argument applies to every positive finite even successor beyond two."),
        binary_axis("support", "What support does a sector hold?", "borrowed-or-measured-denominator", "A named or measured denominator can select the orbit.", "positive-predecessor-denominator", "The unique predecessor d followed by One reassembles sector s."),
        binary_axis("modes", "Which standing modes enter?", "selected-mode-subset", "A subset cannot establish exhaustive confinement.", "all-nonempty-predecessor-labels", "Every positive label from One through the predecessor of d is generated once."),
        binary_axis("action", "How does Fold move a mode?", "selected-orbit-permutation", "A listed permutation imports its answer.", "double-and-cast-denominator-wholes", "Fold pairs the label and casts only complete held denominators."),
        binary_axis("confinement", "Why can no mode escape?", "finite-table-assertion", "A table alone does not close arbitrary successor depth.", "odd-support-exact-inverse", "The half-successor (d+1)/2 is an exact inverse of doubling on odd support."),
        binary_axis("orbits", "How is recurrence support organized?", "named-or-overlapping-orbits", "Named or overlapping rows omit a complete partition proof.", "complete-disjoint-first-return-partition", "Bijection on finite support partitions every label into one first-return orbit."),
        binary_axis("antipodes", "How do complementary modes close?", "borrowed-pairing-rule", "A borrowed pair rule does not prove exhaustiveness.", "unique-positive-One-complements", "Each k has the unique positive complement d-k and odd d forbids a self-pair."),
        binary_axis("pair_count", "What forces the pair count?", "ambiguous-sector-minus-one-over-two", "That notation is not a whole count for even s.", "predecessor-of-denominator-over-two", "The d-1 nonempty labels divide exactly into (d-1)/2 pairs, equivalently (s-2)/2."),
        binary_axis("coupling", "What share is held by the sector?", "measured-or-fitted-coupling", "Measurement cannot select a holding law.", "all-but-one-predecessor-over-sector", "Holding d of the s complete positions forces d/s with no free coefficient."),
        binary_axis("comparison", "What may external evidence establish?", "unobserved-cases-counted-as-confirmed", "A standing prediction is not a measurement.", "sealed-eight-anchor-and-explicit-standing-cases", "The known eight-carrier anchor is inherited post-derivation; every other case remains explicitly testable."),
        binary_axis("extension", "May another orbit or correction be inserted?", "free-orbit-or-coupling-correction", "An inserted row or correction is a free parameter.", "no-extra-rule", "Complete labels, Fold action, complements and held support exhaust the construction."),
    ),
    exact_result=(
        "The complete composite-sector census is: sector 8, denominator 7, orbits "
        "(1,2,4)/(3,6,5), three antipodal pairs and coupling 7/8; sector 12, denominator 11, one ten-mode "
        "orbit, five pairs and 11/12; sector 18, denominator 17, two eight-mode orbits, eight pairs and "
        "17/18; sector 24, denominator 23, two eleven-mode orbits, eleven pairs and 23/24; sector 30, "
        "denominator 29, one twenty-eight-mode orbit, fourteen pairs and 29/30. The general odd-support "
        "inverse proves denominator confinement and complete recurrence at every positive finite Fold depth."
    ),
    induction_base=(
        "For the least even sector beyond the binary fibre, the held predecessor d is odd. Doubling any "
        "nonempty label has the exact inverse multiplication by the positive half-successor (d+1)/2."
    ),
    induction_step=(
        "Advancing one Fold tick applies the same bijection, so a label remains inside the unchanged finite "
        "support. Finite bijection forces first return; adding the next complement pair preserves exhaustive "
        "support, One reassembly and the pair-count successor without altering the coupling construction."
    ),
    exclusions=(
        "no V1/V2 executable, stored orbit table or prior survivor in the derivation runtime",
        "no imported gauge group, particle taxonomy, measured coupling or target-selected sector",
        "no semantic numerical zero, negative, irrational, imaginary, floating or completed-infinity proof value",
        "no claim that every arithmetic composite sector is already an observed independent physical force",
        "no relabelling of the standing sectors twelve, eighteen, twenty-four or thirty as measured confirmations",
        "no ambiguous half-whole pair count: the exact whole formula is (s-2)/2",
    ),
    witnesses=(
        Witness("sector-eight", "The denominator-seven support splits into the two exact three-member orbits and three complement pairs.", sector_certificate(8)["orbits"] == ((1, 2, 4), (3, 6, 5)) and sector_certificate(8)["antipodal_pair_count"] == 3),
        Witness("sector-twelve", "The denominator-eleven support is one ten-member orbit with five complement pairs.", sector_certificate(12)["orbit_sizes"] == (10,) and sector_certificate(12)["antipodal_pair_count"] == 5),
        Witness("sector-eighteen", "The denominator-seventeen support is two eight-member orbits with eight complement pairs.", sector_certificate(18)["orbit_sizes"] == (8, 8) and sector_certificate(18)["antipodal_pair_count"] == 8),
        Witness("sector-twenty-four", "The denominator-twenty-three support is two eleven-member orbits with eleven complement pairs.", sector_certificate(24)["orbit_sizes"] == (11, 11) and sector_certificate(24)["antipodal_pair_count"] == 11),
        Witness("sector-thirty", "The denominator-twenty-nine support is one twenty-eight-member orbit with fourteen complement pairs.", sector_certificate(30)["orbit_sizes"] == (28,) and sector_certificate(30)["antipodal_pair_count"] == 14),
        Witness("complete-general-controls", "Every registered case is bijective, denominator-preserving, orbit-complete and complement-complete.", all(row["Fold_is_bijective"] and row["denominator_preserved"] and row["orbits_are_complete"] and row["pairs_are_complete"] and row["pairs_reassemble_One"] for row in registered_sector_census())),
        Witness("coupling-table", "All five holding couplings are the exact all-but-one shares.", tuple(row["coupling"] for row in registered_sector_census()) == (Fraction(7, 8), Fraction(11, 12), Fraction(17, 18), Fraction(23, 24), Fraction(29, 30))),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "REGISTERED_COMPOSITE_SECTORS",
    "SPEC",
    "antipodal_pairs",
    "fold_mode_label",
    "held_denominator",
    "holding_coupling",
    "inverse_fold_mode_label",
    "orbit_from_label",
    "orbit_partition",
    "registered_sector_census",
    "sector_certificate",
    "standing_mode_labels",
    "standing_modes",
)
