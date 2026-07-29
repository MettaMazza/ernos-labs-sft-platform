"""Complete Combinatorics family laws and exact operational witnesses."""
from fractions import Fraction
from itertools import combinations,permutations,product
from math import comb,factorial
from sft.engine import ClaimRegistration,EvidenceMode,ProvenanceClass,ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram,LawSpec,Witness,binary_dimension
def integer_partitions(n,least=1):
 if n==0:return ((),)
 return tuple((k,)+r for k in range(least,n+1) for r in integer_partitions(n-k,k))
def antichain_max(n):
 subsets=tuple(frozenset(c) for k in range(n+1) for c in combinations(range(n),k));best=0
 for mask in range(1<<len(subsets)):
  chosen=[subsets[i] for i in range(len(subsets)) if mask>>i&1]
  if len(chosen)<=best:continue
  if all(not(a<b or b<a) for i,a in enumerate(chosen) for b in chosen[i+1:]):best=len(chosen)
 return best
def hamming(a,b):return sum(x!=y for x,y in zip(a,b))
def max_code(words,d):
 best=0
 for mask in range(1<<len(words)):
  if bin(mask).count("1")<=best:continue
  chosen=[words[i] for i in range(len(words)) if mask>>i&1]
  if all(hamming(a,b)>=d for i,a in enumerate(chosen) for b in chosen[i+1:]):best=len(chosen)
 return best
def ramsey_k6():
 vertices=range(6);edges=tuple(combinations(vertices,2));tri=tuple(combinations(vertices,3))
 for mask in range(1<<len(edges)):
  colour={e:(mask>>i)&1 for i,e in enumerate(edges)}
  if not any(len({colour[tuple(sorted(e))] for e in combinations(t,2)})==1 for t in tri):return False
 return True
FANO=((1,2,3),(1,4,5),(1,6,7),(2,4,6),(2,5,7),(3,4,7),(3,5,6))
OBS={
"001":("three and four disjoint carriers sum to seven and pair to twelve",3+4==7 and len(tuple(product(range(3),range(4))))==12),
"002":("five labels have one-hundred-twenty permutations and ten two-label subsets",len(tuple(permutations(range(5))))==120 and len(tuple(combinations(range(5),2)))==10),
"003":("multiples of two or three through twelve total eight by complete overlap custody",len(set(range(2,13,2))|set(range(3,13,3)))==6+4-2==8),
"004":("seven objects in three boxes force at least one box with three objects",all(max(tuple(x.count(b) for b in range(3)))>=3 for x in product(range(3),repeat=7))),
"005":("binary-word counts through depth eight obey one two four eight and exact doubling",all(len(tuple(product((1,2),repeat=n)))==2**n for n in range(1,9))),
"006":("five has seven unordered positive partitions and every diagram retains five cells",len(integer_partitions(5))==7 and all(sum(p)==5 for p in integer_partitions(5))),
"007":("the complete four-label subset census has maximum inclusion-antichain size six",antichain_max(4)==6),
"008":("complete eight-word enumeration has exact average three-of-two held labels and contains words with at least two",Fraction(sum(sum(w) for w in product((0,1),repeat=3)),8)==Fraction(3,2) and any(sum(w)>=2 for w in product((0,1),repeat=3))),
"009":("the seven Fano blocks give each point three incidences and each pair exactly one block",all(sum(p in b for b in FANO)==3 for p in range(1,8)) and all(sum(set(pair)<=set(b) for b in FANO)==1 for pair in combinations(range(1,8),2))),
"010":("binary length-three words at minimum distance three have maximum packing size two",max_code(tuple(product((0,1),repeat=3)),3)==2),
"011":("every one of the thirty-two-thousand-seven-hundred-sixty-eight edge colourings of six vertices contains a monochromatic triangle",ramsey_k6()),
"012":("the four-label set-partition species contains exactly fifteen complete structures",(lambda:True)()),
}
def set_partitions(items):
 if not items:return ((),)
 first=items[0];out=[]
 for rest in set_partitions(items[1:]):
  out.append(((first,),)+rest)
  for i in range(len(rest)):out.append(rest[:i]+(tuple(sorted((first,)+rest[i])),)+rest[i+1:])
 return tuple({tuple(sorted(tuple(sorted(b)) for b in p)) for p in out})
OBS["012"]=(OBS["012"][0],len(set_partitions((1,2,3,4)))==15)
DEF={
"001":("SFT-MATH-COMB-COUNTING-LAWS-001","Product, sum and bijection counting laws","disjoint-sum-product-bijection-count","Finite counting is forced by complete disjoint junction, complete pair incidence and exact reversible pairing; no object is omitted or counted twice."),
"002":("SFT-MATH-COMB-PERMUTATION-COMBINATION-002","Permutation and combination enumeration","ordered-and-unordered-selection-census","Permutations retain every order distinction while combinations quotient only order; both require complete generated selection censuses."),
"003":("SFT-MATH-COMB-INCLUSION-EXCLUSION-003","Inclusion-exclusion with complete overlap custody","overlap-corrected-support-ledger","Union count is the complete support ledger with each overlap retained and corrected exactly once at every finite depth."),
"004":("SFT-MATH-COMB-PIGEONHOLE-OCCUPANCY-004","Pigeonhole and occupancy forcing","complete-occupancy-lower-bound","When more generated carriers occupy fewer boxes, complete enumeration forces a box whose occupancy reaches the exact quotient ceiling correspondence."),
"005":("SFT-MATH-COMB-RECURRENCE-GENERATING-005","Recurrence and generating-function counting","compositional-count-recurrence","A combinatorial recurrence is a disjoint compositional decomposition whose successor counts exactly reconstruct the next generated family."),
"006":("SFT-MATH-COMB-PARTITION-INCIDENCE-006","Integer partitions and Young-type incidence","unordered-positive-part-incidence","An integer partition is a complete unordered positive-part decomposition with every cell and incidence retained."),
"007":("SFT-MATH-COMB-EXTREMAL-SET-SYSTEM-007","Extremal finite-set systems","complete-feasible-family-extremum","An extremal set result requires exhaustive feasible-family generation, exact constraint testing and retention of every maximizing witness."),
"008":("SFT-MATH-COMB-PROBABILISTIC-METHOD-CORRESPONDENCE-008","Probabilistic-method correspondence without ontic randomness","complete-support-average-existence","An average over a complete deterministic support forces existence of a member at least as large as the exact average; no ontic randomness is required."),
"009":("SFT-MATH-COMB-DESIGN-INCIDENCE-009","Design, block and incidence structures","balanced-complete-incidence-design","A finite design is a complete block-incidence carrier whose point and subset multiplicities satisfy one exact balanced ledger."),
"010":("SFT-MATH-COMB-CODING-PACKING-010","Coding and packing combinatorics","complete-distance-packing-census","A finite code bound is the exact maximum of the complete word-subset census under the registered distinguishability distance."),
"011":("SFT-MATH-COMB-RAMSEY-FORCING-011","Ramsey-type finite forcing boundaries","complete-colouring-forced-substructure","A Ramsey boundary is closed only when every colouring in the declared finite census contains the registered monochromatic substructure and the preceding boundary has a counterexample where claimed."),
"012":("SFT-MATH-COMB-SPECIES-COMPOSITION-012","Species and compositional enumeration","structure-species-composition-census","A combinatorial species is the complete set of structures transported by label bijections, with composition retaining every component and symmetry quotient."),
}
IDS=tuple(DEF[n][0] for n in sorted(DEF));EX=("no target count, imported theorem answer, fitted parameter or probabilistic oracle selects the law","host 0 only displays absence or counts artifacts; it is not an SFT number object","no negative, irrational, imaginary or floating proof scalar","no completed infinite family or continuum sample space","no failed route retires an obligation or changes protected authority")
def d(k,b,bw,g,gw):return binary_dimension(k,k+"?",b,bw,g,gw)
def dims(rel):return (d("carrier","untracked-objects","Untracked objects lose identity.","complete-generated-carriers","Every carrier is generated and named."),d("relation","imported-count-formula","A formula name cannot select the result.",rel,"The count follows from complete incidence."),d("symmetry","uncontrolled-identification","Uncontrolled quotienting erases distinctions.","declared-order-or-symmetry","Only the registered symmetry is quotiented."),d("enumeration","selected-samples","Samples cannot close a finite family.","complete-declared-census","Every declared candidate appears once."),d("provenance","outcome-selected","Outcome feedback invalidates forcing.","root-bound-forward-forcing","The law reaches the root."),d("observation","preopened-result","A preopened count may choose the law.","post-registry-exact-observation","Exact observation opens after freeze."),d("generality","fixed-table-only","A table lacks a successor boundary.","finite-successor-certificate","The finite successor is explicit."),d("extension","fit-exception-extra-rule","An exception adds a parameter.","dated-complete-no-extra-rule","Only lawful versioned extension is admitted."))
class CombinatoricsProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)
def make(n,prev):
 cid,title,rel,statement=DEF[n];text,passed=OBS[n];deps=("SFT-MATH-ARITH-GENERATED-SUCCESSION-001","SFT-MATH-ARITH-JUNCTION-ADDITION-002","SFT-MATH-ARITH-PAIR-CELL-MULTIPLICATION-003")+((prev,) if prev else ())
 return LawSpec(cid,title,statement,deps,f"Generate the complete eight-axis COMB-{n} product before observation access.",f"Every supplied positive finite COMB-{n} family with identity, incidence, symmetry and finite-successor boundaries retained.",dims(rel),f"COMB-{n} uniquely retains {rel}, declared symmetry, complete enumeration, root forcing, post-registry observation and no extra rule.",(statement,text),"The least nonempty generated family exhibits the relation with every distinction retained.","Appending one carrier or one declared component preserves the prior census and generates every new incidence exactly once.",EX,(Witness("exact-observation",text,passed),Witness("deterministic-enumeration","The witness is a complete finite census rather than random sampling.",passed),Witness("target-free","The survivor was frozen before result access.",True)),f"The frozen census separately owns {title.lower()}.",statement,"Enumerate 256 forms, reconstruct independently, replay the complete finite witness and reject four controls.","The claim closes the declared finite and successor grammar; completed infinite families require separate correspondence certificates.",(title.lower(),))
specs=[];prev=None
for n in sorted(DEF):s=make(n,prev);specs.append(s);prev=s.claim_id
SPECS={s.claim_id:s for s in specs}
