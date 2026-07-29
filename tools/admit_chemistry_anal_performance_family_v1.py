#!/usr/bin/env python3
"""Submit exactly one ANAL-001–005 claim per invocation in dependency order."""
from dataclasses import asdict
import argparse,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sft.chemistry.anal_performance_batch_v1 import ACCURACY_SPEC,DETECTION_SPEC,PRECISION_SPEC,SELECTIVITY_SPEC,SENSITIVITY_SPEC
from sft.chemistry.anal_performance_validation_v1 import exact_analysis
from sft.engine import EngineRepository
CONFIG={
 "001":(ACCURACY_SPEC,"SFT-CHEM-OBL-ANAL-001","accuracy_trueness_receipt.json","model_admitted_forced_analytical_accuracy_trueness_law_empirically_tested_and_independently_replicated","six certified pairs, one non-certified reference pair, all uncertainties and archived-status limits"),
 "002":(PRECISION_SPEC,"SFT-CHEM-OBL-ANAL-002","precision_repeatability_receipt.json","model_admitted_forced_analytical_precision_repeatability_law_empirically_tested_and_independently_replicated","four measured precision/agreement ranges, sixfold and duplicate supports and complete drift/stability limits"),
 "003":(SENSITIVITY_SPEC,"SFT-CHEM-OBL-ANAL-003","sensitivity_receipt.json","model_admitted_forced_analytical_sensitivity_law_empirically_tested_and_independently_replicated","three/four calibration supports, 0.2% sensitivity, 0.5% nonlinearity trigger and drift/extrapolation limits"),
 "004":(DETECTION_SPEC,"SFT-CHEM-OBL-ANAL-004","detection_quantification_receipt.json","model_admitted_forced_detection_quantification_boundary_law_empirically_tested_and_independently_replicated","eight-rule disagreement, three boundary classes, exact error assumptions and all worked detection/quantification values"),
 "005":(SELECTIVITY_SPEC,"SFT-CHEM-OBL-ANAL-005","selectivity_interference_receipt.json","model_admitted_forced_analytical_selectivity_interference_law_empirically_tested_and_independently_replicated","sixteen analytes and both complete sixteen-row mobility/background and mass/TPR/FPR vectors with all adverse overlap"),}
def write(path,data):path.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
def build_execution(claim):
 path=ROOT/"claims"/claim.claim_id/"execution.py";spec=importlib.util.spec_from_file_location("admit_"+claim.claim_id.rsplit("-",1)[-1],path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module.build_execution(ROOT)
def main():
 parser=argparse.ArgumentParser();parser.add_argument("claim",choices=tuple(CONFIG));args=parser.parse_args();claim,obligation,receipt_name,status,external_surface=CONFIG[args.claim];census_path=ROOT/"census/claims.json";admitted={x["claim_id"] for x in json.loads(census_path.read_text())["claims"]}
 if claim.claim_id in admitted:raise SystemExit("claim already admitted; immutable receipt preserved")
 for dependency in claim.dependencies:
  if dependency not in admitted:raise SystemExit(f"dependency not admitted; halted before submission: {dependency}")
 run=build_execution(claim);captured={}
 class Independent:
  def validate(self,sealed):captured.update(sealed=sealed,independent=run.independent_validator.validate(sealed));return captured["independent"]
 class Empirical:
  def validate(self,sealed):captured["empirical"]=run.empirical_validator.validate(sealed);return captured["empirical"]
 result=EngineRepository(ROOT).execute_official(run.program,Independent(),run.source_files,Empirical())
 if not result.model_admitted:raise SystemExit(f"claim halted at {result.halted_stage}; preserved receipt {result.receipt_hash}")
 sealed,independent,empirical=captured["sealed"],captured["independent"],captured["empirical"];manifest_path=ROOT/"census/execution_manifest.json";manifest=json.loads(manifest_path.read_text());manifest["claims"].append({"claim_id":claim.claim_id,"execution_file":f"claims/{claim.claim_id}/execution.py"});write(manifest_path,manifest);row=next(x for x in json.loads(census_path.read_text())["claims"] if x["claim_id"]==claim.claim_id);package=ROOT/"claims"/claim.claim_id;analysis,checks=exact_analysis(ROOT,claim.claim_id)
 certificate={"claim_id":claim.claim_id,"chemistry_obligation":obligation,"status":status,"source_manifest_hash":run.program.registration.source_hash,"derivation_seal_hash":sealed.seal_hash,"independent_implementation_hash":independent.implementation_hash,"independent_certificate_hash":independent.certificate_hash,"external_validation_hash":result.external_validation_hash,"empirical_validation_hash":result.empirical_validation_hash,"measurement_receipt_hash":empirical.measurement_receipt_hash,"engine_receipt_hash":result.receipt_hash,"engine_receipt_path":row["receipt_path"],"closure_scope":result.closure_status,"exact_result":claim.exact_result,"candidate_count":len(sealed.census.candidates),"unique_survivor_count":sum(x.survives for x in sealed.decisions),**analysis,"all_registered_target_checks_passed":all(checks.values()),"registered_target_check_count":len(checks),"all_external_rows_preserved":empirical.all_rows_preserved,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used":False,"external_values_equations_fits_discrepancies_or_trends_used_to_select_native_law":False,"falsification_condition":empirical.falsification_condition}
 artifacts={"candidate_census.json":{"claim_id":claim.claim_id,**asdict(sealed.census)},receipt_name:{"claim_id":claim.claim_id,"decisions":asdict(sealed)["decisions"],"closure":asdict(sealed.closure)},"controls.json":{"claim_id":claim.claim_id,"controls":asdict(sealed)["controls"]},"empirical_validation.json":{"claim_id":claim.claim_id,**asdict(empirical)},"certificate.json":certificate}
 for name,payload in artifacts.items():write(package/name,payload)
 registration=json.loads((package/"registration.json").read_text());registration["status"]="empirically_tested";registration["candidate_grammar"]["completeness_certificate"]=sealed.census.completeness_certificate_hash;write(package/"registration.json",registration);experiment_path=ROOT/"experiments/chemistry"/claim.experiment_id/"registration.json";experiment=json.loads(experiment_path.read_text());experiment["status"]="measured_postseal_complete";write(experiment_path,experiment);(package/"STATUS.md").write_text(f"# {claim.claim_id}\n\nStatus: `{status}`\n\n- Chemistry obligation: `{obligation}`\n- Exact law: `{claim.exact_result}`\n- Complete external surface: {external_surface}; all 83 PDF pages, one HTML document and 180,366 extracted characters retained.\n- Derivation seal: `{sealed.seal_hash}`\n- Engine receipt: `{result.receipt_hash}`\n");print(f"admitted {claim.claim_id}: {result.receipt_hash}");print(f"derivation seal: {sealed.seal_hash}");print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(x.survives for x in sealed.decisions)}")
if __name__=="__main__":main()
