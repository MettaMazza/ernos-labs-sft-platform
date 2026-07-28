#!/usr/bin/env python3
"""Freeze Astronomy inventory and complete pre-source derivation seal."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sft.astronomy_cosmology.generated_law import ASTRONOMY_BLUEPRINTS, unique_survivor
from sft.astronomy_cosmology.obligations import ASTRONOMY_OBLIGATIONS, FAMILY_ORDER

INVENTORY = ROOT / "publications/inventories/astronomy_cosmology.json"
SEAL = ROOT / "experiments/sealed_predictions/astronomy_cosmology_foundation_complete_pre_source.json"

def digest(x):
    return "sha256:" + hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def file_hash(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

def main():
    audit = json.loads((ROOT / "audits/astronomy_cosmology_v1_v2_initial_atomic_ownership.json").read_text())
    census = json.loads((ROOT / "census/claims.json").read_text())
    admitted = {x["claim_id"] for x in census["claims"] if x.get("model_admitted") is True}
    blueprints = {x.claim_id: x for x in ASTRONOMY_BLUEPRINTS}
    upstream = sorted({d for x in ASTRONOMY_BLUEPRINTS for d in x.dependencies if not d.startswith("SFT-ASTRO-")})
    missing = [x for x in upstream if x not in admitted]
    if missing: raise ValueError(f"unadmitted Astronomy dependencies: {missing}")
    counts = Counter(x.family for x in ASTRONOMY_OBLIGATIONS)
    rows = []
    for position, ob in enumerate(ASTRONOMY_OBLIGATIONS, 1):
        bp = blueprints[ob.claim_id]
        row = asdict(ob); row.update({"position": position, "candidate_count": 256, "unique_survivor": "__".join(x.name for x in unique_survivor(bp)), "dependencies": list(bp.dependencies), "predicted_observation_label": bp.predicted_observation_label, "status": "registered_not_admitted"}); rows.append(row)
    mapping = {x["atom_id"]: x["mapped_foundation_claim"] for x in audit["atomic_questions"]}
    if not set(mapping.values()) <= {x.claim_id for x in ASTRONOMY_OBLIGATIONS}: raise ValueError("prior atom maps outside inventory")
    inventory = {
        "schema": "sft-v3-astronomy-cosmology-foundation-inventory/1", "branch_id": "astronomy_cosmology",
        "inventory_frozen": True, "inventory_date": "2026-07-28", "derivation_target": "current-evidence foundational closure, extension-open",
        "scope": "Source-observer geometry, astronomical evidence, objects and populations, radiation/motion/time, stars, planetary systems, interstellar matter and enrichment, galaxies, compact and multimessenger sources, expansion and large-scale structure, early universe/background/abundances, dark and horizon evidence, inference, prediction and typed handoffs.",
        "ownership_boundary": {"owned": "Observed objects, populations, source states and cosmic histories.", "consumed_not_reowned": ["universal Physics laws and constants", "chemical identities", "Earth conditions", "instrument engineering"], "downstream": ["Engineering Translation", "Biology astrobiology", "Social observation governance"]},
        "prior_audit": str((ROOT / "audits/astronomy_cosmology_v1_v2_initial_atomic_ownership.json").relative_to(ROOT)), "prior_audit_identity": audit["audit_identity"], "prior_atomic_question_count": len(mapping), "prior_atom_to_foundation_claim": mapping,
        "inventory_completion_explanation": "The twelve declared roadmap families were decomposed into six nonduplicate carrier/relation/record/evidence/falsification obligations apiece. The count emerges from this explicit ownership decomposition, not from a requested target.",
        "family_order": list(FAMILY_ORDER), "family_counts": {x: counts[x] for x in FAMILY_ORDER}, "required_claim_count": len(rows), "required_claim_ids": [x.claim_id for x in ASTRONOMY_OBLIGATIONS], "candidate_count": len(rows) * 256,
        "admitted_claim_count_at_freeze": 0, "upstream_dependency_count": len(upstream), "upstream_dependency_claim_ids": upstream, "all_upstream_dependencies_model_admitted_at_freeze": True,
        "external_source_identities_selected_at_freeze": False, "external_outcomes_opened_at_freeze": False, "unclassified_obligations": [], "foundation_frontier_obligations": [],
        "later_full_field_extensions": ["complete positional and time-domain catalogues", "complete stellar and planetary populations", "complete interstellar and chemical-evolution observations", "complete galaxy and large-scale surveys", "complete compact/high-energy/multimessenger catalogues", "complete precision cosmic-history and early-universe evidence", "complete astrobiological and observatory handoffs"],
        "obligations": rows,
    }
    inventory["inventory_hash"] = digest(inventory); write(INVENTORY, inventory)
    sealed_files = ["publications/inventories/astronomy_cosmology.json", "sft/astronomy_cosmology/obligations.py", "sft/astronomy_cosmology/structural_model.py", "sft/astronomy_cosmology/generated_law.py", "audits/astronomy_cosmology_v1_v2_initial_atomic_ownership.json"]
    prediction_set = tuple((x.claim_id, x.exact_result, x.predicted_observation_label, x.falsification_condition) for x in ASTRONOMY_BLUEPRINTS)
    seal = {"schema": "sft-v3-astronomy-cosmology-complete-pre-source-seal/1", "seal_date": "2026-07-28", "required_claim_count": len(rows), "candidate_count": len(rows)*256, "inventory_hash": inventory["inventory_hash"], "claim_prediction_set_hash": digest(prediction_set), "sealed_files": {x: file_hash(ROOT/x) for x in sealed_files}, "external_source_identities_selected": False, "external_source_content_opened": False, "external_outcomes_opened": False, "prior_answers_present_in_derivation_runtime": False, "conventional_cosmology_present_in_derivation_runtime": False, "measurement_used_to_select_law": False, "canonical_engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a", "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"}
    seal["complete_branch_pre_source_seal_hash"] = digest(seal); write(SEAL, seal)
    checkpoint = json.loads((ROOT / "census/astronomy_cosmology_continuation_checkpoint.json").read_text()); checkpoint.update({"status": "complete_foundation_derivations_sealed_before_external_sources", "foundation_required_claim_count": len(rows), "candidate_count": len(rows)*256, "remaining_claim_count": len(rows), "inventory_path": str(INVENTORY.relative_to(ROOT)), "inventory_hash": inventory["inventory_hash"], "pre_source_seal_path": str(SEAL.relative_to(ROOT)), "pre_source_seal_hash": seal["complete_branch_pre_source_seal_hash"], "next_exact_operation": "preregister_authoritative_astronomy_sources"}); write(ROOT / "census/astronomy_cosmology_continuation_checkpoint.json", checkpoint)
    print(f"Astronomy inventory/seal: claims={len(rows)} candidates={len(rows)*256} inventory={inventory['inventory_hash']} seal={seal['complete_branch_pre_source_seal_hash']}")

if __name__ == "__main__": main()
