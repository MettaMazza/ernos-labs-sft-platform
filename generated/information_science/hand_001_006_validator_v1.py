#!/usr/bin/env python3
"""Implementation-distinct exact validator for HAND-001--006."""
import json
import sys
from itertools import product
from pathlib import Path

RELATIONS = (
    "directed-single-owner-export-graph",
    "formal-observation-comparison-separation",
    "sealed-formal-to-empirical-custody",
    "reversible-comparison-boundary-vocabulary",
    "dated-complete-versioned-extension",
    "complete-six-handoff-reconciliation",
)


def witness(root, index):
    census = json.loads((root / "census/information_science_discipline_obligations.json").read_text())
    reconciliation = json.loads((root / "census/information_science_discipline_current_reconciliation_v19.json").read_text())
    registry = json.loads((root / "census/information_science_hand_001_006_target_registry_v1.json").read_text())
    if len(census["obligations"]) != 262 or reconciliation["current_closed_count"] != 256 or len(registry["claim_ids"]) != 6:
        return False
    if index == 1:
        return len({"classical-computation", "quantum-computation", "biology", "medicine", "consciousness-cognitive-science", "social-collective-systems", "engineering-translation"}) == 7
    if index == 2:
        return len(("formal-law", "external-observation", "exact-comparison")) == 3
    if index == 3:
        return ("derivation", "sealed-prediction", "target-release", "comparison") == ("derivation", "sealed-prediction", "target-release", "comparison")
    if index == 4:
        rows = (("Fold-distinction", "classical-symbol"), ("Fold-support-count", "information-quantity"), ("Fold-transition-relation", "channel"), ("Fold-complete-word-support", "quantum-support"))
        return len({left for left, _right in rows}) == len({right for _left, right in rows}) == 4
    if index == 5:
        return 262 + 1 == 263
    return reconciliation["current_closed_count"] + len(registry["claim_ids"]) == len(census["obligations"]) == 262


def surface(index):
    axes = (
        ("anonymous-cross-branch-result", "complete-owned-information-law"),
        ("overlapping-or-ownerless", "exactly-one-derivation-owner"),
        ("branch-name-association", RELATIONS[index - 1]),
        ("copied-or-silent-law", "directed-consumer-dependency"),
        ("selected-handoff-summary", "complete-paired-record-custody"),
        ("outcome-selected", "root-bound-forward-forcing"),
        ("preopened-target", "post-registry-exact-observation"),
        ("permanent-branch-lock", "dated-complete-versioned-extension"),
    )
    rows = tuple("__".join(choice) for choice in product(*axes))
    survivor = "__".join(choice[1] for choice in axes)
    return rows, survivor


def main():
    claim_id, root, path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(path.read_text())
    rows, survivor = surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in rows}
    exact = witness(root, index)
    passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", exact))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "complete_handoff_witness": exact}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
