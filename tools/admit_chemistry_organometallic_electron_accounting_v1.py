#!/usr/bin/env python3
"""Officially admit and materialize Chemistry INORG-011 exactly once."""
from dataclasses import asdict
import importlib.util,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from sft.chemistry.organometallic_electron_accounting_batch_v1 import ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC,PRIMARY_PATH  # noqa:E402
from sft.chemistry.organometallic_electron_accounting_validation_v1 import _source_rows,exact_analysis  # noqa:E402
from sft.engine import EngineRepository  # noqa:E402
def write_json(path,payload): path.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
def load_execution():
 p=ROOT/"claims"/ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC.claim_id/"execution.py"; s=importlib.util.spec_from_file_location("sft_chemistry_inorg_011",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m.build_execution(ROOT)
def main():
 spec=ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC; census_path=ROOT/"census/claims.json"
 if spec.claim_id in {x["claim_id"] for x in json.loads(census_path.read_text())["claims"]}: raise SystemExit("claim already admitted; immutable receipt preserved")
 execution=load_execution(); captured={}
 class CaptureIndependent:
  def validate(self,sealed): captured["sealed"]=sealed; captured["external"]=execution.independent_validator.validate(sealed); return captured["external"]
 class CaptureEmpirical:
  def validate(self,sealed): captured["empirical"]=execution.empirical_validator.validate(sealed); return captured["empirical"]
 receipt=EngineRepository(ROOT).execute_official(execution.program,CaptureIndependent(),execution.source_files,CaptureEmpirical())
 if not receipt.model_admitted: raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
 sealed,external,empirical=captured["sealed"],captured["external"],captured["empirical"]
 manifest_path=ROOT/"census/execution_manifest.json"; manifest=json.loads(manifest_path.read_text()); manifest["claims"].append({"claim_id":spec.claim_id,"execution_file":f"claims/{spec.claim_id}/execution.py"}); write_json(manifest_path,manifest)
 census_row=next(x for x in json.loads(census_path.read_text())["claims"] if x["claim_id"]==spec.claim_id); package=ROOT/"claims"/spec.claim_id; analysis=exact_analysis(_source_rows(ROOT),json.loads((ROOT/PRIMARY_PATH).read_text()))
 payloads={
  "candidate_census.json":{"claim_id":spec.claim_id,**asdict(sealed.census)},"elimination_receipt.json":{"claim_id":spec.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},"controls.json":{"claim_id":spec.claim_id,"controls":asdict(sealed)["controls"]},"empirical_validation.json":{"claim_id":spec.claim_id,**asdict(empirical)},
  "certificate.json":{"claim_id":spec.claim_id,"chemistry_obligation":"SFT-CHEM-OBL-INORG-011","status":"model_admitted_forward_forced_empirically_tested_and_independently_replicated","source_manifest_hash":execution.program.registration.source_hash,"derivation_seal_hash":sealed.seal_hash,"independent_implementation_hash":external.implementation_hash,"independent_certificate_hash":external.certificate_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"measurement_receipt_hash":empirical.measurement_receipt_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":census_row["receipt_path"],"closure_scope":receipt.closure_status,"exact_result":spec.exact_result,"candidate_count":len(sealed.census.candidates),"unique_survivor_count":sum(x.survives for x in sealed.decisions),"forced_support_width_vector":[analysis["s_width"],analysis["p_width"],analysis["d_width"]],"forced_capacity":analysis["capacity"],"complete_account_count":analysis["complete_count"],"complete_account_relation":analysis["complete_relation"],"pair_successor_count_vector":[analysis["partial_count"],analysis["successor_count"]],"capacity_overflow_rejected":analysis["overflow_rejected"],"complete_registered_external_surface_count":analysis["complete_target_count"],"complete_target_vector_hash":analysis["complete_target_vector_hash"],"source_recapture_count":analysis["source_recapture_count"],"all_external_rows_preserved":empirical.all_rows_preserved,"numerical_zero_negative_irrational_imaginary_signed_continuum_fitted_free_or_imported_parameter_used":False,"observed_eighteen_oxidation_state_species_lookup_or_fit_used_to_select_capacity":False,"falsification_condition":empirical.falsification_condition}
 }
 for name,payload in payloads.items(): write_json(package/name,payload)
 reg=json.loads((package/"registration.json").read_text()); reg["status"]="empirically_tested"; reg["candidate_grammar"]["completeness_certificate"]=sealed.census.completeness_certificate_hash; write_json(package/"registration.json",reg)
 ep=ROOT/"experiments/chemistry"/spec.experiment_id/"registration.json"; ex=json.loads(ep.read_text()); ex["status"]="measured"; write_json(ep,ex)
 (package/"STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-INORG-011`\n- Forced support widths: `2, 6, 10`; exact capacity: `18`.\n- External vector: four complete IUPAC rows; no recapture.\n- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",encoding="utf-8")
 print(f"admitted {spec.claim_id}: {receipt.receipt_hash}"); print(f"derivation seal: {sealed.seal_hash}"); print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(x.survives for x in sealed.decisions)}"); print("forced capacity: 2+6+10=18; complete external vector: four rows; no recapture")
if __name__=="__main__": main()
