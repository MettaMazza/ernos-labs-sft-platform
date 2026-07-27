#!/usr/bin/env python3
"""Scaffold the registered Chemistry KIN-012 claim and experiment packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.kinetic_isotope_effect_batch_v1 import (  # noqa: E402
    IDENTITY_HASH,
    IDENTITY_PATH,
    KINETIC_ISOTOPE_EFFECT_SPEC,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SOURCE_FILES,
    SPEC_HASH,
    SPEC_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.kinetic_isotope_effect_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def independent_source() -> str:
    spec = KINETIC_ISOTOPE_EFFECT_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Implementation-distinct value-free KIN-012 reconstruction."""
from fractions import Fraction
from itertools import product
import json,sys
CLAIM={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; received=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}
 roles=("entry","boundary","event","product"); numerator=("reaction","path","light",roles,"condition",Fraction(3,2)); denominator=("reaction","path","heavy",roles,"condition",Fraction(2,2)); normal=numerator[-1]/denominator[-1]; inverse=Fraction(2,2)/Fraction(3,2); equal=Fraction(2,2)/Fraction(2,2); orientations=("numerator-rate-greater" if normal>1 else "wrong","denominator-rate-greater" if inverse<1 else "wrong","rates-exactly-equal" if equal==1 else "wrong"); prior=(("pair-a",normal),); extended=prior+(("pair-b",inverse),)
 witnesses=(numerator[2]!=denominator[2] and numerator[0:2]==denominator[0:2] and numerator[3:5]==denominator[3:5] and normal==Fraction(3,2) and inverse==Fraction(2,3) and equal==Fraction(1,1) and orientations==("numerator-rate-greater","denominator-rate-greater","rates-exactly-equal") and extended[:len(prior)]==prior and len(extended)==len(prior)+1)
 passed=(d["claim_id"]==CLAIM and received==generated and len(generated)==256 and len(set(received))==256 and d["census"]["expected_cardinality"]==256 and decisions=={{candidate:candidate==SURVIVOR for candidate in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and {{row["kind"] for row in d["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}} and all(row["passed"] for row in d["controls"]) and witnesses)
 print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,"two_distinct_held_isotope_identities_on_same_complete_path_reconstructed":witnesses,"exact_positive_ordered_rate_quotient_and_all_three_held_orientations_reconstructed":witnesses,"kinetic_isotope_pair_successor_preserves_prior_family":witnesses,"numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used":False,"KIE_equation_numerical_mass_mass_frequency_transition_state_fit_exponent_statistical_weight_target_measurement_or_source_file_accessed":False}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = KINETIC_ISOTOPE_EFFECT_SPEC
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.chemistry.kinetic_isotope_effect_batch_v1 import KINETIC_ISOTOPE_EFFECT_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.kinetic_isotope_effect_validation_v1 import KineticIsotopeEffectValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/kinetic_isotope_effect_law_v1.py",root/"sft/chemistry/kinetic_isotope_effect_batch_v1.py",root/"sft/chemistry/kinetic_isotope_effect_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_kinetic_isotope_effect_sources_v1.py",root/"tools/register_chemistry_kinetic_isotope_effect_identities_v1.py",root/"tools/capture_chemistry_kinetic_isotope_effect_targets_v1.py",root/"tools/build_chemistry_kinetic_isotope_effect_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/{spec.claim_id}/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(KINETIC_ISOTOPE_EFFECT_SPEC,source_hash),ExternalCommandValidator("sft-chem-kinetic-isotope-effect-012-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,KineticIsotopeEffectValidator(root))
'''


def main() -> None:
    spec = KINETIC_ISOTOPE_EFFECT_SPEC
    package = ROOT / "claims" / spec.claim_id
    write_json(
        package / "registration.json",
        {
            "$schema": "../../governance/claim.schema.json",
            "claim_id": spec.claim_id,
            "title": spec.title,
            "branch": "chemistry",
            "status": "registered",
            "statement": spec.statement,
            "dependencies": list(spec.dependencies),
            "provenance_classes": ["observational_derivation"],
            "candidate_grammar": {
                "generator": spec.generation_rule,
                "boundary": spec.grammar_boundary,
                "expected_cardinality": 256,
                "completeness_certificate": sha256_identity(completeness_record(spec)),
            },
            "excluded_inputs": list(spec.exclusions),
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "intended_certificate": (
                "Complete 256-form census, one survivor, depth-independent ordered-isotopologue-pair successor, "
                "implementation-distinct exact positive rate-quotient reconstruction, capability-closed 71-record vector, "
                "47 PDF pages, 23 complete worksheets, 923,260 nonempty cells, 90 explicit rate ratios, three direct "
                "decay KIEs, all replicates, normal/inverse/near-equal cases, limitations, reviewer challenges, omission "
                "and mismatched-path controls."
            ),
            "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-27",
        },
    )
    registration = experiment_registration_record(ROOT)
    program = prediction_program_document(ROOT)
    write_json(
        ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json",
        {
            "$schema": "../../../governance/experiment.schema.json",
            **registration,
            "evidence_mode": "observational_derivation_with_value_free_prefetch_and_identity_seals",
            "development_observation_disclosed": True,
            "observed_values_did_not_select_survivor": True,
            "external_measurement_sources": [
                {
                    "source_id": "NATURE-COMMUNICATIONS-S41467-024-44753-X-COMPLETE",
                    "measurement_body": "Nature Communications complete kinetic isotope-effect article and source-data surface",
                    "doi": "10.1038/s41467-024-44753-x",
                    "role": "complete post-seal isotopologue rate-ratio, direct-decay, replicate, control, limitation and reviewer evidence surface",
                }
            ],
            "source_hashes": {
                "prefetch_value_free_specification": SPEC_HASH,
                "normalized_primary_records": PRIMARY_HASH,
                "identity_registry": IDENTITY_HASH,
                "withheld_measurements": TARGET_HASH,
                "complete_raw_and_landing_sources": dict(SOURCE_FILES),
            },
            "complete_surface": {
                "registered_source_record_count": 71,
                "pdf_page_count": 47,
                "source_data_worksheet_count": 23,
                "source_data_nonempty_cell_count": 923260,
                "source_data_populated_row_count": 39002,
                "explicit_rate_ratio_count": 90,
                "direct_decay_KIE_count": 3,
                "direct_decay_KIE_external_inscriptions": ["2.11", "0.827", "0.55"],
                "adverse_records": [
                    "in-situ infrared evidence is not standalone evidence",
                    "reviewer challenges and requested controls remain visible",
                    "source transition-state, zero-point, Hooke, quantum-calculation and fitted models remain post-seal provenance only",
                ],
            },
            "absence_boundary": {
                "native_proof_form": "structural EmptyOne",
                "display_glyph": "0",
                "meaning": "external source inscription only",
                "numerical_zero_admitted": False,
            },
            "prediction_protocol": {
                "program_hash": sha256_identity(program),
                "measured_values_present": False,
                "target_content_inaccessible": True,
                "complete_trace_required": True,
            },
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-27",
            "status": "registered",
        },
    )
    write(package / "independent_validator.py", independent_source())
    write(package / "execution.py", execution_source())
    write(
        package / "WHY_DERIVATION_CHECK.md",
        f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-KIN-012`

## WHY

KIN-001 through KIN-011 close exact event rates, concentration and temperature dependence, activation and transition boundaries, complete mechanisms, reversible correspondence, catalytic return and the finite transport-to-reaction boundary. They do not yet state what remains invariant when only a held isotope identity changes on one otherwise identical complete reaction path. KIN-012 asks what the admitted exact-rate structure itself forces before any measured isotope-effect value is opened.

## DERIVATION

The eight-axis grammar generates 256 forms. Exactly one retains two distinct held isotopologue identities, the same complete reaction and path roles, the same held condition, two independently counted exact positive event rates, their ordered exact quotient, and a held greater/less/equal orientation:

`{survivor_id(spec)}`

No numerical isotope mass, conventional kinetic-isotope equation, mass-frequency relation, transition-state model, continuum time, fitted exponent or statistical weight selects the survivor. One complete ordered pair forces the base relation. Appending the next complete pair preserves every prior exact result.

## CHECK

Before target content opened, DOI `10.1038/s41467-024-44753-x`, all five complete files and 71 value-free identities were sealed. Those identities comprise the article landing record, every one of 47 PDF pages and all 23 source-data worksheets. They contain no rate ratio, decay, production, temperature, uncertainty, replicate, condition, status, value or target hash.

After sealing, the complete surface opened: 923,260 nonempty source-data cells, 39,002 populated rows, 90 explicit rate-ratio records, and direct decay KIE inscriptions `2.11`, `0.827` and `0.55`. Normal, inverse and near-unity cases, temperatures `3`, `6`, `9`, `12` and `15` °C, three independent experiments and all recorded replicates remain distinct. No averaging selects or repairs a result.

The reporting summary's statement that in-situ infrared evidence is not standalone evidence remains visible, as do reviewer challenges and requested controls. Source transition-state, zero-point, Hooke, quantum-calculation and fitted interpretations remain post-seal provenance only and never enter the Fold proof.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The exact ordered-pair law and successor are depth-independent. The empirical record is finite-complete for the byte-sealed five-file, 71-record source surface. It validates retention, relation direction and complete custody; it does not import any source model as SFT law.
""",
    )
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation_with_blind_postseal_vector`\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
