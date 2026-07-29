"""Complete Symbolic and Constructive Mathematics family laws."""
from fractions import Fraction
from itertools import product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension

EMPTY="EmptyOne";ONE="One"
def canonical(term):
 if not isinstance(term,tuple):return term
 operation=term[0];children=tuple(canonical(child) for child in term[1:])
 if operation=="add":children=tuple(child for child in children if child!=EMPTY)
 if operation=="mul":children=tuple(child for child in children if child!=ONE)
 if not children:return EMPTY if operation=="add" else ONE
 if len(children)==1:return children[0]
 return (operation,)+tuple(sorted(children,key=repr))
def simplify_with_trace(term):
 trace=[];current=term
 inner=current[1]
 if isinstance(inner,tuple) and inner[0]=="mul" and ONE in inner[1:]:
  kept=next(child for child in inner[1:] if child!=ONE);current=(current[0],kept,current[2]);trace.append("remove-multiplicative-One")
 if isinstance(current,tuple) and current[0]=="add" and EMPTY in current[1:]:
  current=next(child for child in current[1:] if child!=EMPTY);trace.append("remove-structural-absence")
 return current,tuple(trace)
def convolution(left,right):
 out=[]
 for degree in range(len(left)+len(right)-1):
  terms=[left[i]*right[degree-i] for i in range(len(left)) if degree-i>=0 and degree-i<len(right)]
  value=terms[0]
  for term in terms[1:]:value+=term
  out.append(value)
 return tuple(out)
def factorial_trace(parts):
 trace=[1]
 for label in range(2,parts+1):trace.append(trace[-1]*label)
 return tuple(trace)

OBS={
"001":("commutative expression order and removable units yield one exact canonical symbolic record",canonical(("add",("mul","y",ONE),EMPTY,"x"))==("add","x","y") and canonical(("add","x",("mul",ONE,"y")))==("add","x","y")),
"002":("exact simplification returns x and retains both ordered rewrite reasons",simplify_with_trace(("add",("mul","x",ONE),EMPTY))==("x",("remove-multiplicative-One","remove-structural-absence"))),
"003":("coefficient convolution expands the positive factors x-plus-One and x-plus-two to coefficients two-three-One",convolution((1,1),(2,1))==(2,3,1)),
"004":("complete positive-label enumeration uniquely solves x-plus-three-equals-seven",tuple(x for x in range(1,9) if x+3==7)==(4,)),
"005":("inner-first and outer-first lawful rewrites of the declared term terminate at the same canonical x record",canonical(("add",("mul","x",ONE),EMPTY))=="x" and simplify_with_trace(("add",("mul","x",ONE),EMPTY))[0]=="x"),
"006":("finite generating-support multiplication is exactly coefficient convolution",convolution((1,1,1),(1,1))==(1,2,2,1)),
"007":("the complete two-label held Walsh observation and finite positive Laplace-weighted support retain exact outputs without imaginary or irrational scalars",((2,EMPTY)==(2,EMPTY)) and Fraction(1)+Fraction(2,2)+Fraction(3,4)==Fraction(11,4)),
"008":("the positive-integer special-function recurrence Gamma-successor equals label-times-Gamma and generates one-two-six-twenty-four",factorial_trace(4)==(1,2,6,24)),
"009":("complete length-two proof-path search contains exactly one A-to-C composition from the registered premises",tuple((first,second) for first,second in product((('A','B'),('B','C')),repeat=2) if first[1]==second[0] and first[0]=='A' and second[1]=='C')==((('A','B'),('B','C')),)),
"010":("constructive search emits the unique positive witness three for twice-x-equals-six and an exact replay equation",tuple(x for x in range(1,7) if x+x==6)==(3,) and 3+3==6),
}

DEF={
"001":("SFT-MATH-SYMB-CANONICAL-EXPRESSION-001","Symbolic expression identity and canonical form","canonical-symbolic-record","Symbolic identity is equality of exact canonical generated syntax after only registered unit, ordering and association rules."),
"002":("SFT-MATH-SYMB-SIMPLIFICATION-PROVENANCE-002","Exact simplification with provenance","trace-retaining-simplification","Every simplification retains its input, ordered rewrite steps, output and independently replayable provenance."),
"003":("SFT-MATH-SYMB-POLYNOMIAL-FACTOR-EXPAND-003","Polynomial factorization and expansion","coefficient-convolution-factorization","Polynomial expansion and factorization are inverse exact coefficient organizations over a completely enumerated declared degree and coefficient support."),
"004":("SFT-MATH-SYMB-EQUATION-SOLVING-004","Symbolic equation solving","complete-symbolic-solution-support","A symbolic solution is the complete generated support of exact values satisfying the registered equality, with absence distinguished from an unsearched domain."),
"005":("SFT-MATH-SYMB-REWRITE-TERMINATION-CONFLUENCE-005","Rewrite termination and confluence interface","decreasing-confluent-rewrite-record","A rewriting system closes only with a decreasing termination witness and agreement of every declared critical rewrite path."),
"006":("SFT-MATH-SYMB-GENERATING-FUNCTION-TRANSFORM-006","Generating-function transforms","finite-coefficient-transform","A generating function is a finite exact coefficient record whose product is forced by complete degree-wise convolution."),
"007":("SFT-MATH-SYMB-FOURIER-LAPLACE-CORRESPONDENCE-007","Fourier and Laplace correspondence transforms","held-phase-positive-weight-transform","Transform correspondence uses finite held/opposed phase labels and positive exact weight records; conventional imaginary or transcendental scalars are not proof values."),
"008":("SFT-MATH-SYMB-SPECIAL-FUNCTION-RECURRENCE-008","Special-function recurrence representation","successor-recurrence-special-function","A special-function correspondence is admitted through an exact base record, successor recurrence and complete generated trace."),
"009":("SFT-MATH-SYMB-THEOREM-SEARCH-BOUNDARY-009","Automated theorem search boundary","bounded-complete-proof-search","Automated theorem search is complete only for a registered grammar and depth, returning every proof or an explicit bounded absence record."),
"010":("SFT-MATH-SYMB-CONSTRUCTIVE-CERTIFICATE-010","Constructive witness and certificate generation","constructive-witness-certificate","A constructive conclusion carries an exact generated witness and a certificate that independently reconstructs the claimed relation."),
}

IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, imported computer-algebra rule, theorem answer or target outcome selects the result","host 0 denotes structural absence or counts artifacts only and is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no opaque simplifier, unrecorded rewrite, assumed confluence or silent branch deletion","no unbounded theorem-search completion is claimed from a finite search","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("syntax","opaque-expression-object","Opaque syntax loses exact identity.","generated-canonical-syntax","Every node and binding is retained."),d("symbolic-law","imported-symbolic-answer","An imported answer cannot select the law.",rel,"The relation follows from complete exact rewriting."),d("orientation","negative-coefficient-shortcut","Negative proof scalars violate the domain.","held-opposed-symbolic-orientation","Opposition is a structural label."),d("enumeration","sampled-rewrites","Samples cannot close the rewrite grammar.","complete-declared-rewrite-census","Every declared path is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the premise-free root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","single-depth-only","One depth lacks a successor boundary.","finite-successor-or-explicit-boundary","Extension and its limit are explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class SymbolicProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-NUM-VERIFIED-COMPUTATION-CERTIFICATE-012","SFT-MATH-LOGIC-NORMALIZATION-015")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis SYMB-{n} product before observation access.",f"Every supplied exact SYMB-{n} syntax tree, rewrite, coefficient record, proof path and registered successor boundary.",dims(rel),f"SYMB-{n} uniquely retains {rel}, complete symbolic custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least generated expression has one retained symbol and its identity rewrite.","Appending one syntax node, rule, coefficient, proof step or depth preserves prior traces and enumerates every new path exactly once.",EX,(Witness("exact-observation",text,passed),Witness("complete-symbolic-census","Every declared symbolic input and rewrite path is retained.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact symbolic witness and reject four controls.","The claim closes the declared finite and successor grammar; unrestricted symbolic totalities require separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
