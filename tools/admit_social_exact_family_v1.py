#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
FORMAL=("SFT-SOCIAL-PREFERENTIAL-FLOW-INEQUALITY-002","SFT-SOCIAL-CONSENSUS-POLARIZATION-LOCK-002","SFT-SOCIAL-DISSIPATIVE-PERIOD-TWO-CYCLE-002");EMP="SFT-SOCIAL-VALIDATION-EXACT-COMPLETE-FAMILY-002"
def w(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def seals():
 for t,s in (("verify_engine_seal.py","VALID_CANONICAL_ENGINE"),("verify_verification_authority_seal.py","VALID_CANONICAL_VERIFICATION_AUTHORITY")):
  r=subprocess.run((sys.executable,str(ROOT/"tools"/t),"--json"),cwd=ROOT,text=True,capture_output=True);d=json.loads(r.stdout)
  if r.returncode or d.get("status")!=s:raise SystemExit("Social admission halted")
def load(c):
 p=ROOT/"claims"/c/"execution.py";s=importlib.util.spec_from_file_location("social_"+c.replace("-","_"),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
def admit(order):
 from sft.engine import EngineRepository
 from sft.social.exact_return_laws_v1 import SPECS
 existing={x["claim_id"] for x in json.loads((ROOT/"census/claims.json").read_text())["claims"]}
 for i,c in enumerate(order,1):
  if c in existing:raise SystemExit("already admitted "+c)
  spec=SPECS[c];missing=tuple(x for x in spec.dependencies if x not in existing)
  if missing:raise SystemExit(f"missing {missing}")
  run=load(c);cap={}
  class I:
   def validate(self,s):cap["s"]=s;z=run.independent_validator.validate(s);cap["i"]=z;return z
  class E:
   def validate(self,s):z=run.empirical_validator.validate(s);cap["e"]=z;return z
  receipt=EngineRepository(ROOT).execute_official(run.program,I(),run.source_files,E() if run.empirical_validator else None)
  if not receipt.model_admitted:raise SystemExit("halted "+c)
  mp=ROOT/"census/execution_manifest.json";md=json.loads(mp.read_text());md["claims"].append({"claim_id":c,"execution_file":f"claims/{c}/execution.py"});w(mp,md);row=next(x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"] if x["claim_id"]==c);s,ind,e=cap["s"],cap["i"],cap.get("e");pkg=ROOT/"claims"/c;cert={"claim_id":c,"status":"authoritatively_corresponded_and_independently_replicated" if e else "independently_replicated","source_manifest_hash":run.program.registration.source_hash,"derivation_seal_hash":s.seal_hash,"independent_implementation_hash":ind.implementation_hash,"independent_certificate_hash":ind.certificate_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"exact_result":spec.exact_result,"closure_scope":receipt.closure_status,"controls_passed":True,"free_parameters":[],"imported_axioms":[]};payload={"candidate_census.json":{"claim_id":c,**asdict(s.census)},"elimination_receipt.json":{"claim_id":c,"decisions":asdict(s)["decisions"],"closure":asdict(s.closure)},"controls.json":{"claim_id":c,"controls":asdict(s)["controls"]},"certificate.json":cert,"registration.json":{"$schema":"../../governance/claim.schema.json","branch":"social_collective","claim_id":c,"title":spec.title,"statement":spec.exact_result,"dependencies":list(spec.dependencies),"excluded_inputs":list(spec.exclusions),"candidate_grammar":{"boundary":spec.grammar_boundary,"generator":spec.generation_rule,"completeness_certificate":"untouched-engine complete literal product"},"registered_by":"Maria Smith","registration_date":"2026-07-28","required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"status":"empirically_tested" if e else "independently_replicated"}}
  if e:payload["empirical_validation.json"]={"claim_id":c,**asdict(e)};cert.update({"measurement_receipt_hash":e.measurement_receipt_hash,"all_external_rows_preserved":e.all_rows_preserved,"external_data_source_ids":list(e.data_source_ids),"falsification_condition":e.falsification_condition})
  for n,v in payload.items():w(pkg/n,v)
  (pkg/"STATUS.md").write_text(f"# {c}\n\nStatus: `{cert['status']}`\n\n- {spec.exact_result}\n- Engine receipt: `{receipt.receipt_hash}`\n");seals();existing.add(c);print(f"[{i}/{len(order)}] admitted {c}: {receipt.receipt_hash}",flush=True)
def main():seals();admit(FORMAL if "--formal-only" in sys.argv else (EMP,) if "--empirical-only" in sys.argv else FORMAL+(EMP,))
if __name__=="__main__":main()
