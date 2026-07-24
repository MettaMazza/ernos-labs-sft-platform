#!/usr/bin/env python3
"""Preregister the same-strength unbounded finite quantum fault-order theorem."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.quantum_computation.current_catalog import SPECS  # noqa: E402
from sft.quantum_computation.generated_law import completeness_record  # noqa: E402
from sft.quantum_computation.lineage_laws import UNBOUNDED_FAULT_TOLERANCE as SPEC  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    claim = ROOT / "claims" / SPEC.claim_id
    write_json(claim / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "branch": "quantum_computation",
        "candidate_grammar": {
            "boundary": SPEC.grammar_boundary,
            "completeness_certificate": sha256_identity(completeness_record(SPEC)),
            "generator": SPEC.generation_rule,
        },
        "claim_id": SPEC.claim_id,
        "dependencies": SPEC.dependencies,
        "empirical_protocol": None,
        "excluded_inputs": SPEC.boundary_exclusions,
        "intended_certificate": "Independent regeneration of the 256-member product, every small fault mask, all predecessor-width counterexamples and the positive-finite fault-order successor.",
        "provenance_classes": ["forward_forcing"],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-24",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "statement": SPEC.statement,
        "status": "registered",
        "title": SPEC.title,
    })
    inventory = {
        "branch_id": "quantum_computation",
        "frozen": True,
        "current_knowledge_scope": "The complete current V3 Reversible and Quantum Computation inventory, including the constructive unbounded positive-finite fault-order theorem 2t+1, distinct from any measured physical hardware threshold.",
        "required_claim_ids": [spec.claim_id for spec in SPECS],
        "unclassified_obligations": [],
        "frontier_obligations": [],
    }
    inventory["inventory_hash"] = sha256_identity(inventory)
    write_json(ROOT / "publications/inventories/quantum_computation.json", inventory)
    print(f"registered {SPEC.claim_id}; current quantum laws={len(SPECS)}")


if __name__ == "__main__":
    main()

