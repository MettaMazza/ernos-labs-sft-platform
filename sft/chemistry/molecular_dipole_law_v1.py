"""Fold-native molecular-dipole organization and exact magnitude-square law.

A molecular dipole is not a signed scalar.  It is a retained charge-distinction
carrier with a held orientation and a finite set of mutually distinct component
axes.  Symmetry closes forbidden components to structural ``EmptyOne``.  Each
surviving component has an exact positive magnitude.  The orientation-free
magnitude relation is forced without an irrational square root: the exact
squared magnitude is the Junction of the exact positive component squares.

No measured dipole, conventional signed direction, field equation, charge
model, continuum vector space, fitted coefficient or floating value occurs in
this executable law.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Union

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension


ExactDipoleMagnitude = Union[EmptyOne, PositiveRatio]


@dataclass(frozen=True)
class DipoleComponent:
    axis: HeldLabel
    orientation: HeldLabel
    magnitude: PositiveRatio

    def __post_init__(self) -> None:
        if self.axis.family != "dipole-axis":
            raise InadmissibleExactValue("dipole component requires a retained axis")
        if self.orientation.family != "held-dipole-orientation":
            raise InadmissibleExactValue("dipole direction must remain a held orientation")
        if not isinstance(self.magnitude, PositiveRatio):
            raise InadmissibleExactValue("dipole component magnitude must be an exact positive ratio")


def exact_squared_magnitude(components: tuple[DipoleComponent, ...]) -> ExactDipoleMagnitude:
    """Junction all retained component squares without taking a square root."""

    if not isinstance(components, tuple):
        raise InadmissibleExactValue("dipole components require a finite generated tuple")
    if not components:
        return EMPTY_ONE
    if any(not isinstance(component, DipoleComponent) for component in components):
        raise InadmissibleExactValue("dipole component support contains an invalid form")
    axes = tuple(component.axis for component in components)
    if len(set(axes)) != len(axes):
        raise InadmissibleExactValue("a dipole axis cannot be counted twice")
    squares = tuple(component.magnitude.fraction**2 for component in components)
    joined = squares[0]
    for part in squares[1:]:
        joined += part
    if joined.numerator < 1 or joined.denominator < 1:
        raise InadmissibleExactValue("dipole square Junction left the exact positive domain")
    return PositiveRatio.from_pair(joined.numerator, joined.denominator)


SYMMETRY_AXES = {
    "inversion-exchange-symmetric-homonuclear-diatomic": (),
    "exchange-symmetric-equal-endpoint-isotopologue": ("principal-b",),
    "isotope-distinguished-principal-axis-carrier": ("principal-a", "principal-b"),
}


@dataclass(frozen=True)
class MolecularDipoleCarrier:
    species: HeldLabel
    molecular_state: HeldLabel
    geometry: HeldLabel
    charge_distinction_carrier: HeldLabel
    symmetry: HeldLabel
    component_axes: tuple[HeldLabel, ...]
    magnitude_definition: HeldLabel

    def __post_init__(self) -> None:
        if self.species.family != "molecular-species":
            raise InadmissibleExactValue("dipole carrier must retain a named species")
        if self.molecular_state.family != "molecular-state":
            raise InadmissibleExactValue("dipole carrier must retain molecular state")
        if self.geometry.family != "molecular-geometry":
            raise InadmissibleExactValue("dipole carrier must retain molecular geometry")
        if self.charge_distinction_carrier.family != "charge-distinction-carrier":
            raise InadmissibleExactValue("dipole carrier must retain complete charge distinction")
        if self.symmetry.family != "molecular-symmetry" or self.symmetry.label not in SYMMETRY_AXES:
            raise InadmissibleExactValue("dipole carrier symmetry lies outside the registered boundary")
        if any(axis.family != "dipole-axis" for axis in self.component_axes):
            raise InadmissibleExactValue("dipole component axes must remain held labels")
        expected = SYMMETRY_AXES[self.symmetry.label]
        if tuple(axis.label for axis in self.component_axes) != expected:
            raise InadmissibleExactValue("component support does not follow the retained symmetry class")
        if self.magnitude_definition != HeldLabel(
            "dipole-magnitude-definition", "exact-Junction-of-positive-component-squares"
        ):
            raise InadmissibleExactValue("dipole magnitude definition changed")

    @property
    def structural_magnitude_class(self) -> HeldLabel:
        if not self.component_axes:
            return HeldLabel("dipole-magnitude-class", "structural-EmptyOne")
        return HeldLabel(
            "dipole-magnitude-class",
            "one-positive-component" if len(self.component_axes) == 1 else "multiple-orthogonal-positive-components",
        )


def registered_molecular_dipole_carriers() -> tuple[MolecularDipoleCarrier, ...]:
    """Return the complete value-free PROP-005 species and symmetry boundary."""

    definition = HeldLabel(
        "dipole-magnitude-definition", "exact-Junction-of-positive-component-squares"
    )
    state = HeldLabel("molecular-state", "gas-phase-ground-vibrational-effective-dipole")
    rows = (
        (
            "H2", "homonuclear-diatomic",
            "exchange-identical-two-endpoint-charge-organization",
            "inversion-exchange-symmetric-homonuclear-diatomic", (),
        ),
        (
            "D2", "homonuclear-diatomic",
            "exchange-identical-two-endpoint-charge-organization",
            "inversion-exchange-symmetric-homonuclear-diatomic", (),
        ),
        (
            "H2O", "bent-water-triatomic",
            "one-oxygen-centred-two-endpoint-electronic-charge-organization",
            "exchange-symmetric-equal-endpoint-isotopologue", ("principal-b",),
        ),
        (
            "D2O", "bent-water-triatomic",
            "one-oxygen-centred-two-endpoint-electronic-charge-organization",
            "exchange-symmetric-equal-endpoint-isotopologue", ("principal-b",),
        ),
        (
            "HDO", "bent-water-triatomic",
            "one-oxygen-centred-two-endpoint-electronic-charge-organization",
            "isotope-distinguished-principal-axis-carrier", ("principal-a", "principal-b"),
        ),
    )
    return tuple(
        MolecularDipoleCarrier(
            HeldLabel("molecular-species", species),
            state,
            HeldLabel("molecular-geometry", geometry),
            HeldLabel("charge-distinction-carrier", charge),
            HeldLabel("molecular-symmetry", symmetry),
            tuple(HeldLabel("dipole-axis", axis) for axis in axes),
            definition,
        )
        for species, geometry, charge, symmetry, axes in rows
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
    "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
    "SFT-PHYS-ATOMIC-FIELD-SPLITTING-TERMINAL-005",
    "SFT-CHEM-BOND-POLARITY-001",
    "SFT-CHEM-MOL-GEOMETRY-001",
    "SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005",
    "SFT-CHEM-NUCLEAR-ELECTRONIC-COMPOSITION-012",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-MOLECULAR-BOND-ANGLE-003",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier", "answer-only-dipole-scalar",
        "A scalar answer erases species, state, geometry, charge carrier and symmetry.",
        "complete-named-molecular-charge-carrier",
        "Species, state, geometry and complete charge distinction remain held.",
    ),
    dimension(
        "symmetry", "component-list-selected-after-values",
        "A value-selected component list cannot establish molecular organization.",
        "symmetry-forced-component-support",
        "Inversion closes all components; retained exchange symmetry leaves one axis; isotope distinction retains two principal axes.",
    ),
    dimension(
        "orientation", "signed-direction-as-proof-number",
        "A conventional sign imports a negative proof magnitude.",
        "held-orientation-positive-components",
        "Direction remains a label and every component magnitude is exact and positive.",
    ),
    dimension(
        "composition", "continuum-vector-premise",
        "A continuum vector space and norm are not generated Fold forms.",
        "finite-distinct-axis-Junction",
        "Each retained axis occurs once and finite component squares join exactly.",
    ),
    dimension(
        "magnitude", "irrational-square-root-or-fitted-norm",
        "A square root or fitted norm can leave the exact rational domain.",
        "exact-squared-magnitude-relation",
        "Magnitude squared equals the exact Junction of all positive component squares.",
    ),
    dimension(
        "prediction", "dipole-value-readable-before-seal",
        "A readable component or total could select the relation.",
        "value-free-symmetry-and-relation-seal",
        "Only identities, symmetry classes, axes and the squared relation seal before values open.",
    ),
    dimension(
        "record", "favorable-species-or-component-subset",
        "A selected subset can conceal an absent row, extra component or inconsistent total.",
        "complete-five-species-nine-row-vector",
        "Both homonuclear controls and every registered water-isotopologue component and total remain present.",
    ),
    dimension(
        "extension", "species-coefficient-charge-fit-or-correction",
        "A species coefficient, charge fit or residual correction is a free parameter.",
        "one-structural-law-no-extra-rule",
        "One symmetry and squared-Junction law exhausts the registered vector.",
    ),
)


EXACT_RESULT = (
    "complete-named-molecular-charge-carrier__symmetry-forced-component-support__"
    "held-orientation-positive-components__finite-distinct-axis-Junction__"
    "exact-squared-magnitude-relation__value-free-symmetry-and-relation-seal__"
    "complete-five-species-nine-row-vector__one-structural-law-no-extra-rule"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    one_axis = (
        DipoleComponent(
            HeldLabel("dipole-axis", "principal-b"),
            HeldLabel("held-dipole-orientation", "toward-distinguished-charge-carrier"),
            PositiveRatio.from_pair(3, 2),
        ),
    )
    two_axes = (
        DipoleComponent(
            HeldLabel("dipole-axis", "principal-a"),
            HeldLabel("held-dipole-orientation", "first-principal-side"),
            PositiveRatio.from_pair(3, 5),
        ),
        DipoleComponent(
            HeldLabel("dipole-axis", "principal-b"),
            HeldLabel("held-dipole-orientation", "second-principal-side"),
            PositiveRatio.from_pair(4, 5),
        ),
    )
    duplicate_rejected = False
    try:
        exact_squared_magnitude((two_axes[0], two_axes[0]))
    except InadmissibleExactValue:
        duplicate_rejected = True
    carriers = registered_molecular_dipole_carriers()
    return (
        (
            "symmetry-component-support",
            "The five registered carriers force component counts EmptyOne, EmptyOne, One, One and two.",
            tuple(len(row.component_axes) for row in carriers) == (0, 0, 1, 1, 2),
        ),
        (
            "structural-absence",
            "No retained component returns structural EmptyOne rather than numerical zero.",
            exact_squared_magnitude(()) is EMPTY_ONE,
        ),
        (
            "one-axis-magnitude",
            "One retained component forces its exact square as the molecular squared magnitude.",
            exact_squared_magnitude(one_axis).fraction == Fraction(9, 4),
        ),
        (
            "orthogonal-square-Junction",
            "Three-fifths and four-fifths component fibres join to the exact One without a square root.",
            exact_squared_magnitude(two_axes).fraction == Fraction(1, 1),
        ),
        (
            "axis-uniqueness",
            "Duplicating a component axis halts instead of double-counting magnitude.",
            duplicate_rejected,
        ),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "DipoleComponent", "EXACT_RESULT", "ExactDipoleMagnitude",
    "MolecularDipoleCarrier", "OPERATIONAL_WITNESSES", "SYMMETRY_AXES",
    "exact_squared_magnitude", "registered_molecular_dipole_carriers",
)
