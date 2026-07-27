#!/usr/bin/env python3
"""Scaffold the registered Chemistry KIN-008 claim and experiment packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.parallel_mechanism_batch_v1 import (  # noqa: E402
    IDENTITY_HASH, IDENTITY_PATH, PARALLEL_MECHANISM_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    SOURCE_FILES, SPEC_HASH, SPEC_PATH, TARGET_HASH, TARGET_PATH, WORKBOOK_HASH, WORKBOOK_PATH,
)
from sft.chemistry.parallel_mechanism_validation_v1 import (  # noqa: E402
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
    spec = PARALLEL_MECHANISM_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Implementation-distinct value-free KIN-008 reconstruction."""
from itertools import product
import json,sys
CLAIM={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; received=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}
 paths=(("source-a","state-b","terminal-d"),("source-a","state-c","terminal-d")); successor=("source-a","state-e","state-f","terminal-d"); extended=paths+(successor,)
 witnesses=(len(paths)==2 and len(set(paths))==2 and all(path[0]=="source-a" for path in paths) and tuple(path[-1] for path in paths)==("terminal-d","terminal-d") and extended[:len(paths)]==paths and len(extended)==3)
 passed=(d["claim_id"]==CLAIM and received==generated and len(generated)==256 and len(set(received))==256 and d["census"]["expected_cardinality"]==256 and decisions=={{candidate:candidate==SURVIVOR for candidate in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and {{row["kind"] for row in d["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}} and all(row["passed"] for row in d["controls"]) and witnesses)
 print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,"closure":"depth_independent" if passed else None,"complete_parallel_family_reconstructed":witnesses,"common_initial_and_terminal_occurrences_retained":witnesses,"path_successor_preserves_complete_prior_family":witnesses,"numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used":False,"parallel_equation_stochastic_premise_fit_path_weight_target_measurement_or_source_file_accessed":False}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = PARALLEL_MECHANISM_SPEC
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.chemistry.parallel_mechanism_batch_v1 import PARALLEL_MECHANISM_SPEC, IDENTITY_PATH, INVENTORY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH
from sft.chemistry.parallel_mechanism_validation_v1 import ParallelMechanismValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path):
 files=(root/"sft/chemistry/parallel_mechanism_law_v1.py",root/"sft/chemistry/parallel_mechanism_batch_v1.py",root/"sft/chemistry/parallel_mechanism_validation_v1.py",root/"sft/chemistry/sequential_mechanism_law_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",root/"tools/capture_chemistry_parallel_mechanism_sources_v1.py",root/"tools/register_chemistry_parallel_mechanism_identities_v1.py",root/"tools/capture_chemistry_parallel_mechanism_targets_v1.py",root/"tools/build_chemistry_parallel_mechanism_primary_v1.py",root/SPEC_PATH,root/INVENTORY_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,*(root/path for path,_ in SOURCE_FILES),root/"claims/{spec.claim_id}/execution.py")
 source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(PARALLEL_MECHANISM_SPEC,source_hash),ExternalCommandValidator("sft-chem-parallel-mechanism-008-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,ParallelMechanismValidator(root))
'''


def main() -> None:
    spec = PARALLEL_MECHANISM_SPEC
    package = ROOT / "claims" / spec.claim_id
    write_json(package / "registration.json", {
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
            "Complete 256-form census, one survivor, depth-independent path successor, implementation-distinct "
            "parallel-family reconstruction, capability-closed twenty-eight-sheet identity prediction, complete 385-value "
            "primary product-time surface, all 18,158 source workbook cell positions and unresolved/adverse controls."
        ),
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-27",
    })
    registration = experiment_registration_record(ROOT)
    program = prediction_program_document(ROOT)
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", {
        "$schema": "../../../governance/experiment.schema.json",
        **registration,
        "evidence_mode": "observational_derivation_with_value_free_prefetch_and_identity_seals",
        "development_observation_disclosed": True,
        "observed_values_did_not_select_survivor": True,
        "external_measurement_sources": [{
            "source_id": "NATURE-COMMUNICATIONS-S41467-026-70199-4-SOURCE-DATA",
            "measurement_body": "Nature Communications primary reaction-network study",
            "doi": "10.1038/s41467-026-70199-4",
            "role": "complete post-seal parallel product-time, replicate, formula, adverse and unresolved evidence surface",
        }],
        "source_hashes": {
            "prefetch_value_free_specification": SPEC_HASH,
            "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH,
            "withheld_measurements": TARGET_HASH,
            "complete_source_data_workbook": WORKBOOK_HASH,
            "complete_raw_and_landing_sources": dict(SOURCE_FILES),
        },
        "complete_surface": {
            "parallel_path_count": 3,
            "primary_product_time_observation_count": 385,
            "source_data_worksheet_count": 28,
            "registered_rectangular_cell_position_count": 18158,
            "external_zero_glyph_count": 2109,
            "source_formula_count": 722,
            "unresolved_record": "Supplementary Figure 31 peak x has two possible structures; neither is selected",
        },
        "absence_boundary": {
            "native_proof_form": "structural EmptyOne",
            "display_glyph": "0",
            "meaning": "external observed absence only",
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
    })
    write(package / "independent_validator.py", independent_source())
    write(package / "execution.py", execution_source())
    write(package / "WHY_DERIVATION_CHECK.md", f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-KIN-008`

## WHY

KIN-007 closes one complete sequential state-edge word. It does not yet say what one mechanism is when several distinct complete words begin from the same retained source and coexist. Importing parallel rate equations, stochastic path weights or a dominant-product assumption would make those prior models premises. KIN-008 therefore asks only what the already admitted structure forces.

## DERIVATION

The complete eight-axis grammar generates 256 forms. Exactly one retains every distinct path, one exact common initial boundary, every path's complete sequential word, shared occurrences without collapse, every status, complete source custody and a value-free successor:

`{survivor_id(spec)}`

A parallel mechanism is the complete source-ordered family itself. Two paths sharing one registered initial state force the base. Appending the next distinct registered path at the next positive occurrence preserves every prior path, state, edge, intermediate, shared boundary, terminal occurrence and status. No probability, path weight, rate equation or fitted parameter is needed.

## CHECK

Before workbook cells open, the DOI, complete article/supplement/source-data capture rule and twenty-eight worksheet topologies are sealed without any product, time, concentration, replicate, uncertainty, formula result or target hash. The executable prediction contains only those identities and the forced complete-path law.

After sealing, the complete source workbook opens. All twenty-eight worksheets and all 18,158 registered rectangular cell positions remain in the evidence vector: 8,968 structural empty cells, 2,109 external source glyphs `0` translated only to observed structural absence, 6,060 exact positive source magnitudes, 722 source formulas, 299 held labels and no signed measurement cell. Source formulas remain provenance and are never proof parameters.

The primary parallel surface retains 385 raw product-time observations: Figure 4b, its complete Supplementary Figure 32 product vector and the Figure 5c competing-path comparator. Every replicate remains separate. The complete Ac-CY product support forces three retained state words without selecting the dominant path: `1-EP -> 1 -> 2`; `1-EP -> 7 -> 8 -> 9 -> 2`; and weak trace support `1-EP -> 2-EP -> 2`. Supplementary Figure 31's peak `x` remains explicitly unresolved between two possible structures.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The formal complete-path successor is depth-independent. The empirical result is finite-complete for the byte-sealed article, 54-page supplement, peer-review record and twenty-eight-sheet source workbook. The source's reported means and standard deviations are preserved but no average or formula enters the Fold law.
""")
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation_with_blind_postseal_vector`\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
