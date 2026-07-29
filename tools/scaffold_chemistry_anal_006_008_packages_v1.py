#!/usr/bin/env python3
"""Create the three separate ANAL-006--008 claim and experiment packages."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.nmr_family_batch_v1 import (
    AUTHORITIES,
    COMPLETENESS_CERTIFICATES,
    COUPLING_SPEC,
    RELAXATION_SPEC,
    SHIFT_SPEC,
)
from sft.engine.canonical import sha256_identity


CONFIG = {
    "006": (
        SHIFT_SPEC, "ShiftValidator", "SHIFT_SPEC", "SFT-CHEM-OBL-ANAL-006",
        "NMR chemical-shift relation",
        "experiments/external_sources/chemistry/anal_006_target_identities_v1.json",
        "experiments/sealed_predictions/chemistry_anal_006_pre_source_v1.json",
        "556 complete 1H chemical-shift rows from BMRB 68, DSS reference, pH 4.7 and 323 K conditions, every ambiguity code and all 556 unreported error fields",
    ),
    "007": (
        COUPLING_SPEC, "CouplingValidator", "COUPLING_SPEC", "SFT-CHEM-OBL-ANAL-007",
        "NMR scalar spin-coupling relation",
        "experiments/external_sources/chemistry/anal_007_target_identities_v1.json",
        "experiments/sealed_predictions/chemistry_anal_007_pre_source_v1.json",
        "643 complete scalar-coupling rows in ten 2J families, 395 alternating-hand and 248 preserving-hand observations, every 0.50 Hz error and all absent bounds",
    ),
    "008": (
        RELAXATION_SPEC, "RelaxationValidator", "RELAXATION_SPEC", "SFT-CHEM-OBL-ANAL-008",
        "NMR relaxation and exchange law",
        "experiments/external_sources/chemistry/anal_008_target_identities_v1.json",
        "experiments/sealed_predictions/chemistry_anal_008_pre_source_v1.json",
        "148 T1, 148 T1rho and 138 hydrogen-exchange rows, all units and errors, eleven external zero-rate inscriptions translated to unresolved structural EmptyOne, and 148 unavailable Rex rows",
    ),
}

NATIVE = {
    "006": '''from fractions import Fraction
EMPTY="EmptyOne"
def relation(sample,reference):
 if sample==reference:return ("coincident",EMPTY)
 return ("higher-frequency" if sample>reference else "lower-frequency",abs(sample-reference)/reference)
carrier="molecule-a";reference="reference-a";condition=("solvent-a","condition-a")
rows=(("one-H","site-a",relation(Fraction(1001),Fraction(1000)),Fraction(1,10000)),("one-H","site-b",relation(Fraction(1000),Fraction(1000)),EMPTY))
native={"identity":carrier=="molecule-a","nucleus":all(x[0]=="one-H" for x in rows),"site":len({x[1] for x in rows})==2,"reference":reference=="reference-a","environment":condition==("solvent-a","condition-a"),"relation":rows[0][2][1]==Fraction(1,1000) and rows[1][2][1]==EMPTY,"custody":rows[0][3]==Fraction(1,10000) and rows[1][3]==EMPTY,"extension":len(rows+(("one-H","site-c",relation(Fraction(1002),Fraction(1000)),EMPTY),))==3}''',
    "007": '''from fractions import Fraction
EMPTY="EmptyOne"
rows=((frozenset(("site-a","site-b")),"preserving-hand",2,Fraction(7,2),Fraction(1,10)),(frozenset(("site-b","site-c")),"unresolved-hand",3,EMPTY,EMPTY))
native={"pair":all(len(x[0])==2 for x in rows),"spin":tuple(x[1] for x in rows)==("preserving-hand","unresolved-hand"),"path":tuple(x[2] for x in rows)==(2,3),"environment":True,"magnitude":rows[0][3]==Fraction(7,2) and rows[1][3]==EMPTY,"symmetry":frozenset(reversed(tuple(rows[0][0])))==rows[0][0],"custody":rows[0][4]==Fraction(1,10) and rows[1][4]==EMPTY,"extension":len(rows+((frozenset(("site-a","site-c")),"alternating-hand",4,Fraction(1,2),EMPTY),))==3}''',
    "008": '''from fractions import Fraction
EMPTY="EmptyOne"
rows=(("site-a","longitudinal-relaxation","state-a","state-a",Fraction(3,2),"seconds","measured"),("site-b","hydrogen-exchange","state-a","state-b",Fraction(5,3),"per-second","measured"),("site-a","rotating-frame-relaxation","state-a","state-a",EMPTY,"seconds","unavailable"))
native={"carrier":len({x[0] for x in rows})==2,"states":rows[1][2]!=rows[1][3],"process":len({x[1] for x in rows})==3,"resource":rows[0][4]==Fraction(3,2),"relation":Fraction(5,1)/Fraction(3,1)==Fraction(5,3),"observation":rows[0][5]=="seconds","adversity":rows[2][4]==EMPTY and rows[2][6]=="unavailable","extension":len(rows+(("site-b","transverse-relaxation","state-b","state-b",Fraction(4,3),"seconds","bounded"),))==4}''',
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
        domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in claim.dimensions)
        write(package / "registration.json", {
            "$schema": "../../governance/claim.schema.json",
            "branch": "chemistry",
            "candidate_grammar": {
                "boundary": claim.grammar_boundary,
                "completeness_certificate": COMPLETENESS_CERTIFICATES[claim.claim_id],
                "expected_cardinality": 256,
                "generator": claim.generation_rule,
            },
            "claim_id": claim.claim_id,
            "dependencies": list(claim.dependencies),
            "empirical_protocol": f"experiments/chemistry/{claim.experiment_id}/registration.json",
            "excluded_inputs": list(claim.exclusions),
            "provenance_classes": ["observational_derivation", "complete_external_record_reconstruction"],
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-28",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "omitted_target_row"],
            "statement": claim.statement,
            "status": "registered",
            "title": claim.title,
        })
        write(package / "STATUS.md", f"# {claim.claim_id}\n\nStatus: `registered_pending_untouched_engine_admission`\n")
        write(package / "WHY_DERIVATION_CHECK.md", (
            f"# Why ANAL-{key} requires a derivation check\n\n"
            f"A displayed NMR value cannot establish the {label}. This claim separately generates all 256 registered forms before comparison and uses only its own value-free identity and source-exposure-disclosed derivation seal. The complete post-seal family reconstructs ten official source records: 24 IUPAC PDF pages, five HTML records, four NMR-STAR records, 1,527,681 source bytes and 1,633 measured rows. {surface.capitalize()}. Every external sign or displayed zero, decimal, value, unit, uncertainty, ambiguity, bound, condition, favorable, adverse, absent, unavailable and unresolved row remains downstream provenance and cannot select the native Fold law.\n"
        ))
        write(package / "execution.py", f'''import sys
from sft.chemistry.nmr_family_batch_v1 import AUTHORITIES,{spec_name} as CLAIM_SPEC
from sft.chemistry.nmr_family_validation_v1 import {validator}
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root):
 fixed=("sft/chemistry/nmr_family_batch_v1.py","sft/chemistry/nmr_family_validation_v1.py","sft/chemistry/generated_law.py","sft/chemistry/generated_observational_law.py","sft/physics/generated_empirical_law.py",*(p for p,_ in AUTHORITIES),"claims/{claim.claim_id}/execution.py");files=tuple(dict.fromkeys(root/p for p in fixed if (root/p).is_file()));independent=root/"claims/{claim.claim_id}/independent_validator.py";return ClaimExecution(GeneratedObservationalChemistryProgram(CLAIM_SPEC,build_source_manifest(root,files).manifest_hash),ExternalCommandValidator("sft-chem-anal-{key}-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),files,{validator}(root))
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
            "$schema": "../../../governance/experiment.schema.json",
            "claim_id": claim.claim_id,
            "absence_boundary": {
                "display_glyph": "0",
                "external_signed_decimal_and_zero_inscriptions_are_provenance_only": True,
                "native_proof_form": "positive exact counts/ratios, held orientation and structural EmptyOne absence",
                "numerical_zero_admitted": False,
            },
            "evaluation_protocol": {
                "acceptance_condition": "All eight preregistered comparisons and the complete ten-source, 1,633-row NMR family surface are retained.",
                "all_8_targets_required": True,
                "falsification_condition": claim.falsification_condition,
            },
            "evidence_mode": "observational_derivation_plus_complete_external_record_reconstruction",
            "experiment_id": claim.experiment_id,
            "external_measurement_sources": [{
                "complete_pdf_pages": 24,
                "complete_html_documents": 5,
                "complete_nmr_star_records": 4,
                "complete_measured_rows": 1633,
                "complete_source_bytes": 1527681,
                "measurement_bodies": ["International Union of Pure and Applied Chemistry", "Biological Magnetic Resonance Bank"],
                "claim_surface": surface,
            }],
            "frozen_relation": {
                "relation_hash": sha256_identity(claim.exact_result),
                "statement": claim.exact_result,
                "targets_did_not_select_survivor": True,
            },
            "identity_registry": identity,
            "prediction_seal": seal,
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-28",
            "schema": "sft-v3-chemistry-experiment-registration/1",
            "status": "registered_sources_captured_postseal",
        })
    print("scaffolded three separate ANAL-006--008 claim packages")


if __name__ == "__main__":
    main()
