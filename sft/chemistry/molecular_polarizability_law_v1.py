"""Fold-native exact molecular-polarizability law for Chemistry PROP-006.

Polarizability is the retained ratio between a positive induced molecular
dipole distinction and the positive external electric distinction that causes
it.  Orientation remains a held axis label.  Repeating one identical field act
scales response and field by the same positive count and therefore preserves
the ratio at every generated depth.  At the admitted three-axis spatial
boundary, the isotropic molecular response is the exact one-third Junction of
the three held component responses.

No measured alpha, continuum field, perturbation series, wavefunction, fitted
coefficient, floating value, signed number or square root occurs here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class PolarizabilityComponent:
    axis: HeldLabel
    induced_dipole_distinction: PositiveRatio
    electric_distinction: PositiveRatio

    def __post_init__(self) -> None:
        if self.axis.family != "molecular-response-axis":
            raise InadmissibleExactValue("polarizability component requires a held molecular axis")
        if not isinstance(self.induced_dipole_distinction, PositiveRatio):
            raise InadmissibleExactValue("induced dipole distinction must be exact and positive")
        if not isinstance(self.electric_distinction, PositiveRatio):
            raise InadmissibleExactValue("electric distinction must be exact and positive")

    @property
    def exact_response(self) -> PositiveRatio:
        ratio = self.induced_dipole_distinction.fraction / self.electric_distinction.fraction
        return PositiveRatio.from_pair(ratio.numerator, ratio.denominator)


def repeated_equal_field_response(
    component: PolarizabilityComponent,
    repetitions: PositiveCount,
) -> PolarizabilityComponent:
    """Append equal field acts while preserving the exact response ratio."""

    if not isinstance(component, PolarizabilityComponent) or not isinstance(repetitions, PositiveCount):
        raise InadmissibleExactValue("response repetition requires a component and positive count")
    response = component.induced_dipole_distinction.fraction * repetitions.value
    field = component.electric_distinction.fraction * repetitions.value
    return PolarizabilityComponent(
        component.axis,
        PositiveRatio.from_pair(response.numerator, response.denominator),
        PositiveRatio.from_pair(field.numerator, field.denominator),
    )


def exact_isotropic_response(components: tuple[PolarizabilityComponent, ...]) -> PositiveRatio:
    """Take the exact one-third Junction of the three distinct axis responses."""

    if not isinstance(components, tuple) or len(components) != 3:
        raise InadmissibleExactValue("isotropic response requires complete three-axis support")
    if any(not isinstance(component, PolarizabilityComponent) for component in components):
        raise InadmissibleExactValue("isotropic response contains an invalid component")
    axes = tuple(component.axis for component in components)
    if len(set(axes)) != 3:
        raise InadmissibleExactValue("each molecular response axis must occur exactly once")
    responses = tuple(component.exact_response.fraction for component in components)
    joined = responses[0] + responses[1] + responses[2]
    mean = joined / 3
    return PositiveRatio.from_pair(mean.numerator, mean.denominator)


@dataclass(frozen=True)
class MolecularPolarizabilityCarrier:
    species: HeldLabel
    molecular_state: HeldLabel
    conformation: HeldLabel
    field_distinction: HeldLabel
    component_definition: HeldLabel
    method: HeldLabel
    condition: HeldLabel
    units: HeldLabel

    def __post_init__(self) -> None:
        required = (
            (self.species, "molecular-species"),
            (self.molecular_state, "molecular-state"),
            (self.conformation, "molecular-conformation"),
            (self.field_distinction, "external-electric-distinction"),
            (self.component_definition, "polarizability-definition"),
            (self.method, "measurement-method"),
            (self.condition, "measurement-condition"),
            (self.units, "measurement-unit"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("molecular polarizability carrier erased a required held field")


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ALGEBRA-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-FIELD-SOURCE-RESPONSE-001",
    "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
    "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
    "SFT-PHYS-ATOMIC-FIELD-SPLITTING-TERMINAL-005",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-MOL-GEOMETRY-001",
    "SFT-CHEM-MOLECULAR-DIPOLE-MAGNITUDE-005",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier", "answer-only-alpha-scalar",
        "A scalar answer erases species, state, conformation, field, method and condition.",
        "complete-named-molecular-response-carrier",
        "Every source identity and response condition remains held.",
    ),
    dimension(
        "response", "imported-continuum-derivative",
        "A continuum derivative imports an ungenerated field neighborhood.",
        "exact-positive-response-over-field-ratio",
        "One positive induced distinction divided by one positive field distinction defines the response.",
    ),
    dimension(
        "orientation", "signed-Cartesian-component",
        "A signed Cartesian scalar imports a negative proof value.",
        "held-axis-positive-component",
        "Orientation remains a held axis and each component magnitude remains positive.",
    ),
    dimension(
        "composition", "continuum-tensor-trace-premise",
        "A continuum tensor is not a generated Fold form.",
        "three-axis-exact-one-third-Junction",
        "The isotropic response is the exact one-third Junction of three distinct held components.",
    ),
    dimension(
        "successor", "depth-specific-response-coefficient",
        "A new coefficient at each field depth is a free parameter family.",
        "equal-act-ratio-invariant-successor",
        "Every repeated equal field act scales response and field together and preserves their ratio.",
    ),
    dimension(
        "prediction", "alpha-readable-before-seal",
        "A readable alpha vector could select the law or boundary.",
        "value-free-identity-and-relation-seal",
        "All identities and exact operations seal before any alpha inscription opens.",
    ),
    dimension(
        "record", "selected-species-or-favorable-subset",
        "A selected subset can conceal ordinary, charged, isotopic or adverse rows.",
        "complete-NIST-non-atomic-vector",
        "Every one of the 252 non-atomic NIST table rows is retained in source order.",
    ),
    dimension(
        "extension", "species-fit-or-residual-correction",
        "A species coefficient or residual correction is a fitted parameter.",
        "one-response-law-no-extra-rule",
        "One response-ratio and three-axis composition law governs the complete registered vector.",
    ),
)


EXACT_RESULT = (
    "complete-named-molecular-response-carrier__exact-positive-response-over-field-ratio__"
    "held-axis-positive-component__three-axis-exact-one-third-Junction__"
    "equal-act-ratio-invariant-successor__value-free-identity-and-relation-seal__"
    "complete-NIST-non-atomic-vector__one-response-law-no-extra-rule"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    axes = tuple(HeldLabel("molecular-response-axis", label) for label in ("a", "b", "c"))
    component = PolarizabilityComponent(
        axes[0], PositiveRatio.from_pair(6, 1), PositiveRatio.from_pair(2, 1)
    )
    repeated = repeated_equal_field_response(component, PositiveCount(5))
    components = (
        PolarizabilityComponent(axes[0], PositiveRatio.from_pair(2, 1), PositiveRatio.from_pair(1, 1)),
        PolarizabilityComponent(axes[1], PositiveRatio.from_pair(6, 1), PositiveRatio.from_pair(2, 1)),
        PolarizabilityComponent(axes[2], PositiveRatio.from_pair(12, 1), PositiveRatio.from_pair(3, 1)),
    )
    incomplete_rejected = False
    duplicate_rejected = False
    try:
        exact_isotropic_response(components[:2])
    except InadmissibleExactValue:
        incomplete_rejected = True
    try:
        exact_isotropic_response((components[0], components[0], components[2]))
    except InadmissibleExactValue:
        duplicate_rejected = True
    return (
        ("exact-response-ratio", "Six response parts over two field parts gives three exactly.", component.exact_response.fraction == Fraction(3, 1)),
        ("successor-invariance", "Five equal acts preserve the exact response ratio.", repeated.exact_response == component.exact_response),
        ("isotropic-one-third-Junction", "Responses two, three and four average exactly to three.", exact_isotropic_response(components).fraction == Fraction(3, 1)),
        ("incomplete-support-rejected", "Two axes cannot masquerade as the complete isotropic carrier.", incomplete_rejected),
        ("duplicate-axis-rejected", "A duplicated axis cannot be counted twice.", duplicate_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "MolecularPolarizabilityCarrier",
    "OPERATIONAL_WITNESSES", "PolarizabilityComponent", "exact_isotropic_response",
    "repeated_equal_field_response",
)
