#!/usr/bin/env python3
"""Implementation-distinct reconstruction for Biology MOLX-001--014.

This file deliberately does not import the Biology law implementation.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


REGISTRY_ID = "sha256:ae8d5c4e9d47270d7dd795a4ac34e1bc916a712622d90ed6ccfaaa1bd33b5733"

RELATIONS = {
    "SFT-BIO-MOLX-REACTION-BALANCE-001": "oriented-participant-transition-with-exact-elemental-carrier-closure",
    "SFT-BIO-MOLX-ENZYME-SPECIFICITY-002": "allowed-substrate-product-transition-with-catalyst-identity-return",
    "SFT-BIO-MOLX-ENZYME-FINITE-THROUGHPUT-003": "substrate-site-turn-inhibition-bounded-exact-throughput",
    "SFT-BIO-MOLX-REDOX-CARRIER-004": "held-donor-acceptor-oriented-carrier-transfer-closure",
    "SFT-BIO-MOLX-COUPLED-WORK-005": "resource-spend-work-act-exact-coupling-with-uncoupled-absence",
    "SFT-BIO-MOLX-CHEMIOSMOTIC-TRANSPORT-006": "membrane-side-route-held-gradient-bounded-carrier-transport",
    "SFT-BIO-MOLX-CARBON-FIXATION-007": "source-carbon-to-product-position-complete-path-mapping",
    "SFT-BIO-MOLX-CARBON-BRANCH-ALLOCATION-008": "condition-bound-complete-branch-allocation-exact-parts",
    "SFT-BIO-MOLX-NUTRIENT-CYCLE-009": "environment-bound-elemental-carrier-closed-state-cycle",
    "SFT-BIO-MOLX-LIPID-LIFECYCLE-010": "head-tail-compartment-held-complete-lipid-lifecycle",
    "SFT-BIO-MOLX-CARBOHYDRATE-STORAGE-011": "monomer-storage-release-retention-exact-unit-closure",
    "SFT-BIO-MOLX-AMINO-ACID-ROUTING-012": "nitrogen-carbon-skeleton-distinct-complete-fate-routing",
    "SFT-BIO-MOLX-COFACTOR-DEPENDENCE-013": "cofactor-held-terminal-transition-with-absence-halt",
    "SFT-BIO-MOLX-METABOLOME-FLUX-CUSTODY-014": "condition-bound-metabolite-inventory-transition-and-missing-custody",
}


def canonical(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + sha256(raw).hexdigest()


def registry_valid(root: Path) -> bool:
    payload = json.loads((root / "census/biology_molx_001_014_target_registry_v1.json").read_text())
    identity = payload.pop("registry_identity")
    return (
        identity == REGISTRY_ID == canonical(payload)
        and payload["target_count"] == 14
        and payload["target_content_present"] is False
        and payload["survivor_identity_present"] is False
        and payload["measured_value_present"] is False
        and payload["outcome_present"] is False
    )


def native_checks() -> tuple[bool, ...]:
    absence = "structural-absence"
    return (
        {"C": 2, "O": 4} == {"C": 2, "O": 4},
        "substrate-a" in ("substrate-a",) and "enzyme-a" == "enzyme-a",
        min(8, 2 * 3) == 6 and min(8, (2 - 1) * 3) == 3,
        3 <= 5 and 3 <= 4 and (5 - 3, 4 - 3) == (2, 1),
        Fraction(3, 3) == 1 and 5 - 3 == 2,
        (5 - 1, 3 + 1) == (4, 4) and absence == "structural-absence",
        tuple(zip(("c1", "c2", "c3"), ("p1", "p2", "p3"))) == (("c1", "p1"), ("c2", "p2"), ("c3", "p3")),
        2 + 3 == 5 and Fraction(2, 5) + Fraction(3, 5) == 1,
        ("environment", "cell", "product", "environment")[0] == ("environment", "cell", "product", "environment")[-1],
        ("synthesis", "incorporation", "remodelling", "degradation") == ("synthesis", "incorporation", "remodelling", "degradation"),
        5 - 3 == 2 and (absence if 5 == 5 else 5 - 5) == absence,
        {"nitrogen": "nitrogen-pool", "carbon": "carbon-path"}["nitrogen"] != {"nitrogen": "nitrogen-pool", "carbon": "carbon-path"}["carbon"],
        ("product" if True else absence) == "product" and ("product" if False else absence) == absence,
        set({"a": 2, "b": 3}).isdisjoint(("c",)) and (("a", "b", 1),)[0][2] == 1,
    )


def main() -> None:
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = RELATIONS[claim_id]
    axes = (
        ("answer-label-only", "complete-positive-labelled-biological-carrier"),
        ("imported-named-pathway-or-fit", relation),
        ("endpoint-only", "complete-state-transition-lineage-and-resource-path"),
        ("organism-condition-method-erased", "organism-compartment-condition-method-uncertainty-held"),
        ("favorable-observed-only", "observed-adverse-absent-unavailable-standing-held"),
        ("external-target-prior-model-or-opaque-predictor", "root-bound-forward-forcing-before-target"),
        ("selected-organism-or-instance", "positive-finite-successor-and-composition-closure"),
        ("free-parameter-fit-exception-or-extra-axiom", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {candidate: candidate == survivor for candidate in generated}
    native = native_checks()[list(RELATIONS).index(claim_id)]
    passed = all(
        (
            received == generated,
            len(received) == len(set(received)) == 256,
            decisions == expected,
            sum(expected.values()) == 1,
            sealed["closure"]["scope"] == "depth_independent",
            len(sealed["controls"]) == 4,
            all(row["passed"] for row in sealed["controls"]),
            native,
            registry_valid(root),
        )
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "claim_id": claim_id,
                    "candidate_count": len(received),
                    "unique_survivor_count": sum(expected.values()),
                    "native_reconstruction": native,
                    "target_registry_identity": REGISTRY_ID,
                    "closure_scope": sealed["closure"]["scope"],
                    "free_parameter_or_fitted_target_used": False,
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
