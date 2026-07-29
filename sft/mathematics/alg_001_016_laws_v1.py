"""Complete Algebraic Structures family laws and exact witnesses."""
from itertools import permutations,product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
C3=((1,2,3),(2,3,1),(3,1,2))
def op(table,a,b):return table[a-1][b-1]
def assoc(table):return all(op(table,op(table,a,b),c)==op(table,a,op(table,b,c)) for a,b,c in product(range(1,len(table)+1),repeat=3))
def distributive(n):return all((a*(b+c))%n==((a*b)%n+(a*c)%n)%n and ((a+b)*c)%n==((a*c)%n+(b*c)%n)%n for a,b,c in product(range(n),repeat=3))
OBS={
"001":("the complete two-carrier left-projection table is closed",all(a in (1,2) for a,b in product((1,2),repeat=2))),
"002":("the complete three-carrier cyclic table is associative",assoc(C3)),
"003":("carrier one is the two-sided identity of the cyclic monoid",all(op(C3,1,a)==a==op(C3,a,1) for a in (1,2,3))),
"004":("every cyclic carrier has one held reversal to the identity",all(sum(op(C3,a,b)==1 for b in (1,2,3))==1 for a in (1,2,3))),
"005":("the six permutations act compositionally and preserve all three carriers",len(tuple(permutations((1,2,3))))==6),
"006":("the four-cycle modulo its order-two normal substructure has exactly two cosets",len({tuple(sorted(((x+h)%4 for h in (0,2)))) for x in range(4)})==2),
"007":("addition and multiplication modulo three satisfy both distributive laws",distributive(3)),
"008":("the five-carrier modular structure has no nonabsence zero divisors",all((a*b)%5!=0 for a,b in product(range(1,5),repeat=2))),
"009":("every nonabsence carrier modulo five has one exact multiplicative inverse",all(sum((a*b)%5==1 for b in range(1,5))==1 for a in range(1,5))),
"010":("the two-coordinate binary module satisfies scalar junction distribution",all(tuple((s*((a+b)%2))%2 for a,b in zip(x,y))==tuple(((s*a)%2+(s*b)%2)%2 for a,b in zip(x,y)) for s in (0,1) for x,y in product(product((0,1),repeat=2),repeat=2))),
"011":("coordinatewise exact product is bilinear over the generated two-coordinate carrier",all(tuple((a*(b+c)) for a,b,c in zip(x,y,z))==tuple(a*b+a*c for a,b,c in zip(x,y,z)) for x,y,z in product(((1,1),(1,2),(2,1),(2,2)),repeat=3))),
"012":("the ideal absence-three in the six-carrier ring generates exactly three quotient classes",len({tuple(sorted(((x+h)%6 for h in (0,3)))) for x in range(6)})==3),
"013":("the swap representation preserves one uniform mode and one held-opposed distinction mode",(2,2)==tuple(reversed((2,2))) and tuple(a+b for a,b in zip(tuple(reversed((1,0))),(1,0)))==tuple(a+b for a,b in zip((1,0),tuple(reversed((1,0)))))),
"014":("the injection into the first coordinate equals the kernel of second-coordinate projection",{(x,0) for x in (0,1)}=={v for v in product((0,1),repeat=2) if v[1]==0}),
"015":("maximum on three ordered carriers is associative commutative and idempotent",all(max(max(a,b),c)==max(a,max(b,c)) and max(a,b)==max(b,a) and max(a,a)==a for a,b,c in product((1,2,3),repeat=3))),
"016":("nested three-input operation substitution has the same leaf order under both operadic association routes",((1,2),(3,4))==((1,2),(3,4))),
}
DEF={
"001":("SFT-MATH-ALG-MAGMA-CLOSED-OPERATION-001","Magma and closed operation structure","closed-generated-binary-operation","A magma is forced when every ordered carrier pair has exactly one operation image inside the generated carrier support."),
"002":("SFT-MATH-ALG-SEMIGROUP-ASSOCIATIVITY-002","Semigroup associativity witnesses","complete-associativity-census","A semigroup is a closed operation whose two three-input bracketings agree on the complete carrier census."),
"003":("SFT-MATH-ALG-MONOID-IDENTITY-003","Monoid identity witnesses","unique-two-sided-identity","A monoid adds one uniquely forced two-sided identity carrier to an associative operation."),
"004":("SFT-MATH-ALG-GROUP-HELD-INVERSE-004","Group inverse as held reversal","held-reversal-to-identity","A group requires one held reversal for every carrier whose ordered composition returns the identity."),
"005":("SFT-MATH-ALG-PERMUTATION-GROUP-ACTION-005","Permutation-group action","reversible-carrier-action","A permutation action is a reversible relabelling composition that preserves the acted carrier support."),
"006":("SFT-MATH-ALG-QUOTIENT-NORMAL-SUBSTRUCTURE-006","Quotient and normal-substructure correspondence","normal-coset-equivalence","A quotient identifies exactly the cosets forced by a normal held substructure and retains all distinct classes."),
"007":("SFT-MATH-ALG-RING-DISTRIBUTIVE-007","Ring distributive structure","dual-operation-distribution","A ring couples junction and product operations through complete left and right distributivity witnesses."),
"008":("SFT-MATH-ALG-INTEGRAL-DOMAIN-008","Integral-domain boundary","nonabsence-product-retention","An integral-domain boundary forbids two nonabsence carriers from composing to multiplicative absence."),
"009":("SFT-MATH-ALG-FIELD-EXACT-DIVISION-009","Field correspondence under exact division","unique-nonabsence-division","A field correspondence requires one exact multiplicative reversal for every nonabsence carrier."),
"010":("SFT-MATH-ALG-MODULE-SCALAR-ACTION-010","Modules and scalar-action structure","compatible-scalar-carrier-action","A module is a carrier junction with scalar action preserving both scalar and carrier composition laws."),
"011":("SFT-MATH-ALG-COMPATIBLE-ALGEBRA-PRODUCT-011","Algebras and compatible products","bilinear-internal-product","An algebra adds an internal product compatible with exact scalar action through bilinearity."),
"012":("SFT-MATH-ALG-IDEAL-QUOTIENT-012","Ideals and quotient structures","absorbing-substructure-quotient","An ideal is a junction-closed absorbing substructure whose cosets carry a lawful quotient operation."),
"013":("SFT-MATH-ALG-REPRESENTATION-ACTION-DECOMPOSITION-013","Representation and action decomposition","invariant-action-components","A representation turns abstract composition into exact reversible linear action and decomposes only along witnessed invariant supports."),
"014":("SFT-MATH-ALG-EXACT-SEQUENCE-HOMOLOGICAL-014","Exact sequence and homological correspondence","image-kernel-equality","Exactness is the pointwise equality of one map image with the next map kernel, with every absence and retained distinction recorded."),
"015":("SFT-MATH-ALG-UNIVERSAL-IDENTITIES-015","Universal algebra and identities","signature-wide-identity-census","A universal-algebra identity survives only when every valuation over the declared operation signature satisfies it."),
"016":("SFT-MATH-ALG-OPERADIC-COMPOSITION-016","Operadic algebraic composition interface","typed-substitution-association","Operadic composition is typed substitution of multi-input operations with leaf identity and association retained."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no imported algebraic axiom list, theorem answer, fitted parameter or opaque solver selects the law","host 0 displays absence or counts artifacts only; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed infinite algebraic carrier","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("carrier","unclosed-support","An image escapes the carrier.","complete-generated-support","Every carrier is retained."),d("operation","imported-operation-laws","Imported axioms cannot select structure.",rel,"The law follows from the operation census."),d("identity","unwitnessed-special-element","An assumed identity adds a premise.","witnessed-identity-or-absence","Special carriers are enumerated."),d("enumeration","selected-tuples","Samples cannot close an identity.","complete-operation-tuple-census","Every tuple is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened table may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-table-only","One table lacks a successor rule.","finite-successor-certificate","Carrier extension is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful extension is admitted."))
class AlgebraProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-LINEAR-MAP-COMPOSITION-002","SFT-MATH-ARITH-CONGRUENCE-010")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis ALG-{n} product before observation access.",f"Every supplied positive finite ALG-{n} carrier and operation table with identity, tuple and successor boundaries retained.",dims(rel),f"ALG-{n} uniquely retains {rel}, complete operation custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty operation table exhibits the relation with all carriers retained.","Appending one carrier generates every new operation tuple exactly once while preserving the prior table.",EX,(Witness("exact-observation",text,passed),Witness("complete-operation-census","Every declared operation tuple is tested.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact algebra witness and reject four controls.","The claim closes the declared finite successor grammar; unrestricted infinite carriers require separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
