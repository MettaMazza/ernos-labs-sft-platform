#!/usr/bin/env python3
"""Open and preserve the complete INORG-003 topology vector after identity seal."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-003-ligand-denticity-chelation-v1"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/ligand_denticity_chelation_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/ligand_denticity_chelation_withheld_targets_v1.json"
PRIMARY = SNAPSHOT / "ligand-denticity-chelation-primary-records-v1.json"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def term(name: str) -> dict:
    return json.loads((SNAPSHOT / name).read_text(encoding="utf-8"))["term"]


def surface(document: dict, role: str, snapshot_path: Path) -> str:
    if role == "complete-current-term-record":
        return hash_file(snapshot_path)
    if role == "complete-definition-surface":
        return canonical(document.get("definitions", []))
    if role == "complete-example-and-boundary-surface":
        return canonical(
            {
                "also_defines": document.get("also defines"),
                "definitions": [
                    {
                        "id": row.get("id"),
                        "text": row.get("text"),
                        "examples": row.get("exams", {}),
                        "contexts": row.get("contexts", {}),
                        "links": row.get("links", []),
                    }
                    for row in document.get("definitions", [])
                ],
            }
        )
    if role == "complete-status-source-citation-license-and-disclaimer-surface":
        return canonical(
            {
                "code": document.get("code"),
                "title": document.get("title"),
                "status": document.get("status"),
                "definition_sources": [
                    {
                        "sources": row.get("sources", []),
                        "seealso": row.get("seealso", []),
                    }
                    for row in document.get("definitions", [])
                ],
                "citation": document.get("citation"),
                "license": document.get("license"),
                "disclaimer": document.get("disclaimer"),
                "accessed": document.get("accessed"),
            }
        )
    raise ValueError(f"unknown INORG-003 source surface: {role}")


def main() -> None:
    identity_document = json.loads(IDENTITIES.read_text(encoding="utf-8"))
    if identity_document.get("target_values_or_hashes_present") is not False:
        raise ValueError("INORG-003 identity seal contains target values")
    documents = {
        row["source_document_identity"]: term(row["source_document_identity"])
        for row in identity_document["rows"]
    }
    rows = []
    for identity in identity_document["rows"]:
        snapshot_path = ROOT / identity["snapshot_path"]
        inscription = surface(
            documents[identity["source_document_identity"]],
            identity["source_record_role"],
            snapshot_path,
        )
        rows.append(
            identity
            | {
                "source_inscription": inscription,
                "target_payload_hash": sha256_identity(
                    (identity["target_id"], identity["source_record_role"], inscription)
                ),
                "status": "reported-authoritative-record",
            }
        )

    targets = {
        "schema": "sft-v3-ligand-denticity-chelation-withheld-targets/1",
        "identity_document_sha256": hash_file(IDENTITIES),
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": len(rows),
        "rows": rows,
    }
    TARGETS.write_text(json.dumps(targets, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    definitions = {
        name: " ".join(row.get("text", "") for row in document.get("definitions", []))
        for name, document in documents.items()
    }
    chelation = definitions["iupac-chelation.json"]
    denticity = definitions["iupac-denticity.json"]
    kappa = definitions["iupac-kappa.json"]
    eta = definitions["iupac-eta.json"]
    binding = definitions["iupac-binding-sites.json"]
    ligands = definitions["iupac-ligands.json"]
    analysis = {
        "all_six_complete_current_term_records_retained": len(documents) == 6
        and all(document.get("status") == "current" for document in documents.values()),
        "binding_site_region_or_atom_and_stabilizing_interaction_retained": "specific region (or atom)" in binding
        and "stabilizing interaction" in binding,
        "denticity_given_ligand_same_central_count_retained": "number of donor groups from a given ligand" in denticity
        and "same central atom" in denticity,
        "chelation_separate_sites_same_ligand_single_central_retained": "two or more separate binding sites within the same ligand" in chelation
        and "single central atom" in chelation,
        "first_multiple_site_threshold_retained": "at least two of which must be used" in chelation,
        "bidentate_ethylenediamine_two_nitrogen_example_retained": "bidentate ethylenediamine" in chelation
        and "both nitrogen atoms" in chelation
        and "bonded to copper" in chelation,
        "single_binding_site_nonchelate_exclusions_retained": all(
            value in chelation
            for value in ("[PtCl3(CH2=CH2)]", "ferrocene", "(benzene)tricarbonylchromium", "single binding sites")
        ),
        "kappa_single_atom_attachment_count_retained": "single ligating atom attachments" in kappa
        and "numerical index indicates the number" in kappa,
        "eta_multi_atom_pi_support_boundary_retained": "topological indication" in eta
        and "number of ligating atoms" in eta,
        "inorganic_and_biochemical_ligand_scope_boundary_retained": "In an inorganic coordination entity" in ligands
        and "Biochemical usage is thus wider" in ligands,
        "all_status_source_citation_license_and_disclaimer_surfaces_retained": all(
            document.get("citation")
            and document.get("license")
            and "continuously reviewing" in document.get("disclaimer", "")
            and all(row.get("sources") for row in document.get("definitions", []))
            for document in documents.values()
        ),
    }
    if not all(analysis.values()):
        raise ValueError(f"INORG-003 authoritative topology surface changed: {analysis}")

    primary = {
        "schema": "sft-v3-ligand-denticity-chelation-primary-records/1",
        "chemistry_obligation": "SFT-CHEM-OBL-INORG-003",
        "claim_id": "SFT-CHEM-LIGAND-DENTICITY-CHELATION-TOPOLOGY-003",
        "identity_document_sha256": hash_file(IDENTITIES),
        "target_document_sha256": hash_file(TARGETS),
        "complete_registered_target_count": len(rows),
        "complete_source_file_count": 6,
        "source_class_census": {"IUPAC": len(rows)},
        "exact_postseal_topology_analysis": analysis,
        "source_reported_term_codes": {
            name: document["code"] for name, document in documents.items()
        },
        "complete_external_topology_vector": {
            "denticity_relation": "given ligand; donor-group count; same central atom",
            "chelation_relation": "multiple separate binding sites; same ligand; one central atom",
            "first_closed_topology": "at least two used binding sites",
            "single_binding_site_exclusions": [
                "PtCl3-ethene",
                "ferrocene",
                "benzene-tricarbonylchromium",
            ],
            "attachment_mode_boundary": ["kappa single-atom attachment count", "eta pi-system ligating-atom topology"],
        },
        "no_source_topology_or_classification_used_as_fold_proof_parameter": True,
        "rows": rows,
    }
    PRIMARY.write_text(json.dumps(primary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "targets": len(rows),
                "targets_sha256": hash_file(TARGETS),
                "primary_sha256": hash_file(PRIMARY),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
