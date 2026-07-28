#!/usr/bin/env python3
"""Freeze the complete pre-source Earth foundation inventory."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.earth_environment.generated_law import EARTH_BLUEPRINTS, unique_survivor  # noqa: E402
from sft.earth_environment.obligations import EARTH_ENVIRONMENT_OBLIGATIONS, FAMILY_ORDER  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402


INVENTORY_PATH = ROOT / "publications/inventories/earth_environment.json"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    audit = json.loads((ROOT / "audits/earth_environment_v1_v2_initial_atomic_ownership.json").read_text(encoding="utf-8"))
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    admitted = {row["claim_id"]: row for row in census["claims"] if row.get("model_admitted") is True}
    blueprints = {row.claim_id: row for row in EARTH_BLUEPRINTS}

    upstream_dependencies = sorted({dependency for blueprint in EARTH_BLUEPRINTS for dependency in blueprint.dependencies if not dependency.startswith("SFT-EARTH-")})
    missing_upstream = [claim_id for claim_id in upstream_dependencies if claim_id not in admitted]
    if missing_upstream:
        raise ValueError(f"Earth inventory has unadmitted upstream dependencies: {missing_upstream}")

    rows = []
    for position, obligation in enumerate(EARTH_ENVIRONMENT_OBLIGATIONS, 1):
        blueprint = blueprints[obligation.claim_id]
        payload = asdict(obligation)
        payload.update({
            "position": position,
            "candidate_count": 256,
            "unique_survivor": "__".join(choice.name for choice in unique_survivor(blueprint)),
            "dependencies": list(blueprint.dependencies),
            "predicted_observation_label": blueprint.predicted_observation_label,
            "status": "model_admitted" if obligation.claim_id in admitted else "registered_not_admitted",
        })
        rows.append(payload)

    counts = Counter(row.family for row in EARTH_ENVIRONMENT_OBLIGATIONS)
    prior_mapping = {
        "SFT-PRIOR-V1-XIV10-EARTH-IONOSPHERE-RESONANCE": "SFT-EARTH-EARTH-IONOSPHERE-RESONANCE-001",
        "SFT-PRIOR-V2-280-EARTH-TIPPING": "SFT-EARTH-EARTH-SYSTEM-TIPPING-001",
        "SFT-PRIOR-V2-280-EARTH-QUAKE-MAGNITUDE-FREQUENCY": "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001",
    }
    if set(prior_mapping) != {row["atom_id"] for row in audit["atomic_questions"]}:
        raise ValueError("Earth prior-atom mapping differs from the frozen audit")
    if not set(prior_mapping.values()) <= {row["claim_id"] for row in rows}:
        raise ValueError("an Earth prior atom maps outside the frozen inventory")

    inventory = {
        "schema": "sft-v3-earth-environment-foundation-inventory/1",
        "branch_id": "earth_environment",
        "inventory_frozen": True,
        "inventory_date": "2026-07-28",
        "derivation_target": "current-evidence foundational closure, extension-open",
        "scope": "Earth-system objects, observations, budgets, geological history, interior and geodynamics, seismic and volcanic processes, hydrosphere and cryosphere, atmosphere and weather, ocean and coasts, climate, biogeochemical coupling, environmental transport and quality, evidence classes, hazards and categorical handoffs.",
        "ownership_boundary": {
            "owned": "Contingent Earth states and histories, Earth-system composition and coupling, Earth observations, reconstructions, attribution and environmental evidence.",
            "consumed_not_reowned": ["universal Physics", "chemical identities and transformations", "material properties", "biological mechanisms"],
            "astronomy_handoff": "Other planets, orbital populations and cosmic histories.",
            "downstream_handoffs": ["Medicine", "Social and Collective Systems", "Engineering Translation"],
        },
        "prior_audit": "audits/earth_environment_v1_v2_initial_atomic_ownership.json",
        "prior_audit_identity": audit["audit_identity"],
        "prior_atomic_question_count": audit["summary"]["atomic_question_count"],
        "prior_atom_to_foundation_claim": prior_mapping,
        "inventory_completion_explanation": "The twelve roadmap families were decomposed into their nonduplicate carrier, relation, record, evidence and falsification obligations. The inherited Earth-ionosphere, tipping and earthquake atoms are explicit rows inside that decomposition. The resulting seventy-four rows determine the count; no target count generated or truncated the inventory.",
        "family_order": list(FAMILY_ORDER),
        "family_counts": {family: counts[family] for family in FAMILY_ORDER},
        "required_claim_count": len(rows),
        "required_claim_ids": [row.claim_id for row in EARTH_ENVIRONMENT_OBLIGATIONS],
        "candidate_count": len(rows) * 256,
        "admitted_claim_count_at_freeze": sum(row.claim_id in admitted for row in EARTH_ENVIRONMENT_OBLIGATIONS),
        "upstream_dependency_count": len(upstream_dependencies),
        "upstream_dependency_claim_ids": upstream_dependencies,
        "all_upstream_dependencies_model_admitted_at_freeze": True,
        "pre_source_complete_branch_seal": "experiments/sealed_predictions/earth_environment_foundation_complete_pre_source.json",
        "external_source_identities_selected_at_freeze": False,
        "external_outcomes_opened_at_freeze": False,
        "unclassified_obligations": [],
        "foundation_frontier_obligations": [],
        "later_full_field_extensions": [
            "complete solid-Earth, geodesy and geomagnetism census",
            "complete mineralogy, petrology, sedimentology, stratigraphy and palaeontology handoff",
            "complete geomorphology, soils and landscape dynamics",
            "complete hydrology, cryosphere, oceanography, atmosphere and meteorology",
            "complete climate, palaeoclimate, forcing, feedback and attribution",
            "complete ecology, biodiversity and coupled Earth systems",
            "complete pollution, toxic transport and environmental quality",
            "complete hazards, risk, resilience, resources and sustainability accounting",
            "complete Earth observation, data assimilation and forecast-validation census",
        ],
        "obligations": rows,
    }
    inventory["inventory_hash"] = sha256_identity(inventory)
    write_json(INVENTORY_PATH, inventory)

    branches_path = ROOT / "census/branches.json"
    branches = json.loads(branches_path.read_text(encoding="utf-8"))
    branch = next(row for row in branches["branches"] if row["branch_id"] == "earth_environment")
    if branch["inventory_status"] not in {"pending", "registered_not_started", "foundation_frozen_0_of_74_registered_not_admitted"}:
        raise ValueError("Earth branch has an unexpected pre-freeze state")
    branch["inventory_status"] = "foundation_frozen_0_of_74_registered_not_admitted"
    branch["paper_status"] = "not_ready"
    write_json(branches_path, branches)

    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "foundation_inventory_frozen_predictions_not_yet_sealed",
        "foundation_required_claim_count": len(rows),
        "candidate_count": len(rows) * 256,
        "admitted_claim_count": sum(row.claim_id in admitted for row in EARTH_ENVIRONMENT_OBLIGATIONS),
        "remaining_claim_count": len(rows) - sum(row.claim_id in admitted for row in EARTH_ENVIRONMENT_OBLIGATIONS),
        "inventory_path": str(INVENTORY_PATH.relative_to(ROOT)),
        "inventory_hash": inventory["inventory_hash"],
        "upstream_dependency_count": len(upstream_dependencies),
        "all_upstream_dependencies_model_admitted_at_freeze": True,
        "next_exact_operation": "seal_complete_foundation_derivations_before_external_source_selection",
    })
    write_json(checkpoint_path, checkpoint)
    print(f"frozen Earth foundation inventory: {len(rows)} obligations; {len(rows) * 256} candidates; {inventory['inventory_hash']}")


if __name__ == "__main__":
    main()
