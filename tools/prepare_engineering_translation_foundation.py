#!/usr/bin/env python3
"""Audit V1/V2, freeze Engineering inventory and seal pre-source derivations."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engineering_translation.generated_law import ENGINEERING_BLUEPRINTS, unique_survivor
from sft.engineering_translation.obligations import ENGINEERING_OBLIGATIONS, FAMILY_ORDER

ENGINE = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"
V1_MAP = {
    "XV-3": "SFT-ENG-REPRODUCIBILITY-001",
    "XIX-5": "SFT-ENG-E2E-001",
    "C-1": "SFT-ENG-ARCHITECTURE-001",
    "C-3": "SFT-ENG-ACCESSIBLE-INTERFACE-001",
}
V2_MAP = {
    285: "SFT-ENG-LAW-TRANSLATION-001",
    303: "SFT-ENG-VALIDATION-001",
    306: "SFT-ENG-CONTROL-001",
}
HANDOFFS = {
    "V1:XIV-6": "Physics owns any vacuum or inertia law; Engineering may only translate an already admitted law into a bounded apparatus and test.",
    "V2:199": "Consciousness owns the substrate-independent consciousness criterion; Engineering owns only a bounded implemented test article.",
    "V2:304": "The future Fold Protein rebuild is an Engineering application after Biology and computation prerequisites, not a foundation selector.",
    "V2:305": "The future Fold Go rebuild is an Engineering application after computation prerequisites, not a foundation selector.",
    "V2:307": "The future Unison AI rebuild is an Engineering application after computation and Social prerequisites, not a foundation selector.",
}


def digest(value) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    v1 = json.loads((ROOT / "audits/v1_theorem_manifest_observation_census.json").read_text())
    v2 = json.loads((ROOT / "audits/v2_407_step_observation_census.json").read_text())
    rows = []
    atoms = []
    for version, source, key_name, hash_name, mapping in (
        ("v1", v1["rows"], "v1_claim_id", "source_row_sha256", V1_MAP),
        ("v2", v2["steps"], "step", "source_block_sha256", V2_MAP),
    ):
        for source_row in source:
            key = source_row[key_name]
            target = mapping.get(key)
            label = f"{version.upper()}:{key}"
            atom = None
            if target:
                atom = {
                    "atom_id": f"SFT-PRIOR-{version.upper()}-{str(key).replace('-', '')}-ENGINEERING",
                    "source_entry": label,
                    "question": f"What exact V3 requirement, artifact, operating boundary, test and failure record accounts for the translation question historically recorded at {label} without importing its answer or implementation?",
                    "mapped_foundation_claim": target,
                    "boundary": "Engineering owns bounded implementations and demonstrations; categorical science owns laws; applications and products cannot select either.",
                }
                atoms.append(atom)
            rows.append(
                {
                    "source": version,
                    "source_entry": key,
                    "source_hash": source_row[hash_name],
                    "source_observation": source_row["prior_result_observation"],
                    "engineering_owned": bool(target),
                    "disposition": "engineering_question_registered" if target else "reviewed_no_engineering_owned_atom",
                    "explicit_handoff": HANDOFFS.get(label),
                    "engineering_atom": atom,
                }
            )
    audit = {
        "schema": "sft.engineering-translation.v1-v2-initial-atomic-ownership-audit.v1",
        "status": "ownership_questions_frozen_derivations_not_yet_admitted",
        "authority_boundary": {
            "canonical_engine_seal": ENGINE,
            "verification_authority_seal": AUTHORITY,
            "engine_called": False,
            "engine_modified": False,
            "prior_answers_or_implementations_used_as_premises": False,
            "external_standards_products_tests_or_outcomes_opened": False,
        },
        "source_surface": {"v1_rows_reviewed": len(v1["rows"]), "v2_steps_reviewed": len(v2["steps"]), "total_entries_reviewed": len(rows)},
        "ownership_law": {
            "engineering_owner": "Bounded requirements, designs, artifacts, interfaces, tests, safety cases, deployment, lifecycle and anomaly handoff.",
            "consumed_not_reowned": ["fundamental scientific laws", "formal computation semantics", "biological or clinical state", "subjective experience", "social legitimacy"],
            "application_boundary": "Fold Protein, Fold Chess, Fold Go and Unison AI remain later translation work and cannot select foundation laws.",
        },
        "summary": {
            "owned_source_entry_count": len(atoms),
            "atomic_question_count": len(atoms),
            "unique_atom_ids": len({x["atom_id"] for x in atoms}) == len(atoms),
            "explicit_handoff_count": len(HANDOFFS),
            "same_strength_admitted_count": 0,
        },
        "atomic_questions": atoms,
        "source_rows": rows,
    }
    audit["audit_identity"] = digest(audit)
    audit_path = ROOT / "audits/engineering_translation_v1_v2_initial_atomic_ownership.json"
    write(audit_path, audit)
    (ROOT / "audits/engineering_translation_v1_v2_initial_atomic_ownership.md").write_text(
        "# Engineering Translation V1/V2 initial atomic ownership audit\n\n"
        f"All **{len(rows)}** entries reviewed; **{len(atoms)}** Engineering-owned questions registered without importing answers or implementations.\n\n"
        + "\n".join(f"- `{x['atom_id']}` → `{x['mapped_foundation_claim']}`" for x in atoms)
        + f"\n\nAudit identity: `{audit['audit_identity']}`\n"
    )
    census = json.loads((ROOT / "census/claims.json").read_text())
    admitted = {x["claim_id"] for x in census["claims"] if x.get("model_admitted") is True}
    upstream = sorted({dependency for blueprint in ENGINEERING_BLUEPRINTS for dependency in blueprint.dependencies if not dependency.startswith("SFT-ENG-")})
    missing = [x for x in upstream if x not in admitted]
    if missing:
        raise ValueError(f"unadmitted Engineering dependencies: {missing}")
    blueprints = {x.claim_id: x for x in ENGINEERING_BLUEPRINTS}
    counts = Counter(x.family for x in ENGINEERING_OBLIGATIONS)
    inventory_rows = []
    for position, obligation in enumerate(ENGINEERING_OBLIGATIONS, 1):
        blueprint = blueprints[obligation.claim_id]
        row_value = asdict(obligation)
        row_value.update(
            {
                "position": position,
                "candidate_count": 256,
                "unique_survivor": "__".join(x.name for x in unique_survivor(blueprint)),
                "dependencies": list(blueprint.dependencies),
                "predicted_observation_label": blueprint.predicted_observation_label,
                "status": "registered_not_admitted",
            }
        )
        inventory_rows.append(row_value)
    mapping = {x["atom_id"]: x["mapped_foundation_claim"] for x in atoms}
    inventory = {
        "schema": "sft-v3-engineering-translation-foundation-inventory/1",
        "branch_id": "engineering_translation",
        "inventory_frozen": True,
        "inventory_date": "2026-07-28",
        "derivation_target": "current-evidence foundational closure, extension-open",
        "scope": "Requirements, function, boundaries, components, interfaces, systems, resources, measurement, design alternatives, control, safety, verification, cross-platform access, lifecycle, science-design distinction and anomaly handoff.",
        "ownership_boundary": {
            "owned": "Versioned translation of admitted laws into bounded designs, instruments, processes, software, tests, deployments and demonstrations.",
            "consumed_not_reowned": ["fundamental science laws", "formal computation laws", "individual biological clinical conscious or social states"],
            "downstream": ["future domain implementations", "future V4 self-hosted reconstruction"],
        },
        "prior_audit": str(audit_path.relative_to(ROOT)),
        "prior_audit_identity": audit["audit_identity"],
        "prior_atomic_question_count": len(mapping),
        "prior_atom_to_foundation_claim": mapping,
        "inventory_completion_explanation": "Each of the twelve declared roadmap families decomposes into six distinct carrier/relation/record/evidence/falsification obligations. The count follows the decomposition rather than a requested target.",
        "family_order": list(FAMILY_ORDER),
        "family_counts": {family: counts[family] for family in FAMILY_ORDER},
        "required_claim_count": len(inventory_rows),
        "required_claim_ids": [x.claim_id for x in ENGINEERING_OBLIGATIONS],
        "candidate_count": len(inventory_rows) * 256,
        "admitted_claim_count_at_freeze": 0,
        "upstream_dependency_count": len(upstream),
        "upstream_dependency_claim_ids": upstream,
        "all_upstream_dependencies_model_admitted_at_freeze": True,
        "external_source_identities_selected_at_freeze": False,
        "external_outcomes_opened_at_freeze": False,
        "unclassified_obligations": [],
        "foundation_frontier_obligations": [],
        "later_full_field_extensions": [
            "systems requirements mechanical manufacturing and industrial engineering",
            "electrical electronic photonic hardware software network control and telecommunications engineering",
            "civil structural transport infrastructure aerospace space marine nuclear geological mining and subsurface engineering",
            "chemical process agricultural food biological materials energy environmental resource and biomedical engineering",
            "robotics autonomy human-machine microtechnology nanotechnology metrology laboratories safety security maintainability resilience and full lifecycle evidence",
            "fresh Fold Protein Fold Chess Fold Go and Unison AI translations only after prerequisite branches are ready",
            "implementation-distinct cross-platform reference artifacts for every scientific branch",
            "future V4 reconstruction in SFT-derived self-hosted language compiler runtime and proof principles",
        ],
        "obligations": inventory_rows,
    }
    inventory["inventory_hash"] = digest(inventory)
    inventory_path = ROOT / "publications/inventories/engineering_translation.json"
    write(inventory_path, inventory)
    sealed_files = (
        "publications/inventories/engineering_translation.json",
        "sft/engineering_translation/obligations.py",
        "sft/engineering_translation/structural_model.py",
        "sft/engineering_translation/generated_law.py",
        "audits/engineering_translation_v1_v2_initial_atomic_ownership.json",
    )
    predictions = tuple((x.claim_id, x.exact_result, x.predicted_observation_label, x.falsification_condition) for x in ENGINEERING_BLUEPRINTS)
    seal = {
        "schema": "sft-v3-engineering-translation-complete-pre-source-seal/1",
        "seal_date": "2026-07-28",
        "required_claim_count": 72,
        "candidate_count": 18432,
        "inventory_hash": inventory["inventory_hash"],
        "claim_prediction_set_hash": digest(predictions),
        "sealed_files": {x: file_hash(ROOT / x) for x in sealed_files},
        "external_source_identities_selected": False,
        "external_source_content_opened": False,
        "external_outcomes_opened": False,
        "prior_answers_or_implementations_present_in_derivation_runtime": False,
        "conventional_engineering_models_present_in_derivation_runtime": False,
        "application_or_performance_used_to_select_law": False,
        "measurement_used_to_select_law": False,
        "canonical_engine_seal": ENGINE,
        "verification_authority_seal": AUTHORITY,
    }
    seal["complete_branch_pre_source_seal_hash"] = digest(seal)
    seal_path = ROOT / "experiments/sealed_predictions/engineering_translation_foundation_complete_pre_source.json"
    write(seal_path, seal)
    checkpoint = {
        "schema": "sft-v3-engineering-translation-continuation-checkpoint/1",
        "branch": "engineering_translation",
        "status": "complete_foundation_derivations_sealed_before_external_sources",
        "foundation_required_claim_count": 72,
        "candidate_count": 18432,
        "admitted_claim_count": 0,
        "remaining_claim_count": 72,
        "prior_entries_reviewed": len(rows),
        "prior_atomic_questions": len(atoms),
        "initial_audit_path": str(audit_path.relative_to(ROOT)),
        "initial_audit_identity": audit["audit_identity"],
        "inventory_path": str(inventory_path.relative_to(ROOT)),
        "inventory_hash": inventory["inventory_hash"],
        "pre_source_seal_path": str(seal_path.relative_to(ROOT)),
        "pre_source_seal_hash": seal["complete_branch_pre_source_seal_hash"],
        "previous_branch_terminal_claim": "SFT-SOCIAL-ENGINEERING-HANDOFF-001",
        "engine_seal": ENGINE,
        "verification_authority_seal": AUTHORITY,
        "protected_authority_modified": False,
        "remote_publication_authorized": False,
        "next_exact_operation": "preregister_primary_engineering_evidence_sources",
    }
    write(ROOT / "census/engineering_translation_continuation_checkpoint.json", checkpoint)
    print(f"Engineering prepared: reviewed={len(rows)} atoms={len(atoms)} claims=72 candidates=18432 seal={seal['complete_branch_pre_source_seal_hash']}")


if __name__ == "__main__":
    main()
