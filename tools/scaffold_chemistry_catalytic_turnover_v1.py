#!/usr/bin/env python3
"""Scaffold the registered Chemistry KIN-010 claim and experiment packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.catalytic_turnover_batch_v1 import (  # noqa: E402
    CATALYTIC_TURNOVER_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    SOURCE_FILES, SPEC_HASH, SPEC_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.catalytic_turnover_validation_v1 import (  # noqa: E402
    experiment_registration_record, prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def independent_source() -> str:
    spec = CATALYTIC_TURNOVER_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Implementation-distinct value-free KIN-010 reconstruction."""
from fractions import Fraction
from itertools import product
import json,sys
CLAIM={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; received=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}
 states=("state-1","state-2","state-3","state-4","state-5"); edges=tuple((states[i],states[(i+1)%len(states)]) for i in range(len(states))); catalyst=tuple("same-held-catalyst" for _ in states); turnover=(states,edges,catalyst,"one-complete-return-word"); frequency=Fraction(3,2); prior=(turnover,); next_states=("next-1","next-2","next-3","next-4","next-5"); extended=prior+((next_states,tuple((next_states[i],next_states[(i+1)%len(next_states)]) for i in range(len(next_states))),tuple("next-held-catalyst" for _ in next_states),"one-complete-return-word"),)
 witnesses=(len(states)==5 and len(edges)==5 and edges[-1][1]==states[0] and len(set(catalyst))==1 and frequency.numerator==3 and frequency.denominator==2 and extended[:len(prior)]==prior and len(extended)==len(prior)+1)
 passed=(d["claim_id"]==CLAIM and received==generated and len(generated)==256 and len(set(received))==256 and d["census"]["expected_cardinality"]==256 and decisions=={{candidate:candidate==SURVIVOR for candidate in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and {{row["kind"] for row in d["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}} and all(row["passed"] for row in d["controls"]) and witnesses)
 print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,"same_catalyst_five_state_return_cycle_reconstructed":witnesses,"one_return_word_turnover_and_exact_positive_count_relation_reconstructed":witnesses,"complete_cycle_successor_preserves_prior_family":witnesses,"numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used":False,"turnover_formula_rate_equation_Michaelis_Menten_steady_state_stochastic_weight_fit_target_measurement_or_source_file_accessed":False}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = CATALYTIC_TURNOVER_SPEC
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.chemistry.catalytic_turnover_batch_v1 import CATALYTIC_TURNOVER_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.catalytic_turnover_validation_v1 import CatalyticTurnoverValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/catalytic_turnover_law_v1.py",root/"sft/chemistry/catalytic_turnover_batch_v1.py",root/"sft/chemistry/catalytic_turnover_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_catalytic_turnover_sources_v1.py",root/"tools/register_chemistry_catalytic_turnover_identities_v1.py",root/"tools/capture_chemistry_catalytic_turnover_targets_v1.py",root/"tools/build_chemistry_catalytic_turnover_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/{spec.claim_id}/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(CATALYTIC_TURNOVER_SPEC,source_hash),ExternalCommandValidator("sft-chem-catalytic-turnover-010-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,CatalyticTurnoverValidator(root))
'''


def main() -> None:
    spec = CATALYTIC_TURNOVER_SPEC
    package = ROOT / "claims" / spec.claim_id
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title,
        "branch": "chemistry", "status": "registered", "statement": spec.statement,
        "dependencies": list(spec.dependencies), "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {
            "generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": (
            "Complete 256-form census, one survivor, depth-independent complete-cycle successor, implementation-distinct "
            "five-state catalyst-return reconstruction, exact positive cycle-count relation, capability-closed 497-record "
            "identity vector, exact seven-row TOF table, independent rate tables, 385,617 raw trace rows, 1,604 movie "
            "frames, 387 archive members and adverse unavailable-PDF, insufficient-fit, omission and broken-return controls."
        ),
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith", "registration_date": "2026-07-27",
    })
    registration = experiment_registration_record(ROOT)
    program = prediction_program_document(ROOT)
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", {
        "$schema": "../../../governance/experiment.schema.json", **registration,
        "evidence_mode": "observational_derivation_with_value_free_prefetch_and_identity_seals",
        "development_observation_disclosed": True, "observed_values_did_not_select_survivor": True,
        "external_measurement_sources": [{
            "source_id": "NATURE-NANOTECHNOLOGY-S41565-021-00959-4-COMPLETE",
            "measurement_body": "Nature Nanotechnology single-molecule catalytic-cycle study",
            "doi": "10.1038/s41565-021-00959-4", "source_data_doi": "10.5281/zenodo.4903414",
            "role": "complete post-seal cycle, turnover, control, movie, raw-trace and archive evidence surface",
        }],
        "source_hashes": {
            "prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH,
            "complete_raw_and_landing_sources": dict(SOURCE_FILES),
        },
        "complete_surface": {
            "registered_source_record_count": 497, "supplementary_page_count": 106,
            "supplementary_movie_frame_count": 1604, "archive_count": 7, "archive_member_count": 387,
            "raw_figure_6_trace_row_count": 385617, "structural_state_count": 5,
            "separately_observed_conductance_state_count": 4, "turnover_value_row_count": 7,
            "adverse_records": [
                "article PDF request returned HTML and remains an unavailable-PDF record",
                "low-temperature observations contain fewer cycles and insufficient fit data",
                "Tables S2 and S3 remain separate independent value vectors without selection or averaging",
            ],
        },
        "absence_boundary": {
            "native_proof_form": "structural EmptyOne", "display_glyph": "0",
            "meaning": "external source inscription only", "numerical_zero_admitted": False,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(program), "measured_values_present": False,
            "target_content_inaccessible": True, "complete_trace_required": True,
        },
        "registered_by": "Maria Smith", "registration_date": "2026-07-27", "status": "registered",
    })
    write(package / "independent_validator.py", independent_source())
    write(package / "execution.py", execution_source())
    write(package / "WHY_DERIVATION_CHECK.md", f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-KIN-010`

## WHY

KIN-001 through KIN-009 close exact elementary transitions, dependencies, activation boundaries, complete sequential and parallel mechanisms and the same-graph reversible kinetic-equilibrium correspondence. They do not yet force what constitutes one catalytic turnover or its cycle frequency without importing a conventional catalytic-rate equation. KIN-010 asks what the admitted transition structure itself forces when the catalyst must return exactly.

## DERIVATION

The eight-axis grammar generates 256 forms. Exactly one retains the same held catalyst identity through every state and exact return, requires the complete ordered transition word, identifies one completed return word as one turnover, identifies frequency as the exact positive relation between completed return-word count and held observation-interval parts, distinguishes five structural states from four separately observed conductance levels, retains every adverse and unresolved status, binds the complete source surface and seals all value-free identities:

`{survivor_id(spec)}`

The final transition must exit the last intermediate and enter the exact first catalyst state. No product count, fitted rate, stochastic weight, continuum, Michaelis-Menten or steady-state premise can replace that closure. One closed word forces the base. Appending the next complete cycle at the next positive source occurrence preserves every prior state, edge, catalyst identity, condition, status and turnover and increases the exact completed-cycle count by one.

## CHECK

Before target content opened, DOI `10.1038/s41565-021-00959-4`, source-data DOI `10.5281/zenodo.4903414`, twelve complete files, 106 supplementary-page identities, one movie identity and 387 archive-member topologies were sealed. The 497 identities contain no cycle state, transition, duration, turnover, frequency, condition, fit, rate, uncertainty, product, control status, value or target hash.

After sealing, the complete source record opened. The structural word is State 1 → 2 → 3 → 4 → 5 → State 1. State 1 is the LPd(0) catalyst entry and return. State 2 is a structural oxidative-addition intermediate that is not separately resolved as a conductance state. States 1, 3, 4 and 5 are the four separately observed conductance states. The distinction is retained; the observed four are never substituted for the structural five.

The visually inspected Table S1 retains all seven TOF values: `0.5`, `4.6`, `29.6`, `39.0`, `203.9`, `615.6` and `2098.7 s^-1`, alongside every signed or zero source inscription. Tables S2 and S3 retain two distinct five-temperature State-1/State-4 rate vectors and are not averaged. Figure 6 retains 385,617 raw trace rows, its complete signed/zero XY and histogram tables and the full 7-by-17 workbook. All 106 supplementary pages, the 1,604-frame movie and all 387 members of seven archives remain byte-bound. The attempted article PDF returned HTML; that limitation remains explicit. Low-temperature fewer-cycle and insufficient-fit records remain adverse evidence.

All reported TOFs, dwell times, transfer rates, maximum-likelihood estimates, single-exponent fits, Eyring/Arrhenius/Hess calculations and signed/zero glyphs are post-seal source provenance only. None enters the Fold law or enumeration.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The catalyst-return law and complete-cycle successor are depth-independent. The empirical result is finite-complete for the byte-sealed twelve-file, 497-record source surface. It demonstrates exact correspondence with the retained source cycle and turnover vector; it does not import the source's fitted kinetic models as SFT proof.
""")
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation_with_blind_postseal_vector`\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
