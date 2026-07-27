"""Fold-native metal-cluster and metal--metal bonding law (INORG-014)."""
from __future__ import annotations
from dataclasses import dataclass
from sft.claim_evidence.fold_language import EMPTY_ONE,EmptyOne
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.physics.generated_empirical_law import LawDimension,dimension
@dataclass(frozen=True)
class MetalCentreRelation:
 left:HeldLabel;right:HeldLabel;mode:HeldLabel;bridge_support:tuple[HeldLabel,...]
 def __post_init__(self):
  if self.left.family!="metal-centre" or self.right.family!="metal-centre" or self.left==self.right:raise InadmissibleExactValue("cluster relation requires two distinct metal centres")
  if self.mode.family!="cluster-relation" or self.mode.label not in {"direct-metal-bond","bridging-ligand-path","held-grouping-relation"}:raise InadmissibleExactValue("cluster relation mode is outside the complete forced set")
  if self.mode.label=="bridging-ligand-path" and (not self.bridge_support or any(x.family!="bridging-ligand-occurrence" for x in self.bridge_support)):raise InadmissibleExactValue("bridging relation requires positive complete bridge support")
  if self.mode.label!="bridging-ligand-path" and self.bridge_support:raise InadmissibleExactValue("only a bridging relation carries bridge support")
@dataclass(frozen=True)
class ExactMetalCluster:
 entity:HeldLabel;centres:tuple[HeldLabel,...];relations:tuple[MetalCentreRelation,...];centre_count:PositiveCount;direct_bond_count:object;bridge_path_count:object
 def __post_init__(self):
  if self.entity.family!="cluster-entity" or len(self.centres)<2 or len(set(self.centres))!=len(self.centres) or any(x.family!="metal-centre" for x in self.centres):raise InadmissibleExactValue("cluster requires finite complete support of at least two distinct metal centres")
  if self.centre_count.value!=len(self.centres) or not self.relations:raise InadmissibleExactValue("cluster count and positive relation support must be complete")
  if len(set((min(r.left.label,r.right.label),max(r.left.label,r.right.label),r.mode.label) for r in self.relations))!=len(self.relations):raise InadmissibleExactValue("cluster relations cannot duplicate")
  reached={self.centres[0]};changed=True
  while changed:
   changed=False
   for r in self.relations:
    if r.left in reached and r.right not in reached:reached.add(r.right);changed=True
    if r.right in reached and r.left not in reached:reached.add(r.left);changed=True
  if reached!=set(self.centres):raise InadmissibleExactValue("cluster support must be connected")
  direct=sum(r.mode.label=="direct-metal-bond" for r in self.relations);bridges=sum(r.mode.label=="bridging-ligand-path" for r in self.relations)
  expected_direct=EMPTY_ONE if direct==0 else PositiveCount(direct);expected_bridges=EMPTY_ONE if bridges==0 else PositiveCount(bridges)
  if self.direct_bond_count!=expected_direct or self.bridge_path_count!=expected_bridges:raise InadmissibleExactValue("direct and bridging counts must preserve exact support or structural EmptyOne")
def relation(left:str,right:str,mode:str,bridge_count:object=EMPTY_ONE)->MetalCentreRelation:
 n=0 if isinstance(bridge_count,EmptyOne) else bridge_count.value;return MetalCentreRelation(HeldLabel("metal-centre",left),HeldLabel("metal-centre",right),HeldLabel("cluster-relation",mode),tuple(HeldLabel("bridging-ligand-occurrence",f"{left}-{right}-bridge-{i}") for i in range(1,n+1)))
def forced_cluster(entity:str,centres:tuple[str,...],relations:tuple[MetalCentreRelation,...])->ExactMetalCluster:
 c=tuple(HeldLabel("metal-centre",x) for x in centres);d=sum(r.mode.label=="direct-metal-bond" for r in relations);b=sum(r.mode.label=="bridging-ligand-path" for r in relations);return ExactMetalCluster(HeldLabel("cluster-entity",entity),c,relations,PositiveCount(len(c)),EMPTY_ONE if d==0 else PositiveCount(d),EMPTY_ONE if b==0 else PositiveCount(b))
def append_centre(cluster:ExactMetalCluster,label:str,attach_to:str,mode:str)->ExactMetalCluster:
 bridge=PositiveCount(1) if mode=="bridging-ligand-path" else EMPTY_ONE;return forced_cluster(cluster.entity.label,tuple(x.label for x in cluster.centres)+(label,),cluster.relations+(relation(attach_to,label,mode,bridge),))
DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-MATH-DISCRETE-001","SFT-MATH-COMBINATORICS-001","SFT-MATH-GRAPH-NETWORK-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-CHEM-MEAS-CHEMICAL-ENTITY-001","SFT-CHEM-BOND-CHEMICAL-BOND-001","SFT-CHEM-BOND-METALLIC-001","SFT-CHEM-STOICH-COMPOSITION-001","SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001","SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004","SFT-CHEM-ORGANOMETALLIC-METAL-CARBON-BOND-010")
DIMENSIONS:tuple[LawDimension,...]=(
 dimension("carrier","free-cluster-name","A name loses centre support.","one-retained-cluster-entity","All centres belong to one retained cluster."),dimension("centres","selected-metal-pair","A selected pair loses remaining centres.","complete-finite-multicentre-support","Every distinct metal centre is retained."),dimension("connectivity","proximity-only-list","A list does not prove connected support.","complete-connected-cluster-relation-graph","The generated cluster relation graph is connected."),dimension("direct","assumed-metal-metal-bond","Assumption confuses grouping with bonding.","explicit-direct-metal-bond-subgraph","Direct metal bonds are an explicit support subset."),dimension("bridge","implicit-ligand-bridge","An implicit bridge loses ligand occurrences.","complete-bridging-ligand-path-support","Every bridging path retains positive ligand support."),dimension("grouping","bond-required-cluster-definition","Requiring a bond rejects lawful held grouping.","held-grouping-relation-without-bond-necessity","Connected grouping may remain held without direct or bridge bonding."),dimension("counts","numerical-zero-missing-mode","Numerical zero is not structural absence.","positive-count-or-EmptyOne-per-relation-class","Each relation class has positive support or structural EmptyOne."),dimension("extension","catalogue-specific-exception","A catalogue destroys closure.","connected-centre-successor-no-extra-rule","A fresh centre attaches once and preserves connectivity."))
def _w():
 direct=forced_cluster("d",("M1","M2"),(relation("M1","M2","direct-metal-bond"),));bridge=forced_cluster("b",("M1","M2"),(relation("M1","M2","bridging-ligand-path",PositiveCount(2)),));group=forced_cluster("g",("M1","M2"),(relation("M1","M2","held-grouping-relation"),));succ=append_centre(bridge,"M3","M2","bridging-ligand-path");bad=False
 try:forced_cluster("x",("M1","M2","M3"),(relation("M1","M2","direct-metal-bond"),))
 except InadmissibleExactValue:bad=True
 return (("direct","Direct support counts one.",direct.direct_bond_count.value==1),("bridge-and-group","Bridge and nonbond grouping remain distinct.",bridge.bridge_path_count.value==1 and isinstance(group.direct_bond_count,EmptyOne)),("successor","Connected successor increments centre count.",succ.centre_count.value==3),("disconnected-control","Disconnected centre rejects.",bad))
OPERATIONAL_WITNESSES=_w();EXACT_RESULT="one-retained-cluster-entity__complete-finite-multicentre-support__complete-connected-cluster-relation-graph__explicit-direct-metal-bond-subgraph__complete-bridging-ligand-path-support__held-grouping-relation-without-bond-necessity__positive-count-or-EmptyOne-per-relation-class__connected-centre-successor-no-extra-rule"
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","OPERATIONAL_WITNESSES","ExactMetalCluster","MetalCentreRelation","append_centre","forced_cluster","relation")
