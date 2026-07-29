#!/usr/bin/env python3
"""Seal five ANAL-001–005 laws before complete-source capture."""
import hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from sft.chemistry.analytical_accuracy_trueness_law_v1 import EXACT_RESULT as A1_RESULT, OPERATIONAL_WITNESSES as A1_WITNESSES
from sft.chemistry.analytical_precision_repeatability_law_v1 import EXACT_RESULT as A2_RESULT, OPERATIONAL_WITNESSES as A2_WITNESSES
from sft.chemistry.analytical_sensitivity_law_v1 import EXACT_RESULT as A3_RESULT, OPERATIONAL_WITNESSES as A3_WITNESSES
from sft.chemistry.analytical_detection_quantification_law_v1 import EXACT_RESULT as A4_RESULT, OPERATIONAL_WITNESSES as A4_WITNESSES
from sft.chemistry.analytical_selectivity_interference_law_v1 import EXACT_RESULT as A5_RESULT, OPERATIONAL_WITNESSES as A5_WITNESSES

REGISTRY="experiments/external_sources/chemistry/anal_001_005_family_source_identity_registry_v1.json"
CONFIG={
 "001":("SFT-CHEM-ANALYTICAL-ACCURACY-TRUENESS-001","SFT-CHEM-OBL-ANAL-001","sft/chemistry/analytical_accuracy_trueness_law_v1.py","experiments/external_sources/chemistry/anal_001_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_001_pre_source_v1.json",A1_RESULT,A1_WITNESSES),
 "002":("SFT-CHEM-ANALYTICAL-PRECISION-REPEATABILITY-002","SFT-CHEM-OBL-ANAL-002","sft/chemistry/analytical_precision_repeatability_law_v1.py","experiments/external_sources/chemistry/anal_002_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_002_pre_source_v1.json",A2_RESULT,A2_WITNESSES),
 "003":("SFT-CHEM-ANALYTICAL-SENSITIVITY-003","SFT-CHEM-OBL-ANAL-003","sft/chemistry/analytical_sensitivity_law_v1.py","experiments/external_sources/chemistry/anal_003_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_003_pre_source_v1.json",A3_RESULT,A3_WITNESSES),
 "004":("SFT-CHEM-ANALYTICAL-DETECTION-QUANTIFICATION-004","SFT-CHEM-OBL-ANAL-004","sft/chemistry/analytical_detection_quantification_law_v1.py","experiments/external_sources/chemistry/anal_004_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_004_pre_source_v1.json",A4_RESULT,A4_WITNESSES),
 "005":("SFT-CHEM-ANALYTICAL-SELECTIVITY-INTERFERENCE-005","SFT-CHEM-OBL-ANAL-005","sft/chemistry/analytical_selectivity_interference_law_v1.py","experiments/external_sources/chemistry/anal_005_target_identities_v1.json","experiments/sealed_predictions/chemistry_anal_005_pre_source_v1.json",A5_RESULT,A5_WITNESSES),}
def digest(data): return "sha256:"+hashlib.sha256(data).hexdigest()
def main():
 registry_hash=digest((ROOT/REGISTRY).read_bytes())
 for key,(claim,obligation,law,identity,output,result,witnesses) in CONFIG.items():
  target=ROOT/output
  if target.exists(): raise SystemExit(f"refusing to replace existing seal: {output}")
  if len(witnesses)!=8 or not all(x[2] for x in witnesses): raise SystemExit(f"ANAL-{key} native witness failed")
  payload={"schema":"sft-v3-source-exposure-disclosed-derivation-seal/1","branch":"chemistry","family":"ANAL-001-005","claim_id":claim,"obligation_id":obligation,"sealed_date":"2026-07-28","derivation_path":law,"derivation_hash":digest((ROOT/law).read_bytes()),"target_identity_path":identity,"target_identity_hash":digest((ROOT/identity).read_bytes()),"source_identity_registry_path":REGISTRY,"source_identity_registry_hash":registry_hash,"candidate_cardinality":256,"operational_witness_count":8,"predicted_unique_survivor":result,"complete_postseal_source_capture_had_occurred_before_this_seal":False,"prior_source_exposure_never_relabelled_blind":True,"source_exposure_before_seal":"titles abstracts search snippets and disclosed summary ranges observed exactly as recorded in the family registry; complete documents tables figures row vectors and limitations not captured","source_value_equation_outcome_or_conventional_model_used_by_candidate_generator_or_eliminator":False}
  payload["sealed_payload_hash"]=digest(json.dumps(payload,sort_keys=True,separators=(",",":")).encode());target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(key,digest(target.read_bytes()),payload["sealed_payload_hash"])
if __name__=="__main__": main()
