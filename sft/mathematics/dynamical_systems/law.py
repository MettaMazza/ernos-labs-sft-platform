"""Force finite exact dynamics from states, transitions and retained trajectories."""

from __future__ import annotations

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-DYNAMICAL-SYSTEMS-001"
EMPTY_ONE = ("empty-One",)


def valid_dynamics(states: tuple[str, ...], transitions: tuple[tuple[str, str], ...]) -> bool:
    return bool(states) and len(set(states)) == len(states) and len(set(transitions)) == len(transitions) and all(
        source in states and target in states for source, target in transitions
    )


def trajectory_valid(transitions: tuple[tuple[str, str], ...], trajectory: tuple[str, ...]) -> bool:
    return bool(trajectory) and all((left, right) in transitions for left, right in zip(trajectory, trajectory[1:]))


def transition_time(trajectory: tuple[str, ...]):
    if not trajectory:
        raise ValueError("time requires a generated trajectory")
    return EMPTY_ONE if len(trajectory) == 1 else tuple((left, right) for left, right in zip(trajectory, trajectory[1:]))


def fixed_forms(transitions: tuple[tuple[str, str], ...]) -> tuple[str, ...]:
    return tuple(source for source, target in transitions if source == target)


def first_return(trajectory: tuple[str, ...]):
    for terminal_position in range(1, len(trajectory)):
        terminal = trajectory[terminal_position]
        for prior_position in range(terminal_position):
            if trajectory[prior_position] == terminal:
                return trajectory[prior_position:terminal_position + 1]
    return None


def predecessor_records(transitions: tuple[tuple[str, str], ...], target: str) -> tuple[str, ...]:
    return tuple(source for source, image in transitions if image == target)


def reversible_with_record(
    transitions: tuple[tuple[str, str], ...],
    retained: tuple[tuple[str, str], ...],
) -> bool:
    return all((source, target) in retained for source, target in transitions) and len(set(retained)) == len(retained)


def stable_under_registered_perturbations(
    transitions: tuple[tuple[str, str], ...],
    reference_terminal: str,
    perturbations: tuple[str, ...],
) -> bool:
    for start in perturbations:
        frontier = (start,)
        visited: tuple[str, ...] = ()
        reached = False
        while frontier:
            held, frontier = frontier[0], frontier[1:]
            if held == reference_terminal:
                reached = True
                break
            if held in visited:
                continue
            visited += (held,)
            frontier += tuple(target for source, target in transitions if source == held and target not in visited)
        if not reached:
            return False
    return True


_states = ("a", "b", "terminal")
_flow = (("a", "b"), ("b", "terminal"), ("terminal", "terminal"))
_merge = (("a", "terminal"), ("b", "terminal"), ("terminal", "terminal"))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact generated finite dynamical systems",
    statement=(
        "An admitted dynamical system is a complete canonical state carrier with a held transition relation. A "
        "trajectory retains every state and transition; time is the positive transition trace and the identity "
        "trajectory is empty One. Fixed forms, returns, recurrence, basins, reversibility and stability are admitted "
        "only through exhaustive generated witnesses. Merged predecessors remain recoverable only when their exact "
        "records are retained."
    ),
    dependencies=(
        "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
        "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-OPTIMIZATION-001",
    ),
    generation_rule=(
        "Generate the complete product of state coverage, transition provenance, trajectory trace, time, fixed forms, "
        "return, basin/recurrence, reversibility, stability and extra-dynamic status."
    ),
    grammar_boundary=(
        "All finite dynamics generated from canonical state carriers, held transition relations, complete paths, "
        "return traces, reachability basins, retained predecessor records and registered finite perturbation classes."
    ),
    dimensions=(
        binary_dimension("states", "What fixes dynamical state?", "partial-or-aliased-state", "Omitted or aliased states change possible evolution.", "complete-canonical-states", "Every generated state occurs once with canonical identity."),
        binary_dimension("transitions", "What fixes evolution?", "opaque-update-rule", "An opaque update hides which relation cells exist.", "held-state-relation", "Every allowed state transition is a retained generated pair."),
        binary_dimension("trajectory", "What witnesses an evolution?", "endpoint-only", "Endpoints erase intervening states and cannot prove reachability.", "complete-transition-trace", "Every adjacent transition is retained in order."),
        binary_dimension("time", "What fixes elapsed computation?", "continuous-clock-parameter", "A free real clock imports scale and continuum.", "positive-transition-count", "Elapsed time is the exact trace of generated transitions; identity is empty One."),
        binary_dimension("fixed", "What fixes a stationary form?", "visual-sameness", "Presentation similarity does not prove dynamical identity.", "retained-identity-transition", "A fixed form has an explicit self relation."),
        binary_dimension("return", "What fixes recurrence or cycle?", "periodic-assertion", "A period name without a trace omits return structure.", "explicit-first-return-trace", "A retained nonempty path returns to a prior canonical state."),
        binary_dimension("basin", "What fixes a basin or attractor?", "sampled-neighborhood", "Sampling cannot establish reachability for the registered perturbation class.", "complete-reachability-selection", "Every registered state is exhaustively tested for reachability to the invariant form."),
        binary_dimension("reversibility", "How is reversal possible after merging?", "infer-unrecorded-predecessor", "A merged image does not identify which predecessor occurred.", "retained-predecessor-record", "The exact source-to-image distinction is held alongside the step."),
        binary_dimension("stability", "What fixes stability?", "epsilon-parameter", "A chosen epsilon imports a free scale.", "registered-perturbation-closure", "Every explicitly generated perturbation form satisfies the invariant reachability condition."),
        binary_dimension("addition", "Is another dynamical law added?", "extra-force-or-random-law", "An added force, differential equation or random update is not supplied by the state relation.", "no-extra-dynamic-law", "All properties follow from exact finite transition structure."),
    ),
    exact_result=(
        "The dynamical kernel is complete canonical states, held transitions, complete trajectories, transition-count "
        "time, witnessed fixed/return/basin structure, retained-record reversibility and registered perturbation stability."
    ),
    laws=(
        "trajectory composition is lawful exactly at an equal canonical interface state",
        "time is a positive transition trace and identity duration is empty One",
        "fixed, cyclic and recurrent behavior require explicit transition witnesses",
        "many-to-one evolution loses predecessor distinction unless a source record is retained",
        "stability is quantified only over a complete registered finite perturbation class",
    ),
    induction_base="One state supplies its identity trajectory; no transition time or predecessor ambiguity is introduced.",
    induction_step=(
        "Adding one transition appends one exact state pair to every extended trajectory. Fixed, return, basin, "
        "predecessor and stability obligations change only for paths that use the new relation and are rechecked completely."
    ),
    boundary_exclusions=(
        "no continuous real time premise",
        "no differential equation imported as a law",
        "no stochastic transition cause",
        "no unrecorded predecessor reconstruction",
    ),
    witnesses=(
        Witness("well-formed", "Every witness transition remains in the complete state carrier.", valid_dynamics(_states, _flow)),
        Witness("trajectory", "The a-to-b-to-terminal trace retains both allowed transitions.", trajectory_valid(_flow, ("a", "b", "terminal"))),
        Witness("time", "Two transitions are retained exactly and an identity trajectory returns empty One.", transition_time(("a", "b", "terminal")) == (("a", "b"), ("b", "terminal")) and transition_time(("a",)) == EMPTY_ONE),
        Witness("fixed-form", "The terminal witness has an explicit identity transition.", fixed_forms(_flow) == ("terminal",)),
        Witness("first-return", "A repeated canonical state yields its exact first return trace.", first_return(("a", "b", "a", "b")) == ("a", "b", "a")),
        Witness("predecessor-retention", "Both merged predecessors remain distinct and an exact retained ledger reverses them.", predecessor_records(_merge, "terminal") == ("a", "b", "terminal") and reversible_with_record(_merge, _merge)),
        Witness("registered-stability", "Every registered witness perturbation reaches terminal.", stable_under_registered_perturbations(_flow, "terminal", ("a", "b", "terminal"))),
    ),
    why=(
        "Computation and natural modelling both require change through state. Exact transitions expose the laws of "
        "time, recurrence and information loss without importing continuous equations or stochastic causes."
    ),
    derivation=(
        "Graph paths supply evolution; optimization supplies complete invariant and basin selection; canonical forms "
        "supply state identity. Ten choices force the finite transition-and-record dynamics kernel."
    ),
    check=(
        "Execute all 1,024 kernels, verify state closure, trajectories, time identity, fixed and return traces, merged "
        "predecessor records and perturbation stability, then independently regenerate the census."
    ),
    limitations=(
        "This closes exact finite dynamical systems. Continuum differential models may later appear only as measured "
        "or finite approximation correspondences, never as premises of this theorem."
    ),
    correspondence_terms=("state space", "trajectory", "fixed point", "cycle", "attractor", "reversibility", "stability"),
)
