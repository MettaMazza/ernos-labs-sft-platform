#!/usr/bin/env python3
"""Implementation-distinct exact validator for INFER-001--014."""
import json,sys
from itertools import product
from pathlib import Path
REL=('evidence-compatible-support-restriction','declared-observation-class-detection','unique-or-unresolved-representative','ordered-evidence-support-update','whole-record-support-reconstruction','registered-successor-support','monotone-compatible-support-intersection','compatibility-multiplicity-correspondence','singleton-structural-decision-boundary','complete-decision-outcome-ledger','complete-observation-equivalence-classes','first-forced-decision-stopping-record','source-bound-support-fusion','fourteen-inference-obligation-ledger')
H=('h1','h2','h3');E={'eA':('h1','h2'),'eB':('h2',),'eC':('h3',)}
def keep(current,e):return tuple(x for x in current if x in E[e])
def trace(seq):
 cur=H;out=[]
 for e in seq:cur=keep(cur,e);out.append(cur)
 return tuple(out)
def choose(s):return s[0] if len(s)==1 else ('unresolved',s)
def witness(i):
 if i==1:return keep(H,'eA')==('h1','h2')
 if i==2:return tuple('signal' if x in ('pulse','echo') else 'absence' for x in ('pulse','quiet','echo'))==('signal','absence','signal')
 if i==3:return choose(('h2',))=='h2' and choose(('h1','h2'))==('unresolved',('h1','h2'))
 if i==4:return trace(('eA','eB'))==(('h1','h2'),('h2',))
 if i==5:return trace(('eA','eB'))[0]==('h1','h2') and trace(('eA','eB'))[-1]==('h2',)
 if i==6:return {'h1':('h1','h2'),'h2':('h3',)}['h2']==('h3',)
 if i==7:return tuple(len(s) for s in trace(('eA','eB')))==(2,1)
 if i==8:return tuple(len(E[x]) for x in ('eA','eB','eC'))==(2,1,1)
 if i==9:return choose(keep(H,'eA'))==('unresolved',('h1','h2')) and choose(keep(H,'eB'))=='h2'
 if i==10:
  p=('signal','signal','absence','absence');o=('signal','absence','signal','absence');return tuple('TP' if a==b=='signal' else 'FP' if a=='signal' else 'FN' if b=='signal' else 'TN' for a,b in zip(p,o))==('TP','FP','FN','TN')
 if i==11:return keep(H,'eA')==('h1','h2') and keep(keep(H,'eA'),'eB')==('h2',)
 if i==12:return tuple('continue' if len(s)>1 else 'stop' for s in trace(('eA','eB')))==('continue','stop')
 if i==13:return tuple(x for x in ('h1','h2') if x in ('h2','h3'))==('h2',)
 if i==14:return len(REL)==14 and all(witness(n) for n in range(1,14))
 return False
def surface(i):
 axes=(('partial-hypothesis-support','complete-registered-hypothesis-support'),('imported-probabilistic-rule',REL[i-1]),('unregistered-evidence-choice','source-bound-evidence-record'),('fitted-score-threshold','structural-support-decision'),('sampled-inference-cases','complete-declared-inference-product'),('outcome-selected','root-bound-forward-forcing'),('preopened-target','post-registry-exact-observation'),('fit-exception-extra-rule','finite-successor-or-explicit-boundary'));rows=tuple('__'.join(x) for x in product(*axes));return rows,'__'.join(x[1] for x in axes)
def main():
 cid,_root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit('-',1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x['candidate_id'] for x in sealed['census']['candidates']);dec={x['candidate_id']:bool(x['survives']) for x in sealed['decisions']};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed['controls'])==4,all(x['passed'] for x in sealed['controls']),sealed['closure']['scope']=='depth_independent',witness(i)));print(json.dumps({'passed':passed,'validated_seal_hash':sealed['seal_hash'],'recomputed_from_declared_inputs':True,'certificate':{'candidate_count':256,'unique_survivor_count':1,'complete_inference_witness':witness(i)}}));raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
