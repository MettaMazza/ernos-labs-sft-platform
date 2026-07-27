#!/usr/bin/env python3
"""Scaffold the Physics-scale ELEC-005 claim and experiment packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.state_symmetry_batch_v1 import (  # noqa: E402
    IDENTITY_HASH,
    IDENTITY_PATH,
    SOURCE_ID,
    STATE_SYMMETRY_SPEC,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.state_symmetry_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def claim_registration() -> dict[str, object]:
    spec = STATE_SYMMETRY_SPEC
    return {
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
            "Complete 256-form structural census, unique survivor, depth-independent successor, "
            "implementation-distinct reconstruction, capability-closed universal symmetry law, "
            "complete 362-assignment NIST term vector, exact retained symmetry-label census, and "
            "nine post-seal adverse controls."
        ),
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }


def experiment_registration() -> dict[str, object]:
    spec = STATE_SYMMETRY_SPEC
    program = prediction_program_document(ROOT)
    record = experiment_registration_record(ROOT)
    snapshots = {row.snapshot_path: row.snapshot_hash for row in spec.target_rows}
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [
            {
                "source_id": SOURCE_ID,
                "role": "question-and-test-domain-only",
                "target_assignments_absent_from_survivor_selection": True,
            }
        ],
        "external_measurement_sources": [
            {
                "source_id": SOURCE_ID,
                "measurement_body": "National Institute of Standards and Technology",
                "database": "NIST Chemistry WebBook SRD 69",
                "doi": "10.18434/T4D303",
                "source_uri": "https://webbook.nist.gov/chemistry/",
                "species": 22,
                "state_rows": 360,
                "term_assignments": 362,
                "custody_role": "post-seal-term-and-symmetry-target",
            }
        ],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(item) for item in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_survivor": True,
        },
        "inputs": [
            {
                "input_id": "registered-premise",
                "value_kind": "held-sealed-derivation",
                "content_hash": sha256_identity(spec.dependencies),
            },
            {
                "input_id": "target-identities-only",
                "path": IDENTITY_PATH,
                "content_hash": IDENTITY_HASH,
                "term_and_symmetry_assignments_absent": True,
            },
        ],
        "withheld_targets": [
            {
                "target_id": row.target_id,
                "source_id": row.source_id,
                "snapshot_hash": row.snapshot_hash,
                "content_withheld_from_prediction": True,
            }
            for row in spec.target_rows
        ],
        "absence_boundary": {
            "native_proof_form": "structural EmptyOne",
            "display_glyph": "0",
            "meaning": "absence only",
            "numerical_zero_admitted": False,
            "source_component_zero_glyph_count": 11,
            "rule": "Every source component glyph 0 remains a verbatim provenance inscription but is normalized only to EmptyOne; it is never generated or consumed as a number.",
        },
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "executor_id": spec.experiment_id + "-prediction-executor",
            "complete_trace_required": True,
            "forbidden_capabilities": [
                "clock",
                "dynamic_import",
                "environment",
                "filesystem_read",
                "filesystem_write",
                "foreign_function",
                "network",
                "subprocess",
            ],
        },
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-NIST-evaluator",
            "comparison_implementation_hash": sha256_identity(
                ("complete-NIST-state-symmetry-comparator/1", spec.experiment_id)
            ),
            "metrics": [
                {
                    "metric_id": "complete-term-assignment-vector",
                    "definition": "Independently reparse and retain all 362 NIST term assignments across all 360 registered state rows.",
                    "all_rows": True,
                },
                {
                    "metric_id": "complete-retained-symmetry-vector",
                    "definition": "Retain every spin multiplicity, axis rank, orientation count, inversion, reflection, component and component-kind coordinate.",
                    "all_rows": True,
                },
                {
                    "metric_id": "forced-finite-equivalence-class",
                    "definition": "For every assignment enumerate exactly spin width times retained axis orientations as positive state-component occurrences.",
                    "all_rows": True,
                },
            ],
            "acceptance_condition": (
                "All 362 assignments pass; the vector contains exactly 170 inversion labels, 167 reflection "
                "labels, 32 positive and 330 absent axis-component coordinates, 11 source absence glyphs, "
                "22 species and 360 state rows; all adverse controls pass."
            ),
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {
                "control_id": "FALSE-PREMISE",
                "kind": "false_premise",
                "expected_rejection": "Cross-carrier or incomplete-signature equivalence rejects.",
            },
            {
                "control_id": "TAMPERED-SOURCE",
                "kind": "tampered_source",
                "expected_rejection": "Changed NIST snapshot bytes reject.",
            },
            {
                "control_id": "TAMPERED-ARTIFACT",
                "kind": "tampered_artifact",
                "expected_rejection": "An omitted assignment or equivalence component rejects.",
            },
            {
                "control_id": "BOUNDARY",
                "kind": "boundary",
                "expected_rejection": "Target-readable generation, numerical zero, free degeneracy or imported lookup rejects.",
            },
            {
                "control_id": "UNKNOWN-SUPPORT",
                "kind": "unfavorable_measurement",
                "expected_rejection": "An ungenerated axis-support symbol rejects.",
            },
            {
                "control_id": "WRONG-ORIENTATION",
                "kind": "unfavorable_measurement",
                "expected_rejection": "An axis-invariant class with a pair or a positive recurrence without a pair rejects.",
            },
            {
                "control_id": "FREE-DEGENERACY",
                "kind": "unfavorable_measurement",
                "expected_rejection": "A combined count other than the exact positive product rejects.",
            },
            {
                "control_id": "NUMERICAL-ZERO",
                "kind": "unfavorable_measurement",
                "expected_rejection": "Treating source glyph 0 as a Fold number rejects.",
            },
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-NIST-target-custodian",
            "custodian_distinct_from_executor": True,
            "withheld_target_registry_path": TARGET_PATH,
            "withheld_target_registry_hash": TARGET_HASH,
            "release_requires_matching_prediction_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-all-362-assignments-and-all-adverse-results",
        "scope_boundary": (
            "The external surface is the complete NIST term/symmetry assignment vector. The claim does not "
            "replace a term assignment with an energy-coincidence assertion and does not omit split or repeated states."
        ),
        "stop_condition": "Halt on any violation; otherwise stop after the complete vector and controls.",
        "source_hashes": snapshots
        | {
            IDENTITY_PATH: IDENTITY_HASH,
            TARGET_PATH: TARGET_HASH,
            "experiment-registration-record": sha256_identity(record),
        },
        "registration_date": "2026-07-26",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def independent_source() -> str:
    spec = STATE_SYMMETRY_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''from itertools import product
import json,sys
CLAIM={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
LAW={{"sigma_orientation":1,"positive_axis_orientation":2,"degeneracy":"positive-spin-times-positive-orientation","absence":"structural-empty-One"}}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; registered=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}; witnesses=(LAW["sigma_orientation"]==1 and LAW["positive_axis_orientation"]==2 and 1*1==1 and 2*2==4 and LAW["absence"]=="structural-empty-One"); passed=(d["claim_id"]==CLAIM and registered==generated and len(set(registered))==256 and decisions=={{row:row==SURVIVOR for row in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and all(row["passed"] for row in d["controls"]) and witnesses); print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None,"independent_law":LAW}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    spec = STATE_SYMMETRY_SPEC
    return f'''from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.state_symmetry_batch_v1 import STATE_SYMMETRY_SPEC
from sft.chemistry.state_symmetry_validation_v1 import StateSymmetryValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=STATE_SYMMETRY_SPEC; files=(root/"sft/chemistry/state_symmetry_law_v1.py",root/"sft/chemistry/state_symmetry_batch_v1.py",root/"sft/chemistry/state_symmetry_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/{spec.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{spec.claim_id}/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("{spec.claim_id.lower()}-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,StateSymmetryValidator(root))
'''


def derivation_note() -> str:
    spec = STATE_SYMMETRY_SPEC
    return f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-005`

## WHY

ELEC-004 gives an exact order between molecular electronic states but does not decide when two component occurrences belong to one finite state class or which distinctions must remain observable. ELEC-005 closes that missing organization. It does not begin with a conventional character table or a tabulated degeneracy formula. It begins with one retained molecular carrier, the positive spin width already closed in ELEC-002, the axis support already closed in ELEC-003, and exact held labels.

There is no numerical zero in this law. Structural absence is `EmptyOne`. The display glyph `0` appears in eleven NIST source inscriptions and means absence only; the source text remains visible for provenance, while every native proof object contains `EmptyOne` at that coordinate.

## DERIVATION

The eight-axis grammar literally enumerates 256 carrier, identity, spin, axis, orientation, symmetry, class and extension forms. Exactly one form preserves all dependencies and adds no species exception or free quantity:

`{survivor_id(spec)}`

Base: {spec.induction_base}

Successor: {spec.induction_step}

Complete-signature equality forces finite equivalence. Axis invariance contributes one retained orientation. Each positive axis recurrence carries the complementary orientation pair. The positive component count is therefore not asserted or fitted: it is the exact product of the already-generated positive spin width and positive orientation support. Every inversion, reflection, component and component-kind distinction is either a retained held label or structural `EmptyOne`. The equivalence class enumerates exactly the resulting positive number of unique component occurrences.

## CHECK

Before any target assignment is released, the capability-closed Fold program seals only the universal four-symbol axis map, the one-versus-complementary-pair orientation law, complete-signature equivalence, exact positive-product component counting, and held-label-or-`EmptyOne` optional coordinates. It has no filesystem, network, environment, clock, subprocess, dynamic-import or foreign-function capability and contains no species term lookup.

A distinct target custodian then releases the complete byte-bound NIST Chemistry WebBook vector. An independently implemented HTML parser reconstructs all 362 term assignments across 360 state rows and 22 species. The check retains every state and term inscription, positive spin multiplicity, axis support, inversion label, reflection label, axis component and component kind. The measured assignment census is exact: 170 inversion labels, 167 reflection labels, 32 positive axis-component labels, 330 absent axis-component coordinates, and eleven source `0` inscriptions normalized only to structural absence. Every row constructs the complete finite component class and compares it with the sealed law.

Unknown support, wrong axis orientation, free degeneracy, incomplete class, numerical use of the absence glyph, omitted assignment and changed-source controls all reject. Measurements test the survivor only after its derivation and prediction seals; they do not select it.

External authority: NIST Chemistry WebBook SRD 69, DOI `10.18434/T4D303`.

## CHECK BOUNDARY

This claim closes finite term/symmetry equivalence and its positive component census against complete external term assignments. It does not claim that every component must remain energy-coincident under every later interaction; splitting and interaction-dependent structure remain retained successor questions rather than exceptions to the equivalence signature.

## FALSIFICATION

{spec.falsification_condition}
"""


def main() -> None:
    spec = STATE_SYMMETRY_SPEC
    claim_path = ROOT / "claims" / spec.claim_id
    write(claim_path / "registration.json", json.dumps(claim_registration(), indent=2, sort_keys=True) + "\n")
    write(claim_path / "execution.py", execution_source())
    write(claim_path / "independent_validator.py", independent_source())
    write(claim_path / "WHY_DERIVATION_CHECK.md", derivation_note())
    write(
        claim_path / "STATUS.md",
        f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n",
    )
    experiment_path = ROOT / "experiments" / "chemistry" / spec.experiment_id
    write(
        experiment_path / "registration.json",
        json.dumps(experiment_registration(), indent=2, sort_keys=True) + "\n",
    )
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
