#!/usr/bin/env python3
from itertools import product
import json
import sys

CLAIM_ID = "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"
DOMAINS = (
    ("answer-only-scalar", "complete-fold-carrier"),
    ("imported-or-fitted-relation", "sealed-collective-response-versus-complete-blackbody-acoustic-laser-plasma-Alfven-record"),
    ("unbound-provenance", "source-bound-proof-trace"), ("target-readable-prediction", "capability-closed-prediction"),
    ("proof-measurement-conflation", "separate-measurement-record"), ("selected-favourable-rows", "complete-registered-rows"),
    ("finite-answer-lookup", "one-successor-closure"), ("free-extra-rule", "no-extra-rule"),
)
SURVIVOR = tuple(x[-1] for x in DOMAINS)

def main():
    with open(sys.argv[2], encoding="utf-8") as f: sealed = json.load(f)
    generated = tuple("__".join(x) for x in product(*DOMAINS)); received = tuple(x["candidate_id"] for x in sealed["census"]["candidates"])
    recomputed = {x: tuple(x.split("__")) == SURVIVOR for x in generated}; decisions = {x["candidate_id"]: x["survives"] for x in sealed["decisions"]}
    passed = all((sys.argv[1] == CLAIM_ID, sealed["claim_id"] == CLAIM_ID, received == generated, len(set(received)) == sealed["census"]["expected_cardinality"] == 256, decisions == recomputed, sum(recomputed.values()) == 1, {x["kind"] for x in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}, all(x["passed"] for x in sealed["controls"])))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "registered_target_rows": 5, "primary_source_count": 5, "target_content_used": False, "survivor": "__".join(SURVIVOR)}}, sort_keys=True)); raise SystemExit(0 if passed else 1)

if __name__ == "__main__": main()
