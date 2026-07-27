"""Fold-native inorganic acid/base and redox network law (INORG-017)."""
from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence.fold_language import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


def chemical_species(label: str) -> HeldLabel:
    return HeldLabel("chemical-species", label)


@dataclass(frozen=True)
class ExactLewisAdductStep:
    step: HeldLabel
    pair_provider: HeldLabel
    pair_acceptor: HeldLabel
    electron_pair: tuple[HeldLabel, HeldLabel]
    adduct: HeldLabel

    def __post_init__(self) -> None:
        if self.step.family != "inorganic-network-step":
            raise InadmissibleExactValue("Lewis step identity is invalid")
        if any(row.family != "chemical-species" for row in (self.pair_provider, self.pair_acceptor, self.adduct)):
            raise InadmissibleExactValue("Lewis endpoints and adduct must retain chemical identities")
        if len({self.pair_provider, self.pair_acceptor, self.adduct}) != 3:
            raise InadmissibleExactValue("Lewis provider, acceptor and adduct occurrences must be distinct")
        if (
            len(self.electron_pair) != 2
            or self.electron_pair[0] == self.electron_pair[1]
            or any(row.family != "electron-carrier" for row in self.electron_pair)
        ):
            raise InadmissibleExactValue("Lewis joining requires the exact two retained pair occurrences")

    @property
    def participants(self) -> tuple[HeldLabel, HeldLabel, HeldLabel]:
        return (self.pair_provider, self.pair_acceptor, self.adduct)


@dataclass(frozen=True)
class ExactRedoxStep:
    step: HeldLabel
    electron_donor: HeldLabel
    electron_acceptor: HeldLabel
    electron_support: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if self.step.family != "inorganic-network-step":
            raise InadmissibleExactValue("redox step identity is invalid")
        if any(row.family != "chemical-species" for row in (self.electron_donor, self.electron_acceptor)):
            raise InadmissibleExactValue("redox endpoints must retain chemical identities")
        if self.electron_donor == self.electron_acceptor:
            raise InadmissibleExactValue("redox transfer requires distinct donor and acceptor occurrences")
        if (
            not self.electron_support
            or len(set(self.electron_support)) != len(self.electron_support)
            or any(row.family != "electron-carrier" for row in self.electron_support)
        ):
            raise InadmissibleExactValue("redox transfer requires positive complete electron support")

    @property
    def transfer_count(self) -> PositiveCount:
        return PositiveCount(len(self.electron_support))

    @property
    def participants(self) -> tuple[HeldLabel, HeldLabel]:
        return (self.electron_donor, self.electron_acceptor)


@dataclass(frozen=True)
class ExactInorganicReactionNetwork:
    network: HeldLabel
    species: tuple[HeldLabel, ...]
    acid_base_steps: object
    redox_steps: object
    ordered_path: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if self.network.family != "inorganic-reaction-network":
            raise InadmissibleExactValue("reaction network identity is invalid")
        if not self.species or len(set(self.species)) != len(self.species):
            raise InadmissibleExactValue("reaction network requires positive complete species support")
        if any(row.family != "chemical-species" for row in self.species):
            raise InadmissibleExactValue("network species identity is invalid")
        acid_steps = () if isinstance(self.acid_base_steps, EmptyOne) else self.acid_base_steps
        redox_steps = () if isinstance(self.redox_steps, EmptyOne) else self.redox_steps
        if not acid_steps and not redox_steps:
            raise InadmissibleExactValue("a reaction network requires positive transition support")
        if any(not isinstance(row, ExactLewisAdductStep) for row in acid_steps):
            raise InadmissibleExactValue("acid/base transition support is invalid")
        if any(not isinstance(row, ExactRedoxStep) for row in redox_steps):
            raise InadmissibleExactValue("redox transition support is invalid")
        steps = tuple(row.step for row in acid_steps + redox_steps)
        if len(set(steps)) != len(steps):
            raise InadmissibleExactValue("network step identities are duplicated")
        if len(self.ordered_path) != len(steps) or set(self.ordered_path) != set(steps):
            raise InadmissibleExactValue("ordered path must retain every network step exactly once")
        participants = tuple(item for row in acid_steps + redox_steps for item in row.participants)
        if any(item not in self.species for item in participants):
            raise InadmissibleExactValue("network species support omits a transition participant")

    @property
    def step_count(self) -> PositiveCount:
        return PositiveCount(len(self.ordered_path))


def lewis_step(label: str, provider: str, acceptor: str, adduct: str) -> ExactLewisAdductStep:
    return ExactLewisAdductStep(
        HeldLabel("inorganic-network-step", label),
        chemical_species(provider),
        chemical_species(acceptor),
        (
            HeldLabel("electron-carrier", f"{label}-fibre-one"),
            HeldLabel("electron-carrier", f"{label}-fibre-two"),
        ),
        chemical_species(adduct),
    )


def redox_step(label: str, donor: str, acceptor: str, transfer_count: PositiveCount) -> ExactRedoxStep:
    return ExactRedoxStep(
        HeldLabel("inorganic-network-step", label),
        chemical_species(donor),
        chemical_species(acceptor),
        tuple(
            HeldLabel("electron-carrier", f"{label}-electron-{index}")
            for index in range(1, transfer_count.value + 1)
        ),
    )


def reverse_redox(step: ExactRedoxStep, reverse_label: str) -> ExactRedoxStep:
    return ExactRedoxStep(
        HeldLabel("inorganic-network-step", reverse_label),
        step.electron_acceptor,
        step.electron_donor,
        step.electron_support,
    )


def reaction_network(
    label: str,
    species_labels: tuple[str, ...],
    acid_base_steps: tuple[ExactLewisAdductStep, ...],
    redox_steps: tuple[ExactRedoxStep, ...],
    ordered_step_labels: tuple[str, ...],
) -> ExactInorganicReactionNetwork:
    return ExactInorganicReactionNetwork(
        HeldLabel("inorganic-reaction-network", label),
        tuple(chemical_species(item) for item in species_labels),
        acid_base_steps if acid_base_steps else EMPTY_ONE,
        redox_steps if redox_steps else EMPTY_ONE,
        tuple(HeldLabel("inorganic-network-step", item) for item in ordered_step_labels),
    )


def append_redox_step(
    state: ExactInorganicReactionNetwork,
    step: ExactRedoxStep,
) -> ExactInorganicReactionNetwork:
    acid_steps = () if isinstance(state.acid_base_steps, EmptyOne) else state.acid_base_steps
    redox_steps = () if isinstance(state.redox_steps, EmptyOne) else state.redox_steps
    new_species = tuple(
        dict.fromkeys(state.species + step.participants)
    )
    return ExactInorganicReactionNetwork(
        state.network,
        new_species,
        acid_steps if acid_steps else EMPTY_ONE,
        redox_steps + (step,),
        state.ordered_path + (step.step,),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-OPERATIONAL-PROCESS-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-AB-LEWIS-001",
    "SFT-CHEM-REDOX-OXIDATION-STATE-001",
    "SFT-CHEM-REDOX-COUPLING-001",
    "SFT-CHEM-RXN-IDENTITY-001",
    "SFT-CHEM-RXN-MECHANISM-001",
    "SFT-CHEM-OXIDATIVE-ADDITION-REDUCTIVE-ELIMINATION-012",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier",
        "selected-inorganic-equation",
        "One selected equation does not close a reaction network.",
        "complete-finite-species-transition-network",
        "Every retained species and transition belongs to one finite complete network.",
    ),
    dimension(
        "species",
        "untracked-reagent-labels",
        "Untracked labels cannot establish conservation.",
        "complete-held-species-identity-support",
        "Every participant and product identity remains held.",
    ),
    dimension(
        "acid-base",
        "assumed-acid-and-base-names",
        "Names alone do not establish pair transfer.",
        "provider-acceptor-two-occurrence-pair-transfer",
        "Two retained electron occurrences join one provider to one acceptor.",
    ),
    dimension(
        "adduct",
        "unstructured-acid-base-mixture",
        "A mixture loses the joining record.",
        "retained-provider-acceptor-adduct-composition",
        "Provider, acceptor, pair support and the resulting adduct remain explicit.",
    ),
    dimension(
        "redox",
        "signed-oxidation-number-arithmetic",
        "A signed inscription is not a native transfer record.",
        "positive-complete-held-electron-transfer",
        "Oxidation and reduction share one positive complete held transfer support.",
    ),
    dimension(
        "coupling",
        "independent-oxidation-and-reduction-labels",
        "Independent labels can violate carrier conservation.",
        "one-donor-acceptor-conserved-transfer",
        "The donor removal and acceptor receipt are the same retained electron occurrences.",
    ),
    dimension(
        "path",
        "unordered-reaction-list",
        "An unordered list loses operational composition.",
        "complete-ordered-transition-path",
        "Every step appears exactly once in the retained path order.",
    ),
    dimension(
        "extension",
        "named-reaction-exception",
        "A named exception destroys closure.",
        "transition-successor-no-extra-rule",
        "A fresh exact step extends species and path support by the same law.",
    ),
)


def _operational_witnesses() -> tuple[tuple[str, str, bool], ...]:
    acid_base = lewis_step("pair", "base", "acid", "adduct")
    acid_network = reaction_network(
        "acid-base",
        ("base", "acid", "adduct"),
        (acid_base,),
        (),
        ("pair",),
    )
    oxidation = redox_step("forward", "donor", "acceptor", PositiveCount(2))
    reduction = reverse_redox(oxidation, "reverse")
    redox_network = reaction_network(
        "redox",
        ("donor", "acceptor"),
        (),
        (oxidation,),
        ("forward",),
    )
    extended = append_redox_step(acid_network, oxidation)
    incomplete_rejected = False
    try:
        reaction_network("bad", ("base", "acid"), (acid_base,), (), ("pair",))
    except InadmissibleExactValue:
        incomplete_rejected = True
    return (
        (
            "Lewis-adduct",
            "Provider, acceptor, two electron occurrences and adduct remain held.",
            acid_network.step_count == PositiveCount(1)
            and len(acid_base.electron_pair) == 2
            and acid_base.adduct in acid_network.species,
        ),
        (
            "redox-transfer",
            "One positive two-occurrence transfer couples donor oxidation to acceptor reduction.",
            redox_network.step_count == PositiveCount(1)
            and oxidation.transfer_count == PositiveCount(2),
        ),
        (
            "redox-reverse",
            "The reverse retains the same electron occurrences and swaps exact endpoints.",
            reduction.electron_support == oxidation.electron_support
            and reduction.electron_donor == oxidation.electron_acceptor
            and reduction.electron_acceptor == oxidation.electron_donor,
        ),
        (
            "network-successor",
            "Appending one redox step retains the Lewis step and extends the path once.",
            extended.step_count == PositiveCount(2)
            and extended.ordered_path == (acid_base.step, oxidation.step),
        ),
        (
            "species-control",
            "Omitting the adduct species rejects the network.",
            incomplete_rejected,
        ),
    )


OPERATIONAL_WITNESSES = _operational_witnesses()
EXACT_RESULT = (
    "complete-finite-species-transition-network__complete-held-species-identity-support__"
    "provider-acceptor-two-occurrence-pair-transfer__retained-provider-acceptor-adduct-composition__"
    "positive-complete-held-electron-transfer__one-donor-acceptor-conserved-transfer__"
    "complete-ordered-transition-path__transition-successor-no-extra-rule"
)

__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "ExactInorganicReactionNetwork",
    "ExactLewisAdductStep",
    "ExactRedoxStep",
    "OPERATIONAL_WITNESSES",
    "append_redox_step",
    "chemical_species",
    "lewis_step",
    "reaction_network",
    "redox_step",
    "reverse_redox",
)
