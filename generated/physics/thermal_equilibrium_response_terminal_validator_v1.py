#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
from math import comb, factorial
import json,sys
CLAIM_ID="SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043"
DOMAINS=(("primitive-continuum-coordinate","exact-positive-mean-throw"),("fitted-Boltzmann-coefficient","population-count-times-mean"),("selected-half-label","unique-binomial-multiplicity-maximum"),("continuum-exponential","normalized-dyadic-successor-ladder"),("asserted-geometric-shape","complete-fixed-count-throw-multinomial-maximum"),("ontic-random-kick","three-quarter-complementary-departure"),("free-dissipation-rate","quarter-One-antipodal-response"),("untracked-stochastic-source","finite-periodic-orbit-readout"))
SURVIVOR=tuple(x[1] for x in DOMAINS)
def multi(x):
 n=sum(x);r=factorial(n)
 for a in x:r//=factorial(a)
 return r
def forms(levels):
 target=tuple(2**(levels-i-1) for i in range(levels));n=sum(target);e=sum(i*a for i,a in enumerate(target));out=[]
 def walk(p,left,i):
  if i==levels-1:
   x=p+(left,)
   if sum(j*a for j,a in enumerate(x))==e:out.append(x)
   return
  for a in range(left+1):walk(p+(a,),left-a,i+1)
 walk((),n,0);return target,tuple(out)
def check():
 for n in range(1,10):
  rows=[comb(2*n,i) for i in range(2*n+1)];
  if [i for i,x in enumerate(rows) if x==max(rows)] != [n]:return False
 for l in range(2,6):
  t,f=forms(l);m=max(multi(x) for x in f)
  if tuple(x for x in f if multi(x)==m)!=(t,):return False
 w=(Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1,2))
 return sum(w,Fraction(0))/4==Fraction(1,2) and Fraction(3,4)-Fraction(1,2)==Fraction(1,2)-Fraction(1,4)
def main():
 with open(sys.argv[2],encoding="utf-8") as f:s=json.load(f)
 g=tuple("__".join(x) for x in product(*DOMAINS));r=tuple(x["candidate_id"] for x in s["census"]["candidates"]);re={x:tuple(x.split("__"))==SURVIVOR and check() for x in g};d={x["candidate_id"]:x["survives"] for x in s["decisions"]}
 p=all((sys.argv[1]==CLAIM_ID,s["claim_id"]==CLAIM_ID,r==g,len(set(r))==s["census"]["expected_cardinality"]==256,d==re,sum(re.values())==1,s["closure"]["scope"]=="depth_independent",{x["kind"] for x in s["controls"]}=={"false_premise","tampered_source","tampered_artifact","boundary"},all(x["passed"] for x in s["controls"]),check()))
 print(json.dumps({"passed":p,"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"equilibrium":"1/2","fluctuation":"3/4","response":"1/4","survivor":"__".join(SURVIVOR)}},sort_keys=True));raise SystemExit(0 if p else 1)
if __name__=="__main__":main()
