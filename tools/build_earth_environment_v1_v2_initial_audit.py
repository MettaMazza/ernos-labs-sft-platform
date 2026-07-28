#!/usr/bin/env python3
"""Freeze the initial V1/V2 ownership audit for Earth and Environment.

This program registers questions and categorical ownership only. Earlier SFT
answers remain observational records and never enter the V3 derivation runtime
as premises. Same-strength closure is assessed only after lawful V3 admission.
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
AUDIT_PATH = ROOT / "audits/earth_environment_v1_v2_initial_atomic_ownership.json"
REPORT_PATH = ROOT / "audits/earth_environment_v1_v2_initial_atomic_ownership.md"
CHECKPOINT_PATH = ROOT / "census/earth_environment_continuation_checkpoint.json"


ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


@dataclass(frozen=True)
class Atom:
    atom_id: str
    question: str
    family: str
    boundary: str
    scope: str = "foundation"


def atom(atom_id: str, question: str, family: str, boundary: str) -> Atom:
    return Atom(atom_id, question, family, boundary)


V1_ATOMS: dict[str, tuple[Atom, ...]] = {
    "XIV-10": (
        atom(
            "SFT-PRIOR-V1-XIV10-EARTH-IONOSPHERE-RESONANCE",
            "What exact Earth-atmosphere boundary, propagation relation and measured geometry establish the Earth-ionosphere cavity and its source-dated resonant modes without using the measured frequency to select the law?",
            "atmosphere_weather",
            "Earth and Environmental Sciences owns the observed Earth-ionosphere system and its source-dated state; Physics owns universal wave and cavity relations; Engineering owns transmission efficiency and implementation.",
        ),
    ),
}


V2_ATOMS: dict[int, tuple[Atom, ...]] = {
    280: (
        atom(
            "SFT-PRIOR-V2-280-EARTH-TIPPING",
            "What complete state, forcing, threshold, recurrence, hysteresis and observation record distinguishes an abrupt Earth-system transition from ordinary variability without assuming a universal half-One physical threshold?",
            "climate_system",
            "Earth and Environmental Sciences owns observed coupled-system transitions and attribution; Mathematics owns generic dynamical bifurcation structure; no abstract Fold coordinate is silently relabelled as a measured environmental threshold.",
        ),
        atom(
            "SFT-PRIOR-V2-280-EARTH-QUAKE-MAGNITUDE-FREQUENCY",
            "Under what complete catalog, magnitude scale, spatial-temporal boundary and detection record does an earthquake size-frequency relation hold, and can a unit exponent be derived before blind comparison rather than read from the catalog?",
            "seismic_volcanic",
            "Earth and Environmental Sciences owns earthquake catalogs and Earth-specific magnitude-frequency evidence; Physics owns universal rupture, wave and energy relations.",
        ),
    ),
}


EXPLICIT_HANDOFFS = {
    "V1:G15": "Physics owns the universal finite-flow and turbulence claim; Earth consumes it for atmosphere, ocean and geophysical flows.",
    "V1:IX-8": "Astronomy and Cosmology owns planetary orbital resonance and tidal locking; Earth owns only Earth-system tidal observations after the universal and orbital dependencies are cited.",
    "V2:153": "Astronomy and Cosmology owns planetary tidal locking; Earth may consume Earth-Moon boundary observations without reowning the orbital law.",
    "V2:279": "Physics owns the universal turbulence exponents; Earth owns purpose-matched atmospheric, oceanic and geophysical comparisons.",
    "V2:291": "Astronomy and Cosmology owns planetary-spacing and galactic observations; Materials owns quasicrystals.",
    "V2:295": "Biology owns ecosystem identity and ecological recurrence; Earth owns abiotic reservoirs and coupled Earth-system boundary records.",
}


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    v1 = json.loads(V1_PATH.read_text(encoding="utf-8"))
    v2 = json.loads(V2_PATH.read_text(encoding="utf-8"))
    lineage = json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))
    source_rows: list[dict[str, object]] = []

    for row in v1["rows"]:
        source_id = str(row["v1_claim_id"])
        atoms = V1_ATOMS.get(source_id, ())
        key = f"V1:{source_id}"
        source_rows.append({
            "source": "v1",
            "source_entry": source_id,
            "source_hash": row["source_row_sha256"],
            "source_observation": row["prior_result_observation"],
            "earth_environment_owned": bool(atoms),
            "disposition": "earth_environment_questions_registered" if atoms else "reviewed_no_earth_environment_owned_atom",
            "explicit_handoff": EXPLICIT_HANDOFFS.get(key),
            "earth_environment_atoms": [asdict(item) for item in atoms],
        })

    for row in v2["steps"]:
        source_id = int(row["step"])
        atoms = V2_ATOMS.get(source_id, ())
        key = f"V2:{source_id}"
        source_rows.append({
            "source": "v2",
            "source_entry": source_id,
            "source_hash": row["source_block_sha256"],
            "source_observation": row["prior_result_observation"],
            "earth_environment_owned": bool(atoms),
            "disposition": "earth_environment_questions_registered" if atoms else "reviewed_no_earth_environment_owned_atom",
            "explicit_handoff": EXPLICIT_HANDOFFS.get(key),
            "earth_environment_atoms": [asdict(item) for item in atoms],
        })

    questions = [item for row in source_rows for item in row["earth_environment_atoms"]]
    family_counts: dict[str, int] = {}
    for item in questions:
        family_counts[item["family"]] = family_counts.get(item["family"], 0) + 1

    lineage_groups = []
    for group in lineage.get("named_consequence_groups", []):
        if "earth and high-energy astrophysical signatures" in group.get("required_results", []):
            lineage_groups.append({
                "group_id": group["group_id"],
                "disposition": "decomposed_without_duplicate_atom",
                "earth_owned_source_step": 280,
                "earth_owned_atoms": [item["atom_id"] for item in questions if item["atom_id"].startswith("SFT-PRIOR-V2-280")],
                "non_earth_remainder": "High-energy burst and ringdown atoms remain Physics/Astronomy-owned.",
            })

    audit = {
        "schema": "sft.earth-environment.v1-v2-initial-atomic-ownership-audit.v1",
        "status": "ownership_questions_frozen_derivations_not_yet_admitted",
        "purpose": "Review all registered V1/V2 entries, decompose every Earth-and-Environment-owned question, preserve explicit handoffs, and freeze accountability before V3 derivation.",
        "authority_boundary": {
            "canonical_engine_seal": ENGINE_SEAL,
            "verification_authority_seal": AUTHORITY_SEAL,
            "engine_called": False,
            "engine_modified": False,
            "claims_admitted": 0,
            "prior_answers_used_as_premises": False,
            "prior_questions_registered_before_derivation": True,
            "external_outcomes_opened": False,
        },
        "source_surface": {
            "v1_path": str(V1_PATH.relative_to(ROOT)),
            "v1_source_hash": v1["source_sha256"],
            "v1_rows_reviewed": len(v1["rows"]),
            "v2_path": str(V2_PATH.relative_to(ROOT)),
            "v2_source_hash": v2["source_sha256"],
            "v2_steps_reviewed": len(v2["steps"]),
            "total_v1_v2_entries_reviewed": len(source_rows),
            "lineage_path": str(LINEAGE_PATH.relative_to(ROOT)),
            "lineage_hash": "sha256:" + hashlib.sha256(LINEAGE_PATH.read_bytes()).hexdigest(),
        },
        "ownership_law": {
            "earth_owner": "Contingent Earth states, Earth history, Earth-system composition, planetary-scale coupled environmental relations and purpose-matched Earth observations.",
            "upstream_consumed_not_reowned": ["physics", "chemistry", "materials", "biology"],
            "downstream_handoffs": ["medicine", "social_collective_systems", "engineering_translation"],
            "astronomy_boundary": "Other planets, orbital populations and cosmic histories remain Astronomy and Cosmology-owned.",
            "universal_law_boundary": "Universal physical, chemical, material and biological laws are cited through admitted dependencies rather than relabelled as Earth discoveries.",
        },
        "summary": {
            "owned_source_entry_count": sum(bool(row["earth_environment_owned"]) for row in source_rows),
            "atomic_question_count": len(questions),
            "unique_atom_ids": len({item["atom_id"] for item in questions}) == len(questions),
            "family_counts": family_counts,
            "explicit_handoff_count": sum(row["explicit_handoff"] is not None for row in source_rows),
            "same_strength_admitted_count": 0,
        },
        "lineage_group_decompositions": lineage_groups,
        "atomic_questions": questions,
        "source_rows": source_rows,
    }
    audit["audit_identity"] = digest(audit)
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Earth and Environmental Sciences V1/V2 initial atomic ownership audit",
        "",
        f"Status: `{audit['status']}`.",
        "",
        f"All `{len(source_rows)}` V1/V2 entries were reviewed. `{len(questions)}` Earth-owned atomic prior questions occur in `{audit['summary']['owned_source_entry_count']}` mixed or Earth-specific source entries.",
        "",
        "This freezes questions, ownership and handoffs only. It does not import a prior answer, open an external target, call the engine or admit a claim.",
        "",
        "## Frozen prior questions",
        "",
    ]
    for item in questions:
        lines.extend((f"- `{item['atom_id']}` — {item['question']}", f"  Boundary: {item['boundary']}"))
    lines.extend(("", "## Explicit handoffs", ""))
    for key, value in EXPLICIT_HANDOFFS.items():
        lines.append(f"- `{key}` — {value}")
    lines.extend(("", "## Audit identity", "", f"`{audit['audit_identity']}`", ""))
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    checkpoint = {
        "schema": "sft-v3-earth-environment-continuation-checkpoint/1",
        "branch": "earth_environment",
        "status": "initial_prior_ownership_audit_complete_inventory_not_yet_frozen",
        "last_admitted_claim_id": None,
        "last_admitted_receipt_hash": None,
        "admitted_claim_count": 0,
        "prior_entries_reviewed": len(source_rows),
        "prior_atomic_questions": len(questions),
        "initial_audit_path": str(AUDIT_PATH.relative_to(ROOT)),
        "initial_audit_identity": audit["audit_identity"],
        "previous_branch_terminal_claim": "SFT-CONSC-RED-EMPIRICAL-BOUNDARY-001",
        "previous_branch_terminal_receipt_hash": "sha256:cdb9dec823a5d95b78a89e3e8605d369e1f26ea20908aee781247bc85a5d21b4",
        "next_exact_operation": "freeze_dependency_boundary_and_complete_foundation_obligation_inventory",
        "engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "protected_authority_modified": False,
        "remote_publication_authorized": False,
    }
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Earth initial audit: reviewed={len(source_rows)} prior_atoms={len(questions)} identity={audit['audit_identity']}")


if __name__ == "__main__":
    main()
