#!/usr/bin/env python3
"""Implementation-distinct ARITH product and witness reconstruction."""
import json,math,sys
from fractions import Fraction
from itertools import product
from pathlib import Path
REL=("generated-one-successor-trace","complete-disjoint-junction","complete-pair-cell-product","complete-divisor-common-return-ledger","maximal-complete-groups-held-remainder","only-one-and-self-complete-divisors","least-divisor-prime-factor-trace","reduced-parts-common-refinement","finite-quotient-remainder-expansion","same-held-remainder-class","least-common-period-compatible-residue","counted-prime-factor-depth","complete-positive-whole-solution-census","initial-record-rule-successor-sequence","coefficient-support-composition","complete-partition-composition-census","complete-divisor-derived-functions","finite-prime-census-successor-enclosures")
def prime(n):return n>1 and not any(n%d==0 for d in range(2,n))
def factor(n):
 out=[];p=2
 while n>1:
  if n%p==0:out.append(p);n//=p
  else:p+=1
 return out
def val(n,p):
 c=0
 while n%p==0:c+=1;n//=p
 return c
def partitions(n,m=1):
 if n==0:return 1
 return sum(partitions(n-k,k) for k in range(m,n+1))
def cf(a,b):
 out=[]
 while b:q=a//b;out.append(q);a,b=b,a-q*b
 return out
def witness(i):
 if i==1:return list(range(1,9))==[1,2,3,4,5,6,7,8]
 if i==2:return len([("left",x) for x in range(3)]+[("right",x) for x in range(5)])==8
 if i==3:return sum(1 for _ in product(range(3),range(4)))==12
 if i==4:return math.gcd(18,24)==6 and math.lcm(18,24)==72
 if i==5:return divmod(17,5)==(3,2)
 if i==6:return [n for n in range(2,31) if prime(n)]==[2,3,5,7,11,13,17,19,23,29]
 if i==7:return all(math.prod(factor(n))==n for n in range(2,101))
 if i==8:return Fraction(6,8)==Fraction(3,4) and Fraction(1,3)+Fraction(1,4)==Fraction(7,12)
 if i==9:return cf(355,113)==[3,7,16]
 if i==10:return 17%5==2%5 and 18%5!=2%5
 if i==11:return [x for x in range(1,106) if (x%3,x%5,x%7)==(2,3,2)]==[23]
 if i==12:return val(40,2)==3 and val(81,3)==4
 if i==13:return len([(x,8-x) for x in range(1,8)])==7 and 3**2+4**2==5**2
 if i==14:
  s=[1,1]
  for _ in range(8):s.append(s[-1]+s[-2])
  return s==[1,1,2,3,5,8,13,21,34,55]
 if i==15:return [sum(1 for a in range(n+1) if n-a>=0) for n in range(8)]==[1,2,3,4,5,6,7,8]
 if i==16:return partitions(8)==22 and 2**7==128
 if i==17:
  d=[x for x in range(1,13) if 12%x==0];return (len(d),sum(d),sum(math.gcd(x,12)==1 for x in range(1,13)))==(6,28,4)
 if i==18:return sum(prime(n) for n in range(2,101))==25 and all(any(prime(p) for p in range(n+1,2*n)) for n in range(2,51))
 return False
def surface(i):
 axes=(("untraced-number-symbol","generated-positive-finite-carrier"),("imported-named-operation",REL[i-1]),("ambiguous-representation","canonical-held-identity"),("selected-examples","complete-declared-census"),("outcome-or-authority","root-bound-forward-forcing"),("unrecorded-comparison","post-registry-exact-observation"),("fixed-table-only","finite-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"))
 rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,sealed_path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(sealed_path.read_text());rows,survivor=surface(i);received=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);decisions={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==survivor for x in rows};controls=sealed["controls"]
 passed=all((received==rows,len(received)==len(set(received))==256,decisions==expected,sum(expected.values())==1,len(controls)==4,all(x["passed"] for x in controls),sealed["closure"]["scope"]=="depth_independent",witness(i)))
 print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":len(rows),"unique_survivor_count":sum(expected.values()),"exact_arithmetic_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
