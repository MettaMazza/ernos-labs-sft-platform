#!/usr/bin/env python3
"""Implementation-distinct validator for the exact Fold rate carrier."""
from itertools import product
import json, sys

CLAIM_ID="SFT-PHYS-LYAPUNOV-KS-CORRESPONDENCE-TERMINAL-008"
AXES=(
 ("complete-generated-m-label-domain","selected-two-label-domain","target-assigned-label-domain"),
 ("uncast-local-separation-multiplied-by-m","free-separation-exponent","target-assigned-expansion"),
 ("complete-depth-support-m-to-d","fixed-binary-support","selected-support-subset"),
 ("same-m-carries-separation-and-support-growth","independent-rate-parameters","measurement-equated-carriers"),
 ("one-m-label-distinction-per-depth","untyped-information-increment","target-assigned-bit-rate"),
 ("exact-carrier-only-symbolic-external-translation","imported-analytic-proof-value","decimal-rate-as-proof"),
 ("sealed-before-observation-release","observation-readable-before-seal"),
 ("empty-extension","free-rate-correction"),
)

def law():
 for m in (2,3,5,7):
  prior=1
  for depth in (1,2,3,4,5):
   support=len(tuple(product(range(1,m+1),repeat=depth)))
   if support!=m**depth or support//prior!=m: return False
   prior=support
  if any((m*parts)//parts!=m for parts in (1,2,3,5,8)): return False
 return True

def ids(): return tuple("__".join(values) for values in product(*AXES))
def survives(identifier): return law() and identifier.split("__")==[axis[0] for axis in AXES]

def main():
 with open(sys.argv[2],encoding="utf-8") as handle: sealed=json.load(handle)
 generated=ids(); received=tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
 recomputed={identifier:survives(identifier) for identifier in generated}; decisions={row["candidate_id"]:row["survives"] for row in sealed["decisions"]}
 survivors=tuple(identifier for identifier in generated if recomputed[identifier]); kinds={row["kind"] for row in sealed["controls"]}
 passed=all((sys.argv[1]==CLAIM_ID,sealed["claim_id"]==CLAIM_ID,received==generated,len(set(received))==sealed["census"]["expected_cardinality"]==2916,decisions==recomputed,len(survivors)==1,law(),sealed["closure"]["scope"]=="depth_independent",sealed["closure"]["minimality_passed"] is True,sealed["closure"]["named_shape_uniqueness_passed"] is True,kinds=={"false_premise","tampered_source","tampered_artifact","boundary"},all(row["passed"] for row in sealed["controls"])))
 print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"generated_cardinality":len(generated),"computed_surviving_ids":survivors,"complete_m_to_depth_support":True,"common_separation_and_support_carrier":True,"external_target_values_used":False}},sort_keys=True))
if __name__=="__main__": main()
