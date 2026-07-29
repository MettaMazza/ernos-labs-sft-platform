#!/usr/bin/env python3
"""Freeze value-free authoritative targets for the complete ELEC family."""
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/materials_elec_001_012_target_registry_v1.json"
ROWS=(
("001","SFT-MAT-ELEC-CONDUCTIVITY-RESISTIVITY-001","conductivity and reciprocal resistivity record",("NIST-HALL-EFFECT",)),
("002","SFT-MAT-ELEC-MOBILITY-CONCENTRATION-002","carrier mobility and concentration separation record",("NIST-HALL-EFFECT",)),
("003","SFT-MAT-ELEC-HALL-RESPONSE-003","Hall voltage, carrier type, density and mobility record",("NIST-RESISTIVITY-HALL",)),
("004","SFT-MAT-ELEC-DIELECTRIC-LOSS-004","relative permittivity, loss and uncertainty record",("NIST-DIELECTRIC-PERMITTIVITY-LOSS",)),
("005","SFT-MAT-ELEC-IONIC-TRANSFERENCE-005","ionic conductivity, mobile species and transference record",("NIST-IONIC-CONDUCTIVITY",)),
("006","SFT-MAT-ELEC-MIXED-TRANSPORT-006","simultaneous ionic and electronic transport record",("NIST-MIXED-IONIC-ELECTRONIC",)),
("007","SFT-MAT-ELEC-FINITE-BARRIER-TUNNELLING-007","finite barrier and tunnelling-response record",("NIST-TUNNEL-BAND-OFFSET",)),
("008","SFT-MAT-ELEC-BAND-ALIGNMENT-008","heterojunction band alignment and offset record",("NIST-TUNNEL-BAND-OFFSET","NIST-OPTOELECTRONIC-BAND-METROLOGY")),
("009","SFT-MAT-ELEC-CARRIER-CONFINEMENT-009","heterostructure carrier confinement and interface record",("NIST-TUNNEL-BAND-OFFSET","NIST-OPTOELECTRONIC-BAND-METROLOGY")),
("010","SFT-MAT-ELEC-DEFECT-TRAP-STATES-010","defect, trap, valence and carrier-interaction record",("NIST-POINT-DEFECT-CHEMISTRY",)),
("011","SFT-MAT-ELEC-SCREENING-DEPLETION-011","accumulation, depletion, inversion and trapped-charge record",("NIST-DIELECTRIC-DEPLETION",)),
("012","SFT-MAT-ELEC-ELECTROCHEMICAL-INSERTION-012","operando charge-transfer, insertion and material-state record",("NIST-OPERANDO-ELECTROCHEMICAL",)),)
def canonical(v):return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("refusing to overwrite frozen ELEC registry")
 p={"schema":"sft-v3-materials-elec-target-identities/1","authority":"Maria Smith","date":"2026-07-29","family":"electronic_dielectric_semiconductor_ionic_transport","selection_rule":"All twelve obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.","custody_disclosure":"Source identities and comparison classes only; no measured value, fragment, candidate, survivor or outcome is present.","targets":[{"obligation_id":f"SFT-MAT-OBL-ELEC-{n}","claim_id":c,"target_class":t,"source_identities":list(s)} for n,c,t,s in ROWS],"target_count":12,"all_family_members_registered":True,"target_content_present":False,"survivor_identity_present":False,"measured_value_present":False,"outcome_present":False,"failed_route_retires_obligation":False};p["registry_identity"]=canonical(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"target_count":12,"registry_identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
