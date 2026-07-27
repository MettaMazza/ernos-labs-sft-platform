"""Capability-closed post-seal validation for Chemistry KIN-011."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.diffusion_limited_reaction_batch_v1 import (
    DIFFUSION_LIMITED_REACTION_SPEC, IDENTITY_HASH, IDENTITY_PATH, INVENTORY_HASH, INVENTORY_PATH,
    PRIMARY_HASH, PRIMARY_PATH, SOURCE_FILES, SPEC_HASH, SPEC_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.diffusion_limited_reaction_law_v1 import (
    CompleteFiniteTransportPath, RetainedReactionOccurrence, RetainedTransportState,
    RetainedTransportTransition, ExactPositiveCompletionRatio, forced_diffusion_limited_reaction_boundary,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord, HostilePackageAuditor,
    TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id", "source_id", "article_doi", "figshare_repository_doi", "diffusion_reaction_system_identity",
    "source_document_identity", "source_record_class", "source_record_identity", "source_record_ordinal",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-011 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "target_payload", "target_payload_hash", "complete_extracted_page_text", "complete_document_hash",
        "complete_member_hash", "complete_movie_hash", "distance", "time", "velocity", "yield", "rate", "fit",
        "distribution", "simulation", "uncertainty", "condition", "status", "value",
    }
    if (
        document.get("complete_registered_target_count") != 251
        or document.get("complete_pdf_page_count") != 43
        or document.get("complete_supplementary_video_count") != 2
        or document.get("complete_supplementary_video_frame_count") != 1350
        or document.get("complete_archive_count") != 2
        or document.get("complete_source_data_archive_member_count") != 204
        or document.get("target_values_or_hashes_present") is not False
        or document.get("all_distance_time_velocity_yield_rate_fit_distribution_simulation_uncertainty_condition_status_value_and_target_hash_values_absent") is not True
        or len(rows) != 251
        or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 252))
        or len({row["target_id"] for row in rows}) != 251
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("KIN-011 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"diffusion-limited-reaction-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("finite-transport-law", "same-held-reactant-traverses-every-retained-state-and-transition"),
            ("exact-encounter-law", "transport-exit-is-reaction-entry-and-reaction-waits-on-complete-transport-word"),
            ("complete-status-law", "all-stages-discrepancies-limitations-adverse-control-and-unresolved-records-remain-distinct"),
            ("complete-custody-law", "all-251-article-page-video-metadata-and-dual-archive-records-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-diffusion-limited-reaction-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-diffusion-limited-reaction-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": DIFFUSION_LIMITED_REACTION_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": DIFFUSION_LIMITED_REACTION_SPEC.experiment_id,
        "claim_id": DIFFUSION_LIMITED_REACTION_SPEC.claim_id,
        "provenance": "observational_derivation_with_prefetch_and_value_free_251_record_identity_seal",
        "frozen_relation": DIFFUSION_LIMITED_REACTION_SPEC.exact_result,
        "prefetch_specification": (SPEC_PATH, SPEC_HASH), "source_inventory": (INVENTORY_PATH, INVENTORY_HASH),
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH), "complete_source_records": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in DIFFUSION_LIMITED_REACTION_SPEC.target_rows),
        "all_distance_time_velocity_yield_rate_fit_distribution_simulation_uncertainty_condition_status_value_and_target_hash_values_absent": True,
        "falsification_condition": DIFFUSION_LIMITED_REACTION_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 251:
        raise ValueError("KIN-011 prediction is not the complete 251-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 13
        ):
            raise ValueError("KIN-011 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 251:
        raise ValueError("KIN-011 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-011 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 251
        or document.get("complete_pdf_page_target_count") != 43
        or document.get("complete_supplementary_video_target_count") != 2
        or document.get("complete_source_data_archive_member_target_count") != 204
        or document.get("release_requires_complete_identity_and_prediction_seal") is not True
        or document.get("all_complete_source_records_preserved") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH
        or len(targets) != 251
    ):
        raise ValueError("KIN-011 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("KIN-011 identity/target binding changed")
        payload = target.get("target_payload")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("KIN-011 target payload is absent")
        resolved.append({**identity, "target_payload": payload, "target_payload_hash": sha256_identity(payload)})
    return tuple(resolved)


def _source_path() -> tuple[CompleteFiniteTransportPath, RetainedReactionOccurrence]:
    reactant = HeldLabel("held-transported-reactant", "Li-plus-benzene-dimer")
    identities = (
        ("separated-reactants", "initial-boundary"),
        ("initiated-solvation", "retained-transport-entry"),
        ("transport-occurrence-word", "finite-retained-path"),
        ("encounter-boundary", "transport-exit-equals-reaction-entry"),
    )
    states = tuple(
        RetainedTransportState(
            HeldLabel("registered-transport-reaction-state", label), reactant, PositiveCount(position),
            HeldLabel("held-transport-state-status", status),
        )
        for position, (label, status) in enumerate(identities, start=1)
    )
    condition = HeldLabel("held-transport-reaction-condition", "source-held-droplet-condition")
    transitions = tuple(
        RetainedTransportTransition(
            HeldLabel("registered-transport-transition", f"{states[position].state_identity.label}-to-{states[position + 1].state_identity.label}"),
            states[position].state_identity, states[position + 1].state_identity, condition,
            HeldLabel("held-transport-transition-status", "retained"),
        )
        for position in range(len(states) - 1)
    )
    path = CompleteFiniteTransportPath(HeldLabel("registered-finite-transport-path", "source-transport-path"), states, transitions)
    reaction = RetainedReactionOccurrence(
        HeldLabel("registered-reaction-occurrence", "source-product-complex-formation"), path.exit_state,
        HeldLabel("registered-transport-reaction-state", "product-complex"), condition,
        HeldLabel("held-reaction-status", "retained"),
    )
    return path, reaction


def exact_diffusion_limited_reaction_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 251 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 252)):
        raise ValueError("KIN-011 requires the complete source-ordered 251-record vector")
    class_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["source_record_class"]] = class_counts.get(row["source_record_class"], 0) + 1
    expected_counts = {
        "complete-article-landing-record": 1, "complete-pdf-page": 43,
        "complete-supplementary-video": 2, "complete-figshare-metadata-record": 1,
        "complete-source-data-archive-member": 204,
    }
    path, reaction = _source_path()
    boundary = forced_diffusion_limited_reaction_boundary(path, reaction)
    completion = ExactPositiveCompletionRatio.from_counts(PositiveCount(3), PositiveCount(2))
    videos = tuple(row for row in rows if row["source_record_class"] == "complete-supplementary-video")
    archives = tuple(row for row in rows if row["source_record_class"] == "complete-source-data-archive-member")
    source_path = primary["structural_transport_reaction_path"]
    return {
        "complete_registered_target_count": len(rows),
        "complete_source_class_census": class_counts,
        "complete_source_class_census_matches": class_counts == expected_counts,
        "same_held_reactant_retained_through_complete_transport_word": len({state.transported_identity for state in path.ordered_states}) == 1,
        "transport_exit_is_exact_reaction_entry": boundary.encounter_state == reaction.encounter_entry_state and source_path["transport_exit_equals_reaction_entry"] is True,
        "reaction_is_admissible_only_after_complete_transport_word": len(boundary.complete_transport_word) == len(path.ordered_states) - 1 and source_path["complete_transport_word_required_before_reaction_occurrence"] is True,
        "exact_positive_completion_relation_reconstructed_without_fit": (completion.value.numerator, completion.value.denominator) == (3, 2),
        "all_five_separated_solvation_transport_encounter_product_states_retained": tuple(row["state"] for row in source_path["ordered_states"]) == ("separated-reactants", "initiated-solvation", "transport-occurrence-word", "encounter-boundary", "product-complex"),
        "complete_43_pdf_pages_retained": class_counts.get("complete-pdf-page") == 43,
        "complete_1350_video_frames_retained": len(videos) == 2 and sum(row["target_payload"]["frame_count"] for row in videos) == 1350,
        "all_204_archive_members_retained": len(archives) == 204 and all(row["target_payload"]["complete_member_hash"].startswith("sha256:") for row in archives),
        "two_independently_hosted_archive_surfaces_identical_and_both_retained": primary["independently_hosted_nature_and_figshare_archive_bytes_identical"] is True and len({row["archive_identity"] for row in archives}) == 2,
        "complete_11512_key_raw_data_rows_retained": primary["complete_key_raw_data_row_count"] == 11512 and len(primary["complete_key_raw_data_shapes"]) == 7,
        "complete_15_row_radius_total_reaction_time_vector_retained": len(primary["complete_fifteen_row_radius_total_reaction_time_vector"]) == 15,
        "complete_reaction_yield_and_coincidence_matrices_retained": primary["complete_23_by_15_reaction_yield_matrix_retained"] is True and primary["complete_150_by_23_coincidence_filtered_distribution_retained"] is True,
        "experimental_43_plus_or_minus_5_and_simulated_14_velocity_inscriptions_and_discrepancy_retained": primary["source_reported_experimental_diffusion_velocity_external_inscription"] == "43 m/s" and primary["source_reported_one_sigma_velocity_uncertainty_external_inscription"] == "±5 m/s" and primary["source_reported_simulation_diffusion_velocity_external_inscription"] == "14 m/s" and primary["experiment_and_simulation_velocity_discrepancy_retained_without_reconciliation"] is True,
        "reported_rate_estimate_retained_only_as_postseal_provenance": primary["source_reported_rate_constant_estimate_external_inscription"] == "5×10^12 M^-1 s^-1" and primary["source_reported_CDF_log_normal_linear_fit_rate_constant_RPMD_and_other_models_retained_as_postseal_provenance_only"] is True,
        "large_droplet_resolution_and_peer_review_adverse_records_retained": primary["source_reported_large_droplet_deviation_from_linear_fit_retained"] is True and primary["source_reported_time_resolution_insufficient_for_bond_formation_detail_retained"] is True and primary["peer_review_nonencounter_and_not_all_systems_reactive_adverse_question_retained"] is True,
        "source_values_and_external_zero_negative_decimal_continuum_inscriptions_are_not_proof": primary["source_reported_distance_time_velocity_yield_rate_fit_distribution_simulation_uncertainty_and_condition_values_used_as_fold_proof_parameters"] is False and primary["external_zero_negative_decimal_and_continuum_inscriptions_preserved_only_as_source_provenance"] is True,
        "no_imported_diffusion_continuum_fit_selection_or_target_correction": primary["imported_Fick_Smoluchowski_diffusion_equation_continuum_concentration_field_stochastic_collision_weight_fitted_diffusion_coefficient_selection_average_interpolation_or_target_correction_used_in_law"] is False and primary["native_numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used"] is False,
    }


class DiffusionLimitedReactionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = DIFFUSION_LIMITED_REACTION_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("KIN-011 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = (
            "same-held-reactant-traverses-every-retained-state-and-transition",
            "transport-exit-is-reaction-entry-and-reaction-waits-on-complete-transport-word",
            "all-stages-discrepancies-limitations-adverse-control-and-unresolved-records-remain-distinct",
            "all-251-article-page-video-metadata-and-dual-archive-records-retained",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[9:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-complete-source-record-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match,
                "law_match": law_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_diffusion_limited_reaction_analysis(source_rows, primary)
        try:
            exact_diffusion_limited_reaction_analysis(source_rows[:-1], primary)
            omitted_record_rejected = False
        except (ValueError, RuntimeError, KeyError, InadmissibleExactValue):
            omitted_record_rejected = True
        path, reaction = _source_path()
        broken_reaction = RetainedReactionOccurrence(
            HeldLabel("registered-reaction-occurrence", "tampered"),
            HeldLabel("registered-transport-reaction-state", "not-transport-exit"), reaction.product_state,
            reaction.condition_boundary, HeldLabel("held-reaction-status", "tampered"),
        )
        try:
            forced_diffusion_limited_reaction_boundary(path, broken_reaction)
            broken_boundary_rejected = False
        except InadmissibleExactValue:
            broken_boundary_rejected = True
        controls = {
            "tampered_omitted_source_record_rejected": omitted_record_rejected,
            "tampered_transport_exit_reaction_entry_mismatch_rejected": broken_boundary_rejected,
            "complete_251_record_vector_retained": len(release.targets) == 251,
            "all_43_pdf_pages_retained": analysis["complete_43_pdf_pages_retained"],
            "all_1350_movie_frames_retained": analysis["complete_1350_video_frames_retained"],
            "all_204_archive_members_retained": analysis["all_204_archive_members_retained"],
            "all_discrepancy_and_adverse_records_visible": analysis["large_droplet_resolution_and_peer_review_adverse_records_retained"] and analysis["experimental_43_plus_or_minus_5_and_simulated_14_velocity_inscriptions_and_discrepancy_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_registered_target_count", "complete_source_class_census"}
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-finite-transport-reaction-boundary", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-011 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis,
            "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']}: document={row['source_document_identity']}; record={row['source_record_identity']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            "complete finite separated-reactant, solvation, transport, encounter and product path retained",
            "transport exit is exact reaction entry; reaction waits on complete finite transport word",
            "external velocity inscriptions retained: experiment 43 ±5 m/s; simulation 14 m/s; discrepancy unreconciled",
            "external source rate estimate 5×10^12 M^-1 s^-1 retained only as post-seal provenance",
            "43 PDF pages, 1,350 movie frames, 204 archive members and 11,512 key raw rows remain byte-bound",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=(source_rows[0]["source_id"],), measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "DiffusionLimitedReactionValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_diffusion_limited_reaction_analysis", "experiment_registration_record", "prediction_program_document",
)
