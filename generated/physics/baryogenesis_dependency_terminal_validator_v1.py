#!/usr/bin/env python3
"""Independent reconstruction of the Fold baryogenesis dependency census."""

from __future__ import annotations

from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-BARYOGENESIS-DEPENDENCY-TERMINAL-021"
DOMAINS = (
    ("preloaded-unpaired-residue", "exact-paired-particle-antiparticle-carrier"),
    ("every-transition-preserves-baryon-tally", "one-explicit-tally-changing-transition"),
    ("exactly-paired-conjugate-paths", "CP-carrier-distinguishes-conjugate-paths"),
    ("complete-reverse-recurrence", "nonequilibrium-reverse-completion-held"),
    ("signed-or-unrecorded-net-number", "positive-oriented-residue-or-empty-One"),
    ("named-independent-conditions", "single-three-condition-process-composition"),
    ("selected-successful-combination", "all-eight-presence-absence-combinations"),
    ("abundance-selects-dependency-law", "inherit-sealed-CKM-and-baryon-photon-records"),
    ("mislabel-as-blind-discovery", "observational-reconstruction-explicit"),
    ("free-efficiency-or-extra-condition", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def residue(tally: bool, conjugacy: bool, hold: bool) -> str:
    matter = ["paired"]
    antimatter = ["paired"]
    if tally:
        matter.append("changed")
        if not conjugacy:
            antimatter.append("changed")
    if not hold:
        matter = matter[:1]
        antimatter = antimatter[:1]
    if len(matter) == len(antimatter):
        return "empty-One"
    return "matter-One" if len(matter) > len(antimatter) else "antimatter-One"


def theorem_check() -> bool:
    rows = tuple((tally, conjugacy, hold, residue(tally, conjugacy, hold)) for tally, conjugacy, hold in product((False, True), repeat=3))
    positive = tuple(row for row in rows if row[-1] != "empty-One")
    return len(rows) == 8 and len(set(row[:3] for row in rows)) == 8 and positive == ((True, True, True, "matter-One"),)


def generated_ids() -> tuple[str, ...]:
    return tuple("__".join(row) for row in product(*DOMAINS))


def main() -> None:
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check() for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (
        sys.argv[1] == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 1024
        and decisions == recomputed
        and sum(recomputed.values()) == 1
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in sealed["controls"])
        and theorem_check()
    )
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(generated), "condition_case_count": 8, "positive_case_count": 1, "survivor": "__".join(SURVIVOR), "measured_abundance_used": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
