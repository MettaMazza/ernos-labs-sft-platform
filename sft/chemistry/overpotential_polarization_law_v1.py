"""Fold-native overpotential and polarization law (ECHEM-010)."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension

@dataclass(frozen=True)
class PolarizationPoint:
    electrode: HeldLabel; reference: HeldLabel; condition: HeldLabel; scan_ordinal: PositiveCount
    potential_side: HeldLabel; potential_distance: PositiveRatio|EmptyOne; current_direction: HeldLabel; current_magnitude: PositiveRatio|EmptyOne
    def __post_init__(self):
        if (self.electrode.family,self.reference.family,self.condition.family,self.potential_side.family,self.current_direction.family)!=("electrode","equilibrium-reference","electrochemical-condition","potential-side","current-direction"): raise InadmissibleExactValue("complete polarization custody required")
        if self.potential_side.label=="equilibrium" and (self.potential_distance!=EMPTY_ONE or self.current_magnitude!=EMPTY_ONE): raise InadmissibleExactValue("equilibrium point closes potential and net current")
        if self.potential_side.label!="equilibrium" and not all(isinstance(x,PositiveRatio) for x in (self.potential_distance,self.current_magnitude)): raise InadmissibleExactValue("polarized points require positive magnitudes")

def polarization_curve(points):
    if not points or tuple(p.scan_ordinal.value for p in points)!=tuple(range(1,len(points)+1)): raise InadmissibleExactValue("complete ordered finite scan required")
    first=points[0]
    if any((p.electrode,p.reference,p.condition)!=(first.electrode,first.reference,first.condition) for p in points): raise InadmissibleExactValue("mixed polarization support")
    return points

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-ORDER-LATTICE-001","SFT-CHEM-ELECTRODE-POTENTIAL-CHEMICAL-RELATION-002","SFT-CHEM-ELECTRODE-REACTION-RATE-009")
DIMENSIONS=(dimension("reference","reference-free-voltage","Overpotential needs equilibrium reference.","one-held-equilibrium-reference","Every point retains its equilibrium reference."),dimension("orientation","signed-potential-offset","A sign imports negative magnitude.","held-anodic-cathodic-equilibrium-side","Potential side is held separately."),dimension("magnitude","continuum-difference-premise","A continuum difference is not an exact proof.","exact-positive-potential-distance","Distance is exact positive Take."),dimension("current","anonymous-current","Current loses reaction direction.","held-current-direction-positive-magnitude","Current direction and magnitude remain separate."),dimension("equilibrium","numerical-zero-origin","Numerical zero is not native equilibrium.","structural-EmptyOne-equilibrium-point","Coincidence closes potential and net current."),dimension("curve","selected-polarization-point","One point hides response organization.","complete-ordered-finite-polarization-curve","Every scan point and reversal is retained."),dimension("condition","mixed-condition-curve","Mixed conditions are incomparable.","common-electrode-reference-condition","Curve support remains common."),dimension("record","fitted-tafel-line","A fitted line can hide deviations.","complete-raw-potential-current-vector","Raw values, breaks, hysteresis and anomalies remain downstream."))
EXACT_RESULT="one-held-equilibrium-reference__held-anodic-cathodic-equilibrium-side__exact-positive-potential-distance__held-current-direction-positive-magnitude__structural-EmptyOne-equilibrium-point__complete-ordered-finite-polarization-curve__common-electrode-reference-condition__complete-raw-potential-current-vector"
def _p(n,side="anodic"):
 e=side=="equilibrium";return PolarizationPoint(HeldLabel("electrode","e"),HeldLabel("equilibrium-reference","r"),HeldLabel("electrochemical-condition","c"),PositiveCount(n),HeldLabel("potential-side",side),EMPTY_ONE if e else PositiveRatio.from_pair(n,2),HeldLabel("current-direction","balanced" if e else side),EMPTY_ONE if e else PositiveRatio.from_pair(n,3))
def _w():
 c=polarization_curve((_p(1,"equilibrium"),_p(2),_p(3,"cathodic")))
 bad=False
 try:polarization_curve((_p(1),_p(3)))
 except InadmissibleExactValue:bad=True
 return (("ordered","All scan points retained.",len(c)==3),("reference","Reference retained.",c[0].reference.label=="r"),("equilibrium","Equilibrium is EmptyOne.",c[0].potential_distance==EMPTY_ONE),("anodic","Anodic side held.",c[1].potential_side.label=="anodic"),("cathodic","Cathodic side held.",c[2].potential_side.label=="cathodic"),("positive","Magnitudes positive.",isinstance(c[1].current_magnitude,PositiveRatio)),("condition","Condition common.",len({p.condition for p in c})==1),("omission","Missing ordinal halts.",bad))
OPERATIONAL_WITNESSES=_w()
