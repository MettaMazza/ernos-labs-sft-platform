"""Fold-native chemical temperature correspondence for THERMO-002.

Chemistry consumes the already admitted Physics temperature carrier unchanged.
It owns the composition, phase, equilibrium-reference and chemical-state
consequences attached to that carrier, but it cannot introduce a chemical
rescaling, fitted conversion, route-specific temperature, or target-derived
coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ChemicalTemperatureContext:
    composition: HeldLabel
    phase: HeldLabel
    equilibrium_reference: HeldLabel
    thermometric_route: HeldLabel
    physics_temperature_carrier: PositiveRatio

    def __post_init__(self) -> None:
        required = (
            (self.composition, "chemical-composition"),
            (self.phase, "phase-identity"),
            (self.equilibrium_reference, "thermal-equilibrium-reference"),
            (self.thermometric_route, "thermometric-route"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("chemical temperature context lost a required held identity")
        if not isinstance(self.physics_temperature_carrier, PositiveRatio):
            raise InadmissibleExactValue("Chemistry must consume one exact positive Physics temperature carrier")


@dataclass(frozen=True)
class CompositionTemperatureConsequence:
    composition: HeldLabel
    chemical_state_consequence: HeldLabel
    physics_temperature_carrier: PositiveRatio

    def __post_init__(self) -> None:
        if not isinstance(self.composition, HeldLabel) or self.composition.family != "chemical-composition":
            raise InadmissibleExactValue("temperature consequence requires held chemical composition")
        if not isinstance(self.chemical_state_consequence, HeldLabel) or self.chemical_state_consequence.family != "composition-dependent-temperature-consequence":
            raise InadmissibleExactValue("temperature consequence requires a held chemical-state result")
        if not isinstance(self.physics_temperature_carrier, PositiveRatio):
            raise InadmissibleExactValue("temperature consequence must retain the Physics carrier unchanged")


def consume_physics_temperature_carrier(context: ChemicalTemperatureContext) -> PositiveRatio:
    """Return the admitted Physics carrier unchanged and without a chemical scale."""

    if not isinstance(context, ChemicalTemperatureContext):
        raise InadmissibleExactValue("chemical temperature correspondence requires a complete context")
    return context.physics_temperature_carrier


def common_thermal_equilibrium_carrier(
    left: ChemicalTemperatureContext,
    right: ChemicalTemperatureContext,
) -> PositiveRatio:
    """Force one common carrier across distinct compositions or routes at equilibrium."""

    if not isinstance(left, ChemicalTemperatureContext) or not isinstance(right, ChemicalTemperatureContext):
        raise InadmissibleExactValue("thermal equilibrium requires two complete chemical contexts")
    if left.equilibrium_reference != right.equilibrium_reference:
        raise InadmissibleExactValue("contexts do not share the same held equilibrium reference")
    if left.physics_temperature_carrier != right.physics_temperature_carrier:
        raise InadmissibleExactValue("equilibrium cannot admit route- or composition-specific temperature rescaling")
    return left.physics_temperature_carrier


def attach_composition_consequence(
    context: ChemicalTemperatureContext,
    consequence: HeldLabel,
) -> CompositionTemperatureConsequence:
    """Attach a composition-owned result without changing the temperature carrier."""

    return CompositionTemperatureConsequence(
        context.composition,
        consequence,
        consume_physics_temperature_carrier(context),
    )


def append_composition_preserves_common_carrier(
    contexts: tuple[ChemicalTemperatureContext, ...],
    extension: ChemicalTemperatureContext,
) -> bool:
    """Adding one composition preserves the one common Physics carrier."""

    if not isinstance(contexts, tuple) or not contexts:
        raise InadmissibleExactValue("temperature correspondence requires nonempty finite context support")
    if extension in contexts:
        raise InadmissibleExactValue("composition extension must be new")
    carrier = contexts[0].physics_temperature_carrier
    reference = contexts[0].equilibrium_reference
    if any(item.physics_temperature_carrier != carrier or item.equilibrium_reference != reference for item in contexts):
        raise InadmissibleExactValue("existing chemical contexts do not share one equilibrium carrier")
    if extension.physics_temperature_carrier != carrier or extension.equilibrium_reference != reference:
        raise InadmissibleExactValue("new composition attempted to rescale the common temperature carrier")
    extended = contexts + (extension,)
    return extended[:-1] == contexts and all(item.physics_temperature_carrier == carrier for item in extended)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-THERMO-TEMPERATURE-001",
    "SFT-PHYS-THERMO-EQUILIBRIUM-001",
    "SFT-PHYS-THERMO-STATE-RELATION-001",
    "SFT-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-CROSS-PROPERTY-MOLECULAR-VECTOR-014",
    "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("authority", "chemistry-redefines-temperature", "A Chemistry-specific temperature law duplicates and can contradict the admitted Physics carrier.", "chemistry-consumes-admitted-physics-temperature-carrier", "The Physics temperature carrier enters Chemistry unchanged."),
    dimension("composition", "composition-erased-temperature-scalar", "Erasing composition loses the chemical state to which a consequence belongs.", "held-chemical-composition-identity", "Composition remains a held identity beside the shared carrier."),
    dimension("condition", "phase-and-equilibrium-reference-erased", "Without phase and reference, distinct chemical states are conflated.", "held-phase-and-equilibrium-reference", "Phase and equilibrium reference remain explicit."),
    dimension("relation", "fitted-chemical-temperature-conversion", "A conversion coefficient lets composition or a target rescale temperature.", "identity-preserving-temperature-correspondence", "Chemical translation returns the exact Physics carrier unchanged."),
    dimension("equilibrium", "route-or-composition-specific-temperature", "Separate route temperatures violate common equilibrium correspondence.", "one-common-carrier-across-equilibrated-routes", "Every equilibrated route and composition retains the same exact carrier."),
    dimension("prediction", "thermometric-values-readable-before-seal", "Measured centers or uncertainties could select the correspondence.", "complete-value-free-thermometric-identity-seal", "All source, route and composition identities seal before values open."),
    dimension("record", "selected-thermometry-route", "One favorable route cannot establish route-independent correspondence.", "complete-three-row-two-route-value-vector", "The exact SI carrier and both independent measured routes remain explicit."),
    dimension("extension", "composition-dependent-rescaling", "A new composition-specific scale is a free parameter.", "append-only-composition-consequence-with-common-carrier", "Each new chemical consequence preserves the common Physics carrier."),
)


EXACT_RESULT = (
    "chemistry-consumes-admitted-physics-temperature-carrier__held-chemical-composition-identity__"
    "held-phase-and-equilibrium-reference__identity-preserving-temperature-correspondence__"
    "one-common-carrier-across-equilibrated-routes__complete-value-free-thermometric-identity-seal__"
    "complete-three-row-two-route-value-vector__append-only-composition-consequence-with-common-carrier"
)


def _context(composition: str, phase: str, route: str, carrier: PositiveRatio) -> ChemicalTemperatureContext:
    return ChemicalTemperatureContext(
        HeldLabel("chemical-composition", composition), HeldLabel("phase-identity", phase),
        HeldLabel("thermal-equilibrium-reference", "held-common-reference"),
        HeldLabel("thermometric-route", route), carrier,
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    carrier = PositiveRatio.from_pair(5, 3)
    argon = _context("argon", "gas", "acoustic", carrier)
    resistor = _context("resistor-material", "condensed", "Johnson-noise", carrier)
    extension = _context("water", "liquid", "contact-equilibrium", carrier)
    mismatch_rejected = False
    try:
        common_thermal_equilibrium_carrier(argon, _context("tampered", "gas", "tampered", PositiveRatio.from_pair(7, 4)))
    except InadmissibleExactValue:
        mismatch_rejected = True
    consequence = attach_composition_consequence(
        argon, HeldLabel("composition-dependent-temperature-consequence", "argon-state-order"),
    )
    return (
        ("unchanged-physics-carrier", "Chemistry returns the admitted carrier unchanged.", consume_physics_temperature_carrier(argon) == carrier),
        ("cross-route-equilibrium", "Acoustic and electronic contexts share one equilibrium carrier.", common_thermal_equilibrium_carrier(argon, resistor) == carrier),
        ("composition-owned-consequence", "The chemical result retains composition and the unchanged carrier.", consequence.composition == argon.composition and consequence.physics_temperature_carrier == carrier),
        ("rescaling-rejected", "A route- or composition-specific carrier cannot enter equilibrium.", mismatch_rejected),
        ("append-only-composition", "Adding one composition preserves every existing carrier.", append_composition_preserves_common_carrier((argon, resistor), extension)),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "ChemicalTemperatureContext", "CompositionTemperatureConsequence",
    "append_composition_preserves_common_carrier", "attach_composition_consequence",
    "common_thermal_equilibrium_carrier", "consume_physics_temperature_carrier",
)
