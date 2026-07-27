"""Fold-native internal-energy composition law for Chemistry THERMO-003."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension


def _ratio(value) -> PositiveRatio:
    return PositiveRatio.from_pair(value.numerator, value.denominator)


@dataclass(frozen=True)
class InternalEnergyPart:
    part_identity: HeldLabel
    exact_positive_content: PositiveRatio

    def __post_init__(self) -> None:
        if not isinstance(self.part_identity, HeldLabel) or self.part_identity.family != "internal-energy-part":
            raise InadmissibleExactValue("internal-energy part requires a held identity")
        if not isinstance(self.exact_positive_content, PositiveRatio):
            raise InadmissibleExactValue("internal-energy part requires exact positive content")


@dataclass(frozen=True)
class ChemicalInternalEnergyState:
    composition: HeldLabel
    molecular_state: HeldLabel
    phase: HeldLabel
    environment: HeldLabel
    internal_energy: PositiveRatio

    def __post_init__(self) -> None:
        required = (
            (self.composition, "chemical-composition"),
            (self.molecular_state, "molecular-state"),
            (self.phase, "phase-identity"),
            (self.environment, "held-environment"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("internal-energy state lost a required held identity")
        if not isinstance(self.internal_energy, PositiveRatio):
            raise InadmissibleExactValue("internal energy must be exact and positive")


@dataclass(frozen=True)
class OrientedInternalEnergyStep:
    orientation: HeldLabel
    exact_positive_magnitude: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.orientation, HeldLabel) or self.orientation.family != "internal-energy-transfer-orientation":
            raise InadmissibleExactValue("internal-energy change requires a held orientation")
        if self.orientation.label == "internal-energy-equal":
            if not isinstance(self.exact_positive_magnitude, EmptyOne):
                raise InadmissibleExactValue("equal internal-energy states require structural EmptyOne")
        elif self.orientation.label in {"internal-energy-rise", "internal-energy-fall"}:
            if not isinstance(self.exact_positive_magnitude, PositiveRatio):
                raise InadmissibleExactValue("oriented internal-energy change requires an exact positive magnitude")
        else:
            raise InadmissibleExactValue("unknown internal-energy orientation")


def compose_internal_energy_parts(parts: tuple[InternalEnergyPart, ...]) -> PositiveRatio:
    """Compose a nonempty exact positive internal-energy content."""

    if not isinstance(parts, tuple) or not parts or any(not isinstance(part, InternalEnergyPart) for part in parts):
        raise InadmissibleExactValue("internal-energy composition requires nonempty exact parts")
    if len({part.part_identity for part in parts}) != len(parts):
        raise InadmissibleExactValue("internal-energy composition duplicated a named part")
    total = parts[0].exact_positive_content.fraction
    for part in parts[1:]:
        total += part.exact_positive_content.fraction
    return _ratio(total)


def exact_internal_energy_relation(
    first: ChemicalInternalEnergyState,
    second: ChemicalInternalEnergyState,
) -> OrientedInternalEnergyStep:
    """Separate direction from exact positive difference; equality is structural."""

    if not isinstance(first, ChemicalInternalEnergyState) or not isinstance(second, ChemicalInternalEnergyState):
        raise InadmissibleExactValue("internal-energy relation requires two complete chemical states")
    if first.composition != second.composition or first.environment != second.environment:
        raise InadmissibleExactValue("internal-energy comparison changed composition or declared environment")
    if first.internal_energy == second.internal_energy:
        return OrientedInternalEnergyStep(HeldLabel("internal-energy-transfer-orientation", "internal-energy-equal"), EmptyOne())
    if second.internal_energy.fraction > first.internal_energy.fraction:
        return OrientedInternalEnergyStep(
            HeldLabel("internal-energy-transfer-orientation", "internal-energy-rise"),
            _ratio(second.internal_energy.fraction - first.internal_energy.fraction),
        )
    return OrientedInternalEnergyStep(
        HeldLabel("internal-energy-transfer-orientation", "internal-energy-fall"),
        _ratio(first.internal_energy.fraction - second.internal_energy.fraction),
    )


def compose_oriented_internal_energy_steps(
    steps: tuple[OrientedInternalEnergyStep, ...],
) -> OrientedInternalEnergyStep:
    """Compose a nonempty path whose non-equal transfers share one held direction."""

    if not isinstance(steps, tuple) or not steps or any(not isinstance(step, OrientedInternalEnergyStep) for step in steps):
        raise InadmissibleExactValue("internal-energy path requires nonempty exact steps")
    active = tuple(step for step in steps if isinstance(step.exact_positive_magnitude, PositiveRatio))
    if not active:
        return OrientedInternalEnergyStep(HeldLabel("internal-energy-transfer-orientation", "internal-energy-equal"), EmptyOne())
    if len({step.orientation for step in active}) != 1:
        raise InadmissibleExactValue("opposed transfers require separate held path records, not signed cancellation")
    total = active[0].exact_positive_magnitude.fraction
    for step in active[1:]:
        total += step.exact_positive_magnitude.fraction
    return OrientedInternalEnergyStep(active[0].orientation, _ratio(total))


def append_energy_part_preserves_prior_composition(
    parts: tuple[InternalEnergyPart, ...],
    extension: InternalEnergyPart,
) -> bool:
    if extension in parts or extension.part_identity in {part.part_identity for part in parts}:
        raise InadmissibleExactValue("internal-energy successor must add a new named part")
    prior = compose_internal_energy_parts(parts)
    extended = parts + (extension,)
    expected = _ratio(prior.fraction + extension.exact_positive_content.fraction)
    return extended[:-1] == parts and compose_internal_energy_parts(extended) == expected


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-COMPOSITION-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001", "SFT-PHYS-THERMO-FIRST-LAW-001",
    "SFT-PHYS-THERMO-STATE-RELATION-001", "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013", "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001",
    "SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "answer-only-signed-energy-scalar", "A signed scalar erases composition, state, phase and environment.", "complete-held-chemical-internal-energy-state", "Every energy value remains attached to its complete chemical state."),
    dimension("parts", "fitted-total-or-unnamed-contribution", "A fitted total or unnamed term can absorb any target discrepancy.", "nonempty-exact-positive-named-part-composition", "Internal energy is the exact sum of its generated named positive parts."),
    dimension("orientation", "negative-proof-magnitude", "A negative proof magnitude conflates direction with content.", "held-transfer-orientation-plus-positive-magnitude", "Rise or fall is held separately from exact positive separation."),
    dimension("equality", "numerical-zero-energy-change", "Numerical zero is not an SFT number or proof object.", "structural-EmptyOne-equality", "Equal states close as structural EmptyOne."),
    dimension("path", "endpoint-only-or-signed-cancellation", "Endpoint-only cancellation deletes intermediate transfer provenance.", "complete-same-orientation-step-composition", "Every exact positive step is retained and summed under one held direction."),
    dimension("prediction", "internal-energy-target-readable-before-seal", "A target value could select the parts or orientation.", "complete-value-free-thermochemical-identity-seal", "All state identities seal before thermochemical values open."),
    dimension("record", "selected-state-or-single-phase-vector", "A selected state can hide phase and unfavorable rows.", "complete-13-row-14-column-state-vector", "Every returned liquid, phase-boundary and vapour row is retained."),
    dimension("extension", "refit-prior-parts-after-successor", "Refitting earlier parts destroys compositional invariance.", "depth-independent-append-only-positive-part-successor", "One new named positive part appends without changing earlier parts."),
)


EXACT_RESULT = (
    "complete-held-chemical-internal-energy-state__nonempty-exact-positive-named-part-composition__"
    "held-transfer-orientation-plus-positive-magnitude__structural-EmptyOne-equality__"
    "complete-same-orientation-step-composition__complete-value-free-thermochemical-identity-seal__"
    "complete-13-row-14-column-state-vector__depth-independent-append-only-positive-part-successor"
)


def _state(label: str, numerator: int) -> ChemicalInternalEnergyState:
    return ChemicalInternalEnergyState(
        HeldLabel("chemical-composition", "held-composition"), HeldLabel("molecular-state", label),
        HeldLabel("phase-identity", "held-phase"), HeldLabel("held-environment", "held-environment"),
        PositiveRatio.from_pair(numerator, 3),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    first, second, third = _state("first", 5), _state("second", 8), _state("third", 14)
    step_one = exact_internal_energy_relation(first, second)
    step_two = exact_internal_energy_relation(second, third)
    composed = compose_oriented_internal_energy_steps((step_one, step_two))
    direct = exact_internal_energy_relation(first, third)
    parts = (
        InternalEnergyPart(HeldLabel("internal-energy-part", "first-part"), PositiveRatio.from_pair(2, 3)),
        InternalEnergyPart(HeldLabel("internal-energy-part", "second-part"), PositiveRatio.from_pair(5, 4)),
    )
    extension = InternalEnergyPart(HeldLabel("internal-energy-part", "third-part"), PositiveRatio.from_pair(7, 5))
    opposite_rejected = False
    try:
        compose_oriented_internal_energy_steps((step_one, exact_internal_energy_relation(third, second)))
    except InadmissibleExactValue:
        opposite_rejected = True
    return (
        ("exact-parts", "Named positive parts compose exactly.", compose_internal_energy_parts(parts) == PositiveRatio.from_pair(23, 12)),
        ("held-orientation", "Rise is held separately from positive magnitude.", step_one.orientation.label == "internal-energy-rise" and step_one.exact_positive_magnitude == PositiveRatio.from_pair(1, 1)),
        ("path-composition", "Successive rises equal the direct exact separation.", composed == direct),
        ("opposed-path-rejected", "Opposed steps cannot silently cancel through signs.", opposite_rejected),
        ("append-only-part", "A new named part preserves every prior part and adds exactly once.", append_energy_part_preserves_prior_composition(parts, extension)),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "ChemicalInternalEnergyState", "InternalEnergyPart", "OrientedInternalEnergyStep",
    "append_energy_part_preserves_prior_composition", "compose_internal_energy_parts",
    "compose_oriented_internal_energy_steps", "exact_internal_energy_relation",
)
