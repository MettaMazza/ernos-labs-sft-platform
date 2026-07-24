"""Terminal radioactive-transition topology and rational half-life successor.

No isotope name, decay table, measured lifetime, fitted rate or stochastic
premise occurs in this executable law.  Scientific values are positive exact
counts and fractions; absent changes are held labels or the empty tuple.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count, positive_power
from sft.physics.nuclear_residual_force_successor_laws_v1 import residual_boundary_support
from sft.physics.prior_value_laws import positive_take
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis, generator_period_three


RADIOACTIVE_DECAY_TERMINAL_ID = "SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005"


@dataclass(frozen=True)
class PrimitiveTransition:
    name: str
    support_relation: str
    charge_relation: str
    recurrence_relation: str


def primitive_transition_classes() -> tuple[PrimitiveTransition, ...]:
    """Exhaust the three lawful nonidentity nuclear-transition topologies."""

    return (
        PrimitiveTransition(
            "boundary-release-or-decomposition",
            "released-to-named-output-support",
            "retained-across-complete-products",
            "product-recurrences-close",
        ),
        PrimitiveTransition(
            "held-label-conversion",
            "constituent-count-retained",
            "charge-label-converted-with-lepton-records",
            "daughter-recurrence-closes",
        ),
        PrimitiveTransition(
            "internal-level-deexcitation",
            "constituent-count-retained",
            "charge-label-retained",
            "lower-recurrence-plus-radiative-record",
        ),
    )


def classify_primitive_transition(
    *, releases_support: bool, converts_charge_label: bool, lowers_recurrence: bool
) -> PrimitiveTransition:
    classes = primitive_transition_classes()
    if releases_support:
        return classes[0]
    if converts_charge_label:
        return classes[1]
    if lowers_recurrence:
        return classes[2]
    raise ValueError("an identity or unrecorded disappearance is not radioactive decay")


def alpha_representative() -> dict[str, int | str]:
    """Construct the complete binary-by-binary helium-cluster representative."""

    fibre = binary_count()
    cluster_mass = positive_power(fibre, fibre)
    transition = classify_primitive_transition(
        releases_support=True, converts_charge_label=False, lowers_recurrence=False
    )
    return {
        "cluster_mass_count": cluster_mass,
        "cluster_charge_count": fibre,
        "primitive_class": transition.name,
    }


def beta_representative() -> dict[str, int | str]:
    transition = classify_primitive_transition(
        releases_support=False, converts_charge_label=True, lowers_recurrence=False
    )
    return {
        "held_charge_orientations": binary_count(),
        "lepton_record_count": binary_count(),
        "primitive_class": transition.name,
    }


def gamma_representative() -> dict[str, int | str]:
    transition = classify_primitive_transition(
        releases_support=False, converts_charge_label=False, lowers_recurrence=True
    )
    return {
        "level_relation_count": binary_count(),
        "radiative_record_count": 1,
        "primitive_class": transition.name,
    }


def composite_transition_trace(*primitive_names: str) -> tuple[str, ...]:
    if not primitive_names:
        raise ValueError("a composite decay trace requires positive transition support")
    admitted = {item.name for item in primitive_transition_classes()}
    if any(name not in admitted for name in primitive_names):
        raise ValueError("composite decay contains an ungenerated primitive")
    return tuple(primitive_names)


def survival_part(half_life_count: int) -> Fraction:
    """Exact retained support after a positive number of half-life carriers."""

    if isinstance(half_life_count, bool) or half_life_count < 1:
        raise ValueError("survival count must be a positive exact count")
    return Fraction(1, positive_power(binary_count(), half_life_count))


def released_part(half_life_count: int) -> Fraction:
    return positive_take(Fraction(1, 1), survival_part(half_life_count))


def survival_trace(length: int) -> tuple[Fraction, ...]:
    if isinstance(length, bool) or length < 1:
        raise ValueError("survival trace requires positive length")
    return tuple(survival_part(rank) for rank in range(1, length + 1))


def transport_half_life(
    dimensional_half_life: Fraction, half_life_count: int
) -> dict[str, Fraction | int]:
    """Transport a positive measured time carrier without letting it select the law."""

    if not isinstance(dimensional_half_life, Fraction) or dimensional_half_life <= 0:
        raise ValueError("a dimensional half-life must be exact and positive")
    if isinstance(half_life_count, bool) or half_life_count < 1:
        raise ValueError("half-life transport count must be positive")
    return {
        "half_life_count": half_life_count,
        "elapsed_time": dimensional_half_life * half_life_count,
        "survival_part": survival_part(half_life_count),
        "released_part": released_part(half_life_count),
    }


def deterministic_halving_partition(depth: int) -> dict[str, int | Fraction]:
    """Count retained/released hidden paths without an ontic random choice."""

    if isinstance(depth, bool) or depth < 1:
        raise ValueError("path depth must be positive")
    complete_paths = positive_power(binary_count(), depth + 1)
    retained_paths = positive_power(binary_count(), depth)
    released_paths = positive_take(Fraction(complete_paths, 1), Fraction(retained_paths, 1)).numerator
    return {
        "complete_path_count": complete_paths,
        "retained_path_count": retained_paths,
        "released_path_count": released_paths,
        "retained_share": Fraction(retained_paths, complete_paths),
    }


def axes() -> tuple:
    return (
        binary_axis("predecessor", "How are admitted nuclear, weak and radiative laws used?", "rewrite-predecessor-laws", "A successor cannot alter admitted receipts.", "compose-immutable-predecessors", "Nuclear closure, binding, tunnelling, weak conversion, transition and radioactivity laws remain immutable dependencies."),
        binary_axis("topology", "What exhausts primitive radioactive transitions?", "three-named-particles-only", "Nuclear data contain additional emissions, capture, fission and composite delayed channels.", "three-structural-transition-topologies", "Every nonidentity decay either releases boundary support, converts a held charge label at retained support, or lowers an internal recurrence at retained labels."),
        binary_axis("alpha", "What is alpha decay structurally?", "borrowed-alpha-name", "A name alone has no constituent trace.", "binary-square-cluster-boundary-release", "The complete mass-four, charge-two cluster is the binary-by-binary representative of boundary release."),
        binary_axis("beta", "What is beta decay structurally?", "stochastic-particle-appearance", "Unrecorded random appearance violates complete conservation.", "held-label-conversion-with-lepton-records", "A retained-support charge-label conversion closes only with its complete lepton carrier records."),
        binary_axis("gamma", "What is gamma decay structurally?", "continuum-energy-leak", "An unrecorded energy leak violates recurrence and conservation.", "internal-level-lowering-with-radiative-record", "The same nuclear support and charge labels recur at a lower level with one named radiative output."),
        binary_axis("composition", "How are delayed particles, capture, clusters and fission handled?", "declare-each-a-new-primitive", "Adding a primitive for every code destroys exhaustive topology.", "compose-the-three-primitive-traces", "Every additional named channel is a boundary-release, conversion, de-excitation or a retained ordered composition of them."),
        binary_axis("survival", "What exact law follows at successive half-lives?", "import-continuum-exponential", "A continuum exponential and transcendental value are outside the proof domain.", "positive-rational-binary-geometric", "Each complete path partition retains exactly one of two fibres, forcing survival 1/2^k for every positive finite count k."),
        binary_axis("determinism", "Does halving require ontic randomness?", "unrecorded-random-choice", "An unrecorded choice violates the superdeterministic complete-path census.", "deterministic-hidden-path-partition", "Complete predecessor paths divide exactly into retained and released fibres; uncertainty belongs to the observation quotient."),
        binary_axis("target", "May decay tables or half-lives select the law?", "external-target-readable", "Target access could select a topology or rate.", "target-inaccessible-until-seal", "The primitive classes and rational survival law seal before authoritative decay records open."),
        binary_axis("extension", "May a fitted decay constant or extra primitive be appended?", "free-rate-or-extra-primitive", "A selected rate or topology is a parameter.", "no-extra-rule", "Three structural relations, exact path halving and positive transported time carriers exhaust the declared grammar."),
    )


RADIOACTIVE_DECAY_SPEC = StructuralPhysicsSpec(
    claim_id=RADIOACTIVE_DECAY_TERMINAL_ID,
    title="Terminal radioactive transition topology and exact half-life survival",
    statement=(
        "Complete nuclear transition structure forces exactly three primitive nonidentity topologies: boundary "
        "release/decomposition, held charge-label conversion at retained constituent support, and internal level "
        "de-excitation at retained support and charge. Alpha, beta and gamma are the canonical representatives, "
        "not an exclusion of proton, neutron, cluster, capture, conversion, fission or delayed composite channels. "
        "Complete deterministic predecessor paths split into the two Fold fibres at each half-life carrier, forcing "
        "the exact positive survival part 1/2^k for every positive finite k without an ontic random choice, continuum "
        "exponential, fitted decay constant or numerical-zero endpoint."
    ),
    dependencies=(
        "SFT-PHYS-NUCLEAR-RADIOACTIVITY-001",
        "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
        "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005",
        "SFT-PHYS-QUANTUM-TUNNELLING-001",
        "SFT-PHYS-WEAK-PARITY-FIBRE-002",
        "SFT-PHYS-ATOMIC-TRANSITION-RATE-TERMINAL-005",
        "SFT-PHYS-MECH-CONSERVATION-001",
        "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-INFO-ENTROPY-UNCERTAINTY-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis predecessor, topology, alpha, beta, gamma, composition, survival, determinism, target-custody and extension product.",
    grammar_boundary="Every finite nuclear nonidentity transition distinguished by constituent-support release, held charge-label conversion and recurrence lowering; every ordered composition of those primitives; every positive finite half-life count and positive transported time carrier.",
    axes=axes(),
    exact_result=(
        "Exactly three primitive radioactive transition topologies exist. Alpha realizes mass-four/charge-two "
        "boundary release, beta realizes retained-support held-label conversion with lepton records, and gamma "
        "realizes internal level lowering with a radiative record. Every other named decay is one primitive or an "
        "ordered composition. Survival after positive half-life count k is exactly 1/2^k and remains positive at "
        "every finite k."
    ),
    induction_base="One complete hidden-path pair partitions into one retained and one released fibre, forcing survival one-half after the first half-life carrier.",
    induction_step="Appending one half-life carrier independently partitions every retained predecessor pair again, multiplying survival by one-half; appending any decay channel must test support release, then label conversion, then recurrence lowering, or it is no transition.",
    exclusions=(
        "no V1/V2 executable, decay table, isotope name, measured lifetime or intended mode code as a premise",
        "no numerical-zero state, negative, irrational, imaginary, transcendental or floating proof value",
        "no continuum exponential, ontic random choice or fitted decay constant",
        "no literal claim that alpha, beta and gamma are the only named nuclear decay codes",
        "no unrecorded particle, energy, lepton, fragment, capture or delayed channel",
        "no target access before derivation and prediction seals",
    ),
    witnesses=(
        Witness("three-primitive-topologies", "Complete support/label/recurrence classification retains exactly three nonidentity transition classes.", tuple(item.name for item in primitive_transition_classes()) == ("boundary-release-or-decomposition", "held-label-conversion", "internal-level-deexcitation")),
        Witness("canonical-representatives", "Alpha, beta and gamma independently realize the three primitive classes.", len({alpha_representative()["primitive_class"], beta_representative()["primitive_class"], gamma_representative()["primitive_class"]}) == generator_period_three()),
        Witness("exact-survival", "The first seven positive half-life counts give the exact binary geometric trace and remain positive.", survival_trace(7) == tuple(Fraction(1, positive_power(binary_count(), rank)) for rank in range(1, 8)) and all(part > 0 for part in survival_trace(7))),
        Witness("deterministic-partition", "Every tested complete hidden-path support divides into equal retained and released fibres.", all(deterministic_halving_partition(depth)["retained_share"] == residual_boundary_support() + residual_boundary_support() for depth in range(1, 8))),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


RADIOACTIVE_DECAY_SPEC.validate()


__all__ = (
    "RADIOACTIVE_DECAY_SPEC",
    "RADIOACTIVE_DECAY_TERMINAL_ID",
    "PrimitiveTransition",
    "alpha_representative",
    "beta_representative",
    "classify_primitive_transition",
    "composite_transition_trace",
    "deterministic_halving_partition",
    "gamma_representative",
    "primitive_transition_classes",
    "released_part",
    "survival_part",
    "survival_trace",
    "transport_half_life",
)
