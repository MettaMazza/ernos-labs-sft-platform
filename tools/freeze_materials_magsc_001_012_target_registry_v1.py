#!/usr/bin/env python3
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/materials_magsc_001_012_target_registry_v1.json"
ROWS=(
("001","SFT-MAT-MAGSC-PARAMAGNETIC-RESPONSE-001","paramagnetic moment and susceptibility response",("NIST-MAGNETIC-SUSCEPTIBILITY-SRM","NIST-PARAMAGNETIC-DIAMAGNETIC")),
("002","SFT-MAT-MAGSC-DIAMAGNETIC-RESPONSE-002","diamagnetic susceptibility and opposed orientation response",("NIST-MAGNETIC-SUSCEPTIBILITY-SRM","NIST-PARAMAGNETIC-DIAMAGNETIC")),
("003","SFT-MAT-MAGSC-SPIN-GLASS-FREEZING-003","spin-glass freezing temperature and retained history",("NIST-MAGNETIZATION-LAB",)),
("004","SFT-MAT-MAGSC-DOMAINS-WALLS-004","magnetic domain nucleation, growth, disappearance and wall motion",("NIST-MAGNETIZATION-LAB","NIST-MAGNETIC-IMAGING")),
("005","SFT-MAT-MAGSC-HYSTERESIS-LOOP-005","magnetization reversal and hysteresis-loop ledger",("NIST-MAGNETIC-IMAGING","NIST-HYSTERESIS-STANDARD")),
("006","SFT-MAT-MAGSC-MAGNETOCRYSTALLINE-ANISOTROPY-006","magnetic and magnetocrystalline anisotropy response",("NIST-MAGNETIC-MATERIALS-METROLOGY","NIST-MAGNETIZATION-LAB")),
("007","SFT-MAT-MAGSC-MAGNETORESISTANCE-007","magnetoresistance and field-orientation response",("NIST-SPIN-ORBIT","NIST-MAGNETIC-IMAGING")),
("008","SFT-MAT-MAGSC-SPIN-TRANSPORT-RELAXATION-008","spin transport, state retention and relaxation record",("NIST-SPIN-TRANSPORT","NIST-SPIN-SPECTROSCOPY")),
("009","SFT-MAT-MAGSC-SC-CRITICAL-FIELDS-009","superconducting critical-field and Meissner-state organization",("NIST-SC-CRITICAL-FIELDS",)),
("010","SFT-MAT-MAGSC-SC-VORTEX-PINNING-010","superconducting vortex matter, lattice and pinning record",("NIST-SC-FLUX-LATTICE",)),
("011","SFT-MAT-MAGSC-SC-COHERENCE-LENGTH-011","superconducting coherence-length and penetration-depth boundary",("NIST-SC-CRITICAL-FIELDS",)),
("012","SFT-MAT-MAGSC-SUPERFLUID-CRITICAL-FLOW-012","superfluid persistent-flow and excitation boundary",("NIST-SUPERFLUID-PERSISTENT-FLOW",)),)
def canon(v):return "sha256:"+sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("refusing overwrite")
 p={"schema":"sft-v3-materials-magsc-target-identities/1","authority":"Maria Smith","date":"2026-07-29","family":"magnetism_spin_superconductivity_superfluidity","selection_rule":"All twelve obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.","custody_disclosure":"Source identities and target classes only; no value, fragment, candidate, survivor or outcome.","targets":[{"obligation_id":f"SFT-MAT-OBL-MAGSC-{n}","claim_id":c,"target_class":t,"source_identities":list(s)} for n,c,t,s in ROWS],"target_count":12,"all_family_members_registered":True,"target_content_present":False,"survivor_identity_present":False,"measured_value_present":False,"outcome_present":False,"failed_route_retires_obligation":False};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(p["registry_identity"])
if __name__=="__main__":main()
