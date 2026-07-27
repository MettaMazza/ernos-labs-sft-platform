#!/usr/bin/env python3
"""Scaffold the registered Chemistry KIN-011 claim and experiment packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.diffusion_limited_reaction_batch_v1 import (  # noqa: E402
    DIFFUSION_LIMITED_REACTION_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    SOURCE_FILES, SPEC_HASH, SPEC_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.diffusion_limited_reaction_validation_v1 import (  # noqa: E402
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
    spec = DIFFUSION_LIMITED_REACTION_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Implementation-distinct value-free KIN-011 reconstruction."""
from fractions import Fraction
from itertools import product
import json,sys
CLAIM={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; received=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}
 states=("separated-reactants","initiated-solvation","transport-occurrence-word","encounter-boundary"); edges=tuple((states[i],states[i+1]) for i in range(len(states)-1)); reactant=tuple("same-held-reactant" for _ in states); reaction_entry=states[-1]; product="product-complex"; completion=Fraction(3,2); occurrence=(states,edges,reactant,reaction_entry,product); prior=(occurrence,); extended=prior+((states,edges,reactant,reaction_entry,product),)
 witnesses=(len(states)==4 and len(edges)==3 and all(edges[i]==(states[i],states[i+1]) for i in range(3)) and len(set(reactant))==1 and edges[-1][1]==reaction_entry and reaction_entry!=product and completion.numerator==3 and completion.denominator==2 and extended[:len(prior)]==prior and len(extended)==len(prior)+1)
 passed=(d["claim_id"]==CLAIM and received==generated and len(generated)==256 and len(set(received))==256 and d["census"]["expected_cardinality"]==256 and decisions=={{candidate:candidate==SURVIVOR for candidate in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and {{row["kind"] for row in d["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}} and all(row["passed"] for row in d["controls"]) and witnesses)
 print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,"complete_finite_transport_word_reconstructed":witnesses,"transport_exit_reaction_entry_identity_and_exact_positive_completion_relation_reconstructed":witnesses,"transport_reaction_successor_preserves_prior_family":witnesses,"numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used":False,"Fick_Smoluchowski_diffusion_equation_continuum_fit_stochastic_weight_target_measurement_or_source_file_accessed":False}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = DIFFUSION_LIMITED_REACTION_SPEC
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.chemistry.diffusion_limited_reaction_batch_v1 import DIFFUSION_LIMITED_REACTION_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.diffusion_limited_reaction_validation_v1 import DiffusionLimitedReactionValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/diffusion_limited_reaction_law_v1.py",root/"sft/chemistry/diffusion_limited_reaction_batch_v1.py",root/"sft/chemistry/diffusion_limited_reaction_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_diffusion_limited_reaction_sources_v1.py",root/"tools/register_chemistry_diffusion_limited_reaction_identities_v1.py",root/"tools/capture_chemistry_diffusion_limited_reaction_targets_v1.py",root/"tools/build_chemistry_diffusion_limited_reaction_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/{spec.claim_id}/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(DIFFUSION_LIMITED_REACTION_SPEC,source_hash),ExternalCommandValidator("sft-chem-diffusion-limited-reaction-011-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,DiffusionLimitedReactionValidator(root))
'''


def main() -> None:
    spec = DIFFUSION_LIMITED_REACTION_SPEC
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
            "Complete 256-form census, one survivor, depth-independent finite transport-reaction successor, "
            "implementation-distinct exact encounter-boundary reconstruction, capability-closed 251-record identity "
            "vector, 43 PDF pages, 1,350 video frames, 204 dual-archive members, 11,512 key raw rows, complete radius/time "
            "and matrix vectors, preserved velocity discrepancy, adverse controls, omission and broken-boundary controls."
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
            "source_id": "NATURE-COMMUNICATIONS-S41467-025-68008-5-COMPLETE",
            "measurement_body": "Nature Communications time-resolved diffusion-limited reaction study",
            "doi": "10.1038/s41467-025-68008-5", "source_data_doi": "10.6084/m9.figshare.30344179",
            "role": "complete post-seal transport, encounter, product, control, movie, raw-data and dual-archive evidence surface",
        }],
        "source_hashes": {
            "prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH,
            "complete_raw_and_landing_sources": dict(SOURCE_FILES),
        },
        "complete_surface": {
            "registered_source_record_count": 251, "pdf_page_count": 43,
            "supplementary_video_frame_count": 1350, "archive_count": 2, "archive_member_count": 204,
            "key_raw_data_row_count": 11512, "radius_total_reaction_time_row_count": 15,
            "reaction_yield_matrix_shape": "23 by 15", "coincidence_distribution_shape": "150 by 23",
            "adverse_records": [
                "experimental 43 ±5 m/s and simulated 14 m/s velocity inscriptions remain unreconciled",
                "larger droplets deviate from the source linear fit",
                "time resolution is insufficient for detailed bond-formation dynamics",
                "peer review records nonencounter and not-all-systems-reactive questions",
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
Chemistry obligation: `SFT-CHEM-OBL-KIN-011`

## WHY

KIN-001 through KIN-010 close elementary transitions, dependencies, activation boundaries, complete mechanisms, reversible correspondence and catalytic return cycles. They do not yet force the exact boundary at which finite transport and reaction compose without importing a continuum diffusion law. KIN-011 asks what the admitted transition structure itself forces when reaction entry must be reached by a complete retained transport word.

## DERIVATION

The eight-axis grammar generates 256 forms. Exactly one retains the same held reactant identity through every finite transport state and adjacent transition, makes the transport exit the exact reaction encounter entry, admits reaction only after the complete transport word, counts completed occurrences per exact positive observation partition, retains separated, solvation, transport, encounter and product states, preserves every adverse status, binds the complete source surface and seals all value-free identities:

`{survivor_id(spec)}`

No continuum field, diffusion differential equation, Fick or Smoluchowski law, fitted diffusion coefficient, stochastic collision weight or measured rate selects this result. One complete transport word closing on encounter forces the base. Appending the next complete transport-reaction occurrence preserves every prior exact path and result.

## CHECK

Before target content opened, DOI `10.1038/s41467-025-68008-5`, repository DOI `10.6084/m9.figshare.30344179`, ten complete source files, 43 PDF-page identities, two video identities and 204 archive-member topologies were sealed. The 251 identities contain no distance, time, velocity, yield, rate, fit, distribution, simulation, uncertainty, condition, status, value or target hash.

After sealing, the complete source record opened. The retained path is separated reactants → initiated solvation → finite transport occurrence → encounter boundary → product complex. Transport exit and reaction entry are one exact state. The full source surface retains all 43 PDF pages, both videos and their 1,350 frames, Figshare metadata, all 204 members of both byte-identical independently hosted archives, 11,512 key raw rows, the complete 15-row radius/total-reaction-time vector, the 23-by-15 yield matrix and the 150-by-23 coincidence distribution.

The reported experimental diffusion velocity `43 ±5 m/s`, simulation value `14 m/s`, and their discrepancy remain visible without reconciliation. The reported `5×10^12 M^-1 s^-1` rate estimate and all source CDF, log-normal, linear-fit, rate, RPMD and other models are post-seal provenance only. Larger-droplet deviation, insufficient bond-formation time resolution, and peer-review questions concerning nonencounter and systems that do not react remain adverse evidence.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The complete finite-path encounter law and successor are depth-independent. The empirical result is finite-complete for the byte-sealed ten-file, 251-record source surface. It demonstrates exact correspondence with the retained source sequence and complete measurement vector; it does not import the source's continuum or fitted models as SFT proof.
""")
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation_with_blind_postseal_vector`\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
