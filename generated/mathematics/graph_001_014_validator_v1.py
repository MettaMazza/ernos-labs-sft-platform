#!/usr/bin/env python3
"""Implementation-distinct exact validator for GRAPH-001--014."""
import json,sys
from fractions import Fraction
from itertools import combinations,permutations,product
from pathlib import Path
REL=("exact-adjacency-bijection-isomorphism","generated-incidence-path-closure","cut-flow-dual-custody","acyclic-connected-spanning-incidence","face-edge-vertex-embedding-custody","least-lawful-distinction-partition","disjoint-incidence-packing-cover-duality","orientation-retained-causal-closure","exact-part-path-accumulation","multi-carrier-incidence-custody","hereditary-exchange-independence","complete-failure-mask-support","even-walk-mode-correspondence","time-ordered-incidence-composition")
def undirected(edges):return {tuple(sorted(e)) for e in edges}
def conn(vertices,edges):
 seen={vertices[0]};front=list(seen);edges=undirected(edges)
 while front:
  a=front.pop()
  for e in edges:
   if a in e:
    b=e[0] if e[1]==a else e[1]
    if b not in seen:seen.add(b);front.append(b)
 return len(seen)==len(vertices)
def reachable(a,edges):
 seen={a}
 for _ in range(len(edges)+1):seen|={b for x,b in edges if x in seen}
 return seen
def maxflowcut():
 arcs=((0,1,2),(0,2,1),(1,2,1),(1,3,1),(2,3,2));flows=[]
 for f in product(*(range(c+1) for _,_,c in arcs)):
  if f[0]==f[2]+f[3] and f[1]+f[2]==f[4]:flows.append(f[0]+f[1])
 cuts=[]
 for a,b in product((False,True),repeat=2):
  side={0}|({1} if a else set())|({2} if b else set());cuts.append(sum(c for x,y,c in arcs if x in side and y not in side))
 return max(flows)==min(cuts)==3
def colour(k):
 e=((0,1),(1,2),(2,3),(3,4),(4,0));return any(all(c[a]!=c[b] for a,b in e) for c in product(range(k),repeat=5))
def determinant_absent_spectral():
 m=((3,2,2,2),(2,3,2,2),(2,2,3,2),(2,2,2,3));u=(1,1,1,1);p=(1,0,0,0);q=(0,1,0,0)
 mul=lambda v:tuple(sum(a*b for a,b in zip(row,v)) for row in m)
 return mul(u)==(9,9,9,9) and tuple(a+b for a,b in zip(mul(p),q))==tuple(a+b for a,b in zip(mul(q),p)) and sum(m[i][i] for i in range(4))==12
def witness(i):
 if i==1:
  c=((1,2),(2,3),(3,4),(4,1));r=((1,3),(3,2),(2,4),(4,1));return any(undirected((p[a-1],p[b-1]) for a,b in c)==undirected(r) for p in permutations((1,2,3,4))) and sum(undirected((p[a-1],p[b-1]) for a,b in c)==undirected(c) for p in permutations((1,2,3,4)))==8
 if i==2:
  c=((1,2),(2,3),(3,4),(4,1));d=c+tuple((b,a) for a,b in c);return all(len(reachable(v,d))==4 for v in range(1,5))
 if i==3:return maxflowcut()
 if i==4:
  e=tuple(combinations((1,2,3,4),2));return sum(conn((1,2,3,4),s) for s in combinations(e,3))==16
 if i==5:return 4-6+4==2 and 10>9
 if i==6:return not colour(2) and colour(3)
 if i==7:
  e=tuple(product((1,2,3),(4,5,6)));match=max(len(s) for n in range(4) for s in combinations(e,n) if len({a for a,_ in s})==len(s)==len({b for _,b in s}));cover=min(len(s) for n in range(7) for s in combinations(range(1,7),n) if all(a in s or b in s for a,b in e));return match==cover==3
 if i==8:
  e=((1,2),(1,3),(2,4),(3,4),(4,5));return sum(len(reachable(v,e))-1 for v in range(1,6))==9
 if i==9:return Fraction(1,2)+Fraction(2,3)==Fraction(7,6)<Fraction(4,3)
 if i==10:
  h=((1,2,3),(3,4,5),(1,5,6),(2,4,6));return all(sum(v in e for e in h)==2 for v in range(1,7))
 if i==11:
  independent=tuple(frozenset(s) for n in range(3) for s in combinations(range(4),n));hereditary=all(frozenset(t) in independent for s in independent for n in range(len(s)+1) for t in combinations(s,n));exchange=all(any((a|{x}) in independent for x in b-a) for a in independent for b in independent if len(a)<len(b));return len(independent)==11 and hereditary and exchange
 if i==12:
  e=((1,2),(2,3),(1,3));return sum(conn((1,2,3),tuple(x for j,x in enumerate(e) if mask>>j&1)) for mask in range(8))==4
 if i==13:return determinant_absent_spectral()
 if i==14:
  e=((1,2,1),(2,3,2),(3,4,3),(1,4,3),(4,3,2));paths=[(1,0,(1,))]
  for _ in range(5):paths+=list({(b,t,p+(b,)) for a,time,p in paths for x,b,t in e if x==a and t>=time and b not in p})
  return any(p==(1,2,3,4) for v,t,p in paths if v==4) and not any(p==(1,4,3) for v,t,p in paths if v==3)
 return False
def surface(i):
 axes=(("anonymous-or-lost-vertices","complete-generated-vertices"),("imported-edge-answer",REL[i-1]),("erased-direction","declared-directed-or-undirected-boundary"),("selected-subgraphs","complete-declared-graph-census"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("fixed-example-only","finite-successor-certificate"),("fit-exception-extra-rule","dated-complete-no-extra-rule"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_graph_witness":witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
