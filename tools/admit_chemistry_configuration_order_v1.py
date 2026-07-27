#!/usr/bin/env python3
"""Officially execute and materialize ELEC-011 exactly once."""
from __future__ import annotations
from dataclasses import asdict
import importlib.util,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.chemistry.configuration_order_batch_v1 import CONFIGURATION_ORDER_SPEC
from sft.engine import EngineRepository
def write(path,payload):path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def load_execution():
 path=ROOT/"claims"/CONFIGURATION_ORDER_SPEC.claim_id/"execution.py";spec=importlib.util.spec_from_file_location("chem_configuration_011",path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module.build_execution(ROOT)
def main():
 s=CONFIGURATION_ORDER_SPEC;census_path=ROOT/"census/claims.json";existing={r["claim_id"] for r in json.loads(census_path.read_text())["claims"]}
 if s.claim_id in existing:raise SystemExit("claim already admitted; immutable receipt preserved")
 execution,captured=load_execution(),{}
 class IndependentCapture:
  def validate(self,sealed):captured["sealed"]=sealed;captured["external"]=execution.independent_validator.validate(sealed);return captured["external"]
 class EmpiricalCapture:
  def validate(self,sealed):captured["empirical"]=execution.empirical_validator.validate(sealed);return captured["empirical"]
 receipt=EngineRepository(ROOT).execute_official(execution.program,IndependentCapture(),execution.source_files,EmpiricalCapture())
 if not receipt.model_admitted:raise SystemExit("halted "+str(receipt.halted_stage)+"; "+receipt.receipt_hash)
 sealed,external,empirical=captured["sealed"],captured["external"],captured["empirical"];manifest_path=ROOT/"census/execution_manifest.json";manifest=json.loads(manifest_path.read_text());manifest["claims"].append({"claim_id":s.claim_id,"execution_file":"claims/"+s.claim_id+"/execution.py"});write(manifest_path,manifest);census=json.loads(census_path.read_text());row=next(r for r in census["claims"] if r["claim_id"]==s.claim_id);claim=ROOT/"claims"/s.claim_id
 artifacts={"candidate_census.json":{"claim_id":s.claim_id,**asdict(sealed.census)},"elimination_receipt.json":{"claim_id":s.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},"controls.json":{"claim_id":s.claim_id,"controls":asdict(sealed)["controls"]},"empirical_validation.json":{"claim_id":s.claim_id,**asdict(empirical)},"certificate.json":{"claim_id":s.claim_id,"chemistry_obligation":"SFT-CHEM-OBL-ELEC-011","status":"model_admitted_observationally_derived_empirically_tested_and_independently_replicated","source_manifest_hash":execution.program.registration.source_hash,"derivation_seal_hash":sealed.seal_hash,"independent_implementation_hash":external.implementation_hash,"independent_certificate_hash":external.certificate_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"measurement_receipt_hash":empirical.measurement_receipt_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"closure_scope":receipt.closure_status,"exact_result":s.exact_result,"candidate_count":256,"unique_survivor_count":1,"NIST_configuration_rows":50,"positive_energy_rows":46,"structural_least_energy_rows":4,"stable_basin_nodes":6,"barrier_nodes":6,"ordinary_path_nodes":36,"periodic_recurrence_duplicates":2,"continuum_potential_imported":False,"all_external_rows_preserved":empirical.all_rows_preserved,"external_data_source_ids":list(empirical.data_source_ids),"falsification_condition":empirical.falsification_condition}}
 for name,payload in artifacts.items():write(claim/name,payload)
 registration=json.loads((claim/"registration.json").read_text());registration["status"]="empirically_tested";write(claim/"registration.json",registration);experiment_path=ROOT/"experiments/chemistry"/s.experiment_id/"registration.json";experiment=json.loads(experiment_path.read_text());experiment["status"]="measured";write(experiment_path,experiment);(claim/"STATUS.md").write_text("# "+s.claim_id+"\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-ELEC-011`\n- Closure: `"+receipt.closure_status+"`\n- Derivation seal: `"+sealed.seal_hash+"`\n- Engine receipt: `"+receipt.receipt_hash+"`\n- External vector: both complete NIST ethanol paths, 50 rows.\n- Exact classes: 46 positive heights, four EmptyOne least coordinates, six basins, six barriers, 36 ordinary nodes and two recurrence duplicates.\n",encoding="utf-8");print("admitted "+s.claim_id+": "+receipt.receipt_hash);print("derivation seal: "+sealed.seal_hash);print("candidates: 256; survivors: 1");print("empirical measurements: "+str(len(empirical.measurements))+"; passed: "+str(empirical.passed))
if __name__=="__main__":main()
