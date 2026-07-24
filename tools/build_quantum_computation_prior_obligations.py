#!/usr/bin/env python3
"""Build the 763-entry categorical-owner audit for Quantum Computation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "census/quantum_computation_prior_obligations.json"

STEP_CLAIMS = {
    351: ("SFT-QUANTUM-COMPLEXITY-001",),
    372: ("SFT-QUANTUM-ALGORITHMS-001",),
    397: (
        "SFT-QUANTUM-REVERSIBLE-MODEL-001", "SFT-QUANTUM-INFORMATION-UNIT-001",
        "SFT-QUANTUM-STATE-COMPOSITION-001", "SFT-QUANTUM-SUPERPOSITION-001",
        "SFT-QUANTUM-PHASE-INTERFERENCE-001", "SFT-QUANTUM-ENTANGLEMENT-001",
        "SFT-QUANTUM-MEASUREMENT-001",
    ),
    398: (
        "SFT-QUANTUM-GATE-001", "SFT-QUANTUM-CIRCUIT-001", "SFT-QUANTUM-UNIVERSALITY-001",
        "SFT-QUANTUM-ALGORITHMS-001", "SFT-QUANTUM-COMPLEXITY-001",
    ),
    399: (
        "SFT-QUANTUM-COMMUNICATION-001", "SFT-QUANTUM-CODING-001",
        "SFT-QUANTUM-ERROR-CORRECTION-001", "SFT-QUANTUM-FAULT-TOLERANCE-001",
    ),
    400: (
        "SFT-QUANTUM-SIMULATION-001", "SFT-QUANTUM-VERIFICATION-001", "SFT-QUANTUM-LEARNING-001",
        "SFT-QUANTUM-CLASSICAL-CORRESPONDENCE-001", "SFT-QUANTUM-LIMITS-001",
    ),
    403: ("SFT-QUANTUM-ERROR-CORRECTION-001", "SFT-QUANTUM-FAULT-TOLERANCE-001"),
    407: ("SFT-QUANTUM-UNBOUNDED-FINITE-FAULT-TOLERANCE-002",),
}


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def atom(step: int, claim_id: str, claim_rows: dict[str, dict]) -> dict:
    row = claim_rows[claim_id]
    return {
        "atomic_obligation_id": f"V2-{step}-{claim_id}",
        "categorical_owner": "quantum_computation",
        "prior_observation": f"Same-strength reconstruction of {row['title']}: {row['statement']}",
        "v3_claim_ids": [claim_id],
        "resolution_kind": "reconstructed",
        "same_strength_closed": bool(row.get("model_admitted")),
        "disposition": "closed" if row.get("model_admitted") else "open",
        "reason": "The mapped current V3 claim carries a model-admitted, implementation-distinct receipt at the exact formal boundary." if row.get("model_admitted") else "Mapped claim is not admitted.",
    }


def main() -> None:
    v1 = read("audits/v1_theorem_manifest_observation_census.json")
    v2 = read("audits/v2_407_step_observation_census.json")
    claim_rows = {row["claim_id"]: row for row in read("census/claims.json")["claims"]}
    v2_rows = {row["step"]: row for row in v2["steps"]}
    entries = []
    for step, claims in STEP_CLAIMS.items():
        entries.append({
            "source": "v2", "source_entry": step,
            "source_hash": v2_rows[step]["source_block_sha256"],
            "source_observation": v2_rows[step]["prior_result_observation"],
            "atomic_obligations": [atom(step, claim, claim_rows) for claim in claims],
        })
    step = 402
    composite_atoms = (
        ("QUANTUM-SUPPORT-SUCCESSOR", "The complete b-way quantum support successor is reconstructed at every supplied finite depth.", ("SFT-QUANTUM-SUPERPOSITION-001",)),
        ("QUANTUM-CIRCUIT-RESOURCE-SUCCESSOR", "Quantum circuit support, size, width and depth retain exact base/successor resource recurrences.", ("SFT-QUANTUM-CIRCUIT-001", "SFT-QUANTUM-COMPLEXITY-001")),
        ("QUANTUM-REVERSE-RECORD-SUCCESSOR", "Each fresh quantum observation or reversible Fold layer adds its exact retained inverse record.", ("SFT-QUANTUM-REVERSIBLE-MODEL-001", "SFT-QUANTUM-MEASUREMENT-001")),
    )
    rows = []
    for slug, observation, claims in composite_atoms:
        closed = all(claim_rows[claim].get("model_admitted") for claim in claims)
        rows.append({
            "atomic_obligation_id": f"V2-402-{slug}", "categorical_owner": "quantum_computation",
            "prior_observation": observation, "v3_claim_ids": list(claims), "resolution_kind": "reconstructed",
            "same_strength_closed": closed, "disposition": "closed" if closed else "open",
            "reason": "Every mapped V3 claim is model-admitted at the exact base/successor boundary." if closed else "A mapped claim remains open.",
        })
    entries.insert(6, {"source": "v2", "source_entry": step, "source_hash": v2_rows[step]["source_block_sha256"], "source_observation": v2_rows[step]["prior_result_observation"], "atomic_obligations": rows})
    atoms = [item for entry in entries for item in entry["atomic_obligations"]]
    open_atoms = [item for item in atoms if not item["same_strength_closed"]]
    relevant = set(STEP_CLAIMS).union({402})
    excluded_v1 = [row["v1_claim_id"] for row in v1["rows"]]
    excluded_v2 = [row["step"] for row in v2["steps"] if row["step"] not in relevant]
    exclusion = json.dumps({"v1": excluded_v1, "v2": excluded_v2}, separators=(",", ":"), sort_keys=True).encode()
    payload = {
        "schema": "sft-v3-quantum-computation-prior-obligation-ledger/1",
        "status": "closed" if not open_atoms else "open",
        "measurement_boundary": {
            "formal_branch_has_natural_measured_value": False,
            "applicable_external_validation": "implementation-distinct exact regeneration plus complete declared finite execution",
            "reason": "A formal code width, branch support or circuit trace is not a measured physical constant. Device fidelity, physical error rates and hardware threshold constants require post-seal Physics or engineering measurements and cannot select this branch's laws.",
            "downstream_empirical_components_retained": ["physical realization of quantum operations", "measured hardware error distributions", "hardware fault thresholds", "energy and timing costs", "application performance"],
        },
        "source_policy": {
            "prior_results_are_observational_reconstruction_requirements": True,
            "prior_executable_answers_are_not_derivational_inputs": True,
            "physical_quantum_effects_are_owned_by_physics": True,
            "formal_quantum_information_and_machine_laws_are_owned_here": True,
            "unbounded_finite_fault_order_is_not_a_physical_threshold_constant": True,
        },
        "reviewed_source_surface": {
            "v1_total_rows": v1["source_row_count"], "v2_total_steps": v2["source_step_count"],
            "reviewed_entry_count": v1["source_row_count"] + v2["source_step_count"],
            "review_complete_for_branch_ownership": True,
            "quantum_computation_relevant_v1_rows": [],
            "quantum_computation_relevant_v2_steps": sorted(relevant),
            "reviewed_nonquantum_computation_v1_rows": excluded_v1,
            "reviewed_nonquantum_computation_v2_steps": excluded_v2,
            "nonowner_exclusion_identity": "sha256:" + hashlib.sha256(exclusion).hexdigest(),
        },
        "source_entries": entries,
        "quantum_computation_summary": {
            "atomic_obligation_count": len(atoms),
            "same_strength_closed_count": len(atoms) - len(open_atoms),
            "open_count": len(open_atoms),
            "open_atomic_obligation_ids": [item["atomic_obligation_id"] for item in open_atoms],
            "new_same_strength_claim_count": 1,
            "physical_quantum_v1_rows_deferred_to_physics": True,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: quantum={len(atoms)} open={len(open_atoms)}")


if __name__ == "__main__":
    main()

