"""Fold-native electronic-state equivalence, degeneracy and symmetry law."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Union
from sft.claim_evidence.fold_language import EMPTY_ONE,EmptyOne
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.physics.generated_empirical_law import LawDimension,dimension
AxisRank=Union[EmptyOne,PositiveCount]

@dataclass(frozen=True)
class StateSymmetrySignature:
 molecular_carrier:HeldLabel
 positive_spin_multiplicity:PositiveCount
 axis_rank:AxisRank
 positive_axis_orientation_count:PositiveCount
 inversion_label:Union[EmptyOne,HeldLabel]
 reflection_label:Union[EmptyOne,HeldLabel]
 axis_component:Union[EmptyOne,HeldLabel]
 component_kind:Union[EmptyOne,HeldLabel]
 def __post_init__(self):
  if self.molecular_carrier.family!="molecular-carrier":raise InadmissibleExactValue("symmetry signature requires one molecule")
  if self.axis_rank==EMPTY_ONE and self.positive_axis_orientation_count.value!=1:raise InadmissibleExactValue("axis-invariant support has one retained orientation")
  if isinstance(self.axis_rank,PositiveCount) and self.positive_axis_orientation_count.value!=2:raise InadmissibleExactValue("positive axis recurrence has the complementary orientation pair")
  for value,family in ((self.inversion_label,"inversion-symmetry"),(self.reflection_label,"reflection-symmetry"),(self.axis_component,"axis-component"),(self.component_kind,"component-kind")):
   if isinstance(value,HeldLabel) and value.family!=family:raise InadmissibleExactValue("held symmetry label has the wrong family")
 @property
 def positive_degeneracy_count(self)->PositiveCount:return PositiveCount(self.positive_spin_multiplicity.value*self.positive_axis_orientation_count.value)

@dataclass(frozen=True)
class FiniteStateEquivalenceClass:
 signature:StateSymmetrySignature
 component_occurrences:tuple[HeldLabel,...]
 def __post_init__(self):
  if len(self.component_occurrences)!=self.signature.positive_degeneracy_count.value:raise InadmissibleExactValue("equivalence-class support must equal the forced positive degeneracy count")
  if len(set(self.component_occurrences))!=len(self.component_occurrences) or any(x.family!="state-component" for x in self.component_occurrences):raise InadmissibleExactValue("state components must be unique retained occurrences")

def build_equivalence_class(signature:StateSymmetrySignature)->FiniteStateEquivalenceClass:
 return FiniteStateEquivalenceClass(signature,tuple(HeldLabel("state-component",f"component-{i}") for i in range(1,signature.positive_degeneracy_count.value+1)))

def equivalent(left:StateSymmetrySignature,right:StateSymmetrySignature)->bool:return left==right

def axis_rank_from_source_symbol(symbol:str)->AxisRank:
 if symbol=="Σ":return EMPTY_ONE
 mapping={"Π":1,"Δ":2,"Φ":3}
 if symbol not in mapping:raise InadmissibleExactValue("source term symbol is outside the declared comparison grammar")
 return PositiveCount(mapping[symbol])

def symmetry_signature_from_source(molecule:str,multiplicity:PositiveCount,symbol:str,inversion:str,reflection:str,component:str,kind:str)->StateSymmetrySignature:
 axis=axis_rank_from_source_symbol(symbol)
 def held(family,label):return EMPTY_ONE if label=="absence" else HeldLabel(family,label)
 return StateSymmetrySignature(HeldLabel("molecular-carrier",molecule),multiplicity,axis,PositiveCount(1 if axis==EMPTY_ONE else 2),held("inversion-symmetry",inversion),held("reflection-symmetry",reflection),held("axis-component",component),held("component-kind",kind))

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-ORDER-LATTICE-001","SFT-MATH-COMBINATORICS-001","SFT-MATH-LOGIC-PROOF-001","SFT-INFO-SYMBOL-DISTINCTION-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-PHYS-QUANTUM-SPIN-001","SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001","SFT-PHYS-QUANTUM-EXCLUSION-001","SFT-CHEM-ELECTRON-COUNT-SPIN-002","SFT-CHEM-ORBITAL-SUPPORT-OCCUPANCY-003","SFT-CHEM-STATE-ENERGY-ORDER-004")
DIMENSIONS:tuple[LawDimension,...]=(
 dimension("carrier","cross-carrier-equivalence","States on different molecules cannot share one declared chemical equivalence class.","one-molecule-equivalence","Every equivalence comparison retains one molecular carrier."),
 dimension("identity","energy-only-equivalence","Equal or nearby energy alone erases support and symmetry distinctions.","complete-symmetry-signature","Equivalence requires equality of every retained state/symmetry coordinate."),
 dimension("spin","unsigned-or-absent-multiplicity","Erasing positive spin width loses generated component support.","positive-spin-multiplicity","Spin multiplicity remains a positive generated count from held-spin organization."),
 dimension("axis","continuum-or-zero-projection","A continuum coordinate or numerical zero violates the generated axis grammar.","empty-One-or-positive-axis-rank","Axis invariance is structural EmptyOne and every non-invariant class a positive recurrence."),
 dimension("orientation","free-degeneracy-number","An asserted degeneracy count is an unforced parameter.","one-or-complementary-orientation-support","Axis invariance retains one orientation; positive axis rank forces the complementary orientation pair."),
 dimension("symmetry","erased-sign-labels","Erasing inversion, reflection and component labels merges distinguishable terms.","held-symmetry-label-composition","Every applicable symmetry distinction remains a held label; absence remains EmptyOne."),
 dimension("class","unbounded-anonymous-members","Anonymous or unbounded members cannot certify degeneracy.","complete-positive-component-class","The equivalence class enumerates exactly spin width times axis-orientation support."),
 dimension("extension","term-table-exception","A species or term lookup lets source assignments select the law.","no-extra-rule","The same finite signature and component law applies at every positive multiplicity and axis recurrence."),)

def _witnesses():
 sigma=symmetry_signature_from_source("H2",PositiveCount(1),"Σ","g","plus-fibre","absence","absence");pi=symmetry_signature_from_source("NO",PositiveCount(2),"Π","absence","absence","absence","r")
 wrong_rejected=False
 try:StateSymmetrySignature(HeldLabel("molecular-carrier","bad"),PositiveCount(1),EMPTY_ONE,PositiveCount(2),EMPTY_ONE,EMPTY_ONE,EMPTY_ONE,EMPTY_ONE)
 except InadmissibleExactValue:wrong_rejected=True
 incomplete_rejected=False
 try:FiniteStateEquivalenceClass(pi,(HeldLabel("state-component","one"),))
 except InadmissibleExactValue:incomplete_rejected=True
 return (("sigma-singlet-class","Axis-invariant singlet support forces one component.",build_equivalence_class(sigma).signature.positive_degeneracy_count==PositiveCount(1)),("pi-doublet-class","First axis recurrence and spin width two force four retained components.",build_equivalence_class(pi).signature.positive_degeneracy_count==PositiveCount(4)),("signature-distinction","Changing carrier, axis or held labels changes equivalence class.",not equivalent(sigma,pi)),("orientation-control","An axis-invariant support with two orientations rejects.",wrong_rejected),("component-census-control","An incomplete degeneracy class rejects.",incomplete_rejected))
OPERATIONAL_WITNESSES=_witnesses()
EXACT_RESULT="one-molecule-equivalence__complete-symmetry-signature__positive-spin-multiplicity__empty-One-or-positive-axis-rank__one-or-complementary-orientation-support__held-symmetry-label-composition__complete-positive-component-class__no-extra-rule"
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","FiniteStateEquivalenceClass","OPERATIONAL_WITNESSES","StateSymmetrySignature","axis_rank_from_source_symbol","build_equivalence_class","equivalent","symmetry_signature_from_source")
