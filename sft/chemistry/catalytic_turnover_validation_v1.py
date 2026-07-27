"""Capability-closed post-seal validation for Chemistry KIN-010."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.catalytic_turnover_batch_v1 import (
    CATALYTIC_TURNOVER_SPEC, IDENTITY_HASH, IDENTITY_PATH, INVENTORY_HASH, INVENTORY_PATH,
    PRIMARY_HASH, PRIMARY_PATH, SOURCE_FILES, SPEC_HASH, SPEC_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.catalytic_turnover_law_v1 import (
    CompleteCatalyticCycle, RetainedCatalystState, RetainedCatalyticTransition,
    forced_catalytic_turnover, forced_cycle_frequency,
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
    "target_id", "source_id", "article_doi", "source_data_repository_doi", "catalytic_system_identity",
    "source_document_identity", "source_record_class", "source_record_identity", "source_record_ordinal",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-010 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "target_payload", "target_payload_hash", "complete_extracted_page_text", "complete_document_hash",
        "complete_member_hash", "complete_movie_hash", "cycle", "state", "transition", "duration", "turnover",
        "frequency", "condition", "fit", "rate", "constant", "uncertainty", "product", "control_status",
    }
    if (
        document.get("complete_registered_target_count") != 497
        or document.get("complete_supplementary_information_page_count") != 106
        or document.get("complete_supplementary_movie_count") != 1
        or document.get("complete_supplementary_movie_frame_count") != 1604
        or document.get("complete_archive_count") != 7
        or document.get("complete_source_data_archive_member_count") != 387
        or document.get("article_pdf_unavailable_response_preserved") is not True
        or document.get("target_values_or_hashes_present") is not False
        or document.get("all_cycle_state_transition_duration_turnover_frequency_condition_fit_rate_constant_uncertainty_product_control_status_value_and_target_hash_values_absent") is not True
        or len(rows) != 497
        or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 498))
        or len({row["target_id"] for row in rows}) != 497
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("KIN-010 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"catalytic-turnover-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("complete-cycle-law", "same-held-catalyst-traverses-every-state-and-last-transition-returns-to-entry"),
            ("turnover-frequency-law", "one-complete-return-word-is-one-turnover-and-count-per-held-interval-is-exact-frequency"),
            ("complete-status-law", "five-structural-states-four-observed-levels-and-all-adverse-control-unresolved-statuses-remain-distinct"),
            ("complete-custody-law", "all-497-article-supplement-movie-metadata-and-archive-records-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-catalytic-turnover-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-catalytic-turnover-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": CATALYTIC_TURNOVER_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": CATALYTIC_TURNOVER_SPEC.experiment_id,
        "claim_id": CATALYTIC_TURNOVER_SPEC.claim_id,
        "provenance": "observational_derivation_with_prefetch_and_value_free_497_record_identity_seal",
        "frozen_relation": CATALYTIC_TURNOVER_SPEC.exact_result,
        "prefetch_specification": (SPEC_PATH, SPEC_HASH), "source_inventory": (INVENTORY_PATH, INVENTORY_HASH),
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH), "complete_source_records": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in CATALYTIC_TURNOVER_SPEC.target_rows),
        "all_cycle_state_transition_duration_turnover_frequency_condition_fit_rate_constant_uncertainty_product_control_status_value_and_target_hash_values_absent": True,
        "falsification_condition": CATALYTIC_TURNOVER_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 497:
        raise ValueError("KIN-010 prediction is not the complete 497-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 13
        ):
            raise ValueError("KIN-010 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 497:
        raise ValueError("KIN-010 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-010 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 497
        or document.get("complete_supplementary_information_page_target_count") != 106
        or document.get("complete_supplementary_movie_target_count") != 1
        or document.get("complete_source_data_archive_member_target_count") != 387
        or document.get("release_requires_complete_identity_and_prediction_seal") is not True
        or document.get("all_complete_source_records_preserved") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH
        or len(targets) != 497
    ):
        raise ValueError("KIN-010 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("KIN-010 identity/target binding changed")
        payload = target.get("target_payload")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("KIN-010 target payload is absent")
        resolved.append({**identity, "target_payload": payload, "target_payload_hash": sha256_identity(payload)})
    return tuple(resolved)


def _source_cycle() -> CompleteCatalyticCycle:
    catalyst = HeldLabel("held-catalyst-identity", "single-LPd-catalyst-carrier")
    identities = (
        ("State 1", "separately-observed-conductance-state"),
        ("State 2", "structural-intermediate-not-separately-resolved"),
        ("State 3", "separately-observed-conductance-state"),
        ("State 4", "separately-observed-conductance-state"),
        ("State 5", "separately-observed-conductance-state"),
    )
    states = tuple(
        RetainedCatalystState(
            HeldLabel("registered-catalytic-state", label), catalyst, PositiveCount(position),
            HeldLabel("held-catalytic-state-status", status),
        )
        for position, (label, status) in enumerate(identities, start=1)
    )
    processes = ("oxidative-addition", "ligand-exchange", "pre-transmetalation", "transmetalation", "reductive-elimination-and-return")
    transitions = tuple(
        RetainedCatalyticTransition(
            HeldLabel("registered-catalytic-transition", f"{states[position].state_identity.label}-to-{states[(position + 1) % len(states)].state_identity.label}"),
            states[position].state_identity, states[(position + 1) % len(states)].state_identity,
            HeldLabel("held-catalytic-process", process), HeldLabel("held-catalytic-condition", "source-held-cycle-condition"),
            HeldLabel("held-catalytic-transition-status", "retained"),
        )
        for position, process in enumerate(processes)
    )
    return CompleteCatalyticCycle(HeldLabel("registered-catalytic-cycle", "source-five-state-cycle"), states, transitions)


def exact_catalytic_turnover_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 497 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 498)):
        raise ValueError("KIN-010 requires the complete source-ordered 497-record vector")
    class_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["source_record_class"]] = class_counts.get(row["source_record_class"], 0) + 1
    expected_counts = {
        "complete-article-landing-record": 1, "attempted-article-pdf-returned-html-record": 1,
        "complete-supplementary-information-page": 106, "complete-supplementary-video": 1,
        "complete-zenodo-metadata-record": 1, "complete-source-data-archive-member": 387,
    }
    cycle = _source_cycle()
    turnover = forced_catalytic_turnover(cycle)
    exact_frequency = forced_cycle_frequency(PositiveCount(7), PositiveCount(5))
    source_cycle = primary["structural_cycle"]
    turnover_rows = primary["complete_substituent_turnover_vector"]["rows"]
    expected_turnover = (
        ("OCH3", "-0.27", "0.5", "-1.9"), ("CH3", "-0.17", "4.6", "-0.9"),
        ("H", "0", "29.6", "0.0"), ("Cl", "0.23", "39.0", "3.1×10^-2"),
        ("COOMe", "0.45", "203.9", "0.7"), ("CF3", "0.54", "615.6", "1.2"),
        ("CN", "0.66", "2098.7", "1.8"),
    )
    turnover_vector = tuple((
        row["substituent"], row["sigma_p_external_inscription"], row["TOF_per_second_external_inscription"],
        row["lg_k_over_k0_external_inscription"],
    ) for row in turnover_rows)
    s2 = primary["independent_state_1_state_4_rate_vector_table_s2"]["rows"]
    s3 = primary["independent_state_1_state_4_rate_vector_table_s3"]["rows"]
    movie_rows = tuple(row for row in rows if row["source_record_class"] == "complete-supplementary-video")
    archive_rows = tuple(row for row in rows if row["source_record_class"] == "complete-source-data-archive-member")
    attempted_pdf = tuple(row for row in rows if row["source_record_class"] == "attempted-article-pdf-returned-html-record")
    figure = primary["figure_6_source_data"]
    return {
        "complete_registered_target_count": len(rows),
        "complete_source_class_census": class_counts,
        "complete_source_class_census_matches": class_counts == expected_counts,
        "same_catalyst_identity_retained_through_all_five_states": len({state.catalyst_identity for state in cycle.ordered_states}) == 1 and source_cycle["registered_state_count"] == 5,
        "final_transition_returns_exact_entry_state": turnover.ordered_transition_word[-1].exit_state == turnover.exact_return_state and source_cycle["entry_state_equals_return_state"] is True,
        "one_complete_return_word_is_one_turnover": turnover.completed_cycle_count.value == 1 and len(turnover.ordered_transition_word) == 5,
        "exact_positive_cycle_frequency_relation_reconstructed_without_fit": exact_frequency.cycle_frequency.value.numerator == 7 and exact_frequency.cycle_frequency.value.denominator == 5,
        "five_structural_states_and_four_observed_levels_distinguished": source_cycle["registered_state_count"] == 5 and source_cycle["separately_observed_conductance_state_count"] == 4 and source_cycle["ordered_states"][1]["source_status"] == "structural-intermediate-not-separately-resolved-as-conductance-state",
        "complete_seven_row_turnover_vector_retained": turnover_vector == expected_turnover,
        "independent_rate_tables_retained_separately_without_average": len(s2) == len(s3) == 5 and s2 != s3 and primary["table_s2_and_table_s3_remain_separate_without_selection_or_averaging"] is True,
        "complete_385617_raw_trace_rows_retained": figure["fig6a_complete_trace_row_count_including_header"] + figure["fig6b_complete_trace_row_count_including_header"] == 385617 and figure["all_complete_raw_rows_remain_byte_bound_without_selection"] is True,
        "all_signed_decimal_and_zero_source_inscriptions_preserved_outside_proof": figure["all_signed_decimal_and_zero_glyphs_are_external_inscriptions_only"] is True and primary["external_zero_and_negative_glyphs_preserved_only_as_source_inscriptions"] is True,
        "complete_1604_frame_movie_retained": len(movie_rows) == 1 and movie_rows[0]["target_payload"]["frame_count"] == 1604,
        "all_387_archive_members_retained": len(archive_rows) == 387 and all(row["target_payload"]["complete_member_hash"].startswith("sha256:") for row in archive_rows),
        "unavailable_article_pdf_adverse_record_retained": len(attempted_pdf) == 1 and attempted_pdf[0]["target_payload"]["source_content_class"] == "HTML-response-not-PDF" and attempted_pdf[0]["target_payload"]["unavailable_article_pdf_adverse_record"] is True,
        "low_temperature_insufficient_fit_adverse_record_retained": primary["low_temperature_fewer_cycle_and_insufficient_fit_data_adverse_record_retained"] is True,
        "source_fits_rates_and_values_are_postseal_provenance_not_proof": primary["source_reported_maximum_likelihood_single_exponent_Eyring_Arrhenius_Hess_and_other_fits_or_calculations_retained_as_postseal_provenance_only"] is True and primary["source_reported_rates_TOF_dwell_times_frequencies_conditions_errors_and_uncertainties_used_as_fold_proof_parameters"] is False,
        "no_import_fit_selection_average_or_target_correction": primary["imported_turnover_frequency_rate_equation_Michaelis_Menten_steady_state_stochastic_cycle_weight_fitted_efficiency_selection_average_interpolation_or_target_correction_used_in_law"] is False,
    }


class CatalyticTurnoverValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = CATALYTIC_TURNOVER_SPEC

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
            raise ValueError("KIN-010 prediction package changed")
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
            "same-held-catalyst-traverses-every-state-and-last-transition-returns-to-entry",
            "one-complete-return-word-is-one-turnover-and-count-per-held-interval-is-exact-frequency",
            "five-structural-states-four-observed-levels-and-all-adverse-control-unresolved-statuses-remain-distinct",
            "all-497-article-supplement-movie-metadata-and-archive-records-retained",
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
        analysis = exact_catalytic_turnover_analysis(source_rows, primary)
        try:
            exact_catalytic_turnover_analysis(source_rows[:-1], primary)
            omitted_record_rejected = False
        except (ValueError, RuntimeError, KeyError, InadmissibleExactValue):
            omitted_record_rejected = True
        cycle = _source_cycle()
        broken_edges = cycle.ordered_transitions[:-1] + (
            RetainedCatalyticTransition(
                HeldLabel("registered-catalytic-transition", "tampered-return"), cycle.ordered_states[-1].state_identity,
                HeldLabel("registered-catalytic-state", "not-entry"), HeldLabel("held-catalytic-process", "tampered"),
                cycle.ordered_transitions[-1].condition_boundary, HeldLabel("held-catalytic-transition-status", "tampered"),
            ),
        )
        try:
            CompleteCatalyticCycle(cycle.cycle_identity, cycle.ordered_states, broken_edges)
            broken_return_rejected = False
        except InadmissibleExactValue:
            broken_return_rejected = True
        controls = {
            "tampered_omitted_source_record_rejected": omitted_record_rejected,
            "tampered_broken_catalyst_return_rejected": broken_return_rejected,
            "complete_497_record_vector_retained": len(release.targets) == 497,
            "all_106_supplementary_pages_retained": analysis["complete_source_class_census_matches"],
            "all_1604_movie_frames_retained": analysis["complete_1604_frame_movie_retained"],
            "all_387_archive_members_retained": analysis["all_387_archive_members_retained"],
            "adverse_unavailable_pdf_and_insufficient_fit_records_visible": analysis["unavailable_article_pdf_adverse_record_retained"] and analysis["low_temperature_insufficient_fit_adverse_record_retained"],
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
            comparison_implementation_identity_hash=sha256_identity(("exact-catalyst-return-and-cycle-frequency-relation", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-010 released target differs from commitment")
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
            "five-state structural cycle retained; four separately observed conductance states retained without substitution",
            "exact transition word: State 1 to 2 to 3 to 4 to 5 to State 1 catalyst return",
            "Table S1 TOF values retained exactly: 0.5, 4.6, 29.6, 39.0, 203.9, 615.6 and 2098.7 per second",
            "Table S2 and Table S3 remain independent and unaveraged; 385,617 raw trace rows remain byte-bound",
            "all source fits, external signed/zero inscriptions, 106 pages, 1,604 movie frames and 387 archive members remain post-seal evidence",
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
    "CatalyticTurnoverValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_catalytic_turnover_analysis", "experiment_registration_record", "prediction_program_document",
)
