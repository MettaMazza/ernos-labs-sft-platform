#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
ORDER=("SFT-CHEM-VALIDATION-MOLECULAR-GEOMETRY-VECTOR-001","SFT-CHEM-VALIDATION-THERMOCHEMICAL-VECTOR-002","SFT-CHEM-VALIDATION-EQUILIBRIUM-VECTOR-003","SFT-CHEM-VALIDATION-KINETIC-VECTOR-004","SFT-CHEM-VALIDATION-SPECTROSCOPY-VECTOR-005","SFT-CHEM-VALIDATION-ELECTROCHEMICAL-VECTOR-006","SFT-CHEM-VALIDATION-INORGANIC-COORDINATION-VECTOR-007","SFT-CHEM-VALIDATION-ORGANIC-REACTION-VECTOR-008","SFT-CHEM-VALIDATION-POLYMER-VECTOR-009","SFT-CHEM-VALIDATION-CROSS-SOURCE-REPRODUCIBILITY-VECTOR-010","SFT-CHEM-VALIDATION-ADVERSE-OUT-OF-BOUND-VECTOR-011","SFT-CHEM-VALIDATION-EMPIRICAL-GRAND-LOCK-012")
def w(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def seals():
 for t,s in (("verify_engine_seal.py","VALID_CANONICAL_ENGINE"),("verify_verification_authority_seal.py","VALID_CANONICAL_VERIFICATION_AUTHORITY")):
  r=subprocess.run((sys.executable,str(ROOT/"tools"/t),"--json"),cwd=ROOT,text=True,capture_output=True);d=json.loads(r.stdout)
  if r.returncode or d.get("status")!=s:raise SystemExit("Chemistry VALID admission halted: protected seal invalid")
def load(c):
 p=ROOT/"claims"/c/"execution.py";s=importlib.util.spec_from_file_location("valid_"+c.replace("-","_"),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
def main():
 from sft.engine import EngineRepository
 from sft.chemistry.valid_001_012_laws_v2 import SPECS
 seals();cp=ROOT/"census/claims.json";mp=ROOT/"census/execution_manifest.json";existing={x["claim_id"] for x in json.loads(cp.read_text())["claims"]}
 for i,c in enumerate(ORDER,1):
  if c in existing:raise SystemExit("already admitted: "+c)
  spec=SPECS[c];missing=tuple(x for x in spec.dependencies if x not in existing)
  if missing:raise SystemExit(f"missing dependencies for {c}: {missing}")
  run=load(c);cap={}
  class I:
   def validate(self,s):cap["s"]=s;z=run.independent_validator.validate(s);cap["i"]=z;return z
  class E:
   def validate(self,s):z=run.empirical_validator.validate(s);cap["e"]=z;return z
  receipt=EngineRepository(ROOT).execute_official(run.program,I(),run.source_files,E())
  if not receipt.model_admitted:raise SystemExit("untouched engine halted: "+c)
  md=json.loads(mp.read_text());md["claims"].append({"claim_id":c,"execution_file":f"claims/{c}/execution.py"});w(mp,md);row=next(x for x in json.loads(cp.read_text())["claims"] if x["claim_id"]==c);s,ind,e,pkg=cap["s"],cap["i"],cap["e"],ROOT/"claims"/c
  cert={"claim_id":c,"chemistry_obligation":f"SFT-CHEM-OBL-VALID-{spec.number}","status":"empirically_tested_and_independently_replicated","source_manifest_hash":run.program.registration.source_hash,"derivation_seal_hash":s.seal_hash,"independent_implementation_hash":ind.implementation_hash,"independent_certificate_hash":ind.certificate_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"measurement_receipt_hash":e.measurement_receipt_hash,"external_data_source_ids":list(e.data_source_ids),"all_external_rows_preserved":e.all_rows_preserved,"falsification_condition":e.falsification_condition,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"exact_result":spec.exact_result,"closure_scope":receipt.closure_status,"controls_passed":True,"base_claim_count":263,"vector_member_count":len(spec.vector_claim_ids),"free_parameters":[],"imported_axioms":[]}
  payload={"candidate_census.json":{"claim_id":c,**asdict(s.census)},"elimination_receipt.json":{"claim_id":c,"decisions":asdict(s)["decisions"],"closure":asdict(s.closure)},"controls.json":{"claim_id":c,"controls":asdict(s)["controls"]},"empirical_validation.json":{"claim_id":c,**asdict(e)},"certificate.json":cert,"registration.json":{"$schema":"../../governance/claim.schema.json","branch":"chemistry","claim_id":c,"title":spec.title,"statement":spec.exact_result,"dependencies":list(spec.dependencies),"excluded_inputs":list(spec.exclusions),"candidate_grammar":{"boundary":spec.grammar_boundary,"generator":spec.generation_rule,"completeness_certificate":"untouched-engine complete literal product"},"registered_by":"Maria Smith","registration_date":"2026-07-29","required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"status":"empirically_tested"}}
  for n,v in payload.items():w(pkg/n,v)
  (pkg/"STATUS.md").write_text(f"# {c}\n\nStatus: `empirically_tested_and_independently_replicated`\n\n- {spec.exact_result}\n- Vector members: `{len(spec.vector_claim_ids)}`\n- Engine receipt: `{receipt.receipt_hash}`\n")
  seals();existing.add(c);print(f"[{i}/{len(ORDER)}] admitted {c}: {receipt.receipt_hash}",flush=True)
if __name__=="__main__":main()
