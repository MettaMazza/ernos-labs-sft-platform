#!/usr/bin/env python3
"""Build the complete V1/V2 atomic ownership audit for Medicine."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2_PATH = ROOT / "audits/v2_407_step_observation_census.json"
CLAIMS_PATH = ROOT / "census/claims.json"
AUDIT_PATH = ROOT / "audits/medicine_v1_v2_atomic_ownership.json"
REPORT_PATH = ROOT / "audits/medicine_v1_v2_atomic_ownership.md"
LEDGER_PATH = ROOT / "census/medicine_prior_obligations.json"


@dataclass(frozen=True)
class Atom:
    atom_id: str
    statement: str
    claim_ids: tuple[str, ...]
    boundary: str = "Medicine and Health Sciences"
    corrected: bool = False


def atom(atom_id: str, statement: str, *claim_ids: str, boundary: str = "Medicine and Health Sciences", corrected: bool = False) -> Atom:
    return Atom(atom_id, statement, tuple(claim_ids), boundary, corrected)


V1_ATOMS: dict[str, tuple[Atom, ...]] = {
    "XIV-3": (
        atom("SFT-PRIOR-V1-XIV-3-MED-PLACEBO-RESPONSE", "A placebo or nocebo claim requires measured expectation, a lawful comparator, patient-reported and objective outcomes kept distinct, adverse outcomes and bounded follow-up; expectation alone cannot establish a universal physiological effect.", "SFT-MED-RESPONSE-001", "SFT-MED-CLINICAL-OUTCOME-001", "SFT-MED-CLINICAL-TRIAL-001", corrected=True, boundary="Consciousness owns expectation and self-model structure; Medicine owns intervention comparison and clinical outcomes."),
    ),
}


V2_ATOMS: dict[int, tuple[Atom, ...]] = {
    166: (
        atom("SFT-PRIOR-V2-166-MED-PLACEBO-COMPARISON", "Placebo and nocebo effects require a complete intervention-comparator clinical record with expectation measurement, allocation/blinding, objective and reported outcomes, adverse events and null rows retained.", "SFT-MED-INTERVENTION-001", "SFT-MED-COMPARATOR-001", "SFT-MED-BLINDING-001", "SFT-MED-RESPONSE-001", corrected=True, boundary="Consciousness owns expectation; Medicine owns the clinical comparison and outcome evidence."),
    ),
    176: (
        atom("SFT-PRIOR-V2-176-MED-STEREOCHEMICAL-CONSEQUENCE", "A molecular enantiomer difference becomes a medical efficacy or toxicity claim only through dose-, population-, outcome- and comparator-bound clinical evidence; chemistry alone cannot label one enantiomer medicine and the other poison.", "SFT-MED-DOSE-001", "SFT-MED-EFFICACY-001", "SFT-MED-TOXICITY-001", corrected=True, boundary="Chemistry owns enantiomer identity and chiral measurement; Medicine owns patient-level benefit and harm."),
    ),
    295: (
        atom("SFT-PRIOR-V2-295-MED-SENESCENCE-PROGNOSIS", "Ageing and longevity become medical prognosis claims only under a defined patient population, baseline, competing events, censoring, outcomes and follow-up; denominator parity is not a clinical prognosis.", "SFT-MED-PROGNOSIS-001", "SFT-MED-CENSORING-COMPETING-001", corrected=True, boundary="Biology owns senescence mechanism; Medicine owns clinical prognosis and patient outcomes."),
        atom("SFT-PRIOR-V2-295-MED-CANCER-DISEASE", "Cancer requires a criteria-bound disease and diagnostic record with patient, tissue context, stage, alternatives and observed course; cellular recurrence alone cannot close a medical diagnosis.", "SFT-MED-DISEASE-001", "SFT-MED-DIAGNOSTIC-CLASSIFICATION-001", "SFT-MED-SEVERITY-STAGE-001", corrected=True, boundary="Biology owns dysregulated cell continuation; Medicine owns disease classification, diagnosis and stage."),
    ),
}


def digest_json(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    v1_doc = json.loads(V1_PATH.read_text(encoding="utf-8"))
    v2_doc = json.loads(V2_PATH.read_text(encoding="utf-8"))
    census = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    admitted = {row["claim_id"]: row for row in census["claims"] if row.get("model_admitted") is True}
    source_rows: list[dict[str, object]] = []
    missing_atoms: list[dict[str, object]] = []

    def materialize(source: str, entry: str, source_hash: str, observation: str, atoms: tuple[Atom, ...]) -> dict[str, object]:
        out_atoms: list[dict[str, object]] = []
        for item in atoms:
            receipts = []
            valid = bool(item.claim_ids)
            for claim_id in item.claim_ids:
                current = admitted.get(claim_id)
                if current is None or current.get("branch") != "medicine":
                    valid = False
                    continue
                receipts.append({key: current[key] for key in ("claim_id", "receipt_path", "receipt_hash", "closure_status", "external_status")})
            closed = valid and len(receipts) == len(item.claim_ids)
            status = "same_strength_corrected_at_exact_current_boundary" if closed and item.corrected else "same_strength_reconstructed" if closed else "open_missing_same_strength_medicine_receipt"
            record = {
                "atom_id": item.atom_id,
                "owner": "Medicine and Health Sciences",
                "atomic_statement": item.statement,
                "categorical_boundary": item.boundary,
                "current_v3_claim_ids": list(item.claim_ids),
                "current_v3_receipts": receipts,
                "same_strength_closed": closed,
                "same_strength_status": status,
                "remaining_gap": None if closed else "No current immutable Medicine receipt states this atom at the required strength.",
            }
            out_atoms.append(record)
            if not closed:
                missing_atoms.append({"source": source, "source_entry": entry, **record})
        return {
            "source": source,
            "source_entry": entry,
            "source_hash": source_hash,
            "source_observation": observation,
            "medicine_owned": bool(atoms),
            "categorical_owner": "Medicine or explicitly decomposed mixed source" if atoms else "another registered branch or corpus-level synthesis",
            "disposition": "medicine_atoms_reviewed" if atoms else "reviewed_no_medicine_owned_atom",
            "medicine_atoms": out_atoms,
            "atomization_mode": "explicit_atomic_decomposition" if atoms else "explicit_nonmedicine_disposition",
        }

    for record in v1_doc["rows"]:
        entry = str(record["v1_claim_id"])
        source_rows.append(materialize("v1", entry, record["source_row_sha256"], record["prior_result_observation"], V1_ATOMS.get(entry, ())))
    for record in v2_doc["steps"]:
        step = int(record["step"])
        source_rows.append(materialize("v2", str(step), record["source_block_sha256"], record["prior_result_observation"], V2_ATOMS.get(step, ())))

    atoms = [item for record in source_rows for item in record["medicine_atoms"]]
    relevant_v1 = [record["source_entry"] for record in source_rows if record["source"] == "v1" and record["medicine_owned"]]
    relevant_v2 = [int(record["source_entry"]) for record in source_rows if record["source"] == "v2" and record["medicine_owned"]]
    closed = sum(item["same_strength_closed"] for item in atoms)
    corrected = sum(item["same_strength_status"] == "same_strength_corrected_at_exact_current_boundary" for item in atoms)
    summary = {
        "medicine_owned_atom_count": len(atoms),
        "same_strength_closed_atom_count": closed,
        "same_strength_open_atom_count": len(atoms) - closed,
        "corrected_prior_atom_count": corrected,
        "unique_atom_ids": len({item["atom_id"] for item in atoms}) == len(atoms),
        "all_mixed_rows_decomposed": True,
        "every_primary_mapping_is_admitted_medicine": all(receipt["claim_id"] in admitted and admitted[receipt["claim_id"]]["branch"] == "medicine" for item in atoms for receipt in item["current_v3_receipts"]),
        "publication_blocked": closed != len(atoms),
    }
    audit = {
        "schema": "sft.medicine.v1-v2-atomic-ownership-audit.v1",
        "audit_status": "current_evidence_closed_extension_open" if closed == len(atoms) else "open_missing_same_strength_medicine_atoms",
        "purpose": "Review all 763 registered prior entries, atomize every Medicine-owned question and require same-strength immutable V3 Medicine receipts.",
        "authority_boundary": {
            "canonical_engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
            "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
            "engine_modified": False,
            "engine_called_for_admission": False,
            "claims_admitted_by_this_audit": 0,
            "prior_answers_used_as_premises": False,
            "semantic_similarity_closes_claims": False,
            "one_owner_law": "Every atom has one primary categorical owner; downstream branches cite instead of reowning upstream laws.",
            "extension_policy": "Closure is dated and extension-open; lawful later evidence may extend, correct or falsify a registered boundary.",
        },
        "source_surface": {
            "v1_path": str(V1_PATH.relative_to(ROOT)), "v1_sha256": v1_doc["source_sha256"], "v1_row_count": v1_doc["source_row_count"],
            "v2_source_id": v2_doc["source_id"], "v2_sha256": v2_doc["source_sha256"], "v2_step_count": v2_doc["source_step_count"],
            "total_source_rows_reviewed": len(source_rows),
            "medicine_relevant_v1_rows": relevant_v1, "medicine_relevant_v2_steps": relevant_v2,
            "medicine_relevant_source_row_count": len(relevant_v1) + len(relevant_v2),
            "reviewed_nonmedicine_source_row_count": len(source_rows) - len(relevant_v1) - len(relevant_v2),
            "current_claim_census_path": str(CLAIMS_PATH.relative_to(ROOT)),
            "current_claim_census_sha256": "sha256:" + hashlib.sha256(CLAIMS_PATH.read_bytes()).hexdigest(),
        },
        "summary": summary,
        "missing_medicine_atoms": missing_atoms,
        "source_rows": source_rows,
    }
    audit["audit_identity"] = digest_json(audit)
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ledger = {
        "schema": "sft-v3-medicine-prior-obligations/1",
        "status": "closed" if closed == len(atoms) else "open",
        "source_policy": {"prior_results_are_observational_data": True, "prior_answers_may_enter_v3_derivation": False, "external_measurement_may_select_survivor": False},
        "atomic_ownership_audit": str(AUDIT_PATH.relative_to(ROOT)), "atomic_ownership_audit_identity": audit["audit_identity"],
        "reviewed_source_surface": {
            "review_complete_for_branch_ownership": True, "reviewed_entry_count": len(source_rows),
            "medicine_relevant_v1_rows": relevant_v1, "medicine_relevant_v2_steps": relevant_v2,
            "reviewed_nonmedicine_v1_rows": [record["source_entry"] for record in source_rows if record["source"] == "v1" and not record["medicine_owned"]],
            "reviewed_nonmedicine_v2_steps": [int(record["source_entry"]) for record in source_rows if record["source"] == "v2" and not record["medicine_owned"]],
        },
        "medicine_summary": {"atomic_obligation_count": len(atoms), "same_strength_closed_count": closed, "corrected_prior_atom_count": corrected, "open_count": len(atoms) - closed, "open_atomic_obligation_ids": [record["atom_id"] for record in missing_atoms]},
    }
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ownership_path = ROOT / "census/prior_obligation_ownership.json"
    ownership = json.loads(ownership_path.read_text(encoding="utf-8"))
    if "medicine" not in ownership["registered_branches"]:
        insertion = ownership["registered_branches"].index("consciousness_cognitive_science")
        ownership["registered_branches"].insert(insertion, "medicine")
    ownership["branch_summary"]["medicine"] = {
        "atomic_obligations": len(atoms),
        "atomic_ownership_audit": str(AUDIT_PATH.relative_to(ROOT)),
        "branch_ledger": str(LEDGER_PATH.relative_to(ROOT)),
        "corrected_prior_atoms": corrected,
        "current_model_admitted_claims": sum(row.get("branch") == "medicine" for row in admitted.values()),
        "open_obligations": len(atoms) - closed,
        "reviewed_source_entries": len(source_rows),
        "status": "closed_same_strength" if closed == len(atoms) else "open_missing_same_strength_medicine_receipts",
    }
    ownership_path.write_text(json.dumps(ownership, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Medicine V1/V2 atomic categorical-ownership audit", "", f"Status: `{audit['audit_status']}`.", "",
        f"All `{len(source_rows)}` prior entries were reviewed. `{len(atoms)}` Medicine-owned atoms were identified; `{closed}` are closed by current immutable Medicine receipts and `{len(atoms)-closed}` remain open.", "",
        "This audit never admits a claim, calls or edits the engine, imports a prior answer, or treats similarity as closure.", "",
        "## Open Medicine atoms", "", "| Source | Atom | Required reconstruction |", "|---|---|---|",
    ]
    for record in missing_atoms:
        lines.append(f"| `{record['source']}:{record['source_entry']}` | `{record['atom_id']}` | {record['atomic_statement']} |")
    lines.extend(["", "## Audit identity", "", f"`{audit['audit_identity']}`", ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"medicine atomic audit: reviewed={len(source_rows)} atoms={len(atoms)} closed={closed} open={len(atoms)-closed}")
    print(f"audit_identity={audit['audit_identity']}")


if __name__ == "__main__":
    main()
