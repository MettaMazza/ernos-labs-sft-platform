"""Fold-native generated concentration/activity potential relation (ECHEM-004)."""
from __future__ import annotations
from dataclasses import dataclass
from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension

@dataclass(frozen=True)
class GeneratedActivityState:
    half_reaction: HeldLabel
    condition: HeldLabel
    quotient_orientation: HeldLabel
    generator_layers: PositiveCount | EmptyOne
    transferred_carriers: PositiveCount
    complete_species_phases: tuple[HeldLabel, ...]
    def __post_init__(self):
        if self.half_reaction.family != "half-reaction-identity" or self.condition.family != "electrochemical-condition":
            raise InadmissibleExactValue("activity state lost half-reaction or condition")
        if self.quotient_orientation.family != "activity-quotient-orientation" or self.quotient_orientation.label not in {"product-heavy", "reactant-heavy", "coincident"}:
            raise InadmissibleExactValue("activity quotient requires an exact held orientation")
        if self.quotient_orientation.label == "coincident" and self.generator_layers != EMPTY_ONE:
            raise InadmissibleExactValue("coincident activity support must be structural EmptyOne")
        if self.quotient_orientation.label != "coincident" and not isinstance(self.generator_layers, PositiveCount):
            raise InadmissibleExactValue("directed activity support requires positive generated layers")
        if not isinstance(self.transferred_carriers, PositiveCount) or not self.complete_species_phases:
            raise InadmissibleExactValue("activity state requires positive transfer and complete species support")

@dataclass(frozen=True)
class ConcentrationPotentialShift:
    orientation: HeldLabel
    exact_layer_per_carrier: PositiveRatio | EmptyOne
    state: GeneratedActivityState

def concentration_potential_shift(state: GeneratedActivityState) -> ConcentrationPotentialShift:
    if state.quotient_orientation.label == "coincident":
        return ConcentrationPotentialShift(HeldLabel("potential-shift-orientation", "standard-state-coincidence"), EMPTY_ONE, state)
    direction = "toward-reactants" if state.quotient_orientation.label == "product-heavy" else "toward-products"
    return ConcentrationPotentialShift(HeldLabel("potential-shift-orientation", direction), PositiveRatio(state.generator_layers, state.transferred_carriers), state)

def generated_activity_support(state: GeneratedActivityState) -> PositiveCount:
    if state.generator_layers == EMPTY_ONE:
        return PositiveCount(1)
    support = 1
    for _ in range(state.generator_layers.value):
        support += support
    return PositiveCount(support)

def _layer_separation(first: PositiveCount, second: PositiveCount) -> PositiveCount | EmptyOne:
    if first == second:
        return EMPTY_ONE
    if first.value > second.value:
        return PositiveCount(first.value - second.value)
    return PositiveCount(second.value - first.value)

def common_layer_successor_preserves_difference(first: GeneratedActivityState, second: GeneratedActivityState) -> bool:
    if first.half_reaction != second.half_reaction or first.condition != second.condition or first.quotient_orientation != second.quotient_orientation:
        raise InadmissibleExactValue("successor comparison requires one half-reaction condition and orientation")
    if not isinstance(first.generator_layers, PositiveCount) or not isinstance(second.generator_layers, PositiveCount):
        raise InadmissibleExactValue("successor comparison requires directed positive layers")
    prior = _layer_separation(first.generator_layers, second.generator_layers)
    return _layer_separation(PositiveCount(first.generator_layers.value + 1), PositiveCount(second.generator_layers.value + 1)) == prior

DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-MATH-COMBINATORICS-001",
    "SFT-INFO-ENTROPY-UNCERTAINTY-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-STOICH-SOLUTION-001", "SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009",
    "SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001", "SFT-CHEM-ELECTRODE-POTENTIAL-CHEMICAL-RELATION-002", "SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003",
)
DIMENSIONS = (
    dimension("state", "concentration-number-only", "A concentration number does not retain chemical identity or condition.", "complete-half-reaction-activity-state", "Half-reaction, condition, species, phases and carrier count remain held."),
    dimension("quotient", "signed-or-continuum-activity-coordinate", "A signed continuum coordinate imports an ungenerated domain.", "held-product-reactant-or-coincident-orientation", "Activity direction is structural and equality closes."),
    dimension("support", "arbitrary-real-activity-premise", "An arbitrary real activity is outside exact Fold arithmetic.", "complete-generated-doubling-support", "Every positive generator layer exactly doubles finite support."),
    dimension("composition", "imported-logarithm", "A logarithm cannot select the native law.", "layer-count-additive-product-composition", "Multiplying generated support corresponds exactly to adding generator layers."),
    dimension("transfer", "unscaled-electron-count", "Potential displacement must retain transferred-carrier multiplicity.", "exact-layer-per-held-carrier-ratio", "The exact shift is generated layers per positive transferred carrier."),
    dimension("coincidence", "numerical-zero-standard-state", "Numerical zero is not a native proof value.", "structural-EmptyOne-standard-state", "Equal product/reactant support closes to EmptyOne."),
    dimension("record", "selected-concentration-point", "A selected point can hide adverse curvature and uncertainty.", "complete-concentration-potential-series", "Every registered concentration, temperature, phase, sign and uncertainty remains downstream."),
    dimension("extension", "refitted-concentration-coefficient", "Refitting at each scale adds free choices.", "common-generator-successor-preserves-separation", "Adding one common layer preserves exact layer difference."),
)
EXACT_RESULT = "complete-half-reaction-activity-state__held-product-reactant-or-coincident-orientation__complete-generated-doubling-support__layer-count-additive-product-composition__exact-layer-per-held-carrier-ratio__structural-EmptyOne-standard-state__complete-concentration-potential-series__common-generator-successor-preserves-separation"

def _state(name, orientation, layers):
    return GeneratedActivityState(HeldLabel("half-reaction-identity", "held-reaction"), HeldLabel("electrochemical-condition", "held-temperature"), HeldLabel("activity-quotient-orientation", orientation), EMPTY_ONE if layers is None else PositiveCount(layers), PositiveCount(2), (HeldLabel("species-phase", name + "-aqueous"),))

def _witnesses():
    coincident, product, reactant = _state("equal", "coincident", None), _state("product", "product-heavy", 3), _state("reactant", "reactant-heavy", 2)
    bad = False
    try: _state("bad", "coincident", 1)
    except InadmissibleExactValue: bad = True
    return (
        ("coincidence", "Standard-state equality closes to EmptyOne.", concentration_potential_shift(coincident).exact_layer_per_carrier == EMPTY_ONE),
        ("product-direction", "Product-heavy support shifts toward reactants.", concentration_potential_shift(product).orientation.label == "toward-reactants"),
        ("reactant-direction", "Reactant-heavy support shifts toward products.", concentration_potential_shift(reactant).orientation.label == "toward-products"),
        ("exact-ratio", "Layer displacement is divided by positive carrier count exactly.", concentration_potential_shift(product).exact_layer_per_carrier.numerator == PositiveCount(3) and concentration_potential_shift(product).exact_layer_per_carrier.denominator == PositiveCount(2)),
        ("support", "Three generator layers give eight exact occurrences.", generated_activity_support(product) == PositiveCount(8)),
        ("coincidence-control", "A numerical layer on coincidence halts.", bad),
        ("successor", "Common layer successor preserves separation.", common_layer_successor_preserves_difference(_state("a", "product-heavy", 2), _state("b", "product-heavy", 5))),
    )
OPERATIONAL_WITNESSES = _witnesses()
__all__ = ("ConcentrationPotentialShift", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "GeneratedActivityState", "OPERATIONAL_WITNESSES", "common_layer_successor_preserves_difference", "concentration_potential_shift", "generated_activity_support")
