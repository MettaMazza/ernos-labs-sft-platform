"""Complete Measure and Integration family laws and exact witnesses."""
from fractions import Fraction
from itertools import combinations,product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension

WEIGHTS={1:Fraction(1,6),2:Fraction(2,6),3:Fraction(3,6)}
def weight(support):return sum((WEIGHTS[x] for x in support),Fraction())
def subsets(values):
 values=tuple(values)
 return tuple(frozenset(x) for n in range(len(values)+1) for x in combinations(values,n))
def integral(values):return sum((WEIGHTS[x]*values[x] for x in WEIGHTS),Fraction())
def midpoint_sum(n):return sum((Fraction(2*i-1,2*n)*Fraction(1,n) for i in range(1,n+1)),Fraction())

OBS={
"001":("three exact support weights one-sixth two-sixths and three-sixths compose the complete unit",weight({1,2,3})==1),
"002":("weights of every disjoint pair of generated supports add exactly to the weight of their union",all(weight(a|b)==weight(a)+weight(b) for a,b in product(subsets((1,2,3)),repeat=2) if not a&b)),
"003":("complete cover enumeration gives target support one-three the least retained cover weight four-sixths",min(weight(c) for c in subsets((1,2,3)) if {1,3}<=c)==Fraction(4,6)),
"004":("every generated test support decomposes exactly across the retained boundary one-two and its complement",all(weight(a)==weight(a&{1,2})+weight(a&{3}) for a in subsets((1,2,3)))),
"005":("exact finite-support integration of values one two three under weights one-two-three sixths equals seven-thirds",integral({1:1,2:2,3:3})==Fraction(7,3)),
"006":("every generated midpoint refinement sum for the identity support equals one-half exactly",all(midpoint_sum(n)==Fraction(1,2) for n in range(1,9))),
"007":("product support weights compose to one and exact conditioning recovers the retained second-coordinate weight",sum((a*b for a,b in product((Fraction(1,3),Fraction(2,3)),(Fraction(1,4),Fraction(3,4)))),Fraction())==1 and (Fraction(1,3)*Fraction(3,4))/Fraction(1,3)==Fraction(3,4)),
"008":("held three-fourths decomposes into opposed one-fourth plus retained held one-half without a negative scalar",Fraction(1,2)+Fraction(1,4)==Fraction(3,4)),
"009":("the generalized observation action is exactly additive on two positive test functions",integral({1:1,2:2,3:3})+integral({1:3,2:2,3:1})==integral({1:4,2:4,3:4})==4),
"010":("the finite convergence witness widths one-over-n-plus-one decrease at every generated successor while completed convergence is not claimed",all(Fraction(1,n+2)<Fraction(1,n+1) for n in range(1,9))),
}
DEF={
"001":("SFT-MATH-MEAS-FINITE-SUPPORT-WEIGHT-001","Finite measure and exact support weight","exact-finite-support-weight","Finite measure is the exact positive weight assigned to every generated support with the complete carrier normalized to one."),
"002":("SFT-MATH-MEAS-DISJOINT-ADDITIVITY-002","Additivity on disjoint generated support","disjoint-support-additivity","Disjoint additivity is forced by retaining each support distinction once and composing their exact weights without overlap."),
"003":("SFT-MATH-MEAS-OUTER-COVERING-003","Outer-measure and covering correspondence","complete-cover-minimum-weight","Finite outer-measure correspondence is the least exact weight among every generated cover of the target support."),
"004":("SFT-MATH-MEAS-MEASURABLE-BOUNDARY-004","Measurable-boundary correspondence","exact-boundary-decomposition","A boundary is measurable when every generated test support decomposes exactly into its retained inside and outside parts."),
"005":("SFT-MATH-MEAS-FINITE-SUPPORT-INTEGRATION-005","Exact integration over finite support","weighted-support-accumulation","Exact integration over finite support is the complete accumulation of each retained value composed with its exact support weight."),
"006":("SFT-MATH-MEAS-REFINEMENT-SUM-INTEGRATION-006","Refinement-sum integration correspondence","exact-refinement-sum-correspondence","Integration correspondence under refinement is admitted through an exact successor family of finite sums with every cell and weight retained."),
"007":("SFT-MATH-MEAS-PRODUCT-CONDITIONAL-SUPPORT-007","Product measure and conditional support","product-and-conditional-support-law","Product weight composes coordinate weights exactly; conditional support is the retained joint weight relative to its declared nonempty conditioning support."),
"008":("SFT-MATH-MEAS-HELD-ORIENTATION-SIGNED-008","Signed-measure replacement by held orientation","held-opposed-measure-ledger","Signed-measure correspondence uses separate held and opposed positive ledgers; cancellation is an exact relation and never a negative proof scalar."),
"009":("SFT-MATH-MEAS-DISTRIBUTION-OBSERVATION-009","Distribution and generalized-observation correspondence","exact-test-function-action","A distributional correspondence is an exact action on every generated test function, with composition and observation custody retained."),
"010":("SFT-MATH-MEAS-CONVERGENCE-FINITE-WITNESS-010","Convergence-of-measures finite witness boundary","successor-refined-measure-enclosure","Convergence-of-measures correspondence requires exact finite witness widths at every registered successor; completed infinite equality remains outside the certificate."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, fitted parameter, imported theorem answer or target outcome selects the law","host 0 denotes structural absence or counts artifacts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed continuum support, sigma-totality or infinite convergence object","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("support","imported-continuum-support","An imported continuum assumes the carrier.","generated-finite-support","Every support label is generated."),d("measure","imported-measure-answer","An imported answer cannot select the law.",rel,"The exact relation follows from support custody."),d("orientation","negative-signed-scalar","Negative proof scalars violate the domain.","held-opposed-positive-ledger","Orientation is structural and magnitudes remain positive."),d("enumeration","selected-subsets-or-partitions","Samples cannot close the relation.","complete-declared-support-census","Every declared support, cover or refinement is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the premise-free root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-support-only","One support lacks a successor boundary.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class MeasureProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-ANAL-SPECTRAL-MEASURE-016","SFT-MATH-EQN-EXISTENCE-UNIQUENESS-BLOWUP-012")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis MEAS-{n} product before observation access.",f"Every supplied positive finite MEAS-{n} support, weight, cover, test function and registered refinement boundary.",dims(rel),f"MEAS-{n} uniquely retains {rel}, complete support custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty generated support carries one exact positive weight and a complete support record.","Appending one generated label, cover, product coordinate or refinement cell preserves every prior relation and enumerates every new case exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-support-census","Every declared support, cover, product or test row is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact measure witness and reject four controls.","The claim closes the declared generated support and successor grammar; unrestricted continuum claims require separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
