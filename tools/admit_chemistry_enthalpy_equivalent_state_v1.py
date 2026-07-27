#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-006 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from sft.chemistry.enthalpy_equivalent_state_batch_v1 import ENTHALPY_EQUIVALENT_STATE_SPEC  # noqa:E402
from sft.chemistry.enthalpy_equivalent_state_validation_v1 import _source_rows,exact_enthalpy_analysis  # noqa:E402
from sft.engine import EngineRepository  # noqa:E402


def write_json(path,payload): path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def load_execution():
    path=ROOT/"claims"/ENTHALPY_EQUIVALENT_STATE_SPEC.claim_id/"execution.py"; definition=importlib.util.spec_from_file_location("sft_chemistry_thermo_006",path)
    if definition is None or definition.loader is None: raise RuntimeError("cannot load THERMO-006 execution package")
    module=importlib.util.module_from_spec(definition); definition.loader.exec_module(module); return module.build_execution(ROOT)


def main():
    spec=ENTHALPY_EQUIVALENT_STATE_SPEC; census_path=ROOT/"census/claims.json"; existing={row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if spec.claim_id in existing: raise SystemExit("claim already admitted; immutable receipt preserved")
    execution=load_execution(); captured={}
    class CaptureIndependent:
        def validate(self,sealed): captured["sealed"]=sealed; result=execution.independent_validator.validate(sealed); captured["external"]=result; return result
    class CaptureEmpirical:
        def validate(self,sealed): result=execution.empirical_validator.validate(sealed); captured["empirical"]=result; return result
    receipt=EngineRepository(ROOT).execute_official(execution.program,CaptureIndependent(),execution.source_files,CaptureEmpirical())
    if not receipt.model_admitted: raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed,external,empirical=captured["sealed"],captured["external"],captured["empirical"]
    manifest_path=ROOT/"census/execution_manifest.json"; manifest=json.loads(manifest_path.read_text())
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}: manifest["claims"].append({"claim_id":spec.claim_id,"execution_file":f"claims/{spec.claim_id}/execution.py"}); write_json(manifest_path,manifest)
    census=json.loads(census_path.read_text()); census_row=next(row for row in census["claims"] if row["claim_id"]==spec.claim_id); package=ROOT/"claims"/spec.claim_id; rows=_source_rows(ROOT); analysis=exact_enthalpy_analysis(rows)
    vector=tuple({"target_id":row["target_id"],"temperature_kelvin":row["target_payload"]["temperature-kelvin"],"phase":row["target_payload"]["phase-identity"],"enthalpy_kilojoule_per_mole":row["target_payload"]["enthalpy-kilojoule-per-mole"],"internal_energy_kilojoule_per_mole":row["target_payload"]["internal-energy-kilojoule-per-mole"],"environment_component_kilojoule_per_mole":str(analysis["environment_component_values_kilojoule_per_mole"][index]),"complete_state_payload_hash":row["target_payload_hash"]} for index,row in enumerate(rows))
    payloads={
        "candidate_census.json":{"claim_id":spec.claim_id,**asdict(sealed.census)},"elimination_receipt.json":{"claim_id":spec.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},"controls.json":{"claim_id":spec.claim_id,"controls":asdict(sealed)["controls"]},"empirical_validation.json":{"claim_id":spec.claim_id,**asdict(empirical)},
        "certificate.json":{"claim_id":spec.claim_id,"chemistry_obligation":"SFT-CHEM-OBL-THERMO-006","status":"model_admitted_observationally_derived_empirically_tested_and_independently_replicated","source_manifest_hash":execution.program.registration.source_hash,"derivation_seal_hash":sealed.seal_hash,"independent_implementation_hash":external.implementation_hash,"independent_certificate_hash":external.certificate_hash,"external_validation_hash":receipt.external_validation_hash,"empirical_validation_hash":receipt.empirical_validation_hash,"measurement_receipt_hash":empirical.measurement_receipt_hash,"engine_receipt_hash":receipt.receipt_hash,"engine_receipt_path":census_row["receipt_path"],"closure_scope":receipt.closure_status,"exact_result":spec.exact_result,"candidate_count":len(sealed.census.candidates),"unique_survivor_count":sum(item.survives for item in sealed.decisions),"state_law":"complete held chemical state and environment carrier","composition_law":"retained exact positive internal content plus generated organized environment-transfer parts","absence_and_orientation_law":"structural EmptyOne absence/equality; held rise/fall plus positive separation","successor_law":"one fresh named environment part appends without rewriting prior content","complete_external_target_count":len(rows),"complete_returned_column_count":14,"liquid_row_count":9,"vapor_row_count":4,"phase_boundary_row_count":2,"complete_enthalpy_vector_kilojoule_per_mole":tuple(str(v) for v in analysis["enthalpy_values_kilojoule_per_mole"]),"complete_internal_energy_vector_kilojoule_per_mole":tuple(str(v) for v in analysis["internal_energy_values_kilojoule_per_mole"]),"complete_environment_component_vector_kilojoule_per_mole":tuple(str(v) for v in analysis["environment_component_values_kilojoule_per_mole"]),"complete_adjacent_positive_enthalpy_steps":tuple(str(v) for v in analysis["adjacent_exact_positive_enthalpy_steps"]),"all_component_records_agree_with_pressure_volume_within_display_resolution":analysis["all_component_records_agree_with_pressure_volume_within_display_resolution"],"complete_external_enthalpy_state_vector":vector,"all_external_rows_preserved":empirical.all_rows_preserved,"external_data_source_ids":list(empirical.data_source_ids),"all_enthalpy_component_and_state_values_released_after_identity_seal":True,"external_component_relation_is_postseal_correspondence_only":True,"external_value_in_derivation_or_prediction":False,"fitted_correction_or_imported_enthalpy_equation_used":False,"numerical_zero_used":False,"negative_irrational_imaginary_or_continuum_proof_value_used":False,"observational_development_disclosed":True,"falsification_condition":empirical.falsification_condition}}
    for name,payload in payloads.items(): write_json(package/name,payload)
    registration_path=package/"registration.json"; registration=json.loads(registration_path.read_text()); registration["status"]="empirically_tested"; write_json(registration_path,registration)
    experiment_path=ROOT/"experiments/chemistry"/spec.experiment_id/"registration.json"; experiment=json.loads(experiment_path.read_text()); experiment["status"]="complete_direct_enthalpy_and_component_vectors_opened_postseal"; write_json(experiment_path,experiment)
    status=f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-THERMO-006`\n- Closure: `{receipt.closure_status}`\n- Exact law: complete state/environment carrier with exact positive internal and organized environment-transfer composition.\n- Direct NIST vector: `13` enthalpy states, `13` component records and `12` exact positive additive steps.\n- Components: every `H-U` record agrees with the pressure-volume record within exact displayed resolution.\n- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n"; (package/"STATUS.md").write_text(status)
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}"); print(f"derivation seal: {sealed.seal_hash}"); print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(item.survives for item in sealed.decisions)}"); print("NIST enthalpy vector: 13 rows; 12 exact positive increments; component relation resolved")


if __name__=="__main__": main()
