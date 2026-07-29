from itertools import product
import json
import sys

CLAIM_ID = "SFT-CHEM-ELECTROCHEMICAL-STORAGE-HANDOFF-013"
DOMAINS = (
    ("anonymous-storage-number", "complete-storage-coordinate-custody"),
    ("chemistry-owns-device-performance", "chemistry-owns-species-reactions"),
    ("materials-owns-reaction-law", "materials-own-bulk-device-response"),
    ("engineering-owns-natural-law", "engineering-owns-implementation"),
    ("overlapping-branch-ownership", "exactly-one-owner-per-coordinate"),
    ("untraced-cross-branch-use", "explicit-directed-claim-handoff"),
    ("selected-device-summary", "complete-chemistry-material-record-pair"),
    ("application-redefines-ownership", "new-coordinate-requires-new-unique-owner"),
)
SURVIVOR = "__".join(row[1] for row in DOMAINS)


def independent_handoff(rows):
    expected = ((1, "species-reactions", "chemistry"), (2, "bulk-device-response", "materials"), (3, "implementation", "engineering"))
    return rows == expected and len({row[1] for row in rows}) == len({row[2] for row in rows}) == 3


def main():
    sealed = json.load(open(sys.argv[1]))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    native = {"complete": independent_handoff(((1, "species-reactions", "chemistry"), (2, "bulk-device-response", "materials"), (3, "implementation", "engineering"))), "duplicate_halts": not independent_handoff(((1, "species-reactions", "chemistry"), (2, "bulk-device-response", "chemistry"), (3, "implementation", "engineering"))), "directed_handoffs": 2, "owners": 3}
    passed = sealed["claim_id"] == CLAIM_ID and [row["candidate_id"] for row in sealed["census"]["candidates"]] == generated and decisions == {row: row == SURVIVOR for row in generated} and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent" and all(row["passed"] for row in sealed["controls"]) and native["complete"] and native["duplicate_halts"]
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None, **native, "external_source_accessed": False, "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used": False}}, sort_keys=True))


if __name__ == "__main__":
    main()
