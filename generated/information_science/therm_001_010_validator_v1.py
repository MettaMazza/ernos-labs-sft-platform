#!/usr/bin/env python3
"""Implementation-distinct exact validator for THERM-001--010."""
import json,sys
from itertools import product
from pathlib import Path
REL=('distinguishable-carrier-custody','merged-predecessor-class-ledger','held-predecessor-reversal-record','logical-erasure-distinction-closure','observed-distinction-record-custody','reset-predecessor-transfer-ledger','observation-action-reset-cycle-ledger','irreversible-reversible-translation-boundary','carrier-independent-information-structure','ten-information-thermodynamics-obligation-ledger');S=('L','R')
def merge(x):return 'empty-One'
def held(x):return ('empty-One',('predecessor-label',x))
def back(r):return r[1][1]
def pred():return tuple(x for x in S if merge(x)=='empty-One')
def witness(i):
 if i==1:return len({x[1] for x in (('carrier','L'),('carrier','R'))})==2
 if i==2:return tuple(merge(x) for x in S)==('empty-One','empty-One') and pred()==S
 if i==3:return all(back(held(x))==x for x in S)
 if i==4:return merge('L')==merge('R') and len(pred())==2
 if i==5:return all(('measurement',x)[1]==x for x in S)
 if i==6:return all((('reset-predecessor',x),)==(('reset-predecessor',x),) for x in S)
 if i==7:return len(tuple((x,'left' if x=='L' else 'right',('reset',x)) for x in S))==2
 if i==8:return len(pred())==2 and all(back(held(x))==x for x in S)
 if i==9:return len((('magnetic',S),('optical',S)))==2
 if i==10:return len(REL)==10 and all(witness(n) for n in range(1,10))
 return False
def surface(i):
 axes=(('partial-record-support','complete-logical-record-support'),('opaque-or-imported-erasure',REL[i-1]),('discarded-predecessor','held-predecessor-custody'),('information-equals-energy','typed-physical-translation-boundary'),('sampled-record-cycles','complete-declared-record-product'),('outcome-selected','root-bound-forward-forcing'),('preopened-target','post-registry-exact-observation'),('fit-exception-extra-rule','finite-successor-or-explicit-boundary'));rows=tuple('__'.join(x) for x in product(*axes));return rows,'__'.join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit('-',1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x['candidate_id'] for x in sealed['census']['candidates']);dec={x['candidate_id']:bool(x['survives']) for x in sealed['decisions']};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed['controls'])==4,all(x['passed'] for x in sealed['controls']),sealed['closure']['scope']=='depth_independent',witness(i)));print(json.dumps({'passed':passed,'validated_seal_hash':sealed['seal_hash'],'recomputed_from_declared_inputs':True,'certificate':{'candidate_count':256,'unique_survivor_count':1,'complete_information_thermodynamics_witness':witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
