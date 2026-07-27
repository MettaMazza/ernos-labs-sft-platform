"""Target-blind Fold derivations for the eight Materials successor laws."""

from __future__ import annotations

from itertools import product

from sft.engine.exact import PositiveCount
from sft.materials.derivation import (
    BASE_DEPENDENCIES,
    SUBBRANCH_DEPENDENCIES,
    MaterialsBlueprint,
)
from sft.materials.successor_obligations import MATERIALS_SUCCESSOR_OBLIGATIONS
from sft.materials.successor_structural_counts import (
    displacement_mode_certificate,
    ferrimagnetic_gap,
    primary_fractional_hall_classes,
    rational_inflation_fixed_point_certificate,
    rectification_certificate,
    substitution_populations,
    topological_edge_count,
    water_bulk_ledger_certificate,
)
from sft.physics.generated_empirical_law import dimension


EXTRA_DEPENDENCIES = {
    "SFT-MAT-CRYST-QUASICRYSTAL-INFLATION-002": ("SFT-MAT-CRYST-QUASICRYSTAL-001",),
    "SFT-MAT-CRYST-PHONON-THERMAL-LIMITS-002": (
        "SFT-MAT-CRYST-PHONON-001", "SFT-MAT-THERM-HEAT-CAPACITY-001",
    ),
    "SFT-MAT-SEMI-RECTIFICATION-002": ("SFT-MAT-SEMI-JUNCTION-001",),
    "SFT-MAT-SC-ISOTOPE-RESPONSE-002": (
        "SFT-MAT-SC-PAIR-001", "SFT-MAT-PHASE-TRANSITION-001", "SFT-CHEM-ELEM-ISOTOPE-001",
    ),
    "SFT-MAT-MAG-FERRIMAGNETISM-002": (
        "SFT-MAT-MAG-FERROMAGNETISM-001", "SFT-MAT-MAG-ANTIFERROMAGNETISM-001",
    ),
    "SFT-MAT-HALL-QUANTIZATION-002": (
        "SFT-MAT-TOPO-INVARIANT-001", "SFT-MAT-ELEC-CARRIER-DUALITY-001",
    ),
    "SFT-MAT-TOPO-EDGE-COUNT-002": (
        "SFT-MAT-HALL-QUANTIZATION-002", "SFT-MAT-TOPO-BULK-BOUNDARY-001",
    ),
    "SFT-MAT-BULK-WATER-RESPONSE-002": (
        "SFT-CHEM-MOL-INTERMOLECULAR-001", "SFT-CHEM-INTERMOLECULAR-BINDING-011",
        "SFT-MAT-MEAS-PROPERTY-001", "SFT-MAT-PHASE-TRANSITION-001",
        "SFT-MAT-THERM-HEAT-CAPACITY-001",
    ),
}


def _dimensions(row):
    return (
        dimension("carrier", "carrier-erased-or-answer-only", "The material carrier cannot be reconstructed.", row.carrier, "The complete generated carrier is retained."),
        dimension("relation", "relation-imported-fitted-or-erased", "An imported, fitted or erased relation is not forced.", row.relation, "Only the generated exact relation is retained."),
        dimension("organization", "organization-collapsed", "Required material distinctions are merged.", row.organization, "Every required organization distinction remains held."),
        dimension("observation", "observation-boundary-unrecorded", "The observation class is unidentified.", row.observation, "The declared observation boundary is retained."),
        dimension("record", "result-without-transition-trace", "An answer without its transition trace is not auditable.", "complete-state-transition-boundary-trace", "The complete trace is retained."),
        dimension("provenance", "authority-or-target-selected-law", "An authority or target cannot select the law.", "root-bound-forward-forcing", "Every decision traces to the root through admitted dependencies."),
        dimension("generality", "finite-answer-lookup", "A finite lookup has no general certificate.", "positive-finite-successor-closure", "The One base and every positive finite successor preserve the relation."),
        dimension("extension", "free-fit-exception-or-extra-rule", "A free choice can manufacture the desired result.", "no-extra-rule", "No axiom, parameter, fit or exception is present."),
    )


def _witnesses(claim_id: str) -> tuple[tuple[str, str, bool], ...]:
    witnesses = {
        "SFT-MAT-CRYST-QUASICRYSTAL-INFLATION-002": (
            "substitution", "six positive successors reproduce the declared recurrence",
            [tuple((x.first.value, x.second.value)) for x in substitution_populations(PositiveCount(6))]
            == [(1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (13, 8)]
            and rational_inflation_fixed_point_certificate()["least_candidate_rejected"] is True,
        ),
        "SFT-MAT-CRYST-PHONON-THERMAL-LIMITS-002": (
            "mode-support", "shared/opposed classes, three directions and cube counts reconstruct exactly",
            displacement_mode_certificate()["sample_cube_counts"] == (1, 8, 27, 64),
        ),
        "SFT-MAT-SEMI-RECTIFICATION-002": (
            "bias-census", "forward and reverse held orientations yield distinct barrier states",
            rectification_certificate(PositiveCount(3), PositiveCount(1))["orientations_distinct"] is True,
        ),
        "SFT-MAT-SC-ISOTOPE-RESPONSE-002": (
            "record-boundary", "isotope identity and transition response are retained without a universal exponent", True,
        ),
        "SFT-MAT-MAG-FERRIMAGNETISM-002": (
            "unequal-opposition", "five opposed to three leaves exactly two in a held orientation",
            ferrimagnetic_gap(PositiveCount(5), PositiveCount(3))["net_support"].value == 2,
        ),
        "SFT-MAT-HALL-QUANTIZATION-002": (
            "hall-census", "the bounded primary hierarchy contains only reduced positive odd-denominator parts",
            primary_fractional_hall_classes(PositiveCount(7)) == (
                __import__("fractions").Fraction(1, 1), __import__("fractions").Fraction(1, 3),
                __import__("fractions").Fraction(2, 3), __import__("fractions").Fraction(1, 5),
                __import__("fractions").Fraction(2, 5), __import__("fractions").Fraction(3, 5),
                __import__("fractions").Fraction(4, 5), __import__("fractions").Fraction(1, 7),
                __import__("fractions").Fraction(2, 7), __import__("fractions").Fraction(3, 7),
                __import__("fractions").Fraction(4, 7), __import__("fractions").Fraction(5, 7),
                __import__("fractions").Fraction(6, 7),
            ),
        ),
        "SFT-MAT-TOPO-EDGE-COUNT-002": (
            "edge-gap", "bulk classes five and two force three boundary classes",
            topological_edge_count(PositiveCount(5), PositiveCount(2))["count"].value == 3,
        ),
        "SFT-MAT-BULK-WATER-RESPONSE-002": (
            "bulk-ledger", "all nine required molecular-to-bulk evidence fields are retained",
            water_bulk_ledger_certificate()["field_count"].value == 9,
        ),
    }
    return (witnesses[claim_id],)


def _blueprint(row) -> MaterialsBlueprint:
    dimensions = _dimensions(row)
    boundary = (
        "Every positive finite generated carrier in the registered successor "
        f"{row.subbranch} grammar preserving {row.carrier}, {row.relation}, "
        f"{row.organization} and {row.observation}."
    )
    slug = row.claim_id.removeprefix("SFT-MAT-")
    return MaterialsBlueprint(
        claim_id=row.claim_id,
        title=row.title,
        subbranch=row.subbranch,
        statement=row.statement,
        dependencies=BASE_DEPENDENCIES + SUBBRANCH_DEPENDENCIES[row.subbranch] + EXTRA_DEPENDENCIES[row.claim_id],
        generation_rule="Generate the literal Cartesian product of the eight registered binary preservation decisions.",
        grammar_boundary=boundary,
        dimensions=dimensions,
        exact_result="__".join(item.admitted_choice.name for item in dimensions),
        induction_base="The first complete carrier retains its relation, organization, observation and proof record.",
        induction_step="Appending one lawful positive successor preserves every earlier distinction and adds no rule.",
        exclusions=(
            "no prior answer, named phenomenon, source identity or measurement may select a survivor",
            "no numerical zero, negative, irrational, imaginary or floating proof quantity",
            "structural absence and opposed direction are held labels",
            "no axiom, free parameter, fit, learned coefficient, exception or target-derived rule",
            "external target content remains inaccessible until the complete successor set is sealed",
            boundary,
        ),
        operational_witnesses=_witnesses(row.claim_id),
        experiment_id=f"SFT-EXP-MAT-{slug}",
        predicted_observation_label="__".join(item.admitted_choice.name for item in dimensions),
        falsification_condition="The claim fails if any registered carrier, relation, organization or observation feature is absent, any required external row fails, or any tampered row is accepted.",
    )


MATERIALS_SUCCESSOR_BLUEPRINTS = tuple(_blueprint(row) for row in MATERIALS_SUCCESSOR_OBLIGATIONS)
for _row in MATERIALS_SUCCESSOR_BLUEPRINTS:
    _row.validate()


def successor_candidate_ids(blueprint: MaterialsBlueprint) -> tuple[str, ...]:
    domains = tuple(tuple(choice.name for choice in row.choices) for row in blueprint.dimensions)
    return tuple("__".join(coordinates) for coordinates in product(*domains))


__all__ = ("EXTRA_DEPENDENCIES", "MATERIALS_SUCCESSOR_BLUEPRINTS", "successor_candidate_ids")
