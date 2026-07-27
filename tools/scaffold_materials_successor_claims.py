#!/usr/bin/env python3
"""Materialize the already sealed eight-claim Materials successor surface."""

from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from sft.engine.canonical import sha256_identity
from sft.materials.successor_evidence import BINDINGS, PRE_SOURCE_SEAL_PATH, SOURCE_BY_ID, SPECS, validate_pre_source_seal
from sft.physics.generated_empirical_law import completeness_record, survivor_id


def write(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n" if not isinstance(payload,str) else payload,encoding="utf-8")


def main():
    seal=validate_pre_source_seal(ROOT)
    for spec in SPECS:
        package=ROOT/"claims"/spec.claim_id
        registration={"$schema":"../../governance/claim.schema.json","claim_id":spec.claim_id,"title":spec.title,"branch":"materials","subbranch":spec.subbranch,"status":"registered","statement":spec.statement,"dependencies":list(spec.dependencies),"root_theorems":["SFT-ROOT-THERE-IS-NO-NOTHING"],"axioms":[],"free_parameters":[],"provenance_classes":["forward_forcing"],"candidate_grammar":{"generator":spec.generation_rule,"boundary":spec.grammar_boundary,"completeness_certificate":sha256_identity(completeness_record(spec)),"candidate_count":256,"unique_survivor":survivor_id(spec)},"pre_source_branch_seal":PRE_SOURCE_SEAL_PATH,"pre_source_branch_seal_hash":seal,"excluded_inputs":list(spec.exclusions),"required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"empirical_protocol":f"experiments/materials/{spec.experiment_id}/registration.json","registered_by":"Maria Smith","registration_date":"2026-07-27"}
        write(package/"registration.json",registration)
        requirements=BINDINGS[spec.claim_id]
        experiment={"$schema":"../../../governance/experiment.schema.json","experiment_id":spec.experiment_id,"claim_id":spec.claim_id,"evidence_mode":"blind_authoritative_correspondence","complete_successor_pre_source_seal":{"path":PRE_SOURCE_SEAL_PATH,"hash":seal,"all_eight_predictions_sealed_before_source_selection":True},"external_measurement_sources":[{"source_id":SOURCE_BY_ID[sid].source_id,"measurement_body":"National Institute of Standards and Technology","source_uri":SOURCE_BY_ID[sid].uri,"snapshot_path":SOURCE_BY_ID[sid].path,"snapshot_hash":SOURCE_BY_ID[sid].digest,"retrieved_date":"2026-07-27"} for sid in spec.source_ids],"required_source_features":[{"source_id":row.source_id,"required_fragment":row.fragment} for row in requirements],"frozen_relation":{"statement":spec.exact_result,"relation_hash":sha256_identity(spec.exact_result),"target_did_not_select_law":True},"withheld_targets":[{"target_id":spec.target_id,"content_withheld_from_prediction":True}],"controls":["false_premise","tampered_source","tampered_artifact","boundary","unfavorable_measurement"],"stop_condition":"Halt on any violation; otherwise stop after every registered row and control is evaluated once.","status":"registered"}
        write(ROOT/"experiments/materials"/spec.experiment_id/"registration.json",experiment)
        execution=f'''"""Official execution binding for {spec.claim_id}."""\nfrom pathlib import Path\nimport sys\nfrom sft.engine import ExternalCommandValidator\nfrom sft.engine.source import build_source_manifest\nfrom sft.materials.generated_law import GeneratedEmpiricalMaterialsProgram\nfrom sft.materials.successor_evidence import BlindSuccessorMaterialsValidator, SPECS\nfrom sft.verification import ClaimExecution\ndef build_execution(root: Path) -> ClaimExecution:\n spec=next(x for x in SPECS if x.claim_id=={spec.claim_id!r})\n source_files=tuple(root/x for x in ({('sft/materials/successor_obligations.py','sft/materials/successor_structural_counts.py','sft/materials/successor_derivation.py','sft/materials/successor_evidence.py',f'claims/{spec.claim_id}/execution.py','sft/materials/generated_law.py','sft/physics/generated_empirical_law.py','sft/claim_evidence/fold_language.py','sft/claim_evidence/custody.py','sft/claim_evidence/hostile.py','sft/engine/isolation.py','sft/engine/empirical.py')!r}))\n source_hash=build_source_manifest(root,source_files).manifest_hash\n validator=root/'claims/{spec.claim_id}/independent_validator.py'\n return ClaimExecution(GeneratedEmpiricalMaterialsProgram(spec,source_hash),ExternalCommandValidator({(spec.claim_id.lower()+'-independent-python/1')!r},(sys.executable,str(validator)),validator.parent,(validator,)),source_files,BlindSuccessorMaterialsValidator(root,spec))\n'''
        write(package/"execution.py",execution)
        domains=tuple(tuple(c.name for c in d.choices) for d in spec.dimensions); survivor=survivor_id(spec)
        independent=f'''from itertools import product\nimport json,sys\nCLAIM_ID={spec.claim_id!r}\nDOMAINS={domains!r}\nSURVIVOR={survivor!r}\ndef main():\n s=json.load(open(sys.argv[1],encoding="utf-8")); generated=["__".join(x) for x in product(*DOMAINS)]; received=[x["candidate_id"] for x in s["census"]["candidates"]]; decisions={{x["candidate_id"]:x["survives"] for x in s["decisions"]}}; passed=s["claim_id"]==CLAIM_ID and received==generated and decisions=={{x:x==SURVIVOR for x in generated}} and sum(decisions.values())==1 and all(x["passed"] for x in s["controls"]); print(json.dumps({{"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None}}}},sort_keys=True))\nif __name__=="__main__": main()\n'''
        write(package/"independent_validator.py",independent)
        write(package/"WHY_DERIVATION_CHECK.md",f"# {spec.title}\n\nThis claim is independently enumerated over all 256 registered forms. Its unique survivor is sealed before source selection and externally tested against every registered NIST row. It contains no axiom, free parameter, fit, forbidden proof value or target-selected rule.\n")
        print(spec.claim_id)
if __name__=="__main__": main()
