"""Fold-native solid-state formula and local-coordination law (INORG-015)."""
from __future__ import annotations
from dataclasses import dataclass
from math import gcd
from functools import reduce
from sft.claim_evidence.fold_language import EMPTY_ONE,EmptyOne
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.physics.generated_empirical_law import LawDimension,dimension
@dataclass(frozen=True)
class FormulaEntry:
 species:HeldLabel;primitive_count:PositiveCount
 def __post_init__(self):
  if self.species.family!="chemical-species":raise InadmissibleExactValue("formula entry requires a retained chemical species")
@dataclass(frozen=True)
class ExactSolidStateLocalChemistry:
 motif:HeldLabel;occurrences:tuple[HeldLabel,...];local_bonds:tuple[tuple[HeldLabel,HeldLabel],...];formula:tuple[FormulaEntry,...];repeat_axes:tuple[HeldLabel,...];constituent_support:object;chemistry_scope:HeldLabel;bulk_handoff:HeldLabel
 def __post_init__(self):
  if self.motif.family!="local-solid-motif" or not self.occurrences or len(set(self.occurrences))!=len(self.occurrences):raise InadmissibleExactValue("local solid chemistry requires one positive complete occurrence motif")
  if any(x.family!="species-occurrence" for x in self.occurrences):raise InadmissibleExactValue("motif occurrence is not a species occurrence")
  if not self.formula or self.formula!=primitive_formula(self.occurrences):raise InadmissibleExactValue("formula must be the exact primitive positive occurrence ratio")
  if not 1<=len(self.repeat_axes)<=3 or any(x.family!="generated-repeat-axis" for x in self.repeat_axes) or len(set(self.repeat_axes))!=len(self.repeat_axes):raise InadmissibleExactValue("repeat support has exact generated rank one, two or three")
  if len(set(self.local_bonds))!=len(self.local_bonds) or any(a not in self.occurrences or b not in self.occurrences or a==b for a,b in self.local_bonds):raise InadmissibleExactValue("local bond support is incomplete or invalid")
  if not isinstance(self.constituent_support,EmptyOne) and (not self.constituent_support or any(x.family!="second-constituent-occurrence" for x in self.constituent_support)):raise InadmissibleExactValue("second constituent support must be positive or structural EmptyOne")
  if self.chemistry_scope!=HeldLabel("ownership","composition-and-local-bonding") or self.bulk_handoff!=HeldLabel("ownership-handoff","materials-bulk-response"):
   raise InadmissibleExactValue("Chemistry/Materials ownership boundary changed")
def primitive_formula(occurrences:tuple[HeldLabel,...])->tuple[FormulaEntry,...]:
 labels=tuple(dict.fromkeys(x.label.split("#",1)[0] for x in occurrences));counts=tuple(sum(x.label.split("#",1)[0]==label for x in occurrences) for label in labels);divisor=reduce(gcd,counts);return tuple(FormulaEntry(HeldLabel("chemical-species",label),PositiveCount(count//divisor)) for label,count in zip(labels,counts))
def occurrence(species:str,index:PositiveCount)->HeldLabel:return HeldLabel("species-occurrence",f"{species}#{index.value}")
def local_solid(motif:str,species_counts:tuple[tuple[str,PositiveCount],...],bonds:tuple[tuple[tuple[str,int],tuple[str,int]],...],rank:PositiveCount,second_constituent_count:object=EMPTY_ONE)->ExactSolidStateLocalChemistry:
 if rank.value>3:raise InadmissibleExactValue("local repeat rank cannot exceed generator-three support")
 occ=tuple(occurrence(s,PositiveCount(i)) for s,n in species_counts for i in range(1,n.value+1));lookup={(x.label.split("#")[0],int(x.label.split("#")[1])):x for x in occ};edges=tuple((lookup[a],lookup[b]) for a,b in bonds);const=EMPTY_ONE if isinstance(second_constituent_count,EmptyOne) else tuple(HeldLabel("second-constituent-occurrence",f"guest-{i}") for i in range(1,second_constituent_count.value+1));return ExactSolidStateLocalChemistry(HeldLabel("local-solid-motif",motif),occ,edges,primitive_formula(occ),tuple(HeldLabel("generated-repeat-axis",f"axis-{i}") for i in range(1,rank.value+1)),const,HeldLabel("ownership","composition-and-local-bonding"),HeldLabel("ownership-handoff","materials-bulk-response"))
def append_occurrence(state:ExactSolidStateLocalChemistry,species:str,bond_to:HeldLabel)->ExactSolidStateLocalChemistry:
 existing=sum(x.label.split("#",1)[0]==species for x in state.occurrences);new=occurrence(species,PositiveCount(existing+1));occ=state.occurrences+(new,);return ExactSolidStateLocalChemistry(state.motif,occ,state.local_bonds+((bond_to,new),),primitive_formula(occ),state.repeat_axes,state.constituent_support,state.chemistry_scope,state.bulk_handoff)
DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-COMBINATORICS-001","SFT-MATH-GRAPH-NETWORK-001","SFT-MATH-GEOMETRY-TOPOLOGY-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-PHYS-STRUCT-GENERATOR-THREE-001","SFT-PHYS-SPACE-DIMENSION-THREE-001","SFT-CHEM-STOICH-COMPOSITION-001","SFT-CHEM-BOND-CHEMICAL-BOND-001","SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001","SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004","SFT-CHEM-METAL-CLUSTER-BONDING-014")
DIMENSIONS:tuple[LawDimension,...]=(dimension("carrier","bulk-material-response","Bulk response is outside Chemistry ownership.","one-finite-local-chemical-motif","Chemistry retains one finite local motif."),dimension("composition","nominal-formula-label","A label can omit occurrences.","complete-species-occurrence-multiset","Every local species occurrence is retained."),dimension("formula","unreduced-or-fitted-stoichiometry","Unreduced or fitted coefficients are not unique.","exact-primitive-positive-count-ratio","The unique formula is the primitive positive count vector."),dimension("bonds","averaged-coordination-number","An average loses local adjacency.","complete-local-bond-adjacency-support","Every local bond incidence remains explicit."),dimension("network","continuum-infinite-lattice","A continuum lattice imports infinity.","generated-repeat-axis-rank-one-two-or-three","Repeat support has exact finite generated rank."),dimension("constituent","real-valued-solid-solution-fraction","A real fraction imports continuum fitting.","positive-second-constituent-support-or-EmptyOne","A second constituent has exact occurrences or structural absence."),dimension("ownership","chemistry-claims-bulk-response","Bulk response belongs to Materials.","chemistry-local-materials-bulk-handoff","Composition/local bonding and bulk response have one explicit owner each."),dimension("extension","crystal-family-exception","A catalogue exception destroys closure.","local-occurrence-successor-no-extra-rule","A fresh occurrence and bond update formula exactly."))
def _w():
 s=local_solid("AB",(("A",PositiveCount(2)),("B",PositiveCount(2))),((("A",1),("B",1)),(("A",2),("B",2))),PositiveCount(2));guest=local_solid("host",(("H",PositiveCount(2)),("G",PositiveCount(1))),((("H",1),("G",1)),),PositiveCount(3),PositiveCount(1));succ=append_occurrence(s,"A",s.occurrences[1]);bad=False
 try:local_solid("bad",(("A",PositiveCount(1)),),(),PositiveCount(4))
 except InadmissibleExactValue:bad=True
 return (("primitive-formula","Two A and two B occurrences reduce exactly to one and one.",tuple(x.primitive_count.value for x in s.formula)==(1,1)),("rank-and-constituent","Rank three and one second constituent remain exact.",len(guest.repeat_axes)==3 and len(guest.constituent_support)==1),("successor","Appending A changes the primitive formula to three-to-two.",tuple(x.primitive_count.value for x in succ.formula)==(3,2)),("rank-control","Rank four rejects.",bad))
OPERATIONAL_WITNESSES=_w();EXACT_RESULT="one-finite-local-chemical-motif__complete-species-occurrence-multiset__exact-primitive-positive-count-ratio__complete-local-bond-adjacency-support__generated-repeat-axis-rank-one-two-or-three__positive-second-constituent-support-or-EmptyOne__chemistry-local-materials-bulk-handoff__local-occurrence-successor-no-extra-rule"
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","OPERATIONAL_WITNESSES","ExactSolidStateLocalChemistry","FormulaEntry","append_occurrence","local_solid","occurrence","primitive_formula")
