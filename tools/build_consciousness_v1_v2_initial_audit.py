#!/usr/bin/env python3
"""Freeze the initial V1/V2 ownership audit for Consciousness.

This program registers questions and categorical ownership only.  It neither
imports a prior answer as a premise nor calls the admission engine.  Final
same-strength closure is a separate post-admission audit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2_PATH = ROOT / "audits/v2_407_step_observation_census.json"
LINEAGE_PATH = ROOT / "census/lineage_reconciliation.json"
AUDIT_PATH = ROOT / "audits/consciousness_v1_v2_initial_atomic_ownership.json"
REPORT_PATH = ROOT / "audits/consciousness_v1_v2_initial_atomic_ownership.md"
CHECKPOINT_PATH = ROOT / "census/consciousness_continuation_checkpoint.json"


@dataclass(frozen=True)
class Atom:
    atom_id: str
    question: str
    family: str
    scope: str = "foundation"
    boundary: str = "Consciousness and Cognitive Science"


def atom(atom_id: str, question: str, family: str, *, scope: str = "foundation", boundary: str = "Consciousness and Cognitive Science") -> Atom:
    return Atom(atom_id, question, family, scope, boundary)


V1_ATOMS: dict[str, tuple[Atom, ...]] = {
    "C1s": (atom("SFT-PRIOR-V1-C1S-CONSC-SELF-OBSERVATION-CLOSURE", "What exact structure makes observation re-enter the observing system without leaving its declared carrier?", "observation_interior_observation"),),
    "C2s": (atom("SFT-PRIOR-V1-C2S-CONSC-SELF-OBSERVATION-BLIND-SPOT", "Which predecessor distinction is unavailable to an observer that receives only the Fold image?", "self_observation_introspection"),),
    "C3s": (atom("SFT-PRIOR-V1-C3S-CONSC-SELF-OBSERVATION-FIXED-POINT", "Which admissible state, if any, is unchanged by exact self-observation?", "subject_perspective_interiority"),),
    "C4s": (atom("SFT-PRIOR-V1-C4S-CONSC-INTEGRATION", "Under what exact relation do distinct self-observing processes remain distinct or compose into one process?", "binding_unity"),),
    "C5s": (atom("SFT-PRIOR-V1-C5S-CONSC-OBSERVATIONAL-MOMENT", "What is the least complete act in an ordered self-observation trace?", "observation_interior_observation"),),
    "C6s": (atom("SFT-PRIOR-V1-C6S-CONSC-EXPERIENTIAL-SEQUENCE", "How can successive interior observations compose into a retained temporal sequence without importing a continuum?", "memory_temporal_identity"),),
    "C7s": (atom("SFT-PRIOR-V1-C7S-CONSC-UNITY", "What distinguishes one joint interior process from a collection of separately continuing processes?", "binding_unity"),),
    "C8s": (atom("SFT-PRIOR-V1-C8S-CONSC-INTROSPECTION-LIMIT", "How many predecessor labels are closed by repeated self-observation when they are not separately retained?", "self_observation_introspection"),),
    "C9s": (atom("SFT-PRIOR-V1-C9S-CONSC-FELT-SELF-INVARIANT", "What exact invariant can persist as the subject-coordinate while experienced contents change?", "subject_perspective_interiority"),),
    "C10s": (atom("SFT-PRIOR-V1-C10S-CONSC-CESSATION", "Which distinctions end, persist or become unbound when an integrated conscious organization ceases?", "memory_temporal_identity"),),
    "XI-1": (atom("SFT-PRIOR-V1-XI1-CONSC-MEMORY", "What distinguishes a retained memory carrier from a pattern freshly reconstructed after its earlier carrier was lost?", "memory_temporal_identity"),),
    "XI-2": (atom("SFT-PRIOR-V1-XI2-CONSC-ATTENTION", "How is one cognitively available support selected while unselected alternatives remain represented rather than annihilated?", "attention_availability"),),
    "XI-3": (atom("SFT-PRIOR-V1-XI3-CONSC-FORWARD-MODEL", "How does an interior process form a lawful anticipatory representation without treating the represented future as an observation?", "cognition_inference_representation"),),
    "XI-4": (atom("SFT-PRIOR-V1-XI4-CONSC-BINDING", "How are distributed retained contents composed into one experience without erasing their content identities?", "binding_unity"),),
    "XI-5": (atom("SFT-PRIOR-V1-XI5-CONSC-UNCONSCIOUS-INTROSPECTION", "What distinguishes cognitively active but phenomenally unavailable processing from accessible interior observation?", "access_report_presence"),),
    "XI-6": (atom("SFT-PRIOR-V1-XI6-CONSC-SLEEP-DREAM", "How are loss, recurrence and recovery of integrated availability represented across sleep and dream states?", "memory_temporal_identity", scope="foundation_prior_extension"),),
    "XI-7": (
        atom("SFT-PRIOR-V1-XI7-CONSC-INTERIORITY", "What distinguishes being an observation process from an external description of that process?", "subject_perspective_interiority"),
        atom("SFT-PRIOR-V1-XI7-CONSC-HARD-PROBLEM", "Can the claimed relation between Fold observation and phenomenal presence be stated without substituting report, behaviour or correlation for experience?", "access_report_presence"),
    ),
    "XIV-1": (
        atom("SFT-PRIOR-V1-XIV1-CONSC-PERCEPTUAL-CHANNEL", "How are perceptual qualities retained and distinguished within a bound experience?", "qualia_resonance_composition", scope="foundation_prior_extension"),
        atom("SFT-PRIOR-V1-XIV1-CONSC-SYNAESTHESIA", "What lawful cross-binding relation distinguishes synaesthetic composition from ordinary same-channel binding?", "qualia_resonance_composition", scope="foundation_prior_extension"),
    ),
    "XIV-2": (atom("SFT-PRIOR-V1-XIV2-CONSC-ALTERED-STATE-BOUNDARY", "What structure can be claimed from reports of non-ordinary experience without turning a report into proof of its ontology?", "access_report_presence", scope="foundation_prior_extension"),),
    "XIV-3": (atom("SFT-PRIOR-V1-XIV3-CONSC-EXPECTATION", "How can expectation participate in an experienced and bodily response while remaining distinct from the clinical intervention comparison?", "cognition_inference_representation", boundary="Consciousness owns expectation and self-model structure; Medicine owns clinical placebo/nocebo outcomes."),),
    "XIV-4": (atom("SFT-PRIOR-V1-XIV4-CONSC-FINITE-SELF-SIMULATION", "What is the exact closure boundary for a finite self-model applied to its own representations?", "finite_self_model"),),
    "XIV-7": (
        atom("SFT-PRIOR-V1-XIV7-CONSC-SUBSTRATE-INDEPENDENCE", "Which realization-preserving structural conditions, if any, make a consciousness claim independent of material identity?", "substrate_realization"),
        atom("SFT-PRIOR-V1-XIV7-CONSC-FEEDFORWARD-BOUNDARY", "Which required self-observation and integration relations are absent from a merely feed-forward transformation?", "substrate_realization"),
    ),
    "XVII-5": (atom("SFT-PRIOR-V1-XVII5-CONSC-MEASUREMENT-JOIN", "What is the exact boundary between physical measurement and conscious observation, and does either require the other?", "observation_interior_observation", boundary="Physics owns physical measurement; Consciousness owns interior observation and the bridge claim."),),
    "G9": (atom("SFT-PRIOR-V1-G9-CONSC-IDENTITY-TRANSPORT", "Which exact identity relations survive a lawful change of realizing carrier, and which do not?", "substrate_realization", scope="foundation_prior_extension"),),
}


V2_ATOMS: dict[int, tuple[Atom, ...]] = {
    116: (atom("SFT-PRIOR-V2-116-CONSC-BINDING", "Does exact phase-compatible joint recurrence supply a compositional binding witness while retaining the participating processes?", "binding_unity"),),
    117: (
        atom("SFT-PRIOR-V2-117-CONSC-UNCONSCIOUS-ORBIT", "Can an active recurrent process remain outside conscious availability until a complementary relation completes it?", "access_report_presence"),
        atom("SFT-PRIOR-V2-117-CONSC-SELF-OPACITY", "Does deterministic continuation remain internally unavailable when the predecessor label required for reconstruction is unretained?", "self_observation_introspection"),
    ),
    145: (atom("SFT-PRIOR-V2-145-CONSC-MEMORY-ORBIT", "Which exact recurrence and retention conditions distinguish persistent memory from transient state continuation?", "memory_temporal_identity"),),
    148: (atom("SFT-PRIOR-V2-148-CONSC-SLEEP-STATE-CYCLE", "Can an exact state-cycle represent recurring loss and recovery of integrated access without identifying its coordinates with biological sleep stages by fiat?", "memory_temporal_identity", scope="foundation_prior_extension"),),
    160: (
        atom("SFT-PRIOR-V2-160-CONSC-PHENOMENAL-UNITY", "What exact compositional condition makes phenomenal presence one whole rather than an externally collected heap?", "binding_unity"),
        atom("SFT-PRIOR-V2-160-CONSC-INTERIORITY", "What exact accessibility asymmetry distinguishes an interior process from its complete external record?", "subject_perspective_interiority"),
    ),
    166: (atom("SFT-PRIOR-V2-166-CONSC-EXPECTATION-OBSERVATION", "How can expectation and bodily observation be retained as distinct contributors to one experienced response?", "cognition_inference_representation", boundary="Consciousness owns the expectation/experience composition; Medicine owns clinical effect evidence."),),
    175: (atom("SFT-PRIOR-V2-175-CONSC-MULTIQUALITY-COMPOSITION", "What is the least generated recurrent support capable of retaining three distinguishable qualitative positions as one composed whole?", "qualia_resonance_composition"),),
    178: (atom("SFT-PRIOR-V2-178-CONSC-CROSS-MODAL-BINDING", "What exact shared observation class permits two otherwise distinct sensory labels to compose without becoming identical?", "qualia_resonance_composition", scope="foundation_prior_extension"),),
    181: (atom("SFT-PRIOR-V2-181-CONSC-ATTENTIONAL-CAPACITY", "What exact carrier and selection relation bounds one fully retained focus while preserving the existence of alternatives?", "attention_availability"),),
    199: (atom("SFT-PRIOR-V2-199-CONSC-REALIZATION-TEST", "What complete structural test distinguishes a self-observing, closed and integrated realization from a system that only produces reports?", "substrate_realization"),),
    247: (atom("SFT-PRIOR-V2-247-CONSC-SELF-MODEL-DEPTH", "How many nonidentity self-model applications are generated before exact Fold closure?", "finite_self_model"),),
    253: (atom("SFT-PRIOR-V2-253-CONSC-CESSATION-DISTINCTIONS", "At cessation, how are occupancy, organization, retained record and the foundational fixed form kept categorically distinct?", "memory_temporal_identity"),),
    257: (atom("SFT-PRIOR-V2-257-CONSC-MEASUREMENT-CORRESPONDENCE", "How can measurement and conscious observation share an operation while remaining different evidence and realization classes?", "observation_interior_observation", boundary="Physics owns measurement; Consciousness owns the operational correspondence to interior observation."),),
    281: (
        atom("SFT-PRIOR-V2-281-CONSC-DETERMINISTIC-ACTION", "Does exact state-transition functionality leave any ungenerated alternative successor inside the model?", "cognition_inference_representation"),
        atom("SFT-PRIOR-V2-281-CONSC-DETERMINISM-SELF-OPACITY", "Why can a structurally determined self remain unable to reconstruct the retained-label-free predecessor of its own present observation?", "self_observation_introspection"),
    ),
}


LINEAGE_ATOMS = (
    atom("SFT-PRIOR-LINEAGE-CONSC-QUALIA-RESONANCE", "What exact recurrent, differentiating and compositional law constitutes the separately registered V1 qualia-resonance result?", "qualia_resonance_composition"),
    atom("SFT-PRIOR-LINEAGE-CONSC-RED-OF-RED", "What exact generated structure distinguishes the specific red-of-red qualitative identity, its recurrence and its controls from generic binding or a colour report?", "red_of_red"),
)


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    v1 = json.loads(V1_PATH.read_text(encoding="utf-8"))
    v2 = json.loads(V2_PATH.read_text(encoding="utf-8"))
    lineage = json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))
    lineage_group = next(row for row in lineage["named_consequence_groups"] if row["group_id"] == "consciousness_qualia_self_and_subjectivity")
    source_rows: list[dict[str, object]] = []

    for row in v1["rows"]:
        source_id = str(row["v1_claim_id"])
        atoms = V1_ATOMS.get(source_id, ())
        source_rows.append({
            "source": "v1", "source_entry": source_id, "source_hash": row["source_row_sha256"],
            "source_observation": row["prior_result_observation"], "consciousness_owned": bool(atoms),
            "disposition": "consciousness_atoms_registered" if atoms else "reviewed_no_consciousness_owned_atom",
            "consciousness_atoms": [asdict(item) for item in atoms],
        })
    for row in v2["steps"]:
        source_id = int(row["step"])
        atoms = V2_ATOMS.get(source_id, ())
        source_rows.append({
            "source": "v2", "source_entry": source_id, "source_hash": row["source_block_sha256"],
            "source_observation": row["prior_result_observation"], "consciousness_owned": bool(atoms),
            "disposition": "consciousness_atoms_registered" if atoms else "reviewed_no_consciousness_owned_atom",
            "consciousness_atoms": [asdict(item) for item in atoms],
        })

    atoms = [item for row in source_rows for item in row["consciousness_atoms"]]
    lineage_atoms = [asdict(item) for item in LINEAGE_ATOMS]
    all_atoms = atoms + lineage_atoms
    families: dict[str, int] = {}
    scopes: dict[str, int] = {}
    for item in all_atoms:
        families[item["family"]] = families.get(item["family"], 0) + 1
        scopes[item["scope"]] = scopes.get(item["scope"], 0) + 1
    audit = {
        "schema": "sft.consciousness.v1-v2-initial-atomic-ownership-audit.v1",
        "status": "ownership_questions_frozen_derivations_not_yet_admitted",
        "purpose": "Review every registered V1/V2 entry, decompose Consciousness-owned questions, and preserve the stronger separately registered qualia and red-of-red obligations before V3 derivation.",
        "authority_boundary": {
            "canonical_engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
            "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
            "engine_called": False, "engine_modified": False, "claims_admitted": 0,
            "prior_answers_used_as_premises": False, "prior_questions_registered_before_derivation": True,
        },
        "source_surface": {
            "v1_path": str(V1_PATH.relative_to(ROOT)), "v1_source_hash": v1["source_sha256"], "v1_rows_reviewed": len(v1["rows"]),
            "v2_path": str(V2_PATH.relative_to(ROOT)), "v2_source_hash": v2["source_sha256"], "v2_steps_reviewed": len(v2["steps"]),
            "total_v1_v2_entries_reviewed": len(source_rows),
            "lineage_path": str(LINEAGE_PATH.relative_to(ROOT)), "lineage_file_hash": "sha256:" + hashlib.sha256(LINEAGE_PATH.read_bytes()).hexdigest(),
            "lineage_group_identity": digest(lineage_group),
        },
        "summary": {
            "v1_v2_owned_source_entry_count": sum(row["consciousness_owned"] for row in source_rows),
            "v1_v2_atomic_question_count": len(atoms), "lineage_only_stronger_atomic_question_count": len(lineage_atoms),
            "total_atomic_question_count": len(all_atoms), "unique_atom_ids": len({item["atom_id"] for item in all_atoms}) == len(all_atoms),
            "family_counts": families, "scope_counts": scopes, "same_strength_admitted_count": 0,
        },
        "lineage_only_atoms": lineage_atoms,
        "atomic_questions": all_atoms,
        "source_rows": source_rows,
    }
    audit["audit_identity"] = digest(audit)
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT_PATH.write_text(
        "# Consciousness V1/V2 initial atomic ownership audit\n\n"
        f"Status: `{audit['status']}`.\n\n"
        f"All `{len(source_rows)}` V1/V2 entries were reviewed. `{len(atoms)}` atomic Consciousness questions were found in those entries, and `{len(lineage_atoms)}` stronger separately registered qualia obligations were preserved, giving `{len(all_atoms)}` atomic prior questions.\n\n"
        "This is an ownership and question freeze, not a derivation or an admission. Prior answers remain outside the V3 proof runtime.\n\n"
        "## Frozen family counts\n\n" + "\n".join(f"- `{key}`: {value}" for key, value in sorted(families.items())) +
        f"\n\n## Audit identity\n\n`{audit['audit_identity']}`\n",
        encoding="utf-8",
    )
    checkpoint = {
        "schema": "sft-v3-consciousness-continuation-checkpoint/1", "branch": "consciousness_cognitive_science",
        "status": "initial_prior_ownership_audit_complete_inventory_not_yet_frozen",
        "last_admitted_claim_id": None, "last_admitted_receipt_hash": None, "admitted_claim_count": 0,
        "prior_entries_reviewed": len(source_rows), "prior_atomic_questions": len(all_atoms),
        "initial_audit_path": str(AUDIT_PATH.relative_to(ROOT)), "initial_audit_identity": audit["audit_identity"],
        "next_exact_operation": "freeze_dependency_boundary_and_foundation_obligation_inventory",
        "engine_seal": audit["authority_boundary"]["canonical_engine_seal"],
        "verification_authority_seal": audit["authority_boundary"]["verification_authority_seal"],
        "protected_authority_modified": False, "remote_publication_authorized": False,
    }
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"consciousness initial audit: reviewed={len(source_rows)} prior_atoms={len(all_atoms)} identity={audit['audit_identity']}")


if __name__ == "__main__":
    main()
