"""Fold-native coupled corrosion reaction-network law (ECHEM-012)."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension

@dataclass(frozen=True)
class CorrosionPath:
    material: HeldLabel; environment: HeldLabel; reaction: HeldLabel; direction: HeldLabel
    events: PositiveCount; resource_intervals: PositiveCount
    def __post_init__(self):
        if (self.material.family,self.environment.family,self.reaction.family,self.direction.family)!=("material","chemical-environment","corrosion-reaction","corrosion-direction"):raise InadmissibleExactValue("complete corrosion path custody required")
    @property
    def rate(self):return Fraction(self.events.value,self.resource_intervals.value)

@dataclass(frozen=True)
class CorrosionNetwork:
    anodic: CorrosionPath; cathodic: CorrosionPath; synchronized_rate: PositiveRatio; excess_orientation: HeldLabel; excess_rate: PositiveRatio|EmptyOne

def corrosion_network(anodic,cathodic):
    if (anodic.material,anodic.environment)!=(cathodic.material,cathodic.environment) or anodic.direction.label!="anodic" or cathodic.direction.label!="cathodic":raise InadmissibleExactValue("coupled anodic/cathodic paths required")
    a,c=anodic.rate,cathodic.rate;sync=min(a,c)
    if a==c:side,excess="balanced",EMPTY_ONE
    elif a>c:side,excess="anodic-excess",PositiveRatio.from_pair((a-c).numerator,(a-c).denominator)
    else:side,excess="cathodic-excess",PositiveRatio.from_pair((c-a).numerator,(c-a).denominator)
    return CorrosionNetwork(anodic,cathodic,PositiveRatio.from_pair(sync.numerator,sync.denominator),HeldLabel("corrosion-excess-orientation",side),excess)

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-GRAPH-NETWORK-001","SFT-CHEM-REDOX-COUPLING-001","SFT-CHEM-ELECTRODE-REACTION-RATE-009","SFT-CHEM-OVERPOTENTIAL-POLARIZATION-010")
DIMENSIONS=(dimension("material","material-free-rate","A rate without material is not corrosion identity.","held-material-environment-custody","Material and environment remain held."),dimension("network","single-reaction-answer","Corrosion requires coupled reactions.","complete-anodic-cathodic-network","Both paths remain explicit."),dimension("events","continuum-loss-rate","A continuum rate hides events.","positive-counted-path-events","Every reaction event is counted."),dimension("resource","unbounded-corrosion-rate","Rate needs resource support.","exact-events-per-resource-ratio","Each path rate is exact."),dimension("coupling","independent-fitted-rates","Independent fits need not conserve current.","exact-synchronized-path-rate","Coupled rate is the exact shared support."),dimension("orientation","signed-net-current","A sign imports negative magnitude.","held-excess-path-orientation","Any excess is held with positive magnitude."),dimension("balance","numerical-zero-corrosion-current","Numerical zero is not native balance.","structural-EmptyOne-balanced-excess","Balanced paths close excess structurally."),dimension("record","selected-corrosion-rate","One rate hides potential, mass loss and adverse rows.","complete-potential-current-rate-mass-loss-vector","Every registered corrosion record remains downstream."))
EXACT_RESULT="held-material-environment-custody__complete-anodic-cathodic-network__positive-counted-path-events__exact-events-per-resource-ratio__exact-synchronized-path-rate__held-excess-path-orientation__structural-EmptyOne-balanced-excess__complete-potential-current-rate-mass-loss-vector"
def _p(direction,n):return CorrosionPath(HeldLabel("material","iron"),HeldLabel("chemical-environment","salt-water"),HeldLabel("corrosion-reaction",direction),HeldLabel("corrosion-direction",direction),PositiveCount(n),PositiveCount(2))
def _w():
 b=corrosion_network(_p("anodic",4),_p("cathodic",4));a=corrosion_network(_p("anodic",6),_p("cathodic",4))
 return (("paths","Both paths retained.",b.anodic.direction!=b.cathodic.direction),("material","Material retained.",b.anodic.material.label=="iron"),("environment","Environment retained.",b.anodic.environment.label=="salt-water"),("rate","Synchronized rate exact.",b.synchronized_rate.fraction==2),("balance","Balanced excess EmptyOne.",b.excess_rate==EMPTY_ONE),("orientation","Anodic excess held.",a.excess_orientation.label=="anodic-excess"),("positive","Excess magnitude positive.",a.excess_rate.fraction==1),("network","Reaction identities retained.",len({b.anodic.reaction,b.cathodic.reaction})==2))
OPERATIONAL_WITNESSES=_w()
