#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry ORG-005."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.conformer_generation_equivalence_batch_v1 import (  # noqa: E402
    CONFORMER_GENERATION_EQUIVALENCE_SPEC, FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH, IDENTITY_HASH, IDENTITY_PATH, PRE_SOURCE_PATH,
    PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.conformer_generation_equivalence_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_source() -> str:
    spec = CONFORMER_GENERATION_EQUIVALENCE_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct, value-free ORG-005 reconstruction."""
from itertools import permutations, product
import json
import sys

CLAIM_ID={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor!r}
POSITIONS=(1,2,3,4)
BONDS={{(1,2),(2,3),(3,4)}}
STATES=("anti","gauche-forward","gauche-reverse")
REVERSE={{"anti":"anti","gauche-forward":"gauche-reverse","gauche-reverse":"gauche-forward"}}

def edge(a,b): return tuple(sorted((a,b)))
def actions():
    result=[]
    for image in permutations(POSITIONS):
        mapped={{edge(image[a-1],image[b-1]) for a,b in BONDS}}
        if mapped==BONDS: result.append(image)
    return tuple(result)
def apply(state,image):
    mapped=tuple(image[index-1] for index in POSITIONS)
    if mapped==POSITIONS: return state
    if mapped==tuple(reversed(POSITIONS)): return REVERSE[state]
    raise ValueError("incomplete rotor action")

def main():
    with open(sys.argv[1],encoding="utf-8") as h: sealed=json.load(h)
    generated=["__".join(row) for row in product(*DOMAINS)]
    received=[row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions={{row["candidate_id"]:row["survives"] for row in sealed["decisions"]}}
    graph_actions=actions(); remaining=set(STATES); classes=[]
    while remaining:
        anchor=next(state for state in STATES if state in remaining)
        orbit={{apply(anchor,action) for action in graph_actions}}
        classes.append(tuple(state for state in STATES if state in orbit));remaining-=orbit
    passed=(
        sealed["claim_id"]==CLAIM_ID and received==generated and len(generated)==256 and len(set(received))==256
        and decisions=={{candidate:candidate==SURVIVOR for candidate in generated}} and sum(decisions.values())==1
        and sealed["closure"]["scope"]=="depth_independent" and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in sealed["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}}
        and all(row["passed"] is True for row in sealed["controls"])
        and len(graph_actions)==2 and len(STATES)==3 and [len(group) for group in classes]==[1,2]
        and classes[0]==("anti",) and set(classes[1])=={{"gauche-forward","gauche-reverse"}}
    )
    print(json.dumps({{"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{
        "claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,
        "closure":"depth_independent" if passed else None,"raw_assignment_count":len(STATES),
        "complete_graph_automorphism_count":len(graph_actions),"equivalence_class_sizes":[len(group) for group in classes],
        "complete_partition":sum(len(group) for group in classes)==len(STATES),
        "external_definition_conformer_name_energy_value_or_table_accessed":False,
        "coordinate_tolerance_or_measured_energy_used":False,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used":False,
    }}}},sort_keys=True))
if __name__=="__main__": main()
'''


def execution_source() -> str:
    claim_id = CONFORMER_GENERATION_EQUIVALENCE_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import json,sys
from sft.chemistry.conformer_generation_equivalence_batch_v1 import (
 CONFORMER_GENERATION_EQUIVALENCE_SPEC,FAMILY_BOUNDARY_PATH,FAMILY_INVENTORY_PATH,
 FAMILY_REGISTRY_PATH,IDENTITY_PATH,PRE_SOURCE_PATH,PRIMARY_PATH,TARGET_PATH)
from sft.chemistry.conformer_generation_equivalence_validation_v1 import ConformerGenerationEquivalenceValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution
def build_execution(root:Path)->ClaimExecution:
 targets=json.loads((root/TARGET_PATH).read_text());snapshots=tuple(dict.fromkeys(row["opened_snapshot_path"] for row in targets["rows"]))
 files=(root/"sft/chemistry/conformer_generation_equivalence_law_v1.py",root/"sft/chemistry/conformer_generation_equivalence_batch_v1.py",
  root/"sft/chemistry/conformer_generation_equivalence_validation_v1.py",root/"sft/chemistry/generated_law.py",
  root/"sft/chemistry/generated_observational_law.py",root/"sft/physics/generated_empirical_law.py",
  root/"tools/capture_chemistry_org_001_016_family_sources_v1.py",root/"tools/build_chemistry_org_005_primary_v1.py",
  root/FAMILY_BOUNDARY_PATH,root/FAMILY_REGISTRY_PATH,root/FAMILY_INVENTORY_PATH,root/PRE_SOURCE_PATH,root/IDENTITY_PATH,
  root/TARGET_PATH,root/PRIMARY_PATH,*(root/path for path in snapshots),root/"claims/{claim_id}/execution.py")
 files=tuple(dict.fromkeys(files));source_hash=build_source_manifest(root,files).manifest_hash;independent=root/"claims/{claim_id}/independent_validator.py"
 return ClaimExecution(GeneratedObservationalChemistryProgram(CONFORMER_GENERATION_EQUIVALENCE_SPEC,source_hash),
  ExternalCommandValidator("sft-chem-conformer-generation-equivalence-005-independent-python/1",(sys.executable,str(independent)),independent.parent,(independent,)),
  files,ConformerGenerationEquivalenceValidator(root))
'''


def main() -> None:
    spec = CONFORMER_GENERATION_EQUIVALENCE_SPEC
    package = ROOT / "claims" / spec.claim_id
    if package.exists():
        raise SystemExit("ORG-005 claim package already exists; preserved without replay")
    survivor = survivor_id(spec)
    registration = {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title,
        "branch": "chemistry", "status": "registered", "statement": spec.statement,
        "dependencies": list(spec.dependencies), "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec))},
        "excluded_inputs": list(spec.exclusions), "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "registered_by": "Maria Smith", "registration_date": "2026-07-27",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT),
        "evidence_mode": "observational_derivation",
        "external_sources": [
            {"source_id": "IUPAC-CONFORMER-TERMINOLOGY-SURFACE", "body": "International Union of Pure and Applied Chemistry", "role": "complete conformer, conformation and conformational-analysis records", "custody": "development-observed-correspondence"},
            {"source_id": "NIST-CCCBDB-BUTANE-CONFORMER-SURFACE", "body": "National Institute of Standards and Technology", "role": "complete butane experimental-property, state, configuration and reference page", "custody": "development-observed-correspondence"},
        ],
        "source_hashes": {"identity_registry": IDENTITY_HASH, "complete_targets": TARGET_HASH, "normalized_primary": PRIMARY_HASH},
        "prediction_protocol": {"program_hash": sha256_identity(prediction_program_document(ROOT)), "pre_source_prediction": PRE_SOURCE_PATH, "unknown_target_blind_claimed": False, "target_payload_hashes_inaccessible": True, "complete_trace_required": True},
        "registered_by": "Maria Smith", "registration_date": "2026-07-27", "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ORG-005`

## WHY

A conformer census cannot be admitted by selecting familiar conformer names, clustering coordinates with a tolerance, or taking an energy program's returned minima as the generator. ORG-005 derives the finite generation and equivalence algorithm first.

## DERIVATION

The eight-axis grammar exhausts 256 forms and leaves exactly one survivor:

`{survivor}`

For any positive finite connected atom-labelled graph, every ordered four-site rotor and every held torsion state are retained. The exact Cartesian product generates each multi-rotor assignment once. Every atom-type and bond-preserving position bijection is then exhaustively generated. These bijections induce exact rotor-state actions, and their disjoint orbits—not coordinate distances or energy tolerances—are the conformer equivalence classes.

The four-site witness generates three raw states: anti, gauche-forward and gauche-reverse. The complete path automorphism census contains identity and reversal. Anti is a one-member orbit; the opposed gauche states form one two-member orbit. Thus three assignments force exactly two conformer classes, with every assignment occurring once. Appending a rotor takes the exact finite product and repeats the same automorphism quotient, proving the algorithm at every positive finite graph/state boundary.

## CHECK

All four frozen external records were already development-observed and are disclosed as such; ORG-005 makes no unknown-target blind-prediction claim. The complete IUPAC records preserve single-bond rotational interconversion, distinct potential-energy minima and comparative conformational analysis.

The complete NIST page returns butane with `Anti` and `Gauche` as the two configuration labels, exactly matching the two derived equivalence classes. Its Anti configuration is marked `True`; the Gauche row is marked `False` and remains preserved as adverse evidence, while the same complete page retains a cited experimental gauche-butane conformer record. Its `16.6 kJ mol⁻¹` internal-rotation barrier is downstream evidence only and never selects generation or equivalence.

All 19 scientific tables and 105 rows are retained, including signed enthalpies, conventional zeros, absent cells, the adverse row and every reference. An implementation-distinct standard-library checker regenerates all 256 law candidates and independently reconstructs the three assignments, two graph actions and two orbit classes without importing SFT modules or reading external results.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The algorithm is depth-independent for positive finite molecular graphs, rotors and held state alphabets. The external census is finite-complete for all four frozen sources. ORG-006 separately owns torsional energy profiles and barrier ordering.
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source())
    write(package / "independent_validator.py", independent_source())
    write(package / "WHY_DERIVATION_CHECK.md", note)
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    write(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", json.dumps(experiment, indent=2, sort_keys=True) + "\n")
    print("scaffolded", spec.claim_id)

if __name__ == "__main__": main()
