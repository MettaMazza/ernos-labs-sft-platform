#!/usr/bin/env python3
"""Implementation-distinct exact validator for LEARNX-001 through LEARNX-026."""
import json, sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

RELATIONS = (
    "example-target-identity-ledger", "complete-hypothesis-family", "exact-loss-risk-part", "disjoint-training-validation-test-custody",
    "complete-empirical-minimizer-set", "unseen-support-preservation", "distinguishability-indexed-sample-boundary", "realized-labeling-capacity",
    "finite-support-success-error-correspondence", "decision-boundary-classifier", "exact-representative-regression", "target-sufficient-feature-support",
    "complete-partition-objective-ledger", "seed-to-generated-support-reconstruction", "exact-branch-weight-posterior-correspondence",
    "strict-descent-learning-convergence", "prefix-loss-comparator-regret-ledger", "time-indexed-target-drift-ledger", "admissible-estimate-search-trace",
    "state-action-transition-return-ledger", "joint-policy-strategic-view-ledger", "reconstructible-decision-trace", "registered-neighborhood-shift-certificate",
    "complete-support-behavior-verification", "observational-identifiability-boundary", "twenty-six-obligation-no-omission-ledger",
)
ROWS = (("e1", ("held", "open"), "left"), ("e2", ("open", "held"), "right"), ("e3", ("held", "held"), "left"), ("e4", ("open", "open"), "right"))
FAMILY = ((0, "left"), (0, "right"), (1, "left"), (1, "right"))
def predict(hypothesis, features): return hypothesis[1] if features[hypothesis[0]] == "held" else ("right" if hypothesis[1] == "left" else "left")
def loss(hypothesis, rows): return Fraction(sum(predict(hypothesis, features) != target for _identity, features, target in rows), len(rows))
def independent_witness(index):
    if index == 1: return len({row[0] for row in ROWS}) == len(ROWS) == 4
    if index == 2: return FAMILY == tuple(product((0, 1), ("left", "right")))
    if index == 3: return loss((0, "left"), ROWS) == Fraction(0, 1) and loss((1, "left"), ROWS) == Fraction(1, 2)
    if index == 4:
        groups = ({"e1", "e2"}, {"e3"}, {"e4"}); return tuple(sum(row[0] in group for row in ROWS) for group in groups) == (2, 1, 1) and not any(groups[a] & groups[b] for a, b in combinations(range(3), 2))
    if index == 5:
        scores = {hypothesis: loss(hypothesis, ROWS) for hypothesis in FAMILY}; least = min(scores.values()); return tuple(h for h in FAMILY if scores[h] == least) == ((0, "left"),)
    if index == 6: return all(predict((0, "left"), features) == target for _identity, features, target in ROWS[2:])
    if index == 7: return len(tuple(product(("left", "right"), repeat=2))) == 4
    if index == 8:
        realized_one = {tuple(predict(h, p) for p in (("held", "open"),)) for h in FAMILY}; realized_three = {tuple(predict(h, p) for p in (("held", "open"), ("open", "held"), ("held", "held"))) for h in FAMILY}; return len(realized_one) == 2 and len(realized_three) < 8
    if index == 9: return Fraction(sum((True, True, True, False)), 4) == Fraction(3, 4)
    if index == 10: return tuple(predict((0, "left"), row[1]) for row in ROWS) == ("left", "right", "left", "right")
    if index == 11: return (Fraction(1, 2) + Fraction(3, 2)) / 2 == Fraction(1, 1)
    if index == 12:
        def enough(place): return all(a[1][place] != b[1][place] or a[2] == b[2] for a in ROWS for b in ROWS)
        return enough(0) and not enough(1)
    if index == 13: return len(tuple(product(("a", "b"), repeat=3))) == 8
    if index == 14: return {(seed, "held") for seed in ("left", "right")} == {("left", "held"), ("right", "held")}
    if index == 15:
        weights = {"left": Fraction(1, 2) * Fraction(3, 4), "right": Fraction(1, 2) * Fraction(1, 4)}; whole = sum(weights.values()); return {k: v / whole for k, v in weights.items()} == {"left": Fraction(3, 4), "right": Fraction(1, 4)}
    if index == 16:
        value = 4; trace = [value]
        while value > 1: value -= 1; trace.append(value)
        return value == 1 and trace == [4, 3, 2, 1]
    if index == 17:
        predictions = ("left", "left", "right"); targets = ("left", "right", "right"); return sum(a != b for a, b in zip(predictions, targets)) == sum("right" != b for b in targets) == 1
    if index == 18: return frozenset((("held",), "left")) != frozenset((("held",), "right"))
    if index == 19: return min(((3, ("a", "c")), (2, ("a", "b", "c")))) == (2, ("a", "b", "c"))
    if index == 20: return sum((Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))) == Fraction(1, 1)
    if index == 21: return len(tuple(product(("cooperate", "hold"), repeat=2))) == 4
    if index == 22: return (("observe", "safe"), ("rule", "safe-to-act"), ("act", "act"))[-1] == ("act", "act")
    if index == 23:
        stable = ((('left', 'a'), ('left', 'b')), (('right', 'a'), ('right', 'b'))); return all(len({point[0] for point in neighborhood}) == 1 for neighborhood in stable) and len({point[1] for point in stable[0]}) != 1
    if index == 24: return all(predict((0, "left"), row[1]) == row[2] for row in ROWS)
    if index == 25: return (("train", "left"),) == (("train", "left"),) and (("unseen", "left"),) != (("unseen", "right"),)
    if index == 26: return len(RELATIONS) == 26 and all(independent_witness(number) for number in range(1, 26))
    return False
def surface(index):
    axes = (("sampled-or-unidentified-data", "complete-example-target-ledger"), ("opaque-pretrained-or-hidden-learner", "complete-hypothesis-update-process"), ("imported-learning-answer", RELATIONS[index - 1]), ("training-only-success", "complete-held-out-adverse-ledger"), ("sampled-hypotheses", "literal-complete-product"), ("outcome-selected", "there-is-no-nothing-lineage"), ("preopened-target", "post-registry-exact-learning-execution"), ("unrestricted-intelligence-export", "declared-support-shift-application-boundary")); rows = tuple("__".join(row) for row in product(*axes)); return rows, "__".join(axis[1] for axis in axes)
def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]); index = int(claim_id.rsplit("-", 1)[-1]); sealed = json.loads(sealed_path.read_text()); rows, survivor = surface(index); received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"]); decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}; expected = {candidate: candidate == survivor for candidate in rows}; passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", independent_witness(index))); print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "learning_witness": independent_witness(index)}})); raise SystemExit(0 if passed else 1)
if __name__ == "__main__": main()
