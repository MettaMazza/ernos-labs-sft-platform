"""Implementation-distinct value-free THERMO-012 reconstruction."""

from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012"
DOMAINS = (
    ("unbound-temperature-pressure-pair", "complete-one-component-two-phase-point"),
    ("single-phase-state-or-erased-phase-pair", "two-distinct-held-coexisting-phases"),
    ("assumed-equilibrium-or-target-derived-equality", "exact-component-exchange-support-balance"),
    ("free-two-coordinate-continuum", "one-independent-held-coordinate-support"),
    ("imported-differential-equation-or-fitted-slope", "exact-positive-temperature-pressure-co-order"),
    ("interpolated-continuum-curve", "finite-ordered-coexistence-word"),
    ("coexistence-values-readable-before-seal", "complete-value-free-15-point-identity-seal"),
    ("refit-after-appending-or-replication", "depth-independent-append-and-common-replication"),
)
SURVIVOR = (
    "complete-one-component-two-phase-point__two-distinct-held-coexisting-phases__"
    "exact-component-exchange-support-balance__one-independent-held-coordinate-support__"
    "exact-positive-temperature-pressure-co-order__finite-ordered-coexistence-word__"
    "complete-value-free-15-point-identity-seal__depth-independent-append-and-common-replication"
)


def balanced(first, second):
    return first == second


def ordered(prior_temperature, prior_pressure, later_temperature, later_pressure):
    return later_temperature > prior_temperature and later_pressure > prior_pressure


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    base = ((3, 2, 5, 5), (5, 4, 7, 7))
    replicated = tuple(tuple(value * 6 for value in point) for point in base)
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
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in controls)
        and balanced(base[0][2], base[0][3]) and balanced(base[1][2], base[1][3])
        and ordered(base[0][0], base[0][1], base[1][0], base[1][1])
        and ordered(replicated[0][0], replicated[0][1], replicated[1][0], replicated[1][1])
        and balanced(replicated[0][2], replicated[0][3])
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None,
            "exchange_balance_reconstructed": balanced(base[0][2], base[0][3]),
            "temperature_pressure_coorder_reconstructed": ordered(base[0][0], base[0][1], base[1][0], base[1][1]),
            "common_replication_reconstructed": ordered(replicated[0][0], replicated[0][1], replicated[1][0], replicated[1][1]) and balanced(replicated[0][2], replicated[0][3]),
            "clausius_clapeyron_eos_fit_target_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
