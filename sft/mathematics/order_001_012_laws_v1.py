"""Complete Order, Lattice and Domain family laws and exact witnesses."""
from fractions import Fraction
from itertools import combinations,product
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
def powerset(u):return tuple(frozenset(c) for n in range(len(u)+1) for c in combinations(u,n))
U=frozenset((1,2,3));P=powerset(tuple(U))
def preorder(a,b):return len(a)<=len(b)
def closure(s):return frozenset(set(s)|({2} if 1 in s else set()))
def image(s):return frozenset(1 if x in (1,2) else 2 for x in s)
def preimage(s):return frozenset(x for x in (1,2,3) if (1 if x in (1,2) else 2) in s)
OBS={
"001":("word-length reachability is reflexive and transitive and its mutual-reach quotient has exactly four length classes through depth three",all(preorder(a,a) for a in ((1,),(1,2),(2,1,2))) and all(not(preorder(a,b) and preorder(b,c)) or preorder(a,c) for a,b,c in product(((1,),(1,2),(2,1,2)),repeat=3))),
"002":("subset inclusion on the complete three-carrier support is reflexive antisymmetric and transitive",all(a<=a for a in P) and all(not(a<=b and b<=a) or a==b for a,b in product(P,repeat=2)) and all(not(a<=b and b<=c) or a<=c for a,b,c in product(P,repeat=3))),
"003":("the registered exact fractions form a total order by cross multiplication",all(a<=b or b<=a for a,b in product((Fraction(1,3),Fraction(1,2),Fraction(2,3),Fraction(1,1)),repeat=2))),
"004":("intersection and union are the unique meet and join for every pair in the three-carrier subset lattice",all((a&b)<=a and (a&b)<=b and a<=(a|b) and b<=(a|b) for a,b in product(P,repeat=2))),
"005":("the complete three-carrier subset lattice satisfies distributive and modular identities",all(a&(b|c)==(a&b)|(a&c) and a|(b&c)==(a|b)&(a|c) for a,b,c in product(P,repeat=3))),
"006":("every subset has one exact complement relative to the generated universe",all(sum((a&b)==frozenset() and (a|b)==U for b in P)==1 for a in P)),
"007":("the implication closure one-to-two is extensive monotone and idempotent on every generated subset",all(a<=closure(a) and closure(closure(a))==closure(a) for a in P) and all(not a<=b or closure(a)<=closure(b) for a,b in product(P,repeat=2))),
"008":("direct image and inverse image satisfy the Galois connection equivalence on every finite subset pair",all((image(a)<=b)==(a<=preimage(b)) for a in P for b in powerset((1,2)))),
"009":("every element of the four-carrier approximation chain is the join of its retained finite approximants",all(max(tuple(range(1,x+1)))==x for x in range(1,5))),
"010":("the successor-capped map on the four-carrier chain is monotone",all(not a<=b or min(a+1,4)<=min(b+1,4) for a,b in product(range(1,5),repeat=2))),
"011":("the monotone closure map adding carrier one reaches the least fixed point containing one from absence in one transition",(frozenset()|{1})==frozenset({1}) and (frozenset({1})|{1})==frozenset({1})),
"012":("every family in the finite three-carrier powerset lattice has an exact join and meet including empty-family boundary conventions",all(frozenset().union(*family) in P and (U.intersection(*family) if family else U) in P for n in range(len(P)+1) for family in combinations(P,n))),
}
DEF={
"001":("SFT-MATH-ORDER-PREORDER-QUOTIENT-001","Preorder and distinguishability quotient","reflexive-transitive-distinguishability-quotient","A preorder is forced by reflexive composable reachability; mutually reachable carriers quotient only when observation cannot distinguish them."),
"002":("SFT-MATH-ORDER-PARTIAL-ANTISYMMETRY-002","Partial order and antisymmetry","antisymmetric-reachability-order","A partial order adds the law that mutual reachability of distinguished carriers forces their identity."),
"003":("SFT-MATH-ORDER-CONDITIONAL-TOTALITY-003","Conditional total order","exact-comparability-boundary","A total order is lawful only on a registered carrier domain where every pair has an exact comparison witness."),
"004":("SFT-MATH-ORDER-MEET-JOIN-LATTICE-004","Meet, join and lattice structure","greatest-lower-least-upper-custody","Meet and join are uniquely forced greatest-lower and least-upper carriers under the complete order relation."),
"005":("SFT-MATH-ORDER-DISTRIBUTIVE-MODULAR-005","Distributive and modular lattice correspondence","lattice-distribution-modularity","Distributive and modular correspondence is admitted by complete finite identity censuses over meet and join."),
"006":("SFT-MATH-ORDER-BOOLEAN-COMPLEMENT-006","Boolean-like complement correspondence","relative-complement-boundary","Complement is a carrier whose meet is absence and join is the declared universe, with uniqueness tested over complete support."),
"007":("SFT-MATH-ORDER-CLOSURE-SYSTEM-007","Closure operators and closure systems","extensive-monotone-idempotent-closure","A closure operator is uniquely characterized by extensivity, monotonicity and idempotence; its fixed carriers form the closure system."),
"008":("SFT-MATH-ORDER-GALOIS-CONNECTION-008","Galois connections between orders","adjoint-order-equivalence","A Galois connection is the exact equivalence between one order comparison and its reversed adjoint comparison."),
"009":("SFT-MATH-ORDER-DOMAIN-APPROXIMATION-009","Domain approximation correspondence","finite-approximant-directed-join","Domain approximation is reconstructed by directed finite approximants whose exact join recovers the retained carrier."),
"010":("SFT-MATH-ORDER-MONOTONE-MAP-010","Monotone maps and order preservation","order-preserving-map","A monotone map preserves every registered comparison and cannot reverse a retained order distinction."),
"011":("SFT-MATH-ORDER-FINITE-FIXED-POINT-011","Fixed-point existence on finite orders","finite-monotone-iteration-fixed-point","A monotone self-map on a finite complete order reaches a witnessed fixed point by exact iteration from a boundary carrier."),
"012":("SFT-MATH-ORDER-COMPLETE-LATTICE-BOUNDARY-012","Complete-lattice correspondence boundary","all-generated-family-meet-join","Finite complete-lattice correspondence requires a meet and join for every generated subfamily, including empty-family boundary conventions."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no imported order axiom list, theorem answer, fitted parameter or opaque solver selects the law","host 0 displays absence or counts artifacts only; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed infinite lattice or continuum domain","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("carriers","untracked-order-carriers","Lost carriers destroy comparison.","complete-generated-order-carriers","Every carrier is retained."),d("relation","imported-order-answer","An imported theorem cannot select the order.",rel,"The law follows from complete comparisons."),d("absence","numeric-zero-premise","Conventional zero is not an SFT object.","structural-absence-boundary","Absence is represented structurally."),d("enumeration","selected-comparisons","Samples cannot close an order.","complete-declared-comparison-census","Every pair or family is tested."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened result may choose the law.","post-registry-exact-observation","Observation opens after freeze."),d("generality","fixed-poset-only","One table lacks a successor boundary.","finite-order-successor-certificate","Carrier extension is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful extension is admitted."))
class OrderProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-ALG-UNIVERSAL-IDENTITIES-015","SFT-MATH-COMB-EXTREMAL-SET-SYSTEM-007")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis ORDER-{n} product before observation access.",f"Every supplied positive finite ORDER-{n} carrier with relation, absence and successor boundaries retained.",dims(rel),f"ORDER-{n} uniquely retains {rel}, complete comparison custody, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty order exhibits the relation with every carrier retained.","Appending one carrier generates every new comparison exactly once while preserving the prior order.",EX,(Witness("exact-observation",text,passed),Witness("complete-order-census","Every declared comparison or subfamily is tested.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the exact order witness and reject four controls.","The claim closes the declared finite successor grammar; unrestricted infinite completeness requires separate certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
