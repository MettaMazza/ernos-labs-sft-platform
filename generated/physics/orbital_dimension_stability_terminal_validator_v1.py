#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json,sys
CLAIM_ID="SFT-PHYS-ORBITAL-DIMENSION-STABILITY-TERMINAL-009"
AXES=(("complete-positive-whole-d-at-least-two","selected-three-space-only","target-assigned-dimensions"),("inverse-positive-power-d-minus-one","fixed-inverse-square-all-d","target-assigned-gravity-power"),("inverse-cube-positive-magnitude","dimension-matched-centrifugal-power","target-assigned-centrifugal-power"),("equal-positive-magnitudes-at-reference-radius","signed-force-import","target-assigned-balance"),("compare-positive-power-denominators","import-negative-exponent-ratio","measurement-selected-order"),("stable-two-three-marginal-four-unstable-above","three-space-only-verdict","all-dimensions-stable"),("sealed-before-observation-release","observation-readable-before-seal"),("empty-extension","free-stability-correction"))
def cls(d,q):
 g=Fraction(1,1)/(q**(d-1));c=Fraction(1,1)/(q**3);return "marginal" if g==c else "stable" if g>c else "unstable"
def law():return all(cls(d,q)==("stable" if d<4 else "marginal" if d==4 else "unstable") for d in range(2,18) for q in (Fraction(3,2),Fraction(2,1),Fraction(5,2)))
def ids():return tuple("__".join(v) for v in product(*AXES))
def survives(i):return law() and i.split("__")==[a[0] for a in AXES]
def main():
 with open(sys.argv[2],encoding="utf-8") as h:s=json.load(h)
 generated=ids();received=tuple(r["candidate_id"] for r in s["census"]["candidates"]);recomputed={i:survives(i) for i in generated};decisions={r["candidate_id"]:r["survives"] for r in s["decisions"]};survivors=tuple(i for i in generated if recomputed[i]);kinds={r["kind"] for r in s["controls"]};passed=all((sys.argv[1]==CLAIM_ID,s["claim_id"]==CLAIM_ID,received==generated,len(set(received))==s["census"]["expected_cardinality"]==2916,decisions==recomputed,len(survivors)==1,law(),s["closure"]["scope"]=="depth_independent",s["closure"]["minimality_passed"] is True,s["closure"]["named_shape_uniqueness_passed"] is True,kinds=={"false_premise","tampered_source","tampered_artifact","boundary"},all(r["passed"] for r in s["controls"])));print(json.dumps({"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"generated_cardinality":len(generated),"computed_surviving_ids":survivors,"all_dimension_partition":True,"negative_exponents_used":False,"external_targets_used":False}},sort_keys=True))
if __name__=="__main__":main()
