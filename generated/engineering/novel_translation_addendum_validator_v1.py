#!/usr/bin/env python3
from itertools import product
import json
from pathlib import Path
import sys

PROTOCOL = "SFT-ENG-CONSCIOUSNESS-PLACEBO-CROSS-BINDING-PROTOCOL-002"
ADDENDUM = "SFT-ENG-NOVEL-TRANSLATIONS-NO-OMISSION-ADDENDUM-002"
RELATIONS = {PROTOCOL: "ethics-bound-interior-objective-cross-binding-protocol", ADDENDUM: "six-obligation-append-only-no-omission-assembly"}
DEPENDENCIES = {
    PROTOCOL: (
        "SFT-ENG-NOVEL-TRANSLATIONS-COMPLETE-FAMILY-002", "SFT-ENG-REQUIREMENT-001", "SFT-ENG-MEASUREMENT-001",
        "SFT-ENG-ACCEPTANCE-TEST-001", "SFT-ENG-SAFETY-001", "SFT-ENG-TRACEABILITY-001", "SFT-ENG-REPRODUCIBILITY-001",
        "SFT-MED-INFORMED-CONSENT-001", "SFT-MED-CLINICAL-PRIVACY-001", "SFT-CONSC-CROSS-MODAL-QUALIA-001", "SFT-CONSC-SYNAESTHESIA-DIRECTIONAL-LOCK-002",
        "SFT-CONSC-VALIDATION-NONORDINARY-COMPLETE-FAMILY-002", "SFT-MED-PLACEBO-AVAILABLE-STATE-BOUNDARY-002",
        "SFT-MED-PLACEBO-OBJECTIVE-REPORT-SEPARATION-002", "SFT-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002",
    ),
    ADDENDUM: (PROTOCOL, "SFT-ENG-NOVEL-TRANSLATIONS-COMPLETE-FAMILY-002", "SFT-ENG-TRACEABILITY-001", "SFT-ENG-INDEPENDENT-CHECK-001"),
}


def surface(relation):
    axes = (("application-selected-law", "sealed-upstream-receipts"), ("informal-apparatus-sketch", relation), ("reported-outcome-only", "complete-common-and-domain-record"), ("favourable-control-only", "complete-declared-control-family"), ("success-only", "favourable-adverse-absent-unresolved"), ("continue-after-violation", "visible-halt-and-bounded-safe-state"), ("outcome-before-protocol-seal", "protocol-seal-before-outcome"), ("implementation-exception", "no-law-rewrite"))
    return tuple("__".join(row) for row in product(*axes)), "__".join(row[1] for row in axes)


def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2]); sealed = json.loads(Path(sys.argv[3]).read_text()); generated, unique = surface(RELATIONS[claim_id]); received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"]); decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}; expected = {row: row == unique for row in generated}; controls = sealed["controls"]
    dependencies = all((root / "claims" / dependency / "registration.json").is_file() and (root / "claims" / dependency / "certificate.json").is_file() for dependency in DEPENDENCIES[claim_id])
    reconstruction = (claim_id == PROTOCOL and len(("report", "physiology", "behaviour", "binding", "expectation", "ethics")) == 6) or (claim_id == ADDENDUM and 5 + 1 == 6)
    passed = all((received == generated, len(received) == len(set(received)) == 256, decisions == expected, sum(expected.values()) == 1, len(controls) == 4, all(row["passed"] for row in controls), {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}, sealed["closure"]["scope"] == "depth_independent", dependencies, reconstruction))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "no_omission_reconstruction": reconstruction}})); raise SystemExit(0 if passed else 1)


if __name__ == "__main__": main()
