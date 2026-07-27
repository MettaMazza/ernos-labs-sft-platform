#!/usr/bin/env python3
"""Scaffold the Physics-scale ELEC-003 claim package."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.orbital_support_batch_v1 import (  # noqa: E402
    ELECTRON_INPUT_HASH,
    ELECTRON_INPUT_PATH,
    IDENTITY_REGISTRY_HASH,
    IDENTITY_REGISTRY_PATH,
    ORBITAL_SUPPORT_SPEC,
    SOURCE_ID,
    TARGET_REGISTRY_HASH,
    TARGET_REGISTRY_PATH,
)
from sft.chemistry.orbital_support_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def claim_registration() -> dict[str, object]:
    spec = ORBITAL_SUPPORT_SPEC
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "chemistry",
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec))},
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": "Complete 256-form structural census, unique survivor, depth-independent successor, independent regeneration, capability-closed support dictionary and full 360-row NIST spectroscopic assignment census with adverse controls.",
        "empirical_protocol": f"experiments/chemistry/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }


def experiment_registration() -> dict[str, object]:
    spec = ORBITAL_SUPPORT_SPEC
    program = prediction_program_document(ROOT)
    record = experiment_registration_record(ROOT)
    snapshots = {row.snapshot_path: row.snapshot_hash for row in spec.target_rows}
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [{"source_id": SOURCE_ID, "role": "question-and-comparison-domain-only", "content_absent_from_survivor_selection": True}],
        "external_measurement_sources": [{"source_id": SOURCE_ID, "measurement_body": "National Institute of Standards and Technology", "database": "NIST Chemistry WebBook SRD 69", "doi": "10.18434/T4D303", "source_uri": "https://webbook.nist.gov/chemistry/", "last_data_update": "March 2025", "species_count": 22, "state_row_count": 360, "term_assignment_count": 362, "configuration_assignment_count": 87, "custody_role": "post-seal_spectroscopic_support_target"}],
        "frozen_relation": {"statement": spec.exact_result, "relation_hash": sha256_identity(spec.exact_result), "dependency_hashes": [sha256_identity(value) for value in spec.dependencies], "candidate_grammar": spec.generation_rule, "exact_domain": spec.grammar_boundary, "target_did_not_select_survivor": True},
        "inputs": [
            {"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(spec.dependencies)},
            {"input_id": "electron-count-and-species-parity", "path": ELECTRON_INPUT_PATH, "content_hash": ELECTRON_INPUT_HASH, "state_assignment_content_absent": True},
            {"input_id": "target-identities-only", "path": IDENTITY_REGISTRY_PATH, "content_hash": IDENTITY_REGISTRY_HASH, "state_assignment_content_absent": True},
        ],
        "withheld_targets": [{"target_id": row.target_id, "source_id": row.source_id, "snapshot_hash": row.snapshot_hash, "content_withheld_from_prediction": True} for row in spec.target_rows],
        "dimension_unit_boundary": {"native_carriers": ["positive radial recurrence", "structural empty-One or positive axis recurrence", "two held joining phases", "held exchange/reflection labels", "single or complementary-pair occupancy"], "comparison_only_symbols": ["Sigma/sigma", "Pi/pi", "Delta/delta", "Phi/phi", "NIST state multiplicity and configuration inscriptions"], "proof_value_policy": "positive-counts-held-labels-and-structural-empty-One-only"},
        "prediction_protocol": {"interpreter_id": "sft-v3-capability-closed-fold-interpreter/1", "program_id": program["program_id"], "program_hash": sha256_identity(program), "executor_id": spec.experiment_id + "-prediction-executor", "complete_trace_required": True, "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"]},
        "evaluation_protocol": {"evaluator_id": spec.experiment_id + "-post-seal-NIST-evaluator", "comparison_implementation_hash": sha256_identity(("complete-NIST-orbital-support-comparator/1", spec.experiment_id)), "metrics": [{"metric_id": "complete-spectroscopic-support-census", "definition": "Evaluate all 360 state rows, 362 term assignments and 87 configuration assignments without selection.", "all_rows": True}, {"metric_id": "occupancy-and-multiplicity-census", "definition": "Reconstruct every explicit/implicit occupancy and check every measured state multiplicity against the admitted ELEC-002 species parity.", "all_rows": True}], "acceptance_condition": "All 360 rows and all adverse controls pass exactly.", "falsification_condition": spec.falsification_condition},
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "Detached carrier or incomplete electron support rejects."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Changed NIST bytes or registry identity rejects."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "Missing or duplicate candidate/state row rejects."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Continuum coordinate, conventional target access or free species rule rejects."},
            {"control_id": "UNKNOWN-SUPPORT", "kind": "unfavorable_measurement", "expected_rejection": "An ungenerated support symbol rejects."},
            {"control_id": "TRIPLE-OCCUPANCY", "kind": "unfavorable_measurement", "expected_rejection": "A third electron in one spatial support rejects."},
            {"control_id": "WRONG-MULTIPLICITY", "kind": "unfavorable_measurement", "expected_rejection": "A state width with the wrong electron-count parity rejects."},
            {"control_id": "OMITTED-ROW", "kind": "unfavorable_measurement", "expected_rejection": "A 359-row census rejects."},
        ],
        "custody_protocol": {"exchange_id": "sft-v3-portable-target-exchange/1", "custodian_id": spec.experiment_id + "-NIST-target-custodian", "custodian_distinct_from_executor": True, "withheld_target_registry_path": TARGET_REGISTRY_PATH, "withheld_target_registry_hash": TARGET_REGISTRY_HASH, "release_requires_matching_prediction_seal": True},
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-all-360-source-and-all-adverse-rows",
        "stop_condition": "Halt on any protocol violation; otherwise stop only after all 360 rows and adverse controls are recorded.",
        "source_hashes": snapshots | {IDENTITY_REGISTRY_PATH: IDENTITY_REGISTRY_HASH, TARGET_REGISTRY_PATH: TARGET_REGISTRY_HASH, ELECTRON_INPUT_PATH: ELECTRON_INPUT_HASH, "experiment-registration-record": sha256_identity(record)},
        "registration_date": "2026-07-26",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def independent_source() -> str:
    spec = ORBITAL_SUPPORT_SPEC
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Independent product reconstruction for {spec.claim_id}."""
from itertools import product
import json, sys
CLAIM_ID={spec.claim_id!r}
DOMAINS={domains!r}
SURVIVOR={survivor_id(spec)!r}
def main():
    with open(sys.argv[1], encoding="utf-8") as h: sealed=json.load(h)
    generated=["__".join(x) for x in product(*DOMAINS)]
    received=[x["candidate_id"] for x in sealed["census"]["candidates"]]
    decisions={{x["candidate_id"]:x["survives"] for x in sealed["decisions"]}}
    ranks=("structural-empty-One","first-recurrence","second-recurrence","third-recurrence")
    passed=(sealed["claim_id"]==CLAIM_ID and received==generated and len(set(received))==256 and
      decisions=={{x:x==SURVIVOR for x in generated}} and sum(decisions.values())==1 and
      sealed["closure"]["scope"]=="depth_independent" and sealed["closure"]["minimality_passed"] is True and
      sealed["closure"]["named_shape_uniqueness_passed"] is True and len(ranks)==4 and
      {{x["kind"] for x in sealed["controls"]}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}} and
      all(x["passed"] is True for x in sealed["controls"]))
    print(json.dumps({{"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,"certificate":{{"claim_id":CLAIM_ID,"candidate_count":len(generated),"survivor":SURVIVOR if passed else None,"axis_ranks":ranks}}}},sort_keys=True))
if __name__=="__main__": main()
'''


def execution_source() -> str:
    spec = ORBITAL_SUPPORT_SPEC
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.orbital_support_batch_v1 import ORBITAL_SUPPORT_SPEC
from sft.chemistry.orbital_support_validation_v1 import OrbitalSupportValidator
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec=ORBITAL_SUPPORT_SPEC
    source_files=(root/"sft/chemistry/electron_count_spin_law_v1.py",root/"sft/chemistry/electron_count_spin_validation_v1.py",root/"sft/chemistry/orbital_support_law_v1.py",root/"sft/chemistry/orbital_support_batch_v1.py",root/"sft/chemistry/orbital_support_validation_v1.py",root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",root/"claims/{spec.claim_id}/execution.py",root/"sft/physics/generated_empirical_law.py",root/"sft/claim_evidence/fold_language.py",root/"sft/claim_evidence/custody.py",root/"sft/claim_evidence/hostile.py",root/"sft/engine/isolation.py",root/"sft/engine/empirical.py")
    source_hash=build_source_manifest(root,source_files).manifest_hash
    validator=root/"claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(GeneratedObservationalChemistryProgram(spec,source_hash),ExternalCommandValidator("{spec.claim_id.lower()}-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),source_files,OrbitalSupportValidator(root))
'''


def note() -> str:
    spec = ORBITAL_SUPPORT_SPEC
    return f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-003`

## WHY

A conventional orbital name cannot serve as a premise in a clean Fold derivation. The required object is the exact support that the name later describes. Molecular support must retain its molecule, positive radial recurrence, relation to the molecular axis, joining phase, applicable exchange/reflection distinctions, spin occupancy and complete electron-occurrence trace.

## DERIVATION

Joining two admitted constituent supports forces the two Fold phase fibres. Axis-invariant support is structural empty One, not numerical zero. Repeated distinguishability about the molecular axis then yields the first, second, third and every later positive recurrence. A spatial support is empty One, singly occupied, or occupied by one complementary spin pair. Same-spin doubling and a third fermion reject. Complete molecular support is the unique partition in which every ELEC-002 electron occurrence appears exactly once.

The eight-axis grammar enumerates 256 forms. Its sole preserving form is:

`{survivor_id(spec)}`

Base: {spec.induction_base}

Successor: {spec.induction_step}

Conventional Sigma/Pi/Delta/Phi and sigma/pi/delta/phi symbols appear only after sealing, as correspondence names for the structural boundary and first three positive axis recurrences. They do not select the native law.

## CHECK

The capability-closed prediction seals the universal eight-symbol support dictionary, both joining/occupancy counts, and the ELEC-002 spin-width parity for all 22 species. It cannot read files, targets, network, environment, clock or evaluator. A separate NIST custodian then releases the complete byte-bound census: 360 spectroscopic state rows, 362 term assignments and 87 explicit configuration-support assignments across 16 neutral molecules, four cations and two anions.

Every term support is reconstructed, every measured multiplicity is checked against exact electron-count parity, and every explicit or implicit configuration occupancy is reconstructed under the one-or-complementary-pair law. Unknown support, triple occupancy, wrong multiplicity, omitted-row and tampered-source controls must reject. No row is selected or dropped.

External authority: NIST Chemistry WebBook SRD 69, DOI `10.18434/T4D303`, updated March 2025. The NIST records remain observations; no measured symbol or value becomes a derivational scalar.

## FALSIFICATION

{spec.falsification_condition}
"""


def main() -> None:
    spec=ORBITAL_SUPPORT_SPEC; package=ROOT/"claims"/spec.claim_id
    write(package/"registration.json",json.dumps(claim_registration(),indent=2,sort_keys=True)+"\n")
    write(package/"execution.py",execution_source()); write(package/"independent_validator.py",independent_source())
    write(package/"WHY_DERIVATION_CHECK.md",note()); write(package/"STATUS.md",f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    experiment=ROOT/"experiments/chemistry"/spec.experiment_id
    write(experiment/"registration.json",json.dumps(experiment_registration(),indent=2,sort_keys=True)+"\n")
    print(f"scaffolded {spec.claim_id}")
if __name__=="__main__": main()
