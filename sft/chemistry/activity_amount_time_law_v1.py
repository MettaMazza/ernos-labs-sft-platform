"""Fold-native activity, amount and counted-time relation (NUCHEM-003)."""
from dataclasses import dataclass
from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension

@dataclass(frozen=True)
class ActivityLedger:
    nuclide: HeldLabel; species: HeldLabel; initial_occurrences: PositiveCount; transformations: PositiveCount; resource_intervals: PositiveCount
    def __post_init__(self):
        if (self.nuclide.family,self.species.family)!=("nuclide","chemical-species") or self.transformations.value>self.initial_occurrences.value:raise InadmissibleExactValue("bounded nuclide activity ledger required")
    @property
    def activity(self):return PositiveRatio.from_pair(self.transformations.value,self.resource_intervals.value)
    @property
    def retained_amount(self):
        left=self.initial_occurrences.value-self.transformations.value
        return EMPTY_ONE if left==0 else PositiveCount(left)

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-CHEM-MEAS-AMOUNT-001","SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005","SFT-CHEM-NUCLEAR-CHEMICAL-CARRIER-001","SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002")
DIMENSIONS=(dimension("identity","anonymous-activity-number","Activity needs nuclide/species custody.","held-nuclide-species","Nuclide and species remain held."),dimension("amount","continuum-amount-premise","Continuum amount hides occurrences.","positive-counted-initial-occurrences","Initial amount is counted."),dimension("events","expected-decay-number","Expectation is not event custody.","positive-counted-transformations","Transformations are counted."),dimension("time","continuous-time-premise","Continuum time is not proof support.","positive-counted-resource-intervals","Time support is counted."),dimension("activity","fitted-decay-constant","A fit cannot define activity.","exact-transformations-per-resource","Activity is an exact ratio."),dimension("remaining","signed-amount-difference","Signed subtraction imports negative values.","positive-Take-or-EmptyOne-retained-amount","Remaining amount is positive or absent."),dimension("record","selected-reference-time","One time hides evolution.","complete-activity-amount-time-vector","All registered times remain."),dimension("extension","differential-equation-premise","A differential equation is not required.","ledger-successor-recomputes-relation","Successors update counts exactly."))
EXACT_RESULT="held-nuclide-species__positive-counted-initial-occurrences__positive-counted-transformations__positive-counted-resource-intervals__exact-transformations-per-resource__positive-Take-or-EmptyOne-retained-amount__complete-activity-amount-time-vector__ledger-successor-recomputes-relation"
def _l(i=5,e=2,t=3):return ActivityLedger(HeldLabel("nuclide","n"),HeldLabel("chemical-species","s"),PositiveCount(i),PositiveCount(e),PositiveCount(t))
OPERATIONAL_WITNESSES=(("identity","Identity held.",_l().nuclide.label=="n"),("amount","Amount counted.",_l().initial_occurrences.value==5),("events","Events counted.",_l().transformations.value==2),("time","Resource counted.",_l().resource_intervals.value==3),("activity","Ratio exact.",_l().activity.fraction.numerator==2 and _l().activity.fraction.denominator==3),("remaining","Take positive.",_l().retained_amount.value==3),("absence","Complete transformation closes.",_l(2,2,1).retained_amount==EMPTY_ONE),("successor","Successor recomputes.",_l(5,3,3).activity.fraction==1))
