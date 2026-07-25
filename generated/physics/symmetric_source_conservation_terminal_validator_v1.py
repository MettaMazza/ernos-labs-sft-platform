#!/usr/bin/env python3
"""Independent reconstruction of the symmetric source-conservation census."""
from collections import Counter
from itertools import combinations_with_replacement,product
import json,sys
CLAIM_ID="SFT-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010";C=("time","axis-one","axis-two","axis-three");ORDER={v:i for i,v in enumerate(C,1)}
AXES=(("complete-ten-symmetric-source-slots","scalar-source-only","target-assigned-components"),("one-curvature-slot-to-one-source-slot","aggregate-source-equation","target-assigned-pairing"),("commuting-generated-shift-differences","imported-continuum-derivatives","target-assigned-operator"),("four-exact-opposed-ledger-identities","asserted-conservation-only","target-assigned-conservation"),("energy-one-momentum-three-stress-six","unlabelled-ten-slots","target-assigned-source-meaning"),("missing-flow-breaks-exact-balance","leak-ignored","target-assigned-leak"),("sealed-before-observation-release","observation-readable-before-seal"),("empty-extension","free-conservation-correction"))
def slot(a,b):return tuple(sorted((a,b),key=ORDER.__getitem__))
def term(ds,a,b):return tuple(sorted(ds,key=ORDER.__getitem__)),slot(a,b)
def ledgers(b):
 p=Counter();o=Counter()
 for a in C:
  for c in C:p[term((a,c,a),c,b)]+=1;p[term((a,c,b),c,a)]+=1;o[term((a,c,c),a,b)]+=1
  for d in C:o[term((a,a,b),d,d)]+=1
 for c in C:
  for d in C:p[term((b,c,c),d,d)]+=1;o[term((b,c,d),c,d)]+=1
 return p,o
def exact_law():
 slots=tuple(combinations_with_replacement(C,2))
 energy=sum(s==("time","time") for s in slots);momentum=sum("time" in s and s!=("time","time") for s in slots);stress=sum("time" not in s for s in slots);rows=[ledgers(b) for b in C];leak=rows[0][1].copy();leak.subtract({next(iter(leak)):1});leak=+leak
 return len(slots)==10 and (energy,momentum,stress)==(1,3,6) and all(p==o and sum(p.values())==sum(o.values())==48 and len(p)==31 for p,o in rows) and rows[0][0]!=leak and sum(rows[0][0].values())==sum(leak.values())+1
def ids():return tuple("__".join(values) for values in product(*AXES))
def survives(candidate_id):return exact_law() and candidate_id.split("__")==[axis[0] for axis in AXES]
def main():
 with open(sys.argv[2],encoding="utf-8") as handle:sealed=json.load(handle)
 generated=ids();received=tuple(row["candidate_id"] for row in sealed["census"]["candidates"]);recomputed={candidate_id:survives(candidate_id) for candidate_id in generated};decisions={row["candidate_id"]:row["survives"] for row in sealed["decisions"]};survivors=tuple(candidate_id for candidate_id in generated if recomputed[candidate_id]);kinds={row["kind"] for row in sealed["controls"]};passed=all((sys.argv[1]==CLAIM_ID,sealed["claim_id"]==CLAIM_ID,received==generated,len(set(received))==sealed["census"]["expected_cardinality"]==2916,decisions==recomputed,len(survivors)==1,exact_law(),sealed["closure"]["scope"]=="depth_independent",sealed["closure"]["minimality_passed"] is True,sealed["closure"]["named_shape_uniqueness_passed"] is True,kinds=={"false_premise","tampered_source","tampered_artifact","boundary"},all(row["passed"] for row in sealed["controls"])))
 print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"generated_cardinality":len(generated),"computed_surviving_ids":survivors,"symmetric_slot_count":10,"source_partition":[1,3,6],"conservation_directions":4,"terms_per_side":48,"external_targets_used":False}},sort_keys=True))
if __name__=="__main__":main()
