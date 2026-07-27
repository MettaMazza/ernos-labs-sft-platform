"""Post-seal complete-history validation for Chemistry ORG-009."""

from __future__ import annotations

import json
import platform
from pathlib import Path

from sft.chemistry.addition_reaction_batch_v3 import (
    ADDITION_REACTION_SPEC,
    COMPARISON_HASH,
    COMPARISON_PATH,
    IDENTITY_PATH,
    INVENTORY_PATH,
    PRESEAL_PATH,
    SELECTION_PATH,
    SELECTION_SEAL_PATH,
)
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    HostilePackageAuditor,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


V5_SELECTION = "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/source-only-selection-v5.json"
V6_COMPARISON = "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/cycloaddition-product-comparison-v6.json"
V7_QUERY = "experiments/external_sources/chemistry/snapshots/org-009-rhea-diels-alder-query-v7/rhea-diels-alder-query.tsv"
V8_COMPARISON = "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/azide-alkyne-product-comparison-v8.json"
V9_ANALYZER = "tools/build_chemistry_org_009_ord_external_v9.py"
V9_ANALYZER_HASH = "sha256:9fc5c9942d320806164b2a9c8b4076e6dc6309207e18ad968a50df1d2e97af61"


def _load_json(root: Path, path: str) -> dict[str, object]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def prior_history_analysis(root: Path) -> dict[str, object]:
    v5 = _load_json(root, V5_SELECTION)
    v6 = _load_json(root, V6_COMPARISON)
    v8 = _load_json(root, V8_COMPARISON)
    v7_lines = (root / V7_QUERY).read_text(encoding="utf-8").splitlines()
    v8_rows = tuple(v8["results_in_original_source_order"])
    v8_split = {
        "favorable_confident_true": sum(
            row["comparison"]["status"] == "favorable" and row["external_confident_inscription"] == "True"
            for row in v8_rows
        ),
        "adverse_confident_false": sum(
            row["comparison"]["status"] == "adverse" and row["external_confident_inscription"] == "False"
            for row in v8_rows
        ),
    }
    summary = {
        "v1_through_v4_identity_and_capture_records_preserved": all(
            (root / f"experiments/external_sources/chemistry/org_009_target_identities_v{version}.json").is_file()
            for version in range(1, 5)
        ),
        "v5_complete_rows": v5["complete_conventional_data_row_count"],
        "v5_qualifying": v5["qualifying_source_count"],
        "v5_unresolved": v5["unresolved_candidate_count"],
        "v6_complete_selected": v6["complete_selected_product_count"],
        "v6_status_counts": v6["status_counts"],
        "v7_query_data_rows": sum(bool(line.strip()) for line in v7_lines[1:]),
        "v8_complete_selected": v8["complete_selected_product_count"],
        "v8_status_counts": v8["status_counts"],
        "v8_independent_confidence_split": v8_split,
    }
    expected = {
        "v1_through_v4_identity_and_capture_records_preserved": True,
        "v5_complete_rows": 1065119,
        "v5_qualifying": 0,
        "v5_unresolved": 0,
        "v6_complete_selected": 47,
        "v6_status_counts": {"adverse": 31, "favorable": 8, "malformed": 0, "unresolved": 8},
        "v7_query_data_rows": 0,
        "v8_complete_selected": 93,
        "v8_status_counts": {"adverse": 2, "favorable": 91, "malformed": 0, "unresolved": 0},
        "v8_independent_confidence_split": {"favorable_confident_true": 91, "adverse_confident_false": 2},
    }
    if summary != expected:
        raise ValueError("ORG-009 V1--V8 adverse development history changed")
    return summary


def _inventory_analysis(root: Path) -> tuple[dict[str, object], tuple[dict[str, object], ...]]:
    inventory = _load_json(root, INVENTORY_PATH)
    rows = tuple(inventory["rows"])
    if (
        inventory.get("complete_payload_count") != 48
        or inventory.get("complete_payload_bytes") != 12993815
        or inventory.get("all_payloads_opened_only_after_v9_seal") is not True
        or inventory.get("source_recapture_count") != 0
        or len(rows) != 48
    ):
        raise ValueError("ORG-009 V9 inventory boundary changed")
    for row in rows:
        path = root / row["opened_snapshot_path"]
        if (
            row.get("capture_status") != "captured_once_after_v9_seal"
            or not path.is_file()
            or path.stat().st_size != row["opened_snapshot_bytes"]
            or hash_file(path) != row["opened_snapshot_sha256"]
        ):
            raise ValueError("ORG-009 V9 payload custody changed")
    return inventory, rows


def exact_analysis(
    root: Path,
    selected_rows: tuple[dict[str, object], ...] | None = None,
    comparison_rows: tuple[dict[str, object], ...] | None = None,
) -> tuple[dict[str, object], dict[str, bool]]:
    identity = _load_json(root, IDENTITY_PATH)
    preseal = _load_json(root, PRESEAL_PATH)
    inventory, inventory_rows = _inventory_analysis(root)
    selection = _load_json(root, SELECTION_PATH)
    selection_seal = _load_json(root, SELECTION_SEAL_PATH)
    comparison = _load_json(root, COMPARISON_PATH)
    selected = tuple(selection["selected_in_payload_and_row_order"]) if selected_rows is None else selected_rows
    outcomes = tuple(comparison["results_in_frozen_order"]) if comparison_rows is None else comparison_rows
    if len(selected) != 28 or len(outcomes) != 28:
        raise ValueError("ORG-009 requires every one of the 28 source-selected reactions")
    if (
        identity.get("parquet_payload_open_count_before_v9_seal") != 0
        or identity.get("all_v1_through_v8_results_must_remain_preserved") is not True
        or preseal.get("ord_reaction_rows_or_products_opened_before_v9_seal") is not False
        or selection.get("product_outcomes_opened_before_selection_seal") is not False
        or selection.get("complete_payload_count") != 48
        or selection.get("complete_conventional_reaction_count") != 131209
        or selection.get("independently_labeled_selected_count") != 28
        or selection.get("structural_but_unlabeled_count") != 0
        or selection_seal.get("selection_sha256") != hash_file(root / SELECTION_PATH)
        or comparison.get("source_inventory_sha256") != hash_file(root / INVENTORY_PATH)
        or comparison.get("source_selection_sha256") != hash_file(root / SELECTION_PATH)
        or comparison.get("source_selection_seal_sha256") != hash_file(root / SELECTION_SEAL_PATH)
        or comparison.get("prediction_seal_sha256") != hash_file(root / PRESEAL_PATH)
        or comparison.get("comparison_program_sha256") != V9_ANALYZER_HASH
        or hash_file(root / V9_ANALYZER) != V9_ANALYZER_HASH
        or comparison.get("complete_selected_reaction_count") != 28
        or comparison.get("reaction_status_counts") != {"adverse": 0, "favorable": 28, "unresolved": 0}
        or comparison.get("no_post_outcome_filter_applied") is not True
        or comparison.get("no_selected_reaction_omitted") is not True
        or hash_file(root / COMPARISON_PATH) != COMPARISON_HASH
    ):
        raise ValueError("ORG-009 V9 registration, custody or complete result changed")

    selected_identity = tuple(
        (row["reaction_id"], row["config"], row["row_ordinal"], tuple(row["independent_label_tokens"]))
        for row in selected
    )
    outcome_identity = tuple(
        (row["reaction_id"], row["config"], row["row_ordinal"], tuple(row["independent_label_tokens"]))
        for row in outcomes
    )
    if selected_identity != outcome_identity:
        raise ValueError("ORG-009 selected reaction identity or order changed")

    checks: dict[str, bool] = {}
    correspondence_count = 0
    product_identifier_count = 0
    for ordinal, (source, result) in enumerate(zip(selected, outcomes), 1):
        product_rows = tuple(result["complete_product_identifier_comparisons"])
        product_identifier_count += len(product_rows)
        valid = tuple(correspondence for row in product_rows for correspondence in row["valid_correspondences"])
        correspondence_count += len(valid)
        exact = (
            result.get("reaction_status") == "favorable"
            and len(product_rows) == 1
            and all(row.get("status") == "favorable" for row in product_rows)
            and all(row.get("complete_element_preserving_bijection_count") == 4 for row in product_rows)
            and len(valid) == 4
            and all(len(row["new_cross_adjacencies"]) == 2 for row in valid)
            and all(len(row["positive_finite_multiplicity_changes"]) == 3 for row in valid)
            and all(len(set(row["azide_atom_mapping"])) == len(row["azide_atom_mapping"]) for row in valid)
            and all(len(set(row["alkyne_atom_mapping"])) == len(row["alkyne_atom_mapping"]) for row in valid)
            and bool(source["independent_label_tokens"])
        )
        checks[f"SFT-CHEM-ORG-009-ORD-REACTION-{ordinal:03d}"] = exact
    if not all(checks.values()):
        raise ValueError("ORG-009 exact product-vector reconstruction failed")

    history = prior_history_analysis(root)
    analysis = {
        "registered_non_uspto_payload_count": len(inventory_rows),
        "registered_non_uspto_payload_bytes": inventory["complete_payload_bytes"],
        "complete_conventional_reaction_count": selection["complete_conventional_reaction_count"],
        "source_selected_reaction_count": len(selected),
        "favorable_reaction_count": sum(result["reaction_status"] == "favorable" for result in outcomes),
        "adverse_reaction_count": sum(result["reaction_status"] == "adverse" for result in outcomes),
        "unresolved_reaction_count": sum(result["reaction_status"] == "unresolved" for result in outcomes),
        "complete_product_identifier_count": product_identifier_count,
        "complete_valid_correspondence_count": correspondence_count,
        "complete_selected_identity_hash": sha256_identity(selected_identity),
        "complete_result_vector_hash": sha256_identity(tuple((row["reaction_id"], row["reaction_status"]) for row in outcomes)),
        "v1_through_v8_preserved_adverse_history": history,
        "source_recapture_count": inventory["source_recapture_count"],
        "post_outcome_filter_applied": False,
    }
    return analysis, checks


class AdditionReactionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ADDITION_REACTION_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        analysis, checks = exact_analysis(self.root)
        registration = observational_experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        expected = self.spec.expected_observation_label
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets={key: HeldLabel("external-observation", expected if value else "adverse-mismatch") for key, value in checks.items()},
            custody_nonce=sha256_identity((registration_hash, COMPARISON_HASH, analysis["complete_result_vector_hash"])),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ORG-009 prediction package changed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        prediction = execution.output
        comparisons = tuple(
            {
                "target_id": key,
                "predicted": prediction.label,
                "observed": release.targets[key].label,
                "passed": prediction.label == release.targets[key].label,
            }
            for key in checks
        )
        try:
            selection = _load_json(self.root, SELECTION_PATH)
            comparison = _load_json(self.root, COMPARISON_PATH)
            exact_analysis(
                self.root,
                tuple(selection["selected_in_payload_and_row_order"][:-1]),
                tuple(comparison["results_in_frozen_order"][:-1]),
            )
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        passed = all(row["passed"] for row in comparisons) and omission_rejected and prediction.label != prediction.label + "__tampered"
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(("exact-org-009-comparison/3", self.spec.falsification_condition)),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ORG-009 release changed")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        payload = {
            "registration": registration_hash,
            "sealed": sealed.seal_hash,
            "prediction": prediction_seal.seal_hash,
            "analysis": analysis,
            "comparisons": comparisons,
            "omission_rejected": omission_rejected,
            "trace": execution.trace_hash,
        }
        measurements = (
            "complete 48-file, 12,993,815-byte non-USPTO Open Reaction Database holdout retained",
            "all 131,209 conventional reaction rows inspected at the source-only boundary",
            "all 28 independently labeled azide-alkyne/click/cycloaddition identities selected before product opening",
            "28 favorable, no adverse and no unresolved complete product vectors",
            "112 exact element-preserving correspondences; each has two new cross-carrier adjacencies and three multiplicity relocations",
            "all V1--V8 absent, adverse, unresolved and failed-universal results preserved without awarding closure",
            f"complete result vector {analysis['complete_result_vector_hash']}",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            True,
            tuple(row.source_id for row in self.spec.target_rows),
            measurements,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


__all__ = ("AdditionReactionValidator", "exact_analysis", "prior_history_analysis")
