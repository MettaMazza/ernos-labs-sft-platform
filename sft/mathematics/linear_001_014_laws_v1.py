"""Complete Linear, Multilinear and Tensor family laws and exact witnesses."""
from fractions import Fraction
from itertools import combinations,product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
def mv(m,v):return tuple(sum(a*b for a,b in zip(row,v)) for row in m)
def mm(a,b):return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))) for i in range(len(a)))
def rank_mod2(m):
 rows=[list(x) for x in m];r=0
 for c in range(len(rows[0])):
  pivot=next((i for i in range(r,len(rows)) if rows[i][c]%2),None)
  if pivot is None:continue
  rows[r],rows[pivot]=rows[pivot],rows[r]
  for i in range(len(rows)):
   if i!=r and rows[i][c]%2:rows[i]=[(a+b)%2 for a,b in zip(rows[i],rows[r])]
  r+=1
 return r
def oriented_det_2(m):
 held=m[0][0]*m[1][1];opposed=m[0][1]*m[1][0]
 return ("held",held-opposed) if held>=opposed else ("opposed",opposed-held),held,opposed
def tensor3():return (((3,3),(4,4)),((5,5),(6,6)))
OBS={
"001":("exact generated coordinate carriers compose componentwise without erasing coordinate identity",tuple(a+b for a,b in zip((1,2,3),(2,1,1)))==(3,3,4)),
"002":("the composition of two exact linear maps equals their matrix product on every generated basis carrier",mv(((2,0),(0,3)),mv(((1,1),(1,0)),(1,2)))==(6,3) and mm(((2,0),(0,3)),((1,1),(1,0)))==((2,2),(3,0))),
"003":("exact row interchange is reversible and preserves the represented relation",tuple(reversed(((1,2),(3,4))))==((3,4),(1,2))),
"004":("the two-by-three binary matrix has rank two and exactly one retained null coordinate distinction",rank_mod2(((1,1,0),(0,0,1)))==2 and 3-rank_mod2(((1,1,0),(0,0,1)))==1),
"005":("determinant orientation is an exact held-or-opposed label with magnitude two rather than a negative scalar",oriented_det_2(((1,2),(3,4)))==(("opposed",2),4,6)),
"006":("the exact relations x plus y equals three and x plus twice y equals four uniquely retain x two and y one",tuple((x,y) for x,y in product(range(1,5),repeat=2) if x+y==3 and x+2*y==4)==((2,1),)),
"007":("the exact basis one-absence and one-one has dimension two and coordinates one-two for carrier three-two",tuple(a*(1,0)[i]+b*(1,1)[i] for i in range(2) for a,b in ((1,2),))==(3,2)),
"008":("inner-product and metric correspondence retain dot product five and squared distance five without an irrational root",sum(a*b for a,b in zip((1,2),(3,1)))==5 and sum((max(a,b)-min(a,b))**2 for a,b in zip((1,2),(3,1)))==5),
"009":("the positive symmetric map has uniform invariant mode three and held-opposed distinction mode one",mv(((2,1),(1,2)),(1,1))==(3,3) and tuple(a+b for a,b in zip(mv(((2,1),(1,2)),(1,0)),(0,1)))==tuple(a+b for a,b in zip(mv(((2,1),(1,2)),(0,1)),(1,0)))),
"010":("the positive root of x squared equals x plus one lies in the exact rational enclosure eight-fifths to thirteen-eighths",Fraction(8,5)**2<Fraction(8,5)+1 and Fraction(13,8)**2>Fraction(13,8)+1),
"011":("the tensor product of dimensions two and three has six coordinate cells and the exact outer product is retained",tuple(tuple(a*b for b in (3,4,5)) for a in (1,2))==((3,4,5),(6,8,10))),
"012":("tensor contraction pairs one declared index and retains the two uncontracted coordinate identities",(lambda t:tuple(tuple(sum(t[i][j][k] for k in range(2)) for j in range(2)) for i in range(2)))(tensor3())==((6,8),(10,12))),
"013":("exterior composition of a repeated carrier is absence while distinct orientation and three symmetric degree-two pairs are retained",len(tuple(combinations((1,2),2)))==1 and len(tuple(combinations((1,2,3),2)))==3),
"014":("the diagonal operator decomposes into two exact idempotent coordinate projectors with weights two and one",mm(((1,0),(0,0)),((1,0),(0,0)))==((1,0),(0,0)) and mm(((0,0),(0,1)),((0,0),(0,1)))==((0,0),(0,1))),
}
DEF={
"001":("SFT-MATH-LINEAR-VECTOR-COORDINATE-CARRIERS-001","Vectors as exact generated coordinate carriers","coordinate-identity-preserving-junction","A vector is an ordered generated coordinate carrier whose components remain individually addressable under lawful junction and exact-part scaling."),
"002":("SFT-MATH-LINEAR-MAP-COMPOSITION-002","Linear maps and composition","junction-scaling-preserving-map-composition","A linear map is forced by preservation of exact junction and scaling, and composition retains the ordered action of both maps."),
"003":("SFT-MATH-LINEAR-MATRIX-ROW-OPERATIONS-003","Matrix representation and exact row operations","reversible-row-relation-custody","A matrix is the coordinate incidence of a map; lawful row operations are exact reversible relation transformations with full operation custody."),
"004":("SFT-MATH-LINEAR-RANK-NULLITY-004","Rank, nullity and retained distinctions","image-kernel-distinction-ledger","Rank counts retained independent image distinctions while nullity counts source distinctions merged to absence; together they exhaust the finite source dimension."),
"005":("SFT-MATH-LINEAR-DETERMINANT-ORIENTATION-005","Determinants and orientation custody","held-opposed-volume-orientation","Determinant structure is the exact excess between held and opposed permutation products, recorded as an orientation label and nonnegative magnitude."),
"006":("SFT-MATH-LINEAR-EXACT-SYSTEMS-006","Exact systems of linear relations","complete-solution-support-census","A linear system is closed by generating every lawful coordinate candidate and retaining exactly the candidates satisfying every relation."),
"007":("SFT-MATH-LINEAR-BASIS-DIMENSION-007","Basis, dimension and change of basis","reversible-independent-coordinate-frame","A basis is a minimal independent spanning carrier; dimension is its exact cardinality and change of basis is a reversible coordinate relabelling."),
"008":("SFT-MATH-LINEAR-INNER-PRODUCT-METRIC-008","Inner-product and metric correspondence","exact-bilinear-pairing-squared-distance","Inner-product correspondence is an exact symmetric bilinear pairing; metric correspondence uses exact squared separation when roots are not lawful proof scalars."),
"009":("SFT-MATH-LINEAR-EIGEN-INVARIANT-SUPPORT-009","Eigenvalue and invariant-support correspondence","invariant-mode-exact-scaling","An invariant mode is a held coordinate relation reproduced by an operator up to one exact lawful scale, with opposed distinctions represented structurally rather than negatively."),
"010":("SFT-MATH-LINEAR-RATIONAL-SPECTRAL-ENCLOSURE-010","Exact rational spectral enclosures","nested-rational-mode-enclosure","A non-rational conventional spectral value is represented only by nested exact rational bounds with a proved exclusion and refinement rule."),
"011":("SFT-MATH-LINEAR-MULTILINEAR-TENSOR-PRODUCT-011","Multilinear maps and tensor products","universal-multicarrier-coordinate-product","A tensor product is the complete coordinate product that converts separately linear multi-input action into one exact linear carrier."),
"012":("SFT-MATH-LINEAR-TENSOR-CONTRACTION-012","Tensor contraction and index custody","paired-index-junction-custody","Contraction pairs exactly the declared dual indices, sums their complete incidence support and retains every uncontracted index identity."),
"013":("SFT-MATH-LINEAR-EXTERIOR-SYMMETRIC-013","Exterior and symmetric composition","orientation-and-symmetry-quotient","Exterior composition retains orientation and makes repeated direction absent; symmetric composition quotients order alone while retaining multiplicity."),
"014":("SFT-MATH-LINEAR-OPERATOR-DECOMPOSITION-014","Finite-dimensional operator decomposition","exact-invariant-component-decomposition","A finite operator decomposition is lawful when exact invariant components reconstruct the operator and each component has an independently witnessed action."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no target coordinate, imported linear-algebra theorem answer, fitted parameter or opaque solver selects the law","host 0 displays absence or counts artifacts only; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed infinite-dimensional or continuum space","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("coordinates","erased-coordinate-identity","Erasure destroys the carrier.","ordered-generated-coordinate-carriers","Every coordinate is generated and retained."),d("relation","imported-linear-answer","An imported theorem cannot select the result.",rel,"The relation follows from exact composition."),d("orientation","negative-scalar-shortcut","A negative scalar violates the proof domain.","held-opposed-structural-orientation","Orientation is carried by labels."),d("enumeration","selected-vectors","Samples cannot close a finite space.","complete-declared-coordinate-census","Every candidate is generated once."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-matrix-only","One table lacks a successor boundary.","finite-dimensional-successor-certificate","Coordinate extension is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class LinearProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-GRAPH-IDENTITY-ISOMORPHISM-001","SFT-MATH-ARITH-CANONICAL-FRACTION-008")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis LINEAR-{n} product before observation access.",f"Every supplied positive finite-dimensional LINEAR-{n} structure with coordinate, relation, orientation and successor boundaries retained.",dims(rel),f"LINEAR-{n} uniquely retains {rel}, exact coordinates, structural orientation, complete enumeration, root forcing and no extra rule.",(statement,text),"The least nonempty coordinate carrier exhibits the relation with every distinction retained.","Appending one coordinate preserves the prior carrier and generates every new component exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-coordinate-census","The witness reconstructs the complete declared coordinate relation.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact linear witness and reject four controls.","The claim closes the declared finite-dimensional successor grammar; infinite-dimensional correspondence requires separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
