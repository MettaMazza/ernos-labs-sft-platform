"""Fold-native chemical phase-rule relation for THERMO-011."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class PhaseRuleAccount:
    components: tuple[HeldLabel, ...]
    phases: tuple[HeldLabel, ...]
    environment_coordinates: tuple[HeldLabel, HeldLabel]

    def __post_init__(self) -> None:
        if not self.components or any(
            not isinstance(value, HeldLabel) or value.family != "chemical-component" for value in self.components
        ):
            raise InadmissibleExactValue("phase-rule account requires positive held component support")
        if not self.phases or any(
            not isinstance(value, HeldLabel) or value.family != "chemical-phase" for value in self.phases
        ):
            raise InadmissibleExactValue("phase-rule account requires positive held phase support")
        if len(set(self.components)) != len(self.components) or len(set(self.phases)) != len(self.phases):
            raise InadmissibleExactValue("phase-rule component or phase identity was duplicated")
        if len(self.environment_coordinates) != 2 or any(
            not isinstance(value, HeldLabel) or value.family != "phase-environment-coordinate"
            for value in self.environment_coordinates
        ):
            raise InadmissibleExactValue("phase rule requires the two held environmental coordinates")
        if len(set(self.environment_coordinates)) != 2:
            raise InadmissibleExactValue("phase-rule environmental coordinates must remain distinct")


@dataclass(frozen=True)
class IndependentDegreeSupport:
    carriers: tuple[HeldLabel, ...] | EmptyOne
    count: PositiveCount | EmptyOne


def independent_degree_support(account: PhaseRuleAccount) -> IndependentDegreeSupport:
    """Cancel one available coordinate carrier for each coexisting phase."""

    if not isinstance(account, PhaseRuleAccount):
        raise InadmissibleExactValue("phase-rule cancellation requires a complete account")
    available = list(account.components + account.environment_coordinates)
    for _phase in account.phases:
        if not available:
            raise InadmissibleExactValue("phase support exceeds the complete coordinate carriers")
        available.pop()
    if not available:
        return IndependentDegreeSupport(EmptyOne(), EmptyOne())
    return IndependentDegreeSupport(tuple(available), PositiveCount(len(available)))


def joint_component_phase_successor_preserves_degree_support(account: PhaseRuleAccount) -> bool:
    """Appending one component and one phase preserves the uncancelled carrier word."""

    prior = independent_degree_support(account)
    successor = PhaseRuleAccount(
        account.components + (HeldLabel("chemical-component", f"component-{len(account.components) + 1}"),),
        account.phases + (HeldLabel("chemical-phase", f"phase-{len(account.phases) + 1}"),),
        account.environment_coordinates,
    )
    after = independent_degree_support(successor)
    if isinstance(prior.count, EmptyOne):
        return isinstance(after.count, EmptyOne)
    return isinstance(after.count, PositiveCount) and after.count.value == prior.count.value


def _account(component_count: int, phase_count: int) -> PhaseRuleAccount:
    if component_count < 1 or phase_count < 1:
        raise InadmissibleExactValue("host witness counts must be positive")
    return PhaseRuleAccount(
        tuple(HeldLabel("chemical-component", f"component-{index}") for index in range(1, component_count + 1)),
        tuple(HeldLabel("chemical-phase", f"phase-{index}") for index in range(1, phase_count + 1)),
        (
            HeldLabel("phase-environment-coordinate", "temperature"),
            HeldLabel("phase-environment-coordinate", "pressure"),
        ),
    )


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
    "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001",
    "SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002",
    "SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003",
    "SFT-CHEM-HEAT-WORK-TRANSFER-PARTITION-004",
    "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    "SFT-CHEM-ENTHALPY-EQUIVALENT-STATE-006",
    "SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007",
    "SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008",
    "SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009",
    "SFT-CHEM-FUGACITY-EQUIVALENT-GAS-MIXTURE-010",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "unbound-degree-number", "A detached number erases which component, phase and coordinate supports produced it.", "complete-component-phase-coordinate-account", "The complete account retains every component, phase and held environmental coordinate."),
    dimension("components", "bulk-substance-with-erased-independent-components", "Erasing independent component identities changes the available coordinate support.", "complete-held-independent-component-support", "Every independent component contributes one held coordinate carrier."),
    dimension("phases", "phase-label-without-coexistence-constraint", "A phase name alone does not record the equilibrium identification it imposes.", "one-exact-coordinate-cancellation-per-coexisting-phase", "Each coexisting phase cancels exactly one available coordinate carrier."),
    dimension("environment", "free-or-continuum-intensive-coordinate-space", "A free continuum imports unenumerated degrees and an additional premise.", "two-held-environment-coordinate-carriers", "Temperature and pressure are the two held environmental carriers of the complete boundary."),
    dimension("relation", "imported-subtractive-phase-rule-equation", "Importing a subtractive formula introduces signed arithmetic instead of forcing the structure.", "exact-carrier-cancellation-relation", "Degree support is the uncancelled finite carrier word after exact phase cancellation."),
    dimension("absence", "numerical-zero-degree-count", "Numerical zero is not an SFT value.", "structural-EmptyOne-invariant-state", "Complete cancellation yields structural EmptyOne rather than a numerical degree value."),
    dimension("observation", "degree-outcome-readable-before-seal", "A readable degree outcome could select the cancellation relation.", "complete-value-free-18-row-identity-seal", "All 18 component/phase identities seal before any degree outcome or source relation opens."),
    dimension("extension", "recalculate-with-free-exception", "A special-case exception would destroy structural closure.", "depth-independent-joint-component-phase-successor", "Appending one component carrier and one phase cancellation preserves the remaining degree support."),
)


EXACT_RESULT = (
    "complete-component-phase-coordinate-account__complete-held-independent-component-support__"
    "one-exact-coordinate-cancellation-per-coexisting-phase__two-held-environment-coordinate-carriers__"
    "exact-carrier-cancellation-relation__structural-EmptyOne-invariant-state__"
    "complete-value-free-18-row-identity-seal__depth-independent-joint-component-phase-successor"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    one_phase = independent_degree_support(_account(1, 1))
    two_phase = independent_degree_support(_account(1, 2))
    three_phase = independent_degree_support(_account(1, 3))
    return (
        ("one-component-one-phase", "One component and one phase leave two positive held carriers.", isinstance(one_phase.count, PositiveCount) and one_phase.count.value == 2),
        ("one-component-two-phase", "A second coexisting phase leaves one positive held carrier.", isinstance(two_phase.count, PositiveCount) and two_phase.count.value == 1),
        ("one-component-three-phase", "Complete cancellation yields structural EmptyOne.", isinstance(three_phase.count, EmptyOne)),
        ("joint-successor", "One added component and one added phase preserve degree support.", joint_component_phase_successor_preserves_degree_support(_account(2, 2))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES",
    "DIMENSIONS",
    "EXACT_RESULT",
    "IndependentDegreeSupport",
    "OPERATIONAL_WITNESSES",
    "PhaseRuleAccount",
    "independent_degree_support",
    "joint_component_phase_successor_preserves_degree_support",
)
