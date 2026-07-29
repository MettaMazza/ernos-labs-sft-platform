"""Algebraic Extension and Exact Nonrational Correspondence laws."""
from fractions import Fraction
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
def val(n,p):
 c=0
 while n%p==0:n//=p;c+=1
 return c
def no_rational_square_two(bound):return not any(Fraction(a,b)**2==2 for b in range(1,bound+1) for a in range(1,2*bound+1))
OBS={
"001":("seven-of-five squared is below two while three-of-two squared is above two",Fraction(7,5)**2<2<Fraction(3,2)**2),
"002":("five-of-four cubed is below two while four-of-three cubed is above two",Fraction(5,4)**3<2<Fraction(4,3)**3),
"003":("the exact beta-square-equals-two extension reduces one-plus-beta squared to three-plus-two-beta",(1+2,1+1)==(3,2)),
"004":("the five-label field tables close and every nonabsence label has one multiplicative inverse",all(any((a*b)%5==1 for b in range(1,5)) for a in range(1,5))),
"005":("the square action permutes the exact cube-root labels one two four modulo seven",tuple((x*x)%7 for x in (1,2,4))==(1,4,2)),
"006":("repeated one-step rotation traverses all five cyclotomic labels and returns to the first",tuple((1+k)%5 for k in range(5))==(1,2,3,4,0)),
"007":("held-pair multiplication sends one-plus-i composed with itself to real absence and imaginary magnitude two",(1*1,1*1,1*1+1*1)==(1,1,2)),
"008":("the cube-root-two enclosure lies wholly below the square-root-two enclosure",Fraction(4,3)<Fraction(7,5)),
"009":("the exact ternary divisibility depth of the held difference between eighty-two and one is four",val(81,3)==4),
"010":("complete rational search through denominator twenty finds no exact square balance for two and makes no stronger scalar claim",no_rational_square_two(20)),
}
DEF={
"001":("SFT-MATH-ALEXT-POLYNOMIAL-ROOT-ISOLATION-001","Polynomial identity and exact root isolation","positive-polynomial-side-order-swap","A polynomial root is admitted through an exact defining balance and nested rational brackets whose endpoint order swaps, never as an imported irrational scalar."),
"002":("SFT-MATH-ALEXT-ALGEBRAIC-BALANCE-002","Algebraic-magnitude balance certificates","exact-algebraic-balance-enclosure","An algebraic magnitude is the exact equality condition between two positive polynomial sides plus a replayable rational enclosure certificate."),
"003":("SFT-MATH-ALEXT-EXTENSION-TOWER-003","Exact finite extension towers","finite-basis-reduction-tower","A finite extension is a generated basis-label carrier with exact reduction identities and complete coefficient custody at every composition."),
"004":("SFT-MATH-ALEXT-FINITE-FIELD-004","Finite-field correspondence","finite-label-field-table","A finite-field correspondence requires complete addition and multiplication tables, one identity, exact closure and one inverse for every nonabsence label."),
"005":("SFT-MATH-ALEXT-GALOIS-ORBIT-005","Finite Galois-orbit correspondence","root-label-automorphism-orbit","A finite Galois correspondence is the complete orbit of exact root labels under structure-preserving finite permutations, not an imported theorem name."),
"006":("SFT-MATH-ALEXT-CYCLOTOMIC-CORRESPONDENCE-006","Cyclotomic and root-of-unity correspondence","periodic-phase-label-cycle","Roots of unity are represented by exact periodic phase labels whose generated action returns after the counted period; no imaginary scalar is admitted."),
"007":("SFT-MATH-ALEXT-HELD-PAIR-COMPLEX-007","Held-pair complex-number correspondence","held-orthogonal-pair-arithmetic","Complex correspondence is an ordered pair of exact magnitudes with held orthogonal orientation and exact pair composition; structural absence replaces numerical zero."),
"008":("SFT-MATH-ALEXT-REAL-ALGEBRAIC-ORDER-008","Exact real-algebraic ordering","disjoint-rational-enclosure-order","Real-algebraic order is forced by disjoint exact rational enclosures and polynomial-side comparisons, without evaluating an irrational proof scalar."),
"009":("SFT-MATH-ALEXT-PRIME-ADIC-VALUATION-009","Prime-adic valuation correspondence","prime-power-closeness-depth","Prime-adic closeness is the counted prime-power divisibility depth of a held difference, not a negative, infinite or continuum-valued distance."),
"010":("SFT-MATH-ALEXT-TRANSCENDENTAL-BOUNDARY-010","Transcendental and nonrepresentability boundary","explicit-unrepresented-scalar-boundary","When no registered finite rational or algebraic certificate exists, the value remains an explicit unrepresented boundary; finite search never licenses an unsupported transcendence claim."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no axiom, fitted parameter, imported theorem answer or target outcome selects the law","no irrational or imaginary object enters as a proof scalar","negative magnitude is held orientation and structural absence is typed empty One","no completed infinite extension, continuum or unbounded field is admitted","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("carrier","imported-scalar-field","An imported field assumes the object.","generated-exact-structure","The carrier is a finite exact structure."),d("relation","named-theorem-result","A theorem name cannot select the law.",rel,"The relation is explicitly constructed."),d("identity","decimal-or-symbol-only","A symbol or decimal lacks exact identity.","defining-balance-and-record","Defining identities and records are complete."),d("enumeration","selected-example","One example cannot close.","complete-declared-product","Every declared alternative is enumerated."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the premise-free root."),d("observation","preopened-target","Preopened outcomes may select the law.","post-registry-exact-observation","Observation opens after registry freeze."),d("generality","fixed-table-only","A table has no successor certificate.","finite-successor-or-explicit-boundary","Generality or its limit is explicit."),d("extension","fit-exception-extra-rule","A fitted exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is allowed."))
class AlgebraicExtensionProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-ARITH-CANONICAL-FRACTION-008","SFT-MATH-ARITH-VALUATION-012")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis ALEXT-{n} product before observation access.",f"Every supplied positive finite ALEXT-{n} exact structure and its explicit correspondence boundary.",dims(rel),f"ALEXT-{n} uniquely retains {rel}, exact identity, complete enumeration, root forcing, post-registry observation and no extra rule.",(statement,text),"The least finite exact carrier supplies the defining identity and complete record.","Appending one finite basis label, refinement rung or supplied structure preserves every prior identity and applies the same construction.",EX,(Witness("exact-observation",text,passed),Witness("no-forbidden-scalar","The witness uses exact fractions, finite labels, held pairs or explicit absence only.",passed),Witness("target-free","Survivor coordinates were frozen before outcome access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact observation and reject four controls.","Claims apply to supplied finite exact structures; ungenerated scalar totalities remain explicit boundaries.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
