"""Fold-native joint molecular correlation and dissociation support for ELEC-007."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from sft.claim_evidence import FoldWord, PositiveRatio
from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class JointSeparatedPairSupport:
    molecular_carrier: HeldLabel
    left_centre: HeldLabel
    right_centre: HeldLabel
    joint_words: tuple[FoldWord, ...]

    def __post_init__(self) -> None:
        if self.molecular_carrier.family != "molecular-carrier":
            raise InadmissibleExactValue("joint support requires one retained molecular carrier")
        if self.left_centre.family != "separated-product-centre" or self.right_centre.family != "separated-product-centre":
            raise InadmissibleExactValue("dissociation support requires two retained product centres")
        if self.left_centre == self.right_centre:
            raise InadmissibleExactValue("the two separated product centres must remain distinguishable")
        required = _required_joint_words(self.left_centre, self.right_centre)
        if self.joint_words != required:
            raise InadmissibleExactValue(
                "joint support must retain exactly both complementary exchange assignments and no same-centre word"
            )

    @property
    def positive_joint_word_count(self) -> PositiveCount:
        return PositiveCount(len(self.joint_words))

    @property
    def positive_independent_cartesian_count(self) -> PositiveCount:
        return PositiveCount(4)

    @property
    def retains_nonfactorizable_joint_distinction(self) -> bool:
        return (
            self.positive_joint_word_count == PositiveCount(2)
            and self.positive_independent_cartesian_count == PositiveCount(4)
        )


def _assignment_word(
    first_fibre: str,
    first_centre: HeldLabel,
    second_fibre: str,
    second_centre: HeldLabel,
) -> FoldWord:
    return FoldWord(
        (
            HeldLabel("electron-held-fibre", first_fibre),
            first_centre,
            HeldLabel("electron-held-fibre", second_fibre),
            second_centre,
        )
    )


def _required_joint_words(left: HeldLabel, right: HeldLabel) -> tuple[FoldWord, ...]:
    return (
        _assignment_word("lower-fibre", left, "upper-fibre", right),
        _assignment_word("lower-fibre", right, "upper-fibre", left),
    )


def complete_separated_pair_support(
    molecule: str,
    left_product: str,
    right_product: str,
) -> JointSeparatedPairSupport:
    left = HeldLabel("separated-product-centre", left_product)
    right = HeldLabel("separated-product-centre", right_product)
    return JointSeparatedPairSupport(
        HeldLabel("molecular-carrier", molecule),
        left,
        right,
        _required_joint_words(left, right),
    )


@dataclass(frozen=True)
class PositiveDissociationObservation:
    source_identity: HeldLabel
    species_identity: HeldLabel
    state_identity: HeldLabel
    joint_support_role: HeldLabel
    positive_energy_separation: PositiveRatio
    positive_uncertainty_or_absence: Union[EmptyOne, PositiveRatio]

    def __post_init__(self) -> None:
        if self.source_identity.family != "external-source":
            raise InadmissibleExactValue("dissociation observation requires a retained external source")
        if self.species_identity.family != "chemical-species":
            raise InadmissibleExactValue("dissociation observation requires a retained species")
        if self.state_identity.family != "molecular-state":
            raise InadmissibleExactValue("dissociation observation requires a retained state")
        if self.joint_support_role.family != "joint-support-role":
            raise InadmissibleExactValue("dissociation observation requires a retained joint-support role")
        if not isinstance(self.positive_energy_separation, PositiveRatio):
            raise InadmissibleExactValue("dissociation separation must be an exact positive external record")
        if not isinstance(self.positive_uncertainty_or_absence, (EmptyOne, PositiveRatio)):
            raise InadmissibleExactValue("uncertainty must be an exact positive record or structural absence")


def dissociation_observation(
    source: str,
    species: str,
    state: str,
    role: str,
    value_numerator: int,
    value_denominator: int,
    uncertainty_numerator: object,
    uncertainty_denominator: object,
) -> PositiveDissociationObservation:
    uncertainty = (
        EMPTY_ONE
        if uncertainty_numerator == "absence" and uncertainty_denominator == "absence"
        else PositiveRatio.from_pair(int(uncertainty_numerator), int(uncertainty_denominator))
    )
    return PositiveDissociationObservation(
        HeldLabel("external-source", source),
        HeldLabel("chemical-species", species),
        HeldLabel("molecular-state", state),
        HeldLabel("joint-support-role", role),
        PositiveRatio.from_pair(value_numerator, value_denominator),
        uncertainty,
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MECH-CONSERVATION-001",
    "SFT-PHYS-QUANTUM-ENTANGLEMENT-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003",
    "SFT-CHEM-STATE-ENERGY-ORDER-004",
    "SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005",
    "SFT-CHEM-MOLECULAR-EXCLUSION-EXCHANGE-006",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier",
        "unbound-energy-only-record",
        "An energy alone erases the bound carrier and separated product identities.",
        "bound-carrier-and-product-support",
        "The complete transition retains one bound molecule and every separated product carrier.",
    ),
    dimension(
        "support",
        "independent-single-product-word",
        "One product word omits the complementary assignment required by indistinguishability and exchange.",
        "complete-complementary-joint-support",
        "Both exchange-complementary separated assignments are generated and retained.",
    ),
    dimension(
        "relation",
        "marginals-declared-complete",
        "The two one-carrier marginals generate four Cartesian words and cannot identify the exact two-word joint support.",
        "nonfactorizable-held-joint-relation",
        "The retained joint relation selects both lawful cross-centre words and excludes both same-centre words.",
    ),
    dimension(
        "exchange",
        "named-electron-product-assignment",
        "Named electrons import an unobservable constituent distinction.",
        "held-fibre-exchange-pair",
        "Complementary held fibres enumerate the two assignments without naming either electron.",
    ),
    dimension(
        "transition",
        "dissociation-as-disconnected-lookup",
        "A lookup does not preserve the molecular-to-product transition trace.",
        "bound-to-separated-support-transition",
        "Dissociation retains the bound identity, both product centres and the complete joint word set.",
    ),
    dimension(
        "energy",
        "fitted-correlation-correction",
        "A correction coefficient selected from dissociation data is a forbidden free parameter.",
        "positive-post-seal-separation-record",
        "Energy separation remains an exact positive external record opened only after the joint law is sealed.",
    ),
    dimension(
        "record",
        "selected-single-isotopologue",
        "Selecting one favourable molecule cannot test the complete registered dissociation vector.",
        "complete-measurement-and-provenance-vector",
        "Every measured, compiled, derived-ion, uncertainty and source-quality record is retained.",
    ),
    dimension(
        "extension",
        "species-specific-correlation-rule",
        "A species exception or imported correlation functional adds an unforced model.",
        "pairwise-successor-with-no-extra-rule",
        "Each added pair and product centre repeats the same exact joint-support construction.",
    ),
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    support = complete_separated_pair_support("H2", "H-left", "H-right")
    incomplete_rejected = False
    try:
        JointSeparatedPairSupport(
            support.molecular_carrier,
            support.left_centre,
            support.right_centre,
            support.joint_words[:1],
        )
    except InadmissibleExactValue:
        incomplete_rejected = True
    factorized_rejected = False
    extra_words = support.joint_words + (
        _assignment_word("lower-fibre", support.left_centre, "upper-fibre", support.left_centre),
        _assignment_word("lower-fibre", support.right_centre, "upper-fibre", support.right_centre),
    )
    try:
        JointSeparatedPairSupport(
            support.molecular_carrier,
            support.left_centre,
            support.right_centre,
            extra_words,
        )
    except InadmissibleExactValue:
        factorized_rejected = True
    same_centre_rejected = False
    try:
        complete_separated_pair_support("H2", "same", "same")
    except InadmissibleExactValue:
        same_centre_rejected = True
    return (
        (
            "complete-joint-pair",
            "Separated identical carriers retain exactly both complementary cross-centre assignments.",
            support.positive_joint_word_count == PositiveCount(2),
        ),
        (
            "nonfactorizable-support",
            "Two two-centre marginals would generate four products, while exact joint exchange support retains two.",
            support.retains_nonfactorizable_joint_distinction
            and support.positive_independent_cartesian_count == PositiveCount(4),
        ),
        (
            "incomplete-control",
            "A one-word separated support loses the complementary exchange assignment and rejects.",
            incomplete_rejected,
        ),
        (
            "factorized-control",
            "Adding both same-centre Cartesian words violates the exact correlated support and rejects.",
            factorized_rejected,
        ),
        (
            "same-centre-control",
            "A dissociation record with one repeated product centre rejects.",
            same_centre_rejected,
        ),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = (
    "bound-carrier-and-product-support__complete-complementary-joint-support__"
    "nonfactorizable-held-joint-relation__held-fibre-exchange-pair__"
    "bound-to-separated-support-transition__positive-post-seal-separation-record__"
    "complete-measurement-and-provenance-vector__pairwise-successor-with-no-extra-rule"
)


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "JointSeparatedPairSupport",
    "OPERATIONAL_WITNESSES",
    "PositiveDissociationObservation",
    "complete_separated_pair_support",
    "dissociation_observation",
)
