"""Force finite channels, confusability and exact capacity families."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-CHANNEL-CAPACITY-001"


@dataclass(frozen=True)
class FiniteChannel:
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    relation: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.inputs or not self.outputs or len(set(self.inputs)) != len(self.inputs) or len(set(self.outputs)) != len(self.outputs):
            raise ValueError("a channel requires complete nonempty canonical carriers")
        if len(set(self.relation)) != len(self.relation):
            raise ValueError("channel relation cannot duplicate transport cells")
        if any(source not in self.inputs or target not in self.outputs for source, target in self.relation):
            raise ValueError("every channel cell must remain inside its carriers")
        if any(not any(source == item for source, _ in self.relation) for item in self.inputs):
            raise ValueError("every input requires at least one possible output")


def output_support(channel: FiniteChannel, source: str) -> tuple[str, ...]:
    if source not in channel.inputs:
        raise ValueError("source is outside channel input support")
    return tuple(target for held, target in channel.relation if held == source)


def confusable(channel: FiniteChannel, left: str, right: str) -> bool:
    return bool(set(output_support(channel, left)).intersection(output_support(channel, right)))


def distinguishable_code(channel: FiniteChannel, held_inputs: tuple[str, ...]) -> bool:
    return bool(held_inputs) and len(set(held_inputs)) == len(held_inputs) and all(
        item in channel.inputs for item in held_inputs
    ) and all(
        not confusable(channel, left, right)
        for left_position, left in enumerate(held_inputs)
        for right in held_inputs[left_position + 1 :]
    )


def capacity_family(channel: FiniteChannel) -> tuple[tuple[str, ...], ...]:
    candidates = tuple(
        selection
        for held_size in range(1, len(channel.inputs) + 1)
        for selection in combinations(channel.inputs, held_size)
        if distinguishable_code(channel, selection)
    )
    greatest = max(len(selection) for selection in candidates)
    return tuple(selection for selection in candidates if len(selection) == greatest)


def compose_channels(first: FiniteChannel, second: FiniteChannel) -> FiniteChannel:
    if first.outputs != second.inputs:
        raise ValueError("channel composition requires equal canonical interface carriers")
    relation = tuple(dict.fromkeys(
        (source, target)
        for source, middle in first.relation
        for held, target in second.relation
        if middle == held
    ))
    return FiniteChannel(first.inputs, second.outputs, relation)


_clean = FiniteChannel(("a", "b", "c"), ("x", "y", "z"), (("a", "x"), ("b", "y"), ("c", "z")))
_merged = FiniteChannel(("a", "b", "c"), ("x", "z"), (("a", "x"), ("b", "x"), ("c", "z")))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact finite channels, confusability and capacity",
    statement=(
        "An admitted channel is a complete canonical input carrier, complete output carrier and held source-bound "
        "transport relation giving every input at least one output. Inputs are confusable exactly when their output "
        "supports overlap. A zero-error code is a held input selection with pairwise disjoint output supports. Exact "
        "channel capacity is the complete family of greatest-cardinality distinguishable codes, with all ties retained; "
        "composition is relational path composition at an equal interface."
    ),
    dependencies=(
        "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-MATH-OPTIMIZATION-001",
        "SFT-INFO-ENCODING-DECODING-001",
        "SFT-INFO-QUANTITY-001",
    ),
    generation_rule=(
        "Generate the complete product of input coverage, output coverage, relation provenance, transport totality, "
        "confusability, code generation, capacity selection, composition, generality and extra-channel status."
    ),
    grammar_boundary=(
        "All finite channels generated from canonical carriers, held transport relations, complete output supports, "
        "pairwise confusability checks, exhaustive input selections and exact relation composition."
    ),
    dimensions=(
        binary_dimension("inputs", "What fixes channel inputs?", "partial-input-carrier", "An omitted input changes possible messages and capacity.", "complete-canonical-inputs", "Every registered input occurs once."),
        binary_dimension("outputs", "What fixes channel outputs?", "partial-output-carrier", "An omitted output hides a possible transport image.", "complete-canonical-outputs", "Every registered output occurs once."),
        binary_dimension("relation", "What fixes transport?", "opaque-channel-box", "An opaque box hides source-to-output alternatives.", "held-transport-relation", "Every possible source/output pair is retained."),
        binary_dimension("totality", "What ensures every input can pass?", "missing-input-row", "An input without an output is outside the claimed channel action.", "nonempty-output-support-per-input", "Every input has at least one retained image."),
        binary_dimension("confusability", "When can inputs be confused?", "probability-threshold", "A threshold imports a distribution and free scale.", "overlapping-output-support", "Confusability is exact shared output membership."),
        binary_dimension("codes", "What makes a zero-error code?", "sampled-input-set", "Sampling cannot establish every pair separated.", "pairwise-disjoint-output-selection", "Every selected input pair has disjoint output support."),
        binary_dimension("capacity", "What fixes channel capacity?", "logarithmic-rate", "A real logarithmic rate imports scale and asymptotic assumptions.", "complete-greatest-code-family", "Every input selection is generated and all maximum distinguishable ties survive."),
        binary_dimension("composition", "How do channels compose?", "endpoint-guess", "Endpoints alone omit the shared interface path.", "exact-relational-paths", "Every source-to-middle and middle-to-target path generates one composite cell."),
        binary_dimension("generality", "What closes arbitrary finite carriers?", "sampled-channels", "Examples do not establish a fresh input relation.", "carrier-successor", "A fresh input adds its complete output support and all new confusability pairs."),
        binary_dimension("addition", "Is another channel model added?", "extra-transition-probability", "A probability law is not supplied by the transport relation.", "no-extra-channel-model", "Capacity follows only from exact relation and distinguishability."),
    ),
    exact_result=(
        "The channel kernel is complete input/output carriers and held total transport, exact overlap confusability, "
        "exhaustive zero-error codes, the complete greatest code family, relational composition and no stochastic rule."
    ),
    laws=(
        "channel output support retains every possible output of one exact input",
        "confusability is symmetric overlap of output supports",
        "a zero-error input code has pairwise disjoint output supports",
        "capacity retains every greatest distinguishable selection rather than applying an undeclared tie rule",
        "composed output paths cannot restore an input distinction already merged at an intermediate interface",
    ),
    induction_base="One input with one nonempty output support forms a one-member distinguishable code family.",
    induction_step=(
        "Adding one fresh input adds its exact output support and one confusability decision with every prior input. "
        "Every prior code either extends by the fresh input when all supports are disjoint or remains unchanged."
    ),
    boundary_exclusions=(
        "no transition probability or stochastic channel cause",
        "no floating error threshold",
        "no logarithmic or asymptotic capacity proof value",
        "no ungenerated infinite code family",
    ),
    witnesses=(
        Witness("clean-capacity", "Disjoint clean outputs retain all three inputs as one greatest code.", capacity_family(_clean) == (("a", "b", "c"),)),
        Witness("merged-confusability", "Inputs a and b are confusable exactly through shared output x.", confusable(_merged, "a", "b") and not confusable(_merged, "a", "c")),
        Witness("tied-capacity", "The merged channel retains both greatest two-input alternatives rather than tie-breaking.", capacity_family(_merged) == (("a", "c"), ("b", "c"))),
        Witness("code-control", "The a/b selection fails zero-error distinction while a/c passes.", not distinguishable_code(_merged, ("a", "b")) and distinguishable_code(_merged, ("a", "c"))),
        Witness("composition", "Composing two clean identity-interface channels preserves exact source/output paths.", compose_channels(_clean, FiniteChannel(("x", "y", "z"), ("u", "v", "w"), (("x", "u"), ("y", "v"), ("z", "w")))).relation == (("a", "u"), ("b", "v"), ("c", "w"))),
    ),
    why=(
        "Capacity must follow from which source distinctions a channel can preserve, not from a borrowed probabilistic "
        "rate formula. Complete finite transport and confusability make that boundary exact."
    ),
    derivation=(
        "Graphs supply relations and paths; encoding supplies messages and codewords; combinatorics exhausts selections; "
        "optimization retains all greatest codes; information quantity supplies exact distinction meaning. Ten axes "
        "force the finite zero-error channel and capacity family."
    ),
    check=(
        "Execute all 1,024 channel kernels, compare clean and merged channels, retain tied capacities, test a false code "
        "and exact composition, run adverse controls and independently regenerate the census."
    ),
    limitations=(
        "This theorem closes finite zero-error structural capacity. Probabilistic error rates and asymptotic coding "
        "theorems require separately generated finite evidence and cannot be imported here."
    ),
    correspondence_terms=("communication channel", "confusability graph", "zero-error code", "channel capacity", "channel composition"),
)
