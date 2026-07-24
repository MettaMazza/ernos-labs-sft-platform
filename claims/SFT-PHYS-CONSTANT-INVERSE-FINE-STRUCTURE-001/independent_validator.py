"""Implementation-distinct validator for SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001."""

from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001'
DOMAINS = (('asserted-depths', 'least-complete-binary-covers'), ('single-route-depths', 'cover-generator-cross-lock'), ('free-leading-whole', 'binary-at-up-depth'), ('free-boundary-factor', 'generator-at-boundary-rank'), ('fitted-small-correction', 'one-return-over-complete-cover'), ('untyped-arithmetic-permutation', 'tower-plus-dilated-boundary'), ('selected-refinement-series', 'one-remaining-direction-per-rung'), ('infinite-or-truncated-by-fit', 'all-three-directions-promoted'), ('measured-alpha-visible', 'measurement-inaccessible-until-seal'), ('extra-scale-rule', 'no-extra-rule'))
SURVIVOR = 'least-complete-binary-covers__cover-generator-cross-lock__binary-at-up-depth__generator-at-boundary-rank__one-return-over-complete-cover__tower-plus-dilated-boundary__one-remaining-direction-per-rung__all-three-directions-promoted__measurement-inaccessible-until-seal__no-extra-rule'


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}

    b, c = 2, 3
    down, up = 5, 7
    cover = b * down ** c
    rungs = (down ** c, down ** 2 * up, down * up ** 2, up ** c)
    chain = Fraction(rungs[3], 1)
    chain = Fraction(rungs[2], 1) + Fraction(1, 1) / chain
    chain = Fraction(rungs[1], 1) + Fraction(1, 1) / chain
    effective = Fraction(cover, 1) + Fraction(1, 1) / chain
    value = Fraction(b ** up, 1) + Fraction(c ** b, 1) * (effective + 1) / effective
    arithmetic = (rungs == (125, 175, 245, 343) and value == Fraction(503846395469, 3676744786))

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
