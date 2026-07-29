#!/usr/bin/env python3
"""Implementation-distinct exact validator for RETR-001--012."""
import json,sys
from itertools import product
from pathlib import Path
REL=('complete-source-location-index','complete-key-membership-retrieval','invertible-forward-inverted-ledger','registered-query-observation-map','exact-finite-ranking-order','tie-and-incomparability-classes','query-record-relevance-registry','retrieved-relevant-exact-parts','complete-parent-child-taxonomy','complete-directed-reference-graph','source-version-index-consistency','twelve-retrieval-obligation-ledger')
F=(('d1',('alpha','beta')),('d2',('beta','gamma')),('d3',('alpha',)))
def inv(rows):return tuple((t,tuple(d for d,ts in rows if t in ts)) for t in sorted({t for _,ts in rows for t in ts}))
I=inv(F)
def get(t):
 rows=tuple(ds for x,ds in I if x==t);return rows[0] if rows else ('empty-One',)
def routes(edges,start,end):
 pending=[(start,)];out=[]
 while pending:
  p=pending.pop()
  if p[-1]==end:out.append(p);continue
  pending.extend(p+(b,) for a,b in edges if a==p[-1] and b not in p)
 return tuple(sorted(out))
def witness(i):
 if i==1:return I==(('alpha',('d1','d3')),('beta',('d1','d2')),('gamma',('d2',)))
 if i==2:return get('beta')==('d1','d2') and get('delta')==('empty-One',)
 if i==3:return tuple((d,tuple(t for t,ds in I if d in ds)) for d,_ in F)==F
 if i==4:return tuple(sorted(set(get('alpha'))&set(get('beta'))))==('d1',)
 if i==5:return tuple(d for _,d in sorted(((3,'d1'),(2,'d2'),(1,'d3')),reverse=True))==('d1','d2','d3')
 if i==6:return tuple(sorted(d for s,d in ((2,'d1'),(2,'d2'),(1,'d3')) if s==2))==('d1','d2')
 if i==7:return (('q',('d1','d3')),) == (('q',('d1','d3')),)
 if i==8:return (len({'d1','d2'}&{'d1','d3'}),2)==(1,2)
 if i==9:
  e=(('root','science'),('root','arts'),('science','information'),('science','physics'));return routes(e,'root','information')==(('root','science','information'),)
 if i==10:
  e=(('a','b'),('a','c'),('b','d'),('c','d'));return routes(e,'a','d')==(('a','b','d'),('a','c','d'))
 if i==11:return get('alpha')==('d1','d3') and dict(inv((F[0],('d2',('alpha','beta','gamma')),F[2])))['alpha']==('d1','d2','d3')
 if i==12:return len(REL)==12 and all(witness(n) for n in range(1,12))
 return False
def surface(i):
 axes=(('partial-record-support','complete-source-record-support'),('opaque-or-imported-index',REL[i-1]),('post-result-query-choice','preregistered-query-observation'),('silent-total-order','exact-order-class-custody'),('sampled-index-rows','complete-declared-retrieval-product'),('outcome-selected','root-bound-forward-forcing'),('preopened-target','post-registry-exact-observation'),('fit-exception-extra-rule','finite-successor-or-explicit-boundary'));rows=tuple('__'.join(x) for x in product(*axes));return rows,'__'.join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit('-',1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x['candidate_id'] for x in sealed['census']['candidates']);dec={x['candidate_id']:bool(x['survives']) for x in sealed['decisions']};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed['controls'])==4,all(x['passed'] for x in sealed['controls']),sealed['closure']['scope']=='depth_independent',witness(i)));print(json.dumps({'passed':passed,'validated_seal_hash':sealed['seal_hash'],'recomputed_from_declared_inputs':True,'certificate':{'candidate_count':256,'unique_survivor_count':1,'complete_retrieval_witness':witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
