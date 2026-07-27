"""Fold-native solvation and dissolution free-order law for THERMO-015."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class SolvationDissolutionAccount:
    solute_identity: HeldLabel
    solvent_identities: tuple[HeldLabel, ...]
    source_state: HeldLabel
    destination_state: HeldLabel
    condition_support: PositiveRatio | EmptyOne

    def __post_init__(self) -> None:
        if not isinstance(self.solute_identity, HeldLabel) or self.solute_identity.family != "chemical-component":
            raise InadmissibleExactValue("solvation account lost solute identity")
        if not self.solvent_identities or any(
            not isinstance(row, HeldLabel) or row.family != "chemical-component" for row in self.solvent_identities
        ):
            raise InadmissibleExactValue("solvation account requires at least one held solvent identity")
        if len(set(self.solvent_identities)) != len(self.solvent_identities) or self.solute_identity in self.solvent_identities:
            raise InadmissibleExactValue("solute and solvent identities must remain distinct")
        if not isinstance(self.source_state, HeldLabel) or self.source_state.family != "chemical-state":
            raise InadmissibleExactValue("solvation account lost source state")
        if not isinstance(self.destination_state, HeldLabel) or self.destination_state.family != "chemical-state":
            raise InadmissibleExactValue("solvation account lost destination state")
        if self.source_state == self.destination_state:
            raise InadmissibleExactValue("transfer requires distinct source and destination states")
        if not isinstance(self.condition_support, (PositiveRatio, EmptyOne)):
            raise InadmissibleExactValue("condition is neither exact positive support nor structural EmptyOne")


@dataclass(frozen=True)
class ExactFreeOrder:
    orientation: HeldLabel
    magnitude: PositiveRatio | EmptyOne


def external_order_as_fold_relation(inscription: str) -> ExactFreeOrder:
    """Translate a post-seal signed external inscription without signed SFT arithmetic."""
    if not isinstance(inscription, str) or not inscription.strip():
        raise InadmissibleExactValue("external order inscription is absent")
    text = inscription.strip()
    if text.startswith("+"):
        text = text[1:]
    source_favored = text.startswith("-")
    magnitude_text = text[1:] if source_favored else text
    try:
        fraction = Fraction(magnitude_text)
        if fraction == 0:
            return ExactFreeOrder(HeldLabel("free-order", "coincident-state-support"), EmptyOne())
        magnitude = PositiveRatio.from_pair(fraction.numerator, fraction.denominator)
    except Exception as exc:
        raise InadmissibleExactValue("external order inscription is not exact finite decimal support") from exc
    return ExactFreeOrder(
        HeldLabel(
            "free-order",
            "destination-solution-retained" if source_favored else "source-separated-state-retained",
        ),
        magnitude,
    )


def forced_transfer_carrier(account: SolvationDissolutionAccount) -> HeldLabel:
    if not isinstance(account, SolvationDissolutionAccount):
        raise InadmissibleExactValue("transfer carrier requires a complete account")
    solvent_kind = "mixed-solvent" if len(account.solvent_identities) > 1 else "single-solvent"
    condition_kind = "reference-condition" if isinstance(account.condition_support, EmptyOne) else "condition-bound"
    return HeldLabel("solvation-dissolution-carrier", f"distinct-solute-{solvent_kind}-{condition_kind}-state-transfer")


def exact_solubility_capacity(inscription: str) -> PositiveRatio:
    if not isinstance(inscription, str) or not inscription.strip() or inscription.strip().startswith("-"):
        raise InadmissibleExactValue("solubility capacity requires an exact positive external inscription")
    try:
        fraction = Fraction(inscription.strip().lstrip("+"))
        return PositiveRatio.from_pair(fraction.numerator, fraction.denominator)
    except Exception as exc:
        raise InadmissibleExactValue("solubility capacity is not exact positive finite support") from exc


def common_support_replication_preserves_carrier(
    account: SolvationDissolutionAccount, replication: PositiveCount
) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("replication requires exact positive support")
    prior = forced_transfer_carrier(account)
    condition = account.condition_support
    if isinstance(condition, PositiveRatio):
        condition = PositiveRatio.from_pair(condition.numerator.value * replication.value, condition.denominator.value)
    replicated = SolvationDissolutionAccount(
        account.solute_identity, account.solvent_identities, account.source_state, account.destination_state, condition
    )
    return forced_transfer_carrier(replicated) == prior


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-THERMO-EQUILIBRIUM-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-MIXTURE-001",
    "SFT-CHEM-STOICH-SOLUTION-001",
    "SFT-CHEM-SOLUTION-EQUILIBRIUM-001",
    "SFT-CHEM-INTERMOLECULAR-BINDING-011",
    "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    "SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007",
    "SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008",
    "SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009",
    "SFT-CHEM-PHASE-RULE-STRUCTURAL-011",
    "SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013",
    "SFT-CHEM-COLLIGATIVE-COMPOSITION-RESPONSE-014",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "detached-solvation-or-solubility-number", "A detached number erases the transfer carrier.", "complete-solute-solvent-state-condition-account", "Every record retains solute, all solvents, both states and condition."),
    dimension("identity", "anonymous-or-collapsed-components", "Collapsed components cannot identify what is transferred into which solvent.", "distinct-held-solute-and-solvent-identities", "Solute and every solvent identity remain distinct and held."),
    dimension("state", "erased-source-or-destination-state", "Erasing either endpoint makes transfer direction undefined.", "held-distinct-source-and-destination-states", "Both distinct transfer endpoints remain in the carrier."),
    dimension("condition", "unbound-or-fitted-condition", "An unbound or fitted condition does not identify a measurement state.", "exact-retained-condition-or-EmptyOne-reference", "Each condition is exact positive support or structural reference absence."),
    dimension("order", "signed-free-energy-proof-value", "Signed arithmetic imports a negative SFT value.", "held-free-order-orientation-plus-positive-magnitude", "Post-seal sign becomes a held state orientation and exact positive magnitude."),
    dimension("absence", "numerical-zero-capacity-or-condition", "Numerical zero is not an SFT value.", "structural-EmptyOne-only-for-absence", "Any absent coordinate is structural EmptyOne."),
    dimension("prediction", "compound-condition-or-value-readable-before-seal", "Readable targets could select the law.", "complete-value-free-799-record-identity-seal", "All 642 solvation and 157 dissolution identities seal before content opens."),
    dimension("extension", "refit-after-replication-or-record-append", "Refitting destroys exact provenance.", "depth-independent-support-replication-and-record-append", "Common support replication and complete finite append preserve the carrier."),
)


EXACT_RESULT = (
    "complete-solute-solvent-state-condition-account__distinct-held-solute-and-solvent-identities__"
    "held-distinct-source-and-destination-states__exact-retained-condition-or-EmptyOne-reference__"
    "held-free-order-orientation-plus-positive-magnitude__structural-EmptyOne-only-for-absence__"
    "complete-value-free-799-record-identity-seal__depth-independent-support-replication-and-record-append"
)


def _account(mixed: bool = False, reference: bool = False) -> SolvationDissolutionAccount:
    solvents = (HeldLabel("chemical-component", "solvent-a"),)
    if mixed:
        solvents += (HeldLabel("chemical-component", "solvent-b"),)
    return SolvationDissolutionAccount(
        HeldLabel("chemical-component", "solute"), solvents,
        HeldLabel("chemical-state", "separated"), HeldLabel("chemical-state", "solution"),
        EmptyOne() if reference else PositiveRatio.from_pair(7, 5),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    favorable = external_order_as_fold_relation("-2.49")
    opposed = external_order_as_fold_relation("1.23")
    coincident = external_order_as_fold_relation("0")
    return (
        ("single-and-mixed-solvent-carriers", "Single and mixed solvents preserve all component identities.", forced_transfer_carrier(_account()).label.startswith("distinct-solute-single-solvent") and forced_transfer_carrier(_account(True)).label.startswith("distinct-solute-mixed-solvent")),
        ("held-free-order", "External sign becomes a held orientation with positive magnitude.", favorable.orientation.label == "destination-solution-retained" and favorable.magnitude.fraction.numerator > 0 and opposed.orientation.label == "source-separated-state-retained" and opposed.magnitude.fraction.numerator > 0),
        ("structural-absence", "An external zero glyph becomes EmptyOne only.", coincident.orientation.label == "coincident-state-support" and isinstance(coincident.magnitude, EmptyOne)),
        ("positive-capacity", "Solubility is an exact positive condition-bound capacity.", exact_solubility_capacity("0.00015").fraction.numerator > 0),
        ("replication-successor", "Common exact support replication preserves the transfer carrier.", common_support_replication_preserves_carrier(_account(), PositiveCount(5))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ExactFreeOrder", "OPERATIONAL_WITNESSES",
    "SolvationDissolutionAccount", "common_support_replication_preserves_carrier", "exact_solubility_capacity",
    "external_order_as_fold_relation", "forced_transfer_carrier",
)
