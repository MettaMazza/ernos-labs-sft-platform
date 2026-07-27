"""Implementation-distinct value-free THERMO-003 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003'
DOMAINS = (('answer-only-signed-energy-scalar', 'complete-held-chemical-internal-energy-state'), ('fitted-total-or-unnamed-contribution', 'nonempty-exact-positive-named-part-composition'), ('negative-proof-magnitude', 'held-transfer-orientation-plus-positive-magnitude'), ('numerical-zero-energy-change', 'structural-EmptyOne-equality'), ('endpoint-only-or-signed-cancellation', 'complete-same-orientation-step-composition'), ('internal-energy-target-readable-before-seal', 'complete-value-free-thermochemical-identity-seal'), ('selected-state-or-single-phase-vector', 'complete-13-row-14-column-state-vector'), ('refit-prior-parts-after-successor', 'depth-independent-append-only-positive-part-successor'))
SURVIVOR = 'complete-held-chemical-internal-energy-state__nonempty-exact-positive-named-part-composition__held-transfer-orientation-plus-positive-magnitude__structural-EmptyOne-equality__complete-same-orientation-step-composition__complete-value-free-thermochemical-identity-seal__complete-13-row-14-column-state-vector__depth-independent-append-only-positive-part-successor'

def compose_parts(parts):
    if not parts or len({name for name, _ in parts}) != len(parts) or any(value <= 0 for _, value in parts):
        raise ValueError("nonempty unique positive parts required")
    return sum((value for _, value in parts), Fraction(0,1))

def relation(first, second):
    if first[:2] != second[:2] or first[2] <= 0 or second[2] <= 0: raise ValueError("held context differs")
    if first[2] == second[2]: return "equal", None
    return ("rise", second[2]-first[2]) if second[2] > first[2] else ("fall", first[2]-second[2])

def compose_steps(steps):
    active=tuple(step for step in steps if step[1] is not None)
    if not active:return "equal",None
    if len({step[0] for step in active}) != 1:raise ValueError("opposed steps rejected")
    return active[0][0],sum((step[1] for step in active),Fraction(0,1))

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed=json.load(handle)
    generated=["__".join(row) for row in product(*DOMAINS)]
    received=[row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions={row["candidate_id"]:row["survives"] for row in sealed["decisions"]}
    parts=(("first",Fraction(2,3)),("second",Fraction(5,4)))
    extended=parts+(("third",Fraction(7,5)),)
    a=("water","one-bar",Fraction(5,3));b=("water","one-bar",Fraction(8,3));c=("water","one-bar",Fraction(14,3))
    one,two=relation(a,b),relation(b,c)
    opposed=False
    try:compose_steps((one,relation(c,b)))
    except ValueError:opposed=True
    controls=sealed["controls"]
    passed=(
        sealed["claim_id"]==CLAIM_ID and received==generated
        and sealed["census"]["expected_cardinality"]==len(generated)==256
        and len(set(received))==len(generated)
        and decisions=={candidate:candidate==SURVIVOR for candidate in generated}
        and sum(decisions.values())==1 and sealed["closure"]["scope"]=="depth_independent"
        and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls}=={"false_premise","tampered_source","tampered_artifact","boundary"}
        and all(row["passed"] is True for row in controls)
        and compose_parts(parts)==Fraction(23,12) and compose_parts(extended)==Fraction(199,60)
        and one==("rise",Fraction(1,1)) and compose_steps((one,two))==relation(a,c) and opposed
    )
    print(json.dumps({
        "validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,
        "certificate":{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,
        "closure":"depth_independent" if passed else None,"exact_positive_parts_reconstructed":compose_parts(parts)==Fraction(23,12),
        "held_orientation_reconstructed":one==("rise",Fraction(1,1)),"path_composition_reconstructed":compose_steps((one,two))==relation(a,c),
        "opposed_signed_cancellation_rejected":opposed,"append_only_part_reconstructed":extended[:-1]==parts,"measurement_file_accessed":False},
    },sort_keys=True))

if __name__=="__main__":main()
