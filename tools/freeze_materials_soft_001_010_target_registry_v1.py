#!/usr/bin/env python3
"""Freeze the complete SOFT-001--010 target surface before outcome capture."""
from hashlib import sha256
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_soft_001_010_target_registry_v1.json"
ROWS = (
    ("001", "SFT-MAT-SOFT-COLLOID-AGGREGATION-001", "colloidal stability and aggregation", ("NIST-FLUID-SUSPENSIONS",)),
    ("002", "SFT-MAT-SOFT-GEL-PERCOLATION-002", "gelation and percolated soft network", ("NIST-DYNAMIC-ARREST-GEL",)),
    ("003", "SFT-MAT-SOFT-FOAM-DRAINAGE-003", "foam cell and drainage organization", ("NIST-FOAM-DRAINAGE",)),
    ("004", "SFT-MAT-SOFT-LIQUID-CRYSTAL-ORDER-004", "liquid-crystal orientational order", ("NIST-LIQUID-CRYSTAL",)),
    ("005", "SFT-MAT-SOFT-EMULSION-DROPLET-005", "emulsion and multiphase droplet organization", ("NIST-EMULSION-DROPLETS",)),
    ("006", "SFT-MAT-SOFT-MEMBRANE-THIN-FILM-006", "membrane and thin-film soft matter", ("NIST-FUNCTIONAL-POLYMERS",)),
    ("007", "SFT-MAT-SOFT-GRANULAR-FORCE-CHAIN-007", "granular packing and force-chain support", ("NIST-STRESS-CHAINS",)),
    ("008", "SFT-MAT-SOFT-JAMMING-BOUNDARY-008", "jamming and unjamming boundary", ("NIST-JAMMING",)),
    ("009", "SFT-MAT-SOFT-STIMULI-RESPONSIVE-009", "responsive and stimuli-sensitive soft materials", ("NIST-RESPONSIVE-POLYMER",)),
    ("010", "SFT-MAT-SOFT-ACTIVE-NONEQUILIBRIUM-010", "active-material nonequilibrium organization", ("NIST-SOFT-NONEQUILIBRIUM",)),
)
def canonical(v): return "sha256:" + sha256(json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def main():
    if OUT.exists(): raise SystemExit("refusing overwrite")
    payload={"schema":"sft-v3-materials-soft-target-identities/1","authority":"Maria Smith","date":"2026-07-29","family":"soft_colloidal_liquid_crystalline_granular_active_materials","selection_rule":"All ten obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.","custody_disclosure":"Source identities and target classes only; no value, fragment, candidate, survivor or outcome.","targets":[{"obligation_id":f"SFT-MAT-OBL-SOFT-{n}","claim_id":c,"target_class":t,"source_identities":list(s)} for n,c,t,s in ROWS],"target_count":10,"all_family_members_registered":True,"target_content_present":False,"survivor_identity_present":False,"measured_value_present":False,"outcome_present":False,"failed_route_retires_obligation":False}
    payload["registry_identity"]=canonical(payload); OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n"); print(payload["registry_identity"])
if __name__=="__main__": main()
