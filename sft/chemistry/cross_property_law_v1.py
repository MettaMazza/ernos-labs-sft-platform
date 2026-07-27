"""Fold-native complete cross-property molecular-vector law for PROP-014.

One retained structural carrier is shared by every applicable property law.
Each property result is an exact named projection of that carrier, never a
separately fitted model.  Adding a new lawful projection cannot alter an
existing projection.  External values and target payloads are unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ExactPropertyProjection:
    property_family: HeldLabel
    generating_relation: HeldLabel
    result_orientation: HeldLabel
    exact_result: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.property_family, HeldLabel) or self.property_family.family != "molecular-property-family":
            raise InadmissibleExactValue("property projection requires a held property family")
        if not isinstance(self.generating_relation, HeldLabel) or self.generating_relation.family != "admitted-property-relation":
            raise InadmissibleExactValue("property projection requires its admitted generating relation")
        if not isinstance(self.result_orientation, HeldLabel) or self.result_orientation.family != "property-result-orientation":
            raise InadmissibleExactValue("property projection requires a held result orientation")
        if not isinstance(self.exact_result, (PositiveRatio, EmptyOne)):
            raise InadmissibleExactValue("property projection result must be exact positive or structural EmptyOne")


@dataclass(frozen=True)
class CrossPropertyMolecularCarrier:
    structural_carrier_id: HeldLabel
    constitution: HeldLabel
    state_identity: HeldLabel
    charge_identity: HeldLabel
    geometry_and_symmetry: HeldLabel
    observation_condition: HeldLabel
    applicable_property_families: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        required = (
            (self.structural_carrier_id, "structural-molecular-carrier"),
            (self.constitution, "molecular-constitution"),
            (self.state_identity, "molecular-state"),
            (self.charge_identity, "held-charge-identity"),
            (self.geometry_and_symmetry, "geometry-symmetry-carrier"),
            (self.observation_condition, "measurement-condition"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("cross-property carrier lost a required held field")
        if not self.applicable_property_families or any(
            not isinstance(value, HeldLabel) or value.family != "molecular-property-family"
            for value in self.applicable_property_families
        ):
            raise InadmissibleExactValue("cross-property carrier requires a nonempty property support")
        if len(set(self.applicable_property_families)) != len(self.applicable_property_families):
            raise InadmissibleExactValue("cross-property carrier duplicated a property family")


def compose_exact_property_vector(
    carrier: CrossPropertyMolecularCarrier,
    projections: tuple[ExactPropertyProjection, ...],
) -> tuple[ExactPropertyProjection, ...]:
    """Close one exact vector on one carrier without a per-property fit."""

    if not isinstance(carrier, CrossPropertyMolecularCarrier) or not isinstance(projections, tuple) or not projections:
        raise InadmissibleExactValue("cross-property vector requires one carrier and nonempty projections")
    labels = tuple(item.property_family for item in projections)
    if len(set(labels)) != len(labels):
        raise InadmissibleExactValue("a property family may occur only once in one exact vector")
    if set(labels) != set(carrier.applicable_property_families):
        raise InadmissibleExactValue("projection support differs from the carrier's complete applicable support")
    return projections


def project_exact_property(
    vector: tuple[ExactPropertyProjection, ...],
    property_family: HeldLabel,
) -> ExactPropertyProjection:
    """Select the unique exact named projection without changing its result."""

    matches = tuple(item for item in vector if item.property_family == property_family)
    if len(matches) != 1:
        raise InadmissibleExactValue("property projection is absent or non-unique")
    return matches[0]


def lawful_projection_extension_preserves_existing(
    carrier: CrossPropertyMolecularCarrier,
    vector: tuple[ExactPropertyProjection, ...],
    extension: ExactPropertyProjection,
) -> bool:
    """Appending one new lawful family preserves every existing projection."""

    if extension.property_family in {item.property_family for item in vector}:
        raise InadmissibleExactValue("projection extension must add a new property family")
    extended_carrier = CrossPropertyMolecularCarrier(
        carrier.structural_carrier_id, carrier.constitution, carrier.state_identity,
        carrier.charge_identity, carrier.geometry_and_symmetry, carrier.observation_condition,
        carrier.applicable_property_families + (extension.property_family,),
    )
    extended = compose_exact_property_vector(extended_carrier, vector + (extension,))
    return all(project_exact_property(extended, item.property_family) == item for item in vector)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-COMBINATORICS-001", "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-COMPOSITION-001",
    "SFT-CHEM-EQUILIBRIUM-BOND-LENGTH-001", "SFT-CHEM-BOND-DISSOCIATION-ENERGY-002",
    "SFT-CHEM-MOLECULAR-BOND-ANGLE-003", "SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004",
    "SFT-CHEM-MOLECULAR-DIPOLE-MAGNITUDE-005", "SFT-CHEM-MOLECULAR-POLARIZABILITY-006",
    "SFT-CHEM-MOLECULAR-IONIZATION-ENERGY-007", "SFT-CHEM-MOLECULAR-ELECTRON-AFFINITY-008",
    "SFT-CHEM-VIBRATIONAL-FREQUENCY-009", "SFT-CHEM-ROTATIONAL-CONSTANT-010",
    "SFT-CHEM-INTERMOLECULAR-BINDING-011", "SFT-CHEM-MOLECULAR-MAGNETIC-RESPONSE-012",
    "SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "separate-carrier-per-property", "Separate carriers permit property-specific identity drift.", "one-complete-structural-carrier", "Every applicable property projects from one retained carrier."),
    dimension("support", "selected-or-favorable-property-subset", "A selected subset can hide absent or disagreeing properties.", "complete-applicable-property-support", "Every registered applicable property family remains explicit."),
    dimension("projection", "answer-only-property-values", "Bare answers erase the relation that generated each result.", "named-admitted-relation-projections", "Each exact result retains its property family and admitted generating law."),
    dimension("parameter", "per-property-fit-or-correction", "A separate coefficient lets each target select its output.", "zero-parameter-shared-carrier-projection", "No projection introduces a coefficient, residual or target-derived field."),
    dimension("absence", "delete-unmeasured-or-inapplicable-row", "Deletion makes the vector appear more complete than the source.", "structural-EmptyOne-and-unjoined-custody-retained", "Absent results and nonjoinable identities remain explicit."),
    dimension("prediction", "target-payload-or-hash-readable-before-seal", "Target content or even its hash can select the carrier or subset.", "complete-value-free-identity-seal", "All 9,025 identities and 13 property families seal before target access."),
    dimension("record", "single-species-showcase", "A showcase species does not establish complete cross-property custody.", "complete-13-family-source-row-custody", "Every admitted PROP-001 through PROP-013 source row is retained."),
    dimension("extension", "recompute-or-refit-existing-properties", "Refitting after a new property destroys prior invariance.", "append-only-depth-independent-projection-extension", "Adding one lawful family preserves every existing projection exactly."),
)


EXACT_RESULT = (
    "one-complete-structural-carrier__complete-applicable-property-support__named-admitted-relation-projections__"
    "zero-parameter-shared-carrier-projection__structural-EmptyOne-and-unjoined-custody-retained__"
    "complete-value-free-identity-seal__complete-13-family-source-row-custody__"
    "append-only-depth-independent-projection-extension"
)


def _projection(label: str, numerator: int, denominator: int) -> ExactPropertyProjection:
    return ExactPropertyProjection(
        HeldLabel("molecular-property-family", label), HeldLabel("admitted-property-relation", label + "-law"),
        HeldLabel("property-result-orientation", "exact-positive"), PositiveRatio.from_pair(numerator, denominator),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    p1, p2, p3 = _projection("bond-length", 3, 2), _projection("vibration", 5, 3), _projection("formation", 7, 4)
    carrier = CrossPropertyMolecularCarrier(
        HeldLabel("structural-molecular-carrier", "held-molecule"), HeldLabel("molecular-constitution", "held-constitution"),
        HeldLabel("molecular-state", "held-state"), HeldLabel("held-charge-identity", "held-charge"),
        HeldLabel("geometry-symmetry-carrier", "held-geometry-symmetry"), HeldLabel("measurement-condition", "held-condition"),
        (p1.property_family, p2.property_family),
    )
    vector = compose_exact_property_vector(carrier, (p1, p2))
    duplicate_rejected = False
    try:
        compose_exact_property_vector(carrier, (p1, p1))
    except InadmissibleExactValue:
        duplicate_rejected = True
    return (
        ("one-carrier-vector", "Two property relations close on one retained carrier.", len(vector) == 2),
        ("exact-named-projection", "Selecting vibration returns its unchanged exact result.", project_exact_property(vector, p2.property_family) == p2),
        ("duplicate-family-rejected", "One property family cannot be fitted twice.", duplicate_rejected),
        ("depth-independent-extension", "Appending formation preserves bond-length and vibration.", lawful_projection_extension_preserves_existing(carrier, vector, p3)),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "CrossPropertyMolecularCarrier", "ExactPropertyProjection", "compose_exact_property_vector",
    "lawful_projection_extension_preserves_existing", "project_exact_property",
)
