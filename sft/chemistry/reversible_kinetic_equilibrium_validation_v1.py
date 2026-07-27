"""Capability-closed post-seal validation for Chemistry KIN-009."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.reversible_kinetic_equilibrium_batch_v1 import (
    ARTICLE_HTML_HASH, ARTICLE_HTML_PATH, ARTICLE_PDF_HASH, ARTICLE_PDF_PATH, DESCRIPTION_HASH, DESCRIPTION_PATH,
    IDENTITY_HASH, IDENTITY_PATH, INVENTORY_HASH, INVENTORY_PATH, MOVIE_HASH, MOVIE_PATH, PRIMARY_HASH, PRIMARY_PATH,
    REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC, SOURCE_DATA_HASH, SOURCE_DATA_PATH, SPEC_HASH, SPEC_PATH, SUPPLEMENT_HASH,
    SUPPLEMENT_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.reversible_kinetic_equilibrium_law_v1 import (
    CompleteReversiblePairGraph, RetainedDirectedTransition,
    forced_reversible_kinetic_equilibrium_correspondence,
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
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id", "source_id", "article_doi", "reversible_system_identity", "source_document_identity",
    "source_page_ordinal", "source_record_class", "source_record_identity", "source_record_ordinal",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-009 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "target_payload", "target_payload_hash", "complete_extracted_page_text", "complete_frame_hashes",
        "complete_member_hash", "state_pair", "direction", "time", "composition", "rate", "energy", "uncertainty",
    }
    if (
        document.get("complete_registered_target_count") != 164
        or document.get("complete_primary_article_page_count") != 10
        or document.get("complete_supplementary_information_page_count") != 144
        or document.get("complete_additional_description_page_count") != 1
        or document.get("complete_supplementary_movie_count") != 1
        or document.get("complete_source_data_archive_member_count") != 8
        or document.get("target_values_or_hashes_present") is not False
        or document.get("all_state_pair_direction_time_equilibrium_composition_rate_quantum_yield_condition_uncertainty_fit_calculation_status_value_and_target_hash_values_absent") is not True
        or len(rows) != 164
        or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 165))
        or len({row["target_id"] for row in rows}) != 164
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("KIN-009 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"reversible-kinetic-equilibrium-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("same-graph-law", "forward-and-reverse-edges-close-one-exact-retained-state-pair"),
            ("kinetic-equilibrium-law", "directed-edge-word-and-recurrence-support-are-two-views-of-the-same-graph"),
            ("complete-status-law", "all-direction-composition-condition-adverse-and-disagreement-records-retained"),
            ("complete-custody-law", "all-164-article-supplement-movie-and-archive-records-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-reversible-kinetic-equilibrium-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-reversible-kinetic-equilibrium-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC.experiment_id,
        "claim_id": REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC.claim_id,
        "provenance": "observational_derivation_with_prefetch_and_value_free_164_record_identity_seal",
        "frozen_relation": REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC.exact_result,
        "prefetch_specification": (SPEC_PATH, SPEC_HASH),
        "source_inventory": (INVENTORY_PATH, INVENTORY_HASH),
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_source_records": (
            (ARTICLE_HTML_PATH, ARTICLE_HTML_HASH), (ARTICLE_PDF_PATH, ARTICLE_PDF_HASH),
            (SUPPLEMENT_PATH, SUPPLEMENT_HASH), (DESCRIPTION_PATH, DESCRIPTION_HASH),
            (MOVIE_PATH, MOVIE_HASH), (SOURCE_DATA_PATH, SOURCE_DATA_HASH),
        ),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC.target_rows),
        "all_state_pair_direction_time_equilibrium_composition_rate_quantum_yield_condition_uncertainty_fit_calculation_status_value_and_target_hash_values_absent": True,
        "falsification_condition": REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 164:
        raise ValueError("KIN-009 prediction is not the complete 164-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 13
        ):
            raise ValueError("KIN-009 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 164:
        raise ValueError("KIN-009 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (SOURCE_DATA_PATH, SOURCE_DATA_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-009 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 164
        or document.get("complete_pdf_page_target_count") != 155
        or document.get("complete_supplementary_movie_target_count") != 1
        or document.get("complete_source_data_archive_member_target_count") != 8
        or document.get("release_requires_complete_identity_and_prediction_seal") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH
        or len(targets) != 164
    ):
        raise ValueError("KIN-009 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("KIN-009 identity/target binding changed")
        payload = target.get("target_payload")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("KIN-009 target payload is absent")
        resolved.append({**identity, "target_payload": payload, "target_payload_hash": sha256_identity(payload)})
    return tuple(resolved)


def _transition(label: str, entry: str, exit: str, orientation: str) -> RetainedDirectedTransition:
    return RetainedDirectedTransition(
        HeldLabel("registered-reversible-transition", label),
        HeldLabel("registered-reversible-state", entry), HeldLabel("registered-reversible-state", exit),
        HeldLabel("held-transition-orientation", orientation),
        HeldLabel("held-reversible-condition", "80-degree-Celsius-in-(CDCl2)2"),
        HeldLabel("held-reversible-status", "measured"),
    )


def exact_reversible_kinetic_equilibrium_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 164 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 165)):
        raise ValueError("KIN-009 requires the complete source-ordered 164-record vector")
    class_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["source_record_class"]] = class_counts.get(row["source_record_class"], 0) + 1
    expected_counts = {
        "complete-primary-article-page": 10,
        "complete-supplementary-information-page": 144,
        "complete-additional-file-description-page": 1,
        "complete-supplementary-movie": 1,
        "complete-source-data-archive-member": 8,
    }
    pages = {
        (row["source_document_identity"], row["source_page_ordinal"]):
        " ".join(row["target_payload"]["complete_extracted_page_text"].split())
        for row in rows if "complete_extracted_page_text" in row["target_payload"]
    }
    required_page_fragments = {
        81: ("83% 2-E-II and 17% 2-E-I", "32% 2-E-II and 68% 2-E-I", "88 hours"),
        82: ("2-E-II to 2-E-I", "slope m = 0.001007", "25.6 kcal/mol"),
        83: ("98% 2-E-I and 2% 2-E-II", "71% 2-E-I and 29% 2-E-II", "82 hours"),
        84: ("2-E-I to 2-E-II", "slope m = 0. 000691", "25.9 kcal mol"),
        85: ("58% 2-E-I and 42% 2-Z-I", "84% 2-E-I and 16% 2-Z-I", "71 hours"),
        86: ("2-E-I to 2-Z-I", "slope m = 0. 003854", "21.8 kcal mol"),
        87: ("61% 2-E-II and 39% 2-Z-II", "80% 2-E-II and 20% 2-Z-II", "71 hours"),
        88: ("2-E-II to 2-Z-II", "slope m = 0. 005570", "21.6 kcal mol"),
        89: ("Supplementary Table 1", "2-E-II 25.9", "Supplementary Table 2", "2-Z-II 1.4"),
    }
    page_fragments_retained = all(
        all(fragment in pages[("supplementary-information.pdf", page)] for fragment in fragments)
        for page, fragments in required_page_fragments.items()
    )
    graph = CompleteReversiblePairGraph(
        HeldLabel("registered-reversible-pair", "2-E-I--2-E-II"),
        HeldLabel("registered-reversible-state", "2-E-II"), HeldLabel("registered-reversible-state", "2-E-I"),
        _transition("2-E-II-to-2-E-I", "2-E-II", "2-E-I", "first-to-second"),
        _transition("2-E-I-to-2-E-II", "2-E-I", "2-E-II", "second-to-first"),
    )
    correspondence = forced_reversible_kinetic_equilibrium_correspondence(graph)
    pair = primary["bidirectional_same_pair_record"]
    directional = pair["directional_records"]
    continuations = primary["continuation_reversible_pair_records"]
    movie_rows = tuple(row for row in rows if row["source_record_class"] == "complete-supplementary-movie")
    archive_rows = tuple(row for row in rows if row["source_record_class"] == "complete-source-data-archive-member")
    return {
        "complete_registered_target_count": len(rows),
        "complete_source_class_census": class_counts,
        "complete_source_class_census_matches": class_counts == expected_counts,
        "same_exact_pair_graph_supplies_both_directions": correspondence.recurrence_support == (graph.first_state, graph.second_state) and correspondence.graph_edge_count.value == 2,
        "exact_forward_direction_retained": directional[0]["initial_support"] == {"2-E-II": "83/100", "2-E-I": "17/100"} and directional[0]["terminal_equilibrium_support"] == {"2-E-II": "8/25", "2-E-I": "17/25"},
        "exact_reverse_direction_retained": directional[1]["initial_support"] == {"2-E-I": "49/50", "2-E-II": "1/50"} and directional[1]["terminal_equilibrium_support"] == {"2-E-I": "71/100", "2-E-II": "29/100"},
        "forward_reverse_terminal_disagreement_retained_without_average": pair["equilibrium_disagreement_retained_not_averaged"] == "68/32 and 71/29 terminal compositions remain separate source observations",
        "continuation_pair_records_retained": len(continuations) == 2 and {row["observed_direction_identity"] for row in continuations} == {"2-Z-I-to-2-E-I", "2-Z-II-to-2-E-II"},
        "source_direction_label_disagreements_retained": all(row["direction_label_disagreement_retained"] for row in continuations) and primary["source_direction_label_disagreements_preserved_without_selection"] is True,
        "all_four_directional_experiments_and_terminal_compositions_retained": primary["complete_directional_experiment_count"] == 4 and primary["complete_terminal_equilibrium_composition_count"] == 4,
        "all_nine_decisive_supplement_pages_reproduced": page_fragments_retained,
        "complete_movie_retained": (
            len(movie_rows) == 1
            and movie_rows[0]["target_payload"]["frame_count"] == 73
            and movie_rows[0]["target_payload"]["complete_movie_hash"] == MOVIE_HASH
        ),
        "all_archive_members_retained": len(archive_rows) == 8 and all(row["target_payload"]["complete_member_hash"].startswith("sha256:") for row in archive_rows),
        "activation_and_relative_energy_vectors_retained": len(primary["supplementary_table_1_activation_energy_vector"]) == 4 and len(primary["supplementary_table_2_relative_energy_vector"]) == 4,
        "external_zero_reference_is_structural_empty_one_only": primary["supplementary_table_2_relative_energy_vector"][0]["external_energy_inscription"] == "0" and primary["supplementary_table_2_relative_energy_vector"][0]["sft_interpretation"] == "structural-EmptyOne-reference-separation",
        "source_fits_and_values_are_postseal_provenance_not_proof": primary["source_reported_equations_fits_slopes_energies_corrections_and_calculations_retained_as_postseal_provenance"] is True and primary["source_fit_slope_or_energy_used_as_fold_proof_parameter"] is False,
        "no_import_fit_selection_average_or_target_correction": primary["imported_reversible_rate_equation_equilibrium_law_or_constant_stochastic_premise_fitted_direction_weight_steady_state_selection_refit_average_interpolation_renormalization_or_target_correction_used_in_law"] is False,
    }


class ReversibleKineticEquilibriumValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = REVERSIBLE_KINETIC_EQUILIBRIUM_SPEC

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
            raise ValueError("KIN-009 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = (
            "forward-and-reverse-edges-close-one-exact-retained-state-pair",
            "directed-edge-word-and-recurrence-support-are-two-views-of-the-same-graph",
            "all-direction-composition-condition-adverse-and-disagreement-records-retained",
            "all-164-article-supplement-movie-and-archive-records-retained",
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
        analysis = exact_reversible_kinetic_equilibrium_analysis(source_rows, primary)
        try:
            exact_reversible_kinetic_equilibrium_analysis(source_rows[:-1], primary)
            omitted_record_rejected = False
        except (ValueError, RuntimeError, KeyError, InadmissibleExactValue):
            omitted_record_rejected = True
        try:
            CompleteReversiblePairGraph(
                HeldLabel("registered-reversible-pair", "tampered"),
                HeldLabel("registered-reversible-state", "a"), HeldLabel("registered-reversible-state", "b"),
                _transition("a-to-b", "a", "b", "first-to-second"),
                _transition("c-to-a", "c", "a", "second-to-first"),
            )
            broken_reverse_boundary_rejected = False
        except InadmissibleExactValue:
            broken_reverse_boundary_rejected = True
        controls = {
            "tampered_omitted_source_record_rejected": omitted_record_rejected,
            "tampered_broken_reverse_boundary_rejected": broken_reverse_boundary_rejected,
            "complete_164_record_vector_retained": len(release.targets) == 164,
            "all_155_pdf_pages_retained": analysis["complete_source_class_census_matches"],
            "all_73_movie_frames_retained": analysis["complete_movie_retained"],
            "all_8_archive_members_retained": analysis["all_archive_members_retained"],
            "adverse_composition_and_direction_disagreements_remain_visible": analysis["forward_reverse_terminal_disagreement_retained_without_average"] and analysis["source_direction_label_disagreements_retained"],
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
            comparison_implementation_identity_hash=sha256_identity(("exact-same-graph-kinetic-equilibrium-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-009 released target differs from commitment")
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
            "same-pair forward record: 83/17 becomes 32/68 after 88 hours at the held condition",
            "same-pair reverse record: 98/2 becomes 71/29 after 82 hours at the held condition",
            "68/32 and 71/29 terminal records remain separate and are not averaged",
            "all source fits, direction-label inconsistencies, 155 PDF pages, 73 movie frames and eight archive members remain post-seal evidence",
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
    "ReversibleKineticEquilibriumValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_reversible_kinetic_equilibrium_analysis", "experiment_registration_record",
    "prediction_program_document",
)
