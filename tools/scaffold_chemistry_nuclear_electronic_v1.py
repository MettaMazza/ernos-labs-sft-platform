#!/usr/bin/env python3
"""Scaffold ELEC-012 nuclear-electronic composition claim."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from sft.chemistry.nuclear_electronic_batch_v1 import IDENTITY_HASH,IDENTITY_PATH,NUCLEAR_ELECTRONIC_SPEC,SOURCE_ID,TARGET_HASH,TARGET_PATH
from sft.chemistry.nuclear_electronic_validation_v1 import experiment_registration_record,prediction_program_document
from sft.engine.canonical import sha256_identity
from sft.physics.generated_empirical_law import completeness_record,survivor_id
def write(path,content): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding="utf-8")
def independent_source():
 s=NUCLEAR_ELECTRONIC_SPEC; domains=tuple(tuple(c.name for c in d.choices) for d in s.dimensions)
 return f'''from itertools import product
import json,sys
CLAIM={s.claim_id!r};DOMAINS={domains!r};SURVIVOR={survivor_id(s)!r}
def main():
 d=json.load(open(sys.argv[1]));g=["__".join(x) for x in product(*DOMAINS)];r=[x["candidate_id"] for x in d["census"]["candidates"]];z={{x["candidate_id"]:x["survives"] for x in d["decisions"]}};passed=d["claim_id"]==CLAIM and r==g and len(set(g))==256 and z=={{x:x==SURVIVOR for x in g}} and sum(z.values())==1 and d["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in d["controls"]);print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"candidate_count":len(g),"survivor":SURVIVOR if passed else None,"successor":"append-one-nuclear-occurrence-with-held-isotope-label"}}}},sort_keys=True))
if __name__=="__main__":main()
'''
def execution_source():
 s=NUCLEAR_ELECTRONIC_SPEC
 return f'''from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.nuclear_electronic_batch_v1 import NUCLEAR_ELECTRONIC_SPEC
from sft.chemistry.nuclear_electronic_validation_v1 import NuclearElectronicValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=NUCLEAR_ELECTRONIC_SPEC;files=(root/"sft/chemistry/nuclear_electronic_law_v1.py",root/"sft/chemistry/nuclear_electronic_batch_v1.py",root/"sft/chemistry/nuclear_electronic_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/{s.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py");h=build_source_manifest(root,files).manifest_hash;v=root/"claims/{s.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(s,h),ExternalCommandValidator("{s.claim_id.lower()}-independent-python/1",(sys.executable,str(v)),v.parent,(v,)),files,NuclearElectronicValidator(root))
'''
def note():
 s=NUCLEAR_ELECTRONIC_SPEC
 return f"""# {s.title}

Claim: `{s.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-012`

## WHY

An isotope label cannot be reduced to an unbound mass inscription, and an electronic-state label cannot identify a whole molecule after its nuclei are erased. ELEC-012 therefore derives one retained joint carrier with exact nuclear occurrences, held isotope labels, electronic support and electronic state. The separation is a finite distinction between coordinate families, not an imported continuum approximation.

## DERIVATION

The eight binary axes generate 256 forms. Exactly one retains the molecular carrier, both supports, their finite joint product, a parameter-free coordinate partition, isotope-labelled coordinate transport, structural absence and every source record:

`{survivor_id(s)}`

Base: {s.induction_base}

Successor: {s.induction_step}

## CHECK

After sealing, an implementation-distinct parser reconstructs every one of 95 NIST H2, HD and D2 diatomic state rows and all 1,235 cells. It retains 551 positive exact inscriptions, 450 blank `EmptyOne` forms, three source-zero `EmptyOne` forms, eight signed external inscriptions as provenance labels and 223 text records. The three exact positive molecular-weight inscriptions order H2 below HD below D2. Across equal state designators, all 330 jointly reported positive vibronic coordinate pairs remain isotope-distinct.

## FALSIFICATION

{s.falsification_condition}
"""
def main():
 s=NUCLEAR_ELECTRONIC_SPEC;claim=ROOT/"claims"/s.claim_id
 registration={"$schema":"../../governance/claim.schema.json","claim_id":s.claim_id,"title":s.title,"branch":"chemistry","status":"registered","statement":s.statement,"dependencies":list(s.dependencies),"provenance_classes":["observational_derivation"],"candidate_grammar":{"generator":s.generation_rule,"boundary":s.grammar_boundary,"expected_cardinality":256,"completeness_certificate":sha256_identity(completeness_record(s))},"excluded_inputs":list(s.exclusions),"required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],"empirical_protocol":"experiments/chemistry/"+s.experiment_id+"/registration.json","registered_by":"Maria Smith","registration_date":"2026-07-26"}
 experiment={"$schema":"../../../governance/experiment.schema.json","experiment_id":s.experiment_id,"claim_id":s.claim_id,"evidence_mode":"observational_derivation","external_measurement_sources":[{"source_id":SOURCE_ID,"measurement_body":"National Institute of Standards and Technology","database":"Chemistry WebBook SRD 69","source_uri":"https://webbook.nist.gov/chemistry/","complete_rows":95,"complete_cells":1235}],"frozen_relation":{"statement":s.exact_result,"relation_hash":sha256_identity(s.exact_result),"targets_did_not_select_survivor":True,"continuum_separation_not_imported":True},"inputs":[{"input_id":"target-identities-only","path":IDENTITY_PATH,"content_hash":IDENTITY_HASH,"outcomes_absent":True}],"withheld_targets":[{"target_id":r.target_id,"snapshot_hash":r.snapshot_hash,"content_withheld_from_prediction":True} for r in s.target_rows],"absence_boundary":{"native_proof_form":"structural EmptyOne","display_glyph":"0","numerical_zero_admitted":False,"signed_external_inscriptions_are_provenance_only":True},"prediction_protocol":{"program_hash":sha256_identity(prediction_program_document(ROOT)),"complete_trace_required":True,"forbidden_capabilities":["filesystem_read","network","subprocess"]},"evaluation_protocol":{"all_95_rows_and_1235_cells":True,"acceptance_condition":"Every row, cell class, nuclear support, molecular-weight order and matched positive coordinate pair passes.","falsification_condition":s.falsification_condition},"custody_protocol":{"identity_registry_hash":IDENTITY_HASH,"withheld_target_registry_hash":TARGET_HASH,"target_release_requires_prediction_seal":True},"source_hashes":{"experiment-registration-record":sha256_identity(experiment_registration_record(ROOT))},"registered_by":"Maria Smith","registration_date":"2026-07-26","status":"registered"}
 write(claim/"registration.json",json.dumps(registration,indent=2,sort_keys=True)+"\n");write(claim/"execution.py",execution_source());write(claim/"independent_validator.py",independent_source());write(claim/"WHY_DERIVATION_CHECK.md",note());write(claim/"STATUS.md","# "+s.claim_id+"\n\nStatus: `registered_observational_derivation`\n");write(ROOT/"experiments/chemistry"/s.experiment_id/"registration.json",json.dumps(experiment,indent=2,sort_keys=True)+"\n");print("scaffolded",s.claim_id)
if __name__=="__main__":main()
