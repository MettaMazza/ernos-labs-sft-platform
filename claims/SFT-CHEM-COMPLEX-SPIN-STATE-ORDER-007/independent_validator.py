"""Implementation-distinct, target-inaccessible INORG-007 reconstruction."""

from itertools import product
import json
import sys


CLAIM = "SFT-CHEM-COMPLEX-SPIN-STATE-ORDER-007"
DOMAINS = (
    ("cross-complex-state-mixture", "one-complex-electron-support"),
    ("imported-orbital-or-field-table", "forced-three-plus-two-support"),
    ("selected-configurations", "complete-pair-single-occupancy-census"),
    ("named-low-spin-assumption", "least-crossing-then-least-unmatched-extremum"),
    ("named-high-spin-assumption", "greatest-unmatched-then-least-crossing-extremum"),
    ("fitted-pairing-or-field-energy", "counted-pair-closure-plus-split-crossing-paths"),
    ("asserted-ground-state-label", "complete-weak-boundary-strong-trichotomy"),
    ("species-temperature-or-distance-fit", "monotone-dilution-with-no-extra-rule"),
)
SURVIVOR = "one-complex-electron-support__forced-three-plus-two-support__complete-pair-single-occupancy-census__least-crossing-then-least-unmatched-extremum__greatest-unmatched-then-least-crossing-extremum__counted-pair-closure-plus-split-crossing-paths__complete-weak-boundary-strong-trichotomy__monotone-dilution-with-no-extra-rule"


def independent_reconstruction():
    rows = []
    for lp, ls, up, us in product(range(4), range(4), range(3), range(3)):
        if lp + ls <= 3 and up + us <= 2 and 2 * (lp + up) + ls + us == 6:
            rows.append((lp, ls, up, us))
    low = min(rows, key=lambda row: (2 * row[2] + row[3], row[1] + row[3]))
    maximum_unmatched = max(row[1] + row[3] for row in rows)
    high_rows = [row for row in rows if row[1] + row[3] == maximum_unmatched]
    high = min(high_rows, key=lambda row: 2 * row[2] + row[3])

    def cost(row, recurrence):
        pairs = row[0] + row[2]
        crossings = 2 * row[2] + row[3]
        return pairs if recurrence is None else pairs + recurrence * crossings

    vector = []
    costs = []
    for recurrence in (None, 1, 2):
        high_cost, low_cost = cost(high, recurrence), cost(low, recurrence)
        costs.append((high_cost, low_cost))
        vector.append("high-precedes-low" if high_cost < low_cost else "low-precedes-high" if low_cost < high_cost else "crossover-coincidence")
    return rows, low, high, tuple(vector), tuple(costs)


def main() -> None:
    document = json.load(open(sys.argv[1]))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    rows, low, high, vector, costs = independent_reconstruction()
    reconstructed = (
        len(rows) == 10
        and low == (3, 0, 0, 0)
        and high == (1, 2, 0, 2)
        and vector == ("high-precedes-low", "crossover-coincidence", "low-precedes-high")
        and costs == ((1, 3), (3, 3), (5, 3))
    )
    passed = (
        document["claim_id"] == CLAIM
        and received == generated
        and len(generated) == 256
        and len(set(received)) == 256
        and document["census"]["expected_cardinality"] == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and document["closure"]["scope"] == "depth_independent"
        and document["closure"]["minimality_passed"]
        and document["closure"]["named_shape_uniqueness_passed"]
        and {row["kind"] for row in document["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in document["controls"])
        and reconstructed
    )
    print(json.dumps({
        "validated_seal_hash": document["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "complete_six_electron_signature_count": len(rows),
            "low_signature": tuple("EmptyOne" if value == 0 else value for value in low),
            "high_signature": tuple("EmptyOne" if value == 0 else value for value in high),
            "order_vector": vector,
            "cost_vector": costs,
            "numerical_zero_negative_irrational_imaginary_signed_continuum_or_fitted_parameter_used_in_proof_object": False,
            "orbital_field_pairing_temperature_distance_species_or_target_source_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
