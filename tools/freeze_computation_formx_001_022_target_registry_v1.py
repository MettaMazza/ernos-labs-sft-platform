#!/usr/bin/env python3
"""Freeze FORMX claim identities and questions before observation access."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/computation_formx_001_022_target_registry_v1.json"
IDS = (
    "SFT-COMP-FORMX-CONFIGURATION-IDENTITY-001",
    "SFT-COMP-FORMX-PARTIAL-TOTAL-TRANSITION-002",
    "SFT-COMP-FORMX-TERMINAL-OUTCOME-DISTINCTION-003",
    "SFT-COMP-FORMX-LANGUAGE-BOOLEAN-CORRESPONDENCE-004",
    "SFT-COMP-FORMX-CONCATENATION-ITERATION-005",
    "SFT-COMP-FORMX-DERIVATION-TREE-AMBIGUITY-006",
    "SFT-COMP-FORMX-PARSE-RECOGNIZE-GENERATE-007",
    "SFT-COMP-FORMX-AUTOMATON-PRODUCT-QUOTIENT-008",
    "SFT-COMP-FORMX-FINITE-TRANSDUCTION-009",
    "SFT-COMP-FORMX-STORAGE-MACHINE-CORRESPONDENCE-010",
    "SFT-COMP-FORMX-REWRITE-NORMAL-FORM-011",
    "SFT-COMP-FORMX-REWRITE-CONFLUENCE-012",
    "SFT-COMP-FORMX-RECURSIVE-COMPOSITION-013",
    "SFT-COMP-FORMX-PRIMITIVE-RECURSION-MINIMIZATION-014",
    "SFT-COMP-FORMX-LAMBDA-CAPTURE-NORMAL-015",
    "SFT-COMP-FORMX-MACHINE-SIMULATION-INVARIANT-016",
    "SFT-COMP-FORMX-CIRCUIT-ACYCLIC-EVALUATION-017",
    "SFT-COMP-FORMX-SEQUENTIAL-COMBINATIONAL-018",
    "SFT-COMP-FORMX-PROCESS-ALGEBRA-EQUIVALENCE-019",
    "SFT-COMP-FORMX-UNIVERSAL-SELF-INTERPRETATION-020",
    "SFT-COMP-FORMX-MODEL-TRANSLATION-OVERHEAD-021",
    "SFT-COMP-FORMX-COMPLETENESS-022",
)


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("FORMX target registry already frozen")
    census = json.loads((ROOT / "census/computation_discipline_obligations.json").read_text())
    rows = [row for row in census["obligations"] if row["family"] == "FORMX"]
    if len(rows) != len(IDS) or len(IDS) != 22:
        raise SystemExit("FORMX census changed")
    payload = {
        "schema": "sft-v3-classical-computation-formx-value-free-registry/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "frozen_before_observation_access": True,
        "target_content_present": False,
        "classical_computation_census_identity": census["census_identity"],
        "claim_ids": IDS,
        "obligation_ids": [row["obligation_id"] for row in rows],
        "question_titles": [row["title"] for row in rows],
        "completion_unit": "all twenty-two claims; no proper subset",
        "prohibited_target_fields": [
            "expected execution outcome",
            "selected survivor",
            "match result",
            "imported automata or computability theorem answer",
        ],
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(IDS), "identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
