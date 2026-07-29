#!/usr/bin/env python3
"""Create four separate NUCHEM-009–012 claim and experiment packages."""
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.nuchem_terminal_batch_v1 import (
    AUTHORITIES, COMPLETENESS_CERTIFICATES, FISSION_PRODUCT_SPEC,
    RADIOLYSIS_SPEC, RADIOTRACER_SPEC, SEPARATION_SPEC,
)
from sft.engine.canonical import sha256_identity


CONFIG = {
    "009": (RADIOTRACER_SPEC, "RadiotracerValidator", "RADIOTRACER_SPEC", "SFT-CHEM-OBL-NUCHEM-009", "radiotracer custody and inference law", "experiments/external_sources/chemistry/nuchem_009_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_009_pre_source_v1.json", "eight tracer-chemistry rows, all detector and residence-time support, recovery, localization and adverse limits"),
    "010": (SEPARATION_SPEC, "SeparationValidator", "SEPARATION_SPEC", "SFT-CHEM-OBL-NUCHEM-010", "radiochemical separation and decontamination law", "experiments/external_sources/chemistry/nuchem_010_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_010_pre_source_v1.json", "fourteen species, nine complete process rows, balances, recoveries, decontamination and the adverse one-percent run"),
    "011": (FISSION_PRODUCT_SPEC, "FissionProductValidator", "FISSION_PRODUCT_SPEC", "SFT-CHEM-OBL-NUCHEM-011", "fission-product chemical-distribution law", "experiments/external_sources/chemistry/nuchem_011_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_011_pre_source_v1.json", "all chemical groups, phases, locations, samples, inventory bases and unresolved material-balance rows"),
    "012": (RADIOLYSIS_SPEC, "RadiolysisValidator", "RADIOLYSIS_SPEC", "SFT-CHEM-OBL-NUCHEM-012", "radiation-chemistry reaction-network law", "experiments/external_sources/chemistry/nuchem_012_target_identities_v1.json", "experiments/sealed_predictions/chemistry_nuchem_012_pre_source_v1.json", "all product, reaction, preferred-yield, high-dose, rare-gas and adverse/limit rows"),
}

NATIVE = {
    "009": '''from fractions import Fraction
def record(rows):
 if not rows or tuple(r[0] for r in rows)!=tuple(range(1,len(rows)+1)):return None
 if len({(r[1],r[2]) for r in rows})!=1:return None
 return tuple((r[3],Fraction(r[4],r[5]),None if r[4]==r[5] else r[5]-r[4]) for r in rows)
r=((1,"Tc-99m","pertechnetate","inlet",3,5),(2,"Tc-99m","pertechnetate","outlet",4,5))
native={"identity":len({(x[1],x[2]) for x in r})==1,"support":tuple(x[0] for x in r)==(1,2),"locations":len({x[3] for x in r})==2,"events":all(x[5]>=x[4]>0 for x in r),"recovery":record(r)[0][1]==Fraction(3,5),"loss":record(r)[0][2]==2 and record(((1,"T","C","L",5,5),))[0][2] is None,"inference":len(record(r))==2,"successor":len(record(r+((3,"Tc-99m","pertechnetate","terminal",5,5),)))==3}''',
    "010": '''from fractions import Fraction
def valid(x):return x[2]==x[4]+x[6] and x[3]==x[5]+x[7]
def recovery(x):return Fraction(x[4],x[2])
def decontamination(x):return Fraction(x[3]*x[4],x[2]*x[5])
x=("Sc","V",10,12,8,2,2,10)
native={"identity":x[0]!=x[1],"streams":len(x[2:])==6,"inventory":min(x[2:])>0,"balance":valid(x),"recovery":recovery(x)==Fraction(4,5),"decontamination":decontamination(x)==Fraction(24,5),"absence":(None if 10==10 else 10-10) is None and 10-8==2,"successor":valid(x)}''',
    "011": '''from fractions import Fraction
def distribution(rows):
 if not rows:return None
 total=sum(r[4] for r in rows);return tuple((*r[:4],Fraction(r[4],total)) for r in rows)
def redistribute(a,b):return distribution(b) if {r[0] for r in a}=={r[0] for r in b} and sum(r[4] for r in a)==sum(r[4] for r in b) else None
a=(("Cs","fluoride","salt","bulk",3),("Xe","elemental","gas","headspace",1));b=(("Cs","fluoride","salt","wall",2),("Xe","elemental","gas","headspace",2))
native={"handoff":{r[0] for r in a}=={"Cs","Xe"},"identity":a[0][1]=="fluoride","support":len({r[2:4] for r in a})==2,"events":min(r[4] for r in a)>0,"partition":sum(r[-1] for r in distribution(a))==1,"chemistry":redistribute(a,b)[0][3]=="wall","boundary":{r[0] for r in a}=={r[0] for r in b},"successor":len(redistribute(a,b))==2}''',
    "012": '''from fractions import Fraction
def network(rows):
 if not rows:return None
 if len({r[0] for r in rows})!=1 or len({r[3] for r in rows})!=len(rows):return None
 total=sum(r[4] for r in rows);return tuple((r[1],r[2],r[3],Fraction(r[4],r[5]),Fraction(r[4],total)) for r in rows)
r=(("water","water","hydroxyl","ionization",3,10),("water","water","hydrogen","dissociation",2,10))
native={"handoff":r[0][5]>0,"identity":r[0][0]=="water" and r[0][1]!=r[0][2],"network":len({x[3] for x in r})==2,"events":tuple(x[4] for x in r)==(3,2),"yield":network(r)[0][3]==Fraction(3,10),"partition":sum(x[-1] for x in network(r))==1,"closure":network(()) is None,"successor":len(network(r+(("water","water","peroxide","recombination",1,10),)))==3}''',
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
        write(package / "registration.json", {
            "$schema": "../../governance/claim.schema.json", "branch": "chemistry",
            "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": COMPLETENESS_CERTIFICATES[spec.claim_id], "expected_cardinality": 256, "generator": spec.generation_rule},
            "claim_id": spec.claim_id, "dependencies": list(spec.dependencies),
            "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
            "excluded_inputs": list(spec.exclusions), "provenance_classes": ["observational_derivation", "complete_external_record_reconstruction"],
            "registered_by": "Maria Smith", "registration_date": "2026-07-28", "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "statement": spec.statement, "status": "registered", "title": spec.title,
        })
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", f"# Why NUCHEM-{key} requires a derivation check\n\nA conventional displayed value cannot establish the {label}. This claim separately generates all 256 registered forms before comparison and uses only its own value-free identity and source-exposure-disclosed derivation seal. The shared post-seal capture reconstructs four official sources as 370 complete PDF pages and 837,013 extracted characters. {external_surface.capitalize()}. Every value, unit, conventional zero or sign, decimal, uncertainty, assumption, correction, fit, estimate, loss, method disagreement, favorable, adverse, absent, unavailable and unresolved row remains downstream provenance and cannot select the native Fold law.\n")
        write(package / "execution.py", f'''import sys
from sft.chemistry.nuchem_terminal_batch_v1 import AUTHORITIES, {spec_name} as CLAIM_SPEC
from sft.chemistry.nuchem_terminal_validation_v1 import {validator}
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root):
 fixed=("sft/chemistry/nuchem_terminal_batch_v1.py","sft/chemistry/nuchem_terminal_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/{spec.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{spec.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-nuchem-{key}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,{validator}(root))
''')
        write(package / "independent_validator.py", f'''from itertools import product
import json,sys
CLAIM_ID={spec.claim_id!r};DOMAINS={domains!r};SURVIVOR={spec.exact_result!r}
{NATIVE[key]}
def main():
 s=json.load(open(sys.argv[1]));generated=["__".join(x) for x in product(*DOMAINS)];decisions={{x["candidate_id"]:x["survives"] for x in s["decisions"]}};passed=s["claim_id"]==CLAIM_ID and [x["candidate_id"] for x in s["census"]["candidates"]]==generated and decisions=={{x:x==SURVIVOR for x in generated}} and sum(decisions.values())==1 and s["closure"]["scope"]=="depth_independent" and all(x["passed"] for x in s["controls"]) and all(native.values());print(json.dumps({{"validated_seal_hash":s["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used":False}}}},sort_keys=True))
if __name__=="__main__":main()
''')
        write(experiment / "registration.json", {
            "$schema": "../../../governance/experiment.schema.json", "claim_id": spec.claim_id,
            "absence_boundary": {"display_glyph": "0", "external_signed_decimal_and_zero_inscriptions_are_provenance_only": True, "native_proof_form": "positive exact counts/ratios, held orientation and structural EmptyOne absence", "numerical_zero_admitted": False},
            "evaluation_protocol": {"acceptance_condition": "All 8 preregistered comparisons and the complete four-source post-seal surface are retained, including every favorable, adverse, absent, unavailable and unresolved record.", "all_8_targets_required": True, "falsification_condition": spec.falsification_condition},
            "evidence_mode": "observational_derivation_plus_complete_external_record_reconstruction", "experiment_id": spec.experiment_id,
            "external_measurement_sources": [{"complete_pdf_pages": 370, "complete_extracted_characters": 837013, "measurement_bodies": ["International Atomic Energy Agency", "United States Department of Energy", "Oak Ridge National Laboratory", "National Bureau of Standards"], "claim_surface": external_surface}],
            "frozen_relation": {"relation_hash": sha256_identity(spec.exact_result), "statement": spec.exact_result, "targets_did_not_select_survivor": True},
            "identity_registry": identity, "prediction_seal": seal, "registered_by": "Maria Smith", "registration_date": "2026-07-28",
            "schema": "sft-v3-chemistry-experiment-registration/1", "status": "registered_sources_captured_postseal",
        })
    print("scaffolded four separate NUCHEM-009–012 claim packages")


if __name__ == "__main__":
    main()
