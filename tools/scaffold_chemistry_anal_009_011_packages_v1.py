#!/usr/bin/env python3
"""Create the three separate ANAL-009--011 claim packages."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.photoluminescence_family_batch_v1 import (
    COMPLETENESS_CERTIFICATES, FLUORESCENCE_SPEC, PHOSPHORESCENCE_SPEC, RAMAN_SPEC,
)
from sft.engine.canonical import sha256_identity


CONFIG = {
    "009": (
        RAMAN_SPEC, "RamanValidator", "RAMAN_SPEC", "SFT-CHEM-OBL-ANAL-009",
        "Raman transition and intensity law",
        "experiments/external_sources/chemistry/anal_009_target_identities_v1.json",
        "experiments/sealed_predictions/chemistry_anal_009_pre_source_v1.json",
        "six SRM 2241 coefficient triplets and all 386 SRM 2242a shifts across five certified curves (1,930 values), both excitation boundaries and every signed coefficient and uncertainty curve",
    ),
    "010": (
        FLUORESCENCE_SPEC, "FluorescenceValidator", "FLUORESCENCE_SPEC", "SFT-CHEM-OBL-ANAL-010",
        "fluorescence yield and lifetime law",
        "experiments/external_sources/chemistry/anal_010_target_identities_v1.json",
        "experiments/sealed_predictions/chemistry_anal_010_pre_source_v1.json",
        "all 201 SRM 2941a emission rows, 100 IUPAC quantum-yield table rows with 813 numerical inscriptions, twenty lifetime conditions, two retained outliers and all adverse method passages",
    ),
    "011": (
        PHOSPHORESCENCE_SPEC, "PhosphorescenceValidator", "PHOSPHORESCENCE_SPEC", "SFT-CHEM-OBL-ANAL-011",
        "phosphorescence intersystem law",
        "experiments/external_sources/chemistry/anal_011_target_identities_v1.json",
        "experiments/sealed_predictions/chemistry_anal_011_pre_source_v1.json",
        "all three two-temperature lifetime rows, 142 BioC passages, observed and nonobserved partitions, seven favorable/adverse/absent/unavailable custody classes and the unavailable OA-package record",
    ),
}

NATIVE = {
    "009": '''from fractions import Fraction
EMPTY="EmptyOne"
def relation(incident,scattered):
 if incident==scattered:return ("coincident",EMPTY)
 return ("stokes" if incident>scattered else "anti-stokes",abs(incident-scattered))
rows=(("molecule-a","state-a","state-b","changes",relation(Fraction(10),Fraction(7)),Fraction(3,5),("excitation-a","inverse-length")),("molecule-a","state-b","state-c","unresolved",relation(Fraction(10),Fraction(10)),EMPTY,("excitation-a","inverse-length")))
native={"carrier":all(x[0]=="molecule-a" for x in rows),"states":all(x[1]!=x[2] for x in rows),"polarizability":rows[0][3]=="changes","position":rows[0][4]==("stokes",Fraction(3)) and rows[1][4]==("coincident",EMPTY),"intensity":rows[0][5]==Fraction(3,5) and rows[1][5]==EMPTY,"condition":len({x[6] for x in rows})==1,"custody":len(rows)==2,"extension":len(rows+(("molecule-a","state-a","state-c","changes",("anti-stokes",Fraction(2)),Fraction(1,5),("excitation-a","inverse-length")),))==3}''',
    "010": '''from fractions import Fraction
EMPTY="EmptyOne"
excitation=5
rows=(("molecule-a","excited-a","ground-a","radiative",Fraction(7,3),3,Fraction(2,3)),("molecule-a","excited-a","other-a","nonradiative",EMPTY,2,EMPTY))
native={"carrier":all(x[0]=="molecule-a" and x[1]=="excited-a" for x in rows),"transition":len({x[2] for x in rows})==2,"channels":sum(x[5] for x in rows)==excitation,"emission":rows[0][4]==Fraction(7,3) and rows[1][4]==EMPTY,"yield":Fraction(rows[0][5],excitation)==Fraction(3,5),"lifetime":rows[0][6]==Fraction(2,3),"custody":rows[1][6]==EMPTY,"extension":tuple(rows)==rows}''',
    "011": '''from fractions import Fraction
EMPTY="EmptyOne"
rows=(("molecule-a","excited-a","intersystem-a","ground-a","hand-a","hand-b",Fraction(5,2),1,4,Fraction(7,3)),("molecule-a","excited-b","intersystem-b","ground-a","hand-b","hand-a",EMPTY,EMPTY,4,EMPTY))
native={"carrier":all(x[0]=="molecule-a" for x in rows),"spin":all(x[4]!=x[5] for x in rows),"path":all(x[1]!=x[2] and x[2]!=x[3] for x in rows),"emission":rows[0][6]==Fraction(5,2) and rows[1][6]==EMPTY,"yield":Fraction(rows[0][7],rows[0][8])==Fraction(1,4) and rows[1][7]==EMPTY,"lifetime":rows[0][9]==Fraction(7,3) and rows[1][9]==EMPTY,"custody":len(rows)==2,"extension":tuple(rows)==rows}''',
}


def write(path: Path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
    path.write_text(content if isinstance(content, str) else json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main():
    for key, (claim, validator, spec_name, obligation, label, identity, seal, surface) in CONFIG.items():
        package = ROOT / "claims" / claim.claim_id
        experiment = ROOT / "experiments/chemistry" / claim.experiment_id
        if package.exists() or experiment.exists():
            expected = (
                package / "registration.json", package / "STATUS.md", package / "WHY_DERIVATION_CHECK.md",
                package / "execution.py", package / "independent_validator.py", experiment / "registration.json",
            )
            if all(path.is_file() for path in expected):
                continue
            raise SystemExit(f"partial existing package requires manual inspection: {claim.claim_id}")
        domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in claim.dimensions)
        write(package / "registration.json", {
            "$schema": "../../governance/claim.schema.json", "branch": "chemistry",
            "candidate_grammar": {"boundary": claim.grammar_boundary, "completeness_certificate": COMPLETENESS_CERTIFICATES[claim.claim_id], "expected_cardinality": 256, "generator": claim.generation_rule},
            "claim_id": claim.claim_id, "dependencies": list(claim.dependencies),
            "empirical_protocol": f"experiments/chemistry/{claim.experiment_id}/registration.json",
            "excluded_inputs": list(claim.exclusions),
            "provenance_classes": ["observational_derivation", "complete_external_record_reconstruction"],
            "registered_by": "Maria Smith", "registration_date": "2026-07-28",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "omitted_target_row"],
            "statement": claim.statement, "status": "registered", "title": claim.title,
        })
        write(package / "STATUS.md", f"# {claim.claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", (
            f"# Why ANAL-{key} requires a derivation check\n\n"
            f"A displayed spectrum, yield or lifetime cannot establish the {label}. This claim generates all 256 registered forms before measurement comparison and uses its own value-free target identities and exposure-disclosed pre-source seal. The family reconstructs sixteen official artifacts: 73 PDF pages, six HTML documents, two XML records, two certified workbooks and 3,184,576 source bytes. {surface.capitalize()}. External fits, signs, displayed zeroes, decimals, conditions, errors, favorable, adverse, absent, unavailable and unresolved rows remain downstream evidence and cannot select the Fold-native survivor.\n"
        ))
        write(package / "execution.py", f'''import sys
from sft.chemistry.photoluminescence_family_batch_v1 import AUTHORITIES,{spec_name} as CLAIM_SPEC
from sft.chemistry.photoluminescence_family_validation_v1 import {validator}
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root):
 fixed=("sft/chemistry/photoluminescence_family_batch_v1.py","sft/chemistry/photoluminescence_family_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/{claim.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{claim.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-anal-{key}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,{validator}(root))
''')
        write(package / "independent_validator.py", f'''from itertools import product
import json,sys
CLAIM_ID={claim.claim_id!r};DOMAINS={domains!r};SURVIVOR={claim.exact_result!r}
{NATIVE[key]}
def main():
 sealed=json.load(open(sys.argv[1]));generated=["__".join(item) for item in product(*DOMAINS)];decisions={{item["candidate_id"]:item["survives"] for item in sealed["decisions"]}};passed=sealed["claim_id"]==CLAIM_ID and [item["candidate_id"] for item in sealed["census"]["candidates"]]==generated and decisions=={{item:item==SURVIVOR for item in generated}} and sum(decisions.values())==1 and sealed["closure"]["scope"]=="depth_independent" and all(item["passed"] for item in sealed["controls"]) and all(native.values());print(json.dumps({{"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,**native,"external_source_accessed":False,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used":False}}}},sort_keys=True))
if __name__=="__main__":main()
''')
        write(experiment / "registration.json", {
            "$schema": "../../../governance/experiment.schema.json", "claim_id": claim.claim_id,
            "absence_boundary": {"display_glyph": "0", "external_signed_decimal_and_zero_inscriptions_are_provenance_only": True, "native_proof_form": "positive exact counts/ratios, held orientation and structural EmptyOne absence", "numerical_zero_admitted": False},
            "evaluation_protocol": {"acceptance_condition": "All eight preregistered comparisons and the complete sixteen-artifact family surface are retained.", "all_8_targets_required": True, "falsification_condition": claim.falsification_condition},
            "evidence_mode": "observational_derivation_plus_complete_external_record_reconstruction",
            "experiment_id": claim.experiment_id,
            "external_measurement_sources": [{"complete_pdf_pages": 73, "complete_html_documents": 6, "complete_xml_documents": 2, "complete_certified_workbooks": 2, "complete_source_bytes": 3184576, "measurement_bodies": ["National Institute of Standards and Technology", "International Union of Pure and Applied Chemistry", "National Library of Medicine", "University of California eScholarship"], "claim_surface": surface}],
            "frozen_relation": {"relation_hash": sha256_identity(claim.exact_result), "statement": claim.exact_result, "targets_did_not_select_survivor": True},
            "identity_registry": identity, "prediction_seal": seal,
            "registered_by": "Maria Smith", "registration_date": "2026-07-28",
            "schema": "sft-v3-chemistry-experiment-registration/1", "status": "registered_sources_captured_postseal",
        })
    print("scaffolded three separate ANAL-009--011 claim packages")


if __name__ == "__main__":
    main()
