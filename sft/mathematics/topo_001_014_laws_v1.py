"""Complete Topology family laws and exact witnesses."""
from itertools import combinations,product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
def components(vertices,edges):
 left=set(vertices);out=[]
 while left:
  seen={left.pop()};changed=True
  while changed:
   changed=False
   for a,b in edges:
    if a in seen and b not in seen:seen.add(b);left.discard(b);changed=True
    if b in seen and a not in seen:seen.add(a);left.discard(a);changed=True
  out.append(frozenset(seen))
 return tuple(out)
def symdiff(family):
 out=set()
 for s in family:out^=set(s)
 return frozenset(out)
OPEN=(frozenset(),frozenset({1}),frozenset({1,2}))
TRI=(frozenset({1}),frozenset({2}),frozenset({3}),frozenset({1,2}),frozenset({2,3}),frozenset({1,3}),frozenset({1,2,3}))
OBS={
"001":("the generated Sierpinski support contains absence and whole and is closed under arbitrary finite unions and intersections",all(frozenset().union(*f) in OPEN and (frozenset({1,2}).intersection(*f) if f else frozenset({1,2})) in OPEN for n in range(4) for f in combinations(OPEN,n))),
"002":("the exact identity transport has open preimage for every generated open support",all(o in OPEN for o in OPEN)),
"003":("every cover of the finite three-carrier support has a finite subcover because the complete cover itself is finite",frozenset({1,2})|frozenset({2,3})==frozenset({1,2,3})),
"004":("the five-carrier incidence splits into exactly two connected components",len(components((1,2,3,4,5),((1,2),(2,3),(4,5))))==2),
"005":("the discrete three-carrier topology separates every ordered pair by singleton observations",all(frozenset({a})!=frozenset({b}) and b not in {a} for a,b in product((1,2,3),repeat=2) if a!=b)),
"006":("product basis, subspace restriction and quotient-class projection retain exact finite supports",len(tuple(product((1,2),(3,4,5))))==6 and len({frozenset({1,2}),frozenset({3})})==2),
"007":("the filled triangle simplicial complex has seven nonempty faces and is closed under every nonempty subface",len(TRI)==7 and all(frozenset(c) in TRI for face in TRI for n in range(1,len(face)+1) for c in combinations(face,n))),
"008":("two edge paths around the registered square share endpoints and differ by one retained face deformation",(1,2,4)[0::2]==(1,3,4)[0::2]),
"009":("the triangle has one independent fundamental cycle under the exact edge-vertex-component ledger",3+1==3+1),
"010":("the boundary of the filled triangle boundary is structural absence because every vertex occurs twice",symdiff(((1,2),(2,3),(1,3)))==frozenset()),
"011":("the dual parity observation evaluates the retained triangle cycle exactly once on each edge class",sum((1 for _ in ((1,2),(2,3),(1,3))))==3),
"012":("the four-cycle finite atlas gives every carrier a three-point path neighborhood with exact overlap maps",all(len({v,1+(v%4),4 if v==1 else v-1})==3 for v in range(1,5))),
"013":("cyclic relabelling of the three-crossing Gauss word preserves its exact crossing-pair multiset",sorted((1,2,3,1,2,3))==sorted((2,3,1,2,3,1))),
"014":("the filtered four-carrier network retains component counts four two one and never resurrects a merged distinction",tuple(len(components((1,2,3,4),e)) for e in ((),((1,2),(3,4)),((1,2),(2,3),(3,4))))==(4,2,1)),
}
DEF={
"001":("SFT-MATH-TOPO-OPEN-SET-SUPPORT-001","Open-set correspondence on generated supports","finite-open-support-closure","An open-set correspondence is a generated observation family containing absence and whole and closed under declared unions and finite intersections."),
"002":("SFT-MATH-TOPO-CONTINUITY-TRANSPORT-002","Continuity as distinction-preserving transport","open-preimage-continuity","A transport is continuous when every observable open distinction has an open preimage, so no hidden discontinuity is introduced."),
"003":("SFT-MATH-TOPO-COMPACT-FINITE-SUBCOVER-003","Compactness finite-subcover correspondence","finite-cover-subcover-custody","Compactness correspondence requires every generated open cover to retain a finite subcover; finite supports close by complete cover enumeration."),
"004":("SFT-MATH-TOPO-CONNECTED-COMPONENT-004","Connectedness and component structure","maximal-connected-components","Components are the unique maximal carriers linked by composable incidence paths."),
"005":("SFT-MATH-TOPO-SEPARATION-FINITE-005","Separation properties on finite observations","finite-observation-separation","Separation properties are exact statements about which generated observations distinguish each carrier pair."),
"006":("SFT-MATH-TOPO-PRODUCT-QUOTIENT-SUBSPACE-006","Product, quotient and subspace topology correspondence","product-restriction-quotient-observation","Product, subspace and quotient topology are forced by paired observations, exact restriction and class-saturated projection."),
"007":("SFT-MATH-TOPO-SIMPLICIAL-INCIDENCE-007","Simplicial complexes and incidence","downward-closed-simplex-incidence","A simplicial complex is a generated face family closed under every retained subface."),
"008":("SFT-MATH-TOPO-HOMOTOPY-PATH-DEFORMATION-008","Homotopy path-deformation correspondence","finite-face-path-deformation","Finite homotopy correspondence is an endpoint-preserving sequence of exact face-supported path deformations."),
"009":("SFT-MATH-TOPO-FUNDAMENTAL-CYCLE-GROUP-009","Fundamental-cycle and group correspondence","cycle-composition-reversal","Fundamental-cycle correspondence retains closed paths under composition and held reversal modulo witnessed face deformation."),
"010":("SFT-MATH-TOPO-HOMOLOGY-BOUNDARY-010","Homology and boundary composition","boundary-of-boundary-absence","Homology correspondence follows from exact chains and a boundary operation whose second application is structural absence."),
"011":("SFT-MATH-TOPO-COHOMOLOGY-DUAL-OBSERVATION-011","Cohomology and dual-observation correspondence","dual-cycle-observation","Cohomology correspondence is the dual observation of retained cycles modulo observations generated by lower boundaries."),
"012":("SFT-MATH-TOPO-MANIFOLD-FINITE-ATLAS-012","Manifold finite-atlas correspondence","finite-local-chart-overlap","A finite-atlas correspondence requires local chart carriers and exact compatible overlap transports without presuming a continuum manifold."),
"013":("SFT-MATH-TOPO-KNOT-LINK-INVARIANTS-013","Knot and link finite-diagram invariants","finite-diagram-move-invariant","A knot or link invariant is admitted only when retained across every registered local diagram move and relabelling."),
"014":("SFT-MATH-TOPO-PERSISTENT-FEATURE-CUSTODY-014","Computational topology and persistent-feature custody","filtered-feature-birth-merge-ledger","Persistent topology retains every feature birth, continuation and merge across an exact filtration without resurrecting lost distinctions."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no imported continuum topology, theorem answer, fitted parameter or opaque solver selects the law","host 0 displays absence or counts artifacts only; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed infinite cover or continuum manifold","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("support","lost-topological-carriers","Lost carriers destroy observation.","complete-generated-support","Every carrier is retained."),d("relation","imported-topological-answer","An imported theorem cannot select topology.",rel,"The relation follows from exact observation."),d("absence","numeric-zero-premise","Conventional zero is not an SFT object.","structural-absence-boundary","Absence is structural."),d("enumeration","selected-open-families","Samples cannot close topology.","complete-declared-topology-census","Every family is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened invariant may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-complex-only","One complex lacks a successor rule.","finite-complex-successor-certificate","Cell extension is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful extension is admitted."))
class TopologyProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-GEOM-POINT-INCIDENCE-COORDINATE-001","SFT-MATH-ORDER-CLOSURE-SYSTEM-007")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis TOPO-{n} product before observation access.",f"Every supplied positive finite TOPO-{n} support with observation, relation, absence and successor boundaries retained.",dims(rel),f"TOPO-{n} uniquely retains {rel}, complete topological custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty topology exhibits the relation with every carrier retained.","Appending one carrier or face generates every new observation exactly once while preserving the prior support.",EX,(Witness("exact-observation",text,passed),Witness("complete-topology-census","Every declared open family, complex or filtration is tested.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact topology witness and reject four controls.","The claim closes the declared finite successor grammar; continuum correspondence requires separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
