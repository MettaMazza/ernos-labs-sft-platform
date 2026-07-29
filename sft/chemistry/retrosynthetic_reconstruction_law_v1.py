"""Fold-native finite retrosynthetic decomposition and reconstruction (ORG-016)."""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from sft.claim_evidence import EMPTY_ONE,EmptyOne
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.physics.generated_empirical_law import LawDimension,dimension

@dataclass(frozen=True)
class SynthesisTree:
 carrier:tuple[HeldLabel,...]
 left:"SynthesisTree | EmptyOne"
 right:"SynthesisTree | EmptyOne"
 def __post_init__(self):
  if not self.carrier or any(x.family!="synthesis-carrier-occurrence" for x in self.carrier) or len(self.carrier)!=len(set(self.carrier)):raise InadmissibleExactValue("synthesis node requires a positive complete distinct carrier")
  terminal=isinstance(self.left,EmptyOne) and isinstance(self.right,EmptyOne)
  if terminal and len(self.carrier)!=1:raise InadmissibleExactValue("only one-occurrence carriers are terminal")
  if not terminal:
   if isinstance(self.left,EmptyOne) or isinstance(self.right,EmptyOne):raise InadmissibleExactValue("decomposition requires both positive parts")
   if self.left.carrier+self.right.carrier!=self.carrier:raise InadmissibleExactValue("forward composition must exactly reconstruct the parent")
 @property
 def forward_reconstruction(self):
  if isinstance(self.left,EmptyOne):return self.carrier
  return self.left.forward_reconstruction+self.right.forward_reconstruction
 @property
 def leaf_count(self):return PositiveCount(1) if isinstance(self.left,EmptyOne) else PositiveCount(self.left.leaf_count.value+self.right.leaf_count.value)

@lru_cache(maxsize=None)
def generate_all_trees(carrier:tuple[HeldLabel,...])->tuple[SynthesisTree,...]:
 if not carrier:raise InadmissibleExactValue("retrosynthesis cannot start from numerical or empty carrier")
 if len(carrier)==1:return (SynthesisTree(carrier,EMPTY_ONE,EMPTY_ONE),)
 rows=[]
 for cut in range(1,len(carrier)):
  for left in generate_all_trees(carrier[:cut]):
   for right in generate_all_trees(carrier[cut:]):rows.append(SynthesisTree(carrier,left,right))
 if len(rows)!=len(set(rows)):raise InadmissibleExactValue("generated synthesis trees duplicated")
 return tuple(rows)

def exhaustive_reconstruction(carrier):
 trees=generate_all_trees(carrier)
 if not trees or any(tree.forward_reconstruction!=carrier for tree in trees):raise InadmissibleExactValue("not every decomposition forward-reconstructs the target")
 return trees

DEPENDENCIES=("SFT-FOUNDATION-FORM-ENFORCEMENT-001","SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001","SFT-MATH-EXACT-ARITHMETIC-001","SFT-MATH-DISCRETE-001","SFT-MATH-COMBINATORICS-001","SFT-MATH-GRAPH-NETWORK-001","SFT-INFO-CONSERVATION-LOSS-001","SFT-COMP-FORM-STATE-TRANSITION-001","SFT-COMP-ALG-TREES-GRAPHS-001","SFT-CHEM-STOICH-COMPOSITION-001","SFT-CHEM-STOICH-CONSERVATION-001","SFT-CHEM-BOND-CHEMICAL-BOND-001","SFT-CHEM-MOL-MOLECULE-001","SFT-CHEM-RXN-IDENTITY-001","SFT-CHEM-RXN-MECHANISM-001","SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007","SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008","SFT-CHEM-ORGANIC-REACTION-FAMILY-001","SFT-CHEM-PROTECTING-GROUP-REVERSIBLE-STATE-015")
DIMENSIONS=(
 dimension("target","selected-target-fragment","A fragment cannot certify the synthesis target.","complete-held-target-carrier","Every target occurrence is retained."),
 dimension("cuts","chosen-disconnection-only","One favored disconnection is not exhaustive.","every-positive-binary-split-generated","Every internal split point is generated."),
 dimension("recursion","one-step-retrosynthetic-story","One step does not close the graph.","recursive-decomposition-to-One-leaves","Both positive parts recurse to one-occurrence leaves."),
 dimension("graph","cyclic-or-duplicate-search","Cycles or duplicates corrupt the finite census.","finite-acyclic-unique-tree-census","Carrier size strictly decreases and every tree occurs once."),
 dimension("forward","unverified-plausible-route","Plausibility is not reconstruction.","every-edge-has-exact-forward-inverse","Each child pair concatenates to its exact parent."),
 dimension("paths","successful-route-only","Keeping one successful route hides alternatives.","all-generated-paths-forward-reconstruct-target","Every complete tree reconstructs the target."),
 dimension("observation","external-mechanism-selects-tree","External examples cannot select the graph.","value-free-graph-sealed-before-comparison","The exhaustive tree law seals before terminology comparison."),
 dimension("extension","fixed-depth-exception","A fixed lookup is not a general law.","fresh-occurrence-successor-generates-all-new-splits","Appending one occurrence generates old embeddings and every new split."),
)

def _example():return exhaustive_reconstruction(tuple(HeldLabel("synthesis-carrier-occurrence",x) for x in ("a","b","c","d")))
def _witnesses():
 trees=_example();bad=empty=False
 try:SynthesisTree(trees[0].carrier,trees[0].left,SynthesisTree((HeldLabel("synthesis-carrier-occurrence","x"),),EMPTY_ONE,EMPTY_ONE))
 except InadmissibleExactValue:bad=True
 try:generate_all_trees(())
 except InadmissibleExactValue:empty=True
 return (("catalan-four","Four ordered leaves generate exactly five full binary trees.",len(trees)==5),("complete-target","Every tree retains the target.",all(x.carrier==trees[0].carrier for x in trees)),("all-splits","All three root split points occur.",len({len(x.left.carrier) for x in trees})==3),("terminal-One","Every terminal has one occurrence.",all(x.leaf_count==PositiveCount(4) for x in trees)),("acyclic","Every child is strictly smaller.",all(len(x.left.carrier)<len(x.carrier) and len(x.right.carrier)<len(x.carrier) for x in trees)),("forward","Every tree reconstructs exactly.",all(x.forward_reconstruction==x.carrier for x in trees)),("unique","No tree is duplicated.",len(trees)==len(set(trees))),("bad-control","Wrong inverse halts.",bad),("empty-control","Empty carrier halts.",empty),("successor","Five-leaf successor generates fourteen trees.",len(exhaustive_reconstruction(tuple(HeldLabel("synthesis-carrier-occurrence",x) for x in ("a1","b1","c1","d1","e1"))))==14))
OPERATIONAL_WITNESSES=_witnesses()
EXACT_RESULT="complete-held-target-carrier__every-positive-binary-split-generated__recursive-decomposition-to-One-leaves__finite-acyclic-unique-tree-census__every-edge-has-exact-forward-inverse__all-generated-paths-forward-reconstruct-target__value-free-graph-sealed-before-comparison__fresh-occurrence-successor-generates-all-new-splits"
__all__=("DEPENDENCIES","DIMENSIONS","EXACT_RESULT","OPERATIONAL_WITNESSES","SynthesisTree","exhaustive_reconstruction","generate_all_trees")
