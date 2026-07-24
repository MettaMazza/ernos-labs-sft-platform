#!/usr/bin/env python3
"""Admit and materialize terminal radioactive topology and half-life law."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.receipt_io import read_receipt  # noqa: E402
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.physics.radioactive_decay_successor_laws_v1 import (  # noqa: E402
    RADIOACTIVE_DECAY_SPEC,
    alpha_representative,
    beta_representative,
    deterministic_halving_partition,
    gamma_representative,
    primitive_transition_classes,
    survival_part,
)
from sft.physics.radioactive_decay_successor_validation_v1 import (  # noqa: E402
    RADIOACTIVE_DECAY_EMPIRICAL_SPEC,
    RAW_HASH,
    RAW_PATH,
    SOURCE_HASH,
    SOURCE_ID,
    SOURCE_PATH,
    measurement_analysis,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / RADIOACTIVE_DECAY_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_radioactive_decay_terminal", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load terminal radioactive decay execution")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def experiment_registration() -> dict[str, object]:
    spec = RADIOACTIVE_DECAY_EMPIRICAL_SPEC
    aggregate = json.loads((ROOT / SOURCE_PATH).read_text(encoding="utf-8"))
    source = aggregate["source"]
    program = prediction_program_document(spec)
    record = experiment_registration_record(spec)
    commitment = sha256_identity((SOURCE_HASH, RAW_HASH, tuple((row.target_id, row.source_id, row.source_locator) for row in spec.target_rows)))
    return {
        "$schema": "../../../governance/experiment.schema.json",
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "evidence_mode": "observational_derivation",
        "development_observations": [{"source_id": SOURCE_ID, "role": "development_only", "content_hash": SOURCE_HASH}],
        "external_measurement_sources": [{
            "source_id": SOURCE_ID,
            "measurement_body": source["measurement_body"],
            "source_uri": source["source_uri"],
            "landing_uri": source["landing_uri"],
            "publication_uri": source["publication_uri"],
            "snapshot_hash": SOURCE_HASH,
            "raw_snapshot_hash": RAW_HASH,
            "retrieved_date": aggregate["retrieval_date"],
            "custody_role": "withheld_target",
        }],
        "frozen_relation": {
            "statement": spec.exact_result,
            "relation_hash": sha256_identity(spec.exact_result),
            "dependency_hashes": [sha256_identity(item) for item in spec.dependencies],
            "candidate_grammar": spec.generation_rule,
            "exact_domain": spec.grammar_boundary,
            "target_did_not_select_law": True,
        },
        "inputs": [{"input_id": "registered-premise", "value_kind": "held-sealed-derivation", "content_hash": sha256_identity(spec.dependencies)}],
        "withheld_targets": [{"target_id": row.target_id, "source_id": row.source_id, "content_withheld_from_prediction": True} for row in spec.target_rows],
        "dimension_unit_boundary": {
            "derived_dimension_carriers": ["SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001"],
            "external_reference_protocol": "The formal law fixes survival at positive half-life counts; NUBASE values and units remain positive post-seal dimensional carriers.",
            "proof_value_policy": "positive-generated-counts-exact-fractions-held-labels-and-empty-form-only",
            "measurement_record_policy": "all-5843-state-5500-decay-row-8718-entry-50-code-and-4700-positive-half-life-records-retained",
        },
        "prediction_protocol": {
            "interpreter_id": "sft-v3-capability-closed-fold-interpreter/1",
            "program_id": program["program_id"],
            "program_hash": sha256_identity(program),
            "executor_id": spec.experiment_id + "-prediction-executor",
            "complete_trace_required": True,
            "forbidden_capabilities": ["clock", "dynamic_import", "environment", "filesystem_read", "filesystem_write", "foreign_function", "network", "subprocess"],
        },
        "evaluation_protocol": {
            "evaluator_id": spec.experiment_id + "-post-seal-evaluator",
            "comparison_implementation_hash": sha256_identity(("exact-complete-nubase2020-decay-mapping", spec.experiment_id, spec.falsification_condition)),
            "metrics": [{
                "metric_id": "complete-mode-topology-and-half-life-vector",
                "definition": "Map every non-abundance mode code, retain every positive numeric half-life/unit/uncertainty and reject the literal only-three-named-code reading.",
                "unit_protocol": "NUBASE time inscriptions remain external; exact half-life-count transport uses positive fractions only.",
                "all_rows": True,
            }],
            "acceptance_condition": "Every NUBASE code maps to the sealed primitives or composition and every positive time carrier transports exact finite survival.",
            "falsification_condition": spec.falsification_condition,
        },
        "controls": [
            {"control_id": "FALSE-PREMISE", "kind": "false_premise", "expected_rejection": "A fourth primitive or literal named-particle-only taxonomy is rejected."},
            {"control_id": "TAMPERED-SOURCE", "kind": "tampered_source", "expected_rejection": "Any changed NUBASE row, code, half-life, uncertainty or source identity is rejected."},
            {"control_id": "TAMPERED-ARTIFACT", "kind": "tampered_artifact", "expected_rejection": "Any changed topology, survival relation, census or trace is rejected."},
            {"control_id": "BOUNDARY", "kind": "boundary", "expected_rejection": "Target access, numerical model zero, continuum exponential, ontic randomness or fitted rate is rejected."},
            {"control_id": "UNFAVORABLE-MEASUREMENT", "kind": "unfavorable_measurement", "expected_rejection": "Omitting proton, neutron, cluster, fission, capture or delayed codes fails."},
        ],
        "custody_protocol": {
            "exchange_id": "sft-v3-portable-target-exchange/1",
            "custodian_id": spec.experiment_id + "-external-target-custodian",
            "custodian_distinct_from_executor": True,
            "target_commitment_hash": commitment,
            "release_requires_matching_seal": True,
        },
        "target_access_policy": "structurally-denied-before-seal",
        "row_retention_policy": "retain-every-state-decay-code-mode-entry-positive-half-life-unit-uncertainty-composition-and-adverse-row",
        "stop_condition": "Halt after every formal, NUBASE, topology, lifetime, custody and adverse row is evaluated once, or immediately on any violation.",
        "source_hashes": {SOURCE_PATH: SOURCE_HASH, RAW_PATH: RAW_HASH, "experiment-registration-record": sha256_identity(record)},
        "registration_date": "2026-07-24",
        "registered_by": "Maria Smith",
        "status": "measured",
    }


def main() -> None:
    spec = RADIOACTIVE_DECAY_SPEC
    empirical = RADIOACTIVE_DECAY_EMPIRICAL_SPEC
    write_json(ROOT / "experiments/physics" / empirical.experiment_id / "registration.json", experiment_registration())
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    if spec.claim_id in existing:
        receipt = read_receipt(ROOT / existing[spec.claim_id]["receipt_path"])
        print(f"retained {spec.claim_id}: {receipt.receipt_hash}")
    else:
        execution = load_execution()
        receipt = EngineRepository(ROOT).execute_official(
            execution.program, execution.independent_validator, execution.source_files, execution.empirical_validator
        )
        print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)

    completed = subprocess.run(
        (sys.executable, str(ROOT / "tools/materialize_empirical_claim_evidence.py"), spec.claim_id, spec.exact_result),
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)

    package = ROOT / "claims" / spec.claim_id
    candidates = json.loads((package / "candidate_census.json").read_text(encoding="utf-8"))
    rows = {row["claim_id"]: row for row in json.loads(census_path.read_text(encoding="utf-8"))["claims"]}
    analysis = measurement_analysis(ROOT)
    write_json(package / "postseal_measurement_analysis.json", analysis)
    write_json(package / "formal_survival_certificate.json", {
        "primitive_transition_classes": [item.__dict__ for item in primitive_transition_classes()],
        "alpha_representative": alpha_representative(),
        "beta_representative": beta_representative(),
        "gamma_representative": gamma_representative(),
        "survival_through_seven": [str(survival_part(rank)) for rank in range(1, 8)],
        "deterministic_path_partitions": [
            {
                key: str(value) if hasattr(value, "numerator") else value
                for key, value in deterministic_halving_partition(depth).items()
            }
            for depth in range(1, 8)
        ],
    })
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "branch": "physics",
        "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": candidates["completeness_certificate_hash"], "generator": spec.generation_rule},
        "claim_id": spec.claim_id,
        "dependencies": list(spec.dependencies),
        "empirical_protocol": f"experiments/physics/{empirical.experiment_id}/registration.json",
        "excluded_inputs": list(spec.exclusions),
        "intended_certificate": "All 1,024 typed forms, one survivor, independent topology/path reconstruction, hostile controls and the complete NUBASE2020 5,843-state/8,718-entry/50-code/4,700-positive-half-life boundary.",
        "provenance_classes": [item.value for item in spec.provenance],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-24",
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "statement": spec.statement,
        "status": "empirically_tested_and_independently_replicated",
        "title": spec.title,
    })

    certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
    (package / "STATUS.md").write_text("\n".join((
        f"# {spec.claim_id}", "", "Status: `empirically_tested_and_independently_replicated`", "",
        "- Protocol: `observational-data-informed_target-inaccessible_sealed-prediction`",
        "- Exactly three primitive transition topologies; alpha, beta and gamma are canonical representatives, not the only named codes.",
        "- Exact deterministic survival: `1/2^k` for every positive finite half-life count `k`.",
        "- Complete NUBASE2020 boundary: 5,843 state rows; 5,500 decay rows; 8,718 entries; 50 codes; 4,700 positive numeric half-lives.",
        f"- Closure: `{certificate['closure_scope']}`",
        f"- Derivation seal: `{certificate['derivation_seal_hash']}`",
        f"- Independent validation: `{certificate['external_validation_hash']}`",
        f"- Post-seal empirical validation: `{certificate['empirical_validation_hash']}`",
        f"- Measurement receipt: `{certificate['measurement_receipt_hash']}`",
        f"- Engine receipt: `{receipt.receipt_hash}`",
        f"- Receipt path: `{rows[spec.claim_id]['receipt_path']}`", "",
    )), encoding="utf-8")

    survivor = "__".join(axis.survivor.name for axis in spec.axes)
    why = [
        f"# {spec.claim_id}: WHY / DERIVATION / CHECK", "", "## WHY", "", spec.statement, "",
        "The successor preserves alpha/beta/gamma as the three primitive representatives while replacing the empirically false literal only-three-named-channel reading with an exhaustive topology and composition law.", "",
        "## DERIVATION", "", f"Grammar boundary: {spec.grammar_boundary}", "",
        f"The ten-axis grammar contains {candidates['expected_cardinality']:,} forms. Exactly one survives:", "", f"`{survivor}`", "",
    ]
    why.extend(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in spec.axes)
    why.extend((
        "", "### Primitive topology", "",
        "- Boundary release/decomposition: alpha, nucleons, clusters and fission.",
        "- Held-label conversion: beta minus/plus, electron capture and double-beta families.",
        "- Internal level de-excitation: gamma/internal transition with retained nucleus and charge.",
        "- Delayed particle and beta-fission modes are ordered compositions, not new primitives.",
        "", "### Exact survival", "",
        "- One complete predecessor pair supplies one retained and one released hidden path.",
        "- Each positive half-life carrier repeats that exact partition, forcing `1/2^k`.",
        "- Every finite survival part is positive; the law never reaches or imports numerical zero.",
        "- A measured dimensional half-life transports the law but cannot select its form.",
        "", f"Base: {spec.induction_base}", "", f"Successor: {spec.induction_step}", "", f"Exact result: {spec.exact_result}", "",
        "## CHECK", "",
        "- Independent Boolean-topology enumeration and hidden-path arithmetic reconstruct the result without source access.",
        "- All 50 NUBASE2020 codes map; no proton, neutron, cluster, capture, fission or delayed mode is omitted.",
        "- Uranium-238/beryllium-8, carbon-14/beryllium-7 and technetium-99m supply release, conversion and de-excitation representatives.",
        "- All 4,700 positive numeric half-life carriers retain their units and reported uncertainties.",
        "- The literal only-three-named-code statement is an adverse control and is rejected explicitly.",
        "", "## EXCLUSIONS", "",
    ))
    why.extend(f"- {item}" for item in spec.exclusions)
    why.append("")
    (package / "WHY_DERIVATION_CHECK.md").write_text("\n".join(why), encoding="utf-8")
    print(completed.stdout.strip())
    print(f"materialized {spec.claim_id}")


if __name__ == "__main__":
    main()
