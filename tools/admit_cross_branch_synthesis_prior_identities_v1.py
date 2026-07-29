#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
ORDER=("SFT-SYNTH-PRIME-VACUUM-ORBIT-IDENTITY-001","SFT-SYNTH-COMMON-LOCK-IDENTITY-001","SFT-SYNTH-COMMON-DESCENT-IDENTITY-001","SFT-SYNTH-WAVE-MODE-RECURRENCE-IDENTITY-001","SFT-SYNTH-FOLD-SECOND-HARMONIC-IDENTITY-001","SFT-SYNTH-VACUUM-PERIOD-DIVISOR-PREDICTION-001","SFT-SYNTH-POSITIVE-OBSERVABLE-ABSENCE-BOUNDARY-001","SFT-SYNTH-TESLA-CORRESPONDENCE-ASSEMBLY-001","SFT-SYNTH-UNIFIED-CONSTANTS-ASSEMBLY-001","SFT-SYNTH-PREDICTION-FALSIFICATION-LEDGER-001","SFT-SYNTH-ONE-OWNER-NO-OMISSION-LEDGER-001","SFT-SYNTH-ROOT-TRACED-TERMINAL-ASSEMBLY-001")
def w(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def seals():
 for t,s in (("verify_engine_seal.py","VALID_CANONICAL_ENGINE"),("verify_verification_authority_seal.py","VALID_CANONICAL_VERIFICATION_AUTHORITY")):
  r=subprocess.run((sys.executable,str(ROOT/"tools"/t),"--json"),cwd=ROOT,text=True,capture_output=True);d=json.loads(r.stdout)
  if r.returncode or d.get("status")!=s:raise SystemExit("Synthesis admission halted: protected seal invalid")
def load(c):
 p=ROOT/"claims"/c/"execution.py";s=importlib.util.spec_from_file_location("synthesis_"+c.replace("-","_"),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
def main():
 from sft.engine import EngineRepository
 from sft.synthesis.prior_identity_laws_v1 import SPECS
 seals();cp=ROOT/"census/claims.json";mp=ROOT/"census/execution_manifest.json";existing={x["claim_id"] for x in json.loads(cp.read_text())["claims"]}
 for i,c in enumerate(ORDER,1):
  if c in existing:raise SystemExit("already admitted: "+c)
  spec=SPECS[c];missing=tuple(x for x in spec.dependencies if x not in existing)
  if missing:raise SystemExit(f"missing dependencies for {c}: {missing}")
  run=load(c);cap={}
  class I:
   def validate(self,s):cap["s"]=s;z=run.independent_validator.validate(s);cap["i"]=z;return z
  receipt=EngineRepository(ROOT).execute_official(run.program,I(),run.source_files)
  if not receipt.model_admitted:raise SystemExit("untouched engine halted: "+c)
  md=json.loads(mp.read_text());md["claims"].append({"claim_id":c,"execution_file":f"claims/{c}/execution.py"});w(mp,md);row=next(x for x in json.loads(cp.read_text())["claims"] if x["claim_id"]==c);s,ind,pkg=cap["s"],cap["i"],ROOT/"claims"/c
  cert={"claim_id":c,"status":"independently_replicated","source_manifest_hash":run.program.registration.source_hash,"derivation_seal_hash":s.seal_hash,"independent_implementation_hash":ind.implementation_hash,"independent_certificate_hash":ind.certificate_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"exact_result":spec.exact_result,"closure_scope":receipt.closure_status,"controls_passed":True,"synthesis_owns_primitive_law":False,"free_parameters":[],"imported_axioms":[]}
  payload={"candidate_census.json":{"claim_id":c,**asdict(s.census)},"elimination_receipt.json":{"claim_id":c,"decisions":asdict(s)["decisions"],"closure":asdict(s.closure)},"controls.json":{"claim_id":c,"controls":asdict(s)["controls"]},"certificate.json":cert,"registration.json":{"$schema":"../../governance/claim.schema.json","branch":"cross_branch_synthesis","claim_id":c,"title":spec.title,"statement":spec.exact_result,"dependencies":list(spec.dependencies),"excluded_inputs":list(spec.exclusions),"candidate_grammar":{"boundary":spec.grammar_boundary,"generator":spec.generation_rule,"completeness_certificate":"untouched-engine complete literal product"},"registered_by":"Maria Smith","registration_date":"2026-07-29","required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"status":"independently_replicated"}}
  for n,v in payload.items():w(pkg/n,v)
  (pkg/"STATUS.md").write_text(f"# {c}\n\nStatus: `independently_replicated`\n\n- {spec.exact_result}\n- Synthesis primitive law: `none`\n- Engine receipt: `{receipt.receipt_hash}`\n")
  seals();existing.add(c);print(f"[{i}/{len(ORDER)}] admitted {c}: {receipt.receipt_hash}",flush=True)
if __name__=="__main__":main()
