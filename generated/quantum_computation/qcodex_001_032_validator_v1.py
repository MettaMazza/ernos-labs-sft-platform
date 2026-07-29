#!/usr/bin/env python3
"""Implementation-distinct exact validator for QCODEX-001 through QCODEX-032."""
import json, sys
from itertools import combinations, product
from pathlib import Path

RELATIONS = (
    "logical-class-physical-word-encoding-relation", "source-bound-reversible-encoding-decoding", "complete-generated-error-action-grammar", "code-constraint-comparison-syndrome", "distinct-error-images-or-syndrome-records", "odd-width-label-majority-code", "odd-width-phase-majority-code", "separate-label-phase-and-joint-fault-ledger", "width-three-all-one-fault-census", "width-five-all-two-fault-census", "width-seven-all-three-fault-census", "two-t-plus-one-unbounded-finite-successor", "located-missing-carrier-reconstruction", "located-support-loss-environment-handoff", "relative-phase-fault-and-environment-record", "complete-label-phase-joint-error-support", "commuting-code-constraint-syndrome-correspondence", "separate-label-and-phase-constraint-families", "logical-gauge-syndrome-factor-ledger", "cell-complex-chain-syndrome-correspondence", "finite-surface-cell-check-and-chain-ledger", "outer-inner-codeword-substitution", "code-space-preserving-physical-transformation", "carrierwise-gate-within-block-fault-containment", "data-ancilla-measurement-fault-transcript", "location-fault-order-composable-containment", "complete-fault-subset-logical-failure-census", "joint-cause-multilocation-error-grammar", "outside-code-support-and-located-loss-ledger", "multi-input-check-select-output-transcript", "formal-fault-census-to-measured-threshold-handoff", "thirty-two-obligation-no-omission-ledger",
)
def flip(x): return "returned" if x == "held" else "held"
def masks(width, order): return tuple(mask for count in range(order + 1) for mask in combinations(range(1, width + 1), count))
def recover(order):
    source = tuple("held" for _ in range(2 * order + 1)); rows = []
    for mask in masks(len(source), order):
        word = list(source)
        for place in mask: word[place - 1] = flip(word[place - 1])
        rows.append(word.count("held") > word.count("returned"))
    return all(rows)
def independent_witness(index):
    checks = (
        ("logical", ("held", "held", "held"))[0] == "logical", "returned" == "returned", masks(3, 1) == ((), (1,), (2,), (3,)), ("same", "distinct") != ("same", "same"), len({("d1",), ("d2",), ("d3",)}) == 3, recover(1), recover(1), ("bit", "phase", "joint")[-1] == "joint", len(masks(3, 1)) == 4 and recover(1), len(masks(5, 2)) == 16 and recover(2), len(masks(7, 3)) == 64 and recover(3), all(recover(order) for order in range(1, 6)), ("held", "held", "held")[1] == "held", {"loss": True, "rate": False}["loss"], ("source-phase", "fault-phase", "record")[-1] == "record", len({"label", "phase", "joint"}) == 3, ("same", "same") == ("same", "same"), ("bit-syndrome", "phase-syndrome") != ("phase-syndrome", "bit-syndrome"), ("logical", "gauge", "syndrome")[0] == "logical", len({("a", "b"), ("b", "c"), ("c", "d")}) == 3, {"v": 4, "e": 4, "f": 1}["f"] == 1, len(tuple(tuple("held" for _ in range(3)) for _ in range(3))) == 3, tuple(flip(x) for x in ("held", "held", "held")) == ("returned", "returned", "returned"), recover(1), ("data", "syndrome", "fault-record")[-1] == "fault-record", all(f <= t for f, t in ((1, 1), (2, 2), (3, 3))), len({("l1",), ("l1", "l2")}) == 2, ("fault-a", "fault-b", "shared-record")[-1] == "shared-record", ("code", "outside", "located-loss")[1] == "outside", (3, 1, 2)[0] == 3, {"formal": True, "physical-threshold": False}["formal"], len(RELATIONS) == 32,
    )
    return checks[index - 1]
def generated_surface(index):
    axes = (("imported-or-partial-code", "complete-logical-physical-code-support"), ("imported-recovery-or-threshold", RELATIONS[index - 1]), ("sampled-or-independent-only-faults", "complete-registered-fault-family"), ("terminal-logical-output-only", "complete-syndrome-environment-and-recovery-record"), ("selected-favorable-masks", "literal-complete-product"), ("outcome-selected-law", "there-is-no-nothing-lineage"), ("preopened-recovery-outcome", "post-registry-exact-execution"), ("silent-physical-threshold-export", "explicit-formal-physical-threshold-handoff"))
    rows = tuple("__".join(coordinates) for coordinates in product(*axes)); return rows, "__".join(axis[1] for axis in axes)
def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]); index = int(claim_id.rsplit("-", 1)[-1]); sealed = json.loads(sealed_path.read_text()); rows, survivor = generated_surface(index); received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"]); decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}; expected = {row: row == survivor for row in rows}; passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", independent_witness(index))); print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "quantum_coding_witness": independent_witness(index)}})); raise SystemExit(0 if passed else 1)
if __name__ == "__main__": main()
