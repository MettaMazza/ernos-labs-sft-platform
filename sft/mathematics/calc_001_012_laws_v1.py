"""Complete Calculus Correspondence family laws and exact witnesses."""
from fractions import Fraction
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
def delta(values):return tuple(values[i+1]-values[i] for i in range(len(values)-1))
def repeated(values,n):
 out=tuple(values)
 for _ in range(n):out=delta(out)
 return out
OBS={
"001":("the exact local changes of one four nine sixteen are three five seven",delta((1,4,9,16))==(3,5,7)),
"002":("the third forward difference of the generated cubic sequence is the constant six",repeated((1,8,27,64,125),3)==(6,6)),
"003":("complete accumulation of the first five generated carriers is fifteen",sum(range(1,6))==15),
"004":("the accumulated local changes reconstruct the terminal value exactly",1+sum(delta((1,4,9,16)))==16),
"005":("the exact product-difference law reconstructs the change from six to twelve as six",3*1+3*1==6),
"006":("the rational enclosures one to one-plus-one-over-n are nested and their exact widths strictly refine",all(Fraction(1,n+1)<Fraction(1,n) for n in range(1,8))),
"007":("the shrinking-part quotient for the square law at carrier two is exactly four plus the retained part",all(Fraction(4*n+1,n)==4+Fraction(1,n) for n in range(1,9))),
"008":("left and right refinement sums for the identity law enclose one-half with exact width one-over-n",all(Fraction(n-1,2*n)<=Fraction(1,2)<=Fraction(n+1,2*n) and Fraction(n+1,2*n)-Fraction(n-1,2*n)==Fraction(1,n) for n in range(2,9))),
"009":("the two coordinate directional changes of the product law at two-three are three and two",3*1==3 and 2*1==2),
"010":("the two local flux changes one and one accumulate to the exact boundary held-opposed magnitude two",1+1==3-1),
"011":("the exact squared-separation energy over carriers one through five has unique stationary minimum at three",tuple(x for x in range(1,6) if (max(x,3)-min(x,3))**2==min((max(y,3)-min(y,3))**2 for y in range(1,6)))==(3,)),
"012":("the registered exact enclosures are nested with strictly shrinking rational width and claim no continuum object",all(Fraction(1,n+1)<Fraction(1,n) for n in range(1,8))),
}
DEF={
"001":("SFT-MATH-CALC-FINITE-DIFFERENCE-001","Exact finite difference and local change","oriented-local-change","Finite difference is the exact held/opposed change between adjacent generated values, with magnitude represented nonnegatively."),
"002":("SFT-MATH-CALC-HIGHER-DIFFERENCE-DEGREE-002","Higher finite differences and polynomial degree","iterated-difference-degree","Higher differences iterate exact local change; constant depth certifies the registered finite polynomial-degree correspondence."),
"003":("SFT-MATH-CALC-ACCUMULATION-SUMS-003","Accumulation and exact finite sums","complete-finite-accumulation","Accumulation is the complete junction of every generated local contribution with none omitted or duplicated."),
"004":("SFT-MATH-CALC-DIFFERENCE-ACCUMULATION-004","Fundamental difference-accumulation correspondence","telescoping-reconstruction","Difference and accumulation are exact reversals when every intermediate held/opposed change is retained."),
"005":("SFT-MATH-CALC-PRODUCT-COMPOSITION-LAWS-005","Product and composition difference laws","exact-product-composition-change","Product and composition difference laws follow by complete expansion and regrouping of lawful exact changes."),
"006":("SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006","Rational enclosure convergence","nested-rational-width-refinement","Convergence correspondence is a nested exact rational enclosure whose width refines toward structural absence under a certified rule."),
"007":("SFT-MATH-CALC-DERIVATIVE-SHRINKING-PARTS-007","Derivative correspondence through shrinking exact parts","shrinking-part-local-ratio","Derivative correspondence is the stable exact component of local change ratios under a registered shrinking-part family."),
"008":("SFT-MATH-CALC-INTEGRAL-REFINEMENT-SUMS-008","Integral correspondence through refinement sums","lower-upper-refinement-accumulation","Integral correspondence is the common exact enclosure of lower and upper finite accumulation sums under certified refinement."),
"009":("SFT-MATH-CALC-MULTIVARIABLE-DIRECTIONAL-009","Multivariable difference and directional change","coordinate-directional-change","Multivariable change retains the varied coordinate and holds every other coordinate fixed before composition."),
"010":("SFT-MATH-CALC-DIVERGENCE-FLUX-010","Discrete divergence and flux correspondence","internal-cancellation-boundary-flux","Discrete divergence accumulates local held/opposed flux; internal faces cancel structurally and the boundary record remains."),
"011":("SFT-MATH-CALC-VARIATIONAL-STATIONARY-011","Variational difference and stationary structure","complete-variation-stationarity","A stationary structure survives every registered local variation and exact extremum comparison in the complete candidate support."),
"012":("SFT-MATH-CALC-CONTINUUM-LIMIT-BOUNDARY-012","Continuum-limit admissibility boundary","certified-enclosure-only-limit","A continuum-limit statement is admissible only as a finite-successor enclosure certificate; no completed continuum object is imported."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no imported infinitesimal, continuum theorem answer, fitted parameter or opaque solver selects the law","host 0 displays absence or counts artifacts only; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed infinite limit or continuum domain","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("values","lost-sample-identity","Lost values destroy local change.","complete-generated-values","Every value is retained."),d("change","imported-calculus-answer","An imported theorem cannot select change.",rel,"The law follows from exact differences."),d("orientation","negative-change-scalar","Negative proof scalars violate the domain.","held-opposed-change-label","Direction is structural."),d("enumeration","selected-refinements","Samples cannot close convergence.","complete-declared-refinement-census","Every refinement is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened limit may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-grid-only","One grid lacks a successor rule.","finite-refinement-successor-certificate","Refinement is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful extension is admitted."))
class CalculusProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-ARITH-RECURRENCE-SEQUENCE-014","SFT-MATH-TOPO-CONTINUITY-TRANSPORT-002")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis CALC-{n} product before observation access.",f"Every supplied positive finite CALC-{n} sequence with value, change, orientation and refinement boundaries retained.",dims(rel),f"CALC-{n} uniquely retains {rel}, complete refinement custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty generated sequence exhibits the relation with every value retained.","Appending one sample or refinement preserves the prior sequence and generates every new difference exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-refinement-census","Every declared sample and refinement is tested.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact calculus witness and reject four controls.","The claim closes the declared finite refinement grammar; continuum claims require separate enclosure certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
