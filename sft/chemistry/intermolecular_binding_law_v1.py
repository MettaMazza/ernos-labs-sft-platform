"""Fold-native exact intermolecular binding law for Chemistry PROP-011.

No measured or calculated binding value, intermolecular potential, continuum
separation coordinate, fitted coefficient, species correction or target source
is available here.  The law retains named constituents, their exact separated
state, one bound composite state and a finite held separation organization.
Binding is the strictly ordered positive Take of the bound state from the
separated state.  A non-bound external record is structural EmptyOne, never a
negative or numerical-zero SFT value.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def exact_intermolecular_binding_take(
    separated_constituent_state: PositiveRatio,
    bound_composite_state: PositiveRatio,
) -> PositiveRatio:
    """Take the lower bound composite from the higher separated state."""

    if not isinstance(separated_constituent_state, PositiveRatio) or not isinstance(bound_composite_state, PositiveRatio):
        raise InadmissibleExactValue("intermolecular binding requires two exact positive state heights")
    if separated_constituent_state.fraction <= bound_composite_state.fraction:
        raise InadmissibleExactValue("binding Take requires a strictly higher separated constituent state")
    result = separated_constituent_state.fraction - bound_composite_state.fraction
    return PositiveRatio.from_pair(result.numerator, result.denominator)


def exact_separated_constituent_state(
    constituent_states: tuple[PositiveRatio, ...],
) -> PositiveRatio:
    """Compose all named positive constituent states without a zero initializer."""

    if not isinstance(constituent_states, tuple) or len(constituent_states) < 2:
        raise InadmissibleExactValue("an intermolecular separated state requires at least two constituents")
    if any(not isinstance(state, PositiveRatio) for state in constituent_states):
        raise InadmissibleExactValue("every separated constituent state must be an exact positive ratio")
    total = constituent_states[0].fraction
    for state in constituent_states[1:]:
        total += state.fraction
    return PositiveRatio.from_pair(total.numerator, total.denominator)


def append_shared_constituent_preserves_binding(
    separated_constituent_state: PositiveRatio,
    bound_composite_state: PositiveRatio,
    appended_constituent_state: PositiveRatio,
) -> bool:
    """A state appended to both endpoints preserves the exact binding Take."""

    original = exact_intermolecular_binding_take(separated_constituent_state, bound_composite_state)
    if not isinstance(appended_constituent_state, PositiveRatio):
        raise InadmissibleExactValue("an appended constituent state must be exact and positive")
    new_separated = separated_constituent_state.fraction + appended_constituent_state.fraction
    new_bound = bound_composite_state.fraction + appended_constituent_state.fraction
    extended = exact_intermolecular_binding_take(
        PositiveRatio.from_pair(new_separated.numerator, new_separated.denominator),
        PositiveRatio.from_pair(new_bound.numerator, new_bound.denominator),
    )
    return extended == original


def repeated_unit_binding(
    separated_constituent_state: PositiveRatio,
    bound_composite_state: PositiveRatio,
    repetition: PositiveCount,
) -> PositiveRatio:
    """Equal positive repetition scales both endpoints and the binding exactly."""

    if not isinstance(repetition, PositiveCount):
        raise InadmissibleExactValue("state repetition requires a positive count")
    separated = separated_constituent_state.fraction * repetition.value
    bound = bound_composite_state.fraction * repetition.value
    return exact_intermolecular_binding_take(
        PositiveRatio.from_pair(separated.numerator, separated.denominator),
        PositiveRatio.from_pair(bound.numerator, bound.denominator),
    )


def unbound_interaction_form() -> EmptyOne:
    """Return structural absence for a record that does not contain a bound state."""

    return EMPTY_ONE


@dataclass(frozen=True)
class IntermolecularBindingCarrier:
    constituents: tuple[HeldLabel, ...]
    constituent_states: tuple[HeldLabel, ...]
    bound_composite: HeldLabel
    bound_composite_state: HeldLabel
    separation_organization: HeldLabel
    interaction_channel: HeldLabel
    condition: HeldLabel
    energy_unit: HeldLabel

    def __post_init__(self) -> None:
        if not isinstance(self.constituents, tuple) or len(self.constituents) < 2:
            raise InadmissibleExactValue("intermolecular binding requires at least two named constituents")
        if len(self.constituents) != len(self.constituent_states):
            raise InadmissibleExactValue("each constituent must retain one named state")
        if len(set(self.constituents)) != len(self.constituents):
            raise InadmissibleExactValue("constituent identities must remain distinguishable")
        if any(not isinstance(value, HeldLabel) or value.family != "molecular-constituent" for value in self.constituents):
            raise InadmissibleExactValue("a constituent identity was erased or relabelled")
        if any(not isinstance(value, HeldLabel) or value.family != "constituent-state" for value in self.constituent_states):
            raise InadmissibleExactValue("a constituent state was erased or relabelled")
        required = (
            (self.bound_composite, "bound-composite"),
            (self.bound_composite_state, "bound-composite-state"),
            (self.separation_organization, "finite-separation-organization"),
            (self.interaction_channel, "intermolecular-channel"),
            (self.condition, "measurement-condition"),
            (self.energy_unit, "held-energy-unit"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("intermolecular binding carrier lost a required held field")


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001",
    "SFT-PHYS-MECH-CONSERVATION-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-MOL-GEOMETRY-001",
    "SFT-CHEM-MOL-INTERMOLECULAR-001",
    "SFT-CHEM-MOL-SUPRAMOLECULAR-001",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-BOND-DISSOCIATION-ENERGY-002",
    "SFT-CHEM-MOLECULAR-DIPOLE-MAGNITUDE-005",
    "SFT-CHEM-MOLECULAR-POLARIZABILITY-006",
    "SFT-CHEM-VIBRATIONAL-FREQUENCY-009",
    "SFT-CHEM-ROTATIONAL-CONSTANT-010",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier", "answer-only-binding-number-with-erased-components",
        "An answer-only magnitude cannot distinguish an intermolecular composite from an internal molecular state.",
        "named-constituents-and-bound-composite-carrier",
        "Every constituent, constituent state and bound composite remains separately identifiable.",
    ),
    dimension(
        "separation", "continuum-distance-or-imported-potential-coordinate",
        "A continuum coordinate or potential surface imports an ungenerated mathematical model.",
        "finite-held-separation-organization",
        "The separated endpoint is a finite generated organization retained as an exact label.",
    ),
    dimension(
        "composition", "constituent-energies-erased-or-merged",
        "Erasing constituent states destroys the separated endpoint and prevents reconstruction.",
        "exact-positive-constituent-state-composition",
        "All positive constituent states compose exactly without a numerical-zero initializer.",
    ),
    dimension(
        "magnitude", "signed-free-energy-or-negative-binding-number",
        "A signed answer leaves the positive Fold domain and obscures state order.",
        "ordered-positive-separated-Take-bound",
        "Binding is the exact positive Take of the lower bound composite from the higher separated state.",
    ),
    dimension(
        "absence", "assume-every-generated-aggregate-is-bound",
        "A proximity or calculation label does not force a stable lower composite state.",
        "strict-bound-order-or-structural-EmptyOne",
        "Only strict state order yields a binding magnitude; an unbound record remains structural EmptyOne.",
    ),
    dimension(
        "prediction", "binding-target-readable-before-seal",
        "A readable binding value could select the law, source rows or an interaction coefficient.",
        "value-free-complete-dimer-cluster-identity-seal",
        "All constituent, composite, method/basis and measurement identities seal without target values.",
    ),
    dimension(
        "record", "favorable-dimer-method-or-measurement-subset",
        "Selecting only positive or agreeing rows conceals adverse and unavailable source records.",
        "complete-computed-measured-adverse-and-scope-custody",
        "Every linked CCCBDB value, all signed adverse inscriptions, reported measurements and the wider cluster boundary remain explicit.",
    ),
    dimension(
        "extension", "fitted-interaction-coefficient-or-species-correction",
        "A fitted coefficient or species residual lets the target choose the result.",
        "one-state-order-law-with-depth-independent-constituent-extension",
        "Appending the same named constituent state to both endpoints preserves the exact Take without a new rule.",
    ),
)


EXACT_RESULT = (
    "named-constituents-and-bound-composite-carrier__finite-held-separation-organization__"
    "exact-positive-constituent-state-composition__ordered-positive-separated-Take-bound__"
    "strict-bound-order-or-structural-EmptyOne__value-free-complete-dimer-cluster-identity-seal__"
    "complete-computed-measured-adverse-and-scope-custody__"
    "one-state-order-law-with-depth-independent-constituent-extension"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    constituent_states = (PositiveRatio.from_pair(5, 2), PositiveRatio.from_pair(7, 3))
    separated = exact_separated_constituent_state(constituent_states)
    bound = PositiveRatio.from_pair(4, 1)
    binding = exact_intermolecular_binding_take(separated, bound)
    reversed_rejected = False
    try:
        exact_intermolecular_binding_take(bound, separated)
    except InadmissibleExactValue:
        reversed_rejected = True
    repeated = repeated_unit_binding(separated, bound, PositiveCount(3))
    return (
        ("exact-constituent-composition", "Two positive constituent states compose without numerical zero.", separated.fraction == Fraction(29, 6)),
        ("ordered-positive-binding-Take", "Separated 29/6 Takes bound 4 and yields exact binding 5/6.", binding.fraction == Fraction(5, 6)),
        ("orientation-retained", "Reversing state order halts rather than producing a negative Fold number.", reversed_rejected),
        ("depth-independent-extension", "Appending one shared state to both endpoints preserves the exact binding Take.", append_shared_constituent_preserves_binding(separated, bound, PositiveRatio.from_pair(11, 5))),
        ("equal-repetition", "Three equal repetitions force three times the exact binding magnitude.", repeated.fraction == Fraction(5, 2)),
        ("unbound-absence", "A record without strict bound-state order is structural EmptyOne.", isinstance(unbound_interaction_form(), EmptyOne)),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "IntermolecularBindingCarrier", "append_shared_constituent_preserves_binding",
    "exact_intermolecular_binding_take", "exact_separated_constituent_state",
    "repeated_unit_binding", "unbound_interaction_form",
)
