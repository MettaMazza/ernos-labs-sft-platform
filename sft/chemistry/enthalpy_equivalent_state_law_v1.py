"""Fold-native enthalpy-equivalent chemical state relation for THERMO-006."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension


def _ratio(value) -> PositiveRatio:
    return PositiveRatio.from_pair(value.numerator, value.denominator)


@dataclass(frozen=True)
class EnvironmentTransferPart:
    identity: HeldLabel
    exact_positive_content: PositiveRatio

    def __post_init__(self) -> None:
        if not isinstance(self.identity, HeldLabel) or self.identity.family != "environment-transfer-part":
            raise InadmissibleExactValue("environment transfer requires a held identity")
        if not isinstance(self.exact_positive_content, PositiveRatio):
            raise InadmissibleExactValue("environment transfer requires exact positive content")


@dataclass(frozen=True)
class EnthalpyEquivalentChemicalState:
    composition: HeldLabel
    molecular_state: HeldLabel
    phase: HeldLabel
    environment: HeldLabel
    internal_energy: PositiveRatio
    environment_transfer_parts: tuple[EnvironmentTransferPart, ...] | EmptyOne
    enthalpy_equivalent_content: PositiveRatio

    def __post_init__(self) -> None:
        required = (
            (self.composition, "chemical-composition"),
            (self.molecular_state, "molecular-state"),
            (self.phase, "phase-identity"),
            (self.environment, "held-environment"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("enthalpy-equivalent state lost a held identity")
        if not isinstance(self.internal_energy, PositiveRatio) or not isinstance(self.enthalpy_equivalent_content, PositiveRatio):
            raise InadmissibleExactValue("enthalpy-equivalent state requires exact positive content")
        expected = compose_enthalpy_equivalent_content(self.internal_energy, self.environment_transfer_parts)
        if self.enthalpy_equivalent_content != expected:
            raise InadmissibleExactValue("enthalpy-equivalent content does not match its retained parts")


@dataclass(frozen=True)
class OrientedEnthalpyRelation:
    orientation: HeldLabel
    exact_positive_magnitude: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.orientation, HeldLabel) or self.orientation.family != "enthalpy-state-orientation":
            raise InadmissibleExactValue("enthalpy relation requires a held orientation")
        if self.orientation.label == "enthalpy-equivalent":
            if not isinstance(self.exact_positive_magnitude, EmptyOne):
                raise InadmissibleExactValue("equivalent states require structural EmptyOne")
        elif self.orientation.label in {"enthalpy-rise", "enthalpy-fall"}:
            if not isinstance(self.exact_positive_magnitude, PositiveRatio):
                raise InadmissibleExactValue("oriented enthalpy relation requires positive separation")
        else:
            raise InadmissibleExactValue("unknown enthalpy orientation")


def compose_enthalpy_equivalent_content(
    internal_energy: PositiveRatio,
    environment_parts: tuple[EnvironmentTransferPart, ...] | EmptyOne,
) -> PositiveRatio:
    """Compose retained internal content with generated environment-transfer parts."""

    if not isinstance(internal_energy, PositiveRatio):
        raise InadmissibleExactValue("enthalpy composition requires exact positive internal energy")
    if isinstance(environment_parts, EmptyOne):
        return internal_energy
    if not isinstance(environment_parts, tuple) or not environment_parts or any(not isinstance(part, EnvironmentTransferPart) for part in environment_parts):
        raise InadmissibleExactValue("environment contribution is EmptyOne or a nonempty exact part tuple")
    if len({part.identity for part in environment_parts}) != len(environment_parts):
        raise InadmissibleExactValue("environment contribution duplicated a named part")
    total = internal_energy.fraction
    for part in environment_parts:
        total += part.exact_positive_content.fraction
    return _ratio(total)


def enthalpy_equivalent_state(
    composition: HeldLabel,
    molecular_state: HeldLabel,
    phase: HeldLabel,
    environment: HeldLabel,
    internal_energy: PositiveRatio,
    environment_parts: tuple[EnvironmentTransferPart, ...] | EmptyOne,
) -> EnthalpyEquivalentChemicalState:
    return EnthalpyEquivalentChemicalState(
        composition, molecular_state, phase, environment, internal_energy, environment_parts,
        compose_enthalpy_equivalent_content(internal_energy, environment_parts),
    )


def exact_enthalpy_state_relation(
    first: EnthalpyEquivalentChemicalState,
    second: EnthalpyEquivalentChemicalState,
) -> OrientedEnthalpyRelation:
    if not isinstance(first, EnthalpyEquivalentChemicalState) or not isinstance(second, EnthalpyEquivalentChemicalState):
        raise InadmissibleExactValue("enthalpy relation requires complete chemical states")
    if first.composition != second.composition or first.environment != second.environment:
        raise InadmissibleExactValue("enthalpy comparison changed composition or held environment")
    left = first.enthalpy_equivalent_content.fraction
    right = second.enthalpy_equivalent_content.fraction
    if left == right:
        return OrientedEnthalpyRelation(HeldLabel("enthalpy-state-orientation", "enthalpy-equivalent"), EmptyOne())
    if right > left:
        return OrientedEnthalpyRelation(HeldLabel("enthalpy-state-orientation", "enthalpy-rise"), _ratio(right - left))
    return OrientedEnthalpyRelation(HeldLabel("enthalpy-state-orientation", "enthalpy-fall"), _ratio(left - right))


def append_environment_part_preserves_state(
    internal_energy: PositiveRatio,
    parts: tuple[EnvironmentTransferPart, ...],
    extension: EnvironmentTransferPart,
) -> bool:
    prior = compose_enthalpy_equivalent_content(internal_energy, parts)
    if extension.identity in {part.identity for part in parts}:
        raise InadmissibleExactValue("environment successor requires a fresh held part")
    extended = parts + (extension,)
    expected = _ratio(prior.fraction + extension.exact_positive_content.fraction)
    return extended[:-1] == parts and compose_enthalpy_equivalent_content(internal_energy, extended) == expected


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-COMPOSITION-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001", "SFT-PHYS-THERMO-HEAT-WORK-001",
    "SFT-PHYS-THERMO-FIRST-LAW-001", "SFT-PHYS-THERMO-STATE-RELATION-001",
    "SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013", "SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003",
    "SFT-CHEM-HEAT-WORK-TRANSFER-PARTITION-004", "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("state", "answer-only-signed-enthalpy-scalar", "A signed scalar erases composition, phase, molecular state and environment.", "complete-held-state-and-environment-carrier", "Every value remains attached to its complete chemical state and held environment."),
    dimension("internal", "fitted-or-unnamed-internal-content", "A fitted internal term can absorb any target discrepancy.", "retained-exact-positive-internal-content", "The admitted chemical internal-energy carrier is retained unchanged."),
    dimension("environment", "imported-pressure-volume-equation", "An imported equation would select the environment correction rather than derive its role.", "observation-forced-organized-environment-transfer-parts", "Only retained organized environment-transfer records extend the state carrier."),
    dimension("composition", "signed-cancellation-or-numerical-zero-correction", "Signs erase transfer provenance and numerical zero is not an SFT number.", "exact-positive-composition-plus-EmptyOne-absence", "Generated environment parts add exactly; absence is structural EmptyOne."),
    dimension("orientation", "negative-enthalpy-proof-magnitude", "A negative proof magnitude conflates relation direction with content.", "held-state-orientation-plus-positive-separation", "Rise/fall is held separately; equality is structural EmptyOne."),
    dimension("prediction", "enthalpy-target-readable-before-seal", "Target values could select an environment part or state order.", "complete-value-free-enthalpy-state-identity-seal", "Every state identity seals before enthalpy or component values open."),
    dimension("record", "selected-enthalpy-or-single-phase-row", "A selected row can hide phase and unfavorable records.", "complete-13-row-enthalpy-component-vector", "All liquid, boundary and vapour enthalpy/component rows are retained."),
    dimension("extension", "refit-prior-state-after-environment-successor", "Refitting prior content destroys compositional invariance.", "depth-independent-append-only-environment-part-successor", "One fresh environment part appends without changing prior parts."),
)


EXACT_RESULT = (
    "complete-held-state-and-environment-carrier__retained-exact-positive-internal-content__"
    "observation-forced-organized-environment-transfer-parts__exact-positive-composition-plus-EmptyOne-absence__"
    "held-state-orientation-plus-positive-separation__complete-value-free-enthalpy-state-identity-seal__"
    "complete-13-row-enthalpy-component-vector__depth-independent-append-only-environment-part-successor"
)


def _parts() -> tuple[EnvironmentTransferPart, ...]:
    return (
        EnvironmentTransferPart(HeldLabel("environment-transfer-part", "first"), PositiveRatio.from_pair(2, 3)),
        EnvironmentTransferPart(HeldLabel("environment-transfer-part", "second"), PositiveRatio.from_pair(5, 4)),
    )


def _state(label: str, internal: int, parts) -> EnthalpyEquivalentChemicalState:
    return enthalpy_equivalent_state(
        HeldLabel("chemical-composition", "held-composition"), HeldLabel("molecular-state", label),
        HeldLabel("phase-identity", "held-phase"), HeldLabel("held-environment", "held-environment"),
        PositiveRatio.from_pair(internal, 3), parts,
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    parts = _parts(); extension = EnvironmentTransferPart(HeldLabel("environment-transfer-part", "third"), PositiveRatio.from_pair(7, 5))
    base = _state("base", 5, EmptyOne()); loaded = _state("loaded", 5, parts); higher = _state("higher", 8, parts)
    return (
        ("EmptyOne-environment", "Absent generated environment transfer preserves internal content exactly.", base.enthalpy_equivalent_content == base.internal_energy),
        ("exact-composition", "Retained internal and environment contents compose exactly.", loaded.enthalpy_equivalent_content == PositiveRatio.from_pair(43, 12)),
        ("held-orientation", "State order is held separately from positive separation.", exact_enthalpy_state_relation(loaded, higher).orientation.label == "enthalpy-rise"),
        ("structural-equality", "Equal state content uses structural EmptyOne.", isinstance(exact_enthalpy_state_relation(loaded, loaded).exact_positive_magnitude, EmptyOne)),
        ("append-only", "One fresh environment part preserves all prior parts and adds once.", append_environment_part_preserves_state(PositiveRatio.from_pair(5, 3), parts, extension)),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "EnthalpyEquivalentChemicalState", "EnvironmentTransferPart", "OrientedEnthalpyRelation",
    "append_environment_part_preserves_state", "compose_enthalpy_equivalent_content",
    "enthalpy_equivalent_state", "exact_enthalpy_state_relation",
)
