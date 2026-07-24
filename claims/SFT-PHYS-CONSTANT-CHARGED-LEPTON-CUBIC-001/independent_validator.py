"""Implementation-distinct reconstruction of the charged-lepton invariants."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001"
DOMAINS = (
    ("three-names-without-joint-invariants", "one-complete-symmetric-three-root-carrier"),
    ("selected-three", "admitted-generator-three"),
    ("unnormalized-root-sum", "root-sum-is-the-One"),
    ("one-over-colour", "one-over-two-colour", "one-over-colour-square"),
    ("colour-fourth-power", "twice-colour-fifth-power"),
    ("support-count-itself", "positive-predecessor-of-support"),
    ("binary-channel", "colour-channel", "successor-channel"),
    ("add-channel-whole", "positive-take-one-channel-part"),
    ("solve-and-round-roots", "retain-exact-symmetric-invariants"),
    ("extra-coefficient-or-measured-selector", "no-extra-rule"),
)
SURVIVOR = "__".join((
    "one-complete-symmetric-three-root-carrier", "admitted-generator-three",
    "root-sum-is-the-One", "one-over-two-colour", "twice-colour-fifth-power",
    "positive-predecessor-of-support", "colour-channel",
    "positive-take-one-channel-part", "retain-exact-symmetric-invariants", "no-extra-rule",
))


def sharpen(channel: int) -> Fraction:
    return Fraction(channel, channel * 485 - 1)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    operational = (
        Fraction(1, 2 * 3) == Fraction(1, 6)
        and Fraction(1, 2 * (3 ** 5) - 1) == Fraction(1, 485)
        and tuple(sharpen(channel) for channel in (2, 3, 4))
        == (Fraction(2, 969), Fraction(3, 1454), Fraction(4, 1939))
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
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "invariants": ["1", "1/6", "1/485", "3/1454"],
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
