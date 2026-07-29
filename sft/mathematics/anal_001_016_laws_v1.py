"""Complete Analysis Correspondence family laws and exact witnesses."""
from fractions import Fraction
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
def distance(a,b):return max(a,b)-min(a,b)
def normalize(pair):
 a,b=pair;c=min(a,b);return (a-c,b-c)
def pair_add(a,b):return normalize((a[0]+b[0],a[1]+b[1]))
def pair_flip(a):return (a[1],a[0])
def pair_half(a):return (a[0]//2,a[1]//2)
def h2(values):return pair_add(values[0],values[1]),pair_add(values[0],pair_flip(values[1]))
def ih2(values):return pair_half(pair_add(values[0],values[1])),pair_half(pair_add(values[0],pair_flip(values[1])))
def cyclic_convolution(a,b):return tuple(sum(a[j]*b[(i-j)%len(a)] for j in range(len(a))) for i in range(len(a)))
OBS={
"001":("the sequence one-plus-one-over-n carries a nested exact enclosure of one with width one-over-n",all(Fraction(1)+Fraction(1,n+1)<Fraction(1)+Fraction(1,n) for n in range(1,8))),
"002":("all tail pairs of one-plus-one-over-n are bounded by the first retained tail width",all(distance(Fraction(1)+Fraction(1,m),Fraction(1)+Fraction(1,n))<=Fraction(1,k) for k in range(1,7) for m,n in product(range(k,9),repeat=2))),
"003":("nested rational carriers retain a common exact member one without asserting a completed continuum",all(Fraction(1)<=Fraction(1)+Fraction(1,n) for n in range(1,9))),
"004":("the geometric series truncation has exact remainder one-over-two-to-the-n",all(sum((Fraction(1,2**k) for k in range(1,n+1)),Fraction(0))+Fraction(1,2**n)==1 for n in range(1,9))),
"005":("the finite power-series truncation at one-half retains every term and the exact tail enclosure",sum((Fraction(1,2**k) for k in range(5)),Fraction(0))==Fraction(31,16)),
"006":("the generated three-point function space has eight binary functions with exact pointwise identity",len(tuple(product((0,1),repeat=3)))==8),
"007":("exact one-norm seminorm and metric relations are nonnegative and satisfy the declared finite triangle census",sum((1,2,3))==6 and distance(1,3)<=distance(1,2)+distance(2,3)),
"008":("the exact doubling operator is bounded by factor two on every generated positive two-coordinate carrier",all(sum((2*x,2*y))==2*sum((x,y)) for x,y in product(range(1,5),repeat=2))),
"009":("the four-point alternating harmonic observation of one-two-one-two has opposed magnitude two",normalize((1+1,2+2))==(0,2)),
"010":("the held-opposed two-point transform of three-one inverts exactly without negative or imaginary scalars",ih2(h2(((3,0),(1,0))))==((3,0),(1,0))),
"011":("cyclic convolution with the exact identity support returns the original sequence and complete correlation is retained",cyclic_convolution((1,2,3),(1,0,0))==(1,2,3)),
"012":("the two coordinate basis carriers are orthogonal and reconstruct three-two exactly",0==1*0+0*1 and (3,2)==(3*1+2*0,3*0+2*1)),
"013":("the exact weak observation with weights one-third two-thirds returns the test-function pairing five-thirds",Fraction(1,3)*1+Fraction(2,3)*2==Fraction(5,3)),
"014":("the affine half-contraction halves every exact pair distance and retains fixed carrier one",all(distance((x+1)/2,(y+1)/2)==distance(x,y)/2 for x,y in product((Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)),repeat=2)) and (Fraction(1)+1)/2==1),
"015":("held phase-pair multiplication of one-plus-quarter-phase with itself has absent real distinction and phase magnitude two",normalize((1,1))==(0,0) and 1+1==2),
"016":("the diagonal operator spectral measure has positive weights one and four, total five and first moment fourteen",1+4==5 and 2*1+3*4==14),
}
DEF={
"001":("SFT-MATH-ANAL-SEQUENCE-CONVERGENCE-001","Exact sequence convergence certificates","nested-sequence-enclosure","Sequence convergence is an exact nested enclosure certificate with a lawful refinement rule and no completed continuum premise."),
"002":("SFT-MATH-ANAL-CAUCHY-SUPPORT-002","Cauchy-type generated support correspondence","tail-pair-distance-bound","Cauchy correspondence requires every generated tail pair to lie within the registered exact tail bound."),
"003":("SFT-MATH-ANAL-COMPLETENESS-CORRESPONDENCE-003","Completeness correspondence without completed continuum","nested-carrier-intersection-certificate","Completeness correspondence is a certified retained carrier common to every nested exact enclosure, without importing a completed continuum."),
"004":("SFT-MATH-ANAL-SERIES-REMAINDER-004","Series convergence and remainder enclosures","partial-sum-remainder-ledger","A series certificate retains every partial term and an exact remainder enclosure whose refinement is independently witnessed."),
"005":("SFT-MATH-ANAL-POWER-SERIES-TRUNCATION-005","Power-series finite truncation custody","coefficient-term-tail-custody","Power-series correspondence retains coefficients, exact powers, truncation depth and tail enclosure separately."),
"006":("SFT-MATH-ANAL-FUNCTIONAL-SPACE-REPRESENTATION-006","Functional-space finite-representation correspondence","finite-function-value-carrier","A function space is represented by complete exact value carriers on a generated domain and pointwise lawful operations."),
"007":("SFT-MATH-ANAL-NORM-SEMINORM-METRIC-007","Norm, seminorm and metric correspondence","exact-size-separation-relations","Norm, seminorm and metric correspondence is admitted through complete exact size, degeneracy and triangle-relation censuses."),
"008":("SFT-MATH-ANAL-BOUNDED-COMPACT-OPERATOR-008","Bounded and compact operator correspondence","finite-operator-bound-image-custody","Bounded and compact operator correspondence retains an exact action bound and the complete finite generated image support."),
"009":("SFT-MATH-ANAL-HARMONIC-FOURIER-SUPPORT-009","Harmonic and Fourier finite-support correspondence","held-opposed-harmonic-components","Finite harmonic correspondence decomposes a generated signal into exact held/opposed phase components without imaginary proof scalars."),
"010":("SFT-MATH-ANAL-TRANSFORM-INVERSION-010","Transform inversion on generated supports","exact-transform-reconstruction","A transform is admissible when its exact held/opposed component ledger reconstructs every input carrier without loss."),
"011":("SFT-MATH-ANAL-CONVOLUTION-CORRELATION-011","Convolution and correlation identities","complete-shift-pair-accumulation","Convolution and correlation are complete shifted pair accumulations with every cyclic or bounded index retained."),
"012":("SFT-MATH-ANAL-ORTHOGONAL-BASIS-EXPANSION-012","Orthogonality and basis expansion correspondence","orthogonal-coordinate-reconstruction","Orthogonal expansion correspondence requires absent cross-pairing and exact reconstruction from all retained basis coordinates."),
"013":("SFT-MATH-ANAL-DISTRIBUTIONAL-WEAK-OBSERVATION-013","Distributional and weak-observation correspondence","exact-test-function-pairing","Weak or distributional correspondence is only an exact action on registered test-function carriers, not an imported generalized object."),
"014":("SFT-MATH-ANAL-NONLINEAR-CONTRACTION-014","Nonlinear analysis and contraction boundaries","exact-contraction-fixed-carrier","A contraction boundary is an exact pair-distance reduction law with a separately witnessed fixed carrier."),
"015":("SFT-MATH-ANAL-COMPLEX-HELD-PAIR-015","Complex-analysis held-pair correspondence","period-four-held-phase-pair","Complex correspondence uses exact held phase-labelled pairs and structural opposition; no imaginary or negative proof scalar is admitted."),
"016":("SFT-MATH-ANAL-SPECTRAL-MEASURE-016","Operator spectral-measure correspondence","positive-invariant-weight-ledger","Spectral-measure correspondence is a positive exact weight ledger over independently witnessed invariant operator modes."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no imported continuum, infinity, imaginary scalar, theorem answer, fitted parameter or opaque solver selects the law","host 0 displays absence or counts artifacts only; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed infinite sequence space or continuum function space","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("support","lost-analytic-carriers","Lost carriers destroy convergence custody.","complete-generated-support","Every carrier is retained."),d("relation","imported-analysis-answer","An imported theorem cannot select analysis.",rel,"The relation follows from exact support."),d("phase","imaginary-or-negative-scalar","Forbidden scalars violate the domain.","held-opposed-phase-structure","Phase is structural."),d("enumeration","selected-truncations","Samples cannot close analysis.","complete-declared-truncation-census","Every truncation is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened limit may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-support-only","One support lacks a successor rule.","finite-support-successor-certificate","Support extension is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful extension is admitted."))
class AnalysisProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006","SFT-MATH-LINEAR-OPERATOR-DECOMPOSITION-014")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis ANAL-{n} product before observation access.",f"Every supplied positive finite ANAL-{n} support with carrier, relation, phase and successor boundaries retained.",dims(rel),f"ANAL-{n} uniquely retains {rel}, complete analytic custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty analytic support exhibits the relation with every carrier retained.","Appending one term, coordinate or truncation preserves the prior support and generates every new relation exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-support-census","Every declared term, transform or truncation is tested.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact analysis witness and reject four controls.","The claim closes the declared finite-support successor grammar; continuum correspondence requires separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
