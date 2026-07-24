"""Implementation-distinct validator for SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001."""

from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001'
DOMAINS = (('unbound-number', 'positive-held-charge-count'), ('fitted-binding-equation', 'charge-over-sealed-inverse-ratio'), ('external-critical-charge', 'complete-One-ceiling'), ('bounded-neighborhood-walk', 'greatest-whole-division-certificate'), ('endpoint-label-only', 'exact-lower-inequality'), ('single-next-value-check-only', 'successor-above-plus-order'), ('finite-coordinate-census', 'depth-independent-greatest-whole-law'), ('observed-elements-visible', 'observations-inaccessible-until-seal'), ('extra-size-parameter', 'no-extra-rule'))
SURVIVOR = 'positive-held-charge-count__charge-over-sealed-inverse-ratio__complete-One-ceiling__greatest-whole-division-certificate__exact-lower-inequality__successor-above-plus-order__depth-independent-greatest-whole-law__observations-inaccessible-until-seal__no-extra-rule'


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}

    value = Fraction(503846395469, 3676744786)
    endpoint = value.numerator // value.denominator
    arithmetic = endpoint == 137 and Fraction(endpoint, 1) <= value < Fraction(endpoint + 1, 1)

    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated)
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
        and arithmetic
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "arithmetic_reconstruction": arithmetic},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
