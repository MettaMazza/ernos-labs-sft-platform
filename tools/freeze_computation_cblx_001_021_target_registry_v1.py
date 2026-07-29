#!/usr/bin/env python3
"""Freeze CBLX claim identities and questions before observation access."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/computation_cblx_001_021_target_registry_v1.json"
IDS = (
    "SFT-COMP-CBLX-DECIDABLE-RECOGNIZABLE-CLOSURE-001",
    "SFT-COMP-CBLX-CO-RECOGNIZABLE-BOUNDARY-002",
    "SFT-COMP-CBLX-DOVETAIL-ENUMERATION-003",
    "SFT-COMP-CBLX-DIAGONAL-LANGUAGE-004",
    "SFT-COMP-CBLX-SELF-REFERENCE-FIXED-POINT-005",
    "SFT-COMP-CBLX-RECURSION-THEOREM-006",
    "SFT-COMP-CBLX-SEMANTIC-PROPERTY-UNDECIDABILITY-007",
    "SFT-COMP-CBLX-MANY-ONE-REDUCTION-008",
    "SFT-COMP-CBLX-TURING-REDUCTION-009",
    "SFT-COMP-CBLX-ENUMERATION-REDUCIBILITY-010",
    "SFT-COMP-CBLX-DEGREE-ORDER-011",
    "SFT-COMP-CBLX-JUMP-RELATIVE-SUCCESSION-012",
    "SFT-COMP-CBLX-ORACLE-ANSWER-CUSTODY-013",
    "SFT-COMP-CBLX-ARITHMETICAL-HIERARCHY-BOUNDARY-014",
    "SFT-COMP-CBLX-POST-CORRESPONDENCE-WITNESS-015",
    "SFT-COMP-CBLX-ENTSCHEIDUNGSPROBLEM-BOUNDARY-016",
    "SFT-COMP-CBLX-INCOMPLETENESS-CONSISTENCY-BOUNDARY-017",
    "SFT-COMP-CBLX-BUSY-BEAVER-DOMINATION-018",
    "SFT-COMP-CBLX-BUSY-BEAVER-FINITE-CENSUS-019",
    "SFT-COMP-CBLX-HYPERCOMPUTATION-ADMISSIBILITY-020",
    "SFT-COMP-CBLX-COMPLETENESS-021",
)


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("CBLX target registry already frozen")
    census = json.loads((ROOT / "census/computation_discipline_obligations.json").read_text())
    rows = [row for row in census["obligations"] if row["family"] == "CBLX"]
    if len(rows) != len(IDS) or len(IDS) != 21:
        raise SystemExit("CBLX census changed")
    payload = {
        "schema": "sft-v3-classical-computation-cblx-value-free-registry/1",
        "date": "2026-07-29", "authority": "Maria Smith",
        "frozen_before_observation_access": True, "target_content_present": False,
        "classical_computation_census_identity": census["census_identity"],
        "claim_ids": IDS, "obligation_ids": [row["obligation_id"] for row in rows],
        "question_titles": [row["title"] for row in rows],
        "completion_unit": "all twenty-one claims; no proper subset",
        "prohibited_target_fields": ["expected computability result", "selected survivor", "match result", "imported theorem answer"],
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(IDS), "identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__": main()
