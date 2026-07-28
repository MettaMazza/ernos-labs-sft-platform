#!/usr/bin/env python3
"""Atomic V1/V2 question and ownership audit for Astronomy/Cosmology."""

from __future__ import annotations

import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2 = ROOT / "audits/v2_407_step_observation_census.json"
OUT = ROOT / "audits/astronomy_cosmology_v1_v2_initial_atomic_ownership.json"
REPORT = ROOT / "audits/astronomy_cosmology_v1_v2_initial_atomic_ownership.md"
CHECKPOINT = ROOT / "census/astronomy_cosmology_continuation_checkpoint.json"
ENGINE = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"

# These are question registrations, never imported answers. Multiple historical
# questions may lawfully reconcile to one present foundation obligation.
V1_OWNED = {
    "IX-1": "SFT-ASTRO-STELLAR-STRUCTURE-001", "IX-2": "SFT-ASTRO-STELLAR-ENERGY-001",
    "IX-3": "SFT-ASTRO-WHITE-DWARF-NEUTRON-STAR-001", "IX-4": "SFT-ASTRO-STELLAR-ENDPOINT-001",
    "IX-5": "SFT-ASTRO-BLACK-HOLE-001", "IX-6": "SFT-ASTRO-MULTIMESSENGER-001",
    "IX-7": "SFT-ASTRO-GALACTIC-DYNAMICS-001", "IX-8": "SFT-ASTRO-RESONANCE-TIDE-001",
    "VIII-1": "SFT-ASTRO-THERMAL-HISTORY-001", "VIII-2": "SFT-ASTRO-PRIMORDIAL-ABUNDANCE-001",
    "VIII-3": "SFT-ASTRO-CMB-001", "VIII-4": "SFT-ASTRO-THERMAL-HISTORY-001",
    "VIII-5": "SFT-ASTRO-COSMIC-WEB-001", "VIII-6": "SFT-ASTRO-INITIAL-PERTURBATION-001",
    "VIII-7": "SFT-ASTRO-ULTIMATE-FATE-001", "VIII-8": "SFT-ASTRO-EXPANSION-HISTORY-001",
    "VIII-9": "SFT-ASTRO-EXPANSION-HISTORY-001", "VIII-10": "SFT-ASTRO-EXPANSION-HISTORY-001",
    "VIII-11": "SFT-ASTRO-EXPANSION-RECORD-001", "VIII-12": "SFT-ASTRO-EXPANSION-RECORD-001",
    "G11": "SFT-ASTRO-DISTANCE-LADDER-001", "N7": "SFT-ASTRO-LAW-HISTORY-001",
    "N8": "SFT-ASTRO-DARK-MATTER-EVIDENCE-001", "N8b": "SFT-ASTRO-EXPANSION-RECORD-001",
}
V2_OWNED = {
    15: "SFT-ASTRO-EXPANSION-RECORD-001", 34: "SFT-ASTRO-THERMAL-HISTORY-001",
    35: "SFT-ASTRO-DARK-ENERGY-EVIDENCE-001", 40: "SFT-ASTRO-DARK-ENERGY-EVIDENCE-001",
    42: "SFT-ASTRO-COSMIC-WEB-001", 46: "SFT-ASTRO-EXPANSION-HISTORY-001",
    58: "SFT-ASTRO-PRIMORDIAL-ABUNDANCE-001", 65: "SFT-ASTRO-REDSHIFT-001",
    85: "SFT-ASTRO-THERMAL-HISTORY-001", 86: "SFT-ASTRO-ORBIT-001",
    107: "SFT-ASTRO-GALACTIC-DYNAMICS-001", 109: "SFT-ASTRO-EXPANSION-HISTORY-001",
    114: "SFT-ASTRO-ULTIMATE-FATE-001", 120: "SFT-ASTRO-PRIMORDIAL-ABUNDANCE-001",
    128: "SFT-ASTRO-STELLAR-ENERGY-001", 135: "SFT-ASTRO-MULTIMESSENGER-001",
    139: "SFT-ASTRO-CMB-001", 140: "SFT-ASTRO-STELLAR-ENDPOINT-001",
    152: "SFT-ASTRO-STELLAR-STRUCTURE-001", 153: "SFT-ASTRO-RESONANCE-TIDE-001",
    161: "SFT-ASTRO-BLACK-HOLE-001", 173: "SFT-ASTRO-THERMAL-HISTORY-001",
    187: "SFT-ASTRO-COSMIC-WEB-001", 197: "SFT-ASTRO-LAW-HISTORY-001",
    201: "SFT-ASTRO-EXPANSION-RECORD-001", 202: "SFT-ASTRO-EXPANSION-RECORD-001",
    255: "SFT-ASTRO-WHITE-DWARF-NEUTRON-STAR-001", 268: "SFT-ASTRO-EXPANSION-RECORD-001",
    291: "SFT-ASTRO-TULLY-FISHER-001",
}
HANDOFFS = {
    "V1:D9e": "Physics owns universal gravitational-wave propagation; Astronomy owns source populations and messenger records.",
    "V1:D9f": "Physics owns orbital stability and dimension; Astronomy owns observed orbit solutions and populations.",
    "V1:XVIII-3": "Physics owns the vacuum-density law and value derivation; Astronomy owns source-dated expansion evidence.",
    "V2:59": "Physics owns gravitational clock/redshift equivalence; Astronomy owns observed source and frame records.",
    "V2:61": "Physics owns universal dilution exponents; Astronomy owns component histories and observational comparisons.",
    "V2:125": "Physics owns the spherical exterior solution; Astronomy owns object-specific compact-source inference.",
    "V2:188": "Physics owns the vacuum equation-of-state relation; Astronomy owns expansion-history evidence.",
    "V2:189": "Physics owns the dimension/stability proof; Astronomy owns observed orbital systems.",
}

def digest(x):
    return "sha256:" + hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main():
    v1, v2 = json.loads(V1.read_text()), json.loads(V2.read_text())
    rows, atoms = [], []
    for version, source, id_key, hash_key, mapping in (
        ("v1", v1["rows"], "v1_claim_id", "source_row_sha256", V1_OWNED),
        ("v2", v2["steps"], "step", "source_block_sha256", V2_OWNED),
    ):
        for row in source:
            key = row[id_key]
            target = mapping.get(key)
            label = f"{version.upper()}:{key}"
            atom = None
            if target:
                atom = {
                    "atom_id": f"SFT-PRIOR-{version.upper()}-{str(key).replace('-', '')}-ASTRONOMY",
                    "source_entry": label, "question": f"What exact V3 Astronomy/Cosmology derivation, retained record and source-bounded comparison accounts for the question historically recorded at {label} without importing its answer?",
                    "mapped_foundation_claim": target,
                    "boundary": "Astronomy owns contingent objects, observations, populations and cosmic history; universal laws remain with their admitted upstream branch.",
                }
                atoms.append(atom)
            rows.append({
                "source": version, "source_entry": key, "source_hash": row[hash_key],
                "source_observation": row["prior_result_observation"], "astronomy_owned": bool(target),
                "disposition": "astronomy_question_registered" if target else "reviewed_no_astronomy_owned_atom",
                "explicit_handoff": HANDOFFS.get(label), "astronomy_atom": atom,
            })
    payload = {
        "schema": "sft.astronomy-cosmology.v1-v2-initial-atomic-ownership-audit.v1",
        "status": "ownership_questions_frozen_derivations_not_yet_admitted",
        "authority_boundary": {"canonical_engine_seal": ENGINE, "verification_authority_seal": AUTHORITY, "engine_called": False, "engine_modified": False, "prior_answers_used_as_premises": False, "external_outcomes_opened": False},
        "source_surface": {"v1_rows_reviewed": len(v1["rows"]), "v2_steps_reviewed": len(v2["steps"]), "total_entries_reviewed": len(rows)},
        "ownership_law": {"astronomy_owner": "Source-dated celestial objects, observations, populations, initial conditions and cosmic histories.", "physics_consumed_not_reowned": "Universal propagation, dynamics, gravity, matter and constants.", "engineering_handoff": "Instrument implementation and observatory engineering.", "earth_biology_handoff": "Earth conditions and life remain their respective owners."},
        "summary": {"owned_source_entry_count": len(atoms), "atomic_question_count": len(atoms), "unique_atom_ids": len({x["atom_id"] for x in atoms}) == len(atoms), "explicit_handoff_count": len(HANDOFFS), "same_strength_admitted_count": 0},
        "atomic_questions": atoms, "source_rows": rows,
    }
    payload["audit_identity"] = digest(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPORT.write_text("# Astronomy and Cosmology V1/V2 initial atomic ownership audit\n\n" + f"All **{len(rows)}** registered V1/V2 entries were reviewed; **{len(atoms)}** Astronomy-owned questions were registered without importing an answer.\n\n" + "\n".join(f"- `{a['atom_id']}` → `{a['mapped_foundation_claim']}`" for a in atoms) + f"\n\nAudit identity: `{payload['audit_identity']}`\n")
    checkpoint = {"schema": "sft-v3-astronomy-cosmology-continuation-checkpoint/1", "branch": "astronomy_cosmology", "status": "initial_prior_ownership_audit_complete_inventory_not_yet_frozen", "admitted_claim_count": 0, "prior_entries_reviewed": len(rows), "prior_atomic_questions": len(atoms), "initial_audit_path": str(OUT.relative_to(ROOT)), "initial_audit_identity": payload["audit_identity"], "previous_branch_terminal_claim": "SFT-EARTH-HAZARD-RISK-HANDOFF-001", "engine_seal": ENGINE, "verification_authority_seal": AUTHORITY, "protected_authority_modified": False, "remote_publication_authorized": False, "next_exact_operation": "freeze_astronomy_foundation_inventory"}
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n")
    print(f"Astronomy prior audit: reviewed={len(rows)} atoms={len(atoms)} identity={payload['audit_identity']}")

if __name__ == "__main__": main()
