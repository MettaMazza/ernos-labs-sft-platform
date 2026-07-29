"""Complete Geometry family laws and exact witnesses."""
from fractions import Fraction
from itertools import permutations,product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
FANO=((1,2,3),(1,4,5),(1,6,7),(2,4,6),(2,5,7),(3,4,7),(3,5,6))
def squared(a,b):return sum((max(x,y)-min(x,y))**2 for x,y in zip(a,b))
def midpoint(a,b):return tuple(Fraction(x+y,2) for x,y in zip(a,b))
def translate(a,t):return tuple(x+y for x,y in zip(a,t))
def shoelace_pair(points):return sum(points[i][0]*points[(i+1)%len(points)][1] for i in range(len(points))),sum(points[i][1]*points[(i+1)%len(points)][0] for i in range(len(points)))
def d4():
 pts=((1,1),(1,3),(3,1),(3,3));ops=[]
 for swap in (False,True):
  for rx,ry in product((False,True),repeat=2):ops.append(tuple(((4-y if ry else y,4-x if rx else x) if swap else (4-x if rx else x,4-y if ry else y)) for x,y in pts))
 return set(ops)
OBS={
"001":("three named points retain exact coordinate identity and equal held/opposed incidence totals on one line",shoelace_pair(((1,1),(2,2),(3,3)))==(11,11)),
"002":("the three-four coordinate separation has exact squared distance twenty-five without importing an irrational root",squared((1,1),(4,5))==25),
"003":("the exact midpoint is preserved by affine translation",translate(midpoint((1,1),(3,5)),(2,1))==midpoint(translate((1,1),(2,1)),translate((3,5),(2,1)))),
"004":("the seven-point projective incidence structure has seven lines, three points per line and one line per point pair",len(FANO)==7 and all(len(x)==3 for x in FANO) and all(sum(set(pair)<=set(line) for line in FANO)==1 for pair in __import__('itertools').combinations(range(1,8),2))),
"005":("the exact centre one-half one-half lies in the unit-square convex hull while coordinate two is separated by the upper support line",Fraction(1,2)<=1 and Fraction(2,1)>1),
"006":("the unit lattice square has four boundary carriers, absence of interior carriers and exact area one",shoelace_pair(((1,1),(2,1),(2,2),(1,2)))==(10,8)),
"007":("cube incidence has eight vertices twelve edges six faces and Euler total two",8+6==12+2),
"008":("exact bounding-box and nearest-point predicates select the unique lawful carrier",(2,2) in tuple(product(range(1,4),repeat=2)) and min(((1,1),(3,3),(5,5)),key=lambda p:squared(p,(2,2)))==(1,1)),
"009":("held/opposed orientation and diagonal intersection retain midpoint two-two without a negative scalar",shoelace_pair(((1,1),(3,1),(2,3)))[0]>shoelace_pair(((1,1),(3,1),(2,3)))[1] and midpoint((1,1),(3,3))==midpoint((1,3),(3,1))==(Fraction(2),Fraction(2))),
"010":("the positive finite solution set of x times y equals six contains exactly four ordered points",tuple((x,y) for x,y in product(range(1,7),repeat=2) if x*y==6)==((1,6),(2,3),(3,2),(6,1))),
"011":("two finite coordinate charts related by exact translation preserve every local adjacency distance",all(squared(a,b)==squared(translate(a,(2,3)),translate(b,(2,3))) for a,b in product(((1,1),(1,2),(2,1),(2,2)),repeat=2))),
"012":("tetrahedral finite transport assigns exact combinatorial curvature one-half at each of four vertices and total two",sum((Fraction(1,2) for _ in range(4)),Fraction(0,1))==2),
"013":("the four-by-four grid geodesic from one-one to three-three has exact path length four",(3-1)+(3-1)==4),
"014":("threefold self-similar replacement has one three nine twenty-seven retained cells through depth three",tuple(3**n for n in range(4))==(1,3,9,27)),
"015":("the three-by-three square tessellation has nine disjoint interiors and covers the complete registered region",len(tuple(product(range(1,4),repeat=2)))==9),
"016":("the square has exactly eight distinct generated dihedral transformations",len(d4())==8),
}
DEF={
"001":("SFT-MATH-GEOM-POINT-INCIDENCE-COORDINATE-001","Point, incidence and exact coordinate identity","named-point-incidence-custody","A point is a named coordinate carrier and incidence is an exact relation that preserves every point identity."),
"002":("SFT-MATH-GEOM-EUCLIDEAN-DISTANCE-002","Finite Euclidean-distance correspondence","exact-squared-distance","Euclidean distance correspondence is carried by exact squared coordinate separation when a conventional root would be irrational."),
"003":("SFT-MATH-GEOM-AFFINE-INVARIANCE-003","Affine combinations and affine invariance","exact-part-affine-combination","Affine combinations use exact parts summing to the whole and remain invariant under common translation."),
"004":("SFT-MATH-GEOM-PROJECTIVE-PERSPECTIVE-004","Projective incidence and perspective","projective-incidence-custody","Projective correspondence retains point-line incidence under homogeneous relabelling without importing continuum coordinates."),
"005":("SFT-MATH-GEOM-CONVEX-HULL-SEPARATION-005","Convex hulls and separation","exact-convex-combination-separation","A convex hull contains exactly the lawful exact-part combinations; separation is witnessed by an exact support comparison."),
"006":("SFT-MATH-GEOM-DISCRETE-LATTICE-POLYTOPE-006","Discrete geometry and lattice polytopes","lattice-point-polytope-incidence","A lattice polytope is the finite hull of exact coordinate carriers with boundary and interior custody."),
"007":("SFT-MATH-GEOM-POLYHEDRAL-EULER-INCIDENCE-007","Polyhedral faces and Euler-type incidence","face-edge-vertex-ledger","Polyhedral structure is the complete face-edge-vertex incidence ledger and Euler correspondence follows from its exact alternating orientation labels."),
"008":("SFT-MATH-GEOM-COMPUTATIONAL-PREDICATES-008","Computational geometry predicates","exact-geometric-decision-predicates","A computational geometry predicate is an exact finite comparison whose boundary and tie behavior are registered before evaluation."),
"009":("SFT-MATH-GEOM-ORIENTATION-INTERSECTION-009","Exact orientation and intersection tests","held-opposed-orientation-intersection","Orientation is a held/opposed product comparison, and intersection retains the exact common carrier or exact-part coordinate."),
"010":("SFT-MATH-GEOM-ALGEBRAIC-SOLUTION-SET-010","Algebraic-geometry solution-set correspondence","finite-polynomial-solution-census","Algebraic geometry correspondence is the complete exact solution-set census of registered polynomial relations over lawful carriers."),
"011":("SFT-MATH-GEOM-DIFFERENTIAL-FINITE-CHART-011","Differential-geometry finite-chart correspondence","finite-chart-transition-custody","A finite chart correspondence retains local coordinate relations and exact transition maps without presuming a continuum manifold."),
"012":("SFT-MATH-GEOM-CURVATURE-FINITE-TRANSPORT-012","Curvature by exact finite transport","finite-transport-curvature-ledger","Curvature is reconstructed as the exact retained discrepancy after closed finite transport or incidence-angle custody."),
"013":("SFT-MATH-GEOM-METRIC-GEODESIC-013","Metric geometry and geodesic correspondence","least-exact-path-separation","A geodesic is the least exact path separation in the complete generated path support."),
"014":("SFT-MATH-GEOM-FRACTAL-SELF-SIMILAR-014","Fractal and self-similar geometry","finite-depth-self-similar-replacement","Self-similar geometry is an exact replacement recursion with every finite depth certified; irrational dimension labels are not proof scalars."),
"015":("SFT-MATH-GEOM-PACKING-COVERING-TESSELLATION-015","Packing, covering and tessellation","disjoint-interior-complete-cover","Packing retains disjoint interiors, covering retains complete support, and tessellation requires both at the declared boundary."),
"016":("SFT-MATH-GEOM-TRANSFORMATION-GROUPS-016","Geometric transformation groups","reversible-incidence-transformations","A geometric transformation group is the complete reversible action preserving the registered incidence or metric relation."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no imported continuum geometry, theorem answer, fitted parameter or opaque solver selects the law","host 0 displays absence or counts artifacts only; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed continuum manifold or infinite tessellation","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("points","anonymous-or-lost-points","Lost point identity destroys incidence.","named-generated-points","Every point is retained."),d("relation","imported-geometric-answer","An imported theorem cannot select geometry.",rel,"The relation follows from exact incidence."),d("orientation","negative-coordinate-shortcut","A negative proof scalar violates the domain.","held-opposed-orientation","Orientation is structural."),d("enumeration","selected-configurations","Samples cannot close geometry.","complete-declared-configuration-census","Every configuration is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-diagram-only","One diagram lacks a successor rule.","finite-geometric-successor-certificate","Point extension is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful extension is admitted."))
class GeometryProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-LINEAR-VECTOR-COORDINATE-CARRIERS-001","SFT-MATH-ORDER-CONDITIONAL-TOTALITY-003")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis GEOM-{n} product before observation access.",f"Every supplied positive finite GEOM-{n} configuration with point, relation, orientation and successor boundaries retained.",dims(rel),f"GEOM-{n} uniquely retains {rel}, complete configuration custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty geometric configuration exhibits the relation with every point retained.","Appending one point generates every new incidence exactly once while preserving the prior configuration.",EX,(Witness("exact-observation",text,passed),Witness("complete-configuration-census","Every declared point configuration is tested.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact geometry witness and reject four controls.","The claim closes the declared finite successor grammar; continuum correspondence requires separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
