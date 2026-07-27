"""Fold-native counted molecular-diffusion law for THERMO-016."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


DIFFUSION_CLASSES = ("binary", "self", "tracer")


@dataclass(frozen=True)
class MolecularDiffusionAccount:
    migrating_identity: HeldLabel
    constituent_identities: tuple[HeldLabel, ...]
    diffusion_class: HeldLabel
    phase_identity: HeldLabel
    source_cell: PositiveCount
    destination_cell: PositiveCount
    transition_count: PositiveCount
    tick_count: PositiveCount
    condition_support: tuple[PositiveRatio | EmptyOne, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.migrating_identity, HeldLabel) or self.migrating_identity.family != "chemical-component":
            raise InadmissibleExactValue("diffusion account lost migrating identity")
        if not self.constituent_identities or any(
            not isinstance(row, HeldLabel) or row.family != "chemical-component" for row in self.constituent_identities
        ):
            raise InadmissibleExactValue("diffusion account requires complete constituent identities")
        if len(set(self.constituent_identities)) != len(self.constituent_identities) or self.migrating_identity not in self.constituent_identities:
            raise InadmissibleExactValue("migrating identity is not uniquely retained in the constituent carrier")
        if (
            not isinstance(self.diffusion_class, HeldLabel) or self.diffusion_class.family != "diffusion-class"
            or self.diffusion_class.label not in DIFFUSION_CLASSES
        ):
            raise InadmissibleExactValue("diffusion class is not generated")
        if not isinstance(self.phase_identity, HeldLabel) or self.phase_identity.family != "chemical-phase":
            raise InadmissibleExactValue("diffusion account lost phase identity")
        if any(not isinstance(row, PositiveCount) for row in (self.source_cell, self.destination_cell, self.transition_count, self.tick_count)):
            raise InadmissibleExactValue("diffusion cells, transitions and ticks require exact positive counts")
        if abs(self.source_cell.value - self.destination_cell.value) != 1:
            raise InadmissibleExactValue("diffusion transition is not between adjacent generated cells")
        if not self.condition_support or any(not isinstance(row, (PositiveRatio, EmptyOne)) for row in self.condition_support):
            raise InadmissibleExactValue("diffusion condition carrier is incomplete")


@dataclass(frozen=True)
class CountedDiffusionRelation:
    carrier: HeldLabel
    orientation: HeldLabel
    transition_density: PositiveRatio


def forced_counted_diffusion(account: MolecularDiffusionAccount) -> CountedDiffusionRelation:
    if not isinstance(account, MolecularDiffusionAccount):
        raise InadmissibleExactValue("diffusion requires a complete molecular account")
    orientation = "toward-later-generated-cell" if account.source_cell.value < account.destination_cell.value else "toward-earlier-generated-cell"
    density = PositiveRatio.from_pair(account.transition_count.value, account.tick_count.value)
    return CountedDiffusionRelation(
        HeldLabel("molecular-diffusion-carrier", f"{account.diffusion_class.label}-identity-retained-adjacent-transition"),
        HeldLabel("diffusion-orientation", orientation), density,
    )


def external_diffusion_magnitude(inscription: str) -> PositiveRatio:
    if not isinstance(inscription, str) or not inscription.strip() or inscription.strip().startswith("-"):
        raise InadmissibleExactValue("diffusion coefficient requires exact positive external support")
    from fractions import Fraction
    try:
        value = Fraction(inscription.strip().lstrip("+"))
        return PositiveRatio.from_pair(value.numerator, value.denominator)
    except Exception as exc:
        raise InadmissibleExactValue("diffusion coefficient is not exact positive finite support") from exc


def complete_constituent_conservation(before: tuple[HeldLabel, ...], after: tuple[HeldLabel, ...]) -> bool:
    if not before or not after or any(not isinstance(row, HeldLabel) for row in before + after):
        raise InadmissibleExactValue("constituent conservation requires complete held labels")
    return tuple(sorted((row.family, row.label) for row in before)) == tuple(sorted((row.family, row.label) for row in after))


def transition_replication_preserves_relation(account: MolecularDiffusionAccount, replication: PositiveCount) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("diffusion replication requires exact positive support")
    prior = forced_counted_diffusion(account)
    replicated = MolecularDiffusionAccount(
        account.migrating_identity, account.constituent_identities, account.diffusion_class, account.phase_identity,
        account.source_cell, account.destination_cell,
        PositiveCount(account.transition_count.value * replication.value),
        PositiveCount(account.tick_count.value * replication.value), account.condition_support,
    )
    successor = forced_counted_diffusion(replicated)
    return (
        successor.carrier == prior.carrier and successor.orientation == prior.orientation
        and successor.transition_density.fraction == prior.transition_density.fraction
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-COMP-CPLX-TIME-SPACE-001",
    "SFT-COMP-CPLX-RANDOMNESS-001",
    "SFT-PHYS-MECH-CONSERVATION-001",
    "SFT-PHYS-CONDENSED-LATTICE-001",
    "SFT-PHYS-THERMO-KINETIC-TRANSPORT-001",
    "SFT-MAT-MICRO-DIFFUSION-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-MOLECULAR-STATE-TRANSITION-009",
    "SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013",
    "SFT-CHEM-SOLVATION-DISSOLUTION-FREE-ORDER-015",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "detached-diffusion-number-or-continuum-field", "A detached number or field erases molecular transitions.", "complete-molecular-transition-condition-account", "Every record retains species, medium, phase, cells, transitions, ticks and conditions."),
    dimension("identity", "anonymous-particle-or-erased-medium", "Anonymous transport cannot preserve chemical ownership.", "distinct-held-migrating-and-medium-identities", "The migrating identity and every medium constituent remain held."),
    dimension("adjacency", "unbounded-continuous-displacement", "A continuous displacement imports an ungenerated continuum.", "counted-adjacent-generated-cell-transition", "Transport is a counted transition between adjacent generated cells."),
    dimension("conservation", "created-lost-or-merged-constituent", "Creation, loss or merging violates the complete material account.", "complete-global-constituent-conservation", "The complete constituent multiset is retained across redistribution."),
    dimension("resource", "unrecorded-time-space-or-random-premise", "Unrecorded resources or random premises cannot reconstruct transport.", "exact-positive-tick-cell-and-path-support", "Time, cells and transitions are exact counted supports; uncertainty is observation closure."),
    dimension("magnitude", "imported-Fick-Brownian-Stokes-Einstein-or-fit", "An imported equation or fit selects the magnitude.", "exact-positive-postseal-diffusion-support", "Measured diffusion support opens only after the transition law seals."),
    dimension("prediction", "species-condition-method-or-value-readable-before-seal", "Readable targets could select the law.", "complete-value-free-164-record-identity-seal", "All binary, self and tracer identities seal before target content opens."),
    dimension("extension", "refit-after-transition-replication-or-record-append", "Refitting destroys exact transition provenance.", "depth-independent-common-replication-and-record-append", "Common transition/tick replication and complete append preserve the relation."),
)


EXACT_RESULT = (
    "complete-molecular-transition-condition-account__distinct-held-migrating-and-medium-identities__"
    "counted-adjacent-generated-cell-transition__complete-global-constituent-conservation__"
    "exact-positive-tick-cell-and-path-support__exact-positive-postseal-diffusion-support__"
    "complete-value-free-164-record-identity-seal__depth-independent-common-replication-and-record-append"
)


def _account(diffusion_class: str = "binary", reverse: bool = False) -> MolecularDiffusionAccount:
    components = (HeldLabel("chemical-component", "migrant"), HeldLabel("chemical-component", "medium"))
    return MolecularDiffusionAccount(
        components[0], components, HeldLabel("diffusion-class", diffusion_class), HeldLabel("chemical-phase", "liquid"),
        PositiveCount(4 if reverse else 3), PositiveCount(3 if reverse else 4), PositiveCount(7), PositiveCount(5),
        (PositiveRatio.from_pair(29815, 100), EmptyOne()),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    forward = forced_counted_diffusion(_account())
    reverse = forced_counted_diffusion(_account(reverse=True))
    components = _account().constituent_identities
    return (
        ("three-diffusion-classes", "Binary, self and tracer carriers are generated without changing the transition law.", tuple(forced_counted_diffusion(_account(name)).carrier.label for name in DIFFUSION_CLASSES) == tuple(f"{name}-identity-retained-adjacent-transition" for name in DIFFUSION_CLASSES)),
        ("held-adjacent-orientation", "Opposed cell directions are held labels, not signed displacements.", forward.orientation.label == "toward-later-generated-cell" and reverse.orientation.label == "toward-earlier-generated-cell"),
        ("exact-transition-density", "Counted transitions per counted tick form exact positive support.", forward.transition_density.fraction == PositiveRatio.from_pair(7, 5).fraction),
        ("constituent-conservation", "Adjacent redistribution preserves the complete constituent multiset.", complete_constituent_conservation(components, tuple(reversed(components)))),
        ("deterministic-replication-successor", "Common transition/tick replication preserves the relation without a random premise.", transition_replication_preserves_relation(_account("tracer"), PositiveCount(6))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIFFUSION_CLASSES", "DIMENSIONS", "EXACT_RESULT", "CountedDiffusionRelation",
    "MolecularDiffusionAccount", "OPERATIONAL_WITNESSES", "complete_constituent_conservation",
    "external_diffusion_magnitude", "forced_counted_diffusion", "transition_replication_preserves_relation",
)
