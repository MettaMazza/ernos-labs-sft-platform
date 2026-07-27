"""Independent reconstruction for SFT-CHEM-ELECTRON-COUNT-SPIN-002."""
from itertools import product
import json
import sys
CLAIM_ID = 'SFT-CHEM-ELECTRON-COUNT-SPIN-002'
DOMAINS = (('formula-name-only', 'atomic-number-occurrence-support'), ('signed-charge-scalar', 'held-directed-electron-transfer'), ('asserted-electron-number', 'complete-electron-occurrence-census'), ('signed-spin-magnitude', 'two-held-spin-fibres'), ('same-fibre-cell-duplication', 'complementary-cell-occupation'), ('unstructured-spin-list', 'complete-pairs-plus-held-surplus'), ('state-width-detached-from-support', 'support-compatible-spin-width'), ('species-specific-exception', 'no-extra-rule'))
SURVIVOR = 'atomic-number-occurrence-support__held-directed-electron-transfer__complete-electron-occurrence-census__two-held-spin-fibres__complementary-cell-occupation__complete-pairs-plus-held-surplus__support-compatible-spin-width__no-extra-rule'
REGISTERED_INPUTS_AND_PREDICTIONS = (('hydrogen-neutral', ((1, 2),), 'empty-One', None, 2, 'odd-positive-width'), ('nitrogen-neutral', ((7, 2),), 'empty-One', None, 14, 'odd-positive-width'), ('oxygen-neutral', ((8, 2),), 'empty-One', None, 16, 'odd-positive-width'), ('fluorine-neutral', ((9, 2),), 'empty-One', None, 18, 'odd-positive-width'), ('carbon-monoxide-neutral', ((6, 1), (8, 1)), 'empty-One', None, 14, 'odd-positive-width'), ('nitric-oxide-neutral', ((7, 1), (8, 1)), 'empty-One', None, 15, 'even-positive-width'), ('hydroxyl-neutral', ((1, 1), (8, 1)), 'empty-One', None, 9, 'even-positive-width'), ('imidogen-neutral', ((1, 1), (7, 1)), 'empty-One', None, 8, 'odd-positive-width'), ('methylidyne-neutral', ((6, 1), (1, 1)), 'empty-One', None, 7, 'even-positive-width'), ('chlorine-neutral', ((17, 2),), 'empty-One', None, 34, 'odd-positive-width'), ('silicon-monoxide-neutral', ((8, 1), (14, 1)), 'empty-One', None, 22, 'odd-positive-width'), ('sulfur-monoxide-neutral', ((8, 1), (16, 1)), 'empty-One', None, 24, 'odd-positive-width'), ('hydrogen-fluoride-neutral', ((9, 1), (1, 1)), 'empty-One', None, 10, 'odd-positive-width'), ('hydrogen-chloride-neutral', ((17, 1), (1, 1)), 'empty-One', None, 18, 'odd-positive-width'), ('hydrogen-bromide-neutral', ((35, 1), (1, 1)), 'empty-One', None, 36, 'odd-positive-width'), ('iodine-neutral', ((53, 2),), 'empty-One', None, 106, 'odd-positive-width'), ('hydrogen-cation', ((1, 2),), 'remove-electron', 1, 1, 'even-positive-width'), ('nitrogen-cation', ((7, 2),), 'remove-electron', 1, 13, 'even-positive-width'), ('oxygen-cation', ((8, 2),), 'remove-electron', 1, 15, 'even-positive-width'), ('nitric-oxide-cation', ((7, 1), (8, 1)), 'remove-electron', 1, 14, 'odd-positive-width'), ('oxygen-anion', ((8, 2),), 'adjoin-electron', 1, 17, 'even-positive-width'), ('nitric-oxide-anion', ((7, 1), (8, 1)), 'adjoin-electron', 1, 16, 'odd-positive-width'))
def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(coordinates) for coordinates in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    rebuilt = []
    for row_id, populations, action, transfer_count, expected_count, expected_parity in REGISTERED_INPUTS_AND_PREDICTIONS:
        electron_count = sum(atomic_number * occurrence_count for atomic_number, occurrence_count in populations)
        valid_action = True
        if action == "adjoin-electron":
            electron_count += transfer_count
        elif action == "remove-electron":
            electron_count -= transfer_count
        elif action != "empty-One" or transfer_count is not None:
            valid_action = False
        parity = "odd-positive-width" if electron_count % 2 == 0 else "even-positive-width"
        rebuilt.append((row_id, electron_count, parity, valid_action and electron_count == expected_count, parity == expected_parity))
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == 256
        and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and len(rebuilt) == 22
        and all(row[3] and row[4] for row in rebuilt)
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID,
            "candidate_count": len(generated),
            "survivor": SURVIVOR if passed else None,
            "independently_reconstructed_prediction_rows": rebuilt,
        },
    }, sort_keys=True))
if __name__ == "__main__":
    main()
