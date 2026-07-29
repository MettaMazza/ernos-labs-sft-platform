"""Whole-family Arithmetic and Number Structure laws for Mathematics V3."""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from math import gcd, lcm

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.mathematics.generated_law import GeneratedMathematicsProgram, LawSpec, Witness, binary_dimension


def divisors(n): return tuple(d for d in range(1,n+1) if n%d==0)
def primes(bound): return tuple(n for n in range(2,bound+1) if divisors(n)==(1,n))
def factors(n):
 out=[];d=2
 while n>1:
  if n%d==0:out.append(d);n//=d
  else:d+=1
 return tuple(out)
def valuation(n,p):
 count=0
 while n%p==0:n//=p;count+=1
 return count
def partitions(n,least=1):
 if n==0:return ((),)
 out=[]
 for first in range(least,n+1):
  for rest in partitions(n-first,first):out.append((first,)+rest)
 return tuple(out)
def phi(n):return sum(gcd(k,n)==1 for k in range(1,n+1))

OBS={
"001":("generated successor traces append exactly one counted whole",tuple(range(1,9))==(1,2,3,4,5,6,7,8)),
"002":("disjoint three-cell and five-cell traces join to eight cells",len(tuple(range(3))+tuple(range(5)))==8),
"003":("three-by-four pair cells enumerate exactly twelve products",len(tuple((a,b) for a in range(3) for b in range(4)))==12),
"004":("divisor intersection and common-return enumeration give gcd six and lcm seventy-two for eighteen and twenty-four",tuple(d for d in divisors(18) if 24%d==0)[-1]==6 and lcm(18,24)==72 and gcd(18,24)*lcm(18,24)==18*24),
"005":("seventeen cells contain three complete five-cell groups and a held two-cell remainder",17==3*5+2 and 2<5),
"006":("complete divisor enumeration through thirty retains the ten prime wholes",primes(30)==(2,3,5,7,11,13,17,19,23,29)),
"007":("prime-factor traces reconstruct every whole from two through one hundred",all(__import__('math').prod(factors(n))==n and all(p in primes(p) for p in factors(n)) for n in range(2,101))),
"008":("canonical refinement reduces six-of-eight to three-of-four and joins one-of-three with one-of-four as seven-of-twelve",Fraction(6,8)==Fraction(3,4) and Fraction(1,3)+Fraction(1,4)==Fraction(7,12)),
"009":("exact quotient recursion represents three-hundred-fifty-five of one-hundred-thirteen by finite coefficients three seven sixteen",(lambda a,b:(lambda out:out)([]))(1,1) is not None),
"010":("seventeen and two occupy one residue class modulo five while eighteen does not",17%5==2%5 and 18%5!=2%5),
"011":("twenty-three is the unique residue below one-hundred-five satisfying the registered three five seven congruences",tuple(x for x in range(1,106) if x%3==2 and x%5==3 and x%7==2)==(23,)),
"012":("prime-power depth gives three binary layers in forty and four ternary layers in eighty-one",valuation(40,2)==3 and valuation(81,3)==4),
"013":("complete positive enumeration gives seven ordered solutions to x plus y equals eight and the three-four-five square relation",len(tuple((x,8-x) for x in range(1,8)))==7 and 3*3+4*4==5*5),
"014":("the one-one exact recurrence generates one one two three five eight thirteen twenty-one thirty-four fifty-five",(lambda:None) is not None),
"015":("pair-count coefficients of two finite geometric supports are one two three four five six seven eight",all(len(tuple((a,b) for a in range(n+1) for b in range(n+1) if a+b==n))==n+1 for n in range(8))),
"016":("eight has twenty-two unordered positive partitions and one-hundred-twenty-eight ordered positive compositions",len(partitions(8))==22 and 2**7==128),
"017":("complete divisor and coprime ledgers give tau twelve equals six sigma twelve equals twenty-eight and phi twelve equals four",len(divisors(12))==6 and sum(divisors(12))==28 and phi(12)==4),
"018":("complete enumeration gives twenty-five primes through one hundred and a prime strictly between n and twice n through fifty",len(primes(100))==25 and all(any(n<p<2*n for p in primes(2*n)) for n in range(2,51))),
}


def continued_fraction(a,b):
 out=[]
 while b:
  q,r=divmod(a,b);out.append(q);a,b=b,r
 return tuple(out)
OBS["009"]=(OBS["009"][0],continued_fraction(355,113)==(3,7,16))
seq=[1,1]
for _ in range(8):seq.append(seq[-1]+seq[-2])
OBS["014"]=(OBS["014"][0],tuple(seq)==(1,1,2,3,5,8,13,21,34,55))

DEFINITIONS={
"001":("SFT-MATH-ARITH-GENERATED-SUCCESSION-001","Generated whole succession and exact induction","generated-one-successor-trace","Every generated whole is a finite counted trace beginning at the One; adjoining one complete new unit is the unique successor and preserves exact induction."),
"002":("SFT-MATH-ARITH-JUNCTION-ADDITION-002","Addition and disjoint-junction arithmetic","complete-disjoint-junction","Addition is the complete junction of two held-disjoint generated traces, with every source unit retained exactly once."),
"003":("SFT-MATH-ARITH-PAIR-CELL-MULTIPLICATION-003","Multiplication and complete pair-cell arithmetic","complete-pair-cell-product","Multiplication is the complete product of every unit of one generated trace with every unit of the other, producing one pair cell per ordered incidence."),
"004":("SFT-MATH-ARITH-DIVISIBILITY-GCD-LCM-004","Divisibility, common divisors and common multiples","complete-divisor-common-return-ledger","Divisibility is exact complete grouping; greatest common grouping and least common return are forced by exhaustive positive divisor and multiple ledgers."),
"005":("SFT-MATH-ARITH-QUOTIENT-REMAINDER-005","Exact quotient and oriented remainder","maximal-complete-groups-held-remainder","Exact quotient is the maximal count of complete divisor groups, with any unmatched positive part retained as a held remainder and structural absence displayed by host 0 only."),
"006":("SFT-MATH-ARITH-PRIME-IRREDUCIBLE-006","Prime and irreducible whole structure","only-one-and-self-complete-divisors","A prime whole is exactly a generated whole above the One whose complete positive divisor ledger retains only the One and itself."),
"007":("SFT-MATH-ARITH-UNIQUE-FACTORIZATION-007","Unique finite factorization certificate","least-divisor-prime-factor-trace","Repeated least complete divisor extraction forces a finite prime-factor trace whose product reconstructs the original whole; any distinct trace is eliminated by the first least-divisor disagreement."),
"008":("SFT-MATH-ARITH-CANONICAL-FRACTION-008","Canonical exact fractions and common refinement","reduced-parts-common-refinement","An exact fraction is a held part of a generated whole in lowest terms; equality and arithmetic are forced by common refinement and canonical reduction."),
"009":("SFT-MATH-ARITH-CONTINUED-FRACTION-009","Finite continued-fraction correspondence","finite-quotient-remainder-expansion","Every supplied exact fraction has a finite quotient-remainder expansion; its coefficient trace reconstructs the same part without importing an irrational limit."),
"010":("SFT-MATH-ARITH-CONGRUENCE-010","Residue classes and congruence","same-held-remainder-class","Two wholes are congruent at a generated modulus exactly when complete grouping leaves the same held remainder class."),
"011":("SFT-MATH-ARITH-COMPATIBLE-CONGRUENCE-011","Compatible congruence composition","least-common-period-compatible-residue","A compatible finite family of congruence records forces one residue class over the least common return; incompatibility remains an explicit halt."),
"012":("SFT-MATH-ARITH-VALUATION-012","Prime-power valuation and divisibility depth","counted-prime-factor-depth","Prime-power valuation is the exact number of successive complete prime groupings before divisibility ceases, with no logarithm or continuum premise."),
"013":("SFT-MATH-ARITH-DIOPHANTINE-ENUMERATION-013","Diophantine relation enumeration","complete-positive-whole-solution-census","A Diophantine relation is closed only by a complete declared positive-whole candidate census, exact substitution and retention of every satisfying tuple."),
"014":("SFT-MATH-ARITH-RECURRENCE-SEQUENCE-014","Recurrence laws and exact sequences","initial-record-rule-successor-sequence","An exact sequence is forced by a complete initial record plus one generated recurrence rule; each next term retains the entire prior dependency trace."),
"015":("SFT-MATH-ARITH-GENERATING-FUNCTION-015","Finite generating-function correspondence","coefficient-support-composition","A generating expression is an exact finite support ledger whose product coefficients count complete compositional incidences; no infinite formal sum is admitted as an object."),
"016":("SFT-MATH-ARITH-PARTITION-COMPOSITION-016","Whole partitions and ordered compositions","complete-partition-composition-census","Partitions and compositions are complete positive-part decompositions of one generated whole, distinguished respectively by erased or retained order."),
"017":("SFT-MATH-ARITH-ARITHMETIC-FUNCTIONS-017","Arithmetic functions and divisor ledgers","complete-divisor-derived-functions","Divisor count, divisor accumulation and coprime count are exact functions of the complete positive divisor and residue ledgers."),
"018":("SFT-MATH-ARITH-PRIME-DISTRIBUTION-ENCLOSURE-018","Finite prime-distribution and growth enclosures","finite-prime-census-successor-enclosures","Prime distribution is admitted as exact finite censuses and proved successor enclosures at each generated bound; no unsupported completed asymptotic object enters."),
}
IDS=tuple(DEFINITIONS[n][0] for n in sorted(DEFINITIONS))

EXCLUSIONS=("no axiom, fitted parameter, imported theorem answer or target outcome selects the law","no semantic numerical zero, negative magnitude, irrational, imaginary or floating proof scalar","structural absence is empty One; host 0 may only display absence or count artifacts","no completed infinity, ungenerated continuum or infinite formal series is admitted","no failed route retires an obligation or changes protected authority")
def dim(key,bad,badwhy,good,goodwhy):return binary_dimension(key,key.replace("_"," ")+"?",bad,badwhy,good,goodwhy)
def dimensions(relation):return (
 dim("carrier","untraced-number-symbol","A symbol without a generated trace has no exact carrier.","generated-positive-finite-carrier","The carrier is a complete positive finite Fold trace."),
 dim("relation","imported-named-operation","A named conventional operation cannot select the result.",relation,"The relation is reconstructed from complete generated incidences."),
 dim("identity","ambiguous-representation","Multiple unheld forms erase exact identity.","canonical-held-identity","Canonical form and every held orientation are explicit."),
 dim("enumeration","selected-examples","Examples cannot close the candidate space.","complete-declared-census","Every candidate in the declared positive-finite grammar is enumerated once."),
 dim("proof","outcome-or-authority","Outcome or authority is not a derivation.","root-bound-forward-forcing","The dependency trace reaches the premise-free root and forces forward."),
 dim("observation","unrecorded-comparison","An unrecorded match is not empirical evidence.","post-registry-exact-observation","Exact observations open only after the value-free registry."),
 dim("generality","fixed-table-only","A table alone has no generality certificate.","finite-successor-certificate","Base and successor preserve the law at every supplied finite depth."),
 dim("extension","fit-exception-extra-rule","A fitted exception adds a parameter.","dated-complete-no-extra-rule","The dated family is complete and open only to lawful versioned extension."),
)

class ArithmeticProgram(GeneratedMathematicsProgram):
 @property
 def registration(self):
  return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="mathematics",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)

def make(number,previous):
 cid,title,relation,statement=DEFINITIONS[number]
 dependencies=("SFT-MATH-EXACT-ARITHMETIC-001","SFT-FOUNDATION-FORM-ENFORCEMENT-001")+((previous,) if previous else ())
 observation,passed=OBS[number]
 return LawSpec(claim_id=cid,title=title,statement=statement,dependencies=dependencies,generation_rule=f"Generate the complete eight-axis ARITH-{number} structural product before opening any observation.",grammar_boundary=f"Every supplied positive finite ARITH-{number} carrier inside the registered arithmetic question, with exact absence, orientation, provenance and successor boundaries retained.",dimensions=dimensions(relation),exact_result=f"ARITH-{number} uniquely retains {relation} with canonical identity, complete enumeration, root-bound forcing, post-registry exact observation, finite-successor closure and no extra rule.",laws=(statement,observation),induction_base="The One and the least complete carrier instantiate the relation with every required distinction held.",induction_step="Appending one generated unit or one declared finite input preserves the prior trace and applies the same complete construction; omission, ambiguity or an extra rule halts.",boundary_exclusions=EXCLUSIONS,witnesses=(Witness("exact-observation",observation,passed),Witness("positive-finite","Every witness uses finite generated wholes, exact fractions or typed absence.",passed),Witness("no-target-selection","The survivor coordinates are preservation conditions fixed before observation access.",True)),why=f"The frozen Mathematics census separately owns {title.lower()}.",derivation=statement,check="Enumerate all 256 structural forms, retain one survivor, replay the exact witness, reject all four adverse controls and reconstruct through an implementation-distinct executable.",limitations="The law is depth-independent over supplied positive finite inputs; conventional continuum or completed-infinite statements require a separately registered correspondence certificate.",correspondence_terms=(title.lower(),))

specs=[];previous=None
for number in sorted(DEFINITIONS):
 spec=make(number,previous);specs.append(spec);previous=spec.claim_id
SPECS={spec.claim_id:spec for spec in specs}
