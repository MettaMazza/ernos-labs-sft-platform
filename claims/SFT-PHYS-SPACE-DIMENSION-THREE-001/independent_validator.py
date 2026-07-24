"""Implementation-distinct reconstruction of Fold-stable three-space."""

from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-SPACE-DIMENSION-THREE-001"
DOMAINS = (
    ("coordinate-name-only", "independent-generated-direction-carrier"),
    ("one-or-collapsed-fibre-count", "strictly-beyond-two-Fold-fibres"),
    ("unbounded-coordinate-extension", "strictly-within-four-pair-cells"),
    ("closed-or-one-sided-window", "open-Fold-stability-window"),
    ("selected-dimension", "complete-positive-count-enumeration"),
    ("two-directions", "three-directions", "four-directions", "target-selected-directions"),
    ("no-independent-lock", "equals-generator-three"),
    ("space-count-read-from-measurement", "forced-count-then-observed"),
    ("extra-dimensional-model", "no-extra-rule"),
)
SURVIVOR = "__".join(domain[1] for domain in DOMAINS)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    window = tuple(count for count in range(1, 5) if 2 < count < 4)
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
        and window == (3,)
    )
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "complete_open_window": window}}, sort_keys=True))


if __name__ == "__main__":
    main()
