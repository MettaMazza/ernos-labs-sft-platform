#!/usr/bin/env python3
"""Build the complete V1/V2 Classical Computation ownership ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2 = ROOT / "audits/v2_407_step_observation_census.json"
OUTPUT = ROOT / "census/computation_prior_obligations.json"


def atom(atomic_id: str, statement: str, claims: tuple[str, ...], resolution: str = "reconstructed") -> dict[str, object]:
    return {
        "atomic_obligation_id": atomic_id, "prior_observation": statement, "categorical_owner": "computation",
        "v3_claim_ids": list(claims), "resolution_kind": resolution, "same_strength_closed": False,
        "disposition": "open_reconstruction_required", "reason": "Every mapped V3 computation claim must carry a model-admitted receipt at the same declared boundary.",
    }


V1_DECOMPOSITION: dict[str, tuple[dict[str, object], ...]] = {
    "XII-4": (
        atom("V1-XII4-BOUNDED-HALT-OR-CYCLE", "Every process on a complete finite generated carrier is decidable as terminal or recurrent by exhaustive state execution.", ("SFT-COMP-CBL-RECOGNITION-DECISION-001", "SFT-COMP-CBL-HALTING-001")),
        atom("V1-XII4-SELF-NEGATION-UNDECIDABILITY", "The unrestricted total internal decider fails where generated self-description and held complement produce the exact contradiction trace.", ("SFT-COMP-CBL-UNDECIDABILITY-001",), "reconciled_proof_correction"),
        atom("V1-XII4-ADMISSIBILITY-BOUNDARY", "Finite decidability does not license an undeclared oracle or completed-infinite computation.", ("SFT-COMP-CBL-HYPERCOMPUTATION-LIMIT-001",)),
    ),
    "XII-5": (
        atom("V1-XII5-P-NP-BOUNDARY", "The conventional P-versus-NP question remains outside the imported-language boundary, while the later native Fold comparison is separately forced.", ("SFT-COMP-CPLX-FOLD-P-NP-EQUALITY-002",), "reconciled_later_native_closure"),
    ),
    "XIV-4": (
        atom("V1-XIV4-BOUNDED-SIMULATION", "Every bounded generated sub-process has a complete exact simulation trace.", ("SFT-COMP-SCI-SIMULATION-001", "SFT-COMP-CBL-UNIVERSAL-MACHINE-001")),
        atom("V1-XIV4-TOTAL-SELF-SIMULATION-BOUNDARY", "A complete self-containing one-to-one internal simulation is blocked by self-description and observation loss.", ("SFT-COMP-CBL-INCOMPLETENESS-001", "SFT-COMP-CBL-UNDECIDABILITY-001")),
        atom("V1-XIV4-FINITE-NESTING", "Nested simulations are admitted only as generated finite composed processes with explicit resource and interface ledgers.", ("SFT-COMP-FORM-COMPOSITION-001", "SFT-COMP-CBL-HYPERCOMPUTATION-LIMIT-001")),
    ),
    "XIV-8": (
        atom("V1-XIV8-SEARCH-TO-EXACT-DESCENT", "Native Fold search follows its exact generated transition depth rather than importing a logarithmic or heuristic answer model.", ("SFT-COMP-ALG-SEARCH-ORDER-001", "SFT-COMP-CPLX-TIME-SPACE-001"), "reconciled_no_logarithm"),
        atom("V1-XIV8-BOUNDED-DECISION", "A bounded process is guaranteed to halt or cycle and the class is decidable; it is not falsely guaranteed to halt.", ("SFT-COMP-CBL-HALTING-001", "SFT-COMP-CBL-RECOGNITION-DECISION-001"), "reconciled_halt_or_cycle_correction"),
        atom("V1-XIV8-DISTRIBUTED-INTEGRATION", "Distributed integration requires exact synchronization, causal and consensus records rather than a hidden coordinator.", ("SFT-COMP-DIST-SYNCHRONIZATION-001", "SFT-COMP-DIST-CONSENSUS-001")),
        atom("V1-XIV8-INVARIANT-CORRECTNESS", "A registered invariant and complete proof trace provide an immediate correctness and verification boundary.", ("SFT-COMP-SEM-CORRECTNESS-001", "SFT-COMP-SEM-VERIFICATION-001")),
    ),
    "X-3": (
        atom("V1-X3-CLASSICAL-TEMPLATE-COPY", "A definite generated classical word can be read and copied with full source and output provenance.", ("SFT-COMP-ALG-STRINGS-SEQUENCES-001", "SFT-COMP-DIST-REPLICATION-CONSISTENCY-001")),
        atom("V1-X3-TEMPLATE-CONSTRUCTOR", "The minimal internal replicator is a held template composed with a source-bound copy process; external process or file replication is not required.", ("SFT-COMP-FORM-RECURSIVE-FUNCTION-001", "SFT-COMP-FORM-OPERATIONAL-PROCESS-001", "SFT-COMP-FORM-COMPOSITION-001")),
    ),
    "C-1": (atom("V1-C1-SIMULATION-KERNEL", "A lawful simulation is an exact registered state-transition trace driven only by its sealed model relation.", ("SFT-COMP-SCI-SIMULATION-001", "SFT-COMP-SCI-MATHEMATICAL-MODELLING-001")),),
    "C-2": (atom("V1-C2-DEPENDENCY-ORDERED-SIMULATION", "A multi-stage simulation preserves the dependency order and proof identity of every stage.", ("SFT-COMP-FORM-COMPOSITION-001", "SFT-COMP-SCI-SIMULATION-001")),),
}


DIRECT_V2_STEPS = (
    325, 327, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345,
    346, 347, 348, 349, 350, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364,
    365, 366, 367, 368, 369, 370, 371, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383,
    392, 393, 394, 395, 396,
)


SPECIAL_V2: dict[int, tuple[dict[str, object], ...]] = {
    402: (
        atom("V2-402-STATE-SUPPORT-SUCCESSOR", "Prepending one native label forces the next complete state and description support.", ("SFT-COMP-FORM-STATE-TRANSITION-001", "SFT-COMP-CPLX-INPUT-SIZE-001")),
        atom("V2-402-CIRCUIT-SUCCESSOR", "The same label successor adds the next circuit layer with exact width, depth and size ledgers.", ("SFT-COMP-CPLX-CIRCUIT-RESOURCE-001", "SFT-COMP-CPLX-ARBITRARY-CIRCUIT-LOWER-BOUND-002")),
        atom("V2-402-REVERSE-RECORD-SUCCESSOR", "One new closing edge requires one additional held reverse label.", ("SFT-COMP-CPLX-REVERSIBILITY-COST-001",)),
    ),
    404: (atom("V2-404-NATIVE-BUSY-BEAVER", "For every supplied positive finite native description depth k, the complete closing-process maximum is BB_F(k)=k and recurrent processes are certified nonhalting.", ("SFT-COMP-CBL-NATIVE-BUSY-BEAVER-002",)),),
    405: (atom("V2-405-NATIVE-P-NP", "Exact evaluation emits the sound complete certificate and sound verification forces the unique evaluation, so P_F=NP_F inside the admitted native grammar.", ("SFT-COMP-CPLX-FOLD-P-NP-EQUALITY-002",)),),
    406: (atom("V2-406-ADMITTED-CIRCUIT-LOWER-BOUNDS", "Every admitted Fold-edge circuit requires path k, width b^k and complete layered edge sum; the registered circuit attains all bounds.", ("SFT-COMP-CPLX-ARBITRARY-CIRCUIT-LOWER-BOUND-002",)),),
}


def main() -> None:
    v1 = json.loads(V1.read_text(encoding="utf-8")); v2 = json.loads(V2.read_text(encoding="utf-8"))
    v1_rows = {row["v1_claim_id"]: row for row in v1["rows"]}; v2_rows = {row["step"]: row for row in v2["steps"]}
    claim_rows = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]}
    if set(V1_DECOMPOSITION) - set(v1_rows): raise SystemExit("Computation V1 decomposition cites an absent row")
    if set(DIRECT_V2_STEPS).union(SPECIAL_V2) - set(v2_rows): raise SystemExit("Computation V2 decomposition cites an absent step")
    entries: list[dict[str, object]] = []
    for source_id, atoms in V1_DECOMPOSITION.items():
        row = v1_rows[source_id]
        entries.append({"source": "v1", "source_entry": source_id, "source_hash": row["source_row_sha256"], "source_observation": row["prior_result_observation"], "atomic_obligations": list(atoms)})
    for step in DIRECT_V2_STEPS:
        row = v2_rows[step]; claims = tuple(claim for claim in row.get("explicit_v3_claim_ids", ()) if claim.startswith("SFT-COMP-"))
        if not claims: raise SystemExit(f"Computation Step {step} has no explicit V3 computation mapping")
        atoms = tuple(atom(f"V2-{step:03d}-{claim.removeprefix('SFT-COMP-')}", f"Same-strength reconstruction of {claim_rows[claim]['title']}: {claim_rows[claim]['statement']}", (claim,)) for claim in claims)
        entries.append({"source": "v2", "source_entry": step, "source_hash": row["source_block_sha256"], "source_observation": row["prior_result_observation"], "atomic_obligations": list(atoms)})
    for step, atoms in SPECIAL_V2.items():
        row = v2_rows[step]
        entries.append({"source": "v2", "source_entry": step, "source_hash": row["source_block_sha256"], "source_observation": row["prior_result_observation"], "atomic_obligations": list(atoms)})

    admitted = {claim for claim, row in claim_rows.items() if row.get("model_admitted")}
    atoms = [item for entry in entries for item in entry["atomic_obligations"]]
    for item in atoms:
        mapped = set(item["v3_claim_ids"])
        if mapped and mapped.issubset(admitted):
            item["same_strength_closed"] = True
            item["disposition"] = "closed" if item["resolution_kind"] == "reconstructed" else item["resolution_kind"]
            item["reason"] = "Every mapped V3 claim carries a model-admitted, independently validated receipt at the exact registered boundary."
    open_atoms = [item for item in atoms if not item["same_strength_closed"]]
    relevant_v1 = set(V1_DECOMPOSITION); relevant_v2 = set(DIRECT_V2_STEPS).union(SPECIAL_V2)
    noncomp_v1 = [key for key in v1_rows if key not in relevant_v1]; noncomp_v2 = [key for key in v2_rows if key not in relevant_v2]
    exclusion = json.dumps({"v1": noncomp_v1, "v2": noncomp_v2}, separators=(",", ":"), sort_keys=True).encode()
    payload = {
        "schema": "sft-v3-computation-prior-obligation-ledger/1", "status": "closed" if not open_atoms else "open",
        "measurement_boundary": {"formal_branch_has_natural_measured_value": False, "applicable_external_validation": "implementation-distinct exact regeneration plus complete declared finite execution", "downstream_empirical_components_retained": ["physical device time and energy: engineering and physics", "application benchmarks: application_frontier", "natural learning data: registered empirical learning claims", "quantum operations: quantum_computation"]},
        "source_policy": {"prior_results_are_observational_reconstruction_requirements": True, "prior_executable_answers_are_not_derivational_inputs": True, "composite_rows_are_decomposed": True, "later_stronger_V2_results_require_new_V3_claims": True, "corrections_are_preserved": True},
        "reviewed_source_surface": {
            "v1_total_rows": v1["source_row_count"], "v2_total_steps": v2["source_step_count"], "review_complete_for_branch_ownership": True, "reviewed_entry_count": v1["source_row_count"] + v2["source_step_count"],
            "computation_relevant_v1_rows": list(V1_DECOMPOSITION), "computation_relevant_v2_steps": sorted(relevant_v2), "reviewed_noncomputation_v1_rows": noncomp_v1, "reviewed_noncomputation_v2_steps": noncomp_v2,
            "noncomputation_exclusion_identity": "sha256:" + hashlib.sha256(exclusion).hexdigest(),
        },
        "source_entries": entries,
        "computation_summary": {"atomic_obligation_count": len(atoms), "same_strength_closed_count": len(atoms)-len(open_atoms), "open_count": len(open_atoms), "open_atomic_obligation_ids": [item["atomic_obligation_id"] for item in open_atoms], "explicit_correction_or_reconciliation_count": sum(item["resolution_kind"] != "reconstructed" for item in atoms), "new_same_strength_claim_count": 3},
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: computation={len(atoms)} open={len(open_atoms)}")


if __name__ == "__main__": main()
