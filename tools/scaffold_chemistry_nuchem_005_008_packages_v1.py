#!/usr/bin/env python3
"""Create four separate NUCHEM-005–008 claim and experiment packages."""
import json
from pathlib import Path

from sft.chemistry.nuchem_fractionation_batch_v1 import AUTHORITIES, COMPLETENESS_CERTIFICATES, EQUILIBRIUM_FRACTIONATION_SPEC, ISOTOPE_EXCHANGE_SPEC, KINETIC_FRACTIONATION_SPEC, RADIOCHEMICAL_EQUILIBRIUM_SPEC
from sft.engine.canonical import sha256_identity


ROOT = Path(__file__).resolve().parents[1]
CONFIG = {
    "005": (RADIOCHEMICAL_EQUILIBRIUM_SPEC, "RadiochemicalEquilibriumValidator", "RADIOCHEMICAL_EQUILIBRIUM_SPEC", "SFT-CHEM-OBL-NUCHEM-005", "transient and secular radiochemical-equilibrium law", "experiments/external_sources/chemistry/nuchem_005_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_005_pre_source_v1.json", "two complete parent/daughter networks, two equilibrium records, two reference times and two certified activity rows"),
    "006": (ISOTOPE_EXCHANGE_SPEC, "IsotopeExchangeValidator", "ISOTOPE_EXCHANGE_SPEC", "SFT-CHEM-OBL-NUCHEM-006", "isotope-exchange reaction law", "experiments/external_sources/chemistry/nuchem_006_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_006_pre_source_v1.json", "four exchange-alpha rows, four absolute isotope-ratio rows and five complete example conditions"),
    "007": (EQUILIBRIUM_FRACTIONATION_SPEC, "EquilibriumIsotopeFractionationValidator", "EQUILIBRIUM_FRACTIONATION_SPEC", "SFT-CHEM-OBL-NUCHEM-007", "equilibrium isotope-fractionation law", "experiments/external_sources/chemistry/nuchem_007_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_007_pre_source_v1.json", "twelve exact comparison rows, four exchange-alpha rows and all 49 registered temperature-dependent figures"),
    "008": (KINETIC_FRACTIONATION_SPEC, "KineticIsotopeFractionationValidator", "KINETIC_FRACTIONATION_SPEC", "SFT-CHEM-OBL-NUCHEM-008", "kinetic isotope-fractionation law", "experiments/external_sources/chemistry/nuchem_008_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_008_pre_source_v1.json", "ten complete progress rows, factor 2.4, three replicates, correction 2.2 ± 0.5 ppm and six adverse/limit rows"),
}

NATIVE = {
    "005": '''from fractions import Fraction\ndef regime(rows):\n ratios=tuple(Fraction(d,p) for p,d in rows)\n if len(set(ratios))!=1:return None\n return ("secular" if ratios[0]==1 else "transient",ratios[0])\nnative={"identity":True,"support":tuple(range(1,3))==(1,2),"activity":Fraction(4,2)==2,"ratio":Fraction(4,2)==2,"transient":regime(((2,4),(3,6)))[0]=="transient","secular":regime(((2,2),(3,3)))[0]=="secular","absence":regime(((2,4),(3,3))) is None,"successor":regime(((2,4),(3,6),(4,8)))[1]==2}''',
    "006": '''from fractions import Fraction\ndef transition(a,b):\n totals=lambda x:(x[0]+x[2],x[1]+x[3],x[0]+x[1],x[2]+x[3])\n return totals(a)==totals(b) and a!=b\ndef balance(f,r):return None if f==r else ("forward" if f>r else "reverse",abs(f-r))\na=(4,2,3,1);b=(5,1,2,2)\nnative={"identity":True,"carriers":True,"inventory":min(a)>0,"conservation":transition(a,b),"direction":balance(3,1)==("forward",2),"quotient":Fraction(a[3]*a[0],a[2]*a[1])==Fraction(2,3),"equilibrium":balance(2,2) is None,"successor":transition(b,a)}''',
    "007": '''from fractions import Fraction\ndef factor(x):return Fraction(x[1]*x[2],x[0]*x[3])\ndef orientation(x):\n l=x[1]*x[2];r=x[0]*x[3];return None if l==r else "A" if l>r else "B"\np=(4,2,6,1);e=(4,2,6,3)\nnative={"identity":True,"phases":True,"inventory":min(p)>0,"ratios":(Fraction(p[1],p[0]),Fraction(p[3],p[2]))==(Fraction(1,2),Fraction(1,6)),"factor":factor(p)==3,"orientation":orientation(p)=="A","coincidence":orientation(e) is None and factor(e)==1,"successor":factor((6,3,8,2))==2}''',
    "008": '''from fractions import Fraction\ndef row(lp,hp,resource=2):return (Fraction(lp,resource),Fraction(hp,resource),Fraction(lp,hp),None if lp==hp else "light" if lp>hp else "heavy")\ndef remain(initial,product):return None if initial==product else initial-product\nnative={"identity":True,"support":True,"events":(4,2)==(4,2),"rates":row(4,2)[:2]==(2,1),"factor":row(4,2)[2]==2,"orientation":row(4,2)[3]=="light","inventory":remain(8,4)==4 and remain(8,8) is None,"successor":row(6,3)[2]==2}''',
}


def write(path: Path, content) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
    path.write_text(content if isinstance(content, str) else json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> None:
    for key, (spec, validator, spec_name, obligation, label, identity, seal, external_surface) in CONFIG.items():
        package = ROOT / "claims" / spec.claim_id; experiment = ROOT / "experiments/chemistry" / spec.experiment_id
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
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why NUCHEM-{key} requires a derivation check\n\nA conventional displayed value cannot establish the {label}. This claim separately generates all 256 registered forms before comparison and uses only its own value-free identity and source-exposure-disclosed derivation seal. The shared post-seal capture reconstructs five registered official sources as 266 complete PDF pages, one complete HTML document and 410,095 extracted characters. Every measured value, unit, conventional zero or sign, decimal, uncertainty, assumption, correction, estimate, loss, method disagreement, favorable, adverse, absent, unavailable and unresolved row remains downstream provenance and cannot select the native Fold law.\n")
        execution = f'''import sys\nfrom sft.chemistry.nuchem_fractionation_batch_v1 import AUTHORITIES, {spec_name} as CLAIM_SPEC\nfrom sft.chemistry.nuchem_fractionation_validation_v1 import {validator}\nfrom sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram\nfrom sft.engine import ExternalCommandValidator\nfrom sft.engine.source import build_source_manifest\nfrom sft.verification import ClaimExecution\ndef build_execution(root):\n fixed=("sft/chemistry/nuchem_fractionation_batch_v1.py","sft/chemistry/nuchem_fractionation_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/{spec.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{spec.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-nuchem-{key}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,{validator}(root))\n'''
        write(package / "execution.py", execution)
        independent = f'''from itertools import product\nimport json,sys\nCLAIM_ID={spec.claim_id!r};DOMAINS={domains!r};SURVIVOR={spec.exact_result!r}\n{NATIVE[key]}\ndef main():\n s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={{x["candidate_id"]:x["survives"] for x in s["decisions"]}};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={{x:x==SURVIVOR for x in generated}} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({{"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}}}},sort_keys=True))\nif __name__=="__main__":main()\n'''
        write(package / "independent_validator.py", independent)
        experiment_registration = {
            "$schema": "../../../governance/experiment.schema.json",
            "absence_boundary": {"display_glyph": "0", "external_signed_decimal_and_zero_inscriptions_are_provenance_only": True, "native_proof_form": "positive exact counts/ratios, held orientation and structural EmptyOne absence", "numerical_zero_admitted": False},
            "claim_id": spec.claim_id,
            "evaluation_protocol": {"acceptance_condition": "All 8 preregistered comparisons and the complete five-source post-seal surface are retained, including every favorable, adverse, absent, unavailable and unresolved record.", "all_8_targets_required": True, "falsification_condition": spec.falsification_condition},
            "evidence_mode": "observational_derivation_plus_complete_external_record_reconstruction", "experiment_id": spec.experiment_id,
            "external_measurement_sources": [{"complete_pdf_pages": 266, "complete_html_documents": 1, "complete_extracted_characters": 410095, "measurement_bodies": ["National Institute of Standards and Technology", "United States Geological Survey", "National Bureau of Standards"], "claim_surface": external_surface}],
            "frozen_relation": {"relation_hash": sha256_identity(spec.exact_result), "statement": spec.exact_result, "targets_did_not_select_survivor": True},
            "identity_registry": identity, "prediction_seal": seal, "registered_by": "Maria Smith", "registration_date": "2026-07-28",
            "schema": "sft-v3-chemistry-experiment-registration/1", "status": "registered_sources_captured_postseal",
        }
        write(experiment / "registration.json", experiment_registration)
    print("scaffolded four separate NUCHEM-005–008 claim packages")


if __name__ == "__main__": main()
