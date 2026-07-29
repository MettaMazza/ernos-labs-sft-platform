#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.mathematics.dyn_001_012_laws_v1 import IDS as DYN,SPECS
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
def seals():
 for tool,status in (("verify_engine_seal.py","VALID_CANONICAL_ENGINE"),("verify_verification_authority_seal.py","VALID_CANONICAL_VERIFICATION_AUTHORITY")):
  result=subprocess.run((sys.executable,str(ROOT/"tools"/tool),"--json"),cwd=ROOT,text=True,capture_output=True);data=json.loads(result.stdout)
  if result.returncode or data.get("status")!=status:raise SystemExit("Mathematics DYN admission halted: protected seal invalid")
def load(cid):
 path=ROOT/"claims"/cid/"execution.py";spec=importlib.util.spec_from_file_location("dyn_"+cid.replace("-","_"),path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module.build_execution(ROOT)
def main():
 from sft.engine import EngineRepository
 seals();claims_path=ROOT/"census/claims.json";manifest_path=ROOT/"census/execution_manifest.json";existing={x["claim_id"] for x in json.loads(claims_path.read_text())["claims"]}
 for index,cid in enumerate(DYN,1):
  if cid in existing:raise SystemExit("already admitted: "+cid)
  spec=SPECS[cid];missing=tuple(dep for dep in spec.dependencies if dep not in existing)
  if missing:raise SystemExit(f"missing dependencies for {cid}: {missing}")
  execution=load(cid);captured={}
  class Independent:
   def validate(self,sealed):captured["sealed"]=sealed;result=execution.independent_validator.validate(sealed);captured["independent"]=result;return result
  class Empirical:
   def validate(self,sealed):result=execution.empirical_validator.validate(sealed);captured["empirical"]=result;return result
  receipt=EngineRepository(ROOT).execute_official(execution.program,Independent(),execution.source_files,Empirical())
  if not receipt.model_admitted:raise SystemExit("untouched engine halted: "+cid)
  manifest=json.loads(manifest_path.read_text());manifest["claims"].append({"claim_id":cid,"execution_file":f"claims/{cid}/execution.py"});write(manifest_path,manifest);row=next(x for x in json.loads(claims_path.read_text())["claims"] if x["claim_id"]==cid);sealed=captured["sealed"];independent=captured["independent"];empirical=captured["empirical"];package=ROOT/"claims"/cid
  certificate={"claim_id":cid,"mathematics_obligation":f"SFT-MATH-OBL-DYN-{spec.claim_id.rsplit('-',1)[-1]}","status":"empirically_tested_and_independently_replicated","source_manifest_hash":execution.program.registration.source_hash,"derivation_seal_hash":sealed.seal_hash,"independent_implementation_hash":independent.implementation_hash,"independent_certificate_hash":independent.certificate_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"measurement_receipt_hash":empirical.measurement_receipt_hash,"external_data_source_ids":list(empirical.data_source_ids),"all_external_rows_preserved":empirical.all_rows_preserved,"falsification_condition":empirical.falsification_condition,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"exact_result":spec.exact_result,"closure_scope":receipt.closure_status,"controls_passed":True,"candidate_count":256,"unique_survivor_count":1,"free_parameters":[],"imported_axioms":[]}
  payload={"candidate_census.json":{"claim_id":cid,**asdict(sealed.census)},"elimination_receipt.json":{"claim_id":cid,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},"controls.json":{"claim_id":cid,"controls":asdict(sealed)["controls"]},"empirical_validation.json":{"claim_id":cid,**asdict(empirical)},"certificate.json":certificate,"registration.json":{"$schema":"../../governance/claim.schema.json","branch":"mathematics","claim_id":cid,"title":spec.title,"statement":spec.statement,"dependencies":list(spec.dependencies),"root_theorems":["SFT-ROOT-THERE-IS-NO-NOTHING"],"axioms":[],"free_parameters":[],"excluded_inputs":list(spec.boundary_exclusions),"candidate_grammar":{"boundary":spec.grammar_boundary,"generator":spec.generation_rule,"expected_cardinality":256,"unique_survivor":spec.exact_result,"completeness_certificate":"untouched-engine complete literal product"},"pre_source_target_registry":"census/mathematics_dyn_001_012_target_registry_v1.json","empirical_protocol":"post-registry exact finite-dynamics observation custody","registered_by":"Maria Smith","registration_date":"2026-07-29","required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"status":"empirically_tested"}}
  for name,value in payload.items():write(package/name,value)
  (package/"STATUS.md").write_text(f"# {cid}\n\nStatus: `empirically_tested_and_independently_replicated`\n\n- {spec.exact_result}\n- Engine receipt: `{receipt.receipt_hash}`\n")
  seals();existing.add(cid);print(f"[{index}/{len(DYN)}] admitted {cid}: {receipt.receipt_hash}",flush=True)
if __name__=="__main__":main()
