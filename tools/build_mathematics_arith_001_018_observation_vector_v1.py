#!/usr/bin/env python3
"""Independently observe the registered ARITH family after registry freeze."""
import hashlib,json,math
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_arith_001_018_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/arith_001_018_observation_vector_v1.json"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def isprime(n):return n>1 and all(n%d for d in range(2,n))
def factor(n):
 out=[]
 for p in range(2,n+1):
  while isprime(p) and n%p==0:out.append(p);n//=p
 return out
def part(n,m=1):
 if n==0:return 1
 return sum(part(n-k,k) for k in range(m,n+1))
def cf(a,b):
 out=[]
 while b:q,r=divmod(a,b);out.append(q);a,b=b,r
 return out
def val(n,p):
 c=0
 while n%p==0:c+=1;n//=p
 return c
def main():
 if OUT.exists():raise SystemExit("ARITH observation vector already frozen")
 reg=json.loads(REG.read_text());rb=dict(reg);ri=rb.pop("registry_identity")
 if canonical(rb)!=ri or reg["target_content_present"] is not False:raise SystemExit("ARITH registry changed")
 seq=[1,1]
 for _ in range(8):seq.append(seq[-1]+seq[-2])
 obs=(
 ("successor",list(range(1,9))),
 ("junction",{"left":3,"right":5,"whole":8}),
 ("pair_cells",{"rows":3,"columns":4,"cells":12}),
 ("common_structure",{"gcd_18_24":math.gcd(18,24),"lcm_18_24":math.lcm(18,24)}),
 ("quotient_remainder",{"whole":17,"part":5,"quotient":3,"remainder":2}),
 ("primes_through_30",[n for n in range(2,31) if isprime(n)]),
 ("factorizations_2_20",{str(n):factor(n) for n in range(2,21)}),
 ("fractions",{"reduced_6_8":[Fraction(6,8).numerator,Fraction(6,8).denominator],"sum_1_3_1_4":[7,12]}),
 ("continued_fraction_355_113",cf(355,113)),
 ("residue_mod_5",{"17":17%5,"2":2%5,"18":18%5}),
 ("compatible_congruence",[x for x in range(1,106) if x%3==2 and x%5==3 and x%7==2]),
 ("valuations",{"v2_40":val(40,2),"v3_81":val(81,3)}),
 ("diophantine",{"positive_x_plus_y_8":len([(x,8-x) for x in range(1,8)]),"three_four_five":3*3+4*4==5*5}),
 ("recurrence",seq),
 ("geometric_pair_coefficients",[len([(a,n-a) for a in range(n+1)]) for n in range(8)]),
 ("decompositions_8",{"partitions":part(8),"compositions":2**7}),
 ("arithmetic_functions_12",{"tau":len([d for d in range(1,13) if 12%d==0]),"sigma":sum(d for d in range(1,13) if 12%d==0),"phi":sum(math.gcd(k,12)==1 for k in range(1,13))}),
 ("prime_enclosures",{"prime_count_100":len([n for n in range(2,101) if isprime(n)]),"between_n_2n_through_50":all(any(isprime(p) for p in range(n+1,2*n)) for n in range(2,51))}),
 )
 records=[]
 for index,(name,value) in enumerate(obs,1):
  records.append({"number":f"{index:03d}","claim_id":reg["claim_ids"][index-1],"obligation_id":reg["obligation_ids"][index-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-arith-{index:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-ARITHMETIC-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 payload={"schema":"sft-v3-mathematics-arith-001-018-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":18,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False}
 payload["vector_identity"]=canonical(payload);OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":18,"identity":payload["vector_identity"],"path":OUT.relative_to(ROOT).as_posix()},indent=2))
if __name__=="__main__":main()
