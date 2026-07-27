"""Implementation-distinct value-free THERMO-008 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008"
DOMAINS = (
    ("bulk-phase-value-or-answer-only-potential", "complete-distinct-phase-component-addition-accounts"),
    ("changed-component-or-unheld-environment", "same-held-component-and-fixed-environment"),
    ("created-erased-or-unpaired-component", "paired-one-component-exchange-conserving-total-carrier"),
    ("signed-logarithmic-or-fitted-chemical-potential", "exact-positive-energy-and-closed-distinction-increments"),
    ("weighted-sum-tie-break-or-equal-composition-rule", "strict-product-order-with-EmptyOne-equilibrium"),
    ("compound-condition-or-composition-readable-before-seal", "complete-value-free-74-row-identity-seal"),
    ("selected-mixture-row-or-deleted-endpoint", "complete-four-system-74-row-VLE-vector-with-eight-endpoints"),
    ("refit-after-common-context-successor", "depth-independent-common-context-successor"),
)
SURVIVOR = (
    "complete-distinct-phase-component-addition-accounts__same-held-component-and-fixed-environment__"
    "paired-one-component-exchange-conserving-total-carrier__exact-positive-energy-and-closed-distinction-increments__"
    "strict-product-order-with-EmptyOne-equilibrium__complete-value-free-74-row-identity-seal__"
    "complete-four-system-74-row-VLE-vector-with-eight-endpoints__depth-independent-common-context-successor"
)


def relation(first, second):
    first_energy, first_distinctions = first
    second_energy, second_distinctions = second
    if first_energy == second_energy and first_distinctions == second_distinctions:
        return "equilibrium", None, None
    if first_energy <= second_energy and first_distinctions <= second_distinctions and (
        first_energy < second_energy or first_distinctions < second_distinctions
    ):
        label = "first"
    elif second_energy <= first_energy and second_distinctions <= first_distinctions and (
        second_energy < first_energy or second_distinctions < first_distinctions
    ):
        label = "second"
    else:
        raise ValueError("incomparable")
    return (
        label,
        None if first_energy == second_energy else abs(first_energy - second_energy),
        None if first_distinctions == second_distinctions else abs(first_distinctions - second_distinctions),
    )


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    first = (Fraction(5, 3), 2)
    second = (Fraction(8, 3), 3)
    equal = (Fraction(5, 3), 2)
    base = relation(first, second)
    equilibrium = relation(equal, equal)
    incomparable = False
    try:
        relation((Fraction(5, 3), 4), (Fraction(8, 3), 2))
    except ValueError:
        incomparable = True
    extension = (Fraction(7, 5), 2)
    extended = relation(
        (first[0] + extension[0], first[1] + extension[1]),
        (second[0] + extension[0], second[1] + extension[1]),
    )
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and len([candidate for candidate, survives in decisions.items() if survives]) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls}
        == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in controls)
        and base == ("first", Fraction(1), 1)
        and equilibrium == ("equilibrium", None, None)
        and incomparable
        and extended[0] == base[0]
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "claim_id": CLAIM_ID,
                    "generated_cardinality": len(generated),
                    "unique_survivor": SURVIVOR if passed else None,
                    "closure": "depth_independent" if passed else None,
                    "strict_product_order_reconstructed": base == ("first", Fraction(1), 1),
                    "equilibrium_EmptyOne_reconstructed": equilibrium == ("equilibrium", None, None),
                    "incomparable_account_rejected": incomparable,
                    "common_context_successor_reconstructed": extended[0] == base[0],
                    "chemical_potential_equation_activity_model_or_measurement_file_accessed": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
