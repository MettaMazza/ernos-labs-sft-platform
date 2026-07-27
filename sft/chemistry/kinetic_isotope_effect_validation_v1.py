"""Capability-closed post-seal validation for Chemistry KIN-012."""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.kinetic_isotope_effect_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    INVENTORY_HASH,
    INVENTORY_PATH,
    KINETIC_ISOTOPE_EFFECT_SPEC,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SOURCE_FILES,
    SPEC_HASH,
    SPEC_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.kinetic_isotope_effect_law_v1 import (
    CompleteIsotopologueRatePair,
    ExactPositiveEventRate,
    RetainedIsotopologuePath,
    forced_kinetic_isotope_effect_relation,
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
    "isotopologue_reaction_system_identity",
    "source_document_identity",
    "source_record_class",
    "source_record_identity",
    "source_record_ordinal",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-012 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "target_payload",
        "target_payload_hash",
        "rate_ratio_external_inscription",
        "KIE_external_inscription",
        "decay",
        "production",
        "temperature",
        "uncertainty",
        "replicate",
        "condition",
        "status",
        "value",
    }
    if (
        document.get("complete_registered_target_count") != 71
        or document.get("complete_pdf_page_count") != 47
        or document.get("complete_article_pdf_page_count") != 8
        or document.get("complete_supplementary_information_page_count") != 11
        or document.get("complete_reporting_summary_page_count") != 28
        or document.get("complete_source_data_worksheet_count") != 23
        or document.get("target_values_or_hashes_present") is not False
        or document.get(
            "all_isotopologue_rate_ratio_decay_production_condition_uncertainty_replicate_figure_table_workbook_cell_status_value_and_target_hash_values_absent"
        ) is not True
        or len(rows) != 71
        or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 72))
        or len({row["target_id"] for row in rows}) != 71
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("KIN-012 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"kinetic-isotope-effect-record-{ordinal}"
        instructions.append(
            {"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]}
        )
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append(
                {"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]}
            )
            registers.append(destination)
        for family, label in (
            ("isotopologue-path-law", "two-held-isotope-identities-share-one-complete-reaction-path-and-condition"),
            ("exact-rate-ratio-law", "two-exact-positive-event-rates-force-one-ordered-quotient-and-held-orientation"),
            ("complete-observation-law", "all-90-ratios-3-direct-decays-replicates-directions-controls-and-adverse-records-retained"),
            ("complete-custody-law", "all-71-records-47-pages-23-worksheets-and-923260-nonempty-cells-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-kinetic-isotope-effect-vector", "arguments": table},
            {"opcode": "emit", "destination": "", "arguments": ["complete-kinetic-isotope-effect-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": KINETIC_ISOTOPE_EFFECT_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": KINETIC_ISOTOPE_EFFECT_SPEC.experiment_id,
        "claim_id": KINETIC_ISOTOPE_EFFECT_SPEC.claim_id,
        "provenance": "observational_derivation_with_prefetch_and_value_free_71_record_identity_seal",
        "frozen_relation": KINETIC_ISOTOPE_EFFECT_SPEC.exact_result,
        "prefetch_specification": (SPEC_PATH, SPEC_HASH),
        "source_inventory": (INVENTORY_PATH, INVENTORY_HASH),
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_source_records": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in KINETIC_ISOTOPE_EFFECT_SPEC.target_rows),
        "all_isotopologue_rate_ratio_decay_production_condition_uncertainty_replicate_status_value_and_target_hash_values_absent": True,
        "falsification_condition": KINETIC_ISOTOPE_EFFECT_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 71:
        raise ValueError("KIN-012 prediction is not the complete 71-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 12
        ):
            raise ValueError("KIN-012 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 71:
        raise ValueError("KIN-012 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-012 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 71
        or document.get("complete_pdf_page_target_count") != 47
        or document.get("complete_source_data_worksheet_target_count") != 23
        or document.get("release_requires_complete_identity_and_prediction_seal") is not True
        or document.get("all_complete_source_records_preserved") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH
        or len(targets) != 71
    ):
        raise ValueError("KIN-012 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("KIN-012 identity/target binding changed")
        payload = target.get("target_payload")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("KIN-012 target payload is absent")
        resolved.append({**identity, "target_payload": payload, "target_payload_hash": sha256_identity(payload)})
    return tuple(resolved)


def _exact_pair(first_events: int, second_events: int, second_path: str = "complete-source-path") -> CompleteIsotopologueRatePair:
    roles = tuple(
        HeldLabel("registered-reaction-path-role", role)
        for role in ("reactant-and-condition-entry", "protonated-intermediate", "event", "product-observation")
    )

    def retained(isotope: str, events: int, path: str) -> RetainedIsotopologuePath:
        return RetainedIsotopologuePath(
            HeldLabel("held-isotope-reaction-identity", "source-reaction"),
            HeldLabel("held-complete-reaction-path", path),
            HeldLabel("held-isotopologue-identity", isotope),
            roles,
            HeldLabel("held-isotope-reaction-condition", "source-condition"),
            ExactPositiveEventRate.from_counts(PositiveCount(events), PositiveCount(2)),
            HeldLabel("held-isotope-rate-status", "retained"),
        )

    return CompleteIsotopologueRatePair(
        HeldLabel("registered-ordered-isotopologue-pair", "source-pair"),
        retained("H2O-held-source-label", first_events, "complete-source-path"),
        retained("D2O-held-source-label", second_events, second_path),
    )


def exact_kinetic_isotope_effect_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 71 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 72)):
        raise ValueError("KIN-012 requires the complete source-ordered 71-record vector")
    class_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["source_record_class"]] = class_counts.get(row["source_record_class"], 0) + 1
    expected_counts = {
        "complete-article-landing-record": 1,
        "complete-article-pdf-page": 8,
        "complete-supplementary-information-page": 11,
        "complete-reporting-summary-page": 28,
        "complete-source-data-worksheet": 23,
    }
    normal = forced_kinetic_isotope_effect_relation(_exact_pair(3, 2))
    inverse = forced_kinetic_isotope_effect_relation(_exact_pair(2, 3))
    equal = forced_kinetic_isotope_effect_relation(_exact_pair(2, 2))
    vector = tuple(primary["complete_explicit_rate_ratio_vector"])
    direct = tuple(primary["source_reported_direct_decay_KIE_external_inscriptions"])
    ratios = tuple(Decimal(row["rate_ratio_external_inscription"]) for row in vector)
    temperatures = tuple(primary["source_reported_temperature_series_boundary_external_inscriptions"]["temperatures_C"])
    shapes = tuple(primary["complete_source_data_worksheet_shapes"])
    return {
        "complete_registered_target_count": len(rows),
        "complete_source_class_census": class_counts,
        "complete_source_class_census_matches": class_counts == expected_counts,
        "two_distinct_held_isotope_identities_share_same_complete_path": normal.numerator_isotopologue != normal.denominator_isotopologue and len(normal.complete_reaction_path) == 4,
        "exact_positive_ordered_rate_quotient_reconstructed": normal.exact_rate_ratio == Fraction(3, 2) and inverse.exact_rate_ratio == Fraction(2, 3) and equal.exact_rate_ratio == Fraction(1, 1),
        "normal_inverse_and_equal_orientations_remain_held": tuple(result.ratio_orientation.label for result in (normal, inverse, equal)) == ("numerator-rate-greater", "denominator-rate-greater", "rates-exactly-equal"),
        "complete_47_pdf_pages_retained": sum(class_counts.get(key, 0) for key in ("complete-article-pdf-page", "complete-supplementary-information-page", "complete-reporting-summary-page")) == 47,
        "all_23_source_data_worksheets_retained": class_counts.get("complete-source-data-worksheet") == 23 and len(shapes) == 23,
        "complete_923260_nonempty_cell_surface_retained": primary["complete_source_data_nonempty_cell_count"] == 923260,
        "complete_39002_source_rows_with_values_retained": primary["complete_source_data_row_with_value_count"] == 39002,
        "complete_90_rate_ratio_vector_retained": len(vector) == primary["complete_explicit_rate_ratio_vector_count"] == 90,
        "complete_three_direct_decay_KIE_vector_retained": len(direct) == 3 and tuple(row["KIE_external_inscription"] for row in direct) == ("2.11", "0.827", "0.55"),
        "normal_inverse_and_near_unity_external_inscriptions_all_retained": any(value > 1 for value in ratios) and any(value < 1 for value in ratios) and any(Decimal("0.9") <= value <= Decimal("1.1") for value in ratios),
        "all_three_independent_experiments_and_replicates_retained_without_averaging": primary["three_independent_experiments_retained_without_averaging"] is True and {row["replicate_ordinal"] for row in vector} == {1, 2, 3},
        "complete_five_temperature_vector_retained": temperatures == ("3", "6", "9", "12", "15") and all(sum(row["temperature_C_external_inscription"] == temperature for row in vector) == 18 for temperature in temperatures),
        "source_direct_KIE_range_and_water_splitting_boundaries_retained": primary["source_reported_temperature_series_boundary_external_inscriptions"] == {"inverse_CO_KSIE_range": ["0.2", "0.9"], "temperatures_C": ["3", "6", "9", "12", "15"], "water_splitting_KSIE_at_15_C": "2.8"},
        "source_models_remain_postseal_provenance_only": primary["source_interpretive_transition_state_zero_point_Hooke_quantum_calculation_and_fit_models_retained_as_postseal_provenance_only"] is True,
        "infrared_limitation_reviewer_challenges_and_controls_retained": primary["reporting_summary_admits_in_situ_infrared_is_not_standalone_evidence"] is True and primary["reporting_summary_retains_reviewer_challenges_and_control_requests"] is True,
        "source_values_and_external_zero_decimal_continuum_inscriptions_are_not_proof": primary["source_reported_rate_ratio_decay_production_temperature_uncertainty_replicate_and_condition_values_used_as_fold_proof_parameters"] is False and primary["external_zero_negative_decimal_and_continuum_inscriptions_preserved_only_as_source_provenance"] is True,
        "no_imported_KIE_mass_frequency_transition_state_continuum_fit_selection_or_target_correction": primary["imported_KIE_equation_mass_frequency_law_transition_state_continuum_fitted_exponent_statistical_weight_selection_average_interpolation_or_target_correction_used_in_law"] is False and primary["native_numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used"] is False,
    }


class KineticIsotopeEffectValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = KINETIC_ISOTOPE_EFFECT_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("KIN-012 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = (
            "two-held-isotope-identities-share-one-complete-reaction-path-and-condition",
            "two-exact-positive-event-rates-force-one-ordered-quotient-and-held-orientation",
            "all-90-ratios-3-direct-decays-replicates-directions-controls-and-adverse-records-retained",
            "all-71-records-47-pages-23-worksheets-and-923260-nonempty-cells-retained",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[8:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-complete-source-record-hash", row["target_payload_hash"]
            )
            comparisons.append(
                {
                    "target_id": row["target_id"],
                    "identity_match": identity_match,
                    "law_match": law_match,
                    "postseal_target_hash_match": target_match,
                    "passed": identity_match and law_match and target_match,
                }
            )
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_kinetic_isotope_effect_analysis(source_rows, primary)
        try:
            exact_kinetic_isotope_effect_analysis(source_rows[:-1], primary)
            omitted_record_rejected = False
        except (ValueError, RuntimeError, KeyError, InadmissibleExactValue):
            omitted_record_rejected = True
        try:
            forced_kinetic_isotope_effect_relation(_exact_pair(3, 2, "mismatched-path"))
            mismatched_path_rejected = False
        except InadmissibleExactValue:
            mismatched_path_rejected = True
        controls = {
            "tampered_omitted_source_record_rejected": omitted_record_rejected,
            "tampered_mismatched_isotopologue_path_rejected": mismatched_path_rejected,
            "complete_71_record_vector_retained": len(release.targets) == 71,
            "all_47_pdf_pages_retained": analysis["complete_47_pdf_pages_retained"],
            "all_23_source_data_worksheets_retained": analysis["all_23_source_data_worksheets_retained"],
            "all_923260_nonempty_cells_retained": analysis["complete_923260_nonempty_cell_surface_retained"],
            "complete_ratio_decay_replicate_direction_and_adverse_surface_visible": analysis["complete_90_rate_ratio_vector_retained"] and analysis["complete_three_direct_decay_KIE_vector_retained"] and analysis["all_three_independent_experiments_and_replicates_retained_without_averaging"] and analysis["infrared_limitation_reviewer_challenges_and_controls_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_registered_target_count", "complete_source_class_census"}
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(("exact-kinetic-isotope-effect-relation", self.spec.falsification_condition)),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-012 released target differs from commitment")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "analysis": analysis,
            "comparisons": comparisons,
            "controls": controls,
            "trace": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']}: document={row['source_document_identity']}; record={row['source_record_identity']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            "two distinct held isotope identities retained on one complete reaction path and condition",
            "two exact positive event rates force one ordered quotient with held greater, lesser or equal orientation",
            "complete external vector: 90 explicit rate ratios and direct decay KIE inscriptions 2.11, 0.827 and 0.55",
            "complete source surface: 47 PDF pages, 23 worksheets, 923,260 nonempty cells and 39,002 populated rows",
            "normal, inverse and near-unity cases, all three experiments, replicates, controls, limitations and reviewer challenges retained",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=(source_rows[0]["source_id"],),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "KineticIsotopeEffectValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_kinetic_isotope_effect_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
