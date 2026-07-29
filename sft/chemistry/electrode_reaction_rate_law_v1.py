"""Fold-native electrode reaction-rate law (ECHEM-009)."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension

@dataclass(frozen=True)
class ElectrodeEventLedger:
    reaction: HeldLabel; interface: HeldLabel; condition: HeldLabel; potential_orientation: HeldLabel
    forward_events: PositiveCount; reverse_events: PositiveCount; resource_intervals: PositiveCount
    def __post_init__(self):
        if (self.reaction.family,self.interface.family,self.condition.family,self.potential_orientation.family)!=("electrode-reaction","electrode-interface","electrochemical-condition","potential-orientation"): raise InadmissibleExactValue("reaction/interface/condition/potential custody required")
        if not all(isinstance(x,PositiveCount) for x in (self.forward_events,self.reverse_events,self.resource_intervals)): raise InadmissibleExactValue("rate ledger uses positive exact counts")

@dataclass(frozen=True)
class ElectrodeRate:
    direction: HeldLabel; net_event_rate: PositiveRatio|EmptyOne; complete_event_rate: PositiveRatio; ledger: ElectrodeEventLedger

def electrode_rate(row):
    f,r,t=row.forward_events.value,row.reverse_events.value,row.resource_intervals.value
    if f==r: direction,net="balanced",EMPTY_ONE
    elif f>r: direction,net="forward",PositiveRatio.from_pair(f-r,t)
    else: direction,net="reverse",PositiveRatio.from_pair(r-f,t)
    return ElectrodeRate(HeldLabel("reaction-rate-direction",direction),net,PositiveRatio.from_pair(f+r,t),row)

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-ORDER-LATTICE-001","SFT-COMP-CPLX-TIME-SPACE-001","SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001","SFT-CHEM-ELECTROCHEMICAL-WORK-REACTION-DIRECTION-005","SFT-CHEM-IONIC-MOBILITY-TRANSFERENCE-008")
DIMENSIONS=(
 dimension("reaction","anonymous-current","Current alone loses reaction identity.","complete-reaction-interface-custody","Reaction and interface remain held."),
 dimension("events","continuum-current-premise","Continuum flow hides event support.","positive-counted-forward-reverse-events","Both event directions are counted."),
 dimension("resource","unbounded-rate","Rate without resource is undefined.","exact-events-per-counted-resource","Rate is an exact positive ratio."),
 dimension("potential","signed-overpotential-premise","Signed potential imports negative magnitude.","held-potential-orientation","Potential direction is held separately."),
 dimension("net","subtracted-negative-rate","Signed subtraction can produce negative proof values.","positive-Take-with-held-rate-direction","Net events use positive Take and held direction."),
 dimension("balance","numerical-zero-net-current","Numerical zero is not a native magnitude.","structural-EmptyOne-balanced-events","Equal event counts close net distinction."),
 dimension("record","selected-current-point","One point hides the curve and conditions.","complete-current-potential-condition-vector","Every registered current/potential/condition row remains downstream."),
 dimension("extension","fitted-exchange-current-exponential","A fit imports answer-producing parameters.","event-successor-recomputes-exact-rate","Successors extend the ledger without refitting."))
EXACT_RESULT="complete-reaction-interface-custody__positive-counted-forward-reverse-events__exact-events-per-counted-resource__held-potential-orientation__positive-Take-with-held-rate-direction__structural-EmptyOne-balanced-events__complete-current-potential-condition-vector__event-successor-recomputes-exact-rate"
def _w():
 def x(f,r):return electrode_rate(ElectrodeEventLedger(HeldLabel("electrode-reaction","r"),HeldLabel("electrode-interface","i"),HeldLabel("electrochemical-condition","c"),HeldLabel("potential-orientation","held"),PositiveCount(f),PositiveCount(r),PositiveCount(2)))
 a,b,c=x(5,1),x(1,5),x(3,3)
 return (("forward","Forward excess is held.",a.direction.label=="forward"),("reverse","Reverse excess is held.",b.direction.label=="reverse"),("take","Net magnitude is positive Take.",a.net_event_rate.fraction==2),("balance","Equal counts close to EmptyOne.",c.net_event_rate==EMPTY_ONE),("complete","Complete activity retains both directions.",a.complete_event_rate.fraction==3),("reaction","Reaction remains held.",a.ledger.reaction.label=="r"),("condition","Condition remains held.",a.ledger.condition.label=="c"),("no-fit","Successor rate is recomputed from counts.",x(6,1).net_event_rate.fraction==Fraction(5,2)))
OPERATIONAL_WITNESSES=_w()
