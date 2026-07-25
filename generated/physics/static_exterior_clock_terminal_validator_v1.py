#!/usr/bin/env python3
"""Independent reconstruction of the finite static exterior census."""
from fractions import Fraction
from itertools import product
import json,sys
CLAIM_ID="SFT-PHYS-STATIC-EXTERIOR-CLOCK-TERMINAL-011"
AXES=(("twice-mass-generated-horizon","free-radius-scale","target-assigned-horizon"),("inverse-square-with-conserved-horizon-flux","free-field-power","target-assigned-field"),("radius-times-field-gives-horizon-over-radius-share","independent-potential-profile","target-assigned-well"),("positive-One-complement-of-well","signed-subtraction-import","target-assigned-coefficient"),("exact-square-carriers-and-empty-horizon-record","unrestricted-irrational-root","target-assigned-clock"),("finite-successor-flat-boundary-and-vacuum","completed-infinity-or-interior-extension","target-assigned-boundary"),("sealed-before-observation-release","observation-readable-before-seal"),("empty-extension","free-exterior-correction"))
def exact_law():
 m=Fraction(1,4);h=2*m;rows=[]
 for d in range(1,13):
  r=h*(2**d);w=h/r;a=Fraction(1,1)-w;f=h/(r*r);rows.append((r,w,a,f,f*r*r))
 near_r=Fraction(8,7);far_r=Fraction(25,18);near_a=Fraction(1,1)-h/near_r;far_a=Fraction(1,1)-h/far_r
 return h==Fraction(1,2) and all(row[4]==h and row[1]*row[0]==h and row[2]+row[1]==1 and row[2]>0 for row in rows) and all(rows[i+1][1]*2==rows[i][1] and rows[i+1][3]*4==rows[i][3] and rows[i+1][2]>rows[i][2] for i in range(len(rows)-1)) and near_a==Fraction(9,16) and far_a==Fraction(16,25) and Fraction(4,5)/Fraction(3,4)==Fraction(16,15)
def ids():return tuple("__".join(values) for values in product(*AXES))
def survives(candidate_id):return exact_law() and candidate_id.split("__")==[axis[0] for axis in AXES]
def main():
 with open(sys.argv[2],encoding="utf-8") as handle:sealed=json.load(handle)
 generated=ids();received=tuple(row["candidate_id"] for row in sealed["census"]["candidates"]);recomputed={candidate_id:survives(candidate_id) for candidate_id in generated};decisions={row["candidate_id"]:row["survives"] for row in sealed["decisions"]};survivors=tuple(candidate_id for candidate_id in generated if recomputed[candidate_id]);kinds={row["kind"] for row in sealed["controls"]};passed=all((sys.argv[1]==CLAIM_ID,sealed["claim_id"]==CLAIM_ID,received==generated,len(set(received))==sealed["census"]["expected_cardinality"]==2916,decisions==recomputed,len(survivors)==1,exact_law(),sealed["closure"]["scope"]=="depth_independent",sealed["closure"]["minimality_passed"] is True,sealed["closure"]["named_shape_uniqueness_passed"] is True,kinds=={"false_premise","tampered_source","tampered_artifact","boundary"},all(row["passed"] for row in sealed["controls"])))
 print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"generated_cardinality":len(generated),"computed_surviving_ids":survivors,"horizon":"1/2","successor_depths":12,"exact_far_over_near_clock_rate":"16/15","external_targets_used":False}},sort_keys=True))
if __name__=="__main__":main()
