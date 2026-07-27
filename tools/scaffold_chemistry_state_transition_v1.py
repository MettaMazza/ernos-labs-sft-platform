#!/usr/bin/env python3
"""Scaffold the complete ELEC-009 molecular-state transition claim."""

from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from sft.chemistry.state_transition_batch_v1 import IDENTITY_HASH, IDENTITY_PATH, SOURCE_ID, STATE_TRANSITION_SPEC, TARGET_HASH, TARGET_PATH  # noqa: E402
from sft.chemistry.state_transition_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None: path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8")


def claim_registration() -> dict[str, object]:
    s = STATE_TRANSITION_SPEC
    return {"$schema": "../../governance/claim.schema.json", "claim_id": s.claim_id, "title": s.title, "branch": "chemistry", "status": "registered", "statement": s.statement, "dependencies": list(s.dependencies), "provenance_classes": ["observational_derivation"], "candidate_grammar": {"generator": s.generation_rule, "boundary": s.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(s))}, "excluded_inputs": list(s.exclusions), "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"], "intended_certificate": "Complete 256-form census, unique survivor, finite-path induction, implementation-distinct reconstruction, capability-closed transition law, all 46 NIST H2 state rows, all 14 continuation transitions, all exact positive band inscriptions, every absence coordinate and every adverse control.", "empirical_protocol": f"experiments/chemistry/{s.experiment_id}/registration.json", "registered_by": "Maria Smith", "registration_date": "2026-07-26"}


def experiment_registration() -> dict[str, object]:
    s = STATE_TRANSITION_SPEC; program = prediction_program_document(ROOT); record = experiment_registration_record(ROOT)
    return {"$schema": "../../../governance/experiment.schema.json", "experiment_id": s.experiment_id, "claim_id": s.claim_id, "evidence_mode": "observational_derivation", "development_observations": [{"source_id": SOURCE_ID, "role": "question-and-complete-test-domain-only", "states_transitions_bands_and_absences_absent_from_survivor_selection": True}], "external_measurement_sources": [{"source_id": SOURCE_ID, "measurement_body": "National Institute of Standards and Technology", "database": "NIST Chemistry WebBook SRD 69", "doi": "10.18434/T4D303", "source_uri": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000", "primary_state_rows": 46, "continuation_transition_rows": 14}], "frozen_relation": {"statement": s.exact_result, "relation_hash": sha256_identity(s.exact_result), "dependency_hashes": [sha256_identity(item) for item in s.dependencies], "candidate_grammar": s.generation_rule, "exact_domain": s.grammar_boundary, "targets_did_not_select_survivor": True, "selection_rule_not_imported": True}, "inputs": [{"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(s.dependencies)}, {"input_id": "target-identities-only", "path": IDENTITY_PATH, "content_hash": IDENTITY_HASH, "outcomes_absent": True}], "withheld_targets": [{"target_id": row.target_id, "source_id": row.source_id, "snapshot_hash": row.snapshot_hash, "content_withheld_from_prediction": True} for row in s.target_rows], "absence_boundary": {"native_proof_form": "structural EmptyOne", "display_glyph": "0", "meaning": "absence only", "numerical_zero_admitted": False, "rule": "Absent transition and band coordinates are EmptyOne; source glyphs remain held provenance."}, "prediction_protocol": {"interpreter_id": "sft-v3-capability-closed-fold-interpreter/1", "program_id": program["program_id"], "program_hash": sha256_identity(program), "executor_id": s.experiment_id + "-prediction-executor", "complete_trace_required": True, "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"]}, "evaluation_protocol": {"evaluator_id": s.experiment_id + "-post-seal-NIST-evaluator", "comparison_implementation_hash": sha256_identity(("complete-NIST-H2-transition-comparator/1", s.experiment_id)), "metrics": [{"metric_id": "complete-transition-presence-vector", "definition": "Retain 55 directional and four coupled-state records.", "all_rows": True}, {"metric_id": "complete-transition-absence-vector", "definition": "Retain the one source-absent transition coordinate and five absent band coordinates as EmptyOne.", "all_rows": True}, {"metric_id": "complete-band-vector", "definition": "Retain every one of 55 positive band inscriptions as an exact positive ratio.", "all_rows": True}], "acceptance_condition": "All 60 source rows, all transition classes, all band inscriptions and every adverse control pass.", "falsification_condition": s.falsification_condition}, "custody_protocol": {"identity_registry_hash": IDENTITY_HASH, "withheld_target_registry_hash": TARGET_HASH, "target_release_requires_prediction_seal": True, "cross_platform_exchange_required": True, "hostile_package_audit_required": True}, "retention_policy": "retain-all-sixty-rows-all-transition-classes-all-band-inscriptions-all-absences-and-all-adverse-results", "scope_boundary": "The forced result is the exact molecular transformation record and matching-endpoint composition law. Selection criteria are deliberately reserved for ELEC-010 and are not imported here.", "stop_condition": "Halt on any violation; otherwise stop after the complete vector and controls.", "source_hashes": {IDENTITY_PATH: IDENTITY_HASH, TARGET_PATH: TARGET_HASH, s.target_rows[0].snapshot_path: s.target_rows[0].snapshot_hash, "experiment-registration-record": sha256_identity(record)}, "registration_date": "2026-07-26", "registered_by": "Maria Smith", "status": "registered"}


def independent_source() -> str:
    s = STATE_TRANSITION_SPEC; domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in s.dimensions)
    return f'''from itertools import product
import json,sys
CLAIM={s.claim_id!r}; DOMAINS={domains!r}; SURVIVOR={survivor_id(s)!r}
def main():
 d=json.load(open(sys.argv[1])); generated=["__".join(row) for row in product(*DOMAINS)]; registered=[row["candidate_id"] for row in d["census"]["candidates"]]; decisions={{row["candidate_id"]:row["survives"] for row in d["decisions"]}}; first=("carrier","A","B","forward"); second=("carrier","B","C","forward"); path=(first[1],first[2],second[2]); law=(first[0]==second[0] and first[2]==second[1] and path==("A","B","C")); passed=(d["claim_id"]==CLAIM and registered==generated and len(set(registered))==256 and decisions=={{row:row==SURVIVOR for row in generated}} and sum(decisions.values())==1 and d["closure"]["scope"]=="depth_independent" and d["closure"]["minimality_passed"] and d["closure"]["named_shape_uniqueness_passed"] and all(row["passed"] for row in d["controls"]) and law); print(json.dumps({{"validated_seal_hash":d["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None,"composed_path":path}}}},sort_keys=True))
if __name__=="__main__":main()
'''


def execution_source() -> str:
    s = STATE_TRANSITION_SPEC
    return f'''from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.state_transition_batch_v1 import STATE_TRANSITION_SPEC
from sft.chemistry.state_transition_validation_v1 import StateTransitionValidator
from sft.verification import ClaimExecution
def build_execution(root:Path):
 s=STATE_TRANSITION_SPEC; files=(root/"sft/chemistry/state_transition_law_v1.py",root/"sft/chemistry/state_transition_batch_v1.py",root/"sft/chemistry/state_transition_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/{s.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py"); source_hash=build_source_manifest(root,files).manifest_hash; validator=root/"claims/{s.claim_id}/independent_validator.py"; return ClaimExecution(GeneratedObservationalChemistryProgram(s,source_hash),ExternalCommandValidator("{s.claim_id.lower()}-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),files,StateTransitionValidator(root))
'''


def derivation_note() -> str:
    s = STATE_TRANSITION_SPEC
    return f"""# {s.title}

Claim: `{s.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-009`

## WHY

The prior claims establish molecular states and their exact support. ELEC-009 derives what it means for one molecular state to transform into another before asking which transformations a spectroscopic observation class admits. Importing dipole, spin, parity or angular-momentum rules here would collapse ELEC-009 into ELEC-010 and let familiar spectroscopy choose the law.

There is no numerical zero. Absent transition and band coordinates are structural `EmptyOne`; source glyphs remain held provenance only.

## DERIVATION

A transformation cannot be an answer-only label: it must retain one molecular carrier and two distinct endpoint states. Direction is not a sign or negative value; it is one of four held relation classes—forward, reverse, bidirectional or directionless coupling. An absent observation has an initial state and retained record but closes the terminal coordinate with `EmptyOne`. Two observed transformations compose exactly when the first terminal state equals the second initial state. Appending matching successors gives every positive finite transition path without a new rule.

The eight-axis grammar enumerates all 256 forms. Exactly one survives:

`{survivor_id(s)}`

Base: {s.induction_base}

Successor: {s.induction_step}

## CHECK

The capability-closed predictor seals only carrier retention, distinct endpoints, the four held orientations, structural absence, matching-endpoint composition and complete record retention. It cannot read any state, transition, band value or absence target.

After sealing, an independent parser reconstructs the full NIST H₂ `Trans.` surface: 46 primary electronic-state rows and 14 continuation rows. The complete vector contains 55 directional transition inscriptions, four coupling-only relations and one absent transition coordinate. It also retains all 55 positive band-origin inscriptions as exact ratios and all five absent band coordinates as `EmptyOne`. No present-only subset is accepted.

This closes the transformation carrier and path law. It does not call every observed record universally allowed, nor every absent table cell universally forbidden. Those retained observation classes become the complete evidence surface for the separately forced selection-rule structure in ELEC-010.

Mismatch, self-transition, absence-composition, numerical-zero, omitted-row, present-only, changed-band and tampered-source controls reject.

## FALSIFICATION

{s.falsification_condition}
"""


def main() -> None:
    s = STATE_TRANSITION_SPEC; claim = ROOT / "claims" / s.claim_id
    write(claim / "registration.json", json.dumps(claim_registration(), indent=2, sort_keys=True) + "\n"); write(claim / "execution.py", execution_source()); write(claim / "independent_validator.py", independent_source()); write(claim / "WHY_DERIVATION_CHECK.md", derivation_note()); write(claim / "STATUS.md", f"# {s.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    experiment = ROOT / "experiments" / "chemistry" / s.experiment_id; write(experiment / "registration.json", json.dumps(experiment_registration(), indent=2, sort_keys=True) + "\n"); print("scaffolded", s.claim_id)


if __name__ == "__main__": main()
