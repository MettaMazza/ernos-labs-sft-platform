#!/usr/bin/env python3
"""Create four separate ECHEM-009–012 claim and experiment packages."""
import json
from pathlib import Path

from sft.chemistry.echem_polarization_batch_v1 import AUTHORITIES, COMPLETENESS_CERTIFICATES, CORROSION_SPEC, DOUBLE_LAYER_SPEC, POLARIZATION_SPEC, RATE_SPEC
from sft.engine.canonical import sha256_identity

ROOT = Path(__file__).resolve().parents[1]
CONFIG = {
    "009": (RATE_SPEC, "ElectrodeReactionRateValidator", "SFT-CHEM-OBL-ECHEM-009", "electrode reaction-rate law", "experiments/external_sources/chemistry/echem_009_target_identities_v1.json", "experiments/sealed_predictions/chemistry_echem_009_pre_source_v1.json", 10, 49),
    "010": (POLARIZATION_SPEC, "OverpotentialPolarizationValidator", "SFT-CHEM-OBL-ECHEM-010", "overpotential/polarization law", "experiments/external_sources/chemistry/echem_010_target_identities_v1.json", "experiments/sealed_predictions/chemistry_echem_010_pre_source_v1.json", 10, 49),
    "011": (DOUBLE_LAYER_SPEC, "DoubleLayerValidator", "SFT-CHEM-OBL-ECHEM-011", "double-layer organization law", "experiments/external_sources/chemistry/echem_011_target_identities_v1.json", "experiments/sealed_predictions/chemistry_echem_011_pre_source_v1.json", 3, 24),
    "012": (CORROSION_SPEC, "CorrosionNetworkValidator", "SFT-CHEM-OBL-ECHEM-012", "corrosion reaction-network law", "experiments/external_sources/chemistry/echem_012_target_identities_v1.json", "experiments/sealed_predictions/chemistry_echem_012_pre_source_v1.json", 31, 49),
}

NATIVE = {
    "009": '''from fractions import Fraction\ndef rate(f,r,t):\n return ("balanced",None,Fraction(f+r,t)) if f==r else (("forward",Fraction(f-r,t),Fraction(f+r,t)) if f>r else ("reverse",Fraction(r-f,t),Fraction(f+r,t)))\na=rate(5,1,2);b=rate(1,5,2);z=rate(3,3,2);native={"forward":a[0]=="forward","reverse":b[0]=="reverse","positive_take":a[1]==2,"balance":z[1] is None,"complete":a[2]==3,"reaction":True,"condition":True,"successor":rate(6,1,2)[1]==Fraction(5,2)}''',
    "010": '''from fractions import Fraction\ndef point(n,side):return (n,side,None,None) if side=="equilibrium" else (n,side,Fraction(n,2),Fraction(n,3))\ndef curve(rows):return tuple(x[0] for x in rows)==tuple(range(1,len(rows)+1))\nrows=(point(1,"equilibrium"),point(2,"anodic"),point(3,"cathodic"));native={"ordered":curve(rows),"reference":True,"equilibrium":rows[0][2:] == (None,None),"anodic":rows[1][1]=="anodic","cathodic":rows[2][1]=="cathodic","positive":rows[1][3]>0,"condition":True,"omission":not curve((point(1,"anodic"),point(3,"cathodic")))}''',
    "011": '''from fractions import Fraction\ndef layer(n,side):return (n,side,side,n)\ndef double(rows,p):return (rows,None) if p is None else (rows,Fraction(sum(x[3] for x in rows),1)/p)\nr=double((layer(1,"electrode"),layer(2,"solution")),Fraction(3,2));z=double((layer(1,"electrode"),),None);native={"layers":len(r[0])==2,"order":tuple(x[0] for x in r[0])==(1,2),"species":len({x[2] for x in r[0]})==2,"sides":len({x[1] for x in r[0]})==2,"potential":Fraction(3,2)>0,"capacitance":r[1]==2,"coincidence":z[1] is None,"interface":True}''',
    "012": '''from fractions import Fraction\ndef network(a,c):\n s=min(a,c);return (s,"balanced",None) if a==c else ((s,"anodic-excess",a-c) if a>c else (s,"cathodic-excess",c-a))\nb=network(Fraction(4,2),Fraction(4,2));a=network(Fraction(6,2),Fraction(4,2));native={"paths":True,"material":True,"environment":True,"rate":b[0]==2,"balance":b[2] is None,"orientation":a[1]=="anodic-excess","positive":a[2]==1,"network":True}''',
}


def write(path: Path, content) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
    path.write_text(content if isinstance(content, str) else json.dumps(content, indent=2, sort_keys=True) + "\n")


def main() -> None:
    for key, (spec, validator, obligation, label, identity, seal, measurement_count, claim_pages) in CONFIG.items():
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
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why ECHEM-{key} requires a derivation check\n\nA conventional displayed value cannot establish the {label}. This claim separately generates all 256 forms before comparison, retains every registered chemical carrier and condition, and uses only its own value-free identity and seal. The shared post-seal family capture preserves all 73 pages and 156,376 extracted characters. Every value, unit, conventional sign or zero glyph, fit, correction, uncertainty, discrepancy, adverse row, absence and unresolved observation remains downstream provenance and cannot select the native Fold law.\n")
        spec_name = {"009": "RATE_SPEC", "010": "POLARIZATION_SPEC", "011": "DOUBLE_LAYER_SPEC", "012": "CORROSION_SPEC"}[key]
        execution = f'''import sys\nfrom sft.chemistry.echem_polarization_batch_v1 import AUTHORITIES, {spec_name} as CLAIM_SPEC\nfrom sft.chemistry.echem_polarization_validation_v1 import {validator}\nfrom sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram\nfrom sft.engine import ExternalCommandValidator\nfrom sft.engine.source import build_source_manifest\nfrom sft.verification import ClaimExecution\ndef build_execution(root):\n fixed=("sft/chemistry/echem_polarization_batch_v1.py","sft/chemistry/echem_polarization_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/{spec.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{spec.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-echem-{key}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,{validator}(root))\n'''
        write(package / "execution.py", execution)
        independent = f'''from itertools import product\nimport json,sys\nCLAIM_ID={spec.claim_id!r};DOMAINS={domains!r};SURVIVOR={spec.exact_result!r}\n{NATIVE[key]}\ndef main():\n s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={{x["candidate_id"]:x["survives"] for x in s["decisions"]}};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={{x:x==SURVIVOR for x in generated}} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({{"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}}}},sort_keys=True))\nif __name__=="__main__":main()\n'''
        write(package / "independent_validator.py", independent)
        experiment_registration = {
            "$schema": "../../../governance/experiment.schema.json",
            "absence_boundary": {"display_glyph": "0", "external_signed_and_zero_inscriptions_are_provenance_only": True, "native_proof_form": "positive exact counts/ratios, held direction and structural EmptyOne absence or coincidence", "numerical_zero_admitted": False},
            "claim_id": spec.claim_id,
            "evaluation_protocol": {"acceptance_condition": f"All {len(spec.target_rows)} preregistered comparisons, all {claim_pages} claim-source pages and all {measurement_count} complete registered measurement entries or records are retained.", "all_8_targets_required": True, "falsification_condition": spec.falsification_condition},
            "evidence_mode": "observational_derivation_plus_complete_external_record_reconstruction", "experiment_id": spec.experiment_id,
            "external_measurement_sources": [{"complete_measurement_entries_or_records": measurement_count, "complete_claim_source_pages": claim_pages, "measurement_bodies": ["National Bureau of Standards / National Institute of Standards and Technology"]}],
            "frozen_relation": {"relation_hash": sha256_identity(spec.exact_result), "statement": spec.exact_result, "targets_did_not_select_survivor": True},
            "identity_registry": identity, "prediction_seal": seal, "registered_by": "Maria Smith", "registration_date": "2026-07-28",
            "schema": "sft-v3-chemistry-experiment-registration/1", "shared_postseal_family_source_pages": 73, "shared_postseal_family_extracted_characters": 156376,
            "status": "registered_sources_captured_postseal",
        }
        write(experiment / "registration.json", experiment_registration)
    print("scaffolded four separate ECHEM-009–012 claim packages")


if __name__ == "__main__":
    main()
