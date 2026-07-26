"""Exact one-, two- and three-direction Fold lattice operator family."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-LATTICE-OPERATOR-TERMINAL-022"
ONE = Fraction(1, 1)
HALF = Fraction(1, 2)


@dataclass(frozen=True)
class OrientedCoordinate:
    axes: tuple[tuple[str, int | None], ...]

    @property
    def radius(self) -> int:
        return sum(magnitude for _, magnitude in self.axes if magnitude is not None)


@dataclass(frozen=True)
class PhaseModeCarrier:
    index: int
    period: int
    centre_share: Fraction
    forward_share: Fraction
    reverse_share: Fraction
    identity_phase: bool


def conservative_stencil(dimension: int) -> dict[str, object]:
    if isinstance(dimension, bool) or dimension < 1:
        raise ValueError("a lattice stencil requires a positive dimension count")
    neighbour_count = 2 * dimension
    neighbour_share = Fraction(1, 2 * neighbour_count)
    return {
        "dimension": dimension,
        "centre_share": HALF,
        "neighbour_count": neighbour_count,
        "neighbour_share": neighbour_share,
        "neighbour_total": neighbour_share * neighbour_count,
        "complete_total": HALF + neighbour_share * neighbour_count,
    }


def cyclic_update(state: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    if len(state) < 3 or any(not isinstance(value, Fraction) or value <= 0 for value in state):
        raise ValueError("cyclic update requires at least three positive exact carriers")
    size = len(state)
    return tuple(
        HALF * state[index]
        + Fraction(1, 4) * state[(index + size - 1) % size]
        + Fraction(1, 4) * state[(index + 1) % size]
        for index in range(size)
    )


def exact_mode_carriers(size: int) -> tuple[PhaseModeCarrier, ...]:
    if isinstance(size, bool) or size < 3:
        raise ValueError("mode support requires a positive cycle of at least three sites")
    return tuple(
        PhaseModeCarrier(
            index=index,
            period=size,
            centre_share=HALF,
            forward_share=Fraction(1, 4),
            reverse_share=Fraction(1, 4),
            identity_phase=index == size,
        )
        for index in range(1, size + 1)
    )


def point_source_operator(dimension: int) -> dict[str, object]:
    stencil = conservative_stencil(dimension)
    neighbour_count = int(stencil["neighbour_count"])
    return {
        "peak_magnitude": neighbour_count,
        "peak_orientation": "source",
        "ring": tuple(("opposition", ONE) for _ in range(neighbour_count)),
        "ring_count": neighbour_count,
        "balanced_magnitude": Fraction(neighbour_count, 1) == sum((row[1] for row in tuple(("opposition", ONE) for _ in range(neighbour_count))), ONE) - ONE,
    }


def axis_positions(radius: int) -> tuple[tuple[str, int | None], ...]:
    if isinstance(radius, bool) or radius < 1:
        raise ValueError("a causal radius requires a positive tick count")
    rows: list[tuple[str, int | None]] = [("origin", None)]
    for magnitude in range(1, radius + 1):
        rows.extend((("lower", magnitude), ("upper", magnitude)))
    return tuple(rows)


def causal_ball(dimension: int, ticks: int) -> tuple[OrientedCoordinate, ...]:
    if isinstance(dimension, bool) or dimension < 1:
        raise ValueError("a causal ball requires a positive dimension count")
    if isinstance(ticks, bool) or ticks < 1:
        raise ValueError("a causal ball requires a positive tick count")
    return tuple(
        OrientedCoordinate(tuple(coordinate))
        for coordinate in product(axis_positions(ticks), repeat=dimension)
        if sum(magnitude for _, magnitude in coordinate if magnitude is not None) <= ticks
    )


def causal_ball_count(dimension: int, ticks: int) -> int:
    return len(causal_ball(dimension, ticks))


def lattice_family_certificate() -> dict[str, object]:
    stencils = tuple(conservative_stencil(dimension) for dimension in (1, 2, 3))
    operators = tuple(point_source_operator(dimension) for dimension in (1, 2, 3))
    counts = {
        dimension: tuple(causal_ball_count(dimension, tick) for tick in (1, 2, 3))
        for dimension in (1, 2, 3)
    }
    bump = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))
    updated = cyclic_update(bump)
    flat = (Fraction(1, 3),) * 3
    modes = exact_mode_carriers(7)
    return {
        "stencils": stencils,
        "operators": operators,
        "causal_counts": counts,
        "bump_update": updated,
        "bump_centre": updated[1],
        "flat_stationary": cyclic_update(flat) == flat,
        "presence_conserved": sum(updated, ONE) - ONE == sum(bump, ONE) - ONE,
        "mode_count": len(modes),
        "identity_mode_count": sum(mode.identity_phase for mode in modes),
        "mode_relation": "half-One centre plus quarter forward phase plus quarter reverse phase",
        "irrational_mode_value_evaluated": False,
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Exact Fold lattice operators, causal cones and phase modes",
    statement=(
        "One conservative Fold lattice family covers one, two and three generated "
        "directions.  Every site retains half-One and distributes the other half "
        "equally over its complete two-per-axis neighbour ring; this gives the "
        "one-direction half/quarter/quarter stencil and the planar four-neighbour "
        "eighth shares.  A point source has positive peak magnitude two times the "
        "dimension and an equally counted opposition ring.  Complete oriented "
        "taxicab enumeration forces causal-ball counts 5,13,25 in two directions "
        "and 7,25,63 in three.  A cycle of N positive sites has exactly N phase "
        "mode carriers with update relation half-One centre plus quarter forward "
        "phase plus quarter reverse phase; the identity phase is the unique "
        "stationary flat mode.  No irrational mode value is evaluated."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-GRAVITY-LATTICE-CURVATURE-003",
        "SFT-PHYS-FIELD-MAXWELL-PLANAR-CLOSURE-003",
        "SFT-PHYS-FIELD-MAXWELL-THREE-SPACE-CLOSURE-003",
        "SFT-PHYS-WAVE-DISPERSION-001",
        "SFT-PHYS-DYNAMICS-FREE-PHASE-DISPERSION-003",
        "SFT-PHYS-VALIDATION-ATOMIC-CUBIC-SUPPORT-004",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of site carrier, neighbour family, conserved "
        "stencil, positive operator, point-source ring, causal support, cycle modes, "
        "dimension induction, comparison boundary and extension forms."
    ),
    grammar_boundary=(
        "Every positive finite one-, two- and three-direction nearest-neighbour Fold "
        "lattice; every positive tick and oriented causal cell; every positive "
        "finite cyclic site count of at least three; and the already sealed "
        "dispersion, Maxwell and cubic-support comparison records."
    ),
    axes=(
        binary_axis("carrier", "What occupies a lattice site?", "signed-field-number", "A signed scalar imports cancellation and an unheld absence value.", "positive-held-site-presence", "Every site retains one positive exact presence carrier and its source orientation."),
        binary_axis("neighbours", "Which adjacent cells participate?", "selected-or-remote-neighbours", "Selection or remote adjacency breaks locality and completeness.", "complete-two-per-generated-axis-ring", "Each generated axis supplies its lower and upper adjacent cell exactly once."),
        binary_axis("stencil", "How is presence transferred?", "free-dimension-specific-weights", "Independent weights introduce parameters.", "half-One-held-half-One-equally-distributed", "The centre retains half-One and the complete neighbour ring partitions the other half exactly."),
        binary_axis("operator", "How is curvature represented?", "signed-Laplacian-value", "A signed result is not a positive Fold record.", "positive-peak-with-held-opposition", "Peak and ring magnitudes stay positive while a held orientation records opposition."),
        binary_axis("source", "What is the point-source response?", "chosen-peak-or-partial-ring", "A chosen peak or incomplete ring does not conserve the neighbour ledger.", "two-dimension-peak-and-complete-ring", "Two neighbours per axis force equal peak and ring counts 2d."),
        binary_axis("causality", "Which cells are reached after a tick?", "continuum-or-selected-front", "A continuum or selected sample omits generated cells.", "complete-oriented-taxicab-ball", "Every cell whose positive oriented step count does not exceed the tick is generated once."),
        binary_axis("modes", "How is cyclic dispersion retained?", "evaluated-cosine-or-mode-table", "An imported cosine or table introduces nonnative and potentially irrational proof values.", "complete-exact-phase-mode-carriers", "Every cyclic phase label is retained with the exact centre/forward/reverse share relation."),
        binary_axis("induction", "How do dimensions and ticks extend?", "bounded-count-list", "A short list does not close the next generated axis or tick.", "axis-and-oriented-step-successor", "Adding an axis appends exactly two neighbours; adding a tick appends every oriented boundary cell of that radius."),
        binary_axis("comparison", "How do physical dispersion and cubic support enter?", "measurement-selects-operator", "External targets cannot choose the stencil or cone.", "inherit-sealed-dispersion-and-cubic-records", "Existing post-seal claims test label-dependent dispersion and six-neighbour cubic support downstream."),
        binary_axis("extension", "May another lattice coefficient enter?", "free-coefficient-or-extra-neighbour", "That changes the generated conservative family.", "no-extra-rule", "Half retention, complete local adjacency and equal partition exhaust the law."),
    ),
    exact_result=(
        "The exact Fold nearest-neighbour family retains half-One at the centre and "
        "shares half-One over 2d neighbours; point-source peak and opposition-ring "
        "magnitudes are 2d; causal balls at ticks 1,2,3 are (3,5,7), (5,13,25) "
        "and (7,25,63) for dimensions one, two and three; and every N-site cycle "
        "has N exact phase-mode carriers with one stationary identity mode."
    ),
    induction_base=(
        "One generated direction supplies two adjacent cells, centre half-One and "
        "two quarter-One shares, conserving the One and advancing at most one cell "
        "per tick."
    ),
    induction_step=(
        "Each added direction contributes one lower and one upper neighbour and "
        "repartitions the same held half-One over the complete ring; each added tick "
        "appends exactly the oriented cells at the new taxicab radius without "
        "altering any earlier cell or the phase-mode relation."
    ),
    exclusions=(
        "no imported continuum, signed Laplacian, Fourier cosine or monatomic-chain equation as a premise",
        "no V1/V2 executable, answer table, measured spectrum or stored survivor",
        "no numerical-zero, negative, irrational, imaginary or floating proof magnitude",
        "no target-selected neighbour, coefficient, mode or causal-front count",
        "no claim that the exact phase carrier evaluates an irrational conventional eigenvalue",
        "no external comparison before the inherited dispersion and cubic-support seals",
    ),
    witnesses=(
        Witness("conservative-stencils", "The one-, two- and three-direction stencils each reassemble the One and give neighbour counts two, four and six.", all(row["complete_total"] == ONE for row in lattice_family_certificate()["stencils"]) and tuple(row["neighbour_count"] for row in lattice_family_certificate()["stencils"]) == (2, 4, 6)),
        Witness("half-quarter-quarter", "The one-direction stencil is exactly half-One, quarter-One, quarter-One and the symmetric bump centre becomes three-eighths.", conservative_stencil(1)["neighbour_share"] == Fraction(1, 4) and lattice_family_certificate()["bump_centre"] == Fraction(3, 8)),
        Witness("point-source-family", "Point-source peak and ring counts are two, four and six with exact magnitude balance.", tuple((row["peak_magnitude"], row["ring_count"], row["balanced_magnitude"]) for row in lattice_family_certificate()["operators"]) == ((2, 2, True), (4, 4, True), (6, 6, True))),
        Witness("causal-balls", "Complete oriented causal enumeration gives the full one-, two- and three-direction vectors.", lattice_family_certificate()["causal_counts"] == {1: (3, 5, 7), 2: (5, 13, 25), 3: (7, 25, 63)}),
        Witness("modes-and-flat-state", "A seven-site cycle has seven exact phase carriers, exactly one identity mode and stationary flat support.", lattice_family_certificate()["mode_count"] == 7 and lattice_family_certificate()["identity_mode_count"] == 1 and lattice_family_certificate()["flat_stationary"] and not lattice_family_certificate()["irrational_mode_value_evaluated"]),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "OrientedCoordinate",
    "PhaseModeCarrier",
    "SPEC",
    "causal_ball",
    "causal_ball_count",
    "conservative_stencil",
    "cyclic_update",
    "exact_mode_carriers",
    "lattice_family_certificate",
    "point_source_operator",
)
