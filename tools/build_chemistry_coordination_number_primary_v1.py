#!/usr/bin/env python3
"""Open and preserve the complete INORG-002 coordination-count vector post seal."""
from __future__ import annotations
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402

SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-002-coordination-number-v1"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/coordination_number_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/coordination_number_withheld_targets_v1.json"
PRIMARY = SNAPSHOT / "coordination-number-primary-records-v1.json"

class Surface(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]
    def handle_starttag(self, tag, attrs):
        if tag == "sub": self.parts.append("_")
    def handle_data(self, data):
        value=" ".join(unescape(data).split())
        if value: self.parts.append(value)
    @property
    def text(self): return " ".join(self.parts)

def text(name):
    parser=Surface(); parser.feed((SNAPSHOT/name).read_text(errors="replace")); return parser.text

def main() -> None:
    identities=json.loads(IDENTITIES.read_text())
    if identities.get("target_values_or_hashes_present") is not False: raise ValueError("INORG-002 identity seal contains targets")
    term=json.loads((SNAPSHOT/"iupac-coordination-number.json").read_text())["term"]
    general=term["definitions"][0]["text"]; inorganic=term["definitions"][1]["text"]
    sc=text("nist-cccbdb-scandium-trifluoride-experimental-geometry.html")
    ti=text("nist-cccbdb-titanium-tetrachloride-experimental-geometry.html")
    fe=text("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html")
    requirements={"ScF3":(sc,("ScF _ 3 (Scandium trifluoride)","Point Group D _ 3h","F-Sc 3","No coordinate data available.","No experimental rotational constants available.")),"TiCl4":(ti,("TiCl _ 4 (Titanium tetrachloride)","Point Group T _ d","Ti-Cl 4","No experimental rotational constants available.")),"FeCO5":(fe,("Fe(CO) _ 5 (Iron pentacarbonyl)","Point Group D _ 3h","C-Fe 5","No experimental rotational constants available."))}
    missing={name:[value for value in required if value not in surface] for name,(surface,required) in requirements.items()}
    if any(missing.values()): raise ValueError(f"INORG-002 NIST structure surface changed: {missing}")
    values={
        "complete-current-term-record": hash_file(SNAPSHOT/"iupac-coordination-number.json"),
        "general-direct-link-definition": general,
        "inorganic-sigma-link-definition": inorganic,
        "crystallographic-sense-boundary": "term is used in a different sense in the crystallographic description of ionic crystals",
        "pi-link-exclusion-boundary": "pi-bonds are not considered in determining the coordination number",
        "ScF3-complete-page": hash_file(SNAPSHOT/"nist-cccbdb-scandium-trifluoride-experimental-geometry.html"),
        "ScF3-entity-identity": "ScF3; Scandium trifluoride", "ScF3-point-group": "D3h", "ScF3-direct-link-count": "3", "ScF3-coordinate-data-status": "No coordinate data available", "ScF3-rotational-data-status": "No experimental rotational constants available",
        "TiCl4-complete-page": hash_file(SNAPSHOT/"nist-cccbdb-titanium-tetrachloride-experimental-geometry.html"),
        "TiCl4-entity-identity": "TiCl4; Titanium tetrachloride", "TiCl4-point-group": "Td", "TiCl4-direct-link-count": "4", "TiCl4-internal-coordinate-record": "rTiCl experimental internal-coordinate record retained", "TiCl4-rotational-data-status": "No experimental rotational constants available",
        "FeCO5-complete-page": hash_file(SNAPSHOT/"nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html"),
        "FeCO5-entity-identity": "Fe(CO)5; Iron pentacarbonyl", "FeCO5-point-group": "D3h", "FeCO5-direct-link-count": "5", "FeCO5-internal-coordinate-record": "rCO=1.145 angstrom; C-Fe direct-link support retained", "FeCO5-rotational-data-status": "No experimental rotational constants available",
    }
    rows=[]
    for identity in identities["rows"]:
        inscription=values[identity["source_record_role"]]
        rows.append(identity|{"source_inscription":inscription,"target_payload_hash":sha256_identity((identity["target_id"],identity["source_record_role"],inscription)),"status":"reported-boundary-or-limitation" if "boundary" in identity["source_record_role"] or "status" in identity["source_record_role"] else "reported-authoritative-record"})
    target={"schema":"sft-v3-coordination-number-withheld-targets/1","identity_document_sha256":hash_file(IDENTITIES),"release_requires_prediction_seal":True,"complete_registered_target_count":len(rows),"rows":rows}
    TARGETS.write_text(json.dumps(target,indent=2,sort_keys=True)+"\n")
    primary={"schema":"sft-v3-coordination-number-primary-records/1","chemistry_obligation":"SFT-CHEM-OBL-INORG-002","claim_id":"SFT-CHEM-COORDINATION-NUMBER-INCIDENCE-COUNT-002","identity_document_sha256":hash_file(IDENTITIES),"target_document_sha256":hash_file(TARGETS),"complete_registered_target_count":len(rows),"source_class_census":{"IUPAC":5,"NIST-CCCBDB":18},"complete_source_file_count":4,"exact_direct_link_vector":{"ScF3":"3","TiCl4":"4","FeCO5":"5"},"adverse_and_boundary_surface":{"scandium_coordinate_data_absent":True,"all_three_rotational_constant_records_absent":True,"crystallographic_alternate_sense_retained":True,"pi_link_exclusion_retained":True,"nist_applicable_external_link_disclaimers_retained":all("No inferences should be drawn" in surface for surface in (ti,fe)) and "References" not in sc,"iupac_continuing_review_disclaimer_retained":"continuously reviewing" in term["disclaimer"]},"no_source_count_used_as_fold_proof_parameter":True,"rows":rows}
    PRIMARY.write_text(json.dumps(primary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"targets":len(rows),"targets_sha256":hash_file(TARGETS),"primary_sha256":hash_file(PRIMARY)},sort_keys=True))

if __name__ == "__main__": main()
