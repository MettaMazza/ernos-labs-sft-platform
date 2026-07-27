#!/usr/bin/env python3
"""Scaffold the Physics-scale ELEC-004 claim package."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from sft.chemistry.state_energy_order_batch_v1 import IDENTITY_HASH,IDENTITY_PATH,SOURCE_ID,STATE_ENERGY_ORDER_SPEC,TARGET_HASH,TARGET_PATH  # noqa:E402
from sft.chemistry.state_energy_order_validation_v1 import experiment_registration_record,prediction_program_document  # noqa:E402
from sft.engine.canonical import sha256_identity  # noqa:E402
from sft.physics.generated_empirical_law import completeness_record,survivor_id  # noqa:E402

def write(path,content): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding="utf-8")
def claim_registration():
 s=STATE_ENERGY_ORDER_SPEC
 return {"$schema":"../../governance/claim.schema.json","claim_id":s.claim_id,"title":s.title,"branch":"chemistry","status":"registered","statement":s.statement,"dependencies":list(s.dependencies),"provenance_classes":["observational_derivation"],"candidate_grammar":{"generator":s.generation_rule,"boundary":s.grammar_boundary,"expected_cardinality":256,"completeness_certificate":sha256_identity(completeness_record(s))},"excluded_inputs":list(s.exclusions),"required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"intended_certificate":"Complete 256-form structural census, unique survivor, depth-independent successor, independent reconstruction, capability-closed 22-species order law, complete 306-value NIST vector and 3,325 pairwise order checks.","empirical_protocol":f"experiments/chemistry/{s.experiment_id}/registration.json","registered_by":"Maria Smith","registration_date":"2026-07-26"}
def experiment_registration():
 s=STATE_ENERGY_ORDER_SPEC;p=prediction_program_document(ROOT);r=experiment_registration_record(ROOT);snapshots={x.snapshot_path:x.snapshot_hash for x in s.target_rows}
 return {"$schema":"../../../governance/experiment.schema.json","experiment_id":s.experiment_id,"claim_id":s.claim_id,"evidence_mode":"observational_derivation","development_observations":[{"source_id":SOURCE_ID,"role":"question-and-test-domain-only","target_values_absent_from_survivor_selection":True}],"external_measurement_sources":[{"source_id":SOURCE_ID,"measurement_body":"National Institute of Standards and Technology","database":"NIST Chemistry WebBook SRD 69","doi":"10.18434/T4D303","source_uri":"https://webbook.nist.gov/chemistry/","state_energy_rows":306,"ground_rows":22,"excited_rows":284,"unit":"inverse-centimetre","custody_role":"post-seal-state-energy-target"}],"frozen_relation":{"statement":s.exact_result,"relation_hash":sha256_identity(s.exact_result),"dependency_hashes":[sha256_identity(x) for x in s.dependencies],"candidate_grammar":s.generation_rule,"exact_domain":s.grammar_boundary,"target_did_not_select_survivor":True},"inputs":[{"input_id":"registered-premise","value_kind":"held-sealed-derivation","content_hash":sha256_identity(s.dependencies)},{"input_id":"target-identities-only","path":IDENTITY_PATH,"content_hash":IDENTITY_HASH,"energy_values_absent":True}],"withheld_targets":[{"target_id":x.target_id,"source_id":x.source_id,"snapshot_hash":x.snapshot_hash,"content_withheld_from_prediction":True} for x in s.target_rows],"dimension_unit_boundary":{"proof_order":"structural-empty-One least state followed by positive successors","external_values":"NIST source-zero and positive decimal inscriptions retained as measurement records only","excluded_unit_rows":"explicit eV rows excluded from the single inverse-centimetre comparison vector before registration","proof_value_policy":"positive-counts-held-labels-and-structural-empty-One-only"},"prediction_protocol":{"interpreter_id":"sft-v3-capability-closed-fold-interpreter/1","program_id":p["program_id"],"program_hash":sha256_identity(p),"executor_id":s.experiment_id+"-prediction-executor","complete_trace_required":True,"forbidden_capabilities":["clock","dynamic_import","environment","filesystem_read","filesystem_write","foreign_function","network","subprocess"]},"evaluation_protocol":{"evaluator_id":s.experiment_id+"-post-seal-NIST-evaluator","comparison_implementation_hash":sha256_identity(("complete-NIST-state-energy-order-comparator/1",s.experiment_id)),"metrics":[{"metric_id":"complete-state-energy-vector","definition":"Retain and exactly parse all 306 registered NIST Te inscriptions.","all_rows":True},{"metric_id":"complete-finite-order","definition":"Verify one unique measured least X state per species, 284 positive excited gaps and every strict pairwise order.","all_rows":True}],"acceptance_condition":"All 306 rows, 22 ground identifications, 284 excited gaps, 3,325 state pairs and adverse controls pass.","falsification_condition":s.falsification_condition},"controls":[{"control_id":"FALSE-PREMISE","kind":"false_premise","expected_rejection":"Missing or duplicated structural least state rejects."},{"control_id":"TAMPERED-SOURCE","kind":"tampered_source","expected_rejection":"Changed NIST bytes reject."},{"control_id":"TAMPERED-ARTIFACT","kind":"tampered_artifact","expected_rejection":"Omitted state or comparison rejects."},{"control_id":"BOUNDARY","kind":"boundary","expected_rejection":"Measured values in derivation, signed proof gaps or mixed units reject."},{"control_id":"TIED-GROUND","kind":"unfavorable_measurement","expected_rejection":"Two least states reject."},{"control_id":"NEGATIVE-GAP","kind":"unfavorable_measurement","expected_rejection":"A reversed higher/lower gap rejects."},{"control_id":"OMITTED-ROW","kind":"unfavorable_measurement","expected_rejection":"A 305-row vector rejects."}],"custody_protocol":{"exchange_id":"sft-v3-portable-target-exchange/1","custodian_id":s.experiment_id+"-NIST-target-custodian","custodian_distinct_from_executor":True,"withheld_target_registry_path":TARGET_PATH,"withheld_target_registry_hash":TARGET_HASH,"release_requires_matching_prediction_seal":True},"target_access_policy":"structurally-denied-before-seal","row_retention_policy":"retain-all-306-values-and-all-adverse-rows","stop_condition":"Halt on any violation; otherwise stop after the complete vector and controls.","source_hashes":snapshots|{IDENTITY_PATH:IDENTITY_HASH,TARGET_PATH:TARGET_HASH,"experiment-registration-record":sha256_identity(r)},"registration_date":"2026-07-26","registered_by":"Maria Smith","status":"registered"}
def independent_source():
 s=STATE_ENERGY_ORDER_SPEC;domains=tuple(tuple(c.name for c in d.choices) for d in s.dimensions)
 return f'''from itertools import product
import json,sys
CLAIM={s.claim_id!r};DOMAINS={domains!r};SURVIVOR={survivor_id(s)!r}
def main():
 d=json.load(open(sys.argv[1]));g=["__".join(x) for x in product(*DOMAINS)];r=[x["candidate_id"] for x in d["census"]["candidates"]];z={{x["candidate_id"]:x["survives"] for x in d["decisions"]}};p=(d["claim_id"]==CLAIM and r==g and len(set(r))==256 and z=={{x:x==SURVIVOR for x in g}} and sum(z.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and all(x["passed"] for x in d["controls"]));print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":p,"certificate":{{"claim_id":CLAIM,"candidate_count":len(g),"survivor":SURVIVOR if p else None}}}},sort_keys=True))
if __name__=="__main__":main()
'''
def execution_source():
 s=STATE_ENERGY_ORDER_SPEC
 return f'''from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.state_energy_order_batch_v1 import STATE_ENERGY_ORDER_SPEC
from sft.chemistry.state_energy_order_validation_v1 import StateEnergyOrderValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=STATE_ENERGY_ORDER_SPEC;files=(root/"sft/chemistry/state_energy_order_law_v1.py",root/"sft/chemistry/state_energy_order_batch_v1.py",root/"sft/chemistry/state_energy_order_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/{s.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/{s.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(s,h),ExternalCommandValidator("{s.claim_id.lower()}-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),files,StateEnergyOrderValidator(root))
'''
def note():
 s=STATE_ENERGY_ORDER_SPEC
 return f"""# {s.title}

Claim: `{s.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-004`

## WHY

A molecular spectrum requires more than named states: it requires a reproducible order over complete state/support identities at one declared molecular composition and geometry. Numerical zero is not imported as the proof of a ground state. The least state is the structural empty-One boundary; every excitation is a positive successor.

## DERIVATION

The eight-axis grammar enumerates 256 carrier, identity, least-state, excitation, order, gap, record and extension forms. Exactly one preserves every admitted dependency and introduces no species lookup or measured value:

`{survivor_id(s)}`

Base: {s.induction_base}

Successor: {s.induction_step}

The resulting finite order has one least state, a gapless sequence of positive successor positions, complete pairwise comparability and a retained positive separation for every higher/lower pair. State identity and ELEC-003 molecular support remain bound throughout.

## CHECK

Before target release, the capability-closed Fold program seals the same least-plus-positive-successor law for all 22 molecular carriers. It has no target, filesystem, network, environment, clock, subprocess or foreign-function access. A distinct custodian then opens 306 byte-bound NIST Chemistry WebBook state-energy records in the common inverse-centimetre unit: 22 source-designated X states and 284 excited states.

The evaluator reproduces every exact decimal inscription as a rational measurement record, verifies one unique least X state for every species, verifies every excited-state gap is positive, constructs all 22 exact finite state orders, and checks 3,325 strict measured state pairs. Source quality markers—plain, bracketed, parenthesized or approximate—are retained. Explicit eV records were excluded before registration rather than mixed into the inverse-centimetre vector. Tied-ground, reversed-gap, omitted-row, mixed-unit and tampered-source controls reject.

External authority: NIST Chemistry WebBook SRD 69, DOI `10.18434/T4D303`. Measurements remain observations and never select the formal survivor.

## FALSIFICATION

{s.falsification_condition}
"""
def main():
 s=STATE_ENERGY_ORDER_SPEC;p=ROOT/"claims"/s.claim_id;write(p/"registration.json",json.dumps(claim_registration(),indent=2,sort_keys=True)+"\n");write(p/"execution.py",execution_source());write(p/"independent_validator.py",independent_source());write(p/"WHY_DERIVATION_CHECK.md",note());write(p/"STATUS.md",f"# {s.claim_id}\n\nStatus: `registered_observational_derivation`\n");e=ROOT/"experiments/chemistry"/s.experiment_id;write(e/"registration.json",json.dumps(experiment_registration(),indent=2,sort_keys=True)+"\n");print("scaffolded",s.claim_id)
if __name__=="__main__":main()
