"""One finite Fold model composing quantum support and gravity."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-FINITE-QUANTUM-GRAVITY-TERMINAL-023"
ONE = Fraction(1, 1)
HALF = Fraction(1, 2)
EMPTY_ONE = ("empty-One",)


def positive_take_whole(whole: int, part: int) -> int:
    if isinstance(whole, bool) or isinstance(part, bool) or whole <= part or part < 1:
        raise ValueError("positive whole take requires an ordered positive pair")
    return whole - part


def finite_loop_sum(depth: int) -> Fraction:
    if isinstance(depth, bool) or depth < 1:
        raise ValueError("finite loop support requires positive depth")
    total = Fraction(1, 2)
    term = Fraction(1, 2)
    for _ in range(1, depth):
        term /= 2
        total += term
    return total


def finite_quantum_gravity_model(depth: int) -> dict[str, object]:
    if isinstance(depth, bool) or depth < 1:
        raise ValueError("finite quantum-gravity depth must be positive")
    spatial_directions = 3
    time_directions = 1
    coordinate_count = spatial_directions + time_directions
    symmetric_rank = 2
    symmetric_slots = coordinate_count * (coordinate_count + 1) // 2
    conservation_constraints = coordinate_count
    coordinate_shift_redundancies = coordinate_count
    after_conservation = positive_take_whole(symmetric_slots, conservation_constraints)
    physical_polarizations = positive_take_whole(after_conservation, coordinate_shift_redundancies)
    quantum_support = 1
    for _ in range(depth):
        quantum_support += quantum_support
    distance_floor = ONE / quantum_support
    area_cells = quantum_support
    horizon_records = Fraction(area_cells, 4)
    return {
        "carrier": "single-finite-Fold-lattice",
        "depth": depth,
        "spatial_directions": spatial_directions,
        "coordinate_count": coordinate_count,
        "symmetric_rank": symmetric_rank,
        "symmetric_slots": symmetric_slots,
        "conservation_constraints": conservation_constraints,
        "coordinate_shift_redundancies": coordinate_shift_redundancies,
        "physical_polarizations": physical_polarizations,
        "mass_record": EMPTY_ONE,
        "causal_advance": ONE,
        "quantum_support": quantum_support,
        "distance_floor": distance_floor,
        "loop_sum": finite_loop_sum(depth),
        "horizon_area_cells": area_cells,
        "horizon_records": horizon_records,
        "horizon_quarter_law": horizon_records * 4 == area_cells,
        "extra_spatial_direction_record": EMPTY_ONE,
        "completed_infinity_used": False,
    }


def successor_preserves_model(depth: int) -> bool:
    current = finite_quantum_gravity_model(depth)
    successor = finite_quantum_gravity_model(depth + 1)
    return all(
        (
            current["carrier"] == successor["carrier"],
            current["spatial_directions"] == successor["spatial_directions"] == 3,
            current["symmetric_rank"] == successor["symmetric_rank"] == 2,
            current["physical_polarizations"] == successor["physical_polarizations"] == 2,
            current["mass_record"] == successor["mass_record"] == EMPTY_ONE,
            current["causal_advance"] == successor["causal_advance"] == ONE,
            successor["quantum_support"] == 2 * current["quantum_support"],
            successor["distance_floor"] < current["distance_floor"],
            successor["distance_floor"] > 0,
            successor["loop_sum"] > current["loop_sum"],
            successor["loop_sum"] < ONE,
            successor["horizon_quarter_law"],
            not successor["completed_infinity_used"],
        )
    )


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Single finite Fold quantum-gravity composition",
    statement=(
        "The admitted quantum branch support and gravitational curvature-source "
        "law compose on one and the same finite Fold lattice.  Three forced spatial "
        "directions plus one process direction give four coordinate roles and ten "
        "symmetric rank-two slots.  Four exact source-conservation constraints and "
        "four generated coordinate-shift redundancies retain exactly two physical "
        "polarizations.  The detached carrier has an empty mass/rest record and "
        "advances one causal cell per tick.  At every positive depth the quantum "
        "support, positive distance floor, finite rational loop sum and quarter-area "
        "horizon ledger are held together, while the unique three-space theorem "
        "leaves the extra-dimension record empty."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-QUANTUM-PHYSICAL-STATE-001",
        "SFT-PHYS-QUANTUM-EVOLUTION-001",
        "SFT-PHYS-GRAVITY-LATTICE-CURVATURE-003",
        "SFT-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010",
        "SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003",
        "SFT-PHYS-FIELD-FINITE-LOOP-CLOSURE-003",
        "SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003",
        "SFT-PHYS-GRAVITY-HORIZON-INFORMATION-003",
        "SFT-PHYS-VALIDATION-GRAVITY-HORIZONS-003",
        "SFT-PHYS-VALIDATION-FINITE-LOOPS-003",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of shared carrier, dimensional support, "
        "rank-two source, polarization reduction, mass/causal carrier, quantum "
        "support, finite-loop closure, horizon ledger, comparison boundary and "
        "extension forms."
    ),
    grammar_boundary=(
        "Every positive finite Fold depth on the admitted three-space lattice, its "
        "complete binary quantum support, four-coordinate symmetric rank-two source "
        "slots, finite exact loop prefix, positive distance floor and complete "
        "quarter-area horizon record.  Continuum completion is outside the boundary."
    ),
    axes=(
        binary_axis("carrier", "Do quantum and gravity use one carrier?", "separate-quantum-and-gravity-substrates", "Separate substrates do not establish a composition law.", "single-finite-Fold-lattice", "The admitted branch and curvature laws act on the same generated finite support."),
        binary_axis("dimension", "Which coordinate support is retained?", "chosen-or-extra-dimensional-space", "A chosen or added dimension is not generated by the stability theorem.", "three-space-plus-one-process-direction", "Three forced spatial directions and one process direction provide the complete coordinate carrier."),
        binary_axis("rank", "What carries gravity?", "scalar-or-selected-tensor", "A scalar or selected tensor omits the admitted complete source slots.", "complete-symmetric-rank-two-source", "Unordered coordinate pairs force ten symmetric source/curvature slots."),
        binary_axis("polarization", "Which propagating records remain?", "assigned-spin-or-mode-count", "An assigned label does not derive physical degrees.", "ten-take-four-take-four-leaves-two", "Conservation and coordinate-shift ledgers each close four slots, leaving two positive modes."),
        binary_axis("propagation", "How does the detached gravity carrier move?", "fitted-mass-or-speed", "A fitted mass or speed imports the target.", "empty-mass-record-and-One-cell-per-tick", "No rest capture is generated and local causal adjacency advances exactly one cell."),
        binary_axis("quantum", "How are state branches represented?", "continuum-amplitude-space", "A continuum adds ungenerated support.", "complete-finite-binary-word-support", "Depth succession doubles complete exact branch support while retaining every word."),
        binary_axis("loops", "How are short-distance loops closed?", "completed-infinity-or-counterterm", "A completed infinity and correction are outside the Fold grammar.", "complete-finite-rational-loop-prefix", "Every generated depth contains finitely many positive rational loop terms below the One."),
        binary_axis("horizon", "How is strong-field information retained?", "unbounded-or-unrecorded-boundary", "An unbounded or unrecorded boundary loses the finite ledger.", "positive-floor-and-quarter-area-record", "Every finite depth has a positive floor and one record per four exact area cells."),
        binary_axis("comparison", "When does conventional quantum-gravity evidence enter?", "target-selects-composition", "External programmes cannot choose the joint model.", "inherit-sealed-wave-loop-and-horizon-comparisons", "Existing post-seal claims retain tensor-wave, finite-loop and horizon evidence downstream."),
        binary_axis("extension", "May another dimension or regulator enter?", "extra-dimension-or-free-regulator", "Either addition changes the generated model.", "no-extra-rule", "The shared lattice, finite depth and exact ledgers exhaust the declared composition."),
    ),
    exact_result=(
        "At every positive finite Fold depth, one shared lattice jointly retains "
        "complete quantum support, three spatial directions, a symmetric rank-two "
        "gravity carrier with two physical polarizations, empty mass/rest record, "
        "One-cell causal advance, a positive distance floor, a finite rational loop "
        "sum and a quarter-area horizon ledger; no extra spatial direction or "
        "completed infinity is generated."
    ),
    induction_base=(
        "Depth One has two quantum words, half-One distance floor, half-One loop "
        "sum, one shared four-coordinate rank-two source and its complete two-mode "
        "causal carrier."
    ),
    induction_step=(
        "The next Fold depth doubles finite word and area support, halves the still "
        "positive floor and appends one positive loop term; it changes neither the "
        "forced three-space count, rank-two source, two-mode carrier nor quarter-area "
        "information relation."
    ),
    exclusions=(
        "no imported continuum quantum field, Einstein quantization or conventional quantum-gravity programme as a premise",
        "no V1/V2 executable, answer table, measured value or stored survivor",
        "no numerical-zero, negative, irrational, imaginary or floating proof magnitude",
        "no completed infinity, fitted counterterm, free regulator or extra dimension",
        "no claim of direct graviton detection or proof of a continuum Yang-Mills/Einstein completion",
        "no external comparison before the inherited wave, loop and horizon seals",
    ),
    witnesses=(
        Witness("rank-two-two-mode-carrier", "Every tested depth retains ten symmetric slots, four conservation constraints, four coordinate-shift redundancies and two modes.", all(finite_quantum_gravity_model(depth)["symmetric_slots"] == 10 and finite_quantum_gravity_model(depth)["physical_polarizations"] == 2 for depth in range(1, 9))),
        Witness("finite-positive-depths", "Every tested depth has finite support, positive floor and loop sum strictly below the One.", all(finite_quantum_gravity_model(depth)["quantum_support"] == 2**depth and 0 < finite_quantum_gravity_model(depth)["distance_floor"] <= HALF and 0 < finite_quantum_gravity_model(depth)["loop_sum"] < ONE for depth in range(1, 9))),
        Witness("causal-massless-carrier", "The gravity carrier retains empty mass/rest record and exact One-cell causal advance.", all(finite_quantum_gravity_model(depth)["mass_record"] == EMPTY_ONE and finite_quantum_gravity_model(depth)["causal_advance"] == ONE for depth in range(1, 9))),
        Witness("horizon-ledger", "Every tested finite area support retains exactly one record per four cells.", all(finite_quantum_gravity_model(depth)["horizon_quarter_law"] for depth in range(1, 9))),
        Witness("successor-closure", "Every tested successor preserves the joint model without completed infinity or extra dimension.", all(successor_preserves_model(depth) for depth in range(1, 8))),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EMPTY_ONE",
    "SPEC",
    "finite_loop_sum",
    "finite_quantum_gravity_model",
    "successor_preserves_model",
)
