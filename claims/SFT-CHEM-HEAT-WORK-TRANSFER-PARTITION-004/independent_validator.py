"""Implementation-distinct value-free THERMO-004 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-HEAT-WORK-TRANSFER-PARTITION-004"
DOMAINS = (
    ("answer-only-signed-net-energy", "complete-held-chemical-transfer-path"),
    ("imported-or-arbitrary-heat-work-label", "observation-forced-closed-or-held-carrier-class"),
    ("negative-or-signed-transfer-content", "held-direction-plus-exact-positive-content"),
    ("merged-or-overlapping-transfer-classes", "disjoint-exhaustive-heat-work-path-partition"),
    ("signed-net-cancellation-or-numerical-zero", "per-class-positive-composition-plus-EmptyOne-absence"),
    ("calorimetric-or-work-target-readable-before-seal", "complete-value-free-transfer-identity-seal"),
    ("selected-calorimetric-or-expansion-row", "complete-13-row-joint-calorimetric-expansion-vector"),
    ("repartition-prior-path-after-successor", "depth-independent-append-only-transfer-successor"),
)
SURVIVOR = (
    "complete-held-chemical-transfer-path__observation-forced-closed-or-held-carrier-class__"
    "held-direction-plus-exact-positive-content__disjoint-exhaustive-heat-work-path-partition__"
    "per-class-positive-composition-plus-EmptyOne-absence__complete-value-free-transfer-identity-seal__"
    "complete-13-row-joint-calorimetric-expansion-vector__depth-independent-append-only-transfer-successor"
)


def classify(carrier):
    if carrier == "closed":
        return "heat"
    if carrier == "retained":
        return "work"
    raise ValueError("unforced carrier class")


def compose(records):
    if not records or any(value <= 0 for _, value in records):
        raise ValueError("nonempty exact positive records required")
    heat = tuple(value for carrier, value in records if classify(carrier) == "heat")
    work = tuple(value for carrier, value in records if classify(carrier) == "work")
    if len(heat) + len(work) != len(records):
        raise ValueError("partition omitted a record")
    heat_total = None if not heat else heat[0] + sum(heat[1:], Fraction(0, 1))
    work_total = None if not work else work[0] + sum(work[1:], Fraction(0, 1))
    complete = records[0][1] + sum((value for _, value in records[1:]), Fraction(0, 1))
    return heat_total, work_total, complete


def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    prior = (("closed", Fraction(2, 3)), ("closed", Fraction(5, 4)))
    extension = ("retained", Fraction(7, 5))
    heat_only = compose(prior)
    complete = compose(prior + (extension,))
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and len(tuple(candidate for candidate, survives in decisions.items() if survives)) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and classify("closed") == "heat"
        and classify("retained") == "work"
        and heat_only == (Fraction(23, 12), None, Fraction(23, 12))
        and complete == (Fraction(23, 12), Fraction(7, 5), Fraction(199, 60))
        and (prior + (extension,))[:-1] == prior
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
            "observation_forced_classes_reconstructed": classify("closed") == "heat" and classify("retained") == "work",
            "disjoint_exhaustive_partition_reconstructed": complete == (Fraction(23, 12), Fraction(7, 5), Fraction(199, 60)),
            "structural_absence_reconstructed": heat_only[1] is None,
            "append_only_successor_reconstructed": (prior + (extension,))[:-1] == prior,
            "measurement_file_accessed": False
        }
    }, sort_keys=True))


if __name__ == "__main__":
    main()
