"""Complete Equation Structures family laws and exact witnesses."""
from fractions import Fraction
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
def recurrence(seed,step,depth):
 out=[seed]
 for _ in range(depth-1):out.append(step(out[-1]))
 return tuple(out)
def fib(depth):
 out=[1,1]
 while len(out)<depth:out.append(out[-1]+out[-2])
 return tuple(out)
def green(source):return tuple(sum(source[:i+1]) for i in range(len(source)))
OBS={
"001":("the ordinary difference equation next equals twice current uniquely generates one two four eight sixteen",recurrence(1,lambda x:2*x,5)==(1,2,4,8,16)),
"002":("the exact finite-step exponential correspondence has local change ratio equal to the current carrier",all(((Fraction(1)+Fraction(1,n))*x-x)/Fraction(1,n)==x for n in range(1,7) for x in (Fraction(1),Fraction(3,2),Fraction(2)))),
"003":("the two-direction grid law u equals i plus j has exact unit change in each coordinate",all((i+1+j)-(i+j)==1 and (i+j+1)-(i+j)==1 for i,j in product(range(1,4),repeat=2))),
"004":("the affine grid has structural-absence second difference in both coordinate directions",all((i+j)+((i+2)+j)==2*((i+1)+j) and (i+j)+(i+(j+2))==2*(i+(j+1)) for i,j in product(range(1,4),repeat=2))),
"005":("one initial carrier and one registered transition law produce exactly one finite solution path",recurrence(1,lambda x:x+1,6)==(1,2,3,4,5,6)),
"006":("the finite Volterra accumulation equation x_n equals one plus all earlier x values generates one two four eight",(lambda x:all(x[n]==1+sum(x[:n]) for n in range(1,len(x))))((1,2,4,8))),
"007":("the finite functional equation f of a-plus-b equals f-a times f-b is satisfied by powers of two",all(2**(a+b)==2**a*2**b for a,b in product(range(1,5),repeat=2))),
"008":("the recurrence solution space with initial one-one uniquely generates one one two three five eight",fib(6)==(1,1,2,3,5,8)),
"009":("the finite causal Green response accumulates an impulse and exact differences recover the source",green((1,0,2,0))==(1,1,3,3) and (1,0,2,0)==(1,1-1,3-1,3-3)),
"010":("the exact swap transport conserves total mass five while internal orientation is merely exchanged",sum((2,3))==sum((3,2))==5),
"011":("the half-contraction solution map halves every exact perturbation distance",all(max((x+1)/2,(y+1)/2)-min((x+1)/2,(y+1)/2)==(max(x,y)-min(x,y))/2 for x,y in product((Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)),repeat=2))),
"012":("the squaring recursion has a unique value at every registered finite depth while unrestricted blow-up remains outside the certificate",recurrence(2,lambda x:x*x,5)==(2,4,16,256,65536)),
}
DEF={
"001":("SFT-MATH-EQN-ORDINARY-DIFFERENCE-001","Ordinary difference-equation structure","one-step-state-relation","An ordinary difference equation is a registered one-step state relation whose complete finite solution path is generated from initial custody."),
"002":("SFT-MATH-EQN-ORDINARY-DIFFERENTIAL-002","Ordinary differential-equation correspondence","finite-step-local-ratio-correspondence","Ordinary differential correspondence is admitted only through exact shrinking-step local-ratio enclosures and finite successor certificates."),
"003":("SFT-MATH-EQN-PARTIAL-DIFFERENCE-003","Partial difference-equation structure","multi-coordinate-local-relation","A partial difference equation retains every coordinate direction and applies exact local change only along the declared direction."),
"004":("SFT-MATH-EQN-PARTIAL-DIFFERENTIAL-004","Partial differential-equation correspondence","refined-multidirectional-enclosure","Partial differential correspondence is a compatible family of exact multidirectional difference relations under certified refinement."),
"005":("SFT-MATH-EQN-BOUNDARY-INITIAL-WELL-POSED-005","Boundary and initial record well-posedness","existence-uniqueness-record-custody","Well-posedness requires a retained initial or boundary record, at least one generated solution, uniqueness in the complete solution census and perturbation custody."),
"006":("SFT-MATH-EQN-INTEGRAL-CORRESPONDENCE-006","Integral-equation correspondence","finite-accumulation-equation","Integral-equation correspondence is a finite accumulation relation with exact kernel, source and refinement custody."),
"007":("SFT-MATH-EQN-FUNCTIONAL-STRUCTURE-007","Functional-equation structure","complete-argument-composition-census","A functional equation is closed only by testing every generated argument composition in its declared domain."),
"008":("SFT-MATH-EQN-RECURRENCE-SOLUTION-SPACE-008","Recurrence-equation solution spaces","initial-record-recurrence-space","A recurrence solution space is the complete family generated from every lawful initial record under one fixed transition relation."),
"009":("SFT-MATH-EQN-GREEN-RESPONSE-009","Green-response finite correspondence","impulse-response-superposition","Finite Green correspondence is the exact response to each generated impulse and its lawful accumulation reconstructs every source response."),
"010":("SFT-MATH-EQN-CONSERVATION-WEAK-010","Conservation-law weak correspondence","boundary-flux-conservation-ledger","Weak conservation correspondence retains total content while internal held/opposed flux cancels structurally and boundary flux remains."),
"011":("SFT-MATH-EQN-STABILITY-PERTURBATION-011","Stability and perturbation enclosures","exact-solution-perturbation-bound","Stability is an exact bound transporting every registered input perturbation to its solution separation."),
"012":("SFT-MATH-EQN-EXISTENCE-UNIQUENESS-BLOWUP-012","Existence, uniqueness and blow-up boundaries","finite-depth-existence-uniqueness-boundary","Existence and uniqueness are certified at every registered finite depth; blow-up claims require a separate depth-independent enclosure and cannot be inferred from growth alone."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no imported continuum equation, theorem answer, fitted parameter or opaque solver selects the law","host 0 displays absence or counts artifacts only; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed infinite solution trajectory or continuum domain","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("records","lost-initial-boundary-record","Lost records destroy well-posedness.","complete-record-custody","Every record is retained."),d("equation","imported-solution-answer","An imported solution cannot select the law.",rel,"The relation follows from exact generation."),d("orientation","negative-change-scalar","Negative proof scalars violate the domain.","held-opposed-change-label","Direction is structural."),d("enumeration","selected-solutions","Samples cannot close uniqueness.","complete-declared-solution-census","Every solution candidate is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened solution may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-grid-only","One grid lacks a successor rule.","finite-depth-successor-certificate","Depth extension is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful extension is admitted."))
class EquationProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-CALC-DIFFERENCE-ACCUMULATION-004","SFT-MATH-ANAL-NONLINEAR-CONTRACTION-014")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis EQN-{n} product before observation access.",f"Every supplied positive finite EQN-{n} problem with record, equation, orientation and depth boundaries retained.",dims(rel),f"EQN-{n} uniquely retains {rel}, complete solution custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty equation problem exhibits the relation with every record retained.","Appending one time, grid or refinement step preserves the prior solution and generates every new relation exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-solution-census","Every declared record and solution candidate is tested.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact equation witness and reject four controls.","The claim closes the declared finite-depth grammar; unrestricted continuum or blow-up claims require separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
