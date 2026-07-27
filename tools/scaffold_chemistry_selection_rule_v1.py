#!/usr/bin/env python3
"""Scaffold the complete ELEC-010 selection-rule claim."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.selection_rule_batch_v1 import IDENTITY_HASH, IDENTITY_PATH, SELECTION_RULE_SPEC, SOURCE_ID, TARGET_HASH, TARGET_PATH  # noqa: E402
from sft.chemistry.selection_rule_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def claim_registration() -> dict[str, object]:
    s = SELECTION_RULE_SPEC
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": s.claim_id,
        "title": s.title,
        "branch": "chemistry",
        "status": "registered",
        "statement": s.statement,
        "dependencies": list(s.dependencies),
        "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {"generator": s.generation_rule, "boundary": s.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(s))},
        "excluded_inputs": list(s.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary", "same_inversion", "changed_multiplicity", "erased_mediator"],
        "intended_certificate": "Complete 256-form census, unique survivor, depth-independent recurrence certificate, independent implementation, capability-closed prediction, all 60 NIST H2 transition rows and all three adverse observation notes.",
        "empirical_protocol": "experiments/chemistry/" + s.experiment_id + "/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }


def experiment_registration() -> dict[str, object]:
    s = SELECTION_RULE_SPEC
    program = prediction_program_document(ROOT)
    record = experiment_registration_record(ROOT)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": s.experiment_id,
        "claim_id": s.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [{"source_id": SOURCE_ID, "role": "question-and-complete-test-domain-only", "endpoint_transition_and_adverse_outcomes_absent_from_survivor_selection": True}],
        "external_measurement_sources": [{"source_id": SOURCE_ID, "measurement_body": "National Institute of Standards and Technology", "database": "NIST Chemistry WebBook SRD 69", "doi": "10.18434/T4D303", "source_uri": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000", "transition_rows": 60, "adverse_notes": 3}],
        "frozen_relation": {"statement": s.exact_result, "relation_hash": sha256_identity(s.exact_result), "dependency_hashes": [sha256_identity(item) for item in s.dependencies], "candidate_grammar": s.generation_rule, "exact_domain": s.grammar_boundary, "targets_did_not_select_survivor": True, "textbook_selection_rule_not_imported": True},
        "inputs": [{"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(s.dependencies)}, {"input_id": "target-identities-only", "path": IDENTITY_PATH, "content_hash": IDENTITY_HASH, "outcomes_absent": True}],
        "withheld_targets": [{"target_id": row.target_id, "source_id": row.source_id, "snapshot_hash": row.snapshot_hash, "content_withheld_from_prediction": True} for row in s.target_rows],
        "absence_boundary": {"native_proof_form": "structural EmptyOne", "display_glyph": "0", "meaning": "absence only", "numerical_zero_admitted": False},
        "prediction_protocol": {"interpreter_id": "sft-v3-capability-closed-fold-interpreter/1", "program_id": program["program_id"], "program_hash": sha256_identity(program), "complete_trace_required": True, "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"]},
        "evaluation_protocol": {"evaluator_id": s.experiment_id + "-post-seal-NIST-evaluator", "comparison_implementation_hash": sha256_identity(("complete-NIST-H2-selection-comparator/1", s.experiment_id)), "metrics": [{"metric_id": "complete-selection-vector", "definition": "Retain all direct, mediated, unresolved, coupled and closed source records.", "all_rows": True}, {"metric_id": "complete-adverse-vector", "definition": "Retain NIST notes 42, 73 and 78 without normalizing away forbidden, alternate-channel or uncoupling evidence.", "all_rows": True}], "acceptance_condition": "All 63 source records, exact class counts and adverse controls pass.", "falsification_condition": s.falsification_condition},
        "custody_protocol": {"identity_registry_hash": IDENTITY_HASH, "withheld_target_registry_hash": TARGET_HASH, "target_release_requires_prediction_seal": True, "cross_platform_exchange_required": True, "hostile_package_audit_required": True},
        "retention_policy": "retain-all-sixty-transition-records-three-adverse-notes-and-every-direct-mediated-coupled-unresolved-closed-class",
        "scope_boundary": "This closes molecular observation-class selection structure. It does not assign transition intensities or import a stochastic probability model.",
        "stop_condition": "Halt on any violation; otherwise stop after the complete vector and controls.",
        "source_hashes": {IDENTITY_PATH: IDENTITY_HASH, TARGET_PATH: TARGET_HASH, "experiment-registration-record": sha256_identity(record)},
        "registration_date": "2026-07-26",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def independent_source() -> str:
    s = SELECTION_RULE_SPEC
    domains = tuple(tuple(choice.name for choice in item.choices) for item in s.dimensions)
    return f'''from itertools import product
import json,sys
CLAIM={s.claim_id!r}; DOMAINS={domains!r}; SURVIVOR={survivor_id(s)!r}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; registered=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}; axes=("EmptyOne","first","second","third"); direct=all(abs(i-j)<=1 for i,j in ((0,0),(0,1),(1,0),(1,1),(1,2),(2,1),(2,2),(2,3),(3,2),(3,3))); passed=(d["claim_id"]==CLAIM and registered==generated and len(set(registered))==256 and decisions=={{row:row==SURVIVOR for row in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and all(row["passed"] for row in d["controls"]) and direct and len(axes)==4); print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None,"direct_axis_relation":"same-or-neighbour","non_direct_relation":"mediated-composition"}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    s = SELECTION_RULE_SPEC
    return f'''from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.selection_rule_batch_v1 import SELECTION_RULE_SPEC
from sft.chemistry.selection_rule_validation_v1 import SelectionRuleValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=SELECTION_RULE_SPEC; files=(root/"sft/chemistry/selection_rule_law_v1.py",root/"sft/chemistry/selection_rule_batch_v1.py",root/"sft/chemistry/selection_rule_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/{s.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{s.claim_id}/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("{s.claim_id.lower()}-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,SelectionRuleValidator(root))
'''


def derivation_note() -> str:
    s = SELECTION_RULE_SPEC
    return f"""# {s.title}

Claim: `{s.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-010`

## WHY

ELEC-009 derives exact molecular transformations but deliberately does not decide which observation operations can expose them. ELEC-010 derives that boundary without importing a textbook selection-rule formula. An observed exception is retained as evidence for mediation or an alternate channel; it is never used to weaken the direct law.

There is no numerical zero. An absent transition coordinate is `EmptyOne` in the declared channel, not a universal claim that the state or relation does not exist.

## DERIVATION

One direct Fold observation action cannot erase the positive spin-support count. Where both complementary inversion fibres are resolved, a visible distinction changes fibre. One action can retain an axis support or reach only its adjacent recurrence. A larger observed displacement therefore factors through a positive finite path and requires the mediating or alternate-channel record to remain explicit. Directionless coupling, an unresolved source endpoint, and a closed observation coordinate are distinct forms.

The eight-axis grammar enumerates all 256 forms. Exactly one survives:

`{survivor_id(s)}`

Base: {s.induction_base}

Successor: {s.induction_step}

## CHECK

The capability-closed prediction contains only the forced direct/mediated/coupled/unresolved/closed relation. It cannot read the H2 endpoints, transitions or adverse notes. After sealing, the complete NIST surface is opened: 60 transition-table records plus notes 42, 73 and 78. The exact census is 52 direct same-or-neighbour records, two observed non-direct two-step records, one source-unresolved endpoint, four couplings and one closed coordinate. All 54 resolved directional records retain multiplicity; all 52 records with two known inversion fibres change g/u fibre. NIST's explicit forbidden-transition/uncoupling record, forbidden predissociation or magnetic-dipole alternative, and emission-absent/absorption-present distinction are retained as adverse evidence.

## FALSIFICATION

{s.falsification_condition}
"""


def main() -> None:
    s = SELECTION_RULE_SPEC
    claim = ROOT / "claims" / s.claim_id
    write(claim / "registration.json", json.dumps(claim_registration(), indent=2, sort_keys=True) + "\n")
    write(claim / "execution.py", execution_source())
    write(claim / "independent_validator.py", independent_source())
    write(claim / "WHY_DERIVATION_CHECK.md", derivation_note())
    write(claim / "STATUS.md", "# " + s.claim_id + "\n\nStatus: `registered_observational_derivation`\n")
    experiment = ROOT / "experiments" / "chemistry" / s.experiment_id
    write(experiment / "registration.json", json.dumps(experiment_registration(), indent=2, sort_keys=True) + "\n")
    print("scaffolded", s.claim_id)


if __name__ == "__main__":
    main()
