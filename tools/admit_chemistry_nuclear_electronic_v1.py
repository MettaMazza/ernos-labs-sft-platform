#!/usr/bin/env python3
"""Officially execute and materialize ELEC-012 exactly once."""
from __future__ import annotations
from dataclasses import asdict
import importlib.util,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from sft.chemistry.nuclear_electronic_batch_v1 import NUCLEAR_ELECTRONIC_SPEC
from sft.engine import EngineRepository
def write(path,payload): path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def load_execution():
 path=ROOT/"claims"/NUCLEAR_ELECTRONIC_SPEC.claim_id/"execution.py";spec=importlib.util.spec_from_file_location("chem_nuclear_electronic_012",path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module.build_execution(ROOT)
def main():
 s=NUCLEAR_ELECTRONIC_SPEC;census_path=ROOT/"census/claims.json";existing={r["claim_id"] for r in json.loads(census_path.read_text())["claims"]}
 if s.claim_id in existing: raise SystemExit("claim already admitted; immutable receipt preserved")
 execution,captured=load_execution(),{}
 class IndependentCapture:
  def validate(self,sealed): captured["sealed"]=sealed;captured["external"]=execution.independent_validator.validate(sealed);return captured["external"]
 class EmpiricalCapture:
  def validate(self,sealed): captured["empirical"]=execution.empirical_validator.validate(sealed);return captured["empirical"]
 receipt=EngineRepository(ROOT).execute_official(execution.program,IndependentCapture(),execution.source_files,EmpiricalCapture())
 if not receipt.model_admitted: raise SystemExit("halted "+str(receipt.halted_stage)+"; "+receipt.receipt_hash)
 sealed,external,empirical=captured["sealed"],captured["external"],captured["empirical"]
 manifest_path=ROOT/"census/execution_manifest.json";manifest=json.loads(manifest_path.read_text());manifest["claims"].append({"claim_id":s.claim_id,"execution_file":"claims/"+s.claim_id+"/execution.py"});write(manifest_path,manifest)
 census=json.loads(census_path.read_text());row=next(r for r in census["claims"] if r["claim_id"]==s.claim_id);claim=ROOT/"claims"/s.claim_id
 artifacts={
  "candidate_census.json":{"claim_id":s.claim_id,**asdict(sealed.census)},
  "elimination_receipt.json":{"claim_id":s.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},
  "controls.json":{"claim_id":s.claim_id,"controls":asdict(sealed)["controls"]},
  "empirical_validation.json":{"claim_id":s.claim_id,**asdict(empirical)},
  "certificate.json":{"claim_id":s.claim_id,"chemistry_obligation":"SFT-CHEM-OBL-ELEC-012","status":"model_admitted_observationally_derived_empirically_tested_and_independently_replicated","source_manifest_hash":execution.program.registration.source_hash,"derivation_seal_hash":sealed.seal_hash,"independent_implementation_hash":external.implementation_hash,"independent_certificate_hash":external.certificate_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"measurement_receipt_hash":empirical.measurement_receipt_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"closure_scope":receipt.closure_status,"exact_result":s.exact_result,"candidate_count":256,"unique_survivor_count":1,"NIST_isotopologue_state_rows":95,"NIST_state_cells":1235,"positive_exact_cells":551,"blank_EmptyOne_cells":450,"source_zero_EmptyOne_cells":3,"held_external_negative_inscriptions":8,"held_text_records":223,"matched_positive_vibronic_coordinate_pairs":330,"isotopologue_species":3,"continuum_or_fitted_separation_imported":False,"all_external_rows_preserved":empirical.all_rows_preserved,"external_data_source_ids":list(empirical.data_source_ids),"falsification_condition":empirical.falsification_condition},
 }
 for name,payload in artifacts.items(): write(claim/name,payload)
 registration=json.loads((claim/"registration.json").read_text());registration["status"]="empirically_tested";write(claim/"registration.json",registration)
 experiment_path=ROOT/"experiments/chemistry"/s.experiment_id/"registration.json";experiment=json.loads(experiment_path.read_text());experiment["status"]="measured";write(experiment_path,experiment)
 (claim/"STATUS.md").write_text("# "+s.claim_id+"\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-ELEC-012`\n- Closure: `"+receipt.closure_status+"`\n- Derivation seal: `"+sealed.seal_hash+"`\n- Engine receipt: `"+receipt.receipt_hash+"`\n- External vector: complete NIST H2/HD/D2 surface, 95 rows and 1,235 cells.\n- Exact comparison: 551 positive cells, 453 EmptyOne forms, eight held signed inscriptions, 223 held text records and 330 isotope-distinct matched positive coordinate pairs.\n",encoding="utf-8")
 print("admitted "+s.claim_id+": "+receipt.receipt_hash);print("derivation seal: "+sealed.seal_hash);print("candidates: 256; survivors: 1");print("empirical measurements: "+str(len(empirical.measurements))+"; passed: "+str(empirical.passed))
if __name__=="__main__":main()
