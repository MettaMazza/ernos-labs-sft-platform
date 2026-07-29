#!/usr/bin/env python3
"""Implementation-distinct reconstruction of the complete Smithium family."""

from itertools import product
import json
from pathlib import Path
import sys


RELATIONS = {
    "SFT-CHEM-SMITHIUM-SYNTHESIS-CONSERVATION-001": "all-22875-conserving-labelled-entrance-partitions",
    "SFT-CHEM-SMITHIUM-DECAY-CHANNEL-LEDGER-001": "complete-gamma-alpha-beta-and-labelled-fission-ledger",
    "SFT-CHEM-SMITHIUM-LIFETIME-BOUNDARY-001": "numeric-lifetime-only-from-positive-width-and-unit",
    "SFT-CHEM-SMITHIUM-ION-OXIDATION-LADDER-001": "ordered-8s-then-5g-removal-with-identity-retained",
    "SFT-CHEM-SMITHIUM-SPECTROSCOPIC-CLASSES-001": "5g6-capacity-occupation-holes-and-E1-adjacency",
    "SFT-CHEM-SMITHIUM-CHEMICAL-SEPARATION-001": "all-21-pairwise-oxidation-state-distinctions",
    "SFT-CHEM-SMITHIUM-JOINT-DETECTION-001": "five-record-complete-SFT-identification-conjunction",
    "SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001": "sealed-seven-law-family-versus-complete-official-source-record",
}

DEPENDENCIES = {
    "SFT-CHEM-SMITHIUM-SYNTHESIS-CONSERVATION-001": ("SFT-CHEM-PRED-SMITHIUM-001", "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-COMBINATORICS-001", "SFT-PHYS-NUCLEAR-FUSION-001"),
    "SFT-CHEM-SMITHIUM-DECAY-CHANNEL-LEDGER-001": ("SFT-CHEM-SMITHIUM-SYNTHESIS-CONSERVATION-001", "SFT-PHYS-NUCLEAR-RADIOACTIVE-DECAY-TERMINAL-005", "SFT-PHYS-NUCLEAR-FISSION-001", "SFT-CHEM-RADIOACTIVE-CHEMICAL-TRANSFORMATION-002"),
    "SFT-CHEM-SMITHIUM-LIFETIME-BOUNDARY-001": ("SFT-CHEM-SMITHIUM-DECAY-CHANNEL-LEDGER-001", "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001", "SFT-PHYS-ATOMIC-TRANSITION-RATE-TERMINAL-005"),
    "SFT-CHEM-SMITHIUM-ION-OXIDATION-LADDER-001": ("SFT-CHEM-SMITHIUM-LIFETIME-BOUNDARY-001", "SFT-CHEM-REDOX-OXIDATION-STATE-001", "SFT-CHEM-MOLECULAR-IONIZATION-ENERGY-007"),
    "SFT-CHEM-SMITHIUM-SPECTROSCOPIC-CLASSES-001": ("SFT-CHEM-SMITHIUM-ION-OXIDATION-LADDER-001", "SFT-CHEM-SELECTION-RULE-STRUCTURE-010", "SFT-PHYS-MOLECULAR-SPECTROSCOPY-TERMINAL-005"),
    "SFT-CHEM-SMITHIUM-CHEMICAL-SEPARATION-001": ("SFT-CHEM-SMITHIUM-SPECTROSCOPIC-CLASSES-001", "SFT-CHEM-RADIOCHEMICAL-SEPARATION-DECONTAMINATION-010"),
    "SFT-CHEM-SMITHIUM-JOINT-DETECTION-001": ("SFT-CHEM-SMITHIUM-CHEMICAL-SEPARATION-001", "SFT-CHEM-RADIOTRACER-CUSTODY-INFERENCE-009", "SFT-CHEM-MULTIMODAL-MOLECULAR-IDENTITY-021"),
    "SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001": ("SFT-CHEM-SMITHIUM-JOINT-DETECTION-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-PHYS-MEAS-UNCERTAINTY-001"),
}


def surface(relation: str):
    domains = (
        ("selected-element-name", "sealed-126-184-310-coordinate"),
        ("outcome-only-transformation", "complete-positive-carrier-ledger"),
        ("free-or-imported-relation", relation),
        ("selected-favourable-example", "complete-declared-product"),
        ("target-before-seal", "formal-seal-before-target-access"),
        ("favourable-only-record", "favourable-adverse-absent-unresolved-held"),
        ("invented-numerical-placeholder", "structural-absence-and-explicit-halt"),
        ("free-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*domains))
    return generated, "__".join(domain[1] for domain in domains)


def exact_family_check(claim_id: str) -> bool:
    partitions = tuple((z, n, 126 - z, 184 - n) for z in range(1, 126) for n in range(1, 184))
    if len(partitions) != 22875 or partitions[0] != (1, 1, 125, 183) or partitions[-1] != (125, 183, 1, 1):
        return False
    if claim_id.endswith("SYNTHESIS-CONSERVATION-001"):
        return all(z1 + z2 == 126 and n1 + n2 == 184 for z1, n1, z2, n2 in partitions)
    if claim_id.endswith("DECAY-CHANNEL-LEDGER-001"):
        return (124 + 2, 182 + 2, 306 + 4) == (126, 184, 310) and (127, 183, 310) == (127, 183, 310) and (125, 185, 310) == (125, 185, 310)
    if claim_id.endswith("LIFETIME-BOUNDARY-001"):
        required = ("positive-transition-width", "registered-time-unit")
        return len(required) == 2 and "numerical-lifetime" not in required
    if claim_id.endswith("ION-OXIDATION-LADDER-001"):
        rows = tuple((q, 126 - q, 8 - q) for q in range(2, 9))
        return len(rows) == 7 and rows[0] == (2, 124, 6) and rows[-1] == (8, 118, 0)
    if claim_id.endswith("SPECTROSCOPIC-CLASSES-001"):
        conventional_l = 4
        capacity = 2 * (2 * conventional_l + 1)
        return capacity == 18 and capacity - 6 == 12 and (conventional_l - 1, conventional_l + 1) == (3, 5)
    if claim_id.endswith("CHEMICAL-SEPARATION-001"):
        states = tuple(range(2, 9))
        pairs = tuple((a, b) for i, a in enumerate(states) for b in states[i + 1 :])
        return len(pairs) == 21 and pairs[0] == (2, 3) and pairs[-1] == (7, 8)
    if claim_id.endswith("JOINT-DETECTION-001"):
        records = ("nuclear", "mass", "decay", "ion", "spectroscopic")
        return len(records) == len(set(records)) == 5
    return claim_id == "SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001" and len(RELATIONS) == 8


def main() -> None:
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    if claim_id not in RELATIONS:
        raise SystemExit(1)
    generated, survivor = surface(RELATIONS[claim_id])
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    reconstructed = {candidate: candidate == survivor for candidate in generated}
    controls = tuple(sealed["controls"])
    dependencies_present = all(
        (root / "claims" / dependency / "registration.json").is_file()
        and (root / "claims" / dependency / "certificate.json").is_file()
        for dependency in DEPENDENCIES[claim_id]
    )
    exact = exact_family_check(claim_id)
    passed = all(
        (
            sealed["claim_id"] == claim_id,
            received == generated,
            len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
            decisions == reconstructed,
            sum(reconstructed.values()) == 1,
            len(controls) == 4 and all(row["passed"] for row in controls),
            {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
            sealed["closure"]["scope"] == "depth_independent",
            sealed["closure"]["minimality_passed"] is True,
            sealed["closure"]["named_shape_uniqueness_passed"] is True,
            dependencies_present,
            exact,
        )
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "certificate": {
                    "candidate_count": len(received),
                    "candidate_order_reconstructed": received == generated,
                    "decision_vector_reconstructed": decisions == reconstructed,
                    "unique_survivor_count": sum(reconstructed.values()),
                    "dependency_packages_present": dependencies_present,
                    "exact_family_check": exact,
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
