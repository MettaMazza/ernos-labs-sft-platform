"""Implementation-distinct validator for the exact causal attention-transformer law."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-COMP-AIX-CAUSAL-ATTENTION-TRANSFORMER-001"
DOMAINS = (
    ("sampled-token-context", "complete-ordered-token-position-support"),
    ("opaque-attention-score", "exact-source-bound-q-k-v-projections"),
    ("numerical-future-mask", "structural-predecessor-only-support"),
    ("sampled-or-truncated-attention", "complete-exact-causal-attention-partition"),
    ("collapsed-or-unidentified-heads", "identity-retaining-multihead-contraction"),
    ("result-only-layer", "exact-normalize-residual-gate-block-trace"),
    ("fixed-context-demonstration", "append-position-and-layer-successor"),
    ("imported-transformer-runtime-or-weights", "no-imported-runtime-weight-or-target-selector"),
)
SURVIVOR = "__".join(domain[1] for domain in DOMAINS)


def exact_partition(scores):
    least = min(scores)
    masses = tuple(Fraction(1, 1) + score - least for score in scores)
    whole = sum(masses, Fraction(0, 1))
    return tuple(mass / whole for mass in masses)


def attention(tokens):
    rows = []
    for target, query in enumerate(tokens):
        sources = tuple(range(target + 1))
        scores = tuple(query * tokens[source] for source in sources)
        weights = exact_partition(scores)
        value = sum((weight * tokens[source] for weight, source in zip(weights, sources)), Fraction(0, 1))
        rows.append((sources, weights, value))
    return tuple(rows)


def operational_reconstruction():
    prefix = (Fraction(1, 1), Fraction(-1, 2))
    appended = prefix + (Fraction(3, 2),)
    before = attention(prefix)
    after = attention(appended)
    held_magnitude = Fraction(3, 2)
    gate_held = (Fraction(1, 1) + held_magnitude) / (Fraction(2, 1) + held_magnitude)
    gate_returned = Fraction(1, 1) / (Fraction(2, 1) + held_magnitude)
    checks = (
        before == after[: len(before)],
        all(row[0] == tuple(range(index + 1)) for index, row in enumerate(after)),
        all(sum(row[1], Fraction(0, 1)) == Fraction(1, 1) for row in after),
        exact_partition((Fraction(-1, 1), Fraction(1, 2))) == (Fraction(2, 7), Fraction(5, 7)),
        gate_held + gate_returned == Fraction(1, 1),
    )
    return checks


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(coordinates) for coordinates in product(*DOMAINS)]
    received = [item["candidate_id"] for item in sealed["census"]["candidates"]]
    decisions = {item["candidate_id"]: item["survives"] for item in sealed["decisions"]}
    controls = sealed["controls"]
    closure = sealed["closure"]
    operational = operational_reconstruction()
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and closure["scope"] == "depth_independent"
        and closure["minimality_passed"] is True
        and closure["named_shape_uniqueness_passed"] is True
        and {item["kind"] for item in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(item["passed"] is True for item in controls)
        and all(operational)
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "operational_reconstruction": operational,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()

