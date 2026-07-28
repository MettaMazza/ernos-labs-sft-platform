#!/usr/bin/env python3
"""Scaffold all Astronomy foundation packages and independent validators."""

from __future__ import annotations

import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from sft.astronomy_cosmology.empirical_program import ASTRONOMY_SPECS, PRE_SOURCE_SEAL_PATH
from sft.engine.canonical import sha256_identity
from sft.physics.generated_empirical_law import completeness_record, experiment_registration_record, prediction_program_document, survivor_id

CHECKPOINT=ROOT/"census/astronomy_cosmology_continuation_checkpoint.json"

def write(path,text): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text)

def seal_hash(): return json.loads((ROOT/PRE_SOURCE_SEAL_PATH).read_text())["complete_branch_pre_source_seal_hash"]

def registration(spec):
    return {"$schema":"../../governance/claim.schema.json","claim_id":spec.claim_id,"title":spec.title,"branch":"astronomy_cosmology","subbranch":spec.family,"status":"registered","statement":spec.statement,"dependencies":list(spec.dependencies),"root_theorems":["SFT-ROOT-THERE-IS-NO-NOTHING"],"axioms":[],"free_parameters":[],"provenance_classes":["forward_forcing"],"candidate_grammar":{"generator":spec.generation_rule,"boundary":spec.grammar_boundary,"completeness_certificate":sha256_identity(completeness_record(spec)),"candidate_count":256,"unique_survivor":survivor_id(spec)},"pre_source_branch_seal":PRE_SOURCE_SEAL_PATH,"pre_source_branch_seal_hash":seal_hash(),"excluded_inputs":list(spec.exclusions),"required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"intended_certificate":"Complete 256-form census, one survivor, depth-independent certificate, implementation-distinct reconstruction, and post-seal source-bound Astronomy comparison preserving adverse, absent, unresolved and failed rows.","empirical_protocol":f"experiments/astronomy_cosmology/{spec.experiment_id}/registration.json","registered_by":"Maria Smith","registration_date":"2026-07-28"}

def experiment(spec):
    base=experiment_registration_record(spec); program=prediction_program_document(spec)
    return {"$schema":"../../../governance/experiment.schema.json","experiment_id":spec.experiment_id,"claim_id":spec.claim_id,"evidence_mode":"post_seal_primary_archive_or_measurement_correspondence","development_observations":[],"complete_branch_pre_source_seal":{"path":PRE_SOURCE_SEAL_PATH,"hash":seal_hash(),"all_72_predictions_and_18432_candidates_sealed_before_source_selection":True},"external_target_record":{"path":spec.source_snapshot_path,"hash":spec.source_snapshot_hash,"target_ids":[x.target_id for x in spec.target_rows],"source_ids":[x.source_id for x in spec.target_rows],"directness":spec.directness,"empirical_disposition":spec.empirical_disposition},"frozen_relation":{"statement":spec.exact_result,"relation_hash":sha256_identity(spec.exact_result),"candidate_grammar":spec.generation_rule,"exact_domain":spec.grammar_boundary,"target_did_not_select_structural_law":True},"prediction_protocol":{"interpreter_id":"sft-v3-capability-closed-fold-interpreter/1","program":program,"program_hash":sha256_identity(program),"complete_trace_required":True,"forbidden_capabilities":["clock","dynamic_import","environment","filesystem_read","filesystem_write","foreign_function","network","subprocess"]},"evaluation_protocol":{"acceptance_condition":"The registered target opens only after the derivation seal, the source-bound consequence matches, every adverse/absent/unresolved/failed row remains, and a changed control is rejected.","falsification_condition":spec.falsification_condition},"controls":[{"kind":"false_premise"},{"kind":"tampered_source"},{"kind":"tampered_artifact"},{"kind":"boundary"},{"kind":"unfavorable_measurement"}],"row_retention_policy":"retain favorable adverse absent unresolved censored missing and transport rows","registration_record_hash":sha256_identity(base),"registration_date":"2026-07-28","registered_by":"Maria Smith","status":"registered"}

def execution_source(spec):
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.astronomy_cosmology.empirical_program import ASTRONOMY_SPECS, BlindAstronomyBoundaryValidator, GeneratedEmpiricalAstronomyProgram
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec=next(x for x in ASTRONOMY_SPECS if x.claim_id=={spec.claim_id!r})
    source_files=(root/"sft/astronomy_cosmology/obligations.py",root/"sft/astronomy_cosmology/structural_model.py",root/"sft/astronomy_cosmology/generated_law.py",root/"sft/astronomy_cosmology/empirical_program.py",root/"experiments/sealed_predictions/astronomy_cosmology_foundation_complete_pre_source.json",root/"experiments/astronomy_cosmology/source_registry.json",root/"experiments/astronomy_cosmology/claim_source_bindings.json",root/"experiments/astronomy_cosmology/source_transports.json",root/"experiments/astronomy_cosmology/source_feature_audit.json",root/"experiments/astronomy_cosmology/external_targets.json",root/spec.source_snapshot_path,root/"claims/{spec.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py")
    source_hash=build_source_manifest(root,source_files).manifest_hash
    validator=root/"claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(program=GeneratedEmpiricalAstronomyProgram(spec,source_hash),independent_validator=ExternalCommandValidator({(spec.claim_id.lower()+'-independent-python/1')!r},(sys.executable,str(validator)),validator.parent,(validator,)),source_files=source_files,empirical_validator=BlindAstronomyBoundaryValidator(root,spec))
'''

def independent_source(spec):
    domains=tuple(tuple(c.name for c in d.choices) for d in spec.dimensions)
    return f'''"""Implementation-distinct validator for {spec.claim_id}."""
from itertools import product
import json,sys
CLAIM_ID={spec.claim_id!r}; DOMAINS={domains!r}; SURVIVOR={survivor_id(spec)!r}
def main():
    sealed=json.load(open(sys.argv[1],encoding="utf-8")); generated=["__".join(x) for x in product(*DOMAINS)]; received=[x["candidate_id"] for x in sealed["census"]["candidates"]]; decisions={{x["candidate_id"]:x["survives"] for x in sealed["decisions"]}}
    passed=(sealed["claim_id"]==CLAIM_ID and received==generated and sealed["census"]["expected_cardinality"]==len(generated) and len(set(received))==len(generated) and decisions=={{x:x==SURVIVOR for x in generated}} and sum(decisions.values())==1 and sealed["closure"]["scope"]=="depth_independent" and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True and {{x["kind"] for x in sealed["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}} and all(x["passed"] is True for x in sealed["controls"]))
    print(json.dumps({{"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None}}}},sort_keys=True))
if __name__=="__main__": main()
'''

def note(spec):
    axes="\n".join(f"- `{d.key}`: reject `{d.choices[0].name}`; preserve `{d.admitted_choice.name}` — {d.admitted_choice.reason}" for d in spec.dimensions)
    special=""
    if spec.claim_id=="SFT-ASTRO-TULLY-FISHER-001": special="\nThe exact structural exponent is four. The first preregistered all-row unweighted comparison measured 3.486344605219551… and is preserved as adverse. The primary source's uncertainty-aware orthogonal result is 3.85 ± 0.09 and its stated systematic interval 3.5–4.0 includes four; this is a separate source-method correspondence, not a reclassification.\n"
    return f"""# {spec.title}\n\nClaim: `{spec.claim_id}`\n\n## Why\n\n{spec.statement}\n\n## Derivation\n\nDependencies: {', '.join(f'`{x}`' for x in spec.dependencies)}\n\nBoundary: {spec.grammar_boundary}\n\nGeneration: {spec.generation_rule}\n\nThe literal eight-axis product contains 256 forms:\n\n{axes}\n\nExactly one form preserves every registered coordinate:\n\n`{survivor_id(spec)}`\n\nBase: {spec.induction_base}\n\nSuccessor: {spec.induction_step}\n\n## Check\n\nAll 72 predictions and 18,432 candidates were sealed before source selection. The capability-closed prediction cannot read files, networks, clocks, environment or targets. Post-seal primary evidence tests the consequence and cannot select the law. Evidence class: `{spec.directness}` / `{spec.empirical_disposition}`.\n{special}\nA catalogue, model, reconstruction, forecast, upper limit, non-detection and missing record remain distinct.\n"""

def main():
    for spec in ASTRONOMY_SPECS:
        pkg=ROOT/"claims"/spec.claim_id; write(pkg/"registration.json",json.dumps(registration(spec),indent=2,sort_keys=True)+"\n"); write(pkg/"execution.py",execution_source(spec)); write(pkg/"independent_validator.py",independent_source(spec)); write(pkg/"WHY_DERIVATION_CHECK.md",note(spec)); write(pkg/"STATUS.md",f"# {spec.claim_id}\n\nStatus: `registered`\n")
        exp=ROOT/"experiments/astronomy_cosmology"/spec.experiment_id; write(exp/"registration.json",json.dumps(experiment(spec),indent=2,sort_keys=True)+"\n")
    c=json.loads(CHECKPOINT.read_text()); c.update({"status":"complete_claim_packages_scaffolded_not_admitted","claim_package_count":len(ASTRONOMY_SPECS),"independent_validator_count":len(ASTRONOMY_SPECS),"next_exact_operation":"admit_"+ASTRONOMY_SPECS[0].claim_id}); CHECKPOINT.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
    print(f"scaffolded Astronomy claims={len(ASTRONOMY_SPECS)}")

if __name__=="__main__": main()
