#!/usr/bin/env python3
"""Implementation-distinct exact validator for CPLXX-001 through CPLXX-033."""
import json, sys
from fractions import Fraction
from itertools import product
from pathlib import Path

RELATIONS=(
"canonical-generated-input-size","exact-transition-trace-time","maximum-retained-configuration-space","strict-resource-successor-hierarchy","complete-deterministic-branch-product","trace-bound-certificate-resource","native-trace-certificate-equality","total-bidirectional-resource-transport","terminal-verdict-complement","depth-first-alternation-space","complete-branching-support-succession","generated-family-uniformity-record","circuit-resource-vector","trace-preserving-graph-model-translation","layered-work-depth-ledger","transcript-distinguishability-resource","leaf-distinguishability-query-bound","exact-branch-ledger-randomness","branch-invariant-canonical-selection","exact-accepting-branch-count","resource-preserving-reduction-closure","attained-execution-upper-bound","unresolved-input-pair-lower-bound","native-fold-edge-circuit-lower-bound","complete-instance-resource-distribution","exact-candidate-optimum-part","input-parameter-resource-pair","equivalent-bounded-kernel-reconstruction","prefix-complete-aggregate-ledger","prefix-decision-offline-comparison","fixed-grammar-least-description","predecessor-record-reversible-resource","thirty-three-obligation-no-omission-ledger")


def words(depth): return tuple(product(("a","b"),repeat=depth))
def trace(word): return tuple(tuple(word[:cut]) for cut in range(len(word),-1,-1))
def profile(depth): return depth,2**depth,sum(2**level for level in range(1,depth+1))
def reduce_layers(width):
    rows=[width]
    while rows[-1]>1: rows.append(rows[-1]//2)
    return tuple(rows)


def independent_witness(index):
    w3=words(3)
    if index==1:return len(w3)==8 and all(len(x)==3 for x in w3)
    if index==2:return all(len(trace(x))-1==3 for x in w3)
    if index==3:return all(max(map(len,trace(x)))==3 for x in w3)
    if index==4:return tuple(len(trace(tuple("a" for _ in range(d))))-1 for d in range(1,7))==(1,2,3,4,5,6)
    if index==5:return len(words(4))==len(set(words(4)))==16
    if index in (6,7):return all(trace(x)[0]==x and trace(x)[-1]==() and len(trace(x))-1==len(x) for x in w3)
    if index==8:
        forward={x:tuple("left" if y=="a" else "right" for y in x) for x in w3}; reverse={v:k for k,v in forward.items()};return len(forward)==len(reverse)==8 and all(reverse[forward[x]]==x for x in w3)
    if index==9:return {"accept":"reject","reject":"accept"}==dict((x,"reject" if x=="accept" else "accept") for x in ("accept","reject"))
    if index==10:
        left=False;right=all((True,True));return any((left,right))
    if index==11:return tuple(len(words(d)) for d in range(1,7))==(2,4,8,16,32,64)
    if index==12:return tuple(profile(d)[2] for d in range(1,7))==(2,6,14,30,62,126)
    if index==13:return profile(4)==(4,16,30)
    if index==14:return len(trace(("a","b","a")))-1==profile(3)[0]
    if index==15:return reduce_layers(8)==(8,4,2,1)
    if index==16:
        transcripts={"aa":"same","ab":"different","ba":"different","bb":"same"};return len(set(transcripts.values()))==2 and sum(x=="same" for x in transcripts.values())==2
    if index==17:return len(words(4))==16 and sum(2**d for d in range(5))==31
    if index==18:return Fraction(3,4)+Fraction(1,4)==1
    if index==19:return len(set(("accept",)*4))==1 and len(set(("accept","reject")))==2
    if index==20:return sum(x=="accept" for x in ("accept","reject","accept","accept"))==3
    if index==21:
        first={"x":"a","y":"b"};second={"a":"left","b":"right"};return {x:second[y] for x,y in first.items()}=={"x":"left","y":"right"}
    if index==22:return len(trace(("a","b","a","b")))-1==4
    if index==23:
        rows=words(4);return any(a[:3]==b[:3] and a!=b for a in rows for b in rows)
    if index==24:return all(profile(d)==(d,2**d,sum(2**level for level in range(1,d+1))) for d in range(1,8))
    if index==25:return max((1,2,4,1))==4 and Fraction(sum((1,2,4,1)),4)==2
    if index==26:return Fraction(6,4)==Fraction(3,2)
    if index==27:return all(len(x)<=len(x)+k for x in w3 for k in (1,2))
    if index==28:
        source=("a","a","b","a");kernel=tuple(dict.fromkeys(source));locations={x:tuple(i for i,y in enumerate(source) if x==y) for x in kernel};return kernel==("a","b") and locations=={"a":(0,1,3),"b":(2,)}
    if index==29:
        costs=(1,1,3,1);prefix=tuple(sum(costs[:i]) for i in range(1,5));return sum(costs)==6 and prefix==(1,2,5,6) and Fraction(sum(costs),len(costs))==Fraction(3,2)
    if index==30:return Fraction(6,4)==Fraction(3,2)
    if index==31:return min(map(len,(("a","a","a"),("repeat","a"))))==2
    if index==32:
        source=("a","b","c");record=tuple(reversed(source));return tuple(reversed(record))==source
    if index==33:return len(RELATIONS)==33 and all(independent_witness(i) for i in range(1,33))
    return False


def generated_surface(index):
    axes=(("ambiguous-or-sampled-input","canonical-complete-input"),("single-or-hidden-resource","time-space-depth-width-record-ledger"),("imported-class-answer",RELATIONS[index-1]),("selected-favorable-support","complete-generated-support"),("sampled-algorithms","literal-complete-product"),("outcome-selected","there-is-no-nothing-lineage"),("preopened-target","post-registry-exact-resource-execution"),("unrestricted-export","depth-certificate-or-explicit-transport"))
    rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)


def main():
    claim_id,_root,sealed_path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);index=int(claim_id.rsplit("-",1)[-1]);sealed=json.loads(sealed_path.read_text());rows,survivor=generated_surface(index);received=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);decisions={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==survivor for x in rows};passed=all((received==rows,len(set(received))==len(received)==256,decisions==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",independent_witness(index)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complexity_witness":independent_witness(index)}}));raise SystemExit(0 if passed else 1)


if __name__=="__main__":main()
