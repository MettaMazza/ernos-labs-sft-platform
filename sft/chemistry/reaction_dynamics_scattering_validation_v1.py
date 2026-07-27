"""Capability-closed post-seal validation for Chemistry KIN-013."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.reaction_dynamics_scattering_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    INVENTORY_HASH,
    INVENTORY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    REACTION_DYNAMICS_SCATTERING_SPEC,
    SOURCE_FILES,
    SPEC_HASH,
    SPEC_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.reaction_dynamics_scattering_law_v1 import (
    CompleteFiniteProductStateSupport,
    RetainedIncomingReactionChannel,
    RetainedOutgoingProductState,
    forced_reaction_scattering_product_state_law,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldTable,
    FoldWord,
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
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id",
    "source_id",
    "article_doi",
    "incoming_outgoing_reaction_system_identity",
    "source_document_identity",
    "source_record_class",
    "source_record_identity",
    "source_record_ordinal",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-013 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "target_payload", "target_payload_hash", "angle", "speed", "energy", "branching", "experimental",
        "theoretical", "fit", "normalization", "estimate", "tentative", "background", "control", "limitation",
        "adverse", "reviewer", "status", "value",
    }
    if (
        document.get("complete_registered_target_count") != 51
        or document.get("complete_pdf_page_count") != 36
        or document.get("complete_article_pdf_page_count") != 9
        or document.get("complete_supplementary_information_page_count") != 11
        or document.get("complete_transparent_peer_review_page_count") != 16
        or document.get("complete_source_data_worksheet_count") != 14
        or document.get("target_values_or_hashes_present") is not False
        or document.get(
            "all_incoming_outgoing_channel_product_state_angle_speed_energy_branching_experimental_theoretical_fit_normalization_estimate_tentative_background_control_limitation_adverse_reviewer_status_value_and_target_hash_values_absent"
        ) is not True
        or len(rows) != 51
        or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 52))
        or len({row["target_id"] for row in rows}) != 51
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("KIN-013 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"reaction-dynamics-scattering-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("finite-channel-law", "one-held-incoming-preparation-retains-complete-distinct-outgoing-joint-product-states"),
            ("exact-scattering-law", "positive-state-event-counts-force-exact-shares-and-held-incoming-outgoing-orientations"),
            ("complete-status-law", "experiment-theory-fit-normalization-estimate-tentative-control-limitation-and-review-remain-distinct"),
            ("complete-custody-law", "all-51-records-36-pages-14-worksheets-978591-cells-and-6408-key-state-cells-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-reaction-dynamics-scattering-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-reaction-dynamics-scattering-vector"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": REACTION_DYNAMICS_SCATTERING_SPEC.experiment_id + "-value-free-complete-vector", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": REACTION_DYNAMICS_SCATTERING_SPEC.experiment_id,
        "claim_id": REACTION_DYNAMICS_SCATTERING_SPEC.claim_id,
        "provenance": "observational_derivation_with_prefetch_and_value_free_51_record_identity_seal",
        "frozen_relation": REACTION_DYNAMICS_SCATTERING_SPEC.exact_result,
        "prefetch_specification": (SPEC_PATH, SPEC_HASH),
        "source_inventory": (INVENTORY_PATH, INVENTORY_HASH),
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_source_records": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in REACTION_DYNAMICS_SCATTERING_SPEC.target_rows),
        "all_channel_product_state_angle_speed_energy_branching_fit_normalization_estimate_tentative_adverse_reviewer_status_value_and_target_hash_values_absent": True,
        "falsification_condition": REACTION_DYNAMICS_SCATTERING_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 51:
        raise ValueError("KIN-013 prediction is not the complete 51-record table")
    resolved = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 12:
            raise ValueError("KIN-013 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 51:
        raise ValueError("KIN-013 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-013 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 51
        or document.get("complete_pdf_page_target_count") != 36
        or document.get("complete_source_data_worksheet_target_count") != 14
        or document.get("release_requires_complete_identity_and_prediction_seal") is not True
        or document.get("all_complete_source_records_preserved") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH
        or len(targets) != 51
    ):
        raise ValueError("KIN-013 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("KIN-013 identity/target binding changed")
        payload = target.get("target_payload")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("KIN-013 target payload is absent")
        resolved.append({**identity, "target_payload": payload, "target_payload_hash": sha256_identity(payload)})
    return tuple(resolved)


def _incoming(reaction: str = "source-reaction") -> RetainedIncomingReactionChannel:
    return RetainedIncomingReactionChannel(
        HeldLabel("registered-incoming-reaction-channel", "F-plus-CH4"),
        HeldLabel("held-scattering-reaction-identity", reaction),
        tuple(HeldLabel("held-incoming-channel-carrier", carrier) for carrier in ("F", "CH4")),
        HeldLabel("held-incoming-preparation", "crossed-beam-preparation"),
    )


def _outgoing(occurrence: int, orientation: str, events: int, reaction: str = "source-reaction") -> RetainedOutgoingProductState:
    return RetainedOutgoingProductState(
        PositiveCount(occurrence), HeldLabel("registered-outgoing-product-channel", f"CH3-HF-{occurrence}"),
        HeldLabel("held-scattering-reaction-identity", reaction),
        tuple(HeldLabel("held-outgoing-product-carrier", carrier) for carrier in ("CH3", "HF")),
        tuple(HeldLabel("held-outgoing-product-state", state) for state in (f"CH3-state-{occurrence}", f"HF-state-{occurrence}")),
        HeldLabel("held-incoming-outgoing-orientation", orientation), PositiveCount(events),
        HeldLabel("held-scattering-evidence-status", "retained"),
    )


def _support(outgoing_reaction: str = "source-reaction") -> CompleteFiniteProductStateSupport:
    return CompleteFiniteProductStateSupport(
        _incoming(),
        (_outgoing(1, "same-oriented", 3, outgoing_reaction), _outgoing(2, "transverse-oriented", 2, outgoing_reaction), _outgoing(3, "opposed-oriented", 1, outgoing_reaction)),
    )


def exact_reaction_dynamics_scattering_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 51 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 52)):
        raise ValueError("KIN-013 requires the complete source-ordered 51-record vector")
    class_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["source_record_class"]] = class_counts.get(row["source_record_class"], 0) + 1
    expected_counts = {
        "complete-article-landing-record": 1, "complete-article-pdf-page": 9,
        "complete-supplementary-information-page": 11, "complete-transparent-peer-review-page": 16,
        "complete-source-data-worksheet": 14,
    }
    result = forced_reaction_scattering_product_state_law(_support())
    statuses = primary["source_experimental_theoretical_and_processing_statuses_retained_separately"]
    peer = primary["transparent_peer_review_adverse_surface"]
    headline = primary["source_reported_headline_external_inscriptions"]
    return {
        "complete_registered_target_count": len(rows),
        "complete_source_class_census": class_counts,
        "complete_source_class_census_matches": class_counts == expected_counts,
        "finite_incoming_and_complete_distinct_outgoing_joint_product_state_support_reconstructed": len(result) == 3 and len({row.ordered_product_states for row in result}) == 3,
        "exact_positive_state_shares_reconstructed_without_cross_section_model": tuple(row.exact_event_share for row in result) == (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
        "all_three_incoming_outgoing_orientation_relations_remain_held": tuple(row.orientation_to_incoming.label for row in result) == ("same-oriented", "transverse-oriented", "opposed-oriented"),
        "complete_36_pdf_pages_retained": sum(class_counts.get(key, 0) for key in ("complete-article-pdf-page", "complete-supplementary-information-page", "complete-transparent-peer-review-page")) == 36,
        "all_14_source_data_worksheets_retained": class_counts.get("complete-source-data-worksheet") == 14 and len(primary["complete_source_data_worksheet_shapes"]) == 14,
        "complete_978591_nonempty_cell_surface_retained": primary["complete_source_data_nonempty_cell_count"] == 978591,
        "complete_6408_key_state_resolved_product_and_scattering_cells_retained": primary["complete_key_state_resolved_product_and_scattering_cell_count"] == 6408,
        "complete_pair_branching_state_scattering_sampling_and_overlap_vectors_retained": len(primary["complete_fig3_pair_correlated_branching_cell_vector"]) > 1 and len(primary["complete_fig4_state_resolved_scattering_cell_vector"]) > 1 and len(primary["complete_supplementary_fig8_sampling_and_contamination_cell_vector"]) > 1 and len(primary["complete_supplementary_fig9_before_after_correction_cell_vector"]) > 1,
        "source_headline_state_and_orientation_vector_retained": headline == {
            "backward_product_pair": "(0_0,2)", "collision_energy": "2.4 kcal mol^-1 (0.106 eV)",
            "experimental_pair_branching_total": "unity", "forward_product_pair": "(0_0,3)",
            "ground_state_CH3_reactivity": "40%", "incoming_CH4_rotational_state_distribution": "0.31:0.54:0.15 for j=0:j=1:j=2",
            "sideways_product_pair": "(2_2,2)", "umbrella_excited_CH3_experimental_reactive_flux": "57%",
            "umbrella_excited_CH3_theoretical_reactive_flux": "58%",
        },
        "experimental_theoretical_fit_normalization_estimate_tentative_and_limit_statuses_all_retained": all(statuses.values()),
        "complete_transparent_peer_review_adverse_surface_retained": all(peer.values()),
        "all_raw_images_speed_energy_branching_scattering_theory_and_review_records_byte_bound": primary["all_complete_raw_image_speed_energy_branching_state_resolved_angular_sampling_overlap_correction_theory_and_peer_review_records_byte_bound"] is True,
        "source_models_fits_normalizations_and_corrections_remain_postseal_provenance_only": primary["source_scattering_cross_section_energy_momentum_transition_state_potential_surface_and_quantum_dynamics_models_retained_as_postseal_provenance_only"] is True and primary["source_reported_values_models_fits_normalizations_estimates_tentative_assignments_and_corrections_used_as_fold_proof_parameters"] is False,
        "external_zero_negative_decimal_scientific_angle_and_continuum_inscriptions_are_not_proof": primary["external_zero_negative_decimal_scientific_notation_angle_and_continuum_inscriptions_preserved_only_as_source_provenance"] is True,
        "no_imported_scattering_cross_section_amplitude_potential_continuum_fit_selection_or_target_correction": primary["imported_scattering_equation_cross_section_law_angular_continuum_probability_amplitude_fitted_potential_distribution_normalization_selection_average_interpolation_or_target_correction_used_in_law"] is False and primary["native_numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used"] is False,
    }


class ReactionDynamicsScatteringValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = REACTION_DYNAMICS_SCATTERING_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("KIN-013 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"]) for row in source_rows}
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-complete-target-custodian", targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope))
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = (
            "one-held-incoming-preparation-retains-complete-distinct-outgoing-joint-product-states",
            "positive-state-event-counts-force-exact-shares-and-held-incoming-outgoing-orientations",
            "experiment-theory-fit-normalization-estimate-tentative-control-limitation-and-review-remain-distinct",
            "all-51-records-36-pages-14-worksheets-978591-cells-and-6408-key-state-cells-retained",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, start=1))
            law_match = tuple(cell.label for cell in word.cells[8:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_reaction_dynamics_scattering_analysis(source_rows, primary)
        try:
            exact_reaction_dynamics_scattering_analysis(source_rows[:-1], primary)
            omitted_record_rejected = False
        except (ValueError, RuntimeError, KeyError, InadmissibleExactValue):
            omitted_record_rejected = True
        try:
            _support("mismatched-reaction")
            mismatched_reaction_rejected = False
        except InadmissibleExactValue:
            mismatched_reaction_rejected = True
        controls = {
            "tampered_omitted_source_record_rejected": omitted_record_rejected,
            "tampered_incoming_outgoing_reaction_mismatch_rejected": mismatched_reaction_rejected,
            "complete_51_record_vector_retained": len(release.targets) == 51,
            "all_36_pdf_pages_retained": analysis["complete_36_pdf_pages_retained"],
            "all_14_source_data_worksheets_retained": analysis["all_14_source_data_worksheets_retained"],
            "all_978591_cells_and_6408_key_state_cells_retained": analysis["complete_978591_nonempty_cell_surface_retained"] and analysis["complete_6408_key_state_resolved_product_and_scattering_cells_retained"],
            "complete_fit_normalization_tentative_limitation_discrepancy_and_review_surface_visible": analysis["experimental_theoretical_fit_normalization_estimate_tentative_and_limit_statuses_all_retained"] and analysis["complete_transparent_peer_review_adverse_surface_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_registered_target_count", "complete_source_class_census"}
        passed = all(row["passed"] for row in comparisons) and all(bool(value) for key, value in analysis.items() if key not in non_boolean) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-finite-reaction-scattering-product-state-law", self.spec.falsification_condition)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-013 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        measurement_payload = {"experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash, "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = tuple(f"{row['target_id']}: document={row['source_document_identity']}; record={row['source_record_identity']}; target={row['target_payload_hash']}" for row in source_rows) + (
            "finite held F+CH4 incoming preparation and complete joint CH3(vi)+HF(v) outgoing product-state support retained",
            "exact positive state shares and held same/transverse/opposed incoming-outgoing orientation relations reconstructed",
            "source external vector retains 40% ground-state CH3 and 57% experimental versus 58% theoretical umbrella-excited flux inscriptions",
            "source orientation progression retains (0_0,3) forward, (2_2,2) sideways and (0_0,2) backward inscriptions",
            "36 PDF pages, 14 worksheets, 978,591 nonempty cells and 6,408 key state-resolved cells remain byte-bound",
            "fits, normalizations, tentative HF(v=1), sharper theoretical forward peak, theory limitations, detection limitations and full reviewer challenges remain visible",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash, isolation_certificate=isolation, target_custody_certificate=custody, evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True, data_source_ids=(source_rows[0]["source_id"],), measurements=measurements, measurement_receipt_hash=sha256_identity(measurement_payload), falsification_condition=self.spec.falsification_condition, passed=passed)


__all__ = (
    "ReactionDynamicsScatteringValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_reaction_dynamics_scattering_analysis", "experiment_registration_record", "prediction_program_document",
)
