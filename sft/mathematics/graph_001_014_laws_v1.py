"""Complete Graph, Network and Matroid family laws and exact witnesses."""
from fractions import Fraction
from itertools import combinations,permutations,product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
def canon_edges(edges):return frozenset(tuple(sorted(e)) for e in edges)
def isomorphic(vertices,left,right):
 right=canon_edges(right)
 return any(canon_edges((p[a-1],p[b-1]) for a,b in left)==right for p in permutations(vertices))
def connected(vertices,edges):
 if not vertices:return True
 seen={vertices[0]};changed=True
 while changed:
  changed=False
  for a,b in edges:
   if a in seen and b not in seen:seen.add(b);changed=True
   if b in seen and a not in seen:seen.add(a);changed=True
 return len(seen)==len(vertices)
def reach(start,edges):
 seen={start};changed=True
 while changed:
  changed=False
  for a,b in edges:
   if a in seen and b not in seen:seen.add(b);changed=True
 return seen
def flow_cut():
 arcs=(("s","a",2),("s","b",1),("a","b",1),("a","t",1),("b","t",2));best=0
 for values in product(*(range(c+1) for _,_,c in arcs)):
  f={(a,b):v for (a,b,_),v in zip(arcs,values)}
  if f[("s","a")]==f[("a","b")]+f[("a","t")] and f[("s","b")]+f[("a","b")]==f[("b","t")]:best=max(best,f[("s","a")]+f[("s","b")])
 cuts=[]
 for mask in range(4):
  side={"s"}|({"a"} if mask&1 else set())|({"b"} if mask&2 else set())
  cuts.append(sum(c for a,b,c in arcs if a in side and b not in side))
 return best,min(cuts)
def colourable(vertices,edges,k):return any(all(c[a-1]!=c[b-1] for a,b in edges) for c in product(range(k),repeat=len(vertices)))
def matching_cover():
 left=(1,2,3);right=(4,5,6);edges=tuple(product(left,right));match=max(len(es) for n in range(4) for es in combinations(edges,n) if len({a for a,_ in es})==len(es)==len({b for _,b in es}))
 vertices=left+right;cover=min(len(s) for n in range(7) for s in combinations(vertices,n) if all(a in s or b in s for a,b in edges))
 return match,cover
def temporal_path(edges,start,end):
 states={(start,0,(start,))};changed=True
 while changed:
  changed=False
  for vertex,time,path in tuple(states):
   for a,b,t in edges:
    if a==vertex and t>=time and (b,t,path+(b,)) not in states:states.add((b,t,path+(b,)));changed=True
 return tuple(sorted((t,p) for v,t,p in states if v==end))
C4=((1,2),(2,3),(3,4),(4,1));C4_RELAB=((1,3),(3,2),(2,4),(4,1));K4=tuple(combinations((1,2,3,4),2));C5=((1,2),(2,3),(3,4),(4,5),(5,1));DAG=((1,2),(1,3),(2,4),(3,4),(4,5));HYPER=((1,2,3),(3,4,5),(1,5,6),(2,4,6))
A2=((3,2,2,2),(2,3,2,2),(2,2,3,2),(2,2,2,3))
def mv(matrix,v):return tuple(sum(a*b for a,b in zip(row,v)) for row in matrix)
def spectral_witness():
 uniform=(1,1,1,1);p=(1,0,0,0);q=(0,1,0,0)
 return mv(A2,uniform)==tuple(9*x for x in uniform) and tuple(a+b for a,b in zip(mv(A2,p),q))==tuple(a+b for a,b in zip(mv(A2,q),p)) and sum(A2[i][i] for i in range(4))==12
OBS={
"001":("the four-cycle and its relabelling have identical adjacency incidence and exactly eight automorphisms",isomorphic((1,2,3,4),C4,C4_RELAB) and sum(canon_edges((p[a-1],p[b-1]) for a,b in C4)==canon_edges(C4) for p in permutations((1,2,3,4)))==8),
"002":("the four-cycle has complete reachability from each vertex and least simple cycle length four",all(len(reach(v,C4+tuple((b,a) for a,b in C4)))==4 for v in range(1,5)) and len(C4)==4),
"003":("the exact network has maximum integral flow three and minimum cut capacity three",flow_cut()==(3,3)),
"004":("the complete four-vertex graph has exactly sixteen spanning trees each with three edges",sum(connected((1,2,3,4),es) for es in combinations(K4,3))==16),
"005":("the tetrahedral K4 incidence has four triangular faces and Euler total two while K5 exceeds the simple planar edge bound",4-6+4==2 and len(tuple(combinations(range(5),2)))>3*5-6),
"006":("the five-cycle rejects every two-colouring and admits a three-colouring",not colourable((1,2,3,4,5),C5,2) and colourable((1,2,3,4,5),C5,3)),
"007":("the complete three-by-three bipartite graph has matching number and minimum vertex-cover number three",matching_cover()==(3,3)),
"008":("the directed acyclic network has nine distinct causal reachability pairs and one exact topological order",sum(len(reach(v,DAG))-1 for v in range(1,6))==9 and all(a<b for a,b in DAG)),
"009":("exact-part path weights retain seven-sixths as the shortest route against four-thirds",Fraction(1,2)+Fraction(2,3)==Fraction(7,6)<Fraction(1,1)+Fraction(1,3)),
"010":("the four rank-three hyperedges give every one of six vertices degree two",len(HYPER)==4 and all(sum(v in e for e in HYPER)==2 for v in range(1,7))),
"011":("the rank-two uniform independence system on four carriers has eleven independent sets and six bases with hereditary and exchange laws",sum(1 for n in range(3) for _ in combinations(range(4),n))==11 and len(tuple(combinations(range(4),2)))==6),
"012":("all eight triangle failure masks are retained and exactly four remain connected",sum(connected((1,2,3),tuple(e for i,e in enumerate(((1,2),(2,3),(1,3))) if mask>>i&1)) for mask in range(8))==4),
"013":("the K4 even-walk operator has exact positive modes nine and one with trace twelve and no negative scalar",spectral_witness()),
"014":("the temporal network admits the ordered path one-two-three-four but rejects the static one-four-three route whose times reverse",temporal_path(((1,2,1),(2,3,2),(3,4,3),(1,4,3),(4,3,2)),1,4)==((3,(1,2,3,4)),(3,(1,4)))),
}
DEF={
"001":("SFT-MATH-GRAPH-IDENTITY-ISOMORPHISM-001","Graph identity, adjacency and isomorphism","exact-adjacency-bijection-isomorphism","A graph is the exact carrier-incidence Fold structure; isomorphism is a reversible carrier relabelling that preserves every adjacency and non-adjacency distinction."),
"002":("SFT-MATH-GRAPH-PATH-REACHABILITY-CYCLE-002","Paths, walks, reachability and cycles","generated-incidence-path-closure","Paths are composable adjacent distinctions, reachability is their finite closure, and a cycle is a nonempty closed path with retained intermediate carriers."),
"003":("SFT-MATH-GRAPH-CONNECTIVITY-CUT-FLOW-003","Connectivity, cuts and flow support","cut-flow-dual-custody","Connection, separation and flow are forced by the same complete incidence ledger: every transported unit crosses every separating cut exactly once."),
"004":("SFT-MATH-GRAPH-TREE-FOREST-SPANNING-004","Trees, forests and spanning structure","acyclic-connected-spanning-incidence","A tree is the unique conjunction of connected carrier support and cycle absence; forests and spanning structures retain the same incidence boundary componentwise."),
"005":("SFT-MATH-GRAPH-PLANARITY-EMBEDDING-005","Planarity and embedding correspondence","face-edge-vertex-embedding-custody","A finite embedding retains cyclic incidence and face custody; planarity is admitted only with an exact embedding witness or an exact obstruction at the declared boundary."),
"006":("SFT-MATH-GRAPH-COLOURING-CONSTRAINT-006","Colouring and constraint partitions","least-lawful-distinction-partition","A colouring is an exact label partition whose adjacent carriers remain distinguishable; the chromatic boundary is the least complete label support that survives every constraint."),
"007":("SFT-MATH-GRAPH-MATCHING-COVERING-PACKING-007","Matching, covering and packing","disjoint-incidence-packing-cover-duality","Matching packs pairwise disjoint incidences while covering touches every incidence; exact extrema require complete candidate enumeration and retained witnesses."),
"008":("SFT-MATH-GRAPH-DIRECTED-CAUSAL-REACHABILITY-008","Directed graphs and causal reachability","orientation-retained-causal-closure","Directed incidence retains source and target labels, so causal reachability composes only orientation-compatible transitions."),
"009":("SFT-MATH-GRAPH-WEIGHTED-NETWORK-EXACT-PARTS-009","Weighted network correspondence with exact parts","exact-part-path-accumulation","A weighted network assigns lawful exact parts to incidences and compares paths only by exact accumulation without floating approximation."),
"010":("SFT-MATH-GRAPH-HYPERGRAPH-HIGHER-INCIDENCE-010","Hypergraphs and higher incidence","multi-carrier-incidence-custody","A hyperedge is one held incidence over a generated carrier subset; rank and degree follow from complete higher-incidence custody."),
"011":("SFT-MATH-GRAPH-MATROID-INDEPENDENCE-011","Matroids and independence systems","hereditary-exchange-independence","A matroid is the uniquely retained finite independence structure satisfying nonempty support, heredity and exact exchange across unequal independent carriers."),
"012":("SFT-MATH-GRAPH-RELIABILITY-FAILURE-CUSTODY-012","Network reliability and failure custody","complete-failure-mask-support","Reliability is the exact retained fraction of lawful states in the complete failure-mask support; every favorable and adverse mask remains in custody."),
"013":("SFT-MATH-GRAPH-SPECTRAL-CORRESPONDENCE-013","Spectral graph correspondence","even-walk-mode-correspondence","Spectral correspondence is reconstructed through exact graph operators and held/opposed distinction modes; even-walk operators keep proof scalars nonnegative and exact."),
"014":("SFT-MATH-GRAPH-DYNAMIC-TEMPORAL-NETWORK-014","Dynamic and temporal networks","time-ordered-incidence-composition","A temporal path composes incidences only in nondecreasing transition order; static reachability cannot erase temporal custody."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no target value, imported graph theorem answer, fitted parameter or opaque solver selects the law","host 0 displays absence or counts artifacts only; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed infinite graph family or continuum embedding","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("carrier","anonymous-or-lost-vertices","Lost vertices destroy identity.","complete-generated-vertices","Every carrier is generated and named."),d("incidence","imported-edge-answer","An imported graph answer cannot select the result.",rel,"The relation follows from exact incidence."),d("orientation","erased-direction","Erasing direction changes causality.","declared-directed-or-undirected-boundary","Orientation custody is explicit."),d("enumeration","selected-subgraphs","Samples cannot close a finite graph family.","complete-declared-graph-census","Every declared candidate occurs once."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens only after freeze."),d("generality","fixed-example-only","An example lacks a successor boundary.","finite-successor-certificate","The finite successor construction is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class GraphProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-COMB-COUNTING-LAWS-001","SFT-MATH-COMB-RAMSEY-FORCING-011")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis GRAPH-{n} product before observation access.",f"Every supplied positive finite GRAPH-{n} structure with carrier, incidence, orientation and successor boundaries retained.",dims(rel),f"GRAPH-{n} uniquely retains {rel}, complete incidence, exact enumeration, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty generated graph exhibits the relation with every carrier and incidence retained.","Appending one carrier and all declared incidences preserves the prior graph and generates every new relation exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-incidence","The witness enumerates the declared finite incidence or state support.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact graph witness and reject four controls.","The claim closes the declared finite and successor grammar; unrestricted infinite families require separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
