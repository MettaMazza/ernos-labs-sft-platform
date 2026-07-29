#!/usr/bin/env python3
"""Freeze value-free authoritative targets for the complete MECH family."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"census/materials_mech_001_014_target_registry_v1.json"
ROWS=(
("001","SFT-MAT-MECH-TENSOR-STRESS-STRAIN-001","tensor-resolved stress and strain measurement",("NIST-MARTENSITIC-MATERIALS-STUDY",)),
("002","SFT-MAT-MECH-TRANSVERSE-STRAIN-002","transverse and longitudinal strain measurement",("NIST-MARTENSITIC-MATERIALS-STUDY",)),
("003","SFT-MAT-MECH-VISCOELASTIC-MEMORY-003","viscoelastic stress-relaxation and recovery record",("NIST-VISCOELASTIC-SEALANT",)),
("004","SFT-MAT-MECH-VISCOPLASTIC-FLOW-004","rate-dependent permanent-deformation record",("NIST-RHEOLOGY",)),
("005","SFT-MAT-MECH-YIELD-PATH-005","yield-stress and loading-path record",("NIST-RHEOLOGY",)),
("006","SFT-MAT-MECH-WORK-HARDENING-006","work-hardening and retained-strain-history record",("NIST-MARTENSITIC-MATERIALS-STUDY",)),
("007","SFT-MAT-MECH-FRACTURE-ENERGY-007","fracture toughness and energy record",("NIST-FAILURE-PROPERTY-TESTS",)),
("008","SFT-MAT-MECH-CRACK-GROWTH-008","stable and unstable crack-growth record",("NIST-FAILURE-PROPERTY-TESTS","NIST-FATIGUE-FRACTURE")),
("009","SFT-MAT-MECH-FATIGUE-009","cyclic fatigue initiation and propagation record",("NIST-FAILURE-PROPERTY-TESTS","NIST-FATIGUE-FRACTURE")),
("010","SFT-MAT-MECH-CREEP-RUPTURE-010","creep mechanism, crack growth and rupture-time record",("NIST-FAILURE-PROPERTY-TESTS",)),
("011","SFT-MAT-MECH-IMPACT-011","absorbed impact energy and high-rate response record",("NIST-FAILURE-PROPERTY-TESTS",)),
("012","SFT-MAT-MECH-FRICTION-CONTACT-012","friction, wear and contact-state record",("NIST-NANOTRIBOLOGY","NIST-LUBRICATION-HANDBOOK")),
("013","SFT-MAT-MECH-LUBRICATION-TRIBOFILM-013","lubricant-film and tribochemical retention record",("NIST-LUBRICANT-FILM","NIST-LUBRICATION-HANDBOOK")),
("014","SFT-MAT-MECH-RHEOLOGY-014","viscosity, yield stress, flow and relaxation-class record",("NIST-RHEOLOGY","NIST-VISCOELASTIC-SEALANT")),
)
def canonical(v): return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists(): raise SystemExit("refusing to overwrite frozen MECH registry")
 p={"schema":"sft-v3-materials-mech-target-identities/1","authority":"Maria Smith","date":"2026-07-29","family":"mechanical_fracture_fatigue_creep_tribology_rheology","selection_rule":"All fourteen obligations and source identities are frozen before source capture and outcome extraction.","custody_disclosure":"Only source identities and target classes are registered; no value, detailed fragment, survivor or outcome is present.","targets":[{"obligation_id":f"SFT-MAT-OBL-MECH-{n}","claim_id":c,"target_class":t,"source_identities":list(s)} for n,c,t,s in ROWS],"target_count":14,"all_family_members_registered":True,"target_content_present":False,"survivor_identity_present":False,"measured_value_present":False,"outcome_present":False,"failed_route_retires_obligation":False};p["registry_identity"]=canonical(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"target_count":14,"registry_identity":p["registry_identity"]},indent=2))
if __name__=="__main__": main()
