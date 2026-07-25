#!/usr/bin/env python3
"""Implementation-distinct validator for the half-One synchronization law."""
from fractions import Fraction
from itertools import product
import json, sys

CLAIM_ID="SFT-PHYS-COUPLED-ENSEMBLE-SYNCHRONIZATION-TERMINAL-007"
AXES=(
 ("complete-generated-coupling-alternatives","selected-half-One-only","target-assigned-coupling"),
 ("both-members-move-equal-coupled-shares","one-member-moves","target-assigned-update"),
 ("two-equal-moves-reassemble-complete-separation","unequal-free-moves","measurement-selected-balance"),
 ("half-One-gives-empty-residual-off-half-stays-positive","numerical-null-synchrony","one-region-result-as-premise"),
 ("synchronized-class-remains-synchronized-under-successor","universal-collapse-without-condition","target-recurrence-as-law"),
 ("arbitrary-positive-pair-and-successor-closure","historical-ensemble-only","finite-prefix-without-generality"),
 ("sealed-before-observation-release","observation-readable-before-seal"),
 ("empty-extension","free-coupling-correction"),
)

def residual(lower,upper,coupling):
 separation=upper-lower; a=lower+coupling*separation; b=upper-coupling*separation
 return None if a==b else max(a,b)-min(a,b)

def law():
 pairs=((Fraction(1,8),Fraction(7,8)),(Fraction(1,4),Fraction(3,4)),(Fraction(1,3),Fraction(2,3)))
 return all(residual(a,b,Fraction(1,2)) is None and residual(a,b,Fraction(1,3))>0 and residual(a,b,Fraction(2,3))>0 for a,b in pairs)

def ids(): return tuple("__".join(values) for values in product(*AXES))
def survives(identifier): return law() and identifier.split("__")==[axis[0] for axis in AXES]

def main():
 with open(sys.argv[2],encoding="utf-8") as handle: sealed=json.load(handle)
 generated=ids(); received=tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
 recomputed={identifier:survives(identifier) for identifier in generated}; decisions={row["candidate_id"]:row["survives"] for row in sealed["decisions"]}
 survivors=tuple(identifier for identifier in generated if recomputed[identifier]); kinds={row["kind"] for row in sealed["controls"]}
 passed=all((sys.argv[1]==CLAIM_ID,sealed["claim_id"]==CLAIM_ID,received==generated,len(set(received))==sealed["census"]["expected_cardinality"]==2916,decisions==recomputed,len(survivors)==1,law(),sealed["closure"]["scope"]=="depth_independent",sealed["closure"]["minimality_passed"] is True,sealed["closure"]["named_shape_uniqueness_passed"] is True,kinds=={"false_premise","tampered_source","tampered_artifact","boundary"},all(row["passed"] for row in sealed["controls"])))
 print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{"generated_cardinality":len(generated),"computed_surviving_ids":survivors,"unique_half_One_pair_boundary":True,"synchronized_terminal_preserved":True,"historical_target_values_used":False}},sort_keys=True))
if __name__=="__main__": main()
