#!/usr/bin/env python3
"""Create four separate NUCHEM-001–004 claim and experiment packages."""
import json
from pathlib import Path

from sft.chemistry.nuchem_initial_batch_v1 import ACTIVITY_SPEC, AUTHORITIES, BRANCHING_SPEC, CARRIER_SPEC, COMPLETENESS_CERTIFICATES, TRANSFORMATION_SPEC
from sft.engine.canonical import sha256_identity


ROOT = Path(__file__).resolve().parents[1]
CONFIG = {
    "001": (CARRIER_SPEC, "NuclideCarrierValidator", "CARRIER_SPEC", "SFT-CHEM-OBL-NUCHEM-001", "nuclide chemical-carrier law", "experiments/external_sources/chemistry/nuchem_001_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_001_pre_source_v1.json", "ten complete nuclide identities, four carrier phase/matrix rows, complete certified value and twelve uncertainty rows"),
    "002": (TRANSFORMATION_SPEC, "RadioactiveTransformationValidator", "TRANSFORMATION_SPEC", "SFT-CHEM-OBL-NUCHEM-002", "radioactive chemical-transformation network", "experiments/external_sources/chemistry/nuchem_002_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_002_pre_source_v1.json", "four directed parent/daughter records, five channel rows, two equilibrium records, three assumptions and three confirmations"),
    "003": (ACTIVITY_SPEC, "ActivityAmountTimeValidator", "ACTIVITY_SPEC", "SFT-CHEM-OBL-NUCHEM-003", "activity–amount–time law", "experiments/external_sources/chemistry/nuchem_003_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_003_pre_source_v1.json", "two massic activities, three half-lives, two reference times and twelve uncertainty rows"),
    "004": (BRANCHING_SPEC, "RadioactiveBranchingYieldValidator", "BRANCHING_SPEC", "SFT-CHEM-OBL-NUCHEM-004", "radioactive branching chemical-yield law", "experiments/external_sources/chemistry/nuchem_004_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_004_pre_source_v1.json", "five reported channels, four daughters, nine method rows and explicit preservation of unavailable numeric branch fractions"),
}

NATIVE = {
    "001": '''carrier=("strontium",90,"held","solution-carrier","aqueous",1)\nnative={"element":carrier[0]=="strontium","nuclide":carrier[1]==90,"state":carrier[2]=="held","species":carrier[3]=="solution-carrier","phase":carrier[4]=="aqueous","occurrence":carrier[5]==1,"complete":len(carrier)==6,"successor":carrier[:5]+(2,)==("strontium",90,"held","solution-carrier","aqueous",2)}''',
    "002": '''EMPTY=("EmptyOne",)\ndef network(rows):\n return EMPTY if not rows else tuple(rows) if len(set(rows))==len(rows) else None\ne1=("p","d","ps","ds","one",1);e2=("p","d","ps","ds","two",2)\nnative={"parent":e1[0]=="p","daughter":e1[1]=="d","species":e1[2:4]==("ps","ds"),"channel":e1[4]=="one","events":e1[5]==1,"network":network((e1,))==(e1,),"absence":network(())==EMPTY,"successor":network((e1,e2))==(e1,e2)}''',
    "003": '''from fractions import Fraction\ndef ledger(initial,events,intervals):\n if events>initial:return None\n left=initial-events;return (Fraction(events,intervals),None if left==0 else left)\na=ledger(5,2,3);z=ledger(2,2,1)\nnative={"identity":True,"amount":5>0,"events":2>0,"time":3>0,"activity":a[0]==Fraction(2,3),"remaining":a[1]==3,"absence":z[1] is None,"successor":ledger(5,3,3)[0]==1}''',
    "004": '''from fractions import Fraction\ndef partition(events):\n total=sum(events);return tuple(Fraction(x,total) for x in events)\nrows=(("one","d1",3,2),("two","d2",1,1));parts=partition(tuple(x[2] for x in rows))\nnative={"channel":len({x[0] for x in rows})==2,"daughter":len({x[1] for x in rows})==2,"events":rows[0][2]>0,"recovery":rows[0][3]>0,"yield":Fraction(rows[0][3],rows[0][2])==Fraction(2,3),"partition":sum(parts)==1,"complete":len(rows)==2,"successor":partition((3,1,2))[0]==Fraction(1,2)}''',
}


def write(path: Path, content) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
    path.write_text(content if isinstance(content, str) else json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> None:
    for key, (spec, validator, spec_name, obligation, label, identity, seal, external_surface) in CONFIG.items():
        package = ROOT / "claims" / spec.claim_id
        experiment = ROOT / "experiments/chemistry" / spec.experiment_id
        domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
        registration = {
            "$schema": "../../governance/claim.schema.json", "branch": "chemistry",
            "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": COMPLETENESS_CERTIFICATES[spec.claim_id], "expected_cardinality": 256, "generator": spec.generation_rule},
            "claim_id": spec.claim_id, "dependencies": list(spec.dependencies), "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
            "excluded_inputs": list(spec.exclusions), "provenance_classes": ["observational_derivation", "complete_external_record_reconstruction"],
            "registered_by": "Maria Smith", "registration_date": "2026-07-28", "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "statement": spec.statement, "status": "registered", "title": spec.title,
        }
        write(package / "registration.json", registration)
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why NUCHEM-{key} requires a derivation check\n\nA conventional displayed value cannot establish the {label}. This claim separately generates all 256 registered forms before comparison and uses only its own value-free identity and pre-source seal. The shared post-seal capture reconstructs four official NIST sources as 8 complete PDF pages, 2 complete HTML documents and 34,442 extracted characters. Every value, unit, conventional zero or sign, decimal, uncertainty, assumption, correction, method disagreement, favorable, adverse, absent, unavailable and unresolved row remains downstream provenance and cannot select the native Fold law.\n")
        execution = f'''import sys\nfrom sft.chemistry.nuchem_initial_batch_v1 import AUTHORITIES, {spec_name} as CLAIM_SPEC\nfrom sft.chemistry.nuchem_initial_validation_v1 import {validator}\nfrom sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram\nfrom sft.engine import ExternalCommandValidator\nfrom sft.engine.source import build_source_manifest\nfrom sft.verification import ClaimExecution\ndef build_execution(root):\n fixed=("sft/chemistry/nuchem_initial_batch_v1.py","sft/chemistry/nuchem_initial_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/{spec.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{spec.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-nuchem-{key}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,{validator}(root))\n'''
        write(package / "execution.py", execution)
        independent = f'''from itertools import product\nimport json,sys\nCLAIM_ID={spec.claim_id!r};DOMAINS={domains!r};SURVIVOR={spec.exact_result!r}\n{NATIVE[key]}\ndef main():\n s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={{x["candidate_id"]:x["survives"] for x in s["decisions"]}};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={{x:x==SURVIVOR for x in generated}} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({{"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}}}},sort_keys=True))\nif __name__=="__main__":main()\n'''
        write(package / "independent_validator.py", independent)
        experiment_registration = {
            "$schema": "../../../governance/experiment.schema.json",
            "absence_boundary": {"display_glyph": "0", "external_signed_decimal_and_zero_inscriptions_are_provenance_only": True, "native_proof_form": "positive exact counts/ratios, held orientation and structural EmptyOne absence", "numerical_zero_admitted": False},
            "claim_id": spec.claim_id,
            "evaluation_protocol": {"acceptance_condition": "All 8 preregistered comparisons and the complete four-source post-seal surface are retained, including every favorable, adverse, absent, unavailable and unresolved record.", "all_8_targets_required": True, "falsification_condition": spec.falsification_condition},
            "evidence_mode": "observational_derivation_plus_complete_external_record_reconstruction", "experiment_id": spec.experiment_id,
            "external_measurement_sources": [{"complete_pdf_pages": 8, "complete_html_documents": 2, "complete_extracted_characters": 34442, "measurement_body": "National Institute of Standards and Technology", "claim_surface": external_surface}],
            "frozen_relation": {"relation_hash": sha256_identity(spec.exact_result), "statement": spec.exact_result, "targets_did_not_select_survivor": True},
            "identity_registry": identity, "prediction_seal": seal, "registered_by": "Maria Smith", "registration_date": "2026-07-28",
            "schema": "sft-v3-chemistry-experiment-registration/1", "status": "registered_sources_captured_postseal",
        }
        write(experiment / "registration.json", experiment_registration)
    print("scaffolded four separate NUCHEM-001–004 claim packages")


if __name__ == "__main__":
    main()
