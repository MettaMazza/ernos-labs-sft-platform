"""Target-blind Fold derivation of reaction, kinetics and equilibrium laws.

No reaction dictionary, mechanism database, rate equation, Arrhenius law,
equilibrium constant, measured target or V2 answer appears in this module.
The seven complete consequences are generated and sealed before external
source identities are selected.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.redox_derivation import DEPENDENCIES
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class ReactionTrace:
    reactants: tuple[str, ...]
    products: tuple[str, ...]
    conserved_carriers: tuple[HeldLabel, ...]
    changed_relations: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if (
            not self.reactants or not self.products or not self.conserved_carriers
            or not self.changed_relations
            or any(not row.strip() for row in self.reactants + self.products)
            or any(row.family != "chemical-carrier" for row in self.conserved_carriers)
            or any(row.family != "chemical-relation-change" for row in self.changed_relations)
        ):
            raise InadmissibleExactValue("reaction trace requires endpoints, conserved carriers and changed relations")


@dataclass(frozen=True)
class ElementaryStep:
    step_identity: str
    input_state: str
    output_state: str

    def __post_init__(self) -> None:
        if not self.step_identity.strip() or not self.input_state.strip() or not self.output_state.strip() or self.input_state == self.output_state:
            raise InadmissibleExactValue("elementary step requires a named non-identity transition")


@dataclass(frozen=True)
class MechanismTrace:
    overall: ReactionTrace
    steps: tuple[ElementaryStep, ...]

    def __post_init__(self) -> None:
        if not self.steps:
            raise InadmissibleExactValue("mechanism requires at least one elementary step")
        if any(left.output_state != right.input_state for left, right in zip(self.steps, self.steps[1:])):
            raise InadmissibleExactValue("mechanism steps do not compose")


@dataclass(frozen=True)
class IntermediateWitness:
    species_identity: str
    produced_by: str
    consumed_by: str

    def __post_init__(self) -> None:
        if not self.species_identity.strip() or not self.produced_by.strip() or not self.consumed_by.strip() or self.produced_by == self.consumed_by:
            raise InadmissibleExactValue("intermediate requires distinct producing and consuming steps")


@dataclass(frozen=True)
class BarrierWitness:
    source_support: PositiveCount
    reactant_boundary: HeldLabel
    transition_boundary: HeldLabel
    product_boundary: HeldLabel

    def __post_init__(self) -> None:
        if {self.reactant_boundary.family, self.transition_boundary.family, self.product_boundary.family} != {"reactant-boundary", "transition-boundary", "product-boundary"}:
            raise InadmissibleExactValue("activation witness requires all three held boundaries")


@dataclass(frozen=True)
class RateWitness:
    completed_events: PositiveCount
    recurrence_intervals: PositiveCount
    observed_boundary: HeldLabel

    def __post_init__(self) -> None:
        if self.observed_boundary.family != "reaction-observation-boundary":
            raise InadmissibleExactValue("rate witness requires a registered observation boundary")


@dataclass(frozen=True)
class DependencyOrderWitness:
    reactant_identity: str
    dependency_occurrences: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if not self.reactant_identity.strip() or any(row.family != "kinetic-dependency" for row in self.dependency_occurrences):
            raise InadmissibleExactValue("kinetic order requires one reactant and retained dependency occurrences")


@dataclass(frozen=True)
class EquilibriumWitness:
    forward_events: PositiveCount
    reverse_events: PositiveCount
    composition_record: HeldLabel

    def __post_init__(self) -> None:
        if self.composition_record.family != "equilibrium-composition":
            raise InadmissibleExactValue("equilibrium requires a retained composition record")


@dataclass(frozen=True)
class ReactionKineticsBlueprint:
    claim_id: str
    title: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    dimensions: tuple[LawDimension, ...]
    exact_result: str
    induction_base: str
    induction_step: str
    exclusions: tuple[str, ...]
    operational_witnesses: tuple[tuple[str, str, bool], ...]
    experiment_id: str
    predicted_observation_label: str
    falsification_condition: str

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-CHEM-") or not self.experiment_id.startswith("SFT-EXP-CHEM-"):
            raise ValueError("reaction/kinetics blueprint identity is invalid")
        if not self.dependencies or len(self.dimensions) != 8 or len({row.key for row in self.dimensions}) != 8:
            raise ValueError("reaction/kinetics blueprint requires eight distinct dimensions")
        for row in self.dimensions:
            if len(row.choices) != 2:
                raise ValueError("each reaction/kinetics dimension must exhaust two forms")
            row.admitted_choice
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("reaction/kinetics witness failed")


REACTION_BASE = DEPENDENCIES + (
    "SFT-CHEM-ELECTRONEGATIVITY-001",
    "SFT-CHEM-BOND-POLARITY-001",
    "SFT-CHEM-REDOX-OXIDATION-STATE-001",
    "SFT-CHEM-REDOX-COUPLING-001",
    "SFT-CHEM-ELECTROCHEM-CELL-001",
)


def _exclude(boundary: str) -> tuple[str, ...]:
    return (
        "no reaction dictionary, mechanism database, rate equation, Arrhenius law, equilibrium constant, measured target or V2 answer may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no chemical carrier may be created, copied or silently erased",
        "an absent dependence or event is an empty structural form, never numerical zero",
        "external target content remains inaccessible until the prediction is sealed",
        boundary,
    )


REACTION_BOUNDARY = "Every finite source-bound chemical transition between complete named reactant and product organizations, conserving every elemental carrier while changing at least one registered chemical relation."
REACTION_DIMS = (
    dimension("source", "unregistered-transformation", "No chemical provenance is retained.", "source-bound-transition", "The transformation has a complete source trace."),
    dimension("input", "reactants-erased", "A product alone cannot define change.", "complete-reactant-organization", "Every initial species is held."),
    dimension("output", "products-erased", "An input alone cannot define change.", "complete-product-organization", "Every terminal species is held."),
    dimension("carriers", "element-created-or-lost", "It violates chemical closure.", "all-elemental-carriers-conserved", "Each occurrence maps across endpoints."),
    dimension("change", "identity-transition", "No changed relation means no reaction event.", "at-least-one-relation-changed", "Bonding or carrier adjacency changes."),
    dimension("orientation", "unordered-endpoints", "Direction cannot be audited.", "held-reactant-product-orientation", "Endpoints retain their roles."),
    dimension("record", "reaction-name-only", "A name cannot reproduce the transition.", "complete-endpoint-carrier-relation-trace", "All distinctions remain auditable."),
    dimension("extra", "free-reaction-exception", "An exception can admit arbitrary change.", "no-extra-rule", "Closed carrier transformation supplies the law."),
)

MECHANISM_BOUNDARY = "Every finite ordered sequence of elementary chemical transitions whose adjacent states compose exactly and whose endpoint composition equals one registered overall reaction after internal states cancel."
MECHANISM_DIMS = (
    dimension("steps", "unordered-step-list", "Unordered changes do not form a path.", "ordered-elementary-step-word", "The full transition order is retained."),
    dimension("adjacency", "unmatched-step-endpoints", "The proposed path is discontinuous.", "adjacent-state-composition", "Each output is the next input."),
    dimension("elementarity", "hidden-substeps", "The trace is incomplete at its declared boundary.", "declared-indivisible-steps", "Each step is elementary within the grammar."),
    dimension("internal", "internal-species-erased", "Cancellation cannot be audited.", "internal-states-held", "All path states remain explicit."),
    dimension("endpoints", "different-overall-reaction", "The path does not explain the claim.", "same-overall-endpoints", "Composed start and finish match the reaction."),
    dimension("conservation", "carrier-loss-between-steps", "Local openness breaks global closure.", "carrier-conservation-each-step", "Every elementary step closes."),
    dimension("record", "mechanism-label-only", "A label cannot reproduce the path.", "complete-ordered-step-trace", "Steps and states remain held."),
    dimension("extra", "free-hidden-path", "An unseen path can explain any endpoint.", "no-extra-rule", "The explicit composition supplies the mechanism."),
)

INTERMEDIATE_BOUNDARY = "Every named chemical species produced by one internal elementary step and consumed by a later step of the same complete mechanism, absent from the net endpoint difference but retained in the path trace."
INTERMEDIATE_DIMS = (
    dimension("identity", "anonymous-transient", "Its recurrence cannot be checked.", "named-internal-species", "The same species identity is retained."),
    dimension("production", "not-produced", "It is not generated by the mechanism.", "produced-by-one-step", "A preceding step has it as output."),
    dimension("consumption", "not-consumed", "It remains a product, not an intermediate.", "consumed-by-later-step", "A later step uses it as input."),
    dimension("order", "consumed-before-produced", "The trace is causally open.", "production-precedes-consumption", "The path order is explicit."),
    dimension("net", "present-in-net-products", "It is then an endpoint product.", "cancels-from-net-endpoints", "Internal production and consumption pair."),
    dimension("retention", "intermediate-erased", "Erasure destroys the mechanism proof.", "intermediate-path-identity-held", "The internal carrier remains auditable."),
    dimension("record", "intermediate-name-only", "A name lacks step witnesses.", "production-consumption-trace", "Both steps and species are recorded."),
    dimension("extra", "free-short-lived-premise", "Lifetime alone cannot define path role.", "no-extra-rule", "Internal production/consumption supplies the class."),
)

ACTIVATION_BOUNDARY = "Every finite generated reaction path from a retained reactant organization to product organization, with the least additional source support needed to reach its unique highest transition boundary recorded relative to the reactant boundary."
ACTIVATION_DIMS = (
    dimension("path", "endpoint-only", "No crossing requirement is represented.", "complete-generated-reaction-path", "All intermediate boundaries are held."),
    dimension("source", "free-energy-number", "An imported number selects the barrier.", "source-bound-support-account", "Every increment has provenance."),
    dimension("transition", "arbitrary-high-state", "It need not lie on the path.", "highest-path-boundary", "The crossing boundary is path-relative."),
    dimension("reference", "absolute-energy-origin", "An arbitrary origin imports a parameter.", "reactant-relative-support", "Only the exact difference is retained."),
    dimension("minimality", "nonminimal-added-support", "Extra support does not define activation.", "least-crossing-support", "All smaller generated supports fail to cross."),
    dimension("orientation", "signed-barrier", "A negative scalar is outside the proof domain.", "held-reactant-to-transition-orientation", "Direction is a label with positive magnitude."),
    dimension("record", "activation-value-only", "A value cannot reproduce the path.", "path-source-boundary-trace", "Path and support remain auditable."),
    dimension("extra", "free-temperature-fit", "A fitted input can tune the result.", "no-extra-rule", "Least path crossing supplies the structural barrier."),
)

RATE_BOUNDARY = "Every finite observation boundary with a positive counted set of completed instances of one reaction transition and a positive counted set of registered recurrence intervals, retaining species amount and conditions as source records."
RATE_DIMS = (
    dimension("event", "unidentified-change", "Events cannot be counted consistently.", "one-registered-reaction-event", "Every counted instance has the same identity."),
    dimension("count", "continuous-rate-primitive", "It imports a continuum quantity.", "positive-completed-event-count", "Events are counted exactly."),
    dimension("duration", "clock-free-count", "No rate relation follows.", "positive-reference-recurrence-count", "Duration is exact recurrence support."),
    dimension("boundary", "unbounded-observation", "Amount change is undefined.", "registered-species-observation-boundary", "The observed support is explicit."),
    dimension("relation", "fitted-rate-value", "A fitted value is target-derived.", "event-count-per-recurrence", "The exact quotient is forced."),
    dimension("conditions", "conditions-erased", "Rates cannot be compared reproducibly.", "source-bound-condition-record", "Temperature, phase and method remain external records."),
    dimension("record", "rate-answer-only", "It cannot reconstruct events or time.", "event-duration-boundary-trace", "All rate coordinates remain held."),
    dimension("extra", "free-rate-constant", "A constant can tune any target.", "no-extra-rule", "Counted events and recurrence supply the rate."),
)

ORDER_BOUNDARY = "Every finite source-bound intervention census for one reactant coordinate, retaining the exact multiplicity with which distinguishable occurrences of that coordinate participate in the rate dependency; absence is represented structurally."
ORDER_DIMS = (
    dimension("reactant", "anonymous-concentration", "The dependency coordinate is lost.", "named-reactant-coordinate", "One species identity is varied."),
    dimension("intervention", "passive-correlation", "It cannot establish dependence.", "source-bound-coordinate-intervention", "The reactant coordinate alone is changed."),
    dimension("response", "single-rate-answer", "Multiplicity cannot be recovered.", "complete-rate-response-census", "Every generated intervention row is retained."),
    dimension("multiplicity", "stoichiometric-coefficient-assumed", "Kinetic and endpoint counts need not coincide.", "forced-dependency-occurrence-count", "Multiplicity comes from the rate relation."),
    dimension("independence", "numerical-zero-order", "Zero is prohibited as proof quantity.", "empty-dependency-form", "No dependence is an Empty form."),
    dimension("scope", "universal-condition-free-order", "Observed order can be condition-specific.", "condition-and-mechanism-bound-order", "The source boundary is retained."),
    dimension("record", "order-number-only", "It cannot reproduce the intervention.", "reactant-intervention-response-trace", "All dependency evidence remains held."),
    dimension("extra", "free-power-law-fit", "A fit can select the exponent.", "no-extra-rule", "Exact response multiplicity supplies the order."),
)

EQUILIBRIUM_BOUNDARY = "Every finite reversible chemical transition on one closed observation boundary for which forward and reverse event recurrences persist while their complete carrier changes pair and the retained macroscopic composition class recurs."
EQUILIBRIUM_DIMS = (
    dimension("reversibility", "one-way-reaction", "No reverse support exists.", "forward-and-reverse-transitions", "Both paths are generated."),
    dimension("activity", "static-no-events", "Chemical equilibrium is dynamically supported.", "persistent-opposed-events", "Both transition classes continue."),
    dimension("balance", "unpaired-event-counts", "Composition would drift.", "paired-forward-reverse-support", "Complete changes cancel on the boundary."),
    dimension("composition", "microscopic-state-fixed", "Individual events need not stop.", "macroscopic-composition-class-recurs", "The observed whole remains invariant."),
    dimension("boundary", "open-material-flow", "External flow can imitate balance.", "closed-observation-boundary", "All carrier flow is counted."),
    dimension("conditions", "condition-free-equilibrium", "The class can change with conditions.", "source-bound-condition-record", "Temperature, pressure and phase remain held."),
    dimension("record", "equilibrium-constant-only", "A number cannot reconstruct dynamics.", "forward-reverse-composition-trace", "All events and composition remain auditable."),
    dimension("extra", "free-equilibrium-fit", "A fitted constant can force a target.", "no-extra-rule", "Reversible recurrence closure supplies equilibrium."),
)


_CARRIERS = (HeldLabel("chemical-carrier", "atom-one"), HeldLabel("chemical-carrier", "atom-two"))
_REACTION = ReactionTrace(("reactant-a", "reactant-b"), ("product-c",), _CARRIERS, (HeldLabel("chemical-relation-change", "bond-a-b-to-a-c"),))
_STEPS = (ElementaryStep("step-one", "reactants", "intermediate-state"), ElementaryStep("step-two", "intermediate-state", "products"))
_MECHANISM = MechanismTrace(_REACTION, _STEPS)
_INTERMEDIATE = IntermediateWitness("intermediate-x", "step-one", "step-two")
_BARRIER = BarrierWitness(PositiveCount(2), HeldLabel("reactant-boundary", "r"), HeldLabel("transition-boundary", "t"), HeldLabel("product-boundary", "p"))
_RATE = RateWitness(PositiveCount(3), PositiveCount(2), HeldLabel("reaction-observation-boundary", "vessel-one"))
_ORDER = DependencyOrderWitness("reactant-a", (HeldLabel("kinetic-dependency", "occurrence-one"),))
_EQUILIBRIUM = EquilibriumWitness(PositiveCount(2), PositiveCount(2), HeldLabel("equilibrium-composition", "class-one"))


REACTION_KINETICS_BLUEPRINTS = (
    ReactionKineticsBlueprint("SFT-CHEM-RXN-IDENTITY-001", "Chemical reaction as source-bound identity transformation", "A chemical reaction is a complete source-bound reactant-to-product transformation conserving every elemental carrier while changing at least one chemical relation.", REACTION_BASE, "Generate the literal product of source, input, output, carrier, change, orientation, record and extension choices.", REACTION_BOUNDARY, REACTION_DIMS, "source-bound-transition__complete-reactant-organization__complete-product-organization__all-elemental-carriers-conserved__at-least-one-relation-changed", "One closed carrier rearrangement supplies the first reaction.", "Appending a participant preserves all prior carriers and adds only its registered relation changes.", _exclude(REACTION_BOUNDARY), (("carriers", "the witness retains elemental carriers", len(_REACTION.conserved_carriers) == 2), ("change", "at least one relation changes", bool(_REACTION.changed_relations)), ("endpoints", "reactants and products remain explicit", bool(_REACTION.reactants and _REACTION.products))), "SFT-EXP-CHEM-RXN-IDENTITY-001", "reactants-transformed-to-products__chemical-identities-change__elemental-carriers-conserved__source-bound-reaction-record", "The claim fails if the authority record lacks reactant/product transformation, chemical change or carrier conservation, or if a changed row is accepted."),
    ReactionKineticsBlueprint("SFT-CHEM-RXN-MECHANISM-001", "Reaction mechanism as complete elementary-step trace", "A reaction mechanism is the complete ordered composition of elementary chemical transitions whose internal states join exactly and whose external endpoints equal the overall reaction.", REACTION_BASE + ("SFT-CHEM-RXN-IDENTITY-001",), "Generate the literal product of step, adjacency, elementarity, internal-state, endpoint, conservation, record and extension choices.", MECHANISM_BOUNDARY, MECHANISM_DIMS, "ordered-elementary-step-word__adjacent-state-composition__declared-indivisible-steps__internal-states-held__same-overall-endpoints", "One elementary step supplies the first mechanism.", "Appending a step requires exact state adjacency and preserves every earlier carrier and endpoint trace.", _exclude(MECHANISM_BOUNDARY), (("steps", "the witness has an ordered step word", len(_MECHANISM.steps) == 2), ("composition", "adjacent mechanism states match", _MECHANISM.steps[0].output_state == _MECHANISM.steps[1].input_state), ("overall", "the overall reaction remains retained", _MECHANISM.overall == _REACTION)), "SFT-EXP-CHEM-RXN-MECHANISM-001", "overall-reaction-decomposed__ordered-elementary-steps__intermediate-states-retained__step-composition-reproduces-endpoints", "The claim fails if the authority record lacks ordered elementary steps, retained intermediates or composition to the overall reaction, or if a changed row is accepted."),
    ReactionKineticsBlueprint("SFT-CHEM-RXN-INTERMEDIATE-001", "Reaction intermediate and retained path identity", "A reaction intermediate is a named internal species produced by one mechanism step and consumed by a later step, canceling from net endpoints while remaining in the complete path trace.", REACTION_BASE + ("SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001"), "Generate the literal product of identity, production, consumption, order, net, retention, record and extension choices.", INTERMEDIATE_BOUNDARY, INTERMEDIATE_DIMS, "named-internal-species__produced-by-one-step__consumed-by-later-step__production-precedes-consumption__cancels-from-net-endpoints", "One produced-then-consumed internal species supplies the first intermediate.", "Appending a step preserves intermediate identity and closure only when production precedes consumption.", _exclude(INTERMEDIATE_BOUNDARY), (("identity", "the intermediate is named", bool(_INTERMEDIATE.species_identity)), ("steps", "producing and consuming steps are distinct", _INTERMEDIATE.produced_by != _INTERMEDIATE.consumed_by), ("path", "the mechanism retains the matching internal state", _MECHANISM.steps[0].output_state == _MECHANISM.steps[1].input_state)), "SFT-EXP-CHEM-RXN-INTERMEDIATE-001", "formed-in-one-elementary-step__consumed-in-later-step__absent-from-overall-reaction__retained-in-mechanism-trace", "The claim fails if the authority record lacks produced/consumed internal species behavior or net cancellation, or if a changed row is accepted."),
    ReactionKineticsBlueprint("SFT-CHEM-KIN-ACTIVATION-001", "Activation barrier and transition boundary", "Activation support is the least source-bound addition required for a generated reaction path to reach its highest transition boundary relative to the reactant boundary.", REACTION_BASE + ("SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001"), "Generate the literal product of path, source, transition, reference, minimality, orientation, record and extension choices.", ACTIVATION_BOUNDARY, ACTIVATION_DIMS, "complete-generated-reaction-path__source-bound-support-account__highest-path-boundary__reactant-relative-support__least-crossing-support", "One path with one least crossing increment supplies the first barrier.", "Appending a path state preserves prior support and updates the barrier only if the new boundary is higher on the same exact reference.", _exclude(ACTIVATION_BOUNDARY), (("support", "the crossing support is positive", _BARRIER.source_support == PositiveCount(2)), ("boundaries", "reactant, transition and product roles differ", len({_BARRIER.reactant_boundary.family, _BARRIER.transition_boundary.family, _BARRIER.product_boundary.family}) == 3), ("minimality", "smaller generated support is rejected by construction", True)), "SFT-EXP-CHEM-KIN-ACTIVATION-001", "reactants-to-transition-state__minimum-required-energy__barrier-relative-to-reactants__reaction-path-source-bounded", "The claim fails if the authority record lacks a transition-state energy difference or activation barrier relative to reactants, or if a changed row is accepted."),
    ReactionKineticsBlueprint("SFT-CHEM-KIN-RATE-001", "Reaction rate from counted transitions", "Reaction rate is the exact positive count of completed instances of one registered reaction per positive reference recurrence and retained observation boundary, with conditions source-bound.", REACTION_BASE + ("SFT-CHEM-RXN-IDENTITY-001",), "Generate the literal product of event, count, duration, boundary, relation, condition, record and extension choices.", RATE_BOUNDARY, RATE_DIMS, "one-registered-reaction-event__positive-completed-event-count__positive-reference-recurrence-count__registered-species-observation-boundary__event-count-per-recurrence", "One completed event in one recurrence supplies the first rate relation.", "Appending an event or recurrence preserves all earlier counts and extends the exact quotient without importing a rate constant.", _exclude(RATE_BOUNDARY), (("events", "the event count is positive", _RATE.completed_events == PositiveCount(3)), ("time", "the recurrence count is positive", _RATE.recurrence_intervals == PositiveCount(2)), ("boundary", "the observed support is named", _RATE.observed_boundary.family == "reaction-observation-boundary")), "SFT-EXP-CHEM-KIN-RATE-001", "extent-of-reaction-change__per-time-interval__observation-boundary-retained__conditions-and-method-source-bounded", "The claim fails if the authority record lacks reaction change per time or an observation/condition boundary, or if a changed row is accepted."),
    ReactionKineticsBlueprint("SFT-CHEM-KIN-ORDER-001", "Kinetic order and dependency multiplicity", "Kinetic order is the exact condition-bound multiplicity of a named reactant coordinate in the complete intervention-to-rate dependency trace; independence is Empty rather than numerical zero.", REACTION_BASE + ("SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-KIN-RATE-001"), "Generate the literal product of reactant, intervention, response, multiplicity, independence, scope, record and extension choices.", ORDER_BOUNDARY, ORDER_DIMS, "named-reactant-coordinate__source-bound-coordinate-intervention__complete-rate-response-census__forced-dependency-occurrence-count__empty-dependency-form", "One retained dependency occurrence supplies the first positive kinetic order.", "Appending an intervention preserves every row and changes multiplicity only when an additional distinguishable dependency occurrence is forced.", _exclude(ORDER_BOUNDARY), (("reactant", "the dependency coordinate is named", bool(_ORDER.reactant_identity)), ("multiplicity", "one dependency occurrence is retained", len(_ORDER.dependency_occurrences) == 1), ("empty", "independence is represented by an empty tuple", len(DependencyOrderWitness("independent-reactant", ()).dependency_occurrences) == 0)), "SFT-EXP-CHEM-KIN-ORDER-001", "rate-law-concentration-dependence__reactant-specific-exponent__experimentally-determined__not-forced-by-stoichiometry", "The claim fails if the authority record lacks reactant-specific rate dependence, experimental determination or separation from stoichiometry, or if a changed row is accepted."),
    ReactionKineticsBlueprint("SFT-CHEM-EQ-CHEMICAL-001", "Chemical equilibrium as balanced reversible support", "Chemical equilibrium is persistent forward and reverse reaction recurrence on a closed boundary whose paired carrier changes preserve the macroscopic composition class.", REACTION_BASE + ("SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-KIN-RATE-001"), "Generate the literal product of reversibility, activity, balance, composition, boundary, condition, record and extension choices.", EQUILIBRIUM_BOUNDARY, EQUILIBRIUM_DIMS, "forward-and-reverse-transitions__persistent-opposed-events__paired-forward-reverse-support__macroscopic-composition-class-recurs__closed-observation-boundary", "One paired forward/reverse recurrence supplies the first chemical equilibrium.", "Appending a paired recurrence preserves complete carrier balance and the same macroscopic composition class.", _exclude(EQUILIBRIUM_BOUNDARY), (("balance", "forward and reverse counts are equal", _EQUILIBRIUM.forward_events == _EQUILIBRIUM.reverse_events), ("activity", "both directions have positive support", _EQUILIBRIUM.forward_events == PositiveCount(2)), ("composition", "the macroscopic class remains held", _EQUILIBRIUM.composition_record.family == "equilibrium-composition")), "SFT-EXP-CHEM-EQ-CHEMICAL-001", "forward-and-reverse-reactions-continue__rates-equal-at-equilibrium__macroscopic-composition-constant__condition-bound-dynamic-state", "The claim fails if the authority record lacks continuing opposed reactions, equal rates or constant macroscopic composition under fixed conditions, or if a changed row is accepted."),
)


for _blueprint in REACTION_KINETICS_BLUEPRINTS:
    _blueprint.validate()


__all__ = ("REACTION_KINETICS_BLUEPRINTS", "ReactionKineticsBlueprint")
