"""Fold-native double-layer and interfacial charge organization (ECHEM-011)."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from sft.claim_evidence import EMPTY_ONE, EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension

@dataclass(frozen=True)
class InterfaceLayer:
    interface: HeldLabel; electrolyte: HeldLabel; side: HeldLabel; spatial_rank: PositiveCount
    carrier_identity: HeldLabel; carrier_count: PositiveCount
    def __post_init__(self):
        if (self.interface.family,self.electrolyte.family,self.side.family,self.carrier_identity.family)!=("electrode-interface","electrolyte-composition","interface-side","charge-carrier"): raise InadmissibleExactValue("interface layer custody required")

@dataclass(frozen=True)
class DoubleLayerResult:
    layers: tuple; potential_separation: PositiveRatio|EmptyOne; capacitance: PositiveRatio|EmptyOne

def double_layer(layers,potential):
    if not layers or tuple(x.spatial_rank.value for x in layers)!=tuple(range(1,len(layers)+1)): raise InadmissibleExactValue("complete finite ordered interface support required")
    if len({x.interface for x in layers})!=1 or len({x.electrolyte for x in layers})!=1: raise InadmissibleExactValue("mixed interface")
    if potential==EMPTY_ONE:return DoubleLayerResult(layers,EMPTY_ONE,EMPTY_ONE)
    if not isinstance(potential,PositiveRatio):raise InadmissibleExactValue("positive potential separation required")
    return DoubleLayerResult(layers,potential,PositiveRatio.from_pair(sum(x.carrier_count.value for x in layers)*potential.denominator.value,potential.numerator.value))

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-COMBINATORICS-001","SFT-CHEM-IONIC-CONDUCTIVITY-RELATION-007","SFT-CHEM-OVERPOTENTIAL-POLARIZATION-010")
DIMENSIONS=(dimension("interface","bulk-charge-number","Bulk charge loses interface identity.","one-held-electrode-electrolyte-interface","One interface remains held."),dimension("support","continuum-profile-premise","Continuum profile is not finite proof support.","complete-finite-ordered-interface-layers","Every generated layer is retained."),dimension("carrier","anonymous-charge-density","Anonymous density loses carrier identity.","held-species-resolved-charge-carriers","Every carrier and side remains held."),dimension("orientation","signed-interfacial-charge","A sign imports negative magnitude.","held-opposed-interface-sides","Charge orientation is structural."),dimension("potential","unreferenced-potential","Potential needs interfacial separation.","exact-positive-interface-potential-separation","Potential magnitude remains positive."),dimension("capacitance","fitted-capacitance-parameter","A fit does not derive charge custody.","exact-carrier-per-potential-ratio","Capacitance is exact counted carrier support per separation."),dimension("coincidence","numerical-zero-charge-state","Numerical zero is not native.","structural-EmptyOne-interface-coincidence","No separation closes the response structurally."),dimension("record","selected-capacitance-point","One point hides spatial and composition response.","complete-interface-potential-capacitance-vector","All registered spatial/potential/composition rows remain downstream."))
EXACT_RESULT="one-held-electrode-electrolyte-interface__complete-finite-ordered-interface-layers__held-species-resolved-charge-carriers__held-opposed-interface-sides__exact-positive-interface-potential-separation__exact-carrier-per-potential-ratio__structural-EmptyOne-interface-coincidence__complete-interface-potential-capacitance-vector"
def _l(n,side):return InterfaceLayer(HeldLabel("electrode-interface","i"),HeldLabel("electrolyte-composition","e"),HeldLabel("interface-side",side),PositiveCount(n),HeldLabel("charge-carrier",side),PositiveCount(n))
def _w():
 r=double_layer((_l(1,"electrode"),_l(2,"solution")),PositiveRatio.from_pair(3,2));z=double_layer((_l(1,"electrode"),),EMPTY_ONE)
 return (("layers","Two layers retained.",len(r.layers)==2),("order","Spatial ranks retained.",tuple(x.spatial_rank.value for x in r.layers)==(1,2)),("species","Carrier identities retained.",len({x.carrier_identity for x in r.layers})==2),("sides","Opposed sides retained.",len({x.side for x in r.layers})==2),("potential","Potential positive.",r.potential_separation.fraction==Fraction(3,2)),("capacitance","Carrier/potential exact.",r.capacitance.fraction==2),("coincidence","Coincidence closes.",z.capacitance==EMPTY_ONE),("interface","Interface common.",len({x.interface for x in r.layers})==1))
OPERATIONAL_WITNESSES=_w()
