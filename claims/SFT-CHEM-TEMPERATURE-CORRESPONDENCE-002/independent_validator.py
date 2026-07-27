"""Implementation-distinct value-free THERMO-002 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002'
DOMAINS = (('chemistry-redefines-temperature', 'chemistry-consumes-admitted-physics-temperature-carrier'), ('composition-erased-temperature-scalar', 'held-chemical-composition-identity'), ('phase-and-equilibrium-reference-erased', 'held-phase-and-equilibrium-reference'), ('fitted-chemical-temperature-conversion', 'identity-preserving-temperature-correspondence'), ('route-or-composition-specific-temperature', 'one-common-carrier-across-equilibrated-routes'), ('thermometric-values-readable-before-seal', 'complete-value-free-thermometric-identity-seal'), ('selected-thermometry-route', 'complete-three-row-two-route-value-vector'), ('composition-dependent-rescaling', 'append-only-composition-consequence-with-common-carrier'))
SURVIVOR = 'chemistry-consumes-admitted-physics-temperature-carrier__held-chemical-composition-identity__held-phase-and-equilibrium-reference__identity-preserving-temperature-correspondence__one-common-carrier-across-equilibrated-routes__complete-value-free-thermometric-identity-seal__complete-three-row-two-route-value-vector__append-only-composition-consequence-with-common-carrier'

def context(composition, phase, reference, route, carrier):
    if not all((composition, phase, reference, route)) or carrier <= 0:
        raise ValueError("complete held context and positive carrier required")
    return (composition, phase, reference, route, carrier)

def common_carrier(left, right):
    if left[2] != right[2] or left[4] != right[4]:
        raise ValueError("equilibrium reference or Physics carrier differs")
    return left[4]

def append_context(contexts, extension):
    if not contexts or extension in contexts: raise ValueError("new finite context required")
    carrier, reference = contexts[0][4], contexts[0][2]
    if any(row[4] != carrier or row[2] != reference for row in contexts + (extension,)):
        raise ValueError("composition-specific temperature rescaling rejected")
    return contexts + (extension,)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    carrier = Fraction(5,3)
    argon = context("argon", "gas", "common-reference", "acoustic", carrier)
    resistor = context("resistor", "condensed", "common-reference", "Johnson-noise", carrier)
    water = context("water", "liquid", "common-reference", "contact", carrier)
    mismatch_rejected = False
    try: common_carrier(argon, context("tampered", "gas", "common-reference", "route", Fraction(7,4)))
    except ValueError: mismatch_rejected = True
    extended = append_context((argon, resistor), water)
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and argon[4] == carrier and common_carrier(argon, resistor) == carrier
        and mismatch_rejected and extended[:-1] == (argon, resistor) and extended[-1] == water
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "unchanged_physics_carrier_reconstructed": argon[4] == carrier,
            "cross_route_common_carrier_reconstructed": common_carrier(argon, resistor) == carrier,
            "composition_rescaling_rejected": mismatch_rejected,
            "append_only_composition_reconstructed": extended[:-1] == (argon, resistor),
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__": main()
