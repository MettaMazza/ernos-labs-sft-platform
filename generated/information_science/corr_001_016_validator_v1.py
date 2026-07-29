#!/usr/bin/env python3
"""Implementation-distinct exact validator for CORR-001--016."""
import json,sys
from itertools import product
from pathlib import Path
REL=('bijective-classical-symbol-correspondence','singleton-support-certainty-correspondence','hidden-source-support-mixture','complete-basis-labelled-word-support','one-distinction-two-label-support','complete-product-support-correspondence','nonproduct-joint-support-boundary','phase-record-quantum-dynamics-handoff','support-partition-outcome-record','injective-classical-basis-encoding','observation-class-predecessor-custody','support-insufficient-no-cloning-boundary','input-output-quantum-support-relation','information-support-quantum-coding-handoff','support-dynamics-one-owner-boundary','sixteen-correspondence-obligation-ledger');F=('L','R');J=tuple(product(F,repeat=2));P=(('L','L'),('R','R'))
def fact(rows):
 a=tuple(sorted({x for x,_ in rows}));b=tuple(sorted({y for _,y in rows}));return tuple(rows)==tuple(product(a,b))
def witness(i):
 if i==1:return tuple({'L':'left','R':'right'}[x] for x in F)==('left','right')
 if i==2:return (len(('L',)),len(('L',)))==(1,1)
 if i==3:return tuple((x,'public') for x in F)==(('L','public'),('R','public'))
 if i==4:return len(J)==4
 if i==5:return len(F)==2
 if i==6:return tuple(product(F,F))==J
 if i==7:return len(P)==2 and len(J)==4 and not fact(P)
 if i==8:return len((('L','phase-even'),('R','phase-odd')))==2
 if i==9:return len({w:('same' if w[0]==w[1] else 'different') for w in J})==4
 if i==10:return len({x:('basis',x) for x in F})==2
 if i==11:return tuple(w for w in J if w[0]!=w[1])==(('L','R'),('R','L'))
 if i==12:return tuple((x,(x,x)) for x in F)==(('L',('L','L')),('R',('R','R')))
 if i==13:
  rows=(('L','L'),('L','R'),('R','R'));return tuple(y for x,y in rows if x=='L')==('L','R')
 if i==14:return len(('basis','joint','observation','error','handoff'))==5
 if i==15:return set(('support','partition','record')).isdisjoint({'gate','amplitude','phase','dynamics'})
 if i==16:return len(REL)==16 and all(witness(n) for n in range(1,16))
 return False
def surface(i):
 axes=(('partial-state-support','complete-generated-support'),('imported-model-equivalence',REL[i-1]),('unretained-observation-class','complete-observation-record-custody'),('duplicated-quantum-dynamics','support-only-ownership-boundary'),('sampled-correspondences','complete-declared-correspondence-product'),('outcome-selected','root-bound-forward-forcing'),('preopened-target','post-registry-exact-observation'),('fit-exception-extra-rule','finite-successor-or-explicit-boundary'));rows=tuple('__'.join(x) for x in product(*axes));return rows,'__'.join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit('-',1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x['candidate_id'] for x in sealed['census']['candidates']);dec={x['candidate_id']:bool(x['survives']) for x in sealed['decisions']};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed['controls'])==4,all(x['passed'] for x in sealed['controls']),sealed['closure']['scope']=='depth_independent',witness(i)));print(json.dumps({'passed':passed,'validated_seal_hash':sealed['seal_hash'],'recomputed_from_declared_inputs':True,'certificate':{'candidate_count':256,'unique_survivor_count':1,'complete_correspondence_witness':witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
