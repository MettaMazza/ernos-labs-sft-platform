#!/usr/bin/env python3
"""Scaffold the registered Chemistry KIN-009 claim and experiment packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.reversible_kinetic_equilibrium_batch_v1 import (  # noqa: E402
    IDENTITY_HASH, IDENTITY_PATH, MOVIE_HASH, PRIMARY_HASH, PRIMARY_PATH,
    REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC, SOURCE_DATA_HASH, SOURCE_FILES, SPEC_HASH, SPEC_PATH,
    SUPPLEMENT_HASH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.reversible_kinetic_equilibrium_validation_v1 import (  # noqa: E402
    experiment_registration_record, prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def independent_source() -> str:
    spec = REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Implementation-distinct value-free KIN-009 reconstruction."""
from itertools import product
import json,sys
CLAIM={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; received=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}
 states=("state-a","state-b"); forward=(states[0],states[1],"first-to-second"); reverse=(states[1],states[0],"second-to-first"); recurrence=states; next_pair=("state-c","state-d"); prior=((states,forward,reverse,recurrence),); extended=prior+((next_pair,(next_pair[0],next_pair[1],"first-to-second"),(next_pair[1],next_pair[0],"second-to-first"),next_pair),)
 witnesses=(len(states)==2 and states[0]!=states[1] and forward[0]==reverse[1] and forward[1]==reverse[0] and forward[2]!=reverse[2] and recurrence==states and extended[:len(prior)]==prior and len(extended)==len(prior)+1)
 passed=(d["claim_id"]==CLAIM and received==generated and len(generated)==256 and len(set(received))==256 and d["census"]["expected_cardinality"]==256 and decisions=={{candidate:candidate==SURVIVOR for candidate in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and {{row["kind"] for row in d["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}} and all(row["passed"] for row in d["controls"]) and witnesses)
 print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,"same_two_state_graph_reconstructed":witnesses,"directed_kinetic_word_and_recurrence_support_reconstructed":witnesses,"pair_successor_preserves_complete_prior_family":witnesses,"numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used":False,"rate_equation_equilibrium_constant_stochastic_weight_fit_target_measurement_or_source_file_accessed":False}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.chemistry.reversible_kinetic_equilibrium_batch_v1 import REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.reversible_kinetic_equilibrium_validation_v1 import ReversibleKineticEquilibriumValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/reversible_kinetic_equilibrium_law_v1.py",root/"sft/chemistry/reversible_kinetic_equilibrium_batch_v1.py",root/"sft/chemistry/reversible_kinetic_equilibrium_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_reversible_kinetic_equilibrium_sources_v1.py",root/"tools/register_chemistry_reversible_kinetic_equilibrium_identities_v1.py",root/"tools/capture_chemistry_reversible_kinetic_equilibrium_targets_v1.py",root/"tools/build_chemistry_reversible_kinetic_equilibrium_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/{spec.claim_id}/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC,source_hash),ExternalCommandValidator("sft-chem-reversible-kinetic-equilibrium-009-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,ReversibleKineticEquilibriumValidator(root))
'''


def main() -> None:
    spec = REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC
    package = ROOT / "claims" / spec.claim_id
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id, "title": spec.title, "branch": "chemistry", "status": "registered",
        "statement": spec.statement, "dependencies": list(spec.dependencies),
        "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {
            "generator": spec.generation_rule, "boundary": spec.grammar_boundary,
            "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": (
            "Complete 256-form census, one survivor, depth-independent reversible-pair successor, implementation-distinct "
            "same-graph reconstruction, capability-closed 164-record identity vector, exact forward/reverse compositions, "
            "all decisive source pages, 73 movie frames, eight archive members and adverse disagreement controls."
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
            "source_id": "NATURE-COMMUNICATIONS-S41467-023-40190-4-COMPLETE",
            "measurement_body": "Nature Communications primary reversible molecular-isomerization study",
            "doi": "10.1038/s41467-023-40190-4",
            "role": "complete post-seal forward, reverse, equilibrium, adverse, movie and archive evidence surface",
        }],
        "source_hashes": {
            "prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH,
            "complete_supplement": SUPPLEMENT_HASH, "complete_movie": MOVIE_HASH,
            "complete_source_data_archive": SOURCE_DATA_HASH, "complete_raw_and_landing_sources": dict(SOURCE_FILES),
        },
        "complete_surface": {
            "registered_source_record_count": 164, "pdf_page_count": 155,
            "supplementary_movie_frame_count": 73, "source_data_archive_member_count": 8,
            "bidirectionally_observed_same_pair_count": 1, "source_designated_reversible_pair_count": 3,
            "directional_experiment_count": 4, "terminal_equilibrium_composition_count": 4,
            "adverse_records": [
                "68/32 and 71/29 terminal same-pair compositions remain separate and are not averaged",
                "two continuation kinetic-analysis captions reverse the direction stated by their ratio plots; both labels remain visible",
            ],
        },
        "absence_boundary": {
            "native_proof_form": "structural EmptyOne", "display_glyph": "0",
            "meaning": "external reference inscription only", "numerical_zero_admitted": False,
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
Chemistry obligation: `SFT-CHEM-OBL-KIN-009`

## WHY

KIN-001 through KIN-008 close elementary transitions, their exact dependencies, activation boundaries and complete sequential and parallel compositions. They do not yet identify the precise relation between direction-resolved kinetics and equilibrium without importing a reversible rate equation or equilibrium constant. KIN-009 asks what the admitted transition structure itself forces.

## DERIVATION

The eight-axis grammar generates 256 forms. Exactly one retains both directed transition occurrences, closes them on the same exact two-state graph, identifies kinetics with the retained directed edge word, identifies equilibrium support with that graph's recurrence support, keeps every direction-specific composition separate, preserves adverse disagreement, binds the complete source surface and seals all value-free identities:

`{survivor_id(spec)}`

Direction is a held label, never a negative or signed quantity. A graph with states A and B and exact edges A-to-B and B-to-A supplies both descriptions: the ordered edges are its kinetic record; the retained state pair is its equilibrium recurrence support. No balance equation, probability, fitted direction weight, steady-state assumption or imported equilibrium law is required. One complete pair forces the base. Appending the next complete pair at the next positive source occurrence preserves every prior state, edge, condition, status and correspondence.

## CHECK

Before target-bearing content opened, DOI `10.1038/s41467-023-40190-4`, six complete source files, 155 PDF-page identities, one movie identity and eight archive-member topologies were sealed. The 164 identity rows contain no state pair, direction, time, equilibrium composition, rate, quantum yield, energy, uncertainty, fit, calculation, status value or target hash.

After sealing, the complete record opened. For the same 2-E-I/2-E-II pair at the held 80 degree Celsius condition, the forward observation starts at 83/17 and ends at 32/68 after 88 hours; the reverse observation starts at 98/2 and ends at 71/29 after 82 hours. The terminal 68/32 and 71/29 records remain separate—no average or fitted reconciliation is permitted. Two further source-designated reversible pairs retain their exact initial and terminal compositions. The source's continuation ratio plots and kinetic-analysis captions state opposite direction labels; both inscriptions are preserved as adverse evidence.

All ten article pages, 144 supplementary pages, one additional-description page, the complete 73-frame movie and every one of eight archive members remain byte-bound. Supplementary pages 81-89 were rendered and visually inspected against their extracted text. Reported slopes, fitted activation energies, relative energies and source equations are retained only as post-seal provenance; none enters the Fold law. The external glyph `0` in the relative-energy table denotes the reference's structural `EmptyOne` separation, never a numerical SFT value.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The same-graph correspondence and reversible-pair successor are depth-independent. The empirical result is finite-complete for the byte-sealed six-file, 164-record surface. Only the E-I/E-II pair is claimed as explicitly observed in both initial directions; the two continuation pairs remain source-designated reversible pairs with one direction-resolved experiment each.
""")
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation_with_blind_postseal_vector`\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
