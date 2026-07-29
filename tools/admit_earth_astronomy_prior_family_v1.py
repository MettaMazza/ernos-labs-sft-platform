#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
FORMAL=("SFT-EARTH-TIPPING-FOLD-LOCK-002","SFT-ASTRO-SOLAR-RADIO-UNIT-RELEASE-002","SFT-ASTRO-ATOMIC-BURST-COMPLETION-002","SFT-ASTRO-PLANETARY-BINARY-LADDER-002","SFT-ASTRO-LITHIUM-SEVEN-ONE-FOLD-DEPLETION-002")
EMPIRICAL="SFT-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002"


def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
def seals():
 for tool,status in (("verify_engine_seal.py","VALID_CANONICAL_ENGINE"),("verify_verification_authority_seal.py","VALID_CANONICAL_VERIFICATION_AUTHORITY")):
  r=subprocess.run((sys.executable,str(ROOT/"tools"/tool),"--json"),cwd=ROOT,text=True,capture_output=True); d=json.loads(r.stdout) if r.stdout.strip() else {}
  if r.returncode or d.get("status")!=status:raise SystemExit("Earth/Astronomy admission halted")
def load(c):
 p=ROOT/"claims"/c/"execution.py"; s=importlib.util.spec_from_file_location("astro_"+c.replace("-","_"),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
def manifest(c):
 p=ROOT/"census/execution_manifest.json";d=json.loads(p.read_text())
 if c not in {x["claim_id"] for x in d["claims"]}:d["claims"].append({"claim_id":c,"execution_file":f"claims/{c}/execution.py"});write(p,d)
def materialize(spec,run,receipt,cap):
 sealed,ind,emp=cap["sealed"],cap["independent"],cap.get("empirical"); row=next(x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"] if x["claim_id"]==spec.claim_id);pkg=ROOT/"claims"/spec.claim_id
 cert={"claim_id":spec.claim_id,"status":"authoritatively_corresponded_and_independently_replicated" if emp else "independently_replicated","source_manifest_hash":run.program.registration.source_hash,"independent_implementation_hash":ind.implementation_hash,"independent_certificate_hash":ind.certificate_hash,"derivation_seal_hash":sealed.seal_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"exact_result":spec.exact_result,"closure_scope":receipt.closure_status,"controls_passed":all(x.passed for x in sealed.controls),"independently_recomputed":ind.passed,"free_parameters":[],"imported_axioms":[]}
 payloads={"candidate_census.json":{"claim_id":spec.claim_id,**asdict(sealed.census)},"elimination_receipt.json":{"claim_id":spec.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},"controls.json":{"claim_id":spec.claim_id,"controls":asdict(sealed)["controls"]},"certificate.json":cert,"registration.json":{"$schema":"../../governance/claim.schema.json","branch":"earth_environment" if spec.claim_id.startswith("SFT-EARTH-") else "astronomy_cosmology","claim_id":spec.claim_id,"title":spec.title,"statement":spec.exact_result,"dependencies":list(spec.dependencies),"excluded_inputs":list(spec.exclusions),"candidate_grammar":{"boundary":spec.grammar_boundary,"generator":spec.generation_rule,"completeness_certificate":"untouched-engine complete literal product"},"intended_certificate":"Complete 256-form depth-independent census and implementation-distinct reconstruction.","provenance_classes":[x.value for x in spec.provenance],"registered_by":"Maria Smith","registration_date":"2026-07-28","required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"status":"empirically_tested" if emp else "independently_replicated"}}
 if emp:
  payloads["empirical_validation.json"]={"claim_id":spec.claim_id,**asdict(emp)};cert.update({"measurement_receipt_hash":emp.measurement_receipt_hash,"all_external_rows_preserved":emp.all_rows_preserved,"external_data_source_ids":list(emp.data_source_ids),"falsification_condition":emp.falsification_condition})
  from sft.astronomy.prior_return_external_v1 import external_registration_record
  write(ROOT/"experiments/astronomy_cosmology/SFT-EXP-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002/registration.json",{**external_registration_record(),"status":"authoritatively_corresponded"})
 for n,v in payloads.items():write(pkg/n,v)
 (pkg/"STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `{cert['status']}`\n\n- {spec.exact_result}\n- 256 forms enumerated; one survived; all controls passed.\n- Engine receipt: `{receipt.receipt_hash}`\n")
def admit(order):
 from sft.engine import EngineRepository
 from sft.astronomy.prior_return_laws_v1 import SPECS
 existing={x["claim_id"] for x in json.loads((ROOT/"census/claims.json").read_text())["claims"]}
 for i,c in enumerate(order,1):
  if c in existing:raise SystemExit("already admitted: "+c)
  spec=SPECS[c];missing=tuple(x for x in spec.dependencies if x not in {y["claim_id"] for y in json.loads((ROOT/"census/claims.json").read_text())["claims"]})
  if missing:raise SystemExit(f"{c} dependencies absent: {missing}")
  run=load(c);cap={}
  class I:
   def validate(self,s):cap["sealed"]=s;z=run.independent_validator.validate(s);cap["independent"]=z;return z
  class E:
   def validate(self,s):z=run.empirical_validator.validate(s);cap["empirical"]=z;return z
  receipt=EngineRepository(ROOT).execute_official(run.program,I(),run.source_files,E() if run.empirical_validator else None)
  if not receipt.model_admitted:raise RuntimeError(c+" did not enter model")
  manifest(c);materialize(spec,run,receipt,cap);seals();existing.add(c);print(f"[{i}/{len(order)}] admitted {c}: {receipt.receipt_hash}",flush=True)
def main():
 seals();admit(FORMAL if "--formal-only" in sys.argv else (EMPIRICAL,) if "--empirical-only" in sys.argv else FORMAL+(EMPIRICAL,))
if __name__=="__main__":main()
