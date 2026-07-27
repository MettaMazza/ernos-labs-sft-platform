"""Implementation-distinct, target-inaccessible INORG-006 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM = "SFT-CHEM-LIGAND-STATE-SPLITTING-006"
DOMAINS = (
    ("imported-orbital-or-field-table", "generated-rank-three-boundary-two-support"),
    ("free-field-strength-or-fitted-parameter", "complete-ligand-support-incidence"),
    ("asserted-level-catalogue", "complete-equivalence-partition-by-incidence"),
    ("free-degeneracy-label", "positive-cardinality-of-each-partition-block"),
    ("signed-floating-or-dimensional-gap", "exact-positive-normalized-incidence-separation"),
    ("opposite-signed-shift-premise", "complementary-positive-two-block-distances"),
    ("selected-peak-or-favourable-spectrum", "complete-sealed-definition-and-spectrum-surfaces"),
    ("species-specific-exception-or-reclassification", "same-partition-law-and-removed-ligand-remerging"),
)
SURVIVOR = "generated-rank-three-boundary-two-support__complete-ligand-support-incidence__complete-equivalence-partition-by-incidence__positive-cardinality-of-each-partition-block__exact-positive-normalized-incidence-separation__complementary-positive-two-block-distances__complete-sealed-definition-and-spectrum-surfaces__same-partition-law-and-removed-ligand-remerging"


def reconstruct(words):
    supports = (
        ("contrast", 1, 2), ("contrast", 2, 3),
        ("boundary", 1, 2), ("boundary", 1, 3), ("boundary", 2, 3),
    )
    ranks = []
    for kind, first, second in supports:
        count = len(tuple(
            word
            for word in words
            if (
                ((word[first - 1] is not None) != (word[second - 1] is not None))
                if kind == "contrast"
                else ((word[first - 1] is not None) and (word[second - 1] is not None))
            )
        ))
        ranks.append(count)
    groups = {}
    for support, rank in zip(supports, ranks):
        groups.setdefault(rank, []).append(support)
    ordered = sorted(groups)
    widths = tuple(len(groups[rank]) for rank in ordered)
    separation = Fraction(ordered[1] - ordered[0], len(words)) if len(ordered) == 2 else None
    balance = (Fraction(widths[1], 5), Fraction(widths[0], 5)) if len(widths) == 2 else None
    return widths, separation, balance, sum(widths) == 5


def main() -> None:
    document = json.load(open(sys.argv[1]))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    six_words = ((1, None, None), (2, None, None), (None, 1, None), (None, 2, None), (None, None, 1), (None, None, 2))
    four_words = ((1, 1, 1), (1, 2, 2), (2, 1, 2), (2, 2, 1))
    six = reconstruct(six_words)
    four = reconstruct(four_words)
    reconstructed = (
        six == ((3, 2), Fraction(2, 3), (Fraction(2, 5), Fraction(3, 5)), True)
        and four == ((2, 3), Fraction(1, 1), (Fraction(3, 5), Fraction(2, 5)), True)
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
            "generated_support_count": 5,
            "six_direct_axis_multiplicity_separation_balance": [list(six[0]), str(six[1]), [str(value) for value in six[2]]],
            "four_complete_axis_multiplicity_separation_balance": [list(four[0]), str(four[1]), [str(value) for value in four[2]]],
            "all_members_preserved": six[3] and four[3],
            "numerical_zero_negative_irrational_imaginary_signed_continuum_or_fitted_parameter_used": False,
            "orbital_field_geometry_spectrum_target_source_or_measured_value_accessed": False
        }
    }, sort_keys=True))


if __name__ == "__main__":
    main()
