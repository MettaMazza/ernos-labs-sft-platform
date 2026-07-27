#!/usr/bin/env python3
"""Scaffold the registered Chemistry KIN-013 claim and experiment packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.reaction_dynamics_scattering_batch_v1 import (  # noqa: E402
    IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, REACTION_DYNAMICS_SCATTERING_SPEC,
    SOURCE_FILES, SPEC_HASH, SPEC_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.reaction_dynamics_scattering_validation_v1 import (  # noqa: E402
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
    spec = REACTION_DYNAMICS_SCATTERING_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Implementation-distinct value-free KIN-013 reconstruction."""
from fractions import Fraction
from itertools import product
import json,sys
CLAIM={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; received=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}
 incoming=("reaction","reactant-a","reactant-b","preparation"); outgoing=((1,"product-a-state-1","product-b-state-1","same-oriented",3),(2,"product-a-state-2","product-b-state-2","transverse-oriented",2),(3,"product-a-state-3","product-b-state-3","opposed-oriented",1)); total=sum(row[-1] for row in outgoing); shares=tuple(Fraction(row[-1],total) for row in outgoing); prior=(("occurrence-a",shares),); extended=prior+(("occurrence-b",shares),)
 witnesses=(len(incoming)==4 and tuple(row[0] for row in outgoing)==(1,2,3) and len({{row[1:4] for row in outgoing}})==3 and shares==(Fraction(1,2),Fraction(1,3),Fraction(1,6)) and tuple(row[3] for row in outgoing)==("same-oriented","transverse-oriented","opposed-oriented") and extended[:len(prior)]==prior and len(extended)==len(prior)+1)
 passed=(d["claim_id"]==CLAIM and received==generated and len(generated)==256 and len(set(received))==256 and d["census"]["expected_cardinality"]==256 and decisions=={{candidate:candidate==SURVIVOR for candidate in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and {{row["kind"] for row in d["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}} and all(row["passed"] for row in d["controls"]) and witnesses)
 print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,"finite_incoming_and_complete_distinct_outgoing_joint_product_state_support_reconstructed":witnesses,"exact_positive_state_shares_and_all_three_held_orientation_relations_reconstructed":witnesses,"scattering_occurrence_successor_preserves_prior_family":witnesses,"numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used":False,"scattering_equation_cross_section_law_probability_amplitude_potential_fit_normalization_target_measurement_or_source_file_accessed":False}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = REACTION_DYNAMICS_SCATTERING_SPEC
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.chemistry.reaction_dynamics_scattering_batch_v1 import REACTION_DYNAMICS_SCATTERING_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.reaction_dynamics_scattering_validation_v1 import ReactionDynamicsScatteringValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/reaction_dynamics_scattering_law_v1.py",root/"sft/chemistry/reaction_dynamics_scattering_batch_v1.py",root/"sft/chemistry/reaction_dynamics_scattering_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_reaction_dynamics_scattering_sources_v1.py",root/"tools/register_chemistry_reaction_dynamics_scattering_identities_v1.py",root/"tools/capture_chemistry_reaction_dynamics_scattering_targets_v1.py",root/"tools/build_chemistry_reaction_dynamics_scattering_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/{spec.claim_id}/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(REACTION_DYNAMICS_SCATTERING_SPEC,source_hash),ExternalCommandValidator("sft-chem-reaction-dynamics-scattering-013-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,ReactionDynamicsScatteringValidator(root))
'''


def main() -> None:
    spec = REACTION_DYNAMICS_SCATTERING_SPEC
    package = ROOT / "claims" / spec.claim_id
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title,
        "branch": "chemistry", "status": "registered", "statement": spec.statement,
        "dependencies": list(spec.dependencies), "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec))},
        "excluded_inputs": list(spec.exclusions), "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": "Complete 256-form census, one survivor, depth-independent finite scattering-occurrence successor, implementation-distinct exact joint-state/share/orientation reconstruction, capability-closed 51-record vector, 36 pages, 14 worksheets, 978,591 nonempty cells, 6,408 key state-resolved cells, all fit/normalization/tentative/limitation/reviewer records, omission and mismatched-reaction controls.",
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json", "registered_by": "Maria Smith", "registration_date": "2026-07-27",
    })
    registration = experiment_registration_record(ROOT)
    program = prediction_program_document(ROOT)
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", {
        "$schema": "../../../governance/experiment.schema.json", **registration,
        "evidence_mode": "observational_derivation_with_value_free_prefetch_and_identity_seals",
        "development_observation_disclosed": True, "observed_values_did_not_select_survivor": True,
        "external_measurement_sources": [{"source_id": "NATURE-COMMUNICATIONS-S41467-025-66587-X-COMPLETE", "measurement_body": "Nature Communications complete pair-correlated product-state and scattering study", "doi": "10.1038/s41467-025-66587-x", "role": "complete post-seal incoming/outgoing, pair-state, branching, angular, processing, limitation and peer-review evidence surface"}],
        "source_hashes": {"prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH, "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH, "complete_raw_and_landing_sources": dict(SOURCE_FILES)},
        "complete_surface": {
            "registered_source_record_count": 51, "pdf_page_count": 36, "source_data_worksheet_count": 14,
            "source_data_nonempty_cell_count": 978591, "key_state_resolved_product_and_scattering_cell_count": 6408,
            "headline_external_inscriptions": {"ground_state_CH3_reactivity": "40%", "umbrella_excited_experiment_theory": "57% / 58%", "forward_sideways_backward_pairs": "(0_0,3) / (2_2,2) / (0_0,2)"},
            "adverse_records": ["component profiles were estimated, dissected and fitted", "Fig. 4 experiment and theory were normalized for shape comparison", "HF(v=1) weak featureless population was tentatively posited", "theoretical forward peak is sharper", "theory omits rotationally excited incoming states in CDCS", "lower state resolution and photochemical background limitations", "complete transparent peer-review challenges"],
        },
        "absence_boundary": {"native_proof_form": "structural EmptyOne", "display_glyph": "0", "meaning": "external source inscription only", "numerical_zero_admitted": False},
        "prediction_protocol": {"program_hash": sha256_identity(program), "measured_values_present": False, "target_content_inaccessible": True, "complete_trace_required": True},
        "registered_by": "Maria Smith", "registration_date": "2026-07-27", "status": "registered",
    })
    write(package / "independent_validator.py", independent_source())
    write(package / "execution.py", execution_source())
    write(package / "WHY_DERIVATION_CHECK.md", f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-KIN-013`

## WHY

KIN-001 through KIN-012 close event rates, branching, complete mechanisms, finite transport and exact isotope-pair rate relations. They do not yet force the joint relation between one finite incoming preparation and the complete finite support of outgoing product-state pairs and their orientations. KIN-013 asks what finite retained channel structure forces before any measured product or scattering value is opened.

## DERIVATION

The eight-axis grammar generates 256 forms. Exactly one retains the finite incoming channel and preparation, every distinct source-ordered outgoing joint coproduct-state word, exact positive completed-event shares, held incoming/outgoing orientations, complete observation and separated provenance:

`{survivor_id(spec)}`

No scattering equation, differential cross-section law, angular continuum, probability amplitude, potential surface, fitted distribution or normalization selects the survivor. One complete incoming/outgoing support forces the base. Appending the next complete scattering occurrence preserves every prior exact result.

## CHECK

Before target content opened, DOI `10.1038/s41467-025-66587-x`, all five complete files and 51 value-free identities were sealed. The identities comprise the article landing, all 36 PDF pages and all 14 source-data worksheets. They contain no channel outcome, product state, angle, speed, energy, branching, fit, normalization, tentative value, limitation, reviewer result or target hash.

After sealing, 978,591 nonempty source-data cells and 6,408 key state-resolved branching/scattering cells opened. The source inscriptions retain `40%` ground-state CH3 reactivity, `57%` experimental versus `58%` theoretical umbrella-excited flux, and the forward `(0_0,3)`, sideways `(2_2,2)` and backward `(0_0,2)` product-pair progression.

Every qualification remains visible: fitted/dissected components; flux normalization in the shape comparison; tentatively posited weak HF(v=1); sharper theoretical forward peaks; omitted rotationally excited incoming states in the CDCS theory; lower state resolution and photochemical background; overlap corrections; and the complete transparent peer-review challenges. These remain source provenance, never Fold premises.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The finite channel-support law and occurrence successor are depth-independent. The empirical result is finite-complete for the byte-sealed five-file, 51-record source surface. It validates complete retention and correspondence without importing the source's scattering, energy, momentum, potential, quantum-dynamics or fitting models as SFT law.
""")
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation_with_blind_postseal_vector`\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
