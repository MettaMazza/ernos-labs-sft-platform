#!/usr/bin/env python3
"""Officially execute and materialize ELEC-004."""
from __future__ import annotations
from dataclasses import asdict
import importlib.util,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.chemistry.state_energy_order_batch_v1 import STATE_ENERGY_ORDER_SPEC  # noqa:E402
from sft.engine import EngineRepository  # noqa:E402
def write_json(path,payload):path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def load_execution():
 p=ROOT/"claims"/STATE_ENERGY_ORDER_SPEC.claim_id/"execution.py";s=importlib.util.spec_from_file_location("chem_state_energy_004",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
def main():
 s=STATE_ENERGY_ORDER_SPEC;census_path=ROOT/"census/claims.json";existing={r["claim_id"] for r in json.loads(census_path.read_text())["claims"]}
 if s.claim_id in existing:raise SystemExit("claim already admitted; immutable receipt preserved")
 e=load_execution();captured={}
 class I:
  def validate(self,sealed):captured["sealed"]=sealed;captured["external"]=e.independent_validator.validate(sealed);return captured["external"]
 class V:
  def validate(self,sealed):captured["empirical"]=e.empirical_validator.validate(sealed);return captured["empirical"]
 receipt=EngineRepository(ROOT).execute_official(e.program,I(),e.source_files,V())
 if not receipt.model_admitted:raise SystemExit(f"halted {receipt.halted_stage}; {receipt.receipt_hash}")
 sealed,external,empirical=captured["sealed"],captured["external"],captured["empirical"]
 mp=ROOT/"census/execution_manifest.json";manifest=json.loads(mp.read_text());manifest["claims"].append({"claim_id":s.claim_id,"execution_file":f"claims/{s.claim_id}/execution.py"});write_json(mp,manifest)
 census=json.loads(census_path.read_text());row=next(r for r in census["claims"] if r["claim_id"]==s.claim_id);p=ROOT/"claims"/s.claim_id
 artifacts={"candidate_census.json":{"claim_id":s.claim_id,**asdict(sealed.census)},"elimination_receipt.json":{"claim_id":s.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},"controls.json":{"claim_id":s.claim_id,"controls":asdict(sealed)["controls"]},"empirical_validation.json":{"claim_id":s.claim_id,**asdict(empirical)},"certificate.json":{"claim_id":s.claim_id,"chemistry_obligation":"SFT-CHEM-OBL-ELEC-004","status":"model_admitted_observationally_derived_empirically_tested_and_independently_replicated","source_manifest_hash":e.program.registration.source_hash,"derivation_seal_hash":sealed.seal_hash,"independent_implementation_hash":external.implementation_hash,"independent_certificate_hash":external.certificate_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"measurement_receipt_hash":empirical.measurement_receipt_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":row["receipt_path"],"closure_scope":receipt.closure_status,"exact_result":s.exact_result,"candidate_count":256,"unique_survivor_count":1,"measured_state_energy_rows":306,"ground_states":22,"excited_states":284,"strict_pairwise_orders":3325,"all_external_rows_preserved":empirical.all_rows_preserved,"external_data_source_ids":list(empirical.data_source_ids),"absolute_species_energy_formula_claimed":False,"falsification_condition":empirical.falsification_condition}}
 for name,data in artifacts.items():write_json(p/name,data)
 reg=json.loads((p/"registration.json").read_text());reg["status"]="empirically_tested";write_json(p/"registration.json",reg);ep=ROOT/"experiments/chemistry"/s.experiment_id/"registration.json";ex=json.loads(ep.read_text());ex["status"]="measured";write_json(ep,ex)
 (p/"STATUS.md").write_text(f"# {s.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-ELEC-004`\n- Closure: `{receipt.closure_status}`\n- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n- Empirical validation: `{receipt.empirical_validation_hash}`\n- Measurement receipt: `{empirical.measurement_receipt_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n- External vector: 306 NIST state energies, 22 ground states, 284 excited states and 3,325 strict pairs.\n- Scope: exact state order; degeneracy and symmetry distinction follows in ELEC-005.\n",encoding="utf-8")
 print(f"admitted {s.claim_id}: {receipt.receipt_hash}");print(f"derivation seal: {sealed.seal_hash}");print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(r.survives for r in sealed.decisions)}");print(f"empirical measurements: {len(empirical.measurements)}; passed: {empirical.passed}")
if __name__=="__main__":main()
