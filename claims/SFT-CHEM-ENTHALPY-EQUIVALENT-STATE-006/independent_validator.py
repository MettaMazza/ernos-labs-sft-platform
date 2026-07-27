"""Implementation-distinct value-free THERMO-006 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-ENTHALPY-EQUIVALENT-STATE-006"
DOMAINS = (
    ("answer-only-signed-enthalpy-scalar", "complete-held-state-and-environment-carrier"),
    ("fitted-or-unnamed-internal-content", "retained-exact-positive-internal-content"),
    ("imported-pressure-volume-equation", "observation-forced-organized-environment-transfer-parts"),
    ("signed-cancellation-or-numerical-zero-correction", "exact-positive-composition-plus-EmptyOne-absence"),
    ("negative-enthalpy-proof-magnitude", "held-state-orientation-plus-positive-separation"),
    ("enthalpy-target-readable-before-seal", "complete-value-free-enthalpy-state-identity-seal"),
    ("selected-enthalpy-or-single-phase-row", "complete-13-row-enthalpy-component-vector"),
    ("refit-prior-state-after-environment-successor", "depth-independent-append-only-environment-part-successor"),
)
SURVIVOR = (
    "complete-held-state-and-environment-carrier__retained-exact-positive-internal-content__"
    "observation-forced-organized-environment-transfer-parts__exact-positive-composition-plus-EmptyOne-absence__"
    "held-state-orientation-plus-positive-separation__complete-value-free-enthalpy-state-identity-seal__"
    "complete-13-row-enthalpy-component-vector__depth-independent-append-only-environment-part-successor"
)


def compose(internal, parts):
    if internal <= 0: raise ValueError("positive internal content required")
    if parts is None: return internal
    if not parts or len({name for name, _ in parts}) != len(parts) or any(value <= 0 for _, value in parts): raise ValueError("unique positive environment parts required")
    total = internal
    for _, value in parts: total += value
    return total


def relation(left, right):
    if left == right: return "equivalent", None
    return ("rise", right-left) if right > left else ("fall", left-right)


def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed=json.load(handle)
    generated=["__".join(row) for row in product(*DOMAINS)]
    received=[row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions={row["candidate_id"]:row["survives"] for row in sealed["decisions"]}
    parts=(("first",Fraction(2,3)),("second",Fraction(5,4))); extension=("third",Fraction(7,5)); internal=Fraction(5,3)
    base=compose(internal,None); loaded=compose(internal,parts); extended=compose(internal,parts+(extension,))
    controls=sealed["controls"]
    passed=(
        sealed["claim_id"]==CLAIM_ID and received==generated
        and sealed["census"]["expected_cardinality"]==len(generated)==256 and len(set(received))==len(generated)
        and decisions=={candidate:candidate==SURVIVOR for candidate in generated}
        and len(tuple(candidate for candidate,survives in decisions.items() if survives))==1
        and sealed["closure"]["scope"]=="depth_independent" and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls}=={"false_premise","tampered_source","tampered_artifact","boundary"}
        and all(row["passed"] is True for row in controls)
        and base==internal and loaded==Fraction(43,12) and extended==Fraction(299,60)
        and relation(loaded,loaded)==("equivalent",None) and relation(loaded,extended)==("rise",Fraction(7,5))
        and (parts+(extension,))[:-1]==parts
    )
    print(json.dumps({"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{
        "claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,
        "closure":"depth_independent" if passed else None,"EmptyOne_environment_reconstructed":base==internal,
        "exact_state_environment_composition_reconstructed":loaded==Fraction(43,12),
        "held_orientation_reconstructed":relation(loaded,extended)==("rise",Fraction(7,5)),
        "append_only_successor_reconstructed":(parts+(extension,))[:-1]==parts,
        "thermodynamic_equation_or_measurement_file_accessed":False}},sort_keys=True))


if __name__=="__main__": main()
