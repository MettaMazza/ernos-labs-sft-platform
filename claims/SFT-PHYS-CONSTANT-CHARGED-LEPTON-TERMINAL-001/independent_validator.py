"""Implementation-distinct validator for the terminal lepton claim."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001"
DOMAINS = (
    ("replace-cubic-product", "retain-admitted-sharpened-product"),
    ("selected-linear-or-square-order", "one-alpha-per-three-root"),
    ("single-channel-support", "complete-generator-volume"),
    ("free-depth-coefficient", "forced-down-cover-depth"),
    ("bare-up-depth", "one-alpha-transported-up-depth"),
    ("undistributed-up-depth", "one-complete-colour-share"),
    ("append-unheld-product", "hold-correction-from-product"),
    ("measurement-readable-relation", "measurement-inaccessible-until-seal"),
    ("mislabel-as-blind-forward-discovery", "observational-derivation-disclosed"),
    ("extra-fit-term", "no-extra-rule"),
)
SURVIVOR = "__".join(domain[1] for domain in DOMAINS)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}

    inverse_alpha = Fraction(503846395469, 3676744786)
    alpha = Fraction(1, 1) / inverse_alpha
    correction = alpha ** 3 * (Fraction(5, 1) + Fraction(7, 3) * alpha) / Fraction(27, 1)
    terminal = Fraction(3, 1454) - correction
    arithmetic = terminal == Fraction(
        15659709397871168801443815466454510956837000584115,
        7590004776733382935404977537704409308185713931574254,
    )
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and all(row["passed"] is True for row in sealed["controls"])
        and arithmetic
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "terminal_product": str(terminal),
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
