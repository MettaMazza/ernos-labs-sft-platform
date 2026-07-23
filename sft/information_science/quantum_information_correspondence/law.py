"""Force the exact support-level classical/probabilistic/quantum correspondence."""

from __future__ import annotations

from itertools import product

from sft.information_science.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-INFO-QUANTUM-CORRESPONDENCE-001"
EMPTY_ONE = ("empty-One",)
Word = tuple[str, ...]


def complete_fold_support(labels: tuple[str, ...], positions: tuple[str, ...]) -> tuple[Word, ...]:
    if len(labels) < 2 or len(set(labels)) != len(labels):
        raise ValueError("quantum support correspondence requires one Fold distinction")
    if not positions or len(set(positions)) != len(positions):
        raise ValueError("support positions must form a nonempty canonical trace")
    return tuple(tuple(word) for word in product(labels, repeat=len(positions)))


def information_unit_trace(labels: tuple[str, ...], positions: tuple[str, ...]):
    support = complete_fold_support(labels, positions)
    trace = []
    for position_index, position in enumerate(positions):
        left = tuple(labels[0] for _ in positions)
        right = left[:position_index] + (labels[1],) + left[position_index + 1 :]
        if left not in support or right not in support:
            raise ValueError("a support position lacks an independently realized Fold distinction")
        trace.append((position, "one-Fold-information-distinction", left, right))
    return tuple(trace)


def basis_correspondence(support: tuple[Word, ...]):
    if not support or len(set(support)) != len(support):
        raise ValueError("basis correspondence requires canonical complete support")
    return tuple((word, "basis:" + ":".join(word)) for word in support)


def superposition_equivalent_support(labels: tuple[str, ...], positions: tuple[str, ...]):
    support = complete_fold_support(labels, positions)
    return {
        "complete_branch_support": support,
        "branch_provenance": tuple((word, tuple(zip(positions, word))) for word in support),
        "amplitudes": "not-admitted-at-support-boundary",
    }


def joint_support(left: tuple[Word, ...], right: tuple[Word, ...]):
    if not left or not right or len(set(left)) != len(left) or len(set(right)) != len(right):
        raise ValueError("joint support requires two canonical nonempty supports")
    return tuple((a, b, a + b) for a in left for b in right)


def observe_support(
    support: tuple[Word, ...], observation: tuple[tuple[Word, str], ...], observed: str
):
    images = dict(observation)
    if len(images) != len(observation) or set(images) != set(support):
        raise ValueError("support observation must classify every branch exactly once")
    members = tuple(word for word in support if images[word] == observed)
    if not members:
        raise ValueError("observed class is outside registered image support")
    return {
        "observed_class": observed,
        "retained_branches": members,
        "closed_alternatives": tuple(word for word in support if word not in members) or EMPTY_ONE,
        "reconstruction_record": tuple((word, images[word]) for word in support),
    }


def reconstruct_support(record: tuple[tuple[Word, str], ...]) -> tuple[Word, ...]:
    if not record or len(dict(record)) != len(record):
        raise ValueError("reconstruction requires a total duplicate-free branch record")
    return tuple(word for word, _ in record)


_labels = ("held-a", "held-b")
_positions = ("p1", "p2", "p3")
_support = complete_fold_support(_labels, _positions)
_first = tuple((word, word[0]) for word in _support)
_observed = observe_support(_support, _first, "held-a")


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact quantum-information support correspondence",
    statement=(
        "One Fold distinction supplies the native information unit. Across k canonical positions, the complete generated "
        "held-label word family supplies the exact branch support corresponding to a finite quantum basis support, and "
        "complete pair cells supply joint-state support. Calling this support superposition-equivalent asserts equality "
        "of enumerated alternatives and provenance only: amplitudes, phase and dynamics are not imported. Observation "
        "returns an exact retained branch class and a complete reconstruction record. Thus classical held states, "
        "probabilistic observation classes and quantum basis support share one exact information carrier at this boundary."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-ASSEMBLY-001",
        "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
        "SFT-INFO-QUANTITY-001",
        "SFT-INFO-CONSERVATION-LOSS-001",
        "SFT-INFO-CLASSICAL-PROBABILISTIC-001",
    ),
    generation_rule=(
        "Generate the complete product of native unit, word support, basis correspondence, branch provenance, "
        "superposition boundary, joint support, observation record, reconstruction, generality and extra-quantum status."
    ),
    grammar_boundary=(
        "All finite quantum-information support correspondences generated from the two held Fold labels, canonical word "
        "positions, complete branch support, bijective basis names, pair-cell composition and total observation classes."
    ),
    dimensions=(
        binary_dimension("unit", "What fixes the quantum information unit?", "imported-qubit", "A conventional qubit premise would select the carrier.", "one-Fold-distinction", "The minimal Fold's two held labels supply one exact distinction unit."),
        binary_dimension("support", "What fixes possible basis alternatives?", "sampled-branches", "Sampling cannot establish complete finite support.", "complete-Fold-word-support", "Every held-label word over every registered position occurs once."),
        binary_dimension("basis", "What fixes correspondence to basis labels?", "unnamed-state-count", "A count erases which Fold word corresponds to which basis state.", "bijective-word-basis-trace", "Every word has one unique retained basis name and inverse."),
        binary_dimension("provenance", "What identifies a branch?", "amplitude-only-row", "A coefficient without a generated word erases branch origin.", "position-label-trace", "Every branch retains every canonical position and held label."),
        binary_dimension("superposition", "What is forced at the information boundary?", "complex-amplitude-premise", "Complex amplitudes, phases and normalization are not derived here.", "complete-alternative-support", "Superposition-equivalence means the exact complete branch family only."),
        binary_dimension("composition", "What fixes joint quantum information support?", "tensor-symbol-premise", "A borrowed symbol does not enumerate joint alternatives.", "complete-pair-cell-support", "Every left branch pairs exactly once with every right branch and retains both origins."),
        binary_dimension("observation", "What fixes a measured information class?", "stochastic-collapse", "A random collapse rule is not generated at this boundary.", "exact-observation-class", "The observed image retains its complete branch predecessor class."),
        binary_dimension("record", "What preserves closed support distinctions?", "discarded-predecessors", "Discarding the record prevents exact support reconstruction.", "complete-branch-image-record", "Every pre-observation branch and image remains available for reconstruction."),
        binary_dimension("generality", "What closes arbitrary finite position depth?", "small-depth-table", "A table does not establish the next support layer.", "position-successor", "A fresh position appends every held label to every prior branch."),
        binary_dimension("addition", "Are operational quantum laws imported?", "extra-amplitude-phase-or-gate-law", "Those structures belong to later forced derivations and would select results here.", "no-extra-quantum-operation", "Only the exact information-support correspondence is admitted."),
    ),
    exact_result=(
        "The quantum-information correspondence kernel is one Fold distinction per position, complete Fold-word branch "
        "support, bijective basis and provenance traces, support-only superposition equivalence, complete pair-cell joint "
        "support, exact observation classes, reconstructing records, position induction and no imported quantum operation."
    ),
    laws=(
        "one Fold position supplies one independently realized information distinction",
        "k positions generate every held-label word exactly once",
        "basis correspondence is bijective and retains each Fold word",
        "joint support is the complete pair product with both source coordinates retained",
        "observation plus the complete branch-image record reconstructs pre-observation support exactly",
    ),
    induction_base="The first Fold position has the two held labels, one exact distinction and a two-branch basis correspondence.",
    induction_step=(
        "Adding one fresh canonical position appends each held label to every prior word exactly once. Prior branch "
        "provenance remains intact, the new position realizes one distinction and joint-support laws remain pairwise."
    ),
    boundary_exclusions=(
        "no complex, irrational or imaginary proof value",
        "no amplitude or phase law",
        "no stochastic collapse postulate",
        "no interference, entanglement or gate semantics claimed at the support boundary",
    ),
    witnesses=(
        Witness("complete-branch-support", "Two held labels over three positions generate eight exact unique branches.", len(_support) == 8 and len(set(_support)) == 8),
        Witness("unit-trace", "Each of three positions independently realizes one Fold information distinction.", len(information_unit_trace(_labels, _positions)) == 3),
        Witness("basis-bijection", "Every branch has one unique retained basis name.", len(basis_correspondence(_support)) == 8 and len({name for _, name in basis_correspondence(_support)}) == 8),
        Witness("support-only-boundary", "Superposition-equivalent support explicitly refuses amplitudes at this boundary.", superposition_equivalent_support(_labels, _positions)["amplitudes"] == "not-admitted-at-support-boundary"),
        Witness("joint-composition", "Two one-position supports generate four exact joint pair cells.", len(joint_support(((_labels[0],), (_labels[1],)), (("x",), ("y",)))) == 4),
        Witness("record-reconstruction", "First-label observation retains four branches and its record reconstructs all eight.", len(_observed["retained_branches"]) == 4 and reconstruct_support(_observed["reconstruction_record"]) == _support),
    ),
    why=(
        "Quantum information must first establish its exact alternative carrier and its relation to classical and "
        "probabilistic information. Operational quantum effects cannot be used to select that foundation."
    ),
    derivation=(
        "Fold assembly supplies words, information quantity supplies position units, conservation supplies records, "
        "classical/probabilistic correspondence supplies held states and observation classes, and composition supplies pair cells."
    ),
    check=(
        "Execute all 1,024 kernels; exhaust three-position support, unit and basis traces, joint cells and observation "
        "reconstruction, verify the support-only boundary and independently regenerate the candidate product."
    ),
    limitations=(
        "This theorem closes only finite quantum-information support correspondence. Phase, interference, entanglement, "
        "measurement dynamics, transformations, gates, circuits and quantum fault tolerance remain quantum-branch obligations."
    ),
    correspondence_terms=("qubit support", "computational basis", "superposition support", "joint quantum state", "measurement record"),
)
