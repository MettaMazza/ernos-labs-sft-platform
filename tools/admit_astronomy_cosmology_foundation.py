#!/usr/bin/env python3
"""Admit Astronomy foundation claims sequentially through the sealed engine."""

from __future__ import annotations

import argparse, importlib.util, json, sys
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))

def boundaries():
    from sft.engine_seal import require_engine_seal
    require_engine_seal(ROOT)
    p=ROOT/"tools/verify_verification_authority_seal.py"; s=importlib.util.spec_from_file_location("_astro_authority",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); a=m.verify()
    if a["violations"]: raise RuntimeError("VOID_INVALID_HALTED: "+"; ".join(a["violations"]))
boundaries()
from sft.astronomy_cosmology.empirical_program import ASTRONOMY_SPECS, PRE_SOURCE_SEAL_PATH
from sft.engine import EngineRepository

CHECKPOINT=ROOT/"census/astronomy_cosmology_continuation_checkpoint.json"

def write(path,value): path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
def admitted(): return {x["claim_id"]:x for x in json.loads((ROOT/"census/claims.json").read_text())["claims"] if x.get("model_admitted") is True}
def execution(claim_id):
    p=ROOT/"claims"/claim_id/"execution.py"; s=importlib.util.spec_from_file_location("sft_astro_"+claim_id.replace("-","_"),p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m.build_execution(ROOT)
def manifest(claim_id):
    p=ROOT/"census/execution_manifest.json"; d=json.loads(p.read_text())
    if claim_id not in {x["claim_id"] for x in d["claims"]}: d["claims"].append({"claim_id":claim_id,"execution_file":f"claims/{claim_id}/execution.py"}); write(p,d)
def checkpoint(last,last_hash,count,next_op,status="in_progress"):
    c=json.loads(CHECKPOINT.read_text()); c.update({"schema":"sft-v3-astronomy-cosmology-continuation-checkpoint/1","branch":"astronomy_cosmology","foundation_required_claim_count":len(ASTRONOMY_SPECS),"admitted_claim_count":count,"remaining_claim_count":len(ASTRONOMY_SPECS)-count,"last_admitted_claim_id":last,"last_admitted_receipt_hash":last_hash,"closure_status":"depth_independent" if last else None,"status":status,"next_exact_operation":next_op,"engine_seal":"sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a","verification_authority_seal":"sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8","protected_authority_modified":False,"remote_publication_authorized":False}); write(CHECKPOINT,c)
def materialize(spec,exe,receipt,captured):
    sealed,external,empirical=captured["sealed"],captured["external"],captured["empirical"]; row=admitted()[spec.claim_id]; pkg=ROOT/"claims"/spec.claim_id; target=json.loads((ROOT/spec.source_snapshot_path).read_text()); transports=json.loads((ROOT/"experiments/astronomy_cosmology/source_transports.json").read_text())
    payloads={
      "candidate_census.json":{"claim_id":spec.claim_id,**asdict(sealed.census)},
      "elimination_receipt.json":{"claim_id":spec.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},
      "controls.json":{"claim_id":spec.claim_id,"controls":asdict(sealed)["controls"]},
      "empirical_validation.json":{"claim_id":spec.claim_id,**asdict(empirical)},
      "certificate.json":{"claim_id":spec.claim_id,"status":"model_admitted_empirically_tested_and_independently_reconstructed","pre_source_complete_branch_seal":PRE_SOURCE_SEAL_PATH,"source_manifest_hash":exe.program.registration.source_hash,"independent_implementation_hash":external.implementation_hash,"independent_certificate_hash":external.certificate_hash,"derivation_seal_hash":sealed.seal_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"measurement_receipt_hash":empirical.measurement_receipt_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"exact_result":spec.exact_result,"closure_scope":receipt.closure_status,"controls_passed":all(x.passed for x in sealed.controls),"independently_recomputed":external.passed,"all_external_rows_preserved":empirical.all_rows_preserved,"external_data_source_ids":list(empirical.data_source_ids),"external_evidence_class":spec.empirical_disposition,"evidence_directness":spec.directness,"registered_transport_count":transports["attempted"],"failed_transport_rows_preserved":transports["failed_preserved"],"claim_target_evaluation":target,"external_evidence_selected_survivor":False,"formal_structure_relabelled_as_direct_measurement":False,"model_or_forecast_relabelled_as_observation":False,"free_parameters":[],"axioms":[],"falsification_condition":empirical.falsification_condition},
    }
    for name,value in payloads.items(): write(pkg/name,value)
    reg=json.loads((pkg/"registration.json").read_text()); reg["status"]="empirically_tested"; write(pkg/"registration.json",reg)
    ep=ROOT/"experiments/astronomy_cosmology"/spec.experiment_id/"registration.json"; ex=json.loads(ep.read_text()); ex["status"]="empirical_boundary_corresponded"; write(ep,ex)
    (pkg/"STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `model_admitted_empirically_tested_and_independently_reconstructed`\n\n- Closure: `{receipt.closure_status}`\n- Engine receipt: `{receipt.receipt_hash}`\n- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n- Post-seal empirical validation: `{receipt.empirical_validation_hash}`\n- Preserved transport failures: `{transports['failed_preserved']}`\n- External evidence selected the survivor: `false`\n")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--limit",type=int); args=ap.parse_args(); boundaries(); repo=EngineRepository(ROOT); have=admitted(); ids=[x.claim_id for x in ASTRONOMY_SPECS]; prefix=0
    for cid in ids:
        if cid in have: prefix+=1
        else: break
    if any(x in have for x in ids[prefix:]): raise RuntimeError("Astronomy receipts are not a continuous prefix")
    last=ids[prefix-1] if prefix else None; last_hash=have[last]["receipt_hash"] if last else None; pending=ASTRONOMY_SPECS[prefix:]
    if args.limit: pending=pending[:args.limit]
    checkpoint(last,last_hash,prefix,"admit_"+(ids[prefix] if prefix<len(ids) else "reconcile"))
    for index,spec in enumerate(pending,prefix+1):
        boundaries(); exe=execution(spec.claim_id); captured={}
        class I:
            def validate(self,sealed): captured["sealed"]=sealed; captured["external"]=exe.independent_validator.validate(sealed); return captured["external"]
        class E:
            def validate(self,sealed): captured["empirical"]=exe.empirical_validator.validate(sealed); return captured["empirical"]
        try: receipt=repo.execute_official(exe.program,I(),exe.source_files,E())
        except Exception: checkpoint(last,last_hash,index-1,"repair_or_preserve_halt_"+spec.claim_id,"halted_on_claim"); raise
        boundaries(); manifest(spec.claim_id); materialize(spec,exe,receipt,captured); last=spec.claim_id; last_hash=receipt.receipt_hash; next_id=ids[index] if index<len(ids) else None; checkpoint(last,last_hash,index,"admit_"+next_id if next_id else "reconcile_audit_inventory_and_paper")
        if index==1 or index%5==0 or index==len(ids): print(f"[{index}/{len(ids)}] admitted {spec.claim_id}: {receipt.receipt_hash}",flush=True)

if __name__=="__main__": main()
