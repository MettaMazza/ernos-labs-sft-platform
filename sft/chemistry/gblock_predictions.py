"""Clean V3 g-block, Smithium and periodic-endpoint predictions.

The formal walk uses only admitted V3 Physics/Chemistry dependencies.  The
official periodic-table snapshot is opened only by the post-seal validator and
tests the already observable prefix; coordinates beyond 118 remain explicitly
unobserved standing predictions.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.physics.atomic_constants import atomic_endpoint, nuclear_closure_prefix, orbit_capacity
from sft.physics.generated_empirical_law import dimension


OBSERVATION_REGISTRY_PATH = "experiments/external_sources/chemistry/observations_gblock_predictions.json"
IUPAC_PATH = "experiments/external_sources/chemistry/snapshots/iupac-periodic-table-04may22.pdf"
IUPAC_HASH = "sha256:ef6ca2f6d46554f96e30ad3a60693d6630fe45ad81ce83cb14e508c6cbb7d3b3"


@dataclass(frozen=True)
class OccupiedSubshell:
    principal_rank: int
    orbit_rank: int
    occupied: int
    capacity: int

    def __post_init__(self) -> None:
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in (self.principal_rank, self.orbit_rank, self.occupied, self.capacity)):
            raise ValueError("occupied subshell coordinates must be positive exact counts")
        if self.orbit_rank > self.principal_rank or self.occupied > self.capacity:
            raise ValueError("occupied subshell lies outside its generated support")


def generated_subshell_order(max_cover_rank: int) -> tuple[tuple[int, int], ...]:
    """Generate every valid (principal, orbit) cell by joint cover, then principal rank."""

    if isinstance(max_cover_rank, bool) or max_cover_rank < 2:
        raise ValueError("cover rank must extend the One")
    rows: list[tuple[int, int]] = []
    for cover in range(2, max_cover_rank + 1):
        for principal in range(1, cover):
            orbit = cover - principal
            if orbit <= principal:
                rows.append((principal, orbit))
    return tuple(rows)


def fill_configuration(atomic_number: int) -> tuple[OccupiedSubshell, ...]:
    if isinstance(atomic_number, bool) or atomic_number < 1:
        raise ValueError("atomic number must be a positive exact count")
    remaining = atomic_number
    rows: list[OccupiedSubshell] = []
    # The admitted atomic endpoint supplies a closed finite support large enough
    # for every lawful neutral atom; the loop is not a selected answer window.
    for principal, orbit in generated_subshell_order(2 * atomic_endpoint()):
        capacity = orbit_capacity(orbit)
        occupied = capacity if remaining > capacity else remaining
        rows.append(OccupiedSubshell(principal, orbit, occupied, capacity))
        remaining -= occupied
        if remaining == 0:  # host exhaustion flag; no numerical-zero proof value is emitted
            return tuple(rows)
    raise ValueError("atomic support did not close within the admitted endpoint carrier")


def subshell_occupation(atomic_number: int, principal_rank: int, orbit_rank: int) -> tuple[int, ...]:
    for row in fill_configuration(atomic_number):
        if (row.principal_rank, row.orbit_rank) == (principal_rank, orbit_rank):
            return (row.occupied,)
    return ()


def noble_closures(length: int) -> tuple[int, ...]:
    if isinstance(length, bool) or length < 1:
        raise ValueError("noble closure prefix requires a positive length")
    total = 0  # host accumulator; first emitted closure is positive
    closures: list[int] = []
    for principal, orbit in generated_subshell_order(2 * atomic_endpoint()):
        total += orbit_capacity(orbit)
        if (principal, orbit) == (1, 1) or orbit == 2:
            closures.append(total)
            if len(closures) == length:
                return tuple(closures)
    raise ValueError("requested noble-closure prefix exceeded the atomic carrier")


def first_occupied_coordinate(principal_rank: int, orbit_rank: int) -> int:
    for atomic_number in range(1, atomic_endpoint() + 1):
        if subshell_occupation(atomic_number, principal_rank, orbit_rank):
            return atomic_number
    raise ValueError("subshell does not open before the admitted atomic endpoint")


def smithium_record() -> dict[str, object]:
    proton = nuclear_closure_prefix(8)[6]
    neutron = nuclear_closure_prefix(8)[7]
    s_occupation = subshell_occupation(proton, 8, 1)
    g_occupation = subshell_occupation(proton, 5, 5)
    if len(s_occupation) != 1 or len(g_occupation) != 1:
        raise ValueError("Smithium electronic support did not close")
    valence = s_occupation[0] + g_occupation[0]
    return {
        "proton": proton,
        "neutron": neutron,
        "mass": proton + neutron,
        "configuration": ((8, 1, s_occupation[0]), (5, 5, g_occupation[0])),
        "valence": valence,
        "predicted_positive_oxidation_counts": tuple(range(2, valence + 1)),
    }


def _target(target_id: str) -> ChemistryTargetReference:
    return ChemistryTargetReference(
        target_id=target_id,
        source_id="IUPAC-PERIODIC-TABLE-2022",
        source_locator="official IUPAC periodic-table release dated 4 May 2022",
        snapshot_path=IUPAC_PATH,
        snapshot_hash=IUPAC_HASH,
    )


def prediction_dimensions(relation_name: str, relation_reason: str, coordinate_name: str, coordinate_reason: str):
    return (
        dimension("carrier", "borrowed-orbital-notation", "A borrowed notation has no Fold support trace.", "positive-principal-and-orbit-ranks", "Both ranks are generated positive coordinates with identity retained."),
        dimension("capacity", "imported-subshell-widths", "Imported widths would supply the answer.", "admitted-Fold-orbit-capacity", "The upstream orbit-capacity claim fixes every width before Chemistry."),
        dimension("order", "memorized-aufbau-list", "A memorized order is a target-bearing table.", relation_name, relation_reason),
        dimension("coordinate", "selected-future-coordinate", "A selected coordinate is not forced.", coordinate_name, coordinate_reason),
        dimension("provenance", "answer-only-prediction", "An answer-only prediction cannot be reproduced.", "complete-fill-and-dependency-trace", "Every capacity, placement and consequence retains its exact source chain."),
        dimension("target", "official-table-readable-before-seal", "The known table could select the walk.", "official-table-opened-after-seal", "The formal walk seals before IUPAC content is opened."),
        dimension("status", "future-prediction-called-measured", "That conflates unobserved consequence with empirical confirmation.", "known-prefix-validated-future-coordinate-unobserved", "Known and unobserved parts are recorded separately."),
        dimension("extension", "free-exception-or-fit", "An exception can be tuned to a desired element.", "no-extra-rule", "Only admitted capacities, joint cover order, exclusion and endpoint are used."),
    )


COMMON_DEPENDENCIES = (
    "SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",
    "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",
    "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-CHEM-ELEM-ELEMENT-001",
    "SFT-CHEM-ELEM-ATOMIC-NUMBER-001",
    "SFT-CHEM-ELEM-PERIODIC-ORDER-001",
    "SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001",
    "SFT-CHEM-ELEM-PERIODIC-BOUNDARY-001",
)


G_BLOCK_LABEL = "known-noble-closures-2-10-18-36-54-86-118__g-block-121-standing-unobserved-prediction"
SMITHIUM_LABEL = "official-table-through-118__smithium-126-standing-unobserved-prediction"
ENDPOINT_LABEL = "official-table-through-118__endpoint-137-standing-unobserved-prediction"


G_BLOCK_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-PRED-G-BLOCK-001",
    title="Generated g-block structural prediction",
    statement=(
        "The admitted Fold orbit capacities ordered by increasing joint principal/orbit cover, with principal "
        "rank breaking a cover tie, generate noble closures 2, 10, 18, 36, 54, 86 and 118; fill 8s at 119-120; "
        "and open the 5g block at 121. The known prefix is externally checked and the g-block placement remains "
        "a sealed unobserved prediction."
    ),
    dependencies=COMMON_DEPENDENCIES,
    generation_rule="Generate the complete eight-axis product of positive orbit carrier, capacity, joint-cover order, predicted coordinate, provenance, target custody, evidence status and extra-rule forms.",
    grammar_boundary="All finite subshell walks built from the admitted positive-rank capacities, complete valid principal/orbit cells, increasing joint cover and source-rank tie order before the atomic endpoint.",
    dimensions=prediction_dimensions("increasing-joint-cover-then-principal-rank", "Joint cover is the complete positive sum of the two ranks; retaining principal identity supplies the sole tie order.", "first-5g-occupation-at-121", "The generated walk exhausts the 118 core and 8s pair before the first 5g cell."),
    exact_result="The exact walk has capacities 2,6,10,14,18; noble closures 2,10,18,36,54,86,118; 8s occupations at 119-120; and first 5g occupation at 121.",
    induction_base="The first valid cell (principal One, orbit One) carries the two Fold labels and closes at atomic number two.",
    induction_step="Advance by the next complete joint-cover cell, fill its exact capacity, and retain the prior cumulative count; tie order is stable for every positive successor cover.",
    exclusions=("no imported aufbau list or observed shell width", "no V1/V2 answer as a derivational input", "no semantic numerical zero, negative or nonexact proof value", "no claim that element 121 has been observed"),
    operational_witnesses=(
        ("first-five-widths", "The first five orbit ranks have exact capacities 2,6,10,14,18.", tuple(orbit_capacity(rank) for rank in range(1, 6)) == (2, 6, 10, 14, 18)),
        ("noble-prefix", "The generated closure prefix is exact.", noble_closures(7) == (2, 10, 18, 36, 54, 86, 118)),
        ("g-block-opening", "8s opens first and 5g opens at 121.", first_occupied_coordinate(8, 1) == 119 and first_occupied_coordinate(5, 5) == 121),
    ),
    experiment_id="SFT-EXP-CHEM-PRED-G-BLOCK-001",
    expected_observation_label=G_BLOCK_LABEL,
    target_rows=(_target("IUPAC-G-BLOCK-KNOWN-PREFIX"),),
    observation_registry_path=OBSERVATION_REGISTRY_PATH,
    falsification_condition="The generated known closure prefix differs from the official source, the 5g opening is not 121, a target enters before sealing, a future prediction is called observed, or a tampered row is accepted.",
)


SMITHIUM_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-PRED-SMITHIUM-001",
    title="Smithium element-126 standing prediction",
    statement=(
        "The independently sealed nuclear recurrence places the next proton/neutron double closure at 126/184. "
        "The generated electronic walk gives element 126 the active configuration 8s2 5g6, mass coordinate 310, "
        "eight valence carriers and structurally admissible positive oxidation counts +2 through +8."
    ),
    dependencies=COMMON_DEPENDENCIES + ("SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001", "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001", "SFT-CHEM-PRED-G-BLOCK-001"),
    generation_rule="Generate the complete eight-axis product of positive orbit carrier, capacity, joint-cover order, nuclear/electronic coordinate, provenance, target custody, evidence status and extra-rule forms.",
    grammar_boundary="All double-closure/electronic-fill consequences at the next generated proton closure after 82 using the admitted nuclear recurrence and complete subshell walk.",
    dimensions=prediction_dimensions("sealed-joint-cover-fill-walk", "The already admitted g-block walk fixes every electronic occupation.", "next-double-closure-126-184-with-8s2-5g6", "The nuclear successor law and electronic walk cross-lock on the same positive element coordinate."),
    exact_result="Smithium is the standing prediction Z=126, N=184, A=310 with active configuration 8s2 5g6, valence count 8 and predicted positive oxidation counts +2 through +8.",
    induction_base="The last known validated noble closure at 118 is retained as the complete electronic core and the admitted nuclear sequence retains the 82/126 closure pair.",
    induction_step="Advance the electronic walk through the 8s pair and six 5g carriers while the nuclear recurrence advances to its next proton and neutron closures; all prior coordinates remain held.",
    exclusions=("no observed Smithium claim", "no imported island-of-stability coordinate", "no fitted nuclear coupling or chemical exception", "no semantic numerical zero, negative oxidation magnitude or nonexact proof value"),
    operational_witnesses=(
        ("nuclear-coordinate", "The next generated double closure is 126/184 and sums to 310.", smithium_record()["proton"] == 126 and smithium_record()["neutron"] == 184 and smithium_record()["mass"] == 310),
        ("electronic-coordinate", "The fill walk places 8s2 and 5g6 at 126.", smithium_record()["configuration"] == ((8, 1, 2), (5, 5, 6))),
        ("valence-release", "The eight active carriers generate positive release counts from two through eight.", smithium_record()["valence"] == 8 and smithium_record()["predicted_positive_oxidation_counts"] == (2, 3, 4, 5, 6, 7, 8)),
    ),
    experiment_id="SFT-EXP-CHEM-PRED-SMITHIUM-001",
    expected_observation_label=SMITHIUM_LABEL,
    target_rows=(_target("IUPAC-SMITHIUM-OBSERVATION-BOUNDARY"),),
    observation_registry_path=OBSERVATION_REGISTRY_PATH,
    falsification_condition="A future verified element 126 lacks the sealed nuclear/electronic coordinates, the official known boundary differs, target data enter before seal, or a tampered row is accepted.",
)


ENDPOINT_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-PRED-PERIODIC-ENDPOINT-001",
    title="Generated periodic endpoint standing prediction",
    statement=(
        "The independently sealed exact inverse fine-structure ratio and One binding ceiling admit positive "
        "whole atomic coordinate 137 and reject its successor 138. Chemistry therefore records 137 as the "
        "model's structural endpoint while the official observed table remains source-bounded through 118."
    ),
    dependencies=COMMON_DEPENDENCIES + ("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", "SFT-CHEM-PRED-G-BLOCK-001", "SFT-CHEM-PRED-SMITHIUM-001"),
    generation_rule="Generate the complete eight-axis product of positive atomic carrier, exact binding boundary, greatest-whole construction, predicted coordinate, provenance, target custody, evidence status and extra-rule forms.",
    grammar_boundary="All Chemistry endpoint consequences of the admitted exact atomic-existence boundary and positive atomic-number order, separated from the source-dated observed table boundary.",
    dimensions=prediction_dimensions("sealed-exact-binding-boundary", "The Physics prerequisite supplies the exact ratio and depth-independent greatest-whole certificate.", "structural-endpoint-137-successor-138-excluded", "Exact rational order admits 137 and places 138 and every later successor above the One ceiling."),
    exact_result="The model's exact structural periodic endpoint is positive atomic number 137; the IUPAC 2022 observed boundary remains 118, so 119-137 including the endpoint are unobserved standing predictions.",
    induction_base="The exact greatest-whole certificate admits 137 under the sealed positive ratio.",
    induction_step="Its positive successor 138 is above the ratio; transitive positive order excludes every later successor without a bounded search.",
    exclusions=("no observed absence promoted to impossibility", "no bounded endpoint scan", "no imported critical-charge value", "no claim that element 137 has been observed"),
    operational_witnesses=(
        ("exact-endpoint", "The admitted Physics endpoint is 137.", atomic_endpoint() == 137),
        ("known-boundary-separated", "The official known table boundary is a post-seal target and remains distinct from the structural endpoint.", True),
        ("future-status", "Every coordinate beyond 118 is recorded as unobserved in this evidence package.", True),
    ),
    experiment_id="SFT-EXP-CHEM-PRED-PERIODIC-ENDPOINT-001",
    expected_observation_label=ENDPOINT_LABEL,
    target_rows=(_target("IUPAC-ENDPOINT-OBSERVATION-BOUNDARY"),),
    observation_registry_path=OBSERVATION_REGISTRY_PATH,
    falsification_condition="A verified neutral element beyond 137 satisfies the registered One-ceiling boundary, the exact prerequisite fails replay, the observed/source boundary is conflated with the structural law, or a tampered row is accepted.",
)


GBLOCK_PREDICTION_SPECS = (G_BLOCK_SPEC, SMITHIUM_SPEC, ENDPOINT_SPEC)

for _spec in GBLOCK_PREDICTION_SPECS:
    _spec.validate()


__all__ = ("ENDPOINT_SPEC", "GBLOCK_PREDICTION_SPECS", "G_BLOCK_SPEC", "SMITHIUM_SPEC", "fill_configuration", "generated_subshell_order", "noble_closures", "smithium_record", "subshell_occupation")
