"""Implementation-distinct validator for the v3 root theorem.

This file imports no SFT package or root-theorem implementation.
"""

import hashlib
import json
import sys


GENERATION_RULE = (
    "Partition every purported operational counterexample by whether it emits "
    "an identifiable presentation at the proof boundary."
)
GRAMMAR_BOUNDARY = (
    "All operational statements, denials, records and proof challenges, "
    "independent of their internal length or notation."
)


def identity(value):
    encoded = json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def records():
    return (
        {
            "candidate_id": "unpresented-absence",
            "presented": False,
            "exact_form": (
                "No statement, denial, record, trace or identity is presented; "
                "there is therefore no operational counterexample to admit."
            ),
        },
        {
            "candidate_id": "presented-occurrence",
            "presented": True,
            "exact_form": (
                "A statement, denial, record, trace or identity is presented; "
                "that presentation is an occurrence and therefore is not nothing."
            ),
        },
    )


def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = records()
    expected_candidates = []
    expected_decisions = []
    for record in generated:
        expected_candidates.append(
            {
                "candidate_id": record["candidate_id"],
                "exact_form": record["exact_form"],
                "trace_hash": identity(
                    {"generator": GENERATION_RULE, "generated_record": record}
                ),
            }
        )
        presented = record["presented"] is True
        reason = (
            "Presentation supplies the witnessed occurrence required by the theorem."
            if presented
            else "Without a presentation there is no counterexample object to admit."
        )
        decision = {
            "candidate_id": record["candidate_id"],
            "survives": presented,
            "reason": reason,
        }
        expected_decisions.append(
            {
                **decision,
                "proof_hash": identity(
                    {
                        "candidate": record,
                        "decision": decision,
                        "rule": (
                            "presentation entails an occurrence; nonpresentation "
                            "supplies no challenge"
                        ),
                    }
                ),
            }
        )
    census = sealed["census"]
    passed = (
        sealed["claim_id"] == "SFT-ROOT-THERE-IS-NO-NOTHING"
        and census["generation_rule"] == GENERATION_RULE
        and census["grammar_boundary"] == GRAMMAR_BOUNDARY
        and census["expected_cardinality"] == len(generated)
        and census["candidates"] == expected_candidates
        and sealed["decisions"] == expected_decisions
        and [item["survives"] for item in sealed["decisions"]] == [False, True]
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and len(sealed["controls"]) == len({item["kind"] for item in sealed["controls"]}) == 4
        and all(item["passed"] is True for item in sealed["controls"])
    )
    certificate = {
        "partition_classes": [record["candidate_id"] for record in generated],
        "survivor": "presented-occurrence" if passed else None,
        "operational_boundary": GRAMMAR_BOUNDARY,
        "control_kinds": sorted(item["kind"] for item in sealed["controls"]),
    }
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": certificate,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
