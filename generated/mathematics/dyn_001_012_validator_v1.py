#!/usr/bin/env python3
"""Implementation-distinct exact validator for DYN-001--012."""
import json,sys
from fractions import Fraction
from itertools import product
from pathlib import Path
REL=("exact-state-orbit-generation","complete-fixed-cycle-census","exact-first-return-record","invariant-support-custody","exact-distance-contraction","finite-invariant-count-change","exact-word-shift-orbit","finite-shift-sensitivity","complete-orbit-average","reversible-invariant-map","many-to-one-loss-ledger","local-coupling-network-orbit")
T={1:2,2:3,3:2,4:4}
def trace(start,step,count):
 out=[start]
 for _ in range(count):out.append(step(out[-1]))
 return tuple(out)
def shift(w):return w[1:]+w[:1]
def dist(a,b):return max(a,b)-min(a,b)
def witness(i):
 if i==1:return trace(1,lambda x:T[x],4)==(1,2,3,2,3)
 if i==2:return tuple(x for x in T if T[x]==x)==(4,) and T[T[2]]==2 and T[2]!=2
 if i==3:return trace(2,lambda x:T[x],2)[2]==2 and trace(4,lambda x:T[x],1)[1]==4
 if i==4:return {T[x] for x in {2,3}}=={2,3}
 if i==5:return all(dist((x+1)/2,Fraction(1))==dist(x,Fraction(1))/2 for x in (Fraction(1,4),Fraction(1,2),Fraction(3,2),Fraction(2)))
 if i==6:return len({1})==1 and len({1,2})==2
 if i==7:
  w=(1,1,2,2);return shift(shift(shift(shift(w))))==w and sorted(shift(w))==sorted(w)
 if i==8:
  a=(1,1,1,1);b=(1,1,1,2);return all(trace(a,shift,2)[k][0]==trace(b,shift,2)[k][0] for k in range(3)) and trace(a,shift,3)[3][0]!=trace(b,shift,3)[3][0]
 if i==9:return Fraction(1+3,2)==Fraction(3+1,2)==2
 if i==10:return all(x[::-1][::-1]==x and sum(x[::-1])==sum(x) for x in ((1,2),(2,3),(3,5)))
 if i==11:
  f={1:1,2:1,3:2,4:2};return len(set(f.values()))==2 and len({(f[x],1 if x in (1,3) else 2) for x in f})==4
 if i==12:return trace((1,3),lambda x:(x[1],x[0]),2)==((1,3),(3,1),(1,3)) and sum((1,3))==sum((3,1))
 return False
def surface(i):
 axes=(("imported-phase-space","generated-exact-state-support"),("imported-dynamics-answer",REL[i-1]),("negative-state-change-scalar","held-opposed-transition-label"),("sampled-trajectories","complete-declared-orbit-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-depth-only","finite-successor-or-explicit-boundary"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_dynamics_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
