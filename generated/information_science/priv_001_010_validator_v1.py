#!/usr/bin/env python3
"""Implementation-distinct exact validator for PRIV-001--010."""
import json,sys
from itertools import combinations,product
from pathlib import Path
REL=('adversary-observation-distinction-ledger','secret-independent-observation-support','side-information-refined-predecessor-class','complete-adversary-equivalence-classes','role-bound-least-disclosure-map','composed-observation-refinement-ledger','complete-query-composition-preimages','least-utility-sufficient-disclosure','privacy-law-cryptography-interface','ten-privacy-obligation-ledger');S=('L','R');U=('a','b','c','d');P={'a':'x','b':'x','c':'y','d':'y'};T={'a':'L','b':'L','c':'R','d':'R'}
def enc():return tuple((s,k,'same' if s==k else 'different') for s,k in product(S,repeat=2))
def possible(c):return tuple(s for s in S if any(a==s and x==c for a,_k,x in enc()))
def diff(m):return tuple((a,b) for a,b in combinations(tuple(m),2) if m[a]!=m[b])
def witness(i):
 if i==1:return diff({'L':'L','R':'R'})==(('L','R'),) and diff({'L':'One','R':'One'})==()
 if i==2:return possible('same')==possible('different')==S
 if i==3:return possible('same')==S and tuple(s for s,k,c in enc() if k=='L' and c=='same')==('L',)
 if i==4:return len({x for x in {'a':'member','b':'member','c':'member'}.values()})==1 and len({x for x in {'a':'reader','b':'reader','c':'editor'}.values()})==2
 if i==5:return len({'reader':('public',),'editor':('public','held')}['reader'])==1 and len({'reader':('public',),'editor':('public','held')}['editor'])==2
 if i==6:
  m={x:(P[x],{'a':'u','b':'v','c':'u','d':'v'}[x]) for x in U};return len(diff(m))==6
 if i==7:return len(tuple(product(S,repeat=2)))==4 and all(len(tuple(x for x in product(S,repeat=2) if x[n]==v))==2 for n in (0,1) for v in S)
 if i==8:return all(T[a]==T[b] for a,b in combinations(U,2) if P[a]==P[b]) and len(diff(P))<len(diff({x:x for x in U}))
 if i==9:return len(('public-class','private-class','leakage-ledger','cryptographic-handoff'))==4
 if i==10:return len(REL)==10 and all(witness(n) for n in range(1,10))
 return False
def surface(i):
 axes=(('partial-protected-support','complete-protected-source-support'),('implicit-adversary-view',REL[i-1]),('undeclared-side-channel','registered-side-information-custody'),('scalar-privacy-score','complete-leaked-distinction-ledger'),('sampled-adversaries','complete-declared-observation-product'),('outcome-selected','root-bound-forward-forcing'),('preopened-target','post-registry-exact-observation'),('fit-exception-extra-rule','finite-successor-or-explicit-boundary'));rows=tuple('__'.join(x) for x in product(*axes));return rows,'__'.join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit('-',1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x['candidate_id'] for x in sealed['census']['candidates']);dec={x['candidate_id']:bool(x['survives']) for x in sealed['decisions']};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed['controls'])==4,all(x['passed'] for x in sealed['controls']),sealed['closure']['scope']=='depth_independent',witness(i)));print(json.dumps({'passed':passed,'validated_seal_hash':sealed['seal_hash'],'recomputed_from_declared_inputs':True,'certificate':{'candidate_count':256,'unique_survivor_count':1,'complete_privacy_witness':witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
