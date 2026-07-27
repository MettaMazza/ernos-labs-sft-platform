#!/usr/bin/env python3
"""Scaffold all pre-source-sealed foundational Medicine claim packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.medicine.external_bindings import BINDING_BY_CLAIM  # noqa: E402
from sft.medicine.empirical_program import MEDICINE_SPECS, PRE_SOURCE_SEAL_PATH, experiment_registration_record, prediction_program_document, validate_pre_source_seal  # noqa: E402
from sft.medicine.sources import SOURCE_BY_ID  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


EXACT_COUNT_CLAIMS = {
    "SFT-MED-DIAGNOSTIC-ACCURACY-001": "four exact cells from the complete condition-by-test observation product",
    "SFT-MED-EFFICACY-001": "four exact cells from the complete intervention-by-outcome product",
    "SFT-MED-ABSOLUTE-RELATIVE-EFFECT-001": "four exact cells from the complete intervention-by-outcome product",
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def claim_registration(spec) -> dict[str, object]:
    return {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "medicine",
        "subbranch": spec.family,
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "root_theorems": ["SFT-ROOT-THERE-IS-NO-NOTHING"],
        "axioms": [],
        "free_parameters": [],
        "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "completeness_certificate": sha256_identity(completeness_record(spec)), "candidate_count": 256, "unique_survivor": survivor_id(spec)},
        "pre_source_branch_seal": PRE_SOURCE_SEAL_PATH,
        "pre_source_branch_seal_hash": validate_pre_source_seal(ROOT),
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": "Complete content-specific 256-form census, unique survivor, depth-independent certificate, independent reconstruction and post-seal purpose-matched clinical comparison.",
        "empirical_protocol": f"experiments/medicine/{spec.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-27",
    }


def experiment_registration(spec) -> dict[str, object]:
    record = experiment_registration_record(ROOT, spec)
    program = prediction_program_document(spec)
    binding = BINDING_BY_CLAIM[spec.claim_id]
    source_rows = [SOURCE_BY_ID[source_id] for source_id in spec.source_ids]
    exact = EXACT_COUNT_CLAIMS.get(spec.claim_id)
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "blind_authoritative_and_primary_data_correspondence",
        "development_observations": [],
        "complete_branch_pre_source_seal": {"path": PRE_SOURCE_SEAL_PATH, "hash": validate_pre_source_seal(ROOT), "all_72_predictions_sealed_before_source_selection": True},
        "external_measurement_sources": [{"source_id": row.source_id, "measurement_body": row.body, "source_uri": row.source_uri, "snapshot_path": row.snapshot_path, "snapshot_hash": row.snapshot_hash, "evidence_scope": row.evidence_scope, "retrieved_date": "2026-07-27", "custody_role": "post-seal-authority-or-primary-evidence"} for row in source_rows],
        "required_source_features": [{"source_id": row.source_id, "required_fragment": row.fragment} for row in binding.requirements],
        "frozen_relation": {"statement": spec.exact_result, "relation_hash": sha256_identity(spec.exact_result), "dependency_hashes": [sha256_identity(row) for row in spec.dependencies], "candidate_grammar": spec.generation_rule, "exact_domain": spec.grammar_boundary, "target_did_not_select_law": True},
        "withheld_targets": [{"target_id": spec.target_id, "source_ids": list(spec.source_ids), "content_absent_from_target_blind_blueprint": True, "content_withheld_from_prediction": True}],
        "prediction_protocol": {"interpreter_id": "sft-v3-capability-closed-fold-interpreter/1", "program_id": program["program_id"], "program_hash": sha256_identity(program), "executor_id": spec.experiment_id + "-prediction-executor", "complete_trace_required": True, "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"]},
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-source-evaluator",
            "comparison_implementation_hash": sha256_identity(("source-fragment-extraction-and-exact-medicine-label-equality", spec.experiment_id)),
            "metrics": [{"metric_id": "source-derived-structural-correspondence", "definition": "Require every registered fragment in every byte-sealed source and compare its reconstructed categorical record with the sealed consequence.", "unit_protocol": f"Exact structural result: {exact}." if exact else "Conditional categorical clinical relation; patient-, population-, setting- or method-dependent magnitudes remain bounded records.", "all_rows": True}],
            "acceptance_condition": "Every source hash and fragment reproduces, the held label matches exactly, all failed and adverse source rows remain preserved, and the changed control is rejected.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A form missing the clinical carrier is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "A changed snapshot or missing fragment is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "A changed candidate support or prediction is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, an imported law, opaque predictor or forbidden proof value is rejected."},
            {"control_id": "UNFAVORABLE-CORRESPONDENCE", "kind": "unfavorable_measurement", "expected_rejection": "A changed source-derived label fails exact comparison."},
        ],
        "custody_protocol": {"exchange_id": "sft-v3-portable-target-exchange/1", "custodian_id": spec.experiment_id + "-external-target-custodian", "custodian_distinct_from_executor": True, "target_reference_hash": sha256_identity(record["source_references"]), "release_requires_matching_seal": True},
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-every-source-feature, transport/content failure, adverse scientific result and tampered row",
        "stop_condition": "Halt after every target and control is evaluated once, or immediately on any violation.",
        "source_hashes": {row.snapshot_path: row.snapshot_hash for row in source_rows} | {"experiment-registration-record": sha256_identity(record)},
        "registration_date": "2026-07-27",
        "registered_by": "Maria Smith",
        "status": "registered",
    }


def execution_source(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.medicine.empirical_program import BlindMedicineAuthorityValidator, GeneratedEmpiricalMedicineProgram, MEDICINE_SPECS
from sft.verification import ClaimExecution
def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in MEDICINE_SPECS if item.claim_id == {spec.claim_id!r})
    source_files = (
        root / "sft/medicine/obligations.py", root / "sft/medicine/structural_counts.py",
        root / "sft/medicine/generated_law.py", root / "sft/medicine/empirical_program.py",
        root / "sft/medicine/external_bindings.py", root / "sft/medicine/sources.py",
        root / "claims/{spec.claim_id}/execution.py", root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py", root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py", root / "sft/engine/isolation.py", root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalMedicineProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator({spec.claim_id.lower()!r} + "-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files,
        empirical_validator=BlindMedicineAuthorityValidator(root, spec),
    )
'''


def independent_source(spec) -> str:
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Implementation-distinct product validator for {spec.claim_id}."""
from itertools import product
import json
import sys
CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}
def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    passed = (sealed["claim_id"] == CLAIM_ID and received == generated and sealed["census"]["expected_cardinality"] == len(generated) and len(set(received)) == len(generated) and decisions == {{row: row == SURVIVOR for row in generated}} and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent" and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True and {{row["kind"] for row in sealed["controls"]}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}} and all(row["passed"] is True for row in sealed["controls"]))
    print(json.dumps({{"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {{"claim_id": CLAIM_ID, "candidate_count": len(generated), "survivor": SURVIVOR if passed else None}}}}, sort_keys=True))
if __name__ == "__main__": main()
'''


def note(spec) -> str:
    axes = "\n".join(f"- `{row.key}` — reject `{row.choices[0].name}`: {row.choices[0].reason} Admit `{row.admitted_choice.name}`: {row.admitted_choice.reason}" for row in spec.dimensions)
    exact = EXACT_COUNT_CLAIMS.get(spec.claim_id)
    magnitude = f"This claim seals and externally checks **{exact}**." if exact else "This claim closes a conditional clinical relation; it does not turn a patient-, population-, setting- or method-dependent magnitude into a universal constant."
    return f"""# {spec.title}

Claim: `{spec.claim_id}`

## WHY

{spec.statement}

## DERIVATION

Dependencies: {', '.join(f'`{row}`' for row in spec.dependencies)}

Boundary: {spec.grammar_boundary}

Generation: {spec.generation_rule}

The literal eight-axis product contains 256 forms:

{axes}

Exactly one form preserves every registered coordinate:

`{survivor_id(spec)}`

Base: {spec.induction_base}

Successor: {spec.induction_step}

## CHECK

All 72 Medicine predictions and 18,432 candidate forms were sealed before source selection. The capability-closed prediction process cannot read a filesystem, network, clock, environment or target. A distinct post-seal custodian opens every bound source, requires each claim-specific fragment, retains adverse, null, unresolved and failed rows, and compares the reconstructed held label exactly. A changed record must fail.

{magnitude}

External evidence tests the consequence and never selects the Fold grammar.
"""


def main() -> None:
    for spec in MEDICINE_SPECS:
        package = ROOT / "claims" / spec.claim_id
        write(package / "registration.json", json.dumps(claim_registration(spec), indent=2, sort_keys=True) + "\n")
        write(package / "execution.py", execution_source(spec))
        write(package / "independent_validator.py", independent_source(spec))
        write(package / "WHY_DERIVATION_CHECK.md", note(spec))
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments/medicine" / spec.experiment_id
        write(experiment / "registration.json", json.dumps(experiment_registration(spec), indent=2, sort_keys=True) + "\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
