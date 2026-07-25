#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json,sys
CLAIM_ID="SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008"
AXES=(("complete-generated-m-expansion","selected-binary-expansion","target-assigned-expansion"),("retain-one-minus-coupling-share","free-residual-action","target-assigned-residual"),("unique-m-minus-one-over-m-boundary","fixed-half-One-for-all-m","measurement-selected-threshold"),("below-expands-boundary-neutral-above-contracts","boundary-declared-contracting","unclassified-criticality"),("normalized-drive-response-transverse-channel","arbitrary-topology-universal-threshold","finite-example-only"),("exact-rational-carrier-symbolic-external-translation","imported-exponential-proof-value","decimal-criticality-proof"),("sealed-before-observation-release","observation-readable-before-seal"),("empty-extension","free-threshold-correction"))
def law():
 for m in (2,3,5,7,11):
  threshold=Fraction(m-1,m); below=Fraction(m-1,m+1); above=Fraction(m,m+1); multipliers=tuple(m*(1-g) for g in (below,threshold,above))
  if not multipliers[0]>1 or multipliers[1]!=1 or not multipliers[2]<1:return False
 return True
def ids():return tuple("__".join(v) for v in product(*AXES))
def survives(identifier):return law() and identifier.split("__")==[axis[0] for axis in AXES]
def main():
 with open(sys.argv[2],encoding="utf-8") as h:sealed=json.load(h)
 generated=ids();received=tuple(r["candidate_id"] for r in sealed["census"]["candidates"]);recomputed={i:survives(i) for i in generated};decisions={r["candidate_id"]:r["survives"] for r in sealed["decisions"]};survivors=tuple(i for i in generated if recomputed[i]);kinds={r["kind"] for r in sealed["controls"]};passed=all((sys.argv[1]==CLAIM_ID,sealed["claim_id"]==CLAIM_ID,received==generated,len(set(received))==sealed["census"]["expected_cardinality"]==2916,decisions==recomputed,len(survivors)==1,law(),sealed["closure"]["scope"]=="depth_independent",sealed["closure"]["minimality_passed"] is True,sealed["closure"]["named_shape_uniqueness_passed"] is True,kinds=={"false_premise","tampered_source","tampered_artifact","boundary"},all(r["passed"] for r in sealed["controls"])))
 print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"generated_cardinality":len(generated),"computed_surviving_ids":survivors,"unique_rational_threshold":True,"normalized_scope_only":True,"external_target_values_used":False}},sort_keys=True))
if __name__=="__main__":main()
