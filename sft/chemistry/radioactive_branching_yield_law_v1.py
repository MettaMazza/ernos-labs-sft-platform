"""Fold-native radioactive branching chemical-yield law (NUCHEM-004)."""
from dataclasses import dataclass
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension

@dataclass(frozen=True)
class BranchYield:
    channel: HeldLabel; daughter_species: HeldLabel; events: PositiveCount; recovered: PositiveCount
    def __post_init__(self):
        if (self.channel.family,self.daughter_species.family)!=("decay-channel","daughter-species") or self.recovered.value>self.events.value:raise InadmissibleExactValue("bounded branch recovery required")
    @property
    def recovery(self):return PositiveRatio.from_pair(self.recovered.value,self.events.value)

def branch_partition(rows):
    if not rows or len({row.channel for row in rows})!=len(rows):raise InadmissibleExactValue("complete distinct branch vector required")
    total=sum(row.events.value for row in rows)
    return tuple(PositiveRatio.from_pair(row.events.value,total) for row in rows)

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-COMBINATORICS-001","SFT-PHYS-DECAY-WIDTH-BRANCHING-LIFETIME-TERMINAL-006","SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002","SFT-CHEM-ACTIVITY-AMOUNT-TIME-003")
DIMENSIONS=(dimension("channel","unlabelled-yield","Yield needs channel identity.","held-decay-channel","Channel remains held."),dimension("daughter","anonymous-product-amount","Product amount loses species.","held-daughter-chemical-species","Daughter species remains."),dimension("events","continuum-branch-probability","Probability hides event support.","positive-counted-branch-events","Branch events are counted."),dimension("recovery","fitted-chemical-recovery","A fitted factor is not custody.","positive-counted-recovered-events","Recovered events are counted."),dimension("yield","percentage-premise","A percentage is a display form.","exact-recovered-per-branch-ratio","Yield is an exact ratio."),dimension("partition","independent-branch-fractions","Independent values need not close.","complete-branch-partition-sums-to-One","All branch shares partition One."),dimension("record","selected-favorable-daughter","Selection hides adverse/absent branches.","complete-daughter-yield-vector","Every branch and recovery remains."),dimension("extension","renormalize-after-omission","Renormalization hides missing branches.","new-branch-repartitions-complete-total","Successors retain all prior branches."))
EXACT_RESULT="held-decay-channel__held-daughter-chemical-species__positive-counted-branch-events__positive-counted-recovered-events__exact-recovered-per-branch-ratio__complete-branch-partition-sums-to-One__complete-daughter-yield-vector__new-branch-repartitions-complete-total"
def _r(n,e,r):return BranchYield(HeldLabel("decay-channel",str(n)),HeldLabel("daughter-species",str(n)),PositiveCount(e),PositiveCount(r))
def _w():
 rows=(_r(1,3,2),_r(2,1,1));parts=branch_partition(rows)
 return (("channel","Channels held.",len({x.channel for x in rows})==2),("daughter","Daughters held.",len({x.daughter_species for x in rows})==2),("events","Events positive.",rows[0].events.value==3),("recovery","Recovery positive.",rows[0].recovered.value==2),("yield","Yield exact.",rows[0].recovery.fraction==Fraction(2,3)),("partition","Shares sum One.",sum(x.fraction for x in parts)==1),("complete","Both rows retained.",len(rows)==2),("successor","New branch repartitions.",branch_partition(rows+(_r(3,2,1),))[0].fraction==Fraction(1,2)))
OPERATIONAL_WITNESSES=_w()
