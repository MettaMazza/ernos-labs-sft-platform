#!/usr/bin/env python3
"""Build the complete V1/V2 atomic ownership audit for Biology.

This is a read-only reconciliation. Prior statements identify questions and
possible overclaims; they never enter a V3 derivation as premises. Closure is
awarded only from immutable model-admitted Biology receipts in the live census.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2_PATH = ROOT / "audits/v2_407_step_observation_census.json"
CLAIMS_PATH = ROOT / "census/claims.json"
AUDIT_PATH = ROOT / "audits/biology_v1_v2_atomic_ownership.json"
REPORT_PATH = ROOT / "audits/biology_v1_v2_atomic_ownership.md"
LEDGER_PATH = ROOT / "census/biology_prior_obligations.json"


@dataclass(frozen=True)
class Atom:
    atom_id: str
    statement: str
    claim_ids: tuple[str, ...]
    boundary: str = "Biology and Life Sciences"
    corrected: bool = False


def atom(atom_id: str, statement: str, *claim_ids: str, boundary: str = "Biology and Life Sciences", corrected: bool = False) -> Atom:
    return Atom(atom_id, statement, tuple(claim_ids), boundary, corrected)


V1_ATOMS: dict[str, tuple[Atom, ...]] = {
    "G17": (
        atom("SFT-PRIOR-V1-G17-BIO-PROTEIN-FOLD", "A biological protein-folding law must retain sequence, conditions, conformational alternatives and the observed recurrent structure class while demonstrating directed reduction without an exhaustive random search.", "SFT-BIO-PROTEIN-FOLD-001", corrected=True),
        atom("SFT-PRIOR-V1-G17-BIO-PROTEIN-ENSEMBLE", "One native-state observation may not erase alternate recurrent conformations or intrinsically disordered support.", "SFT-BIO-PROTEIN-ENSEMBLE-001", corrected=True),
    ),
    "X-1": (
        atom("SFT-PRIOR-V1-X-1-BIO-RESOURCE-COUPLED-ORGANIZATION", "Living organization must retain its resource-coupled maintenance relation while upstream thermodynamic loss remains recorded.", "SFT-BIO-LIFE-ORGANIZATION-001", "SFT-BIO-ENERGY-COUPLING-001", boundary="Physics owns thermodynamic irreversibility; Biology owns resource-coupled living maintenance."),
    ),
    "X-2": (
        atom("SFT-PRIOR-V1-X-2-BIO-LIFE-BOUNDARY", "Dissipative recurrence is not by itself life; Biology additionally requires compartment, maintenance, inheritance and regulated resource exchange.", "SFT-BIO-LIFE-CHEMICAL-BOUNDARY-001", corrected=True, boundary="Physics owns dissipative recurrence; Biology owns the additional living-organization boundary."),
    ),
    "X-3": (
        atom("SFT-PRIOR-V1-X-3-BIO-TEMPLATE-COPY", "Biological replication requires a retained template/product relation and distinct predecessor-successor provenance.", "SFT-BIO-TEMPLATE-001", "SFT-BIO-REPLICATION-001", corrected=True),
    ),
    "X-4": (
        atom("SFT-PRIOR-V1-X-4-BIO-FOUR-BASE-ALPHABET", "Two independent held distinctions generate four DNA coding symbols.", "SFT-BIO-NUCLEOTIDE-ALPHABET-001"),
        atom("SFT-PRIOR-V1-X-4-BIO-TRIPLET-CODON", "Three ordered symbol positions define the codon boundary.", "SFT-BIO-CODON-001"),
        atom("SFT-PRIOR-V1-X-4-BIO-SIXTY-FOUR-CODONS", "Four symbols in three ordered positions generate sixty-four distinct codon words.", "SFT-BIO-CODON-001"),
    ),
    "X-5": (
        atom("SFT-PRIOR-V1-X-5-BIO-HOMOCHIRALITY", "Biological homochirality is a lineage-maintained same-hand recurrence across a declared biopolymer class; molecular chirality is supplied by Chemistry and parity language cannot substitute for biological evidence.", "SFT-BIO-BIOLOGICAL-HOMOCHIRALITY-001", corrected=True, boundary="Chemistry owns molecular chirality; Biology owns its lineage-maintained biopolymer recurrence."),
    ),
    "X-6": (
        atom("SFT-PRIOR-V1-X-6-BIO-AUTOCATALYTIC-CLOSURE", "An origin-of-life candidate requires complete finite autocatalytic regeneration plus explicit compartment and resource boundaries; a threshold metaphor alone is insufficient.", "SFT-BIO-LIFE-AUTOCATALYTIC-CLOSURE-001", "SFT-BIO-LIFE-CHEMICAL-BOUNDARY-001", corrected=True),
    ),
    "X-7": (
        atom("SFT-PRIOR-V1-X-7-BIO-SELECTION", "Evolutionary selection requires heritable variation and reproducible differential continuation under a declared environment.", "SFT-BIO-VARIATION-001", "SFT-BIO-SELECTION-001"),
        atom("SFT-PRIOR-V1-X-7-BIO-FIXATION-BOUNDARY", "Fixation is whole population support at a finite boundary and is not guaranteed for every beneficial variant; drift-compatible alternatives remain explicit.", "SFT-BIO-FIXATION-001", "SFT-BIO-DRIFT-BOUNDARY-001", corrected=True),
    ),
    "X-8": (
        atom("SFT-PRIOR-V1-X-8-BIO-ECOLOGICAL-NETWORK", "Scale-free and small-world biological network labels require complete degree, path, clustering and unfavorable-model comparison on a declared sampled graph.", "SFT-BIO-ECOLOGICAL-NETWORK-001", corrected=True),
        atom("SFT-PRIOR-V1-X-8-BIO-ALLOMETRY", "Biological allometry retains taxa, size range, conditions, residuals and alternative exponents; three quarters may be tested but cannot be imported as universal.", "SFT-BIO-BIOLOGICAL-ALLOMETRY-001", corrected=True),
    ),
}


V2_ATOMS: dict[int, tuple[Atom, ...]] = {
    29: (
        atom("SFT-PRIOR-V2-29-BIO-FOUR-BASE-ALPHABET", "The DNA coding alphabet contains four generated symbol labels.", "SFT-BIO-NUCLEOTIDE-ALPHABET-001"),
        atom("SFT-PRIOR-V2-29-BIO-TRIPLET-CODON", "A codon contains three ordered symbol positions.", "SFT-BIO-CODON-001"),
        atom("SFT-PRIOR-V2-29-BIO-SIXTY-FOUR-CODONS", "The complete four-symbol triplet word space contains sixty-four codons.", "SFT-BIO-CODON-001"),
    ),
    37: (
        atom("SFT-PRIOR-V2-37-BIO-REPLICATION", "Biological copying requires template/product and predecessor/successor provenance plus explicit resource and capacity bounds; Fold preimage doubling alone does not establish biological replication.", "SFT-BIO-TEMPLATE-001", "SFT-BIO-REPLICATION-001", corrected=True),
    ),
    41: (
        atom("SFT-PRIOR-V2-41-BIO-PROTEIN-FOLD", "Protein folding is a condition-bounded transition into a recurrent structure class without exhaustive search.", "SFT-BIO-PROTEIN-FOLD-001", corrected=True),
        atom("SFT-PRIOR-V2-41-BIO-CONFORMATIONAL-ENSEMBLE", "Observed protein states retain alternate conformations and disorder rather than presupposing exactly one shape.", "SFT-BIO-PROTEIN-ENSEMBLE-001", corrected=True),
    ),
    84: (
        atom("SFT-PRIOR-V2-84-BIO-SELECTION", "Positive selection is a registered heritable differential-continuation relation, not merely an increasing fraction.", "SFT-BIO-SELECTION-001", corrected=True),
        atom("SFT-PRIOR-V2-84-BIO-FIXATION", "Fixation is whole support in a declared finite population; benefit does not make fixation structurally inevitable.", "SFT-BIO-FIXATION-001", "SFT-BIO-DRIFT-BOUNDARY-001", corrected=True),
    ),
    99: (
        atom("SFT-PRIOR-V2-99-BIO-HOMOCHIRALITY", "Biological homochirality requires source-bound same-hand biopolymer evidence and cannot be closed by an asserted weak-parity bias alone.", "SFT-BIO-BIOLOGICAL-HOMOCHIRALITY-001", corrected=True),
    ),
    144: (
        atom("SFT-PRIOR-V2-144-BIO-ORIGIN-LIFE-CLOSURE", "An origin-of-life claim requires complete autocatalytic, compartment, inheritance and resource closure at an explicit finite boundary.", "SFT-BIO-LIFE-AUTOCATALYTIC-CLOSURE-001", "SFT-BIO-LIFE-CHEMICAL-BOUNDARY-001", corrected=True),
    ),
    294: (
        atom("SFT-PRIOR-V2-294-BIO-CODON-BOXES", "Sixty-four codons partition by their first two positions into sixteen four-member boxes while all third-position labels remain held.", "SFT-BIO-CODON-BOX-001", boundary="Biology owns the codon-box atom; Chemistry owns the periodic g-block atom."),
    ),
    295: (
        atom("SFT-PRIOR-V2-295-BIO-SENESCENCE", "Senescence requires population survival, repair, censoring and condition evidence and cannot be inferred from denominator parity alone.", "SFT-BIO-SENESCENCE-001", corrected=True),
        atom("SFT-PRIOR-V2-295-BIO-EXCITABLE-THRESHOLD", "Excitable-cell firing is a condition-bounded regenerative threshold transition with subthreshold and refractory controls; no universal voltage or half-One numerical threshold is imported.", "SFT-BIO-EXCITABLE-THRESHOLD-001", corrected=True),
        atom("SFT-PRIOR-V2-295-BIO-CANCER-BOUNDARY", "Cancer requires lineage-supported dysregulation of division, death or differentiation control in tissue context; recurrence alone is insufficient.", "SFT-BIO-DYSREGULATED-DIVISION-001", corrected=True),
        atom("SFT-PRIOR-V2-295-BIO-ECOSYSTEM-STABILITY", "Ecosystem stability requires a complete state, perturbation and observation-effort record and cannot be inferred from one bounded-denominator periodic orbit.", "SFT-BIO-ECOLOGICAL-RECURRENCE-001", corrected=True),
    ),
    304: (
        atom("SFT-PRIOR-V2-304-BIO-QUATERNARY-ASSEMBLY", "Quaternary protein assembly must preserve chain identity, stoichiometry, interface contacts, adverse steric alternatives and purpose-matched structure evidence; Euclidean search, an imported clash cutoff and inaccurate Lambda Cro coordinates are not an admitted zero-parameter law.", "SFT-BIO-PROTEIN-QUATERNARY-001", corrected=True),
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
                if current is None or current.get("branch") != "biology":
                    valid = False
                    continue
                receipts.append({key: current[key] for key in ("claim_id", "receipt_path", "receipt_hash", "closure_status", "external_status")})
            closed = valid and len(receipts) == len(item.claim_ids)
            status = "same_strength_corrected_at_exact_current_boundary" if closed and item.corrected else "same_strength_reconstructed" if closed else "open_missing_same_strength_biology_receipt"
            record = {
                "atom_id": item.atom_id,
                "owner": "Biology and Life Sciences",
                "atomic_statement": item.statement,
                "categorical_boundary": item.boundary,
                "current_v3_claim_ids": list(item.claim_ids),
                "current_v3_receipts": receipts,
                "same_strength_closed": closed,
                "same_strength_status": status,
                "remaining_gap": None if closed else "No current immutable Biology receipt states this atom at the required strength.",
            }
            out_atoms.append(record)
            if not closed:
                missing_atoms.append({"source": source, "source_entry": entry, **record})
        return {
            "source": source,
            "source_entry": entry,
            "source_hash": source_hash,
            "source_observation": observation,
            "biology_owned": bool(atoms),
            "categorical_owner": "Biology or explicitly decomposed mixed source" if atoms else "another registered branch or corpus-level synthesis",
            "disposition": "biology_atoms_reviewed" if atoms else "reviewed_no_biology_owned_atom",
            "biology_atoms": out_atoms,
            "atomization_mode": "explicit_atomic_decomposition" if atoms else "explicit_nonbiology_disposition",
        }

    for record in v1_doc["rows"]:
        entry = str(record["v1_claim_id"])
        source_rows.append(materialize("v1", entry, record["source_row_sha256"], record["prior_result_observation"], V1_ATOMS.get(entry, ())))
    for record in v2_doc["steps"]:
        step = int(record["step"])
        source_rows.append(materialize("v2", str(step), record["source_block_sha256"], record["prior_result_observation"], V2_ATOMS.get(step, ())))

    atoms = [item for record in source_rows for item in record["biology_atoms"]]
    relevant_v1 = [record["source_entry"] for record in source_rows if record["source"] == "v1" and record["biology_owned"]]
    relevant_v2 = [int(record["source_entry"]) for record in source_rows if record["source"] == "v2" and record["biology_owned"]]
    closed = sum(item["same_strength_closed"] for item in atoms)
    corrected = sum(item["same_strength_status"] == "same_strength_corrected_at_exact_current_boundary" for item in atoms)
    summary = {
        "biology_owned_atom_count": len(atoms),
        "same_strength_closed_atom_count": closed,
        "same_strength_open_atom_count": len(atoms) - closed,
        "corrected_prior_atom_count": corrected,
        "unique_atom_ids": len({item["atom_id"] for item in atoms}) == len(atoms),
        "all_mixed_rows_decomposed": True,
        "every_primary_mapping_is_admitted_biology": all(receipt["claim_id"] in admitted and admitted[receipt["claim_id"]]["branch"] == "biology" for item in atoms for receipt in item["current_v3_receipts"]),
        "publication_blocked": closed != len(atoms),
    }
    audit = {
        "schema": "sft.biology.v1-v2-atomic-ownership-audit.v1",
        "audit_status": "current_evidence_closed_extension_open" if closed == len(atoms) else "open_missing_same_strength_biology_atoms",
        "purpose": "Review all 763 registered prior entries, atomize every Biology-owned question and require same-strength immutable V3 Biology receipts.",
        "authority_boundary": {
            "canonical_engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
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
            "biology_relevant_v1_rows": relevant_v1, "biology_relevant_v2_steps": relevant_v2,
            "biology_relevant_source_row_count": len(relevant_v1) + len(relevant_v2),
            "reviewed_nonbiology_source_row_count": len(source_rows) - len(relevant_v1) - len(relevant_v2),
            "current_claim_census_path": str(CLAIMS_PATH.relative_to(ROOT)),
            "current_claim_census_sha256": "sha256:" + hashlib.sha256(CLAIMS_PATH.read_bytes()).hexdigest(),
        },
        "summary": summary,
        "missing_biology_atoms": missing_atoms,
        "source_rows": source_rows,
    }
    audit["audit_identity"] = digest_json(audit)
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ledger = {
        "schema": "sft-v3-biology-prior-obligations/1",
        "status": "closed" if closed == len(atoms) else "open",
        "source_policy": {"prior_results_are_observational_data": True, "prior_answers_may_enter_v3_derivation": False, "external_measurement_may_select_survivor": False},
        "atomic_ownership_audit": str(AUDIT_PATH.relative_to(ROOT)), "atomic_ownership_audit_identity": audit["audit_identity"],
        "reviewed_source_surface": {
            "review_complete_for_branch_ownership": True, "reviewed_entry_count": len(source_rows),
            "biology_relevant_v1_rows": relevant_v1, "biology_relevant_v2_steps": relevant_v2,
            "reviewed_nonbiology_v1_rows": [record["source_entry"] for record in source_rows if record["source"] == "v1" and not record["biology_owned"]],
            "reviewed_nonbiology_v2_steps": [int(record["source_entry"]) for record in source_rows if record["source"] == "v2" and not record["biology_owned"]],
        },
        "biology_summary": {"atomic_obligation_count": len(atoms), "same_strength_closed_count": closed, "corrected_prior_atom_count": corrected, "open_count": len(atoms) - closed, "open_atomic_obligation_ids": [record["atom_id"] for record in missing_atoms]},
    }
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Biology V1/V2 atomic categorical-ownership audit", "", f"Status: `{audit['audit_status']}`.", "",
        f"All `{len(source_rows)}` prior entries were reviewed. `{len(atoms)}` Biology-owned atoms were identified; `{closed}` are closed by current immutable Biology receipts and `{len(atoms)-closed}` remain open.", "",
        "This audit never admits a claim, calls or edits the engine, imports a prior answer, or treats similarity as closure.", "",
        "## Open Biology atoms", "", "| Source | Atom | Required reconstruction |", "|---|---|---|",
    ]
    for record in missing_atoms:
        lines.append(f"| `{record['source']}:{record['source_entry']}` | `{record['atom_id']}` | {record['atomic_statement']} |")
    lines.extend(["", "## Audit identity", "", f"`{audit['audit_identity']}`", ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"biology atomic audit: reviewed={len(source_rows)} atoms={len(atoms)} closed={closed} open={len(atoms)-closed}")
    print(f"audit_identity={audit['audit_identity']}")


if __name__ == "__main__":
    main()
