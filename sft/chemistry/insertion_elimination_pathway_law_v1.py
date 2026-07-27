"""Fold-native insertion, migratory-insertion and elimination pathway law (INORG-013)."""
from __future__ import annotations
from dataclasses import dataclass
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.physics.generated_empirical_law import LawDimension,dimension

Adjacency=tuple[HeldLabel,HeldLabel]

def _edge(left:HeldLabel,right:HeldLabel)->Adjacency:
 return (left,right) if (left.family,left.label)<=(right.family,right.label) else (right,left)

@dataclass(frozen=True)
class ExactAdjacencyTransformationTrace:
 carriers:tuple[HeldLabel,...]
 before:tuple[Adjacency,...]
 after:tuple[Adjacency,...]
 removed:tuple[Adjacency,...]
 added:tuple[Adjacency,...]
 pathway_class:HeldLabel
 composition:tuple[HeldLabel,...]
 def __post_init__(self):
  if len(set(self.carriers))!=len(self.carriers) or len(self.carriers)<2:raise InadmissibleExactValue("pathway requires complete distinct retained carrier support")
  if any(a==b for a,b in self.before+self.after):raise InadmissibleExactValue("self-adjacency is inadmissible")
  if len(set(self.before))!=len(self.before) or len(set(self.after))!=len(self.after):raise InadmissibleExactValue("adjacency support cannot duplicate an edge")
  if set(self.removed)!=set(self.before)-set(self.after) or set(self.added)!=set(self.after)-set(self.before):raise InadmissibleExactValue("removed and added support must be the complete exact adjacency difference")
  if any(cell not in self.carriers for edge in self.before+self.after for cell in edge):raise InadmissibleExactValue("an adjacency loses a retained carrier")
  if self.pathway_class.family!="organometallic-pathway" or not self.composition:raise InadmissibleExactValue("pathway class and composition must remain held")

def insertion(x:str,z:str,y:str)->ExactAdjacencyTransformationTrace:
 X=HeldLabel("carrier",x);Z=HeldLabel("carrier",z);Y=HeldLabel("carrier",y);before=(_edge(X,Z),);after=(_edge(X,Y),_edge(Y,Z))
 return ExactAdjacencyTransformationTrace((X,Z,Y),before,after,before,after,HeldLabel("organometallic-pathway","insertion"),(HeldLabel("process-component","insertion"),))

def extrusion(trace:ExactAdjacencyTransformationTrace)->ExactAdjacencyTransformationTrace:
 if trace.pathway_class.label!="insertion":raise InadmissibleExactValue("extrusion requires one exact insertion trace")
 return ExactAdjacencyTransformationTrace(trace.carriers,trace.after,trace.before,trace.added,trace.removed,HeldLabel("organometallic-pathway","extrusion"),(HeldLabel("process-component","reverse-insertion"),))

def migratory_insertion(metal:str,migrant:str,inserted:str)->ExactAdjacencyTransformationTrace:
 M=HeldLabel("metal-occurrence",metal);X=HeldLabel("carrier",migrant);Y=HeldLabel("carrier",inserted);before=(_edge(M,X),_edge(M,Y));after=(_edge(M,Y),_edge(X,Y))
 return ExactAdjacencyTransformationTrace((M,X,Y),before,after,(_edge(M,X),),(_edge(X,Y),),HeldLabel("organometallic-pathway","migratory-insertion"),(HeldLabel("process-component","migration"),HeldLabel("process-component","insertion")))

def elimination(centre_left:str,centre_right:str,eliminand_left:str,eliminand_right:str)->ExactAdjacencyTransformationTrace:
 A=HeldLabel("reaction-centre",centre_left);B=HeldLabel("reaction-centre",centre_right);X=HeldLabel("eliminand",eliminand_left);Y=HeldLabel("eliminand",eliminand_right)
 carriers=tuple(dict.fromkeys((A,B,X,Y))); before=tuple(dict.fromkeys((_edge(A,X),_edge(B,Y)))); added=(_edge(A,B),) if A!=B else (_edge(X,Y),); after=added
 return ExactAdjacencyTransformationTrace(carriers,before,after,before,added,HeldLabel("organometallic-pathway","elimination"),(HeldLabel("process-component","two-eliminand-loss"),HeldLabel("product-class","new-unsaturation-ring-or-carbene-boundary")))

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001","SFT-MATH-DISCRETE-001","SFT-MATH-COMBINATORICS-001","SFT-MATH-GRAPH-NETWORK-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-COMP-FORM-STATE-TRANSITION-001","SFT-CHEM-STOICH-CONSERVATION-001","SFT-CHEM-BOND-CHEMICAL-BOND-001","SFT-CHEM-RXN-IDENTITY-001","SFT-CHEM-RXN-MECHANISM-001","SFT-CHEM-ORGANOMETALLIC-METAL-CARBON-BOND-010","SFT-CHEM-OXIDATIVE-ADDITION-REDUCTIVE-ELIMINATION-012")
DIMENSIONS:tuple[LawDimension,...]=(
 dimension("carrier","anonymous-products","Anonymous products lose occurrence identity.","complete-retained-carrier-support","Every source and product carrier remains explicit."),
 dimension("trace","endpoint-only-reaction","Endpoints alone do not certify the transformation.","complete-before-after-adjacency-difference","Every before, after, removed and added edge is retained."),
 dimension("insertion","imported-product-formula","A product formula can hide adjacency.","xz-plus-y-to-x-y-z-adjacency-law","Insertion replaces X-Z by X-Y and Y-Z."),
 dimension("migration","named-migratory-step","A name does not force composition.","migration-plus-insertion-composition","Migratory insertion retains the migration and insertion components."),
 dimension("reverse","insertion-elimination-conflation","Conflating reverse classes loses the exact boundary.","extrusion-exact-insertion-inverse","Extrusion, not generic elimination, exactly reverses insertion."),
 dimension("elimination","selected-leaving-group","Selection loses one eliminand or centre.","complete-two-eliminand-centre-trace","Elimination retains both eliminands, centres and new product adjacency."),
 dimension("product","imported-unsaturation-name","A conventional name is not a generated adjacency.","held-unsaturation-ring-or-carbene-boundary","Product class remains held while adjacency is exact."),
 dimension("extension","mechanism-specific-exception","An exception destroys closure.","adjacency-trace-composition-no-extra-rule","Matching traces compose without changing prior edges."),
)
def _witnesses():
 ins=insertion("X","Z","Y");rev=extrusion(ins);mig=migratory_insertion("M","X","Y");elim=elimination("A","B","X","Y");same=elimination("A","A","X","Y")
 return (("insertion","Insertion removes one edge and adds two.",len(ins.removed)==1 and len(ins.added)==2),("exact-extrusion","Extrusion restores the exact source adjacency.",rev.after==ins.before),("migratory-composition","Migratory insertion retains migration plus insertion.",tuple(x.label for x in mig.composition)==("migration","insertion")),("elimination-boundaries","Distinct- and single-centre eliminations retain exact traces.",len(elim.removed)==2 and len(same.carriers)==3))
OPERATIONAL_WITNESSES=_witnesses()
EXACT_RESULT="complete-retained-carrier-support__complete-before-after-adjacency-difference__xz-plus-y-to-x-y-z-adjacency-law__migration-plus-insertion-composition__extrusion-exact-insertion-inverse__complete-two-eliminand-centre-trace__held-unsaturation-ring-or-carbene-boundary__adjacency-trace-composition-no-extra-rule"
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","OPERATIONAL_WITNESSES","ExactAdjacencyTransformationTrace","elimination","extrusion","insertion","migratory_insertion")
