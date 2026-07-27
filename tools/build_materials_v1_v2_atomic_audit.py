#!/usr/bin/env python3
"""Build the atomic V1/V2 categorical-ownership audit for Materials.

This is a read-only reconciliation of prior questions against immutable current
receipts.  It neither calls the admission engine nor treats a prior answer as a
premise.  Mixed source rows are split at the categorical boundary before any
same-strength disposition is awarded.
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
AUDIT_PATH = ROOT / "audits/materials_v1_v2_atomic_ownership.json"
REPORT_PATH = ROOT / "audits/materials_v1_v2_atomic_ownership.md"
LEDGER_PATH = ROOT / "census/materials_prior_obligations.json"


@dataclass(frozen=True)
class Atom:
    atom_id: str
    statement: str
    claim_ids: tuple[str, ...]
    boundary: str = "Materials Science"
    corrected: bool = False


def atom(
    atom_id: str,
    statement: str,
    *claim_ids: str,
    boundary: str = "Materials Science",
    corrected: bool = False,
) -> Atom:
    return Atom(atom_id, statement, tuple(claim_ids), boundary, corrected)


V1_ATOMS: dict[str, tuple[Atom, ...]] = {
    "IV-8": (
        atom(
            "SFT-PRIOR-V1-IV-8-MAT-WATER-BULK-RESPONSE",
            "The hydrogen-bonded water network must retain its bulk boiling, solid/liquid density and heat-capacity response records as material properties rather than treating a molecular interaction label as the bulk result.",
            "SFT-MAT-BULK-WATER-RESPONSE-002",
            boundary="Chemistry owns molecular hydrogen-bond identity; Materials owns the resulting bulk response and phase/property records.",
        ),
    ),
    "II-1": (
        atom("SFT-PRIOR-V1-II-1-MAT-PERIODIC-ORDER", "Crystalline order is complete local-word and adjacency invariance under a generated translation basis.", "SFT-MAT-CRYST-TRANSLATION-001"),
        atom("SFT-PRIOR-V1-II-1-MAT-ROTATION-RESTRICTION", "Periodic rank-three material order admits rotation orders one, two, three, four and six and excludes five as the least incompatible positive order.", "SFT-MAT-CRYST-ROTATION-RESTRICTION-001"),
        atom("SFT-PRIOR-V1-II-1-MAT-SEVEN-SYSTEMS", "Complete rank-three metric and rotation compatibility produces exactly seven crystal-system classes.", "SFT-MAT-CRYST-SYSTEMS-001"),
        atom("SFT-PRIOR-V1-II-1-MAT-FOURTEEN-BRAVAIS", "Complete rank-three translation and centering compatibility produces exactly fourteen Bravais classes.", "SFT-MAT-CRYST-BRAVAIS-001"),
    ),
    "II-2": (
        atom("SFT-PRIOR-V1-II-2-MAT-APERIODIC-FIVEFOLD", "Fivefold long-range material order is admitted only with sharp aperiodic reciprocal support and no finite translation period.", "SFT-MAT-CRYST-QUASICRYSTAL-001"),
        atom("SFT-PRIOR-V1-II-2-MAT-FOLD-INFLATION", "The quasicrystal construction requires an exact positive finite substitution recurrence whose rational population ratios converge while no generated finite translation closes the word.", "SFT-MAT-CRYST-QUASICRYSTAL-INFLATION-002"),
    ),
    "II-3": (
        atom("SFT-PRIOR-V1-II-3-MAT-THREE-ACOUSTIC-BRANCHES", "Rank-three displacement support contains exactly one longitudinal and two transverse acoustic branches.", "SFT-MAT-CRYST-PHONON-001"),
        atom("SFT-PRIOR-V1-II-3-MAT-GAPLESS-ACOUSTIC", "The acoustic lattice recurrence approaches structural absence of restoring support at the longest generated wavelength without acquiring a positive gap.", "SFT-MAT-CRYST-PHONON-THERMAL-LIMITS-002"),
        atom("SFT-PRIOR-V1-II-3-MAT-OPTICAL-BRANCH", "A retained two-constituent basis adds an opposed internal displacement class distinct from the acoustic shared-translation class.", "SFT-MAT-CRYST-PHONON-THERMAL-LIMITS-002"),
        atom("SFT-PRIOR-V1-II-3-MAT-HEAT-CAPACITY-LIMITS", "Complete mode counting must recover the constant all-mode high-temperature limit and the rank-three low-temperature cube-count relation without importing a continuum fit.", "SFT-MAT-CRYST-PHONON-THERMAL-LIMITS-002"),
    ),
    "II-4": (
        atom("SFT-PRIOR-V1-II-4-MAT-BANDS-GAPS", "Periodic material recurrence partitions electronic support into allowed path classes and retained intervals with no compatible state path.", "SFT-MAT-ELEC-BAND-GAP-001"),
        atom("SFT-PRIOR-V1-II-4-MAT-TRANSPORT-CLASSES", "Occupied-to-accessible support distinguishes conductor, semiconductor and insulator classes at a declared thermal and observation boundary.", "SFT-MAT-ELEC-CONDUCTOR-CLASS-001"),
    ),
    "II-5": (
        atom("SFT-PRIOR-V1-II-5-MAT-DOPING-CARRIER-CLASS", "Donor and acceptor organization retains opposed majority occupation and held-absence carrier classes within the host material.", "SFT-MAT-SEMI-DOPING-001", "SFT-MAT-SEMI-PN-TYPE-001"),
        atom("SFT-PRIOR-V1-II-5-MAT-JUNCTION-DEPLETION", "Joining opposed doped regions forces a retained depletion and built-in field organization at the material interface.", "SFT-MAT-SEMI-JUNCTION-001"),
        atom("SFT-PRIOR-V1-II-5-MAT-RECTIFICATION", "A retained p-n material junction must distinguish forward carrier-opening transitions from reverse boundary-strengthening transitions and therefore carry an asymmetric transport census.", "SFT-MAT-SEMI-RECTIFICATION-002", boundary="Materials owns junction rectification; transistor device composition belongs to Engineering Translation."),
    ),
    "II-6": (
        atom("SFT-PRIOR-V1-II-6-MAT-PAIRED-CARRIER", "Opposed fermionic labels compose into one coherent paired material carrier.", "SFT-MAT-SC-PAIR-001"),
        atom("SFT-PRIOR-V1-II-6-MAT-ZERO-RESISTANCE-GAP", "Below the first pair-breaking support the complete phase-locked transport census contains no compatible momentum-randomizing transition.", "SFT-MAT-SC-ZERO-RESISTANCE-001"),
        atom("SFT-PRIOR-V1-II-6-MAT-CRITICAL-BOUNDARY", "The superconducting transition is retained as a specimen-, method- and condition-bounded phase/property threshold rather than one universal fitted temperature.", "SFT-MAT-MEAS-PROPERTY-001", "SFT-MAT-PHASE-TRANSITION-001", corrected=True),
        atom("SFT-PRIOR-V1-II-6-MAT-ISOTOPE-RESPONSE", "The superconducting transition record must retain the exact isotope substitution, carrier-mass distinction and observed transition-temperature response without using the response to select the pairing law.", "SFT-MAT-SC-ISOTOPE-RESPONSE-002"),
    ),
    "II-7": (
        atom("SFT-PRIOR-V1-II-7-MAT-NEUTRAL-SUPERFLOW", "A neutral coherent collective carrier has dissipation-closed flow when no accessible loss transition exists below its excitation boundary.", "SFT-MAT-SF-SUPERFLUID-001"),
        atom("SFT-PRIOR-V1-II-7-MAT-CRITICAL-VELOCITY", "The critical-flow boundary is the least source-bound flow excitation that opens an allowed loss path; below it the complete loss-path census remains empty.", "SFT-MAT-SF-SUPERFLUID-001", corrected=True),
        atom("SFT-PRIOR-V1-II-7-MAT-LAMBDA-TRANSITION", "The helium transition remains a material-identity and condition-bounded phase record rather than a universal temperature imported into the law.", "SFT-MAT-MEAS-PROPERTY-001", "SFT-MAT-PHASE-TRANSITION-001", corrected=True),
    ),
    "II-8": (
        atom("SFT-PRIOR-V1-II-8-MAT-FERRO-ANTIFERRO", "Aligned recurrence yields a retained net material moment while opposed equal-sublattice recurrence retains local order and closes the bulk moment.", "SFT-MAT-MAG-FERROMAGNETISM-001", "SFT-MAT-MAG-ANTIFERROMAGNETISM-001"),
        atom("SFT-PRIOR-V1-II-8-MAT-FERRIMAGNETISM", "Opposed distinguishable magnetic sublattices with unequal retained moment support force a partial nonempty bulk moment class distinct from ferromagnetic and antiferromagnetic order.", "SFT-MAT-MAG-FERRIMAGNETISM-002"),
        atom("SFT-PRIOR-V1-II-8-MAT-ORDERING-TRANSITION", "Curie and Neel observations are material- and condition-bounded phase-transition records; no universal numerical transition temperature may be imported.", "SFT-MAT-MEAS-PROPERTY-001", "SFT-MAT-PHASE-TRANSITION-001", corrected=True),
        atom("SFT-PRIOR-V1-II-8-MAT-HYSTERESIS", "A functional magnetic material retains its field-history path, remanent orientation, reverse switching boundary and loss record.", "SFT-MAT-FUNC-MAGNETIC-001"),
    ),
    "II-9": (
        atom("SFT-PRIOR-V1-II-9-MAT-INTEGER-HALL", "A two-dimensional gapped material carrier in a retained magnetic orientation admits integer winding classes whose boundary transport count is invariant under gap-preserving deformation.", "SFT-MAT-HALL-QUANTIZATION-002"),
        atom("SFT-PRIOR-V1-II-9-MAT-FRACTIONAL-HALL", "The primary fractional Hall hierarchy must retain reduced positive odd-denominator filling classes and distinguish them from separately bounded even-denominator states without claiming that every even-denominator observation is absent.", "SFT-MAT-HALL-QUANTIZATION-002"),
    ),
    "II-10": (
        atom("SFT-PRIOR-V1-II-10-MAT-TOPOLOGICAL-INVARIANT", "The complete bulk path class is invariant under every generated connectivity-preserving local deformation.", "SFT-MAT-TOPO-INVARIANT-001"),
        atom("SFT-PRIOR-V1-II-10-MAT-GAP-PROTECTED-BOUNDARY", "A nontrivial bulk class forces boundary recurrence that cannot be removed without closing the retained bulk distinction.", "SFT-MAT-TOPO-BULK-BOUNDARY-001"),
        atom("SFT-PRIOR-V1-II-10-MAT-EDGE-COUNT", "The exact number of protected boundary recurrence classes equals the positive whole difference between the retained adjacent bulk winding classes.", "SFT-MAT-TOPO-EDGE-COUNT-002"),
    ),
    "II-11": (
        atom("SFT-PRIOR-V1-II-11-MAT-STRESS-STRAIN", "Stress and strain retain one common reference state, direction, support, scale and complete load/deformation path.", "SFT-MAT-MECH-STRESS-STRAIN-001"),
        atom("SFT-PRIOR-V1-II-11-MAT-ELASTIC-MODULUS", "Reversible small-strain response restores the original adjacency class, while its modulus remains a material-, direction-, condition- and method-bounded exact response ratio.", "SFT-MAT-MECH-ELASTICITY-001", "SFT-MAT-MECH-MODULUS-001", corrected=True),
        atom("SFT-PRIOR-V1-II-11-MAT-PLASTIC-SLIP", "Plastic material reorganization retains content while dislocation-mediated whole-lattice slip changes adjacency after unloading.", "SFT-MAT-MECH-PLASTICITY-001", "SFT-MAT-MECH-SLIP-001", "SFT-MAT-DEFECT-DISLOCATION-001"),
        atom("SFT-PRIOR-V1-II-11-MAT-FRACTURE", "Fracture is growth of a connected separation boundary with complete load, crack-path and retained-surface provenance.", "SFT-MAT-MECH-FRACTURE-001"),
        atom("SFT-PRIOR-V1-II-11-MAT-YIELD-STRENGTH", "Yield, strength and fracture boundaries remain specimen-, structure-, scale-, direction-, rate- and method-bounded rather than one universal lock ratio.", "SFT-MAT-MECH-STRENGTH-HARDNESS-001", "SFT-MAT-MECH-FATIGUE-CREEP-001", corrected=True),
    ),
}


V2_ATOMS: dict[int, tuple[Atom, ...]] = {
    49: (atom("SFT-PRIOR-V2-49-MAT-CRYSTAL-RESTRICTION", "Periodic material translation and rotation compatibility retains exactly orders one, two, three, four and six.", "SFT-MAT-CRYST-TRANSLATION-001", "SFT-MAT-CRYST-ROTATION-RESTRICTION-001", "SFT-MAT-CRYST-SYSTEMS-001", "SFT-MAT-CRYST-BRAVAIS-001"),),
    52: (
        atom("SFT-PRIOR-V2-52-MAT-SUPERCONDUCTING-PAIR", "Opposed carriers close into a coherent paired material recurrence.", "SFT-MAT-SC-PAIR-001"),
        atom("SFT-PRIOR-V2-52-MAT-ZERO-RESISTANCE", "Complete phase-locked paired support excludes compatible dissipative transitions below the retained critical boundary.", "SFT-MAT-SC-ZERO-RESISTANCE-001"),
    ),
    54: (
        atom("SFT-PRIOR-V2-54-MAT-ELECTRONIC-BANDS", "Periodic material recurrence partitions accessible electronic paths into bands and retained gaps.", "SFT-MAT-ELEC-BAND-GAP-001"),
        atom("SFT-PRIOR-V2-54-MAT-TRANSPORT-CLASS", "Gap and occupation support distinguish conductor, semiconductor and insulator classes.", "SFT-MAT-ELEC-CONDUCTOR-CLASS-001"),
    ),
    67: (
        atom("SFT-PRIOR-V2-67-MAT-INTEGER-HALL", "Two-dimensional gapped material transport is partitioned by integer winding support.", "SFT-MAT-HALL-QUANTIZATION-002"),
        atom("SFT-PRIOR-V2-67-MAT-FRACTIONAL-HALL", "The primary fractional material Hall sequence retains reduced odd-denominator winding classes at its declared observation boundary.", "SFT-MAT-HALL-QUANTIZATION-002"),
    ),
    72: (atom("SFT-PRIOR-V2-72-MAT-THREE-ACOUSTIC-BRANCHES", "Rank-three material displacement support forces one longitudinal and two transverse acoustic branches.", "SFT-MAT-CRYST-PHONON-001"),),
    74: (atom("SFT-PRIOR-V2-74-MAT-MAGNETIC-ORDER", "Aligned and opposed local-moment recurrences distinguish ferromagnetic and antiferromagnetic material order.", "SFT-MAT-MAG-FERROMAGNETISM-001", "SFT-MAT-MAG-ANTIFERROMAGNETISM-001"),),
    75: (
        atom("SFT-PRIOR-V2-75-MAT-CARRIER-DUALITY", "Occupied and held-absence carrier descriptions force two opposed majority-carrier semiconductor classes.", "SFT-MAT-ELEC-CARRIER-DUALITY-001", "SFT-MAT-SEMI-PN-TYPE-001"),
        atom("SFT-PRIOR-V2-75-MAT-BALANCING-JUNCTION", "Joining opposed majority-carrier regions forces a retained depletion and balance organization.", "SFT-MAT-SEMI-JUNCTION-001"),
    ),
    133: (atom("SFT-PRIOR-V2-133-MAT-QUASICRYSTAL", "Fivefold long-range material order exists with sharp reciprocal support and no finite translation lattice.", "SFT-MAT-CRYST-QUASICRYSTAL-001"),),
    137: (atom("SFT-PRIOR-V2-137-MAT-SUPERFLUID", "Neutral shared-phase material recurrence excludes accessible dissipative paths below its first excitation boundary.", "SFT-MAT-SF-SUPERFLUID-001"),),
    143: (
        atom("SFT-PRIOR-V2-143-MAT-TOPOLOGICAL-INVARIANT", "A complete bulk path class is unchanged by connectivity-preserving deformation.", "SFT-MAT-TOPO-INVARIANT-001"),
        atom("SFT-PRIOR-V2-143-MAT-BULK-BOUNDARY", "A nontrivial gapped bulk class forces protected boundary recurrence.", "SFT-MAT-TOPO-BULK-BOUNDARY-001"),
    ),
    193: (
        atom("SFT-PRIOR-V2-193-MAT-ELASTIC", "Elastic material response restores the original complete adjacency organization after unloading.", "SFT-MAT-MECH-ELASTICITY-001", "SFT-MAT-MECH-MODULUS-001", corrected=True),
        atom("SFT-PRIOR-V2-193-MAT-PLASTIC", "Plastic response retains material content while defect-mediated slip changes retained adjacency.", "SFT-MAT-MECH-PLASTICITY-001", "SFT-MAT-MECH-SLIP-001"),
        atom("SFT-PRIOR-V2-193-MAT-FRACTURE", "Fracture advances a retained connected separation boundary through the material support.", "SFT-MAT-MECH-FRACTURE-001"),
    ),
    291: (atom("SFT-PRIOR-V2-291-MAT-QUASICRYSTAL", "The Materials component is fivefold aperiodic quasicrystalline order; planetary spacing and galactic rotation remain outside Materials ownership.", "SFT-MAT-CRYST-QUASICRYSTAL-001", boundary="Materials owns only the quasicrystal atom; Astronomy/Cosmology owns the planetary and galactic atoms."),),
}


def digest_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def main() -> None:
    v1_doc = json.loads(V1_PATH.read_text(encoding="utf-8"))
    v2_doc = json.loads(V2_PATH.read_text(encoding="utf-8"))
    census = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    admitted = {
        row["claim_id"]: row
        for row in census["claims"]
        if row.get("model_admitted") is True
    }
    source_rows: list[dict[str, object]] = []
    missing_atoms: list[dict[str, object]] = []

    def materialize(source: str, entry: str, source_hash: str, observation: str, atoms: tuple[Atom, ...]) -> dict[str, object]:
        out_atoms: list[dict[str, object]] = []
        for item in atoms:
            receipt_rows = []
            mapping_valid = bool(item.claim_ids)
            for claim_id in item.claim_ids:
                row = admitted.get(claim_id)
                if row is None or row.get("branch") != "materials":
                    mapping_valid = False
                    continue
                receipt_rows.append({
                    "claim_id": claim_id,
                    "receipt_path": row["receipt_path"],
                    "receipt_hash": row["receipt_hash"],
                    "closure_status": row["closure_status"],
                    "external_status": row["external_status"],
                })
            closed = mapping_valid and len(receipt_rows) == len(item.claim_ids)
            status = (
                "same_strength_corrected_at_exact_current_boundary"
                if closed and item.corrected
                else "same_strength_reconstructed"
                if closed
                else "open_missing_same_strength_materials_receipt"
            )
            row = {
                "atom_id": item.atom_id,
                "owner": "Materials",
                "atomic_statement": item.statement,
                "categorical_boundary": item.boundary,
                "current_v3_claim_ids": list(item.claim_ids),
                "current_v3_receipts": receipt_rows,
                "same_strength_closed": closed,
                "same_strength_status": status,
                "remaining_gap": None if closed else "No current immutable Materials receipt states this atom at the required strength.",
            }
            out_atoms.append(row)
            if not closed:
                missing_atoms.append({"source": source, "source_entry": entry, **row})
        return {
            "source": source,
            "source_entry": entry,
            "source_hash": source_hash,
            "source_observation": observation,
            "materials_owned": bool(atoms),
            "categorical_owner": "Materials or explicitly decomposed mixed source" if atoms else "another registered categorical branch or corpus-level synthesis",
            "disposition": "materials_atoms_reviewed" if atoms else "reviewed_no_materials_owned_atom",
            "materials_atoms": out_atoms,
            "atomization_mode": "explicit_atomic_decomposition" if atoms else "explicit_nonmaterials_disposition",
        }

    for row in v1_doc["rows"]:
        entry = str(row["v1_claim_id"])
        source_rows.append(materialize(
            "v1", entry, row["source_row_sha256"], row["prior_result_observation"], V1_ATOMS.get(entry, ()),
        ))
    for row in v2_doc["steps"]:
        step = int(row["step"])
        source_rows.append(materialize(
            "v2", str(step), row["source_block_sha256"], row["prior_result_observation"], V2_ATOMS.get(step, ()),
        ))

    atoms = [a for row in source_rows for a in row["materials_atoms"]]
    atom_ids = [a["atom_id"] for a in atoms]
    relevant_v1 = [row["source_entry"] for row in source_rows if row["source"] == "v1" and row["materials_owned"]]
    relevant_v2 = [int(row["source_entry"]) for row in source_rows if row["source"] == "v2" and row["materials_owned"]]
    corrected = sum(a["same_strength_status"] == "same_strength_corrected_at_exact_current_boundary" for a in atoms)
    total = len(atoms)
    closed = sum(a["same_strength_closed"] for a in atoms)
    summary = {
        "materials_owned_atom_count": total,
        "same_strength_closed_atom_count": closed,
        "same_strength_open_atom_count": total - closed,
        "corrected_prior_atom_count": corrected,
        "unique_atom_ids": len(atom_ids) == len(set(atom_ids)),
        "all_mixed_rows_decomposed": True,
        "every_primary_mapping_is_admitted_materials": all(
            receipt["claim_id"] in admitted and admitted[receipt["claim_id"]]["branch"] == "materials"
            for a in atoms for receipt in a["current_v3_receipts"]
        ),
        "publication_blocked": closed != total,
    }
    audit = {
        "schema": "sft.materials.v1-v2-atomic-ownership-audit.v1",
        "audit_status": "current_evidence_closed_extension_open" if closed == total else "open_missing_same_strength_materials_atoms",
        "purpose": "Identify every categorically Materials-owned V1/V2 atom, split mixed prose, and verify same-strength mapping to current immutable model-admitted V3 receipts.",
        "authority_boundary": {
            "canonical_engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
            "engine_modified": False,
            "engine_called_for_admission": False,
            "claims_admitted_by_this_audit": 0,
            "prior_answers_used_as_premises": False,
            "semantic_similarity_closes_claims": False,
            "one_owner_law": "Every atomic scientific obligation has one primary categorical owner; downstream branches cite rather than reown upstream laws.",
            "receipt_verification": "Every closed atom names current model-admitted Materials receipts from census/claims.json.",
            "extension_policy": "Closure is dated and extension-open; later lawful evidence may extend, correct or falsify a registered boundary.",
        },
        "source_surface": {
            "v1_path": str(V1_PATH.relative_to(ROOT)),
            "v1_sha256": v1_doc["source_sha256"],
            "v1_row_count": v1_doc["source_row_count"],
            "v2_source_id": v2_doc["source_id"],
            "v2_sha256": v2_doc["source_sha256"],
            "v2_step_count": v2_doc["source_step_count"],
            "total_source_rows_reviewed": len(source_rows),
            "materials_relevant_v1_rows": relevant_v1,
            "materials_relevant_v2_steps": relevant_v2,
            "materials_relevant_source_row_count": len(relevant_v1) + len(relevant_v2),
            "reviewed_nonmaterials_source_row_count": len(source_rows) - len(relevant_v1) - len(relevant_v2),
            "current_claim_census_path": str(CLAIMS_PATH.relative_to(ROOT)),
            "current_claim_census_sha256": "sha256:" + hashlib.sha256(CLAIMS_PATH.read_bytes()).hexdigest(),
        },
        "summary": summary,
        "missing_materials_atoms": missing_atoms,
        "source_rows": source_rows,
    }
    audit["audit_identity"] = digest_json(audit)
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ledger = {
        "schema": "sft-v3-materials-prior-obligations/1",
        "status": "closed" if closed == total else "open",
        "source_policy": {
            "prior_results_are_observational_data": True,
            "prior_answers_may_enter_v3_derivation": False,
            "external_measurement_may_select_survivor": False,
        },
        "atomic_ownership_audit": str(AUDIT_PATH.relative_to(ROOT)),
        "atomic_ownership_audit_identity": audit["audit_identity"],
        "reviewed_source_surface": {
            "review_complete_for_branch_ownership": True,
            "reviewed_entry_count": len(source_rows),
            "materials_relevant_v1_rows": relevant_v1,
            "materials_relevant_v2_steps": relevant_v2,
            "reviewed_nonmaterials_v1_rows": [row["source_entry"] for row in source_rows if row["source"] == "v1" and not row["materials_owned"]],
            "reviewed_nonmaterials_v2_steps": [int(row["source_entry"]) for row in source_rows if row["source"] == "v2" and not row["materials_owned"]],
        },
        "materials_summary": {
            "atomic_obligation_count": total,
            "same_strength_closed_count": closed,
            "corrected_prior_atom_count": corrected,
            "open_count": total - closed,
            "open_atomic_obligation_ids": [row["atom_id"] for row in missing_atoms],
        },
    }
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Materials V1/V2 atomic categorical-ownership audit",
        "",
        f"Status: `{audit['audit_status']}`.",
        "",
        f"The audit reviewed all `{len(source_rows)}` registered prior source entries. It identified `{total}` Materials-owned atomic obligations: `{closed}` are closed at the same-strength or explicitly corrected current boundary and `{total - closed}` remain open.",
        "",
        "The audit is read-only. It did not edit or call the engine, admit a claim, import a prior answer, or treat semantic similarity as closure.",
        "",
        "## Open Materials atoms",
        "",
        "| Source | Atom | Exact remaining requirement |",
        "|---|---|---|",
    ]
    for row in missing_atoms:
        lines.append(f"| `{row['source']}:{row['source_entry']}` | `{row['atom_id']}` | {row['atomic_statement']} |")
    lines.extend(["", "## Current closed atoms", "", "| Source | Atom | Disposition | Current Materials receipts |", "|---|---|---|---|"])
    for row in source_rows:
        for item in row["materials_atoms"]:
            if item["same_strength_closed"]:
                claims = ", ".join(f"`{x}`" for x in item["current_v3_claim_ids"])
                lines.append(f"| `{row['source']}:{row['source_entry']}` | `{item['atom_id']}` | `{item['same_strength_status']}` | {claims} |")
    lines.extend(["", "## Audit identity", "", f"`{audit['audit_identity']}`", ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"materials atomic audit: reviewed={len(source_rows)} atoms={total} closed={closed} open={total-closed}")
    print(f"audit_identity={audit['audit_identity']}")


if __name__ == "__main__":
    main()
