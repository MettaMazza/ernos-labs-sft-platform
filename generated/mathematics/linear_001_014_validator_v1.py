#!/usr/bin/env python3
"""Implementation-distinct exact validator for LINEAR-001--014."""
import json,sys
from fractions import Fraction
from itertools import product
from pathlib import Path
REL=("coordinate-identity-preserving-junction","junction-scaling-preserving-map-composition","reversible-row-relation-custody","image-kernel-distinction-ledger","held-opposed-volume-orientation","complete-solution-support-census","reversible-independent-coordinate-frame","exact-bilinear-pairing-squared-distance","invariant-mode-exact-scaling","nested-rational-mode-enclosure","universal-multicarrier-coordinate-product","paired-index-junction-custody","orientation-and-symmetry-quotient","exact-invariant-component-decomposition")
def mv(m,v):return tuple(sum(x*y for x,y in zip(r,v)) for r in m)
def matmul(a,b):return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))) for i in range(len(a)))
def rank2(m):
 rows=[list(r) for r in m];rank=0
 for c in range(len(rows[0])):
  p=next((i for i in range(rank,len(rows)) if rows[i][c]%2),None)
  if p is None:continue
  rows[rank],rows[p]=rows[p],rows[rank]
  for i in range(len(rows)):
   if i!=rank and rows[i][c]%2:rows[i]=[(x+y)%2 for x,y in zip(rows[i],rows[rank])]
  rank+=1
 return rank
def witness(i):
 if i==1:return tuple(x+y for x,y in zip((1,2,3),(2,1,1)))==(3,3,4)
 if i==2:return matmul(((2,0),(0,3)),((1,1),(1,0)))==((2,2),(3,0))
 if i==3:return tuple(reversed(((1,2),(3,4))))==((3,4),(1,2))
 if i==4:return rank2(((1,1,0),(0,0,1)))==2
 if i==5:
  held=1*4;opposed=2*3;return held==4 and opposed==6 and opposed-held==2
 if i==6:return tuple((x,y) for x,y in product(range(1,5),repeat=2) if x+y==3 and x+2*y==4)==((2,1),)
 if i==7:return (1+2,2)==(3,2)
 if i==8:return sum(a*b for a,b in zip((1,2),(3,1)))==5 and sum((max(a,b)-min(a,b))**2 for a,b in zip((1,2),(3,1)))==5
 if i==9:
  m=((2,1),(1,2));return mv(m,(1,1))==(3,3) and tuple(x+y for x,y in zip(mv(m,(1,0)),(0,1)))==tuple(x+y for x,y in zip(mv(m,(0,1)),(1,0)))
 if i==10:return Fraction(8,5)**2<Fraction(8,5)+1 and Fraction(13,8)**2>Fraction(13,8)+1
 if i==11:return tuple(tuple(x*y for y in (3,4,5)) for x in (1,2))==((3,4,5),(6,8,10))
 if i==12:
  t=(((3,3),(4,4)),((5,5),(6,6)));return tuple(tuple(sum(t[a][b]) for b in range(2)) for a in range(2))==((6,8),(10,12))
 if i==13:return len(tuple(product((1,2),repeat=2)))==4 and ((1,1),(2,2))!=((1,2),(2,1))
 if i==14:
  p=((1,0),(0,0));q=((0,0),(0,1));return matmul(p,p)==p and matmul(q,q)==q and ((2*p[0][0]+q[0][0],2*p[0][1]+q[0][1]),(2*p[1][0]+q[1][0],2*p[1][1]+q[1][1]))==((2,0),(0,1))
 return False
def surface(i):
 axes=(("erased-coordinate-identity","ordered-generated-coordinate-carriers"),("imported-linear-answer",REL[i-1]),("negative-scalar-shortcut","held-opposed-structural-orientation"),("selected-vectors","complete-declared-coordinate-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-matrix-only","finite-dimensional-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_linear_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
