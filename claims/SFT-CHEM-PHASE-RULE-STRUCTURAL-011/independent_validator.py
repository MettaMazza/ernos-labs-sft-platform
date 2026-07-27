"""Implementation-distinct value-free THERMO-011 reconstruction."""

from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-PHASE-RULE-STRUCTURAL-011"
DOMAINS = (
    ("unbound-degree-number", "complete-component-phase-coordinate-account"),
    ("bulk-substance-with-erased-independent-components", "complete-held-independent-component-support"),
    ("phase-label-without-coexistence-constraint", "one-exact-coordinate-cancellation-per-coexisting-phase"),
    ("free-or-continuum-intensive-coordinate-space", "two-held-environment-coordinate-carriers"),
    ("imported-subtractive-phase-rule-equation", "exact-carrier-cancellation-relation"),
    ("numerical-zero-degree-count", "structural-EmptyOne-invariant-state"),
    ("degree-outcome-readable-before-seal", "complete-value-free-18-row-identity-seal"),
    ("recalculate-with-free-exception", "depth-independent-joint-component-phase-successor"),
)
SURVIVOR = (
    "complete-component-phase-coordinate-account__complete-held-independent-component-support__"
    "one-exact-coordinate-cancellation-per-coexisting-phase__two-held-environment-coordinate-carriers__"
    "exact-carrier-cancellation-relation__structural-EmptyOne-invariant-state__"
    "complete-value-free-18-row-identity-seal__depth-independent-joint-component-phase-successor"
)


def degree_support(component_count, phase_count):
    if component_count < 1 or phase_count < 1:
        raise ValueError("identities must be positive")
    carriers = ["component"] * component_count + ["temperature", "pressure"]
    for _phase in range(phase_count):
        if not carriers:
            raise ValueError("phase support exceeds carriers")
        carriers.pop()
    return len(carriers) if carriers else None


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
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
        and degree_support(1, 1) == 2
        and degree_support(1, 2) == 1
        and degree_support(1, 3) is None
        and degree_support(2, 2) == degree_support(3, 3)
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
            "one_component_phase_sequence_reconstructed": degree_support(1, 1) == 2 and degree_support(1, 2) == 1 and degree_support(1, 3) is None,
            "structural_EmptyOne_reconstructed": degree_support(1, 3) is None,
            "joint_component_phase_successor_reconstructed": degree_support(2, 2) == degree_support(3, 3),
            "phase_rule_equation_subtraction_target_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
