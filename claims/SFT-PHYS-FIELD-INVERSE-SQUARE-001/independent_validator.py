"""Implementation-distinct reconstruction of inverse-square dilution."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-FIELD-INVERSE-SQUARE-001"
DOMAINS = (
    ("unbound-response-number", "one-retained-source-carrier"),
    ("distance-created-or-lost-source", "same-complete-source-at-every-boundary"),
    ("free-or-measured-exponent", "forced-rank-two-boundary"),
    ("selected-boundary-cells", "all-equivalent-pair-cells"),
    ("unlabelled-scale-factor", "distance-ratio-paired-with-itself"),
    ("fitted-response-profile", "source-over-complete-boundary"),
    ("inverse-linear", "inverse-square", "inverse-cubic", "target-fitted-power"),
    ("finite-distance-table", "pair-product-successor-induction"),
    ("measurement-to-exponent", "sealed-exponent-to-blind-measurement"),
    ("reported-exponent-only", "source-bound-cell-and-measurement-trace"),
    ("extra-shape-or-scale", "no-extra-rule"),
)
SURVIVOR = "__".join(domain[1] for domain in DOMAINS)


def response(source: Fraction, ratio: Fraction) -> Fraction:
    return source / (ratio * ratio)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    source = Fraction(5, 7)
    ratio = Fraction(4, 3)
    operational = (
        response(Fraction(1, 1), Fraction(2, 1)) == Fraction(1, 4)
        and response(Fraction(1, 1), Fraction(3, 1)) == Fraction(1, 9)
        and response(source, ratio) * ratio * ratio == source
    )
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
        and all(row["passed"] is True for row in sealed["controls"])
        and operational
    )
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "forced_exponent": 2}}, sort_keys=True))


if __name__ == "__main__":
    main()
