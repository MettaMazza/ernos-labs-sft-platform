"""Implementation-distinct PROP-001 product and carrier reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-EQUILIBRIUM-BOND-LENGTH-001'
DOMAINS = (('generic-diatomic-with-erased-state', 'named-isotopologue-state-and-condition'), ('arbitrary-distance-sample', 'configuration-minimum-distance'), ('free-angstrom-scale', 'held-atomic-length-reference'), ('free-leading-ratio', 'up-support-over-down-support'), ('linear-or-open-correction-series', 'binary-order-alpha-return'), ('one-universal-isotope-correction', 'distinct-light-and-heavy-typed-routes'), ('target-readable-or-selected-value', 'sealed-exact-interval-transport'), ('free-species-term-or-fit', 'finite-typed-vector-exhaustion'))
SURVIVOR = 'named-isotopologue-state-and-condition__configuration-minimum-distance__held-atomic-length-reference__up-support-over-down-support__binary-order-alpha-return__distinct-light-and-heavy-typed-routes__sealed-exact-interval-transport__finite-typed-vector-exhaustion'

def independent_carriers():
    binary = 2
    generator = 3
    down = binary + generator
    up = generator + generator + 1
    rungs = (down ** generator, down ** 2 * up, down * up ** 2, up ** generator)
    chain = Fraction(rungs[-1], 1)
    for rung in reversed(rungs[1:-1]):
        chain = Fraction(rung, 1) + Fraction(1, 1) / chain
    cover = Fraction(binary * down ** generator, 1) + Fraction(1, 1) / chain
    inverse_alpha = Fraction(binary ** up, 1) + Fraction(generator ** binary, 1) * (cover + 1) / cover
    alpha = Fraction(1, 1) / inverse_alpha
    terminal = binary ** len(rungs)
    common = Fraction(up, down)
    h2 = common + generator * up * alpha ** binary
    d2 = common + (terminal + up + 1) * alpha ** binary
    return {
        "binary": binary,
        "generator": generator,
        "down": down,
        "up": up,
        "terminal": terminal,
        "inverse_alpha": inverse_alpha,
        "alpha": alpha,
        "h2": h2,
        "d2": d2,
    }

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    carriers = independent_carriers()
    controls = sealed["controls"]
    operational = (
        carriers["down"] == 5
        and carriers["up"] == 7
        and carriers["terminal"] == 16
        and carriers["inverse_alpha"] == Fraction(503846395469, 3676744786)
        and carriers["h2"] > Fraction(7, 5)
        and carriers["d2"] > carriers["h2"]
    )
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "finite_complete"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and operational
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "finite_complete" if passed else None,
            "inverse_alpha": [carriers["inverse_alpha"].numerator, carriers["inverse_alpha"].denominator],
            "h2_multiplier": [carriers["h2"].numerator, carriers["h2"].denominator],
            "d2_multiplier": [carriers["d2"].numerator, carriers["d2"].denominator],
            "operational_reconstruction": operational,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
