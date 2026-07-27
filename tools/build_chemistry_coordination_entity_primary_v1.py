#!/usr/bin/env python3
"""Open and preserve the complete INORG-001 structural target vector post seal."""

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-001-coordination-entity-v1"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/coordination_entity_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/coordination_entity_withheld_targets_v1.json"
PRIMARY = SNAPSHOT / "coordination-entity-primary-records-v1.json"


class Surface(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag == "sub":
            self.parts.append("_")

    def handle_data(self, data: str) -> None:
        value = " ".join(unescape(data).split())
        if value:
            self.parts.append(value)

    @property
    def text(self) -> str:
        return " ".join(self.parts)


def html_text(name: str) -> str:
    parser = Surface()
    parser.feed((SNAPSHOT / name).read_text(encoding="utf-8", errors="replace"))
    return parser.text


def main() -> None:
    identity_document = json.loads(IDENTITIES.read_text(encoding="utf-8"))
    if identity_document.get("target_values_or_hashes_present") is not False:
        raise ValueError("INORG-001 identity seal contains target values")
    terms = {
        name: json.loads((SNAPSHOT / name).read_text(encoding="utf-8"))["term"]
        for name in ("iupac-coordination-entity.json", "iupac-central-atom.json", "iupac-ligands.json")
    }
    fe = html_text("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html")
    ferro = html_text("nist-cccbdb-ferrocene-experimental-geometry.html")
    required_fe = (
        "Listing of experimental geometry data for Fe(CO) _ 5 (Iron pentacarbonyl)", "Point Group D _ 3h",
        "rCO 1.145", "C-Fe 5", "C#O 5", "Fe1 0.0000 0.0000 0.0000",
        "1976Hellwege(II/7)", "No experimental rotational constants available.",
    )
    required_ferro = (
        "Listing of experimental geometry data for Fe(C _ 5 H _ 5 ) _ 2 (ferrocene)", "Point Group D _ 5d",
        "C-Fe 10", "C:C 10", "H-C 10", "No coordinate data available.",
        "No experimental rotational constants available.",
    )
    if any(value not in fe for value in required_fe) or any(value not in ferro for value in required_ferro):
        raise ValueError("INORG-001 complete NIST structure surface changed")
    values = {
        "coordination-entity-current-term": terms["iupac-coordination-entity.json"]["definitions"][0]["text"],
        "central-atom-current-term": terms["iupac-central-atom.json"]["definitions"][0]["text"],
        "ligands-current-term": terms["iupac-ligands.json"]["definitions"][0]["text"],
        "FeCO5-complete-page": hash_file(SNAPSHOT / "nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html"),
        "FeCO5-entity-identity": "Fe(CO)5; Iron pentacarbonyl",
        "FeCO5-point-group": "D3h",
        "FeCO5-C-Fe-link-count": "5",
        "FeCO5-C-O-link-count": "5",
        "FeCO5-internal-coordinate-record": "rCO=1.145 angstrom; source comment average of equatorial and axial",
        "FeCO5-coordinate-table": "Fe1 and ten retained C/O occurrences; five Fe-C distances 1.8240 angstrom",
        "FeCO5-reference-record": "1976Hellwege(II/7); Structure Data of Free Polyatomic Molecules",
        "FeCO5-rotational-data-status": "No experimental rotational constants available",
        "ferrocene-complete-page": hash_file(SNAPSHOT / "nist-cccbdb-ferrocene-experimental-geometry.html"),
        "ferrocene-entity-identity": "Fe(C5H5)2; ferrocene",
        "ferrocene-point-group": "D5d",
        "ferrocene-C-Fe-link-count": "10",
        "ferrocene-C-C-link-count": "10",
        "ferrocene-H-C-link-count": "10",
        "ferrocene-coordinate-data-status": "No coordinate data available",
        "ferrocene-rotational-data-status": "No experimental rotational constants available",
    }
    rows = []
    for identity in identity_document["rows"]:
        inscription = values[identity["source_record_role"]]
        rows.append(identity | {
            "source_inscription": inscription,
            "target_payload_hash": sha256_identity((identity["target_id"], identity["source_record_role"], inscription)),
            "status": "reported-authoritative-record" if "status" not in identity["source_record_role"] else "reported-absence-or-limitation",
        })
    target_document = {
        "schema": "sft-v3-coordination-entity-withheld-targets/1",
        "identity_document_sha256": hash_file(IDENTITIES),
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": len(rows),
        "rows": rows,
    }
    TARGETS.write_text(json.dumps(target_document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    primary = {
        "schema": "sft-v3-coordination-entity-primary-records/1",
        "chemistry_obligation": "SFT-CHEM-OBL-INORG-001",
        "claim_id": "SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001",
        "identity_document_sha256": hash_file(IDENTITIES),
        "target_document_sha256": hash_file(TARGETS),
        "complete_registered_target_count": len(rows),
        "source_class_census": {"IUPAC": 3, "NIST-CCCBDB": 17},
        "complete_source_file_count": 5,
        "complete_structural_examples": {
            "iron_pentacarbonyl": {"central_identity": "Fe", "ligand_group_identity": "CO", "retained_central_ligand_links": "5"},
            "ferrocene": {"central_identity": "Fe", "ligand_group_identity": "C5H5", "retained_central_carbon_links": "10"},
        },
        "adverse_and_limitation_surface": {
            "ferrocene_coordinate_data_absent": True,
            "both_rotational_constant_records_absent": True,
            "nist_external_link_disclaimer_retained": "No inferences should be drawn" in fe,
            "iupac_continuously_reviewed_disclaimer_retained": all("continuously reviewing" in term["disclaimer"] for term in terms.values()),
        },
        "no_source_value_used_as_fold_proof_parameter": True,
        "rows": rows,
    }
    PRIMARY.write_text(json.dumps(primary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(rows), "targets_sha256": hash_file(TARGETS), "primary_sha256": hash_file(PRIMARY)}, sort_keys=True))


if __name__ == "__main__":
    main()
