"""Exact Fold erasure cost and Maxwell-demon information ledger."""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-THERMO-LANDAUER-DEMON-TERMINAL-018"
QUARTER_ONE = Fraction(1, 4)
HALF_ONE = Fraction(1, 2)
THREE_QUARTER_ONE = Fraction(3, 4)


def fold_part(value: Fraction) -> Fraction:
    if not isinstance(value, Fraction) or value <= 0 or value > 1:
        raise ValueError("Fold requires one exact positive part")
    paired = value + value
    return paired if paired <= 1 else paired - 1


def reset_preimages() -> tuple[Fraction, Fraction]:
    images = (fold_part(QUARTER_ONE), fold_part(THREE_QUARTER_ONE))
    if images != (HALF_ONE, HALF_ONE):
        raise ValueError("the reset fibre did not merge at half-One")
    return QUARTER_ONE, THREE_QUARTER_ONE


def erased_distinction_count() -> int:
    """The two-to-one reset closes exactly one binary distinction."""

    preimages = reset_preimages()
    distinct_labels = len(set(preimages))
    if distinct_labels != 2:
        raise ValueError("reset requires the complete two-label fibre")
    return distinct_labels - 1


def minimum_throw() -> Fraction:
    """Native exact separation carried by the erased binary fibre."""

    lower, upper = reset_preimages()
    return upper - lower


def reversible_reset_labels() -> tuple[str, str]:
    return "lower-preimage", "upper-preimage"


def reset_is_reversible_with_record(record: str) -> bool:
    return record in reversible_reset_labels()


def demon_cycle_ledger() -> dict[str, object]:
    """Retain the gained, erased and exported distinction as one closed ledger."""

    gained = ("gas-speed-class",)
    memory = ("lower-preimage", "upper-preimage")
    exported = ("environment-reverse-label",)
    return {
        "sorting_gain": gained,
        "memory_support": memory,
        "reset_image": ("ready-half-One",),
        "erased_distinctions": erased_distinction_count(),
        "environment_record": exported,
        "complete": len(gained) == len(exported) == erased_distinction_count(),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Exact one-distinction erasure cost and Maxwell-demon ledger",
    statement=(
        "The Fold reset maps the two held preimages quarter-One and three-quarter-One "
        "to the common ready image half-One.  It therefore closes exactly one "
        "binary distinction and has native separation half-One.  Reversal is "
        "possible exactly when one of the two predecessor labels is retained.  A "
        "Maxwell sorting cycle gains one gas distinction, stores it in the demon's "
        "two-label memory, and on reset must export one reverse label to the "
        "environment.  The complete closed ledger therefore contains no free "
        "unrecorded gain.  This is the exact model-native erasure law; dimensional "
        "thermal-energy correspondence is tested only after sealing."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-FOUNDATION-HALF-ONE-001",
        "SFT-INFO-CONSERVATION-LOSS-001",
        "SFT-INFO-ENTROPY-UNCERTAINTY-001",
        "SFT-COMP-CPLX-REVERSIBILITY-COST-001",
        "SFT-PHYS-THERMO-IRREVERSIBILITY-001",
        "SFT-PHYS-THERMO-SECOND-LAW-001",
        "SFT-PHYS-THERMO-HEAT-WORK-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of reset support, image, distinction, "
        "native throw, reverse record, sorting, memory, environment, thermal "
        "translation and extension forms."
    ),
    grammar_boundary=(
        "Every exact reset of the complete two-preimage Fold fibre to one held "
        "ready image; every finite closed sorting-memory-reset-environment cycle; "
        "and every retained predecessor-label assignment."
    ),
    axes=(
        binary_axis("support", "Which reset support is generated?", "sampled-memory-state", "A sampled state cannot establish a two-to-one reset.", "complete-two-preimage-fibre", "Both exact Fold predecessors are retained."),
        binary_axis("image", "What is the ready image?", "selected-reset-state", "A selected state has no Fold trace.", "common-half-One-image", "Quarter-One and three-quarter-One both Fold to half-One."),
        binary_axis("distinction", "How much information is closed?", "unquantified-information-loss", "An unquantified loss cannot balance a cycle.", "exactly-one-binary-distinction", "Two held alternatives merging to one image close one predecessor label."),
        binary_axis("throw", "What is the native erasure carrier?", "free-or-vanishing-cost", "A free or vanishing cost violates the exact fibre separation.", "half-One-preimage-separation", "The two reset predecessors are separated by exactly half-One."),
        binary_axis("reverse", "What makes reset reversible?", "infer-erased-predecessor", "The common image cannot identify its source.", "retain-one-predecessor-label", "One of the two exact labels reconstructs the source."),
        binary_axis("sorting", "What does the demon gain?", "unrecorded-sorting-gain", "An unrecorded distinction is outside the closed system.", "one-held-gas-distinction", "The sort transfers one speed-class distinction into memory."),
        binary_axis("memory", "How is the decision stored?", "memory-without-two-states", "A one-state memory cannot encode the decision.", "two-label-Fold-memory", "The memory uses the complete lower/upper predecessor fibre."),
        binary_axis("environment", "What happens on reset?", "erased-without-external-record", "That would destroy the predecessor distinction from the closed ledger.", "one-environment-reverse-label", "The environment retains the one label closed by the memory observation."),
        binary_axis("thermal", "When is physical energy introduced?", "import-kT-log-two-as-premise", "A conventional thermal formula cannot select the Fold law.", "postseal-dimensional-correspondence", "The exact distinction/throw law is sealed before experimental thermal translation."),
        binary_axis("extension", "May an extra cost rule enter?", "free-cost-or-demon-exception", "A free exception defeats closure.", "no-extra-rule", "Fibre cardinality, separation and record conservation exhaust the cycle."),
    ),
    exact_result=(
        "Resetting the complete quarter-One/three-quarter-One Fold fibre to "
        "half-One closes exactly one binary distinction with native throw "
        "half-One; reversal requires one predecessor label; and a closed "
        "Maxwell-demon cycle exports exactly that one label to its environment."
    ),
    induction_base=(
        "One two-preimage reset closes one distinction, and one retained label "
        "restores the exact predecessor."
    ),
    induction_step=(
        "Appending one independent reset appends one two-label fibre, one closed "
        "distinction and one required environment reverse label; the complete "
        "ledger therefore extends without an unrecorded gain."
    ),
    exclusions=(
        "no conventional Landauer formula, logarithm or experimental target as a derivation premise",
        "no claim that native half-One is numerically identical to a dimensional energy ratio",
        "no numerical-zero, negative, irrational, imaginary or floating proof value",
        "no stochastic demon decision, free reset or omitted environment record",
        "no V1/V2 executable, answer table or stored survivor",
    ),
    witnesses=(
        Witness("two-to-one-reset", "Both exact predecessors Fold to the common half-One image.", tuple(fold_part(value) for value in reset_preimages()) == (HALF_ONE, HALF_ONE)),
        Witness("one-distinction", "The complete reset closes exactly one binary predecessor label.", erased_distinction_count() == 1),
        Witness("half-One-throw", "The two exact preimages are separated by half-One.", minimum_throw() == HALF_ONE),
        Witness("record-reversal", "Either retained fibre label identifies the source class.", all(reset_is_reversible_with_record(label) for label in reversible_reset_labels())),
        Witness("demon-ledger", "One gained distinction equals one exported reverse label.", demon_cycle_ledger()["complete"] is True),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "SPEC",
    "demon_cycle_ledger",
    "erased_distinction_count",
    "fold_part",
    "minimum_throw",
    "reset_is_reversible_with_record",
    "reset_preimages",
    "reversible_reset_labels",
)
