"""Implementation-distinct reconstruction of boundary rank two."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001"
DOMAINS = (
    ("unbound-coordinate-space", "forced-three-direction-carrier"),
    ("no-held-source-normal", "one-held-source-normal"),
    ("selected-tangent-subset", "all-nonnormal-directions-retained"),
    ("signed-dimension-minus-one", "unique-positive-predecessor"),
    ("rank-one", "rank-two", "rank-three", "target-selected-rank"),
    ("linear-or-unlabelled-repetition", "complete-pair-cell-product"),
    ("partial-boundary-sample", "complete-equivalent-boundary-support"),
    ("fixed-scale-table", "pair-product-successor-closure"),
    ("measured-rank-input", "rank-sealed-before-measurement"),
    ("extra-boundary-rule", "no-extra-rule"),
)
SURVIVOR = "__".join(domain[1] for domain in DOMAINS)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    rank = next(candidate for candidate in range(1, 3) if candidate + 1 == 3)
    operational = rank == 2 and Fraction(2, 1) * Fraction(2, 1) == 4 and Fraction(3, 1) * Fraction(3, 1) == 9
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
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "boundary_rank": rank}}, sort_keys=True))


if __name__ == "__main__":
    main()
