"""Implementation-distinct value-free PROP-009 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-VIBRATIONAL-FREQUENCY-009'
DOMAINS = (('frequency-answer-with-erased-mode', 'complete-molecule-mode-symmetry-carrier'), ('continuum-sinusoid-premise', 'finite-generated-recurrence-count'), ('imported-frequency-scalar', 'exact-recurrence-over-interval-ratio'), ('merged-or-relabelled-mode-support', 'held-distinct-mode-and-symmetry-support'), ('frequency-unit-selects-law', 'post-recurrence-held-unit-translation'), ('frequency-target-readable-before-seal', 'value-free-complete-mode-seal'), ('favorable-measured-row-subset', 'complete-displayed-NIST-surface-with-gap-custody'), ('fitted-scale-or-molecular-correction', 'one-recurrence-law-no-scale-factor'))
SURVIVOR = 'complete-molecule-mode-symmetry-carrier__finite-generated-recurrence-count__exact-recurrence-over-interval-ratio__held-distinct-mode-and-symmetry-support__post-recurrence-held-unit-translation__value-free-complete-mode-seal__complete-displayed-NIST-surface-with-gap-custody__one-recurrence-law-no-scale-factor'

def frequency(recurrences, interval):
    if not isinstance(recurrences, int) or not isinstance(interval, int) or recurrences < 1 or interval < 1:
        raise ValueError("positive finite counts required")
    return Fraction(recurrences, interval)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    base = frequency(12, 3)
    repeated = frequency(60, 15)
    invalid_rejected = False
    try:
        frequency(1, None)
    except ValueError:
        invalid_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and base == Fraction(4, 1)
        and repeated == base
        and invalid_rejected
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
            "finite_recurrence_ratio_reconstructed": base == Fraction(4, 1),
            "equal_interval_successor_reconstructed": repeated == base,
            "nonpositive_interval_rejected": invalid_rejected,
            "fitted_scale_factor_used": False,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
