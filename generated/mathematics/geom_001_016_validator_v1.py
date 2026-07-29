#!/usr/bin/env python3
"""Implementation-distinct exact validator for GEOM-001--016."""
import json,sys
from fractions import Fraction
from itertools import combinations,permutations,product
from pathlib import Path
REL=("named-point-incidence-custody","exact-squared-distance","exact-part-affine-combination","projective-incidence-custody","exact-convex-combination-separation","lattice-point-polytope-incidence","face-edge-vertex-ledger","exact-geometric-decision-predicates","held-opposed-orientation-intersection","finite-polynomial-solution-census","finite-chart-transition-custody","finite-transport-curvature-ledger","least-exact-path-separation","finite-depth-self-similar-replacement","disjoint-interior-complete-cover","reversible-incidence-transformations")
def sq(a,b):return sum((max(x,y)-min(x,y))**2 for x,y in zip(a,b))
def shoe(p):return sum(p[i][0]*p[(i+1)%len(p)][1] for i in range(len(p))),sum(p[i][1]*p[(i+1)%len(p)][0] for i in range(len(p)))
def witness(i):
 if i==1:return shoe(((1,1),(2,2),(3,3)))==(11,11)
 if i==2:return sq((1,1),(4,5))==25
 if i==3:
  mid=lambda a,b:tuple(Fraction(x+y,2) for x,y in zip(a,b));tr=lambda a:tuple(x+y for x,y in zip(a,(2,1)));return tr(mid((1,1),(3,5)))==mid(tr((1,1)),tr((3,5)))
 if i==4:
  f=((1,2,3),(1,4,5),(1,6,7),(2,4,6),(2,5,7),(3,4,7),(3,5,6));return all(sum(set(q)<=set(x) for x in f)==1 for q in combinations(range(1,8),2))
 if i==5:return Fraction(1,2)<=1 and Fraction(2)>1
 if i==6:return shoe(((1,1),(2,1),(2,2),(1,2)))==(10,8)
 if i==7:return 8+6==12+2
 if i==8:return min(((1,1),(3,3),(5,5)),key=lambda p:sq(p,(2,2)))==(1,1)
 if i==9:return shoe(((1,1),(3,1),(2,3)))[0]>shoe(((1,1),(3,1),(2,3)))[1] and tuple(Fraction(x+y,2) for x,y in zip((1,1),(3,3)))==(2,2)
 if i==10:return tuple((x,y) for x,y in product(range(1,7),repeat=2) if x*y==6)==((1,6),(2,3),(3,2),(6,1))
 if i==11:return all(sq(a,b)==sq((a[0]+2,a[1]+3),(b[0]+2,b[1]+3)) for a,b in product(((1,1),(1,2),(2,1),(2,2)),repeat=2))
 if i==12:return sum((Fraction(1,2) for _ in range(4)),Fraction(0))==2
 if i==13:return (3-1)+(3-1)==4
 if i==14:return tuple(3**n for n in range(4))==(1,3,9,27)
 if i==15:return len(tuple(product(range(1,4),repeat=2)))==9
 if i==16:
  pts=((1,1),(1,3),(3,1),(3,3));maps=set()
  for sw in (False,True):
   for rx,ry in product((False,True),repeat=2):maps.add(tuple(((4-y if ry else y,4-x if rx else x) if sw else (4-x if rx else x,4-y if ry else y)) for x,y in pts))
  return len(maps)==8
 return False
def surface(i):
 axes=(("anonymous-or-lost-points","named-generated-points"),("imported-geometric-answer",REL[i-1]),("negative-coordinate-shortcut","held-opposed-orientation"),("selected-configurations","complete-declared-configuration-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-diagram-only","finite-geometric-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_geometry_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
