#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"census/materials_surf_001_008_target_registry_v1.json"
ROWS=(("001","SFT-MAT-SURF-FREE-STATE-ENERGY-001","surface free-state and energy relation",("NIST-POLYMER-SURFACE-INTERFACE",)),("002","SFT-MAT-SURF-WETTING-CONTACT-ANGLE-002","wetting and contact-angle custody",("NIST-WETTING-WRINKLED-SURFACES",)),("003","SFT-MAT-SURF-ADHESION-SEPARATION-003","adhesion and work-of-separation ledger",("NIST-ADHESION-ENERGY-DISSIPATION",)),("004","SFT-MAT-SURF-COATING-SUBSTRATE-004","coating layer and substrate organization",("NIST-COATING-MICROSTRUCTURE",)),("005","SFT-MAT-SURF-ROUGHNESS-SCALE-005","surface roughness and scale boundary",("NIST-COATING-SURFACE-ROUGHNESS",)),("006","SFT-MAT-SURF-REACTION-CATALYSIS-HANDOFF-006","surface reaction and catalysis handoff",("NIST-POLYMER-SURFACE-CHEMISTRY",)),("007","SFT-MAT-SURF-TRIBOFILM-RETENTION-007","tribofilm formation and retention",("NIST-TRIBOLOGICAL-COATINGS",)),("008","SFT-MAT-SURF-DELAMINATION-008","interface fracture and delamination",("NIST-EDGE-DELAMINATION",)))
def canonical(value): return "sha256:"+sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists(): raise SystemExit("refusing overwrite")
 value={"schema":"sft-v3-materials-surf-target-identities/1","authority":"Maria Smith","date":"2026-07-29","family":"surfaces_coatings_adhesion_interfacial_response","selection_rule":"All eight obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.","custody_disclosure":"Source identities and target classes only; no value, fragment, candidate, survivor or outcome.","targets":[{"obligation_id":f"SFT-MAT-OBL-SURF-{number}","claim_id":claim_id,"target_class":target,"source_identities":list(sources)} for number,claim_id,target,sources in ROWS],"target_count":8,"all_family_members_registered":True,"target_content_present":False,"survivor_identity_present":False,"measured_value_present":False,"outcome_present":False,"failed_route_retires_obligation":False}; value["registry_identity"]=canonical(value); OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n"); print(value["registry_identity"])
if __name__=="__main__": main()

