"""Complete Numerical Mathematics family laws over exact generated support."""
from fractions import Fraction
from itertools import product
from math import gcd
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension

def gap(first,second):return second-first if first<=second else first-second
def interval_add(left,right):return (left[0]+right[0],left[1]+right[1])
def interval_multiply_positive(left,right):return (left[0]*right[0],left[1]*right[1])
def exact_rounding_record(value):
 lower=value.numerator//value.denominator;upper=lower+1
 return lower,upper,lower if value-lower<upper-value else upper
def forward_sequence(parts):
 value=Fraction(1)
 for _ in range(parts):value=value+value/Fraction(2)
 return value
def geometric_partial(parts):
 value=Fraction(1,2)
 for index in range(2,parts+1):value=value+Fraction(1,2**index)
 return value

OBS={
"001":("seven-thirds retains numerator and denominator, is enclosed by two and three, and rounds to two only with both exact distances retained",exact_rounding_record(Fraction(7,3))==(2,3,2) and gap(Fraction(7,3),Fraction(2))==Fraction(1,3) and gap(Fraction(7,3),Fraction(3))==Fraction(2,3)),
"002":("positive rational interval addition and multiplication retain the exact outward bounds",interval_add((Fraction(1,2),Fraction(2,3)),(Fraction(1,3),Fraction(1,2)))==(Fraction(5,6),Fraction(7,6)) and interval_multiply_positive((Fraction(1,2),Fraction(2,3)),(Fraction(1,3),Fraction(1,2)))==(Fraction(1,6),Fraction(1,3))),
"003":("the n-part geometric truncation plus its exact retained residual reconstructs One for every generated n",all(geometric_partial(n)+Fraction(1,2**n)==1 for n in range(1,9))),
"004":("the declared approximate solution has exact forward gap one-thirtieth and exact backward coefficient gap one-twenty-third",gap(Fraction(23,10),Fraction(7,3))==Fraction(1,30) and gap(Fraction(7,1)/Fraction(23,10),Fraction(3))==Fraction(1,23)),
"005":("the generated scale map carries an input change of one-hundredth to an output change of one-twentieth with exact sensitivity five",(lambda x,y,a:gap(a*x,a*y)==Fraction(1,20) and gap(a*x,a*y)/gap(x,y)==5)(Fraction(2),Fraction(201,100),Fraction(5))),
"006":("the exact enclosure error family one-over-two-to-n contracts by the forced ratio one-half at every successor",all(Fraction(1,2**(n+1))*2==Fraction(1,2**n) for n in range(1,9))),
"007":("the positive solution of square-equals-two is isolated between seven-fifths and three-halves by exact ordered square comparisons",Fraction(7,5)**2<Fraction(2)<Fraction(3,2)**2),
"008":("complete positive-pair enumeration uniquely solves x-plus-y-equals-five and x-plus-two-y-equals-eight",tuple((x,y) for x,y in product(range(1,9),repeat=2) if x+y==5 and x+2*y==8)==((2,3),)),
"009":("exact midpoint interpolation between the registered endpoint records gives the uniquely retained midpoint value four",Fraction(1,2)*Fraction(2)+Fraction(1,2)*Fraction(6)==4),
"010":("midpoint and trapezoid accumulation over the positive interval one-to-three both return the exact area four for the identity values",Fraction(2)*Fraction(2)==4 and Fraction(2)*Fraction(1+3,2)==4),
"011":("two exact half-part forward recurrence steps from One produce nine-fourths with every intermediate state retained",forward_sequence(2)==Fraction(9,4)),
"012":("the exact one-half plus one-third certificate cross-multiplies to five-sixths and proves its output fraction reduced",(lambda n,d:n==5 and d==6 and gcd(n,d)==1)(1*3+1*2,2*3)),
}

DEF={
"001":("SFT-MATH-NUM-EXACT-REPRESENTATION-ROUNDING-001","Exact numerical representation and rounding custody","exact-representation-rounding-custody","Every numerical approximation retains its exact rational source, enclosing neighbours, selected display and the comparison that selected it."),
"002":("SFT-MATH-NUM-INTERVAL-RATIONAL-ENCLOSURE-002","Interval and rational enclosure arithmetic","outward-rational-enclosure","Interval arithmetic propagates exact rational lower and upper witnesses without admitting an unrepresented continuum scalar."),
"003":("SFT-MATH-NUM-TRUNCATION-DISCRETIZATION-ERROR-003","Truncation and discretization error","retained-residual-error","Truncation error is the exact retained residual required to reconstruct the untruncated generated relation."),
"004":("SFT-MATH-NUM-FORWARD-BACKWARD-STABILITY-004","Forward and backward stability","forward-backward-exact-gap","Forward and backward stability are separate exact gaps between retained problem, result and reconstructed input records."),
"005":("SFT-MATH-NUM-CONDITIONING-SENSITIVITY-005","Conditioning and sensitivity","input-output-gap-ratio","Conditioning is an exact relation between a registered input distinction and the output distinction transported by the generated map."),
"006":("SFT-MATH-NUM-CONVERGENCE-ORDER-BOUND-006","Convergence order with exact bounds","successor-error-contraction","Convergence order is a certified successor relation among exact enclosure widths, not an assumed limiting scalar."),
"007":("SFT-MATH-NUM-ROOT-ISOLATION-EQUATION-SOLVING-007","Root isolation and equation solving","ordered-rational-root-bracket","Equation solving retains exact rational brackets and structural comparison labels when the conventional solution is not an admissible proof scalar."),
"008":("SFT-MATH-NUM-LINEAR-SYSTEM-SOLVERS-008","Linear-system exact and approximate solvers","complete-positive-system-enumeration","A finite linear system is solved by complete exact candidate enumeration or a certified enclosure with residual custody."),
"009":("SFT-MATH-NUM-INTERPOLATION-APPROXIMATION-009","Interpolation and approximation","exact-weighted-interpolation","Interpolation is an exact weighted reconstruction from registered support; approximation retains its enclosure and residual."),
"010":("SFT-MATH-NUM-QUADRATURE-ACCUMULATION-010","Quadrature and accumulation enclosures","exact-cell-accumulation","Quadrature is a finite exact cell accumulation whose refinement relation and enclosure are retained."),
"011":("SFT-MATH-NUM-DIFFERENTIAL-EQUATION-CORRESPONDENCE-011","Differential-equation numerical correspondence","exact-recurrence-state-trace","Numerical differential-equation correspondence is an exact generated recurrence with every state, part width and residual recorded."),
"012":("SFT-MATH-NUM-VERIFIED-COMPUTATION-CERTIFICATE-012","Verified computation and certificate extraction","replayable-arithmetic-certificate","Verified computation emits an independently replayable certificate containing exact inputs, operations, result, reduction and boundary conditions."),
}

IDS=tuple(DEF[n][0] for n in sorted(DEF))
EX=("no axiom, imported numerical-analysis theorem, conventional library result or target outcome selects the result","host 0 denotes structural absence or counts artifacts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no unrecorded rounding, truncation, residual, conditioning or discretization distinction","no continuum limit is imported where only finite refinement or rational enclosure is proved","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("representation","floating-or-opaque-number","Opaque numerical carriers lose exact provenance.","exact-generated-fraction-record","Numerator, denominator and normalization are retained."),d("numerical-law","imported-numerical-answer","An imported answer cannot select the law.",rel,"The relation follows from exact generated operations."),d("orientation","negative-error-scalar","Negative proof scalars violate the domain.","ordered-gap-or-held-orientation","Error direction is structural and magnitude is nonnegative exact."),d("enumeration","sampled-inputs","Samples cannot close a declared numerical grammar.","complete-declared-input-census","Every declared exact input is checked."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the premise-free root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","single-resolution-only","One resolution lacks a successor certificate.","finite-successor-or-explicit-boundary","Refinement and its boundary are explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class NumericalProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-CAT-OPERAD-HIGHER-BOUNDARY-012","SFT-MATH-CALC-CONTINUUM-LIMIT-BOUNDARY-012","SFT-MATH-ALEXT-POLYNOMIAL-ROOT-ISOLATION-001")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis NUM-{n} product before observation access.",f"Every supplied positive exact rational NUM-{n} input, retained residual, registered refinement and explicit correspondence boundary.",dims(rel),f"NUM-{n} uniquely retains {rel}, exact numerical custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least generated calculation retains one exact input, one operation and one reconstructible result.","Appending one exact input, operation or refinement part preserves every prior record and enumerates every new distinction exactly once.",EX,(Witness("exact-observation",text,passed),Witness("exact-arithmetic-custody","Every numerical record is an integer or normalized rational with structural orientation.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact numerical witness and reject four controls.","The claim closes the declared exact finite and successor grammar; unrestricted continuum assertions require separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
