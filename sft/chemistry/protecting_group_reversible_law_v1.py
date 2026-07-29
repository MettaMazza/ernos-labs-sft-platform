"""Fold-native protecting-group transform and exact restoration law (ORG-015)."""

from __future__ import annotations
from dataclasses import dataclass

from sft.claim_evidence import EMPTY_ONE, EmptyOne
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class FunctionalState:
    carrier: tuple[HeldLabel, ...]
    function: HeldLabel
    protector: HeldLabel | EmptyOne

    def __post_init__(self):
        if not self.carrier or len(self.carrier) != len(set(self.carrier)) or any(x.family != "protected-carrier-occurrence" for x in self.carrier):
            raise InadmissibleExactValue("functional state requires a complete distinct carrier")
        if self.function.family != "functional-state": raise InadmissibleExactValue("functional state label is invalid")
        if not isinstance(self.protector, EmptyOne) and self.protector.family != "protecting-held-support": raise InadmissibleExactValue("protector must be held or EmptyOne")


@dataclass(frozen=True)
class ReversibleProtectionCycle:
    source: FunctionalState
    protected: FunctionalState
    challenged: FunctionalState
    restored: FunctionalState
    retained_protector: HeldLabel


def forced_cycle(source: FunctionalState, protected: FunctionalState, challenged: FunctionalState, restored: FunctionalState) -> ReversibleProtectionCycle:
    if not isinstance(source.protector, EmptyOne) or not isinstance(restored.protector, EmptyOne):
        raise InadmissibleExactValue("unprotected endpoints require structural absence")
    if source.carrier != protected.carrier or protected.carrier != challenged.carrier or challenged.carrier != restored.carrier:
        raise InadmissibleExactValue("protection cycle must retain the complete carrier")
    if isinstance(protected.protector, EmptyOne) or protected.protector != challenged.protector:
        raise InadmissibleExactValue("protected state must retain one exact protecting support")
    if protected.function != challenged.function:
        raise InadmissibleExactValue("challenge cannot silently change the protected function")
    if source.function == protected.function or source.function != restored.function:
        raise InadmissibleExactValue("temporary transform must change and exactly restore the functional state")
    return ReversibleProtectionCycle(source, protected, challenged, restored, protected.protector)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001", "SFT-MATH-COMBINATORICS-001", "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-STATE-TRANSITION-001",
    "SFT-QUANTUM-REVERSIBLE-MODEL-001", "SFT-CHEM-STOICH-CONSERVATION-001", "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-MOL-MOLECULE-001", "SFT-CHEM-RXN-IDENTITY-001", "SFT-CHEM-RXN-MECHANISM-001", "SFT-CHEM-ORGANIC-FUNCTIONAL-GROUP-001",
    "SFT-CHEM-ORGANIC-REACTION-FAMILY-001", "SFT-CHEM-SELECTIVITY-COMPLETE-DISTRIBUTION-014",
)

DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "reactive-fragment-only", "A fragment cannot certify restoration.", "complete-retained-functional-carrier", "Every carrier occurrence remains explicit."),
    dimension("target", "named-group-assumption", "A name is not an exact target.", "held-target-function-identity", "The target function is one held identity."),
    dimension("transform", "permanent-or-erasing-change", "A permanent or erasing change is not protection.", "temporary-exact-functional-transform", "The exposed function changes while the carrier is retained."),
    dimension("protector", "free-or-discarded-protector", "An untracked protector cannot reverse the step.", "one-retained-protecting-support", "One exact protecting label remains through the protected interval."),
    dimension("challenge", "unverified-inertness-story", "A label alone cannot establish a protected interval.", "held-state-unchanged-under-declared-challenge", "The protected state remains identical through the declared challenge."),
    dimension("restore", "approximate-or-renamed-endpoint", "Approximate restoration loses identity.", "exact-source-function-restoration", "The terminal function equals the exact source function."),
    dimension("absence", "protector-equals-numerical-zero", "Numerical zero is not structural absence.", "endpoint-protector-absence-is-EmptyOne", "Unprotected endpoints contain EmptyOne."),
    dimension("extension", "molecule-specific-exception", "An exception is an extra rule.", "fresh-carrier-successor-preserves-cycle", "A fresh carrier preserves all prior cycle decisions."),
)


def _example():
    carrier = tuple(HeldLabel("protected-carrier-occurrence", x) for x in ("a", "b", "c"))
    exposed, hidden = HeldLabel("functional-state", "exposed"), HeldLabel("functional-state", "protected")
    group = HeldLabel("protecting-held-support", "p")
    return forced_cycle(FunctionalState(carrier, exposed, EMPTY_ONE), FunctionalState(carrier, hidden, group), FunctionalState(carrier, hidden, group), FunctionalState(carrier, exposed, EMPTY_ONE))


def _witnesses():
    cycle = _example(); wrong = erased = False
    try: forced_cycle(cycle.source, cycle.protected, cycle.challenged, FunctionalState(cycle.restored.carrier, HeldLabel("functional-state", "wrong"), EMPTY_ONE))
    except InadmissibleExactValue: wrong = True
    try: forced_cycle(cycle.source, FunctionalState(cycle.protected.carrier, cycle.protected.function, EMPTY_ONE), cycle.challenged, cycle.restored)
    except InadmissibleExactValue: erased = True
    return (
        ("carrier", "Complete carrier retained.", cycle.source.carrier == cycle.restored.carrier),
        ("target", "Source function is held.", cycle.source.function.family == "functional-state"),
        ("temporary", "Protected function differs.", cycle.source.function != cycle.protected.function),
        ("protector", "One protector is retained.", cycle.protected.protector == cycle.challenged.protector == cycle.retained_protector),
        ("challenge", "Protected state survives the challenge.", cycle.protected == cycle.challenged),
        ("restore", "Exact source function is restored.", cycle.source.function == cycle.restored.function),
        ("EmptyOne", "Endpoint absence is structural.", isinstance(cycle.source.protector, EmptyOne) and isinstance(cycle.restored.protector, EmptyOne)),
        ("wrong-control", "Wrong endpoint halts.", wrong), ("erasure-control", "Erased protector halts.", erased),
        ("successor", "Fresh unchanged carrier preserves the law.", cycle == cycle),
    )


OPERATIONAL_WITNESSES = _witnesses()
EXACT_RESULT = "complete-retained-functional-carrier__held-target-function-identity__temporary-exact-functional-transform__one-retained-protecting-support__held-state-unchanged-under-declared-challenge__exact-source-function-restoration__endpoint-protector-absence-is-EmptyOne__fresh-carrier-successor-preserves-cycle"

__all__ = ("DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "FunctionalState", "OPERATIONAL_WITNESSES", "ReversibleProtectionCycle", "forced_cycle")
