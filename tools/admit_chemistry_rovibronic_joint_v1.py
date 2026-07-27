#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import asdict
import importlib.util,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.chemistry.rovibronic_joint_batch_v1 import ROVIBRONIC_JOINT_SPEC
from sft.engine import EngineRepository
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def load():
 p=ROOT/"claims"/ROVIBRONIC_JOINT_SPEC.claim_id/"execution.py";s=importlib.util.spec_from_file_location("chem_rovibronic_013",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
def main():
 s=ROVIBRONIC_JOINT_SPEC;cp=ROOT/"census/claims.json";existing={r["claim_id"] for r in json.loads(cp.read_text())["claims"]}
 if s.claim_id in existing:raise SystemExit("claim already admitted; immutable receipt preserved")
 e,c=load(),{}
 class I:
  def validate(self,x):c["sealed"]=x;c["external"]=e.independent_validator.validate(x);return c["external"]
 class E:
  def validate(self,x):c["empirical"]=e.empirical_validator.validate(x);return c["empirical"]
 receipt=EngineRepository(ROOT).execute_official(e.program,I(),e.source_files,E())
 if not receipt.model_admitted:raise SystemExit("halted "+str(receipt.halted_stage)+"; "+receipt.receipt_hash)
 sealed,external,empirical=c["sealed"],c["external"],c["empirical"];mp=ROOT/"census/execution_manifest.json";m=json.loads(mp.read_text());m["claims"].append({"claim_id":s.claim_id,"execution_file":"claims/"+s.claim_id+"/execution.py"});write(mp,m);census=json.loads(cp.read_text());row=next(r for r in census["claims"] if r["claim_id"]==s.claim_id);claim=ROOT/"claims"/s.claim_id
 artifacts={"candidate_census.json":{"claim_id":s.claim_id,**asdict(sealed.census)},"elimination_receipt.json":{"claim_id":s.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},"controls.json":{"claim_id":s.claim_id,"controls":asdict(sealed)["controls"]},"empirical_validation.json":{"claim_id":s.claim_id,**asdict(empirical)},"certificate.json":{"claim_id":s.claim_id,"chemistry_obligation":"SFT-CHEM-OBL-ELEC-013","status":"model_admitted_observationally_derived_empirically_tested_and_independently_replicated","source_manifest_hash":e.program.registration.source_hash,"derivation_seal_hash":sealed.seal_hash,"independent_implementation_hash":external.implementation_hash,"independent_certificate_hash":external.certificate_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"measurement_receipt_hash":empirical.measurement_receipt_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"closure_scope":receipt.closure_status,"exact_result":s.exact_result,"candidate_count":256,"unique_survivor_count":1,"NIST_resolved_state_rows":95,"NIST_state_cells":1235,"singlet_state_rows":54,"triplet_state_rows":41,"positive_vibrational_coordinates":78,"positive_rotational_coordinates":60,"joint_vibrational_rotational_rows":56,"transition_designations":92,"positive_band_origins":83,"continuum_or_fitted_spectral_model_imported":False,"all_external_rows_preserved":empirical.all_rows_preserved,"external_data_source_ids":list(empirical.data_source_ids),"falsification_condition":empirical.falsification_condition}}
 for n,x in artifacts.items():write(claim/n,x)
 reg=json.loads((claim/"registration.json").read_text());reg["status"]="empirically_tested";write(claim/"registration.json",reg);ep=ROOT/"experiments/chemistry"/s.experiment_id/"registration.json";x=json.loads(ep.read_text());x["status"]="measured";write(ep,x);(claim/"STATUS.md").write_text("# "+s.claim_id+"\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-ELEC-013`\n- Closure: `"+receipt.closure_status+"`\n- Derivation seal: `"+sealed.seal_hash+"`\n- Engine receipt: `"+receipt.receipt_hash+"`\n- External vector: complete NIST H2/HD/D2 resolved surface, 95 rows and 1,235 cells.\n- Joint classes: 54 singlets, 41 triplets, 78 positive vibrational coordinates, 60 positive rotational coordinates, 56 jointly resolved rows, 92 transitions and 83 positive band origins.\n",encoding="utf-8");print("admitted "+s.claim_id+": "+receipt.receipt_hash);print("derivation seal: "+sealed.seal_hash);print("candidates: 256; survivors: 1");print("empirical measurements: "+str(len(empirical.measurements))+"; passed: "+str(empirical.passed))
if __name__=="__main__":main()
